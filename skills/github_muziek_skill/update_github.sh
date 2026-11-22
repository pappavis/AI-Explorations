#!/usr/bin/env bash
# Versie: 1.0.0 | Release ChatID: 20261101-8C3A1F20
set -uo pipefail
ROOT="${MUSIC_REPOS_ROOT:-/Volumes/data1/AI_Gerelateerd/github/muziek_gerelateerd}"
REPORT="${MUSIC_REPORT_DIR:-$HOME/Library/Logs/muziek-github-updater}"
mkdir -p "$REPORT"
STAMP=$(date +%Y%m%d-%H%M%S)
LOG="$REPORT/$STAMP.log"; CSV="$REPORT/$STAMP.csv"
exec > >(tee -a "$LOG") 2>&1
printf 'projek,status,voor,na,bou\n' > "$CSV"
PROJECTS=(Lemon-Studio ACE-Step-1.5 heartlib t3 RC-stable-audio-tools muscriptor symphonygen YuE chord-seq-ai-app tegridy-tools ACE-Step ComposerAI MiniMax-Music3 NeuralNote theDAW)
TOTAL=${#PROJECTS[@]}; N=0; FAIL=0
log(){ printf '%s %s\n' "$(date +%H:%M:%S)" "$*"; }
record(){ printf '%s,%s,%s,%s,%s\n' "$1" "$2" "$3" "$4" "$5" >> "$CSV"; }
if [[ ! -d "$ROOT" ]]; then log "FOUT: gids ontbreek: $ROOT"; exit 2; fi
for name in "${PROJECTS[@]}"; do
  ((N+=1)); dir="$ROOT/$name"; log "[$N/$TOTAL] ▶ $name"; status=; build=nie_nodig; before=-; after=-
  if [[ ! -d "$dir" ]] || ! git -C "$dir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    log "  ⚠ Ontbreek of nie 'n Git-repo nie"; record "$name" ontbreek "$before" "$after" "$build"; ((FAIL+=1)); continue
  fi
  before=$(git -C "$dir" rev-parse --short HEAD)
  if [[ -n "$(git -C "$dir" status --porcelain --untracked-files=no)" ]]; then
    log "  ⚠ Plaaslike wysigings: oorgeslaan"; record "$name" plaaslike_wysigings "$before" "$before" "$build"; ((FAIL+=1)); continue
  fi
  if ! git -C "$dir" fetch --quiet; then
    log "  ❌ Fetch misluk"; record "$name" fetch_misluk "$before" "$before" "$build"; ((FAIL+=1)); continue
  fi
  upstream=$(git -C "$dir" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)
  if [[ -z "$upstream" ]]; then
    log "  ⚠ Geen upstream ingestel"; record "$name" geen_upstream "$before" "$before" "$build"; ((FAIL+=1)); continue
  fi
  read -r behind ahead < <(git -C "$dir" rev-list --left-right --count HEAD..."$upstream" | awk '{print $2, $1}')
  if (( ahead > 0 )); then
    log "  ⚠ Plaaslike commits/divergensie: oorgeslaan"; record "$name" divergeer "$before" "$before" "$build"; ((FAIL+=1)); continue
  fi
  if (( behind == 0 )); then
    log "  ✓ Reeds op datum"; record "$name" op_datum "$before" "$before" "$build"; continue
  fi
  if ! git -C "$dir" merge --ff-only "$upstream"; then
    log "  ❌ Fast-forward misluk"; record "$name" update_misluk "$before" "$before" "$build"; ((FAIL+=1)); continue
  fi
  after=$(git -C "$dir" rev-parse --short HEAD); log "  ✓ Bygewerk: $before → $after"
  case "$name" in
    Lemon-Studio)
      if [[ -f "$dir/Cargo.toml" ]] && command -v cargo >/dev/null; then
        log '  🔨 Bou Lemon-Studio (cargo build)'; if (cd "$dir" && cargo build -p os-app --release); then build=geslaag; else build=misluk; ((FAIL+=1)); fi
      else build=oor_geslaan_geen_cargo; fi ;;
    NeuralNote)
      if [[ -f "$dir/CMakeLists.txt" ]] && command -v cmake >/dev/null; then
        log '  🔨 Bou NeuralNote (CMake)'; if cmake -S "$dir" -B "$dir/build" -DCMAKE_BUILD_TYPE=Release && cmake --build "$dir/build" --config Release; then build=geslaag; else build=misluk; ((FAIL+=1)); fi
      else build=oor_geslaan_geen_cmake; fi ;;
  esac
  record "$name" bygewerk "$before" "$after" "$build"
done
log "KLAAR: $TOTAL projekte nagegaan; $FAIL waarskuwings/foute. Verslag: $CSV | Log: $LOG"
(( FAIL == 0 ))
