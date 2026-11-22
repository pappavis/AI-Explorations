#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "$0")/.." && pwd)"
# Keep dependencies outside the skill so copies remain portable.
cache="${XDG_CACHE_HOME:-$HOME/.cache}/mcp-connect-verify"
py=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; assert sys.version_info >= (3,11)' 2>/dev/null; then
    py="$candidate"; break
  fi
done
if [ -z "$py" ]; then
  if command -v uv >/dev/null 2>&1; then
    uv python install 3.12
    py="$(uv python find 3.12)"
  elif command -v brew >/dev/null 2>&1; then
    HOMEBREW_NO_AUTO_UPDATE=1 brew install python@3.12
    py="$(brew --prefix python@3.12)/bin/python3.12"
  else
    echo 'Python >=3.11 ontbreekt. Installeer Python via de officiële OS-pakketbeheerder en voer dit script opnieuw uit; vraag alleen om benodigde systeemtoestemming.' >&2
    exit 2
  fi
fi
mkdir -p "$cache"
if [ ! -x "$cache/venv/bin/python" ]; then "$py" -m venv "$cache/venv"; fi
fingerprint="$("$py" -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$root/scripts/requirements.txt")"
if [ ! -f "$cache/requirements.sha256" ] || [ "$(cat "$cache/requirements.sha256")" != "$fingerprint" ]; then
  "$cache/venv/bin/python" -m pip --disable-pip-version-check install -r "$root/scripts/requirements.txt" >&2
  printf '%s\n' "$fingerprint" > "$cache/requirements.sha256"
fi
exec "$cache/venv/bin/python" "$root/scripts/mcp_manager.py" "$@"
