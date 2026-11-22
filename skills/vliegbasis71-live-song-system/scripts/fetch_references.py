#!/usr/bin/env python3
"""Fetch allowlisted Vliegbasis71 Markdown references without executing them."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'references' / 'upstream'
BASE = 'https://raw.githubusercontent.com/pappavis/Vliegbasis71-Live-Song-System/main/'
PROFILES = {
    'core': [
        'docs/index.md', 'docs/03-De-Vijf-Lagen.md',
        'docs/live-song-workbench/index.md', 'docs/live-song-workbench/quick-start.md',
        'docs/live-song-workbench/song/keyword-to-lines.md',
        'docs/live-song-workbench/field/three-five-fifteen-minute-modes.md',
    ],
    'collaborative': [
        'docs/collaborative-song/index.md','docs/collaborative-song/master-prompt.md',
        'docs/collaborative-song/ai-project-bootstrap.md',
        'docs/collaborative-song/12-line-method.md',
        'docs/collaborative-song/facilitator-guide.md',
        'docs/collaborative-song/ai-practice.md',
    ],
    'production': [
        'docs/live-song-workbench/ai-system/Vliegbasis71 Field Masterprompt.md',
        'docs/live-song-workbench/ai-system/suno_styles.md',
        'docs/live-song-workbench/song/song-structure.md',
        'docs/live-song-workbench/song/mantra-12-measure.md',
        'docs/live-song-workbench/music/chord-progressions.md',
        'docs/live-song-workbench/music/rhythm-strumming.md',
        'docs/live-song-workbench/offline/json-contract.md',
    ],
    'reference': [
        'docs/06_Het_kleurenkompas.md','docs/21-Complete_Safe_Notes_Matrix.md',
        'docs/22-Begrippenlijst.md','docs/23-Vliegbasis71_kennisbank.md',
    ]
}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profile', choices=[*PROFILES, 'all'], default='core')
    args = p.parse_args()
    selected = PROFILES[args.profile] if args.profile != 'all' else sorted(set(sum(PROFILES.values(), [])))
    data = []
    failed = []
    for path in selected:
        url = BASE + quote(path, safe='/')
        try:
            with urlopen(Request(url, headers={'User-Agent': 'Vliegbasis71-Skill-Reference-Fetch/0.1'}), timeout=15) as response:
                contents = response.read(2_000_001)
            if len(contents) > 2_000_000:
                raise ValueError('Markdown > 2 MB; refused')
            contents.decode('utf-8')
            output = (DEST / path).resolve()
            if not output.is_relative_to(DEST.resolve()):
                raise ValueError('path escaped cache folder')
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(contents)
            data.append({'source_path': path, 'sha256': hashlib.sha256(contents).hexdigest(), 'bytes':len(contents),'url':url})
            print('OK  ', path)
        except Exception as exc:
            failed.append({'source_path':path, 'error':str(exc)})
            print('FAIL', path, exc)
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST/'fetch-manifest.json').write_text(json.dumps({'retrieved_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(), 'profile': args.profile,'files':data,'failures':failed},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'Done: {len(data)} OK, {len(failed)} failed. No downloaded code executed.')
    raise SystemExit(1 if failed else 0)

if __name__ == '__main__':
    main()
