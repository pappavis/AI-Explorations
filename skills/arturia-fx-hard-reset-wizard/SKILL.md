---
name: arturia-fx-hard-reset-wizard
description: Diagnostiseer, herstel en ouditeer ontbrekende presets vir Arturia FX Collection-inproppe in Logic Pro op macOS. Los die Apple PackageKit shove cross-device symlink bug, ontbrekende fabrieks-presets en SQLite db.db3 indekseringsfoute op met outomatiese CDN-herstel en auval-validering.
---

# Arturia FX Collection — Hard Reset & Preset Herstel

Hierdie vaardigheid herstel ontbrekende fabrieks-presets in Arturia FX Collection-inproppe (soos *Delay BRIGADE*, *Chorus JUN-6*, *Rev LX-24*, ens.) in Logic Pro en ander macOS DAWs. Dit los stelselprobleme op waar die inprop oopmaak, maar die preset-kieser 0 items vertoon.

## Kernoorsaak in 'n Neutedop
Wanneer `/Library/Arturia` 'n simboliese skakel is na 'n eksterne volume (bv. `/Volumes/data1/Library/Arturia`):
1. Wis die installeerder se `preinstall`-skrif die ou presets uit (`rm -rf ...`).
2. Weier Apple se PackageKit (`shove`) weens sandkas-sekuriteit om nuwe lêers oor 'n *cross-device symlink* te skryf (`Operation not permitted`).
3. Gevolglik bly die fabrieksmappe leeg en faal Arturia se databasis-indeksering (`postdbc_ko.info`).

Sien die volledige tegniese ontleding in [references/ROOT_CAUSE.md](file:///Users/michiele/.agents/skills/arturia-fx-hard-reset-wizard/references/ROOT_CAUSE.md).

---

## Snelle Aksies (Drie Knoppies)

Bied altyd eers die volgende keuses aan die gebruiker:

- **(A) OUDITEER EN HERSTEL ALLES**: Ouditeer alle 39 FX-inproppe en herstel enige ontbrekende fabrieks-presets outomaties via die amptelike CDN.
- **(B) HERSTEL ENKELE FX**: Vra die gebruiker watter spesifieke inprop (bv. *Delay BRIGADE*) herstel moet word.
- **(STOP) KANSELLEER**: Geen stelselveranderings nie.

---

## Aanbevole Herstelwerkvloei

### Stap 1: Voorvlug en Diagnostiese Oudit
Sluit eers Logic Pro en Arturia Software Center:
```bash
killall "Logic Pro" "Arturia Software Center" 2>/dev/null || true
```

Voer die ingeboude oudit uit om te sien watter inproppe ontbrekende fabrieks-presets het:
```bash
python3 scripts/restore_arturia_fx.py --audit
```

### Stap 2: Voer Herstel uit
Die ingeboude Python-hulpmiddel laai die amptelike `__resources.pkg`-bundels regstreeks af vanaf Arturia se CDN, pak dit uit met `pkgutil --expand-full` (omseil Apple PackageKit se sandkas-beperkings), korrigeer geneste vouers en dateer `db.db3` op met `databaseCreator`.

- **Vir alle inproppe gelyktydig**:
  ```bash
  python3 scripts/restore_arturia_fx.py --all
  ```
- **Vir 'n enkele inprop**:
  ```bash
  python3 scripts/restore_arturia_fx.py --product "Delay BRIGADE"
  ```
- **Om herstel te forseer** (selfs as presets reeds bestaan):
  ```bash
  python3 scripts/restore_arturia_fx.py --product "Delay BRIGADE" --force
  ```

### Stap 3: Valideer Audio Units (`auval`)
Toets of macOS CoreAudio die inprop suksesvol valideer:
```bash
# Toets 'n spesifieke inprop:
./scripts/test_auval_fx.sh "Delay BRIGADE"

# Of toets alle geïnstalleerde FX-inproppe:
./scripts/test_auval_fx.sh
```
Die afvoer moet `PASS` aandui.

### Stap 4: Logic Pro Eindaanvaarding
1. Maak Logic Pro oop.
2. Laai die herstelde inprop op 'n spoor (*Audio FX > Audio Units > Arturia > [Produk]*).
3. Open die inprop-koppelvlak en klik op die preset-kieslys.
4. **Kriteria vir Voltooiing**: Fabrieks-presets is sigbaar, kan gekies en gelaai word sonder foute.

---

## Verwysingsgidse en Hulpmiddels

- [scripts/restore_arturia_fx.py](file:///Users/michiele/.agents/skills/arturia-fx-hard-reset-wizard/scripts/restore_arturia_fx.py): Generiese, outonome Python CLI-herstelwerktuig.
- [scripts/test_auval_fx.sh](file:///Users/michiele/.agents/skills/arturia-fx-hard-reset-wizard/scripts/test_auval_fx.sh): Outomatiese AU-valideringskrip via Apple se `auval`.
- [references/ROOT_CAUSE.md](file:///Users/michiele/.agents/skills/arturia-fx-hard-reset-wizard/references/ROOT_CAUSE.md): Diepgaande verduideliking van PackageKit `shove`, sandkas-beperkings en `postdbc_ko.info`.
- [references/COMMANDS_AND_CLI.md](file:///Users/michiele/.agents/skills/arturia-fx-hard-reset-wizard/references/COMMANDS_AND_CLI.md): Volledige opdraglyn-handleiding insluitend handmatige stappe, SQLite-navrae en foutsporing.
- [references/PROCEDURE.md](file:///Users/michiele/.agents/skills/arturia-fx-hard-reset-wizard/references/PROCEDURE.md): Gedetailleerde 5-fase uitvoeringsprosedure, veiligheidsmaatreëls en terugrolprotokol.
- [references/SOURCES.md](file:///Users/michiele/.agents/skills/arturia-fx-hard-reset-wizard/references/SOURCES.md): Amptelike skakels, historiese konteks en CDN-slugregister vir al 39 FX-produkte.
