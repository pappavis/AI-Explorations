---
name: smk37-unbrick
description: Herstel een M-VAVE SMK-37 Pro na een onderbroken firmware-update, zwart scherm of verdwenen USB/MIDI-verbinding. Voer bereikbare software-recovery uit met een flash-rugsteun en officiële Pro-firmware als terugvaloptie; herken wanneer fysieke USB_KEY-recovery nodig is. Primair voor macOS, niet voor FM-1-firmwarebeheer.
---

# SMK-37 Pro herstellen

Werk naar een aantoonbaar opstartende SMK-37 Pro toe. Doe de computerhandelingen zelf en stel zo weinig mogelijk vragen. Scheid voorbereiding, verbinding, rugsteun, schrijven, verificatie en daadwerkelijk herstel in de verslaglegging.

## Reikwijdte en toestemming

- Gebruik de informatie uit het gesprek. Laat de gebruiker een al beschreven fout of mislukte knoppoging niet opnieuw reconstrueren.
- Een verzoek om te unbricken geeft ruimte om herstel voor te bereiden en uit te voeren. Respecteer expliciete beperkingen, bijvoorbeeld alleen onderzoeken of eerst een preview. Reeds gegeven toestemming binnen het gesprek hoeft niet opnieuw gevraagd te worden.
- Deze skill zelf is geen permanente toestemming om in toekomstige sessies apparaten te flashen. Bij uitsluitend een adviesvraag: onderzoek en adviseer, schrijf geen firmware.
- Bevestig vóór schrijven het doelapparaat via de flasher en het firmwaremodel. Een algemene JieLi-vermelding, USB VID of onbekende USB-schijf is onvoldoende. Raak geen andere MIDI-apparaten, USB-schijven of aangesloten interfaces aan.
- Doel is de **SMK-37 Pro**. Gebruik nooit een FM-1-, Elite- of MKE-pakket als vervanging. Behandel andere modellen als een afzonderlijke opdracht.

## 1. Controleer de huidige bronnen en lokale uitgangssituatie

Lees de actuele primaire documentatie; versies en herstelmogelijkheden kunnen veranderen:

