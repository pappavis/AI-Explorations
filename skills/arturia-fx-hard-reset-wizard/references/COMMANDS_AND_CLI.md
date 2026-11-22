# Arturia FX Herstel — Shell & CLI Opdragte Handleiding

Hierdie handleiding lys alle getoetste, werkende opdragte wat op enige Mac met Logic Pro gebruik kan word.

---

## 1. Inspeksie en Diagnostiek

### Kontroleer Arturia-hulpbronpad en simboliese skakel
```bash
ls -ld /Library/Arturia
readlink /Library/Arturia 2>/dev/null || echo "Gewone gids (geen simlink)"
```

### Ouditeer alle FX-inproppe met die ingeboude Python-nutsding
```bash
python3 scripts/restore_arturia_fx.py --audit
```

### Tel fisiese preset-lêers vir 'n spesifieke FX
```bash
FX="Delay BRIGADE"
find "/Library/Arturia/Presets/$FX/Factory" -type f ! -name ".*" 2>/dev/null | wc -l
```

### Kontroleer installeerder-mislukkingmerkers
```bash
FX="Delay BRIGADE"
ls -la "/Library/Arturia/$FX/Install"
# Soek vir postdbc_ko.info (dui op mislukte databasis-indeksering weens ontbrekende lêers)
```

---

## 2. Herstel via die Ingeboude Python-skrip

### Herstel ALLE ontbrekende FX-presets gelyktydig
```bash
python3 scripts/restore_arturia_fx.py --all
```

### Herstel slegs een spesifieke FX
```bash
python3 scripts/restore_arturia_fx.py --product "Delay BRIGADE"
```

### Dwing herstel af selfs as lêers reeds bestaan
```bash
python3 scripts/restore_arturia_fx.py --product "Chorus JUN-6" --force
```

---

## 3. Handmatige Herstelproses (Stap-vir-Stap)

As 'n produk handmatig herstel moet word sonder die volledige Python-CLI:

### 1. Laai amptelike Arturia resources-pakket af
```bash
SLUG="delay-brigade"
PKG="Delay_BRIGADE__1_7_1_6566__resources.pkg"
curl -L -o "/tmp/$PKG" "https://dl.arturia.net/products/$SLUG/soft/components/$PKG"
```

### 2. Pak uit sonder Apple-installeerder sandkas
```bash
pkgutil --expand-full "/tmp/$PKG" "/tmp/${SLUG}_exp"
```

### 3. Kopieer fabrieks-presets na Arturia Presets-gids
```bash
PRESETS_DIR="$(realpath /Library/Arturia/Presets)"
mkdir -p "$PRESETS_DIR/Delay BRIGADE/Factory/Factory"

# Hanteer Arturia se 3-vlak geneste gids indien teenwoordig
SRC="/tmp/${SLUG}_exp/Payload/Library/Arturia/Presets/Delay BRIGADE/Factory"
if [ -d "$SRC/Factory/Factory" ]; then
    cp -r "$SRC/Factory/Factory/"* "$PRESETS_DIR/Delay BRIGADE/Factory/Factory/"
elif [ -d "$SRC/Factory" ]; then
    cp -r "$SRC/Factory/"* "$PRESETS_DIR/Delay BRIGADE/Factory/Factory/"
fi

# Kopieer xml en tutorials indien beskikbaar
cp "$SRC/../presets.featured.xml" "$PRESETS_DIR/Delay BRIGADE/" 2>/dev/null || true
cp -r "$SRC/../Tutorials" "$PRESETS_DIR/Delay BRIGADE/" 2>/dev/null || true
```

### 4. Voer Arturia databaseCreator uit om db.db3 by te werk
```bash
DBC="/tmp/${SLUG}_exp/Payload/Library/Arturia/Presets/databaseCreator"
chmod +x "$DBC"
cd "$PRESETS_DIR"
"$DBC" -u -p "./Delay BRIGADE" -i "Delay BRIGADE" -d "./db.db3"
```

### 5. Dateer die statusmerkers op
```bash
BASE_DIR="$(realpath /Library/Arturia)"
rm -f "$BASE_DIR/Delay BRIGADE/Install/postdbc_ko.info"
touch "$BASE_DIR/Delay BRIGADE/Install/postdbc_ok.info"
chmod -R 777 "$PRESETS_DIR/Delay BRIGADE"
```

---

## 4. Databasis-verifikasie via SQLite

### Kontroleer geïndekseerde presets in db.db3
```bash
DB="$(realpath /Library/Arturia/Presets/db.db3)"

# Totaal aantal presets in databasis
sqlite3 "$DB" "SELECT count(*) FROM Preset_Id;"

# Presette vir spesifieke effek
sqlite3 "$DB" "SELECT count(*), name, file_path FROM Preset_Id WHERE file_path LIKE '%Delay BRIGADE%' LIMIT 5;"
```

---

## 5. Audio Unit Validering (`auval`)

### Toets met die ingeboude valideringskrif
```bash
./scripts/test_auval_fx.sh "Delay BRIGADE"
```

### Of voer auval direk uit
```bash
# Delay BRIGADE: type=aumf, subtype=MeBr, manu=Artu
auval -v aumf MeBr Artu

# Chorus JUN-6: type=aumf, subtype=CJU6, manu=Artu
auval -v aumf CJU6 Artu

# Rev LX-24: type=aumf, subtype=LX24, manu=Artu
auval -v aumf LX24 Artu
```

---

## 6. Proses- en Toepassingsbeheer

### Sluit Logic Pro en Arturia-prosesse veilig voor ingryping
```bash
pkill -x "Logic Pro" 2>/dev/null || true
pkill -x "Arturia Software Center" 2>/dev/null || true
pkill -if "Arturia Software Center Agent" 2>/dev/null || true
```

### Begin Logic Pro om herstel visueel te verifieer
```bash
open -a "/Applications/Logic Pro.app"
```
