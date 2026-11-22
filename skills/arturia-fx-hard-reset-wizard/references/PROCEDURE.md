# Arturia FX Herstel — Uitvoeringsprosedure en Kontrolelys

Hierdie dokument beskryf die volledige 5-fase protokol vir die diagnose, rugsteun, herstel en validering van Arturia FX Collection-presets op macOS.

---

## Fase 1: Omgewing- en Diagnostiese Oudit

Voor enige aksie geneem word, moet die stelseltoestand presies vasgestel word:

1. **Kontroleer prosesse**:
   Maak seker Logic Pro, ander DAWs en Arturia Software Center is heeltemal gesluit:
   ```bash
   killall "Logic Pro" "Arturia Software Center" 2>/dev/null || true
   ```
2. **Kontroleer hulpbrongids en simboliese skakels**:
   ```bash
   ls -ld /Library/Arturia
   # Indien dit 'n simboliese skakel is na bv. /Volumes/data1/Library/Arturia:
   # Verifieer dat die eksterne volume gemount en skryfbaar is:
   DEST=$(readlink /Library/Arturia || echo "/Library/Arturia")
   test -w "$DEST" && echo "Doelwit is skryfbaar" || echo "FOUT: Nie skryfbaar nie"
   ```
3. **Voer die stelselwye oudit uit**:
   Gebruik die ingeboude Python-skrip:
   ```bash
   python3 scripts/restore_arturia_fx.py --audit
   ```
   Dit lys alle 39 FX-produkte, toon watter geïnstalleer is in `/Library/Audio/Plug-Ins/Components`, en tel die aantal fisiese fabrieks-presets.
4. **Kontroleer vir installer-mislukkingmerkers**:
   Kyk of `postdbc_ko.info` bestaan in `/Library/Arturia/[FX Naam]/Install/`. Dit dui op mislukte databasis-indeksering weens ontbrekende lêers tydens die laaste installer-lopie.

---

## Fase 2: Veilige Rugsteun en Kwarantyn

1. **Rugsteun die huidige SQLite-databasis**:
   ```bash
   PRESETS_DIR="$(realpath /Library/Arturia)/Presets"
   BACKUP_DIR="$HOME/Arturia_Backup_$(date +%Y%m%d_%H%M%S)"
   mkdir -p "$BACKUP_DIR"
   
   if [ -f "$PRESETS_DIR/db.db3" ]; then
       cp "$PRESETS_DIR/db.db3" "$BACKUP_DIR/db.db3"
   fi
   ```
2. **Beskerm gebruikersdata**:
   - Gebruikerspresets (`/Library/Arturia/Presets/[FX]/User/`) word **nooit** verwyder of oorskryf nie.
   - Lisensiedata en ASC-aanmeldinligting bly onaangeraak.

---

## Fase 3: Hulpbronherstel via Amptelike CDN

In plaas daarvan om die hele inprop te deïnstalleer (wat weer `preinstall` sal laat hardloop en Apple se PackageKit `shove`-fout sal veroorsaak), herstel ons slegs die ontbrekende `Factory/`-hulpbronne direk vanaf Arturia se amptelike CDN.

### Opsie A: Outomatiese herstel van ALLE ontbrekende produkte
```bash
python3 scripts/restore_arturia_fx.py --all
```

### Opsie B: Herstel van 'n spesifieke enkele inprop (bv. Delay BRIGADE)
```bash
python3 scripts/restore_arturia_fx.py --product "Delay BRIGADE"
```

### Wat die herstelproses agter die skerms doen:
1. Laai die amptelike `[FX]__resources.pkg` af vanaf `https://dl.arturia.net/products/{slug}/soft/components/{pkg}` na 'n tydelike gids.
2. Pak die `.pkg` uit met `/usr/sbin/pkgutil --expand-full`. Dit omseil Apple se installer-sandkas en PackageKit se cross-device symlink-blokkering heeltemal.
3. Ontleed die uitgepakte `Payload/Library/Arturia/Presets/[FX]/Factory/`.
4. **Vouernesting-regstelling**: Indien die pakket 3 vlakke diep geneste vouers bevat (`Factory/Factory/Factory/`), kollapseer die skrip dit na die standaard 2 vlakke (`Factory/Factory/`).
5. Plaas die fabrieks-presetlêers in die regte teikengids op die stelsel of eksterne skyf.
6. Stel korrekte toestemmings (`chmod -R 755`).

---

## Fase 4: Databasis-herbouing en Indeksering

Sodra die fisiese presetlêers op die skyf geplaas is, moet Arturia se SQLite-indeks (`db.db3`) bygewerk word.

1. **Gebruik Arturia se eie `databaseCreator`-nutsding**:
   Die `databaseCreator`-binaarlêer is geleë in `/Library/Arturia/Presets/databaseCreator`.
2. **Indekseer die herstelde produk**:
   ```bash
   cd "$PRESETS_DIR"
   ./databaseCreator -u -p "./$FX" -i "$FX" -d "./db.db3"
   ```
3. **Verifieer die databasistoename**:
   Kontroleer met `sqlite3` dat die presets suksesvol geregistreer is:
   ```bash
   sqlite3 "$PRESETS_DIR/db.db3" "SELECT COUNT(*) FROM presets WHERE product_id = '$FX';"
   ```

---

## Fase 5: Aanvaardingstoetsing & Validering

Die herstel is eers afgehandel wanneer sowel die stelselvalidering as die DAW-gebruikerservaring geverifieer is.

### 1. Audio Unit Validering (`auval`)
Voer die ingeboude valideringskrip uit om seker te maak macOS en CoreAudio aanvaar die inproppe sonder foute:
```bash
# Valideer 'n enkele inprop:
./scripts/test_auval_fx.sh "Delay BRIGADE"

# Of valideer alle geïnstalleerde Arturia FX-inproppe:
./scripts/test_auval_fx.sh
```
Die verslag moet `* * PASS` aandui vir die getoetste inproppe.

### 2. Logic Pro Aanvaardingstoets
1. Maak Logic Pro oop.
2. Voeg 'n audiospoor by en voeg die herstelde effek in as 'n Audio FX-inprop (bv. *Audio Units > Arturia > Delay BRIGADE*).
3. Maak die Arturia-inpropvenster oop.
4. Klik op die preset-kieser / biblioteek-ikoon links bo.
5. **Kriteria vir SUKSES**:
   - Die lys toon alle fabrieks-kategorieë (bv. *Default, Slapback, Echoes, Modulated, Ambient, Creative*).
   - Die presets kan aangeklik en gelaai word.
   - Geen fouthaakplekke of leë biblioteekskerms verskyn nie.

---

## Terugrolprosedure (Rollback)

Indien 'n probleem opduik of die gebruiker die proses wil kanselleer:
1. Sluit Logic Pro en ASC.
2. Herstel die vorige databasis:
   ```bash
   if [ -f "$BACKUP_DIR/db.db3" ]; then
       cp "$BACKUP_DIR/db.db3" "$PRESETS_DIR/db.db3"
   fi
   ```
3. Verwyder die tydelike aflaailêers in `/tmp/arturia_recovery_*`.
