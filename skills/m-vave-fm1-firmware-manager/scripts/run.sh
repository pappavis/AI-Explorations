#!/usr/bin/env sh
# Version: 1.6.0 | Release ChatID: A61E4C92
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON=${PYTHON:-python3}
ACTION=${1:-start}
shift 2>/dev/null || true
case "$ACTION" in
 status)
   if [ "${1:-}" = "full" ]; then
     shift
     exec "$PYTHON" "$HERE/fm1_update.py" --mode status --status-full "$@"
   fi
   exec "$PYTHON" "$HERE/fm1_update.py" --mode status "$@" ;;
 start) exec "$PYTHON" "$HERE/fm1_update.py" --mode status "$@" ;;
 refresh) exec "$PYTHON" "$HERE/fm1_update.py" --mode refresh "$@" ;;
 update|update-all|alles) exec "$PYTHON" "$HERE/fm1_update.py" --mode update-all "$@" ;;
 *) echo 'Gebruik: run.sh start|status|status full|refresh|update [--target PAD]' >&2; exit 2 ;;
esac
