# Die Werklike Kernoorsaak van Ontbrekende Arturia FX Presets op macOS

## 1. Oorsig van die Verskynsel
In Logic Pro (en ander macOS DAWs) vertoon Arturia FX-inproppe (soos *Delay BRIGADE*, *Chorus DIMENSION-D*, *Comp FET-76*, ens.) dikwels skielik **0 presets** in die preset-kieslys. Selfs 'n herinstallasie ("Reinstall") via Arturia Software Center (ASC) of die verwydering/herbouing van `db.db3` los die fout nie op nie, of maak dit selfs erger.

---

## 2. Die Drie Gekoppelde Foutmeganismes

### Meganisme A: Cross-Device Simboliese Skakels en Apple PackageKit (`shove`)
Baie gebruikers verskuif hul groot klank- en hulpbronbiblioteke na 'n eksterne volume (bv. `/Volumes/data1/Library/Arturia`) en skep 'n simboliese skakel vanaf `/Library/Arturia`:
```bash
/Library/Arturia -> /Volumes/data1/Library/Arturia
```

Wanneer Arturia Software Center (ASC) 'n inprop aflaai en die macOS-installeerder (`/usr/sbin/installer`) aanroep:
1. Apple se agtergronddiens `installd` laai die pakket in 'n sandkas (`/Library/InstallerSandboxes/`).
2. Die sub-gereedskap **`shove`** skuif die lêers vanaf die tydelike sandkas na die finale teikengids op `/Library/Arturia/...`.
3. Op moderne macOS weier `shove` om 'n simboliese skakel te volg wat na 'n **ander lêerstelsel / eksterne volume** wys (`cross-device symlink`). Dit word deur macOS sandkas-sekuriteit geblokkeer met die fout:
   ```text
   shove: [resolved symlink dest=not openable] error opening resolved_dest=/Volumes/data1/...: Operation not permitted
   shove: Cross device symlink found in shove path, including /Volumes/data1/Library/Arturia/Delay BRIGADE
   ```
4. Gevolglik faal `shove` om die nuwe preset-lêers na die eksterne skyf te skryf.

### Meganisme B: Die `preinstall`-skrif wis bestaande lêers uit
Die Arturia-installeerderpakket bevat egter 'n `preinstall`-skulpskrif wat deur `package_script_service` as `root` uitgevoer word. Hierdie skrif hardloop buite die `shove`-sandkas en voer opdragte soos die volgende uit:
```bash
rm -rf '/Library/Arturia/Presets/Delay BRIGADE/Factory/Factory'
rm -rf '/Library/Arturia/Presets/Delay BRIGADE/Factory/Templates'
rm -rf '/Library/Arturia/Presets/Delay BRIGADE/Factory/Originals'
rm -rf '/Library/Arturia/Presets/Delay BRIGADE/Factory/Stereo'
rm -rf '/Library/Arturia/Presets/Delay BRIGADE/Factory/Mono'
```
**Die gevolg:** Die `preinstall`-skrif wis die bestaande presets suksesvol uit, maar `shove` kan nie die nuwe presets plaas nie. Die gids op skyf word dus heeltemal leeggemaak!

### Meganisme C: `postinstall` en die Databasis-mislukking (`postdbc_ko.info`)
Nadat `shove` gefaal het, hardloop Arturia se `postinstall`-skrif. Dit soek na die nuwe lêers om `databaseCreator` uit te voer:
```bash
check_and_fix_factory_pre_db_creator $2
"$2""Library/Arturia/Presets/databaseCreator" -u -p "./Delay BRIGADE" -i "Delay BRIGADE" -d "./db.db3"
check_and_fix_factory_post_db_creator $2
```
Omdat die gids leeg is:
- Skep `postinstall` die merker `/Library/Arturia/[FX]/Install/postdbc_ko.info` (Post-Database-Creation Knocked Out / Failed).
- Vind `databaseCreator` 0 lêers om te indekseer.
- Bevat `db.db3` 0 rekords vir daardie inprop.

---

## 3. Waarom Algemene Advies Misluk
- **"Rebuild db.db3":** As die fisiese `.preset`-lêers nie op skyf in `/Factory/Factory/` bestaan nie, bou 'n herindeksering bloot 'n leë databasis vir daardie inprop.
- **"Reinstall in ASC":** Elke keer as ASC "Reinstall" uitvoer, herhaal dit presies dieselfde siklus: `preinstall` wis die gids uit, en `shove` faal oor die simlink.
- **"Check Logic AU Cache":** Die probleem lê nie in Logic Pro se AU-kas nie, maar in die afwesigheid van die data wat die Audio Unit-proses probeer laai.

---

## 4. Die Oplossing
Om die probleem permanent en generies op te los:
1. **Omseil Apple se `shove`:** Laai die amptelike `__resources.pkg` direk af vanaf Arturia se CDN (`dl.arturia.net`).
2. **Pak handmatig uit:** Gebruik `pkgutil --expand-full <pkg> <dest>` wat geen sandkas-beperkings het nie.
3. **Plaas lêers direk:** Kopieer die fabrieks-presets regstreeks na die geverifieerde `Presets/[FX]/Factory/Factory/`-gids (met korreksie van Arturia se eie 3-vlak geneste vouer bug).
4. **Indekseer met Arturia se amptelike `databaseCreator`:** Voer `databaseCreator -u -p "./[FX]" -i "[FX]" -d "./db.db3"` uit.
5. **Stel vlae reg:** Vee `postdbc_ko.info` uit en skep `postdbc_ok.info`.
