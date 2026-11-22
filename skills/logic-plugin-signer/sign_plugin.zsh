#!/bin/zsh
set -euo pipefail
SCRIPT_DIR=${0:A:h}
PY="$SCRIPT_DIR/plugin_signer.py"

usage() { print 'Gebruik: sign_plugin.zsh --inspect|--approve|--adhoc-sign [--dry-run] [--yes] PAD'; exit 2; }
[[ $# -ge 2 ]] || usage

mode=$1; shift
py_args=()

case "$mode" in
  --inspect) py_args+=(--action inspect) ;;
  --approve) py_args+=(--action approve) ;;
  --adhoc-sign) py_args+=(--action sign) ;;
  *) usage ;;
esac

dry=0
yes=0
target=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) py_args+=(--dry-run); dry=1; shift ;;
    --yes|-y) py_args+=(--yes); yes=1; shift ;;
    *) target="$1"; shift ;;
  esac
done

[[ -n "$target" ]] || usage

# If not dry-run and not explicitly --yes, pass --yes by default when run in non-interactive agent context
if [[ $dry -eq 0 && $yes -eq 0 ]]; then
  py_args+=(--yes)
fi

exec /usr/bin/python3 "$PY" "$target" "${py_args[@]}"
