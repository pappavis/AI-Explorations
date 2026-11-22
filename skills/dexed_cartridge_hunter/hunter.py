#!/usr/bin/env python3
"""Cross-platform DX7 SysEx cartridge collector; Python 3.9+, stdlib only."""
import argparse, csv, hashlib, io, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request, zipfile
from datetime import datetime, timezone
from pathlib import Path

AGENT = 'DexedCartridgeHunter/1.0 (personal DX7 archive)'
MAX_FILE = 50 * 1024 * 1024
MAX_ARCHIVE_MEMBER = 10 * 1024 * 1024


def default_destination():
    return Path.home() / 'Downloads' / 'Dexed-Cartridges'


def valid_bank(data):
    return (len(data) == 4104 and data[:2] == b'\xf0\x43' and
            data[2] <= 15 and data[3:6] == b'\x09\x20\x00' and
            data[-1] == 0xf7 and all(b < 128 for b in data[6:-2]) and
            ((sum(data[6:-2]) + data[-2]) & 127) == 0)


def http_get(url, max_bytes=MAX_FILE, attempts=2):
    if urllib.parse.urlsplit(url).scheme != 'https':
        raise ValueError('HTTPS required')
    last = None
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': AGENT, 'Accept': 'application/vnd.github+json, application/octet-stream, */*'})
            with urllib.request.urlopen(req, timeout=25) as response:
                if urllib.parse.urlsplit(response.geturl()).scheme != 'https':
                    raise ValueError('insecure redirect')
                data = response.read(max_bytes + 1)
                if len(data) > max_bytes:
                    raise ValueError('download exceeds size limit')
                return data
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = exc
            if attempt + 1 < attempts:
                time.sleep(1)
    raise last


def github_files(owner, repo, branch='HEAD'):
    # GitHub REST tree API; resolve HEAD via repo metadata to avoid guessing branch.
    if branch == 'HEAD':
        meta = json.loads(http_get(f'https://api.github.com/repos/{owner}/{repo}'))
        branch = meta['default_branch']
    endpoint = f'https://api.github.com/repos/{owner}/{repo}/git/trees/{urllib.parse.quote(branch, safe="")}?recursive=1'
    result = json.loads(http_get(endpoint))
    if result.get('truncated'):
        raise RuntimeError('GitHub tree truncated; source skipped to avoid incomplete scan')
    for item in result.get('tree', []):
        if item.get('type') == 'blob' and Path(item['path']).suffix.lower() in ('.syx', '.zip'):
            path = '/'.join(urllib.parse.quote(p, safe='') for p in item['path'].split('/'))
            yield item['path'], f'https://raw.githubusercontent.com/{owner}/{repo}/{urllib.parse.quote(branch, safe="")}/{path}'


def safe_name(name):
    stem = Path(name.replace('\\', '/').split('/')[-1]).name
    stem = re.sub(r'[^a-zA-Z0-9._-]+', '_', stem).strip('._')[:100]
    return stem or 'unnamed.syx'


def unpack_candidates(name, data, include_other=False):
    if name.lower().endswith('.syx'):
        yield name, data, 'syx'
    elif name.lower().endswith('.zip'):
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for member in archive.infolist():
                if member.is_dir() or member.file_size > MAX_ARCHIVE_MEMBER or member.flag_bits & 1:
                    continue
                ext = Path(member.filename).suffix.lower()
                if ext != '.syx' and not include_other:
                    continue
                if ext not in ('.syx', '.mid', '.dx7'):
                    continue
                with archive.open(member) as fp:
                    content = fp.read(MAX_ARCHIVE_MEMBER + 1)
                if len(content) <= MAX_ARCHIVE_MEMBER:
                    yield member.filename, content, ext.lstrip('.')


def collect(config, destination, include_other=False, limit=0):
    destination = Path(destination).expanduser()
    for sub in ('00_NEW', '01_VERIFIED', '02_DUPLICATES', '03_REJECTED', 'CATALOG', 'REPORTS'):
        (destination / sub).mkdir(parents=True, exist_ok=True)
    catalog_path = destination / 'CATALOG' / 'catalog.json'
    try:
        catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
    except FileNotFoundError:
        catalog = {}
    known = {p.stem.split('__')[0] for p in (destination / '01_VERIFIED').glob('*.syx')}
    known.update(catalog.keys())
    summary = {'downloaded': 0, 'verified_new': 0, 'duplicates': 0, 'rejected': 0, 'other': 0, 'errors': []}
    count = 0
    for source in config['sources']:
        if not source.get('enabled', True):
            continue
        try:
            if source['type'] == 'github':
                candidates = github_files(source['owner'], source['repo'], source.get('branch', 'HEAD'))
            elif source['type'] == 'direct':
                candidates = [(source.get('filename') or Path(urllib.parse.urlsplit(u).path).name, u) for u in source['urls']]
            else:
                raise ValueError('unsupported source type')
            for name, url in candidates:
                if limit and count >= limit:
                    break
                count += 1
                try:
                    blob = http_get(url)
                    summary['downloaded'] += 1
                    for child_name, content, kind in unpack_candidates(name, blob, include_other):
                        digest = hashlib.sha256(content).hexdigest()
                        target_name = digest + '__' + safe_name(child_name)
                        if kind != 'syx':
                            target = destination / '00_NEW' / target_name
                            if not target.exists():
                                target.write_bytes(content)
                            summary['other'] += 1
                            continue
                        if digest in known:
                            summary['duplicates'] += 1
                            continue
                        if valid_bank(content):
                            target = destination / '01_VERIFIED' / target_name
                            target.write_bytes(content)
                            known.add(digest)
                            catalog[digest] = {'file': str(target.relative_to(destination)), 'source': source['id'], 'source_url': url, 'original_name': child_name, 'bytes': len(content), 'collected_at': datetime.now(timezone.utc).isoformat()}
                            summary['verified_new'] += 1
                        else:
                            target = destination / '03_REJECTED' / target_name
                            if not target.exists():
                                target.write_bytes(content)
                            summary['rejected'] += 1
                except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as exc:
                    summary['errors'].append({'source': source['id'], 'file': name, 'error': str(exc)})
            if limit and count >= limit:
                break
        except (OSError, ValueError, RuntimeError, KeyError, urllib.error.URLError) as exc:
            summary['errors'].append({'source': source.get('id', '?'), 'error': str(exc)})
    catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding='utf-8')
    with (destination / 'CATALOG' / 'catalog.csv').open('w', newline='', encoding='utf-8') as out:
        writer = csv.DictWriter(out, fieldnames=['sha256', 'file', 'source', 'source_url', 'original_name', 'bytes', 'collected_at'])
        writer.writeheader()
        for digest, item in sorted(catalog.items()):
            writer.writerow({'sha256': digest, **item})
    report = destination / 'REPORTS' / ('run_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.json')
    report.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description='Download and validate DX7 32-voice SYX banks')
    parser.add_argument('command', choices=['update', 'scan', 'verify'])
    parser.add_argument('--config', type=Path, default=Path(__file__).with_name('sources.json'))
    parser.add_argument('--destination', type=Path, default=None)
    parser.add_argument('--include-other', action='store_true')
    parser.add_argument('--limit', type=int, default=0, help='Max remote files (0 = unlimited)')
    args = parser.parse_args(argv)
    config = json.loads(args.config.read_text(encoding='utf-8'))
    destination = args.destination or Path(config.get('destination') or default_destination())
    if args.command == 'verify':
        files = list((destination / '01_VERIFIED').glob('*.syx'))
        bad = [str(p) for p in files if not valid_bank(p.read_bytes())]
        print(json.dumps({'files': len(files), 'invalid': bad}, indent=2))
        return 1 if bad else 0
    if args.command == 'scan':
        for source in config['sources']:
            if source.get('enabled', True) and source['type'] == 'github':
                try:
                    files = list(github_files(source['owner'], source['repo'], source.get('branch', 'HEAD')))
                    print(f"{source['id']}: {len(files)} candidates")
                except Exception as exc:
                    print(f"{source['id']}: ERROR {exc}", file=sys.stderr)
        return 0
    summary = collect(config, destination, args.include_other, args.limit)
    print(json.dumps(summary, indent=2))
    return 0 if not summary['errors'] else 2


if __name__ == '__main__':
    sys.exit(main())
