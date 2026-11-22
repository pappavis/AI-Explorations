#!/usr/bin/env python3
"""Configure remote MCP clients and verify the protocol independently."""
from __future__ import annotations

import argparse
import asyncio
from datetime import timedelta
import json
import logging
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit, urlunsplit


def endpoint(value: str) -> str:
    """Validate URLs without logging credentials."""
    parts = urlsplit(value)
    if parts.scheme not in ('http', 'https') or not parts.hostname or parts.username or parts.password or parts.fragment:
        raise ValueError('Use an HTTP(S) URL without userinfo or a fragment')
    _ = parts.port
    return value


def display_url(value: str) -> str:
    """Never include query values in diagnostics."""
    p = urlsplit(value)
    return urlunsplit((p.scheme, p.netloc, p.path, '', ''))


def version(command: str) -> str | None:
    """Read a client version without printing arbitrary command output."""
    binary = shutil.which(command)
    if not binary:
        return None
    try:
        result = subprocess.run([binary, '--version'], capture_output=True, text=True, timeout=5)
        match = re.search(r'\b(\d+\.\d+(?:\.\d+)?)\b', result.stdout)
        return match.group(1) if match else 'unknown'
    except (OSError, subprocess.TimeoutExpired):
        return 'unknown'


def paths(home: Path) -> dict[str, Path]:
    """Find existing global files before choosing current defaults."""
    oc = Path(os.environ.get('XDG_CONFIG_HOME', str(home / '.config'))) / 'opencode'
    # --home isolates fixtures from real user paths, including XDG overrides.
    if home != Path.home():
        oc = home / '.config/opencode'
    ag = home / '.gemini/config/mcp_config.json'
    legacy = home / '.gemini/antigravity/mcp_config.json'
    return {
        'codex': (Path(os.environ.get('CODEX_HOME', str(home / '.codex'))) if home == Path.home() else home / '.codex') / 'config.toml',
        'antigravity': ag if ag.exists() or not legacy.exists() else legacy,
        'opencode': next((oc / n for n in ('opencode.json', 'opencode.jsonc') if (oc / n).exists()), oc / 'opencode.json'),
    }


def load_config(path: Path, client: str):
    """Parse configs strictly enough to prevent accidental overwrite."""
    import json5
    import tomlkit
    source = path.read_text(encoding='utf-8') if path.exists() else ''
    data = tomlkit.parse(source) if client == 'codex' else json5.loads(source or '{}', allow_duplicate_keys=False)
    if not isinstance(data, dict):
        raise ValueError('Configuration root must be an object')
    return data


def atomic_write(path: Path, content: str, expected: bytes | None) -> str | None:
    """Backup exact original bytes and atomically replace a configuration."""
    path.parent.mkdir(parents=True, exist_ok=True)
    original = path.read_bytes() if path.exists() else None
    if original != expected:
        raise ValueError('Configuration changed since reading; retry after inspecting it')
    backup = None
    if original is not None:
        fd, backup = tempfile.mkstemp(prefix=path.name + '.backup-', dir=path.parent)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(original)
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        # Avoid overwriting concurrent client edits.
        current = path.read_bytes() if path.exists() else None
        if current != original:
            raise ValueError('Configuration changed during update; retry after inspecting it')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return backup


