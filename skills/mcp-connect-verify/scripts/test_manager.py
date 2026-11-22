#!/usr/bin/env python3
"""Exercise isolated config updates and an actual loopback MCP server."""
from __future__ import annotations

import asyncio
from argparse import Namespace
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest

import mcp_manager as manager


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)

    def args(self, client='codex', **overrides):
        values = dict(home=self.home, client=client, config=None, name='demo', url='http://127.0.0.1:3900/mcp',
                      token_env=None, opencode_schema='v2', apply=True, replace=False)
        values.update(overrides)
        return Namespace(**values)

    def test_all_adapters_and_idempotency(self):
        for client in ('codex', 'antigravity', 'opencode'):
            with self.subTest(client=client):
                args = self.args(client)
                result = manager.configure(args)
                self.assertEqual(result['configuration'], 'saved')
                path = Path(result['config'])
                before = path.read_bytes()
                self.assertEqual(manager.configure(args)['configuration'], 'unchanged')
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(manager.load_config(path, client).get('mcp_servers' if client == 'codex' else 'mcpServers' if client == 'antigravity' else 'mcp') is not None, True)

    def test_backup_and_preserve_unrelated_toml(self):
        path = manager.paths(self.home)['codex']
        path.parent.mkdir(parents=True)
        original = b'# retain this comment\nmodel = "existing"\n[mcp_servers.other]\nurl = "https://other.example/mcp"\n'
        path.write_bytes(original)
        result = manager.configure(self.args())
        self.assertEqual(Path(result['backup']).read_bytes(), original)
        self.assertIn('# retain this comment', path.read_text())
        config = manager.load_config(path, 'codex')
        self.assertEqual(config['model'], 'existing')
        self.assertIn('other', config['mcp_servers'])

    def test_plan_does_not_write(self):
        manager.configure(self.args(apply=False))
        self.assertFalse(manager.paths(self.home)['codex'].exists())

    def test_conflict_is_not_overwritten(self):
        manager.configure(self.args())
        path = manager.paths(self.home)['codex']
        original = path.read_bytes()
        with self.assertRaises(ValueError):
            manager.configure(self.args(url='https://different.example/mcp'))
        self.assertEqual(path.read_bytes(), original)

    def test_explicit_replace(self):
        manager.configure(self.args())
        result = manager.configure(self.args(url='https://different.example/mcp', replace=True))
        self.assertTrue(Path(result['backup']).exists())
        self.assertEqual(manager.load_config(Path(result['config']), 'codex')['mcp_servers']['demo']['url'], 'https://different.example/mcp')

    def test_json_comments_preserved_on_refusal(self):
        for suffix in ('.json', '.jsonc'):
            path = self.home / ('custom' + suffix)
            original = '// important comment\n{"mcpServers": {}}\n'
            path.write_text(original)
            with self.assertRaises(ValueError):
                manager.configure(self.args('antigravity', config=path))
            self.assertEqual(path.read_text(), original)

    def test_bad_config_is_not_overwritten(self):
        path = self.home / 'bad.json'
        path.write_text('{broken')
        with self.assertRaises(ValueError):
            manager.configure(self.args('antigravity', config=path))
        self.assertEqual(path.read_text(), '{broken')

    def test_opencode_v1_and_env_reference(self):
        result = manager.configure(self.args('opencode', opencode_schema='v1', token_env='MCP_TEST_TOKEN'))
        entry = json.loads(Path(result['config']).read_text())['mcp']['demo']
        self.assertTrue(entry['enabled'])
        self.assertEqual(entry['headers']['Authorization'], 'Bearer {env:MCP_TEST_TOKEN}')
        self.assertFalse(entry['oauth'])

    def test_secret_url_redaction_and_validation(self):
        self.assertEqual(manager.display_url('https://example.com/mcp?token=SECRET'), 'https://example.com/mcp')
        for url in ('file:///tmp/a', 'http://user:password@example.com/mcp', 'http://example.com/#secret'):
            with self.assertRaises(ValueError):
                manager.endpoint(url)

    def test_concurrent_change_is_not_overwritten(self):
        path = self.home / 'concurrent.json'
        path.write_text('changed')
        with self.assertRaises(ValueError):
            manager.atomic_write(path, 'new', b'old')
        self.assertEqual(path.read_text(), 'changed')


class ProtocolTests(unittest.TestCase):
    def test_real_handshake_inventory_call_and_endpoint_discovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', 0))
                port = sock.getsockname()[1]
            server = Path(tmp) / 'server.py'
            server.write_text('''from mcp.server.fastmcp import FastMCP
mcp = FastMCP("skill-test", host="127.0.0.1", port=PORT, stateless_http=True)
@mcp.tool()
def health() -> str:
    """Return a read-only health result."""
    return "healthy"
@mcp.resource("test://status")
def status() -> str:
    return "ready"
@mcp.prompt()
def greet() -> str:
    return "Hello"
mcp.run(transport="streamable-http")
'''.replace('PORT', str(port)))
            process = subprocess.Popen([sys.executable, str(server)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                for _ in range(100):
                    if process.poll() is not None:
                        self.fail('MCP test server exited before accepting a connection')
                    try:
                        with socket.create_connection(('127.0.0.1', port), timeout=.1):
                            break
                    except OSError:
                        time.sleep(.05)
                else:
                    self.fail('MCP test server did not start')
                args = Namespace(url=f'http://127.0.0.1:{port}/', transport='http', discover=True, timeout=5,
                                 token_env=None, call=None, arguments='{}')
                result = asyncio.run(manager.probe(args))
                self.assertEqual(result['handshake'], 'passed', result)
                self.assertTrue(result['url'].endswith('/mcp'))
                self.assertIn('health', result['tools'])
                self.assertIn('status', result['resources'])
                self.assertIn('greet', result['prompts'])
                self.assertEqual(result['client_loaded'], 'not_verified')
                args.url = result['url']
                args.discover = False
                args.call = 'health'
                result = asyncio.run(manager.probe(args))
                self.assertEqual(result['tool_call'], 'passed', result)
                args.call = None
                args.url = f'http://127.0.0.1:{port}/missing?token=SECRET'
                result = asyncio.run(manager.probe(args))
                self.assertEqual(result['handshake'], 'failed')
                self.assertNotIn('SECRET', json.dumps(result))
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
