---
name: m-vave-fm1-firmware-manager
description: Bestuur FM-1 VIBE FM- en SMK-37 Pro-firmwarekatalogusse; start/status, refresh of update alles. Flash nooit hardeware nie.
---
# M-VAVE Firmware Manager
Version: 1.6.0 | Release ChatID: A61E4C92

Bepaal de operating system waarop je draait.

Gebruik uitsluitlik `./scripts/run.sh start|refresh|update` op macOS/Linux/Raspberry Pi; Windows `./scripts/run.ps1 start|refresh|update`. `start` wys status sonder aflaaie. `refresh` laai ontbrekende/veranderde FM-1-pakkette af; `update` laai alle ontdekte FM-1-pakkette opnuut af en oorskryf plaaslike lêers. SMK-37 Pro: hou katalogus/weergawes by, geen hardeware-opdaterings nie; meld installeerders wat nie afgelaai kan word nie. Gebruik geverifieerde bron-skakels, moet nooit ID's uitdink nie. Onvolledige FM-1-ontdekking: stop sonder installasie. Kontroleer ZIP/CRC/pad/grootte/SHA-256; valideer eers alles en installeer daarna atomies met rollback. Bewaar ander lêers en suksesvolle manifestgeskiedenis. Maak net die eie tydelike werkmap skoon. 'n Kleurvolle ASCII-kassie is verpligtend met webwerf/plaaslik voor/na, nuut/veranderd, aflaaie, validering, opruiming en 'Hardware flash NOOIT'; tabelle GEWIJZIGD voor NIEUW met vorige/webwerf/plaaslike weergawes en URL. Meld onbekende weergawes eerlik. Lees README.md. Toetse: `python3 -m unittest discover -s tests -v`.

Wys vordering; skryf by elke uitvoering `firmware-debug.json` opnuut met stappe, keuses, aflaaie, foute en eindstatus. Opsioneel `--debug-json PAD`.

## Agent-opdragte (Codex / OpenCode)
By "FM-1 Firmware Manager update" voer **refresh** uit: `./scripts/run.sh refresh` (Windows `./scripts/run.ps1 refresh`). By "update alles" voer `update` uit. By "status" voer `start` uit. Moenie na standaardvouers vra nie; gebruik die oorspronklike paaie. Wys lewendige vordering en die volledige eindverslag, ook by foute. Geen hardeware-flashing nie. Vir 'n grafiese venster: `./scripts/gui.sh` of `./scripts/gui.ps1`. Indien geen plaaslike uitvoeromgewing beskikbaar is nie, sê dit eerlik; moenie 'n opdatering naboots nie.

## Status-oorsig
`status` wys 'n oorsig met getalle vir nuut, veranderd, aktueel en onbekend. `status full` wys **alle** firmware-ID's met webwerfweergawe, plaaslike manifestweergawe, status en bron-URL. `refresh` laai slegs geselekteerde verskille af; `update` laai alle FM-1-pakkette weer af. By 'n versoek om grafiese status: begin `./scripts/gui.sh` (Windows `./scripts/gui.ps1`) en kies Status. CLI-status is 'n terminaltabel, nie 'n GUI-venster nie. Meld onbekende weergawes eerlik.

## Dashboard v1.6.0
Die grafiese koppelvlak (`./scripts/gui.sh` of `./scripts/gui.ps1`) wys ná 'n outomatiese statuskontrole 'n dashboard met ACTUEEL, BIJWERKEN, NIEUW, ONBEKEND, 'n deursoekbare/filterbare tabel, webwerfweergawe en plaaslike manifestweergawe. `Nu bijwerken` voer refresh uit en kontroleer daarna weer die status. `status` en `status full` bly terminalopdragte; die firmware-enjin bly die enigste bron vir ontdekking, aflaai, ZIP-validering en installasie. Die GUI lees `--status-json` en wys tegniese besonderhede afsonderlik. Meld altyd dat die plaaslike weergawe uit die manifest kom, nie uit 'n lopende plugin nie.


## Platform en werkmap — VERPLIGTEND vir agente
Bepaal **eers** die bedryfstelsel voordat enige skrip uitgevoer word. Op **macOS, Linux en Raspberry Pi OS** gebruik **uitsluitlik** `scripts/gui.sh` vir `gui` en `scripts/run.sh` vir `status`, `status full`, `refresh` en `update`; **moet nooit `.ps1` op hierdie stelsels probeer nie**. Gebruik `.ps1` **slegs op Windows**. Die agent se huidige werkmap kan enige projek wees: `./scripts/gui.sh` is daarom **nie** 'n betroubare pad nie. Vind die werklike gids waarin hierdie `SKILL.md` lê (skill se base directory) en voer die skrip daarvandaan uit, byvoorbeeld op macOS/Linux: `cd "$HOME/.agents/skills/m-vave-fm1-firmware-manager" && ./scripts/gui.sh` wanneer die skill dáár geïnstalleer is. As die skill elders geïnstalleer is, gebruik daardie **werklike** gids; moenie die voorbeeldpad blindelings aanvaar nie. Moet nie by 'n ontbrekende `.sh`-pad na PowerShell oorskakel nie; herstel eers die werkmap/pad. Op Windows: gaan eers na die skillgids en voer `./scripts/gui.ps1` of `./scripts/run.ps1` uit. Behou alle bestaande opdragte, firmwarelogika en verslagdoening.