def configure(args) -> dict:
    """Merge one server while preserving unrelated settings."""
    import tomlkit
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}', args.name):
        raise ValueError('Use a short alphanumeric server name with hyphens/underscores')
    if args.token_env and not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', args.token_env):
        raise ValueError('Invalid environment variable name')
    if args.token_env and args.client == 'antigravity':
        raise ValueError('Configure Antigravity authentication using its documented native mechanism')
    path = args.config or paths(args.home)[args.client]
    if path.is_symlink():
        raise ValueError('Resolve the configuration symlink explicitly with --config')
    expected = path.read_bytes() if path.exists() else None
    data = load_config(path, args.client)
    if args.client == 'codex':
        servers = data.setdefault('mcp_servers', {})
        entry = {'url': args.url, 'enabled': True}
        if args.token_env:
            entry['bearer_token_env_var'] = args.token_env
    elif args.client == 'antigravity':
        servers = data.setdefault('mcpServers', {})
        entry = {'serverUrl': args.url, 'disabled': False}
    else:
        schema = args.opencode_schema
        if schema == 'auto':
            installed = version('opencode')
            if not installed or installed == 'unknown':
                raise ValueError('Cannot detect OpenCode version; inspect CLI/schema and specify --opencode-schema v1 or v2')
            schema = 'v2' if int(installed.split('.')[0]) >= 2 else 'v1'
        mcp = data.setdefault('mcp', {})
        servers = mcp.setdefault('servers', {}) if schema == 'v2' else mcp
        entry = {'type': 'remote', 'url': args.url}
        entry.update({'disabled': False} if schema == 'v2' else {'enabled': True})
        if args.token_env:
            entry['headers'] = {'Authorization': 'Bearer {env:' + args.token_env + '}'}
            entry['oauth'] = False
    if not isinstance(servers, dict):
        raise ValueError('Server configuration must be an object')
    existing = servers.get(args.name)
    if existing is not None:
        if isinstance(existing, dict) and all(existing.get(k) == v for k, v in entry.items()):
            return {'client': args.client, 'config': str(path), 'configuration': 'unchanged', 'client_loaded': 'not_verified'}
        if not args.replace:
            raise ValueError('Existing server differs; inspect it and use --replace only for the requested replacement')
    servers[args.name] = entry
    result = {'client': args.client, 'config': str(path), 'configuration': 'planned', 'url': display_url(args.url), 'client_loaded': 'not_verified'}
    if args.apply:
        # JSONC comments require a surgical agent edit; never silently erase them.
        if path.suffix == '.jsonc':
            raise ValueError('Use a comment-preserving editor for JSONC, then run check-config')
        if args.client != 'codex' and expected:
            try:
                json.loads(expected)
            except (ValueError, UnicodeError):
                raise ValueError('Use a comment-preserving editor for non-strict JSON, then run check-config') from None
        content = tomlkit.dumps(data) if args.client == 'codex' else json.dumps(data, indent=2, ensure_ascii=False) + '\n'
        result['backup'] = atomic_write(path, content, expected)
        load_config(path, args.client)
        result['configuration'] = 'saved'
    return result


async def inventory(session, method: str, attribute: str) -> list:
    """Read paginated capability inventories with a bounded loop."""
    items = []
    cursor = None
    for _ in range(100):
        page = await getattr(session, method)(cursor=cursor)
        items.extend(getattr(page, attribute))
        cursor = page.nextCursor
        if not cursor:
            return items
    raise ValueError('Pagination exceeded 100 pages')


async def probe_one(url: str, args) -> dict:
    """Perform the SDK lifecycle and inventory only advertised capabilities."""
    from mcp import ClientSession
    from mcp.client.sse import sse_client
    from mcp.client.streamable_http import streamablehttp_client
    headers = {}
    if args.token_env:
        token = os.environ.get(args.token_env)
        if not token:
            raise ValueError('The requested token environment variable is not set')
        headers['Authorization'] = 'Bearer ' + token
    context = (sse_client(url, headers=headers, timeout=args.timeout)
               if args.transport == 'sse' else
               streamablehttp_client(url, headers=headers, timeout=timedelta(seconds=args.timeout)))
    async with asyncio.timeout(args.timeout):
        async with context as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                initialized = await session.initialize()
                caps = initialized.capabilities
                result = {'url': display_url(url), 'transport': args.transport, 'protocol': initialized.protocolVersion,
                          'handshake': 'passed', 'authentication': 'accepted_for_this_session',
                          'tools': [], 'resources': [], 'prompts': [], 'client_loaded': 'not_verified', 'tool_call': 'not_run'}
                for capability, method, attribute in [('tools', 'list_tools', 'tools'), ('resources', 'list_resources', 'resources'), ('prompts', 'list_prompts', 'prompts')]:
                    if getattr(caps, capability, None) is not None:
                        objects = await inventory(session, method, attribute)
                        result[capability] = [getattr(obj, 'name', None) or str(getattr(obj, 'uri', '')) for obj in objects]
                if args.call:
                    if args.call not in result['tools']:
                        raise ValueError('Requested tool is not advertised')
                    response = await session.call_tool(args.call, json.loads(args.arguments))
                    result['tool_call'] = 'failed' if response.isError else 'passed'
                    # Tool content may contain secrets; report metadata only.
                return result


