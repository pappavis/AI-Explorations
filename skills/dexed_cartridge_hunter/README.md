# Dexed Cartridge Hunter v1.0

Cross-platform, Python standard-library Yamaha DX7 SysEx bank collector.

## Start

```sh
python hunter.py update --limit 10
python hunter.py update
python hunter.py verify
```

Windows may use `py -3 hunter.py update`. Set `destination` in `sources.json` or pass `--destination`. Defaults to `<home>/Downloads/Dexed-Cartridges` on every OS. No pip packages or browser needed.

Sources: https://github.com/visualizersdotnl/Yamaha-DX7-patch-library and https://github.com/asb2m10/dexed . Only these two sources are enabled by default because they have a documented GitHub API retrieval method. Other sites from the research round need direct-download URL verification before enabling.

Validation: 4104-byte Yamaha 32-voice bank only. Valid checksum is not a guarantee of playable sound. Exact-byte SHA256 deduplication. Existing verified files are never overwritten; unsupported SYX stored in rejected folder. Network retries max 2 per request. GitHub unauthenticated API limits can cause errors; report captures them.

## Limitations

GitHub API recursive trees can be truncated; collector refuses such incomplete listings. No automatic scraping of arbitrary sites. No content-based voice-level deduplication. `--include-other` supports `.mid` and `.dx7` inside ZIP archives, not standalone GitHub files. ZIP archives are size bounded, but decompression ratio is not independently checked. `02_DUPLICATES` is reserved rather than populated.
