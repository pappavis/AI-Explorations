# M-VAVE Firmware Manager v1.1.0 — B4E29C71

macOS/Linux: `sh scripts/run.sh start` of `sh scripts/run.sh update`.
Windows: `powershell -File scripts/run.ps1 start` of `powershell -File scripts/run.ps1 update`.
Python 3.11+ required; standard library only. `start` discovers direct download links and changes nothing; `update` downloads packages, checks ZIP safety and stages files. All FM-1 archives must expose direct `/api/convert/lib?id=...` hyperlinks; SMK-37 must expose `.zip` hyperlinks. No guessed API or download URLs. If a site uses JavaScript-only links, discovery fails closed: use a verified HTML snapshot or add a verified browser adapter before production. No guarantee that link discovery covers the complete catalog; a non-empty list is NOT proof of completeness. No version metadata is inferred: version is reported as unknown; SHA-256 tracks changes across successful runs. Physical devices are never accessed. Downloads and extraction are NOT firmware flashing.

`--target` overrides destination; `--temp` overrides temporary root. Full downloads happen each update. SMK-37 ZIPs are retained separately. Existing unrelated files are retained. Rollback protects installation files if an install fails, but filesystem/power failures may require recovery.

## v1.2.0 review en beperkingen
- ASCII-rapportage met FM-1/SMK-37 secties, verschillen, status en download-URL's is teruggebracht; onbekende versies worden niet verzonnen.
- `start` is alleen discovery: 'nieuw' betekent ontbrekend in vorige manifest, niet noodzakelijk een nieuwe websitepublicatie.
- Discovery van alle firmware is NIET gegarandeerd door directe HTML-links. De live site kon vanuit deze omgeving niet worden bereikt; bij discoveryfout stopt het programma zonder installatie.
- Alleen SMK-37 ZIP-links van thefirmwarehub.com worden toegelaten; externe uitgeverslinks vereisen een expliciete betrouwbare bronlijst en aparte implementatie.
- Automatische Python-installatie en Playwright fallback zijn nog niet geïmplementeerd. Gebruik Python 3.11+.
- Tests gebruiken lokale fixtures, niet de live website. De firmwareversie is 'onbekend' totdat betrouwbare metadata beschikbaar is.

## v1.4.0 commando's
`./scripts/run.sh start` / `status`: website vs lokaal (geen download).
`./scripts/run.sh refresh`: alleen ontbrekende, gewijzigde of niet-verifieerbare FM-1-pakketten.
`./scripts/run.sh update`: download alle gevonden FM-1-pakketten opnieuw.
Windows: dezelfde opdrachten via `scripts/run.ps1`.
SMK-37 Pro is catalogus-only totdat directe, geverifieerde downloadpakketten beschikbaar zijn. Geen hardware-flash.
Catalogusbron: https://thefirmwarehub.com/catalog.json (schema wordt gecontroleerd, geen endpoints verzonnen).

## Debuglog (v1.4.2)
Iedere run overschrijft `firmware-debug.json` in de projectmap. Terminal toont `[DEBUG]`-voortgang; JSON bevat tijdstempels, stappen, downloads, SHA-256, fouten en eindstatus. Kies een andere locatie met `--debug-json /pad/naar/log.json`. Let op: de log bevat download-URL’s en lokale paden.

## v1.5.0 — Gebruik zonder Python-kennis

**Codex / OpenCode / chat-agent:** zeg "FM-1 Firmware Manager update". De agent leest `SKILL.md`, voert `scripts/run.sh refresh` uit op macOS/Linux of `scripts/run.ps1 refresh` op Windows en toont de uitvoer. "Update alles" gebruikt de `update`-modus. **Een chat zonder lokale computer-/shelltoegang kan de update niet op jouw computer uitvoeren.**

**Grafisch venster:** macOS/Linux `./scripts/gui.sh`; Windows `./scripts/gui.ps1` (Tkinter nodig). Het venster gebruikt hetzelfde Python-script en toont live download- en validatiestappen. Er wordt niets naar hardware geflasht.

**Terminal:** `./scripts/run.sh status`, `./scripts/run.sh refresh`, `./scripts/run.sh update`. Alle opdrachten tonen firmware-ID, versie, bron-URL, ZIP, bestandsgrootte, ZIP-validatie, voortgang en eindrapport. `firmware-debug.json` wordt per run overschreven.

**Belangrijk:** de website toont een aparte FM-1-hardwarebibliotheek en een kleinere VIBE FM VST-conversiebibliotheek. Deze manager werkt op de **VIBE FM-conversiebibliotheek** (`/convert/`), niet op de hardware-flashbestanden. De plugin is niet door deze tests daadwerkelijk geopend of in een DAW getest. De website vermeldt dat recente pluginversies een ZIP direct kunnen importeren; deze manager blijft het oorspronkelijke `.aot/.json/.wasm`-bestandsmodel gebruiken.

**Beperkingen:** De downloadroutes zijn niet live getest in de bouwomgeving; lokale DNS naar `thefirmwarehub.com` werkt daar niet. GUI is niet interactief getest op macOS/Windows. De bestaande engine is bewust niet volledig herschreven om regressierisico te beperken; een volledige class-based refactor zonder moduleconstanten is nog openstaand. De nieuwe `FirmwareGUI` en `ProgressView` zijn wel class-based.

### Status voor eindgebruikers (v1.5.1)
- `./scripts/run.sh status`: compact overzicht (geen downloads).
- `./scripts/run.sh status full`: volledige tabel van alle firmwares, lokale manifestversie, websiteversie en bronlinks.
- `./scripts/run.sh refresh`: alleen ontbrekende/gewijzigde pakketten.
- `./scripts/run.sh update`: alle FM-1 pakketten opnieuw.
- `./scripts/gui.sh`: grafisch venster met statusknop.
Windows: `./scripts/run.ps1` met dezelfde acties.

## Grafisch dashboard (v1.6.0)
Start `./scripts/gui.sh` (Windows `./scripts/gui.ps1`). Het dashboard controleert automatisch de status en toont vier tellers, een zoekbare en filterbare firmwaretabel met website- en lokale manifestversies, en een knop `Nu bijwerken`. Na refresh/update wordt de status opnieuw opgehaald. De technische uitvoer blijft beschikbaar onderaan. `--status-json PAD` exporteert een JSON-statussnapshot vanuit de bestaande CLI zonder bestanden te installeren.
