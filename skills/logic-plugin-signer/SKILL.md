---
name: logic-plugin-signer
version: 1.1.0
description: Inspect, de-quarantine, and ad-hoc sign trusted macOS audio plugins (AU, VST3, CLAP, VST, Standalone) blocked by Gatekeeper. Use when plugins fail to open in Logic Pro, DAWs, or when the user asks to inspect, approve, or sign audio plugins.
metadata:
  category: audio-engineering
  author: agent
  triggers:
    - sign plugin
    - logic plugin signer
    - audio plugin gatekeeper
    - quarantine audio plugin
    - sign vst3
    - sign au
    - sign clap
    - codesign plugin
    - auval plugin error
---

# Logic Plugin Signer

Inspect, de-quarantine, and ad-hoc sign macOS audio plug-ins (`.component`, `.vst3`, `.clap`, `.vst`, `.app`) without unnecessary prompts or multi-step tool overhead.

## Snelle Uitvoering (Aanbevolen)

Gebruik het meegeleverde script [`plugin_signer.py`](plugin_signer.py) (of de zsh-wrapper [`sign_plugin.zsh`](sign_plugin.zsh)). Dit script herkent plug-ins op naam (ook zonder extensie of uit eerdere inventaris), voert validaties uit en levert beknopte, token-efficiënte markdown-uitvoer.

```bash
# 1. Alleen inspecteren (read-only: Gatekeeper, handtekening, quarantine, architectuur, hash):
python3 plugin_signer.py "PluginNaamOfPad" --action inspect

# 2. Dry-run simulatie van ondertekening:
python3 plugin_signer.py "PluginNaamOfPad" --action sign --dry-run

# 3. Direct ondertekenen (ad-hoc sign + quarantine verwijderen):
python3 plugin_signer.py "PluginNaamOfPad" --action sign --yes

# 4. Alleen quarantine verwijderen (indien handtekening al geldig is):
python3 plugin_signer.py "PluginNaamOfPad" --action approve --yes
```

> **Wrapper alternatief:** `./sign_plugin.zsh --inspect|--approve|--adhoc-sign [--dry-run] PAD`

---

## Richtlijnen & Toestemmingsbeleid

1. **Geen onnodige tussenbevestigingen:**
   Wanneer de gebruiker vraagt om te inspecteren, dry-runnen of signen, voer dit direct uit. Vraag géén interactieve tussenstappen ("typ VERTROUWD") tenzij de opdracht dubbelzinnig is of een systeembestand buiten audio-plug-ins betreft.
2. **Logic Pro vereist Audio Units (`.component`):**
   Logic Pro laadt van nature géén VST3 of CLAP. Het script controleert automatisch of er een gelijkname `.component` (Audio Unit) aanwezig is en meldt dit.
3. **Automatische opsporing:**
   Het script zoekt automatisch in:
   - `~/Library/Audio/Plug-Ins/` & `/Library/Audio/Plug-Ins/`
   - Recente inventaris ([`components.tsv`](components.tsv))
   - Lokale project- en buildmappen
   - Directe paden
4. **Automatische ledger-registratie:**
   Bij `--action sign` of `--action approve` wordt de plug-in automatisch geregistreerd in [`components.tsv`](components.tsv) met naam, type, absoluut pad en binary SHA-256 hash.

---

## Foutafhandeling

- **Operation not permitted:** macOS sandbox of Terminal mist Full Disk Access. Voer uit met `BypassSandbox: true` of controleer privacy-instellingen.
- **AU Validation faalt na signing:** Herstart Logic Pro en run `killall -9 AudioComponentRegistrar` om de macOS AU-cache te verversen.
