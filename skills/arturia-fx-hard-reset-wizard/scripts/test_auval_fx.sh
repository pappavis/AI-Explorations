#!/usr/bin/env bash
#
# test_auval_fx.sh — Toets Audio Unit-validering (auval) vir Arturia FX-inproppe
#

set -e

AU_DIR="/Library/Audio/Plug-Ins/Components"

validate_component() {
    local comp="$1"
    local plist="$comp/Contents/Info.plist"
    
    if [ ! -f "$plist" ]; then
        return 0
    fi
    
    local name
    name=$(basename "$comp" .component)
    
    # Lees AudioComponents uit Info.plist
    local type subtype manu
    type=$(plutil -extract AudioComponents.0.type raw "$plist" 2>/dev/null || true)
    subtype=$(plutil -extract AudioComponents.0.subtype raw "$plist" 2>/dev/null || true)
    manu=$(plutil -extract AudioComponents.0.manufacturer raw "$plist" 2>/dev/null || true)
    
    if [ -n "$type" ] && [ -n "$subtype" ] && [ -n "$manu" ]; then
        echo -n "Valideer AU: $name ($type $subtype $manu) ... "
        if auval -v "$type" "$subtype" "$manu" > /tmp/auval_last.log 2>&1; then
            echo "PASS"
        else
            echo "FAIL (sien /tmp/auval_last.log)"
        fi
    fi
}

if [ -n "$1" ]; then
    TARGET="$AU_DIR/$1.component"
    if [ -d "$TARGET" ]; then
        validate_component "$TARGET"
    else
        validate_component "$1"
    fi
else
    echo "================================================="
    echo " Valideer alle geïnstalleerde Arturia FX Audio Units"
    echo "================================================="
    for comp in "$AU_DIR"/*.component; do
        bname=$(basename "$comp" .component)
        # Slegs Arturia FX
        case "$bname" in
            Bus*|Chorus*|Comp*|Delay*|Dist*|Efx*|EQ*|Filter*|Flanger*|Mix*|Phaser*|Pitch*|Pre*|Rev*|Rotary*|Tape*)
                validate_component "$comp"
                ;;
        esac
    done
fi
