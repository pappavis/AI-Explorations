# Vliegbasis71 Live Song System — Agent Skill (prototype v0.1)

A portable Agent Skill for the published Vliegbasis71 handbook. This **does not replace** the website or write to the GitHub repository. It adds an agent-readable `SKILL.md` with source-routing and an optional explicit fetch script. It supports Nederlands and Afrikaans.

## Install on your Mac

Unzip to e.g. `~/Downloads/vliegbasis71-live-song-system`. Copy the folder to your global skills directory:

```bash
mkdir -p ~/.agents/skills
cp -R ~/Downloads/vliegbasis71-live-song-system ~/.agents/skills/
```

Or include this folder in a GitHub repository and install with a compatible skills manager. GitHub publication and automatic indexing depend on client settings; they are not done by this ZIP.

## Check the source references

```bash
cd ~/.agents/skills/vliegbasis71-live-song-system
python3 scripts/fetch_references.py --profile core
```

In a compatible agent, try: “Gebruik Vliegbasis71 Live Song System. START. Afrikaans, 5 minute.” Or: “Gebruik Vliegbasis71 se Collaborative Song Method as gehoorsimulator. Audience Mode, Nederlands.”

## Security & permissions

Review this skill before using it. The fetch script performs HTTPS reads of allowlisted Markdown only; it makes no Git writes, never runs remotely downloaded code, and does not access personal files. Network may be blocked; core skill rules still work offline. See the source handbook for detailed method and attribution.

Author of source methodology: Michiel Erasmus / Vliegbasis71. Skill package assembled as a first-draft technical adaptation on 2026-10-24. Source changes are not synced automatically.