- [M-Flasher](https://github.com/jvitkauskas/m-flasher), [releases](https://github.com/jvitkauskas/m-flasher/releases), [gebruik](https://github.com/jvitkauskas/m-flasher/blob/main/docs/usage.md).
- [Officiële M-VAVE-downloads](https://www.m-vave.com/appdownload): volg de downloadlink bij **SMK-37 PRO**.
- Bij Skiff: [SMK-37-instructies](https://github.com/illuminus5/skiff/blob/main/SMK37.md).
- Alleen voor fysieke recovery: [m-bootloader-specificatie](https://github.com/jvitkauskas/m-bootloader/blob/main/docs/SPEC.md), zoek `USB_KEY`.

Maak een aparte herstelmap in een beschrijfbare gebruikerslocatie. Bewaar daarin hulpmiddelen, bron-URL's, versies, checksums, logbestanden en rugsteunen. Hergebruik bestaande bestanden alleen na controle. Een eerdere download of oudere herstelnotitie bewijst niet dat het apparaat nu bereikbaar is.

Op macOS:

```sh
ioreg -p IOUSB -w 0
```

Gebruik de compacte boom voor opsporing. Lees uitgebreide eigenschappen alleen voor een relevante kandidaat; vermijd volledige systeemdumps met onnodige persoonsgegevens. Zoek ook naar reeds aanwezige M-Flasher-installaties en firmwarebestanden zonder andere bestanden te wijzigen.

## 2. Bereid het herstelgereedschap voor

Download een actuele stabiele M-Flasher-release voor het juiste besturingssysteem vanaf de repository. Vergelijk de download met de gepubliceerde asset-digest indien beschikbaar. Controleer de integriteit van een macOS-DMG en pak de toepassing uit of mount hem alleen-lezen. Installatie in Applications is niet vereist als de lokale app correct draait.

Download de officiële Pro-firmware via M-VAVE. Bewaar het ongewijzigde `.fwsc`-bestand en bereken een SHA-256 voor het dossier. Een zelf berekende hash is een integriteitsregistratie, geen onafhankelijke verificatie van de fabrikant. Laat M-Flasher later ook pakket en model controleren.

Lees de actuele CLI-help vóór gebruik. Voorbeeld met een zelf gekozen app-locatie:

```sh
flasher='/absolute/path/M-Flasher.app/Contents/MacOS/M-Flasher'
"$flasher" --help
"$flasher" find
"$flasher" info
```

Gebruik de vereiste tool-escalatie bij sandbox-, netwerk- of USB-toegangsbeperkingen. Interpreteer een DNS-fout of geweigerde sandboxtoegang niet als een defect apparaat. Laat eventuele macOS-beheerdersauthenticatie via de normale systeemdialoog verlopen; vraag geen wachtwoord in de chat.

## 3. Kies de route op basis van waargenomen bereikbaarheid

| Waarneming | Vervolg |
| --- | --- |
| Skiff toont UPDATE MODE of biedt Felucca Update aan | Volg Skiffs actuele hervatprocedure; laat de installer de onderbroken update afmaken. Gebruik alleen een passend Pro-pakket. |
| M-Flasher herkent het juiste apparaat via MIDI | Gebruik de gedocumenteerde download-mode-functie uitsluitend voor dit apparaat; controleer daarna opnieuw de identiteit in herstelmodus. |
| M-Flasher vindt een WL82 UBOOT-hersteltoestel | Lees informatie, identificeer het bord en maak een rugsteun vóór schrijven. |
| Geen ondersteund USB/MIDI-apparaat gevonden | Voer de begrensde herkoppelroute hieronder uit; flash niets zolang het doel niet bereikbaar en geïdentificeerd is. |
| Meerdere kandidaten, onbekend model of tegenstrijdige informatie | Los de doelidentificatie eerst op. Gebruik geen force-optie of modeloverride om de controle te omzeilen. |

Een leeg Finder-venster bewijst niet dat USB-herstelmodus ontbreekt. UBOOT kan als onbruikbare of lege schijf verschijnen; initialiseer of formatteer die nooit.

Bij geen verbinding: vraag maximaal één noodzakelijke fysieke handeling als die nog niet is uitgevoerd of bevestigd: uitzetten, rechtstreeks met een USB-datakabel aansluiten en weer aanzetten; vervolgens aangesloten laten. Leg kort uit dat de agent dit niet op afstand kan doen. Doe daarna zelf een begrensde observatie en opnieuw `find`/`info`. Geef de gebruiker tijd om de handeling uit te voeren; stilte is geen bevestiging.

Stuur geen generieke SysEx naar alle MIDI-poorten. Reset geen complete USB-controller en herstart de Mac niet automatisch: daar hangen mogelijk andere apparaten en actief werk aan.

## 4. Maak een controleerbare rugsteun

Zodra de juiste SMK-37 Pro bereikbaar is:

1. Lees de flasher-informatie en bewaar model, firmware, bootloader en doelidentificatie.
2. Maak een volledige flash-rugsteun in de herstelmap. Gebruik een tweede onafhankelijke lezing en hashvergelijking als de tool geen gelijkwaardige leesverificatie biedt.
3. Controleer bestandsgrootte en leesresultaat volgens de actuele apparaatspecificatie. Historisch heeft dit model 1 MiB flash; onverwachte waarden vereisen onderzoek, geen automatische override.
4. Bewaar de ongewijzigde dump en metadata vóór elke schrijfpoging. Ook een dump met beschadigde firmware kan unieke kalibratie en Bluetooth-gegevens bevatten.

Als uitlezen of verificatie faalt: stop vóór schrijven en rapporteer de concrete fout. Een download van iemand anders vervangt de eigen fabriekskalibratie niet.

## 5. Herstel de firmware

Gebruik de actuele M-Flasher-firmwarefunctie met het ongewijzigde officiële **Pro**-pakket wanneer terugkeer naar fabrieksfirmware is toegestaan. Lees de voorgestelde wijzigingen en modelcontroles vóór uitvoering. Selecteer bij meerdere apparaten expliciet het geverifieerde doel volgens de actuele toolsyntax.

- Schrijf alleen wat voor herstel nodig is. Vervang de bootloader niet standaard en installeer niet ongevraagd m-bootloader.
- Let op versieafhankelijke standaardinstellingen: M-Flasher 0.7.0 wist in de GUI standaard instellingen en Bluetooth-koppelingen; de CLI deed dat alleen met `--wipe-settings`. Controleer het huidige gedrag en onderbouw of wissen voor deze firmwarewisseling nodig is.
- Behoud unieke fabriekskalibratie. Gebruik geen volledige chip-erase, onbekende flash-offsets of FM-1-wizards op de SMK.
- Houd stroom en verbinding stabiel. Onderbreek een actieve schrijfactie niet omdat het scherm tijdelijk leeg blijft.
- Bewaar het resultaat van de schrijfverificatie. Bij een fout: geen onbeperkte retries en geen willekeurige andere firmware. Beoordeel eerst de nieuwe toestand.

## 6. Verifieer het resultaat of benoem de fysieke blokkade

Na succesvolle schrijfverificatie: gebruik de gedocumenteerde herstart en wacht de beschreven opstarttijd af. Controleer of het apparaat terugkeert met de verwachte USB/MIDI-identiteit. Vraag alleen voor niet op afstand zichtbare zaken een korte bevestiging, bijvoorbeeld of scherm en toetsen weer werken. Zonder die observatie: meld precies welke technische checks wel geslaagd zijn; claim geen volledig functionerend instrument.

Als geen herstelverbinding verschijnt na de bevestigde directe aansluiting, of als verdere voortgang specifieke hardware vereist: stop de softwarepogingen. Een onbereikbaar apparaat is niet automatisch onherstelbaar. De ROM-downloadmodus kan fysieke USB_KEY/Pico-hulp vereisen.

De [FM-1 Transporter-handleiding](https://github.com/Quixotic7/MvaveFM1Unbricker/blob/main/TRANSPORTER-GUIDE.md) beschrijft verwante hardware, maar is geen SMK-37-flashinstructie. Neem geen pinout, firmwarebestand of schrijfwizard daaruit over zonder actuele bevestiging voor het exacte bord. Vraag alleen naar benodigde hardware als dit de volgende uitvoerbare stap verandert; doe geen aankoop zonder opdracht.

### Fysieke recovery & gebruikersprofiel (Geen soldeerervaring)

> [!IMPORTANT]
> **Aanname gebruikerservaring:** Ga er standaard altijd van uit dat de gebruiker **geen soldeerervaring** en **geen soldeergereedschap** heeft. 
> - Vraag of verwacht nooit dat de gebruiker zelf draden aan een printplaat soldeert of kabels openknipt/stript, tenzij dit expliciet door de gebruiker is aangeboden.
> - Bied bij een hard-brick uitsluitend **kant-en-klare, soldeervrije opties** aan:
>   1. **Soldeervrije kabels/adapters:** Een kant-en-klaar *USB-C male naar Dupont female jumperkabeltje* of een *USB-C breakout bordje met schroefterminals* (~€4-€6). De Dupont-stekkertjes schuiven rechtstreeks over de pinheaders van de Pico zonder solderen.
>   2. **Lokale hulp:** Verwijs naar een Repair Café, makerspace of handige kennis.
>   3. **Fabrieksgarantie:** Wijs de gebruiker op garantieregelingen bij recente aankoop (een mislukte update valt doorgaans onder garantie).

### RP2040 / Raspberry Pi Pico USB_KEY Transporter-configuratie

Wanneer een Raspberry Pi Pico (of compatibel RP2040-bord met USB-C) beschikbaar is:
1. **Firmware:** Flash `fm1_transporter.uf2` (gebouwd via `python3 fm1_transporter_recover.py setup` of de officiële release) door het bestand naar het gemounte `RPI-RP2`-volume te kopiëren. De Pico herstart als *FM-1 Transporter* met twee CDC-seriële poorten (console en data).
2. **Bedrading (alleen 3 aders, VBUS loslaten!):**
   - Pico **`GP0`** (Pin 1) $\rightarrow$ USB **`D+`** (Groene ader)
   - Pico **`GP1`** (Pin 2) $\rightarrow$ USB **`D-`** (Witte ader)
   - Pico **`GND`** (Pin 3) $\rightarrow$ USB **`GND`** (Zwarte ader)
   - **VBUS (5V, rode ader): ABSOLUUT NIET VERBINDEN.** De SMK-37 Pro draait tijdens recovery op zijn eigen accu om voedingsconflicten te voorkomen.
3. **Rolbeperking:** Gebruik de Transporter **uitsluitend** om de USB_KEY puls (`0x16EF`) te injecteren en de JieLi-chip in `WL82 UBOOT1.00` te dwingen. Gebruik **nooit** de automatische herstelwizard van FM-1 op de SMK-37 (het applicatiegebied van de SMK-37 Pro reikt tot `0x9D000` / 153 sectoren, terwijl de FM-1 stopt bij `0x93000` / 143 sectoren). Zodra de eenheid in UBOOT ontwaakt, wordt geflashed met **M-Flasher** en het officiële `SMK-37_Pro_016.fwsc`-pakket of de eigen back-up.

Lever bij een fysieke blokkade het voorbereide herstelpakket en een korte overdracht: exact model, symptomen, geobserveerde USB-toestand, gebruikte toolversie, beschikbare eigen rugsteun en verzoek om USB_KEY-ROM-recovery met behoud van kalibratie. Claim niet dat software de fysieke dongle kan vervangen.

## Rapportage

Houd updates kort en feitelijk. Eindig met: wat daadwerkelijk is uitgevoerd, wat geverifieerd is, of er geschreven is, waar de herstelbestanden staan en de ene noodzakelijke vervolgstap. Geen herhaald diagnose-interview of garantie op herstel binnen een vast aantal rondes.

## Historische onderzoeks- en herstelcases

- **1 november 2026 (Sessie 1):** M-Flasher 0.7.0 en officiële Pro V016 voorbereid; `find` vond geen apparaat en `info` meldde geen UBOOT-toestel. Geen back-up, geen schrijfhandeling.
- **1 november 2026 (Sessie 2 - Praktijkonderzoek & Geverifieerde Flash-rugsteun):**
  - Apparaat herkend via USB MIDI als `Felucca`. Succesvol omgeschakeld naar downloadmodus (`WL82 UBOOT1.00`).
  - M-Flasher (`--board smk37`) identificeerde de eenheid: *SMK-37 Pro / Elite*, stock bootloader, chip key `0x980F`, flash chip `0x856014` (1 MiB), Unit ID `4150354433333615`.
  - **Twee identieke, volledige 1 MiB flash-rugsteunen gemaakt en geverifieerd** (`smk37-20261101-225139.bin` en `smk37-20261101-225152.bin`, SHA-256 `2b01d2e8bf84a43992ae6636cf7c540b1f66ca0914700a53b2d732374f980cc4`). De fabriekskalibratie en unieke BT-data zijn hiermee 100% veiliggesteld.
  - Schrijfplan geëvalueerd: officiële `SMK-37_Pro_016.fwsc` vereist `--wipe-settings` om afwijkende VM-instellingen van Felucca (`0x9D000-0xBFFFF`) en BTIF (`0xC0000-0xC0FFF`) te wissen, terwijl de bootloader (`0x0000-0x3FFF`) en kalibratie intact blijven.
  - Vóór uitvoering trad een timeout op in de RAM-loader; eenheid viel weg van USB en scherm bleef leeg. Knoppen (`OCTAVE −`, `OCTAVE +`, `SEQ PLAY`) en accu-ontlaadcycli wekten de USB-laag niet softwarematig.
  - Raspberry Pi Pico (RP2040 met USB-C) succesvol direct vanaf macOS geflashed met Transporter UF2 (`fm1_transporter.uf2`).
  - Fysieke blokkade bevestigd: gebruiker heeft geen soldeerbout en geen ervaring met solderen. Conclusie: adviseer bij hard-brick uitsluitend kant-en-klare Dupont-kabels of externe service; dwing geen DIY-solderen af.
