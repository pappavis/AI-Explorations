# Vliegbasis71 source map / Bronnenkaart

Repository: https://github.com/pappavis/Vliegbasis71-Live-Song-System
Website: https://pappavis.github.io/Vliegbasis71-Live-Song-System/
Canonical raw base: https://raw.githubusercontent.com/pappavis/Vliegbasis71-Live-Song-System/main/

## Profiles and authoritative entry points

### core
- `docs/index.md` — main book index
- `docs/03-De-Vijf-Lagen.md` — fundament, melody, groove, color, freedom (fixed order)
- `docs/live-song-workbench/index.md` — field workbench philosophy
- `docs/live-song-workbench/quick-start.md` — first session and 12-line recipe
- `docs/live-song-workbench/song/keyword-to-lines.md` — 10 keywords / 3–5 chosen / 2–4 word lines
- `docs/live-song-workbench/field/three-five-fifteen-minute-modes.md` — time-boxed modes

### collaborative
- `docs/collaborative-song/index.md` — experimental collaborative song method
- `docs/collaborative-song/master-prompt.md` — training master prompt
- `docs/collaborative-song/ai-project-bootstrap.md` — four separate AI roles
- `docs/collaborative-song/12-line-method.md` — anchor lines and method
- `docs/collaborative-song/facilitator-guide.md` — practice facilitator
- `docs/collaborative-song/ai-practice.md` — role-play coaching

### production
- `docs/live-song-workbench/ai-system/Vliegbasis71 Field Masterprompt.md` — interactive AI field prompt (note: source has incomplete ending)
- `docs/live-song-workbench/ai-system/suno_styles.md` — Suno style references
- `docs/live-song-workbench/song/song-structure.md` — song structure
- `docs/live-song-workbench/song/mantra-12-measure.md` — 12 measure mantra
- `docs/live-song-workbench/music/chord-progressions.md` — chord progressions
- `docs/live-song-workbench/music/rhythm-strumming.md` — rhythm and strumming
- `docs/live-song-workbench/offline/json-contract.md` — machine-readable song JSON

### reference
- `docs/06_Het_kleurenkompas.md` — note-color compass
- `docs/21-Complete_Safe_Notes_Matrix.md` — safe-note matrix
- `docs/22-Begrippenlijst.md` — terms
- `docs/23-Vliegbasis71_kennisbank.md` — knowledge base

## How the agent retrieves chapters

From the skill root:

```bash
python3 scripts/fetch_references.py --profile core
python3 scripts/fetch_references.py --profile collaborative
python3 scripts/fetch_references.py --profile production
python3 scripts/fetch_references.py --profile all
```

The script downloads **only allowlisted text Markdown** to `references/upstream/`, never executes content, and produces a JSON manifest. Requires Python 3.10+ and outbound HTTPS access. If the network is blocked, open the GitHub links in a browser, or clone the repository outside the skill directory and inspect docs locally. Do not guess inaccessible details.

## Design conventions

- Your source MkDocs documentation is the *knowledge source*; this skill is the *agent entry point*.
- Local cached reference pages are a convenience, not guaranteed freshest.
- When different source pages disagree, cite the chosen path and request a decision only if it materially blocks execution.
- Record author approval before publishing a song based on another person's identifiable story.
