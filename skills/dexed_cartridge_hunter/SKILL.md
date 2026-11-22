---
name: dexed-cartridge-hunter
description: Automatically collect, validate, deduplicate and catalog Yamaha DX7 32-voice .syx cartridges on macOS, Windows, Linux or Raspberry Pi without browser automation or interactive confirmations.
---

# Dexed Cartridge Hunter

## Objective
Run the bundled deterministic Python helper to collect publicly downloadable Yamaha DX7 32-voice SysEx cartridges. The user authorizes unattended downloading from configured sources. Do not ask for confirmation per file. Never use a browser, Playwright, scraping login sessions, or bypass access controls. Use only public HTTPS endpoints. Do not modify the Dexed installation or any existing patches.

## Requirements
Python 3.9+; standard library only. Works on Windows, macOS, Linux and Raspberry Pi with Python and network access. Run commands from this skill's directory. The helper is `hunter.py`, and sources are in `sources.json`. Never assume shell-specific syntax.

## Default destination
Use the current OS user's `~/Downloads/Dexed-Cartridges` (resolved via `pathlib.Path.home()`), unless `sources.json` has a non-null `destination` or the user passes `--destination`. On headless Linux or Raspberry Pi, the Downloads directory is created if absent. Use an absolute destination path when configuring unattended jobs.

## Commands
- `python hunter.py update` — download and process all configured public sources, no prompts.
- `python hunter.py scan` — list candidate counts from GitHub without downloading cartridges.
- `python hunter.py verify` — recheck files in `01_VERIFIED`.
- `python hunter.py update --destination PATH` — override output directory.
- `python hunter.py update --include-other` — also save `.mid` and `.dx7` files found in ZIPs to `00_NEW`, without declaring them DX7-compatible.
- `python hunter.py update --limit 10` — bounded smoke test.

## Validation and output
Only a single standard 4,104-byte Yamaha DX7 32-voice VMEM SysEx message with `F0 43`, format `09`, 4,096 data bytes, valid 7-bit payload, Yamaha checksum, and `F7` is accepted into `01_VERIFIED`. Everything else is rejected or ignored. Do not convert other SysEx formats silently. SHA-256 deduplicates exact file content. Catalog files are in `CATALOG/catalog.json` and `.csv`; run reports in `REPORTS/`. `03_REJECTED` contains unsupported/invalid `.syx` for manual inspection. `02_DUPLICATES` is reserved; duplicates are counted rather than saved.

## Sources and safety
`sources.json` enables BlackWinny's public CC0 repository and Dexed's public repository. To add a source, use a `github` record with `owner` and `repo`, or a `direct` record with a list of explicit HTTPS `urls` and optional `filename`. Do not add third-party pages as download URLs unless a stable direct downloadable file has been independently verified. No credentials, browser automation, infinite retries or destructive cleanup. Network requests time out and retry at most twice. Respect licensing, service rate limits, and server failures. Record failures and continue with other sources.

## Agent workflow
1. Confirm Python is installed; don't install dependencies.
2. Run `python hunter.py update` from the skill directory.
3. Read the printed JSON summary and latest report; show counts and failed sources.
4. Never assert a bank sounds correct solely because its checksum passes. If the user requests actual Dexed installation, ask for the explicit destination; don't guess it.