async def probe(args) -> dict:
    """Try only the supplied URL unless root discovery is requested."""
    logging.disable(logging.CRITICAL)  # HTTP exceptions may embed credential-bearing URLs.
    if args.call and args.discover:
        raise ValueError('Discover the endpoint first, then run one explicit tool call')
    candidates = [args.url]
    p = urlsplit(args.url)
    if args.discover and p.path in ('', '/') and not p.query:
        candidates += [urlunsplit((p.scheme, p.netloc, path, '', '')) for path in ('/mcp', '/mcp/')]
    attempts = []
    for url in candidates:
        try:
            result = await probe_one(url, args)
            result['attempts'] = attempts
            return result
        except Exception as exc:
            # SDK/HTTP exceptions can embed auth headers, query strings or content.
            attempts.append({'url': display_url(url), 'error_type': type(exc).__name__})
    return {'handshake': 'failed', 'attempts': attempts, 'client_loaded': 'not_verified', 'tool_call': 'not_run',
            'next': 'Inspect port/transport/authentication using redacted diagnostics; no configuration was changed'}


def parser() -> argparse.ArgumentParser:
    """Build the command line interface."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--home', type=Path, default=Path.home(), help='Alternate home for isolated tests')
    commands = p.add_subparsers(dest='command', required=True)
    commands.add_parser('doctor')
    check = commands.add_parser('check-config')
    check.add_argument('--client', choices=['codex', 'antigravity', 'opencode'], required=True)
    check.add_argument('--config', type=Path)
    config = commands.add_parser('configure')
    config.add_argument('--client', choices=['codex', 'antigravity', 'opencode'], required=True)
    config.add_argument('--config', type=Path)
    config.add_argument('--name', required=True)
    config.add_argument('--url', type=endpoint, required=True)
    config.add_argument('--token-env')
    config.add_argument('--opencode-schema', choices=['auto', 'v1', 'v2'], default='auto')
    config.add_argument('--apply', action='store_true')
    config.add_argument('--replace', action='store_true')
    remote = commands.add_parser('probe')
    remote.add_argument('--url', type=endpoint, required=True)
    remote.add_argument('--transport', choices=['http', 'sse'], default='http')
    remote.add_argument('--discover', action='store_true')
    remote.add_argument('--timeout', type=float, default=12)
    remote.add_argument('--token-env')
    remote.add_argument('--call', help='Only a tool whose execution the task authorizes')
    remote.add_argument('--arguments', default='{}')
    return p


def main() -> int:
    """Print sanitized JSON and a meaningful exit status."""
    args = parser().parse_args()
    try:
        if args.command == 'doctor':
            result = {'python': sys.version.split()[0], 'clients': {
                name: {'version': version('agy' if name == 'antigravity' else name), 'config': str(path), 'exists': path.exists()}
                for name, path in paths(args.home).items()}, 'skill': str(Path(__file__).resolve().parents[1])}
        elif args.command == 'check-config':
            path = args.config or paths(args.home)[args.client]
            if not path.exists():
                raise ValueError('Configuration does not exist')
            load_config(path, args.client)
            result = {'config': str(path), 'syntax': 'valid', 'client_loaded': 'not_verified'}
        elif args.command == 'configure':
            result = configure(args)
        else:
            if args.timeout <= 0:
                raise ValueError('Timeout must be positive')
            result = asyncio.run(probe(args))
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1 if result.get('handshake') == 'failed' or result.get('tool_call') == 'failed' else 0
    except Exception as exc:
        # Only our own ValueErrors contain deliberately sanitized diagnostics.
        detail = str(exc) if type(exc) is ValueError else 'Inspect configuration or dependency compatibility; input was not printed'
        print(json.dumps({'error_type': type(exc).__name__, 'detail': detail}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
