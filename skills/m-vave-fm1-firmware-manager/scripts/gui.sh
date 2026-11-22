#!/usr/bin/env sh
# Version: 1.6.1 | Release ChatID: E72C9B14
# Select an interpreter that can actually load Tkinter. No changes to firmware engine.
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

has_tk() {
    command -v "$1" >/dev/null 2>&1 || return 1
    "$1" -c 'import tkinter; import _tkinter' >/dev/null 2>&1
}

if [ -n "${PYTHON:-}" ]; then
    if has_tk "$PYTHON"; then
        exec "$PYTHON" "$HERE/firmware_gui.py" "$@"
    fi
    printf '%s\n' "FOUT: PYTHON=$PYTHON kan Tkinter nie laai nie." >&2
else
    for candidate in \
        /opt/homebrew/bin/python3.12 \
        /opt/homebrew/bin/python3.15 \
        /opt/homebrew/bin/python3.14 \
        /opt/homebrew/bin/python3.13 \
        python3.12 python3.15 python3.14 python3.13 python3
    do
        if has_tk "$candidate"; then
            exec "$candidate" "$HERE/firmware_gui.py" "$@"
        fi
    done
fi

printf '%s\n' \
    'M-VAVE GUI: Geen Python met werkende Tkinter gevind nie.' \
    'Jou firmwarebiblioteek is NIE verander nie.' \
    '' \
    'Op macOS met Homebrew Python 3.15:' \
    '    brew install python-tk@3.15' \
    '' \
    'Toets daarna:' \
    '    /opt/homebrew/bin/python3.15 -m tkinter' \
    '    ./scripts/gui.sh' \
    '' \
    'Alternatief vir Python 3.12:' \
    '    brew install python-tk@3.12' >&2
exit 1
