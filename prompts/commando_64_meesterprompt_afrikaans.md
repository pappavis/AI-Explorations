# Meesterprompt: Bou die Klassieke Commodore 64-Speletjie **COMMANDO** van Grondvlak Af

> **Taal van opdrag en eindproduk:** Afrikaans (met ondersteuning vir duidelike arkade-terme)  
> **Teikenplatform:** Enkel-lêer HTML5 Canvas (`index.html`), 100% selfstandig (geen eksterne lêers of netwerkversoeke nie)  
> **Beginsel:** Hierdie dokument is geskryf vir ’n ontwikkelaar of KI-agent wat die oorspronklike 1985-speletjie *Commando* **nog nooit gesien, gespeel of gehoor het nie**. Moet niks veronderstel nie—volg elke visuele, meganiese, ouditiewe en tegniese spesifikasie noukeurig.

---

## 1. Jou Rol en Hoofdoel

Jy is ’n ervare speletjie-argitek en sagteware-ingenieur. Jou taak is om ’n getroue, vinnige en gepoleerde herskepping van die klassieke 1985 Commodore 64-arkadespeletjie **COMMANDO** te bou in ’n enkele, selfstandige `index.html`-lêer.

### Wat *is* hierdie speletjie? (Uitleg vir iemand wat dit nog nooit gesien het nie)
Stel jou voor jy kyk **reguit van bo af (voëlperspektief / top-down)** op ’n oorlogsveld.  
* Jy beheer ’n **enkele soldaat** (genaamd *Super Joe*) wat aan die onderkant van die skerm deur ’n helikopter afgelaai word.
* Jou doel is om **noordwaarts (boontoe)** deur vyandelike gebied te veg—verby bome, rotse, sandsak-loopgrawe, riviere met houtbrûe en vyandelike patrollies—totdat jy aan die bokant van die vlak by ’n **groot vyandelike vestinghek** aankom.
* Sodra jy die vesting bereik, skuif die ysterhek oop en stroom ’n laaste golf vyande uit. Wanneer jy almal verslaan het, is die vlak gewen en beweeg jy aan na die volgende, moeiliker gebied.
* Die speletjie voel **vinnig, gespanne en direk**: één raakskoot of botsing kos jou ’n lewe, maar jou masjiengeweer vuur blitsvinnig en jou handgranate kan hindernisse oorspring om hele groepe vyande uit te wis.

---

## 2. Visuele Identiteit en Skermargitektuur (Commodore 64 VIC-II)

Die speletjie moet lyk en voel soos ’n outentieke 1985 Commodore 64-speletjie op ’n CRT-monitor.

### 2.1 Resolusie en Skalering
* **Logiese interne resolusie:** Presies `320 × 200` piksels op die HTML5 `<canvas>`.
* **Skerp piksels:** Skakel beeldgladmaking af (`ctx.imageSmoothingEnabled = false`) en gebruik CSS `image-rendering: pixelated;` sodat elke piksel blokkig en haarskerp vertoon wanneer die skerm groter geskaal word.
* **CRT-effek (Opsioneel skakelbaar met sleutel `C`):** ’n Subtiele deursigtige oorsig van horisontale skanderingslyne (*scanlines*) en effense donker hoeke (vignet) bo-oor die doek.

### 2.2 Outentieke 16-Kleur Commodore 64 Palet (Pepto)
Gebruik **uitsluitlik** hierdie 16 kleure vir alle grafika, teks en effekte:

| Kode | Kleurnaam | Hex | Tipiese Gebruik in die Spel |
| :---: | :--- | :---: | :--- |
| `0` | Swart | `#000000` | Statusbalk, skaduwees, geweerlope, stewels |
| `1` | Wit | `#ffffff` | Telling-syfers, ontploffingskern, koeëlglans, krygsgevangenes |
| `2` | Rooi | `#883932` | Speler se kopband, granaatgooiers, vestinghek, ontploffingsrand |
| `3` | Siaan | `#67b6bd` | Waterglinstering, helikopter-ruit, HUD-aksente |
| `4` | Pers | `#8b3f96` | Opsionele aksente |
| `5` | Groen | `#55a049` | Speler se uniform, palmboomblare, pantservoertuig |
| `6` | Blou | `#40318d` | Rivierwater, standaard vyandelike soldate se uniforms |
| `7` | Geel | `#bfce72` | Grondpad, speler-koeëls, ammunisiekis, offisier-uniform, baniere |
| `8` | Oranje | `#8b5429` | Grond in Vlak 1, sandsakke, houtbrûe, ontploffings |
| `9` | Bruin | `#574200` | Boomstamme, brugrande, grond in Vlak 2, hare |
| `A` | Ligrooi / Vel | `#b86962` | Gesigte en hande van karakters |
| `B` | Donkergrys | `#505050` | Rotse, vestingmure, grond in Vlak 3 |
| `C` | Mediumgrys | `#787878` | Vyandelike helms, klip-tekstuur, vesting-blokke |
| `D` | Liggroen | `#94e089` | Ligpunte op speler-uniform en palmblare |
| `E` | Ligblou | `#7869c4` | Skermraam, ligpunte op vyandelike uniforms |
| `F` | Liggrys | `#9f9f9f` | Helikopter-rotor, rots-ligpunte |

### 2.3 Piksel-Sprites (Ingeboude Bitmaps)
Skep alle karakters en voorwerpe as vooraf-gerasteriseerde piksel-matrikse (bv. `12×14` piksels vir soldate, `20×6` vir sandsakke, `16×8` vir voertuie, `30×11` vir die helikopter) op buiteskerm-doeke (*offscreen canvases*) tydens opstart sodat daar geen geheue-oorskot per raam is nie.

### 2.4 Skermuitleg en Statusbalk (HUD)
* Die boonste **`18` piksels** van die `320 × 200`-skerm is ’n vaste swart statusbalk met ’n 1-piksel ligblou onderste lyn.
* Vertoon van links na regs in ’n skerp enkelspasie-lettertipe:
  1. `1UP` + huidige telling (6 syfers met voorloper-nulle, bv. `001500`)
  2. `HI` + beste telling (6 syfers)
  3. `VLAK:` + huidige vlaknommer (`1`, `2`, `3`, ...)
  4. `GR:` + aantal handgranate oor
  5. `LEWENS:` + aantal lewens oor

### 2.5 Kamerareël en Dieptelaag-Volgorde
* **Slegs Opwaartse Rol (One-Way Vertical Scroll):** Die vlak is lank (bv. `1880` piksels hoog). Die kamera begin heel onder (`camY = STAGE_LEN - 200`). Sodra die speler bokant 60% van die skermhoogte beweeg, rol die kamera glad na bo (`camY` verminder). Die kamera mag **nooit terug na onder rol nie**, en die speler mag nooit onder die sigbare skermrand uitloop nie.
* **Teken-volgorde (van onder na bo):**
  1. Grondtekstuur en kronkelende grondpad.
  2. Riviere (met geanimeerde waterglinstering) en houtbrûe.
  3. Vestingmure en skuifhek (aan die bokant van die vlak).
  4. Grondhindernisse: rotse, sandsakke en **slegs die stamme** van palmbome.
  5. Versamelstukke (flitsende granaatkiste) en krygsgevangenes.
  6. Vyande en die Speler.
  7. **Palmboom-blaredakke** (word *bo-oor* karakters geteken sodat soldate outentiek onderdeur die blare kan loop).
  8. Koeëls, boogvormende granate (met donker grondskaduwee onder hulle), ontploffings, vonke, die helikopter en swewende puntetelling-opspringsels (`+300`, `+2000`).
  9. Vaste HUD-statusbalk en skermoortreksels (Titel, Pouse, Spel Verby, Demo-banier).

---

## 3. Volledige Spelmeganika en Entiteite

### 3.1 Beheer (Sleutelbord, Muis én Aanraakskerm)
* **8-Rigting Beweging:** `W A S D` of Pyltjiesleutels (`▲ ▼ ◄ ►`), insluitend skuins bewegings (genormaliseerde vektor teen konstante spoed van ~`74` piksels/sekonde).
* **Masjiengeweer (M60):** `Q`, linker/regter `Ctrl`, of Linkermuisklik (hou in vir volgehoue vuur).
* **Handgranaat Gooi:** `Spasiebalk` of Regtermuisklik.
* **Pouseer:** `P` of `Escape`.
* **Klank aan/af:** `M`.
* **CRT-lyne aan/af:** `C`.
* **Aanraakbeheer:** Op mobiele/aanraaktoestelle verskyn ’n deursigtige D-pad links onder en twee ronde knoppies (`VUUR` en `GRANAAT`) regs onder.
* **Veiligheid:** Voorkom standaard blaaier-aksies vir pyltjies, spasiebalk en `Ctrl+W/A/S/D/Q`, en stel alle sleutels terug wanneer die blaaiervenster fokus verloor (`blur`).

### 3.2 Die Speler (*Super Joe*)
* **Animasie:** 2-raam stap-siklus terwyl hy beweeg; staan stil op sy laaste rigting wanneer hy stop. Aparte aansig vir op/af en links/regs (horisontaal gespieël vir links).
* **M60 Masjiengeweer:**
  * Onbeperkte ammunisie, vuurtempo ongeveer elke `0.13` sekondes.
  * Koeëls beweeg vinnig (~`225` px/s) in die presiese rigting waarin die speler laas gekyk/beweeg het.
  * Koeëls het ’n beperkte reikafstand (~`0.72` sekondes) en stop met ’n wit vonkie teen rotse, sandsakke en vestingmure (maar vlieg verby palmblare).
* **Handgranate:**
  * Begin elke nuwe spel met **`6` granate** (maksimum `9`). Kry `+3` granate tussen vlakke en `+4` uit granaatkiste.
  * **Belangrike oorspronklike reël:** Granate word altyd **reguit noord (boontoe)** gegooi oor ’n afstand van ~`68` piksels.
  * Die granaat volg ’n paraboliese boog (`z = sin(u * PI) * 26`), met ’n skaduwee op die grond. Omdat dit deur die lug vlieg, **spring dit oor rotse, sandsakke, riviere en mure**.
  * By landing ontplof dit met skerm-skudding (`screen shake`), ’n multi-kleur C64-vuurbal (`wit → geel → oranje → rooi`), vernietig alle vyande binne ~`35` piksels, en blaas sandsak-bunkers op.
* **Lewens, Dood en Herlewing:**
  * Begin met **`3` lewens**. Ekstra lewe (`1UP`) by `10 000` punte, en daarna elke `20 000` punte (`30 000`, `50 000`, ...).
  * Enige vyandelike koeël, granaat-ontploffing of direkte liggaamsbotsing met ’n vyand laat die speler onmiddellik sterf (ontploffing + klankeffek + alle vyandelike koeëls word skoongemaak).
  * Na `1.25` sekondes herleef die speler effens terug van sy sterfplek met `2.4` sekondes tydelike onkwesbaarheid (knipperende sprite). As lewens `0` bereik, gaan die spel na `SPEL VERBY`.

### 3.3 Helikopter-Inleiding (Vlak 1)
* Aan die begin van Vlak 1 sweef ’n groen pixel-helikopter met draaiende rotorblaaie bo die speler se beginpunt, en vlieg dan skuins regs-bo van die skerm af weg terwyl die speler dadelik beheer neem.

### 3.4 Terrein en Hindernisse
* **Riviere & Brûe:** Elke vlak het 2 horisontale riviere wat die hele skermbreedte oorspan. Die water blokkeer alle voetgangers; die speler (en vyande) kan slegs oor die **houtbrug** (`48` piksels wyd) beweeg.
* **Palmbome:** Slegs die onderste stamblok keer beweging; koeëls en karakters kan visueel onder die blaredak inbeweeg.
* **Rotse:** Soliede dekking—keer beweging én koeëls.
* **Sandsak-Loopgrawe:** Keer beweging én koeëls, maar kan deur ’n speler-granaat opgeblaas word.

### 3.5 Vyande en KI-Gedrag
Vyande aktiveer slegs wanneer hulle binne of naby die sigbare skerm is:
1. **Infanterie-Soldaat (Blou Uniform — `300` punte, 1 HP):** Beweeg in rigting van die speler met effense willekeurige flankering, vermy hindernisse, en vuur enkel gerigte skote.
2. **Loopgraaf-Skutter (Agter Sandsakke — `300` punte, 1 HP):** Sit vas agter ’n sandsak-verskansing en vuur vinniger. Koeëls van voor tref die sandsakke—die speler moet hom flankeer of ’n granaat bo-oor gooi.
3. **Granaatgooier (Rooi Uniform — `500` punte, 1 HP):** Hou middelmatige afstand en gooi paraboliese vyandelike granate na die speler se posisie.
4. **Motorfiets-Patrollie (`500` punte, 2 HP) & Pantser-Jeep (`500` punte, 3 HP):** Jaag periodiek vinnig horisontaal oor die boonste helfte van die skerm (van links na regs of regs na links) terwyl hulle vuur.
5. **Vesting-Offisier (Geel/Goud Uniform — `2 000` punte, 2 HP):** Verskyn aan die einde van die vesting-aanval; beweeg vinniger as gewone soldate en is ’n hoë-waarde teiken.

### 3.6 Bonusse en Versamelstukke
* **Flitsende Granaatkis (`1 000` punte + `4` granate):** Wissel vinnig tussen twee kleur-rame sodat dit uitstaan op die terrein.
* **Krygsgevangene / P.O.W. (`2 000` punte):** Staan vasgebind op die slagveld. Sodra die speler naby genoeg kom, word hy bevry, hardloop sywaarts van die skerm af, en verskyn ’n banier (`KRYGSGEVANGENE GERED! +2000`).

### 3.7 Die Vestinghek-Klimaks en Vlakvordering
* Aan die bokant van elke vlak (`y = 74..98`) staan ’n soliede muur met ’n sentrale opening (`x = 128..192`) wat deur twee rooi ysterdeure afgesluit is.
* Sodra die kamera heel bo sluit (`camY <= 14`), verskyn ’n waarskuwingsbanier (`VESTINGHEK MAAK OOP!`), die deure skuif oop, en `10 + (vlak × 3)` verdedigers stroom in sarsies uit (met die Offisier heel laaste).
* Wanneer alle verdedigers verslaan is:
  * Toon `VESTING VEROORWIN!`
  * Ken `2 000` vlak-bonus + `(oorblywende granate × 200)` toe.
  * Beweeg na `2.9` sekondes aan na die volgende vlak.
* **Drie Visuele Temas (wat lus met toenemende moeilikheidsgraad):**
  * **Vlak 1 — Buitepos:** Oranje-bruin grond, geel pad, blou water.
  * **Vlak 2 — Kloof:** Donkerbruin grond, grys pad, rooi mure, siaan water.
  * **Vlak 3 — Sitadel:** Donkergrys klipgrond, grys pad, blou mure.
  * Vlak 4+ herhaal die temas maar met vinniger vyande, vinniger vuurtempo en meer vesting-verdedigers.

---

## 4. Speltoestande en Aantrek-Demo (State Machine)

Implementeer ’n eksplisiete toestandsmasjien met hierdie 6 toestande:
1. **`TITELSKERM`:** Vertoon die titel (*COMMANDO 64*), die Top-5 Rekordtabel (gestoor in `localStorage`), en ’n knipperende boodskap (`DRUK SPASIE / KLIK OM TE BEGIN`). Ná **3.2 sekondes** sonder invoer skakel dit outomaties oor na `AANTREK_DEMO`.
2. **`AANTREK_DEMO` (Presies 15 sekondes):** Begin ’n lewendige speelsessie waar ’n ingeboude KI-speler outomaties vorentoe beweeg, oor brûe stuur, op vyande skiet en granate gooi. Vertoon onderaan ’n knipperende banier met ’n aftelling (`DEMO (15s) — DRUK ENIGE SLEUTEL OM TE SPEEL`). Enige sleutel of muisklik onderbreek die demo onmiddellik en begin ’n regte spel. Ná 15 sekondes keer dit terug na `TITELSKERM`.
3. **`AKTIEWE_SPEL`:** Volledige spelerbeheer.
4. **`GEPOUSEER`:** Bevries die simulasie en toon ’n deursigtige pouse-oortreksel.
5. **`VLAK_VOLTOOI`:** Kort vieringsfase tussen vlakke.
6. **`SPEL_VERBY`:** Vertoon finale telling, vlak bereik, en `★ NUWE REKORD! ★` indien die toptelling gebreek is. Ná **4.5 sekondes** sonder invoer begin die 15-sekonde `AANTREK_DEMO` outomaties weer.

---

## 5. Klank- en Musiekenjin (MOS 6581 SID-Sintese)

Geen eksterne oudiolêers mag gebruik word nie. Bou ’n suiwer Web Audio API 3-stem sintetiseerder wat die beroemde Commodore 64 SID-klankskyfie naboots:
* **Stem 1 (Bas):** Ritmiese 16de-noot saagtandgolf (`sawtooth`) in ’n drywende militêre mars-patroon (64 stappe teen ~`118 ms` per stap).
* **Stem 2 (Hoofmelodie):** Vierkantgolf (`square`) heroïese 8-bis melodie bo-oor die bas.
* **Stem 3 (Perkussie & Klankeffekte):** Vooraf-gegenereerde witruis-buffer met banddeurlaat-filter vir militêre tromslae (snare/hi-hat), plus afsonderlike klankeffekte vir:
  * Masjiengeweerskote (kort dalende vierkantgolf-puls; hoër toonhoogte vir speler, laer vir vyande).
  * Granaat-ontploffing (laagdeurlaat-gefilterde witruis wat oor `0.38s` wegsak).
  * Bonus / 1UP / P.O.W. (vinnige stygende 4-noot arpeggio).
  * Speler-dood (dramatiese dalende saagtandtoon oor `0.45s`).
* **Blaaier-beleid:** Inisialiseer of hervat `AudioContext` veilig by die eerste gebruikersinteraksie.

---

## 6. Metodiese Ingenieursproses (Verpligte Werkvloei)

Volg hierdie 4 fases streng in volgorde voordat jy die finale `index.html` lewer:

### Fase 1 — Argitektuur & Deterministiese Ontwerp
* Konsolideer alle HTML, CSS en JavaScript in een skoon `index.html`-lêer binne ’n geïsoleerde IIFE (`(function(){ 'use strict'; ... })();`).
* Gebruik ’n deterministiese ewekansige getalgenerator (soos `mulberry32`) per vlaknommer sodat elke vlak ’n konsekwente, gebalanseerde uitleg het.
* Kap die raam-tydstap (`dt = Math.min(0.05, ...)`) sodat die fisika nooit breek as die gebruiker van oortjie wissel nie.

### Fase 2 — Toetsgedrewe Ontwikkeling (TDD: ROOI → GROEN → REFAKTOREER)
Bou ’n liggewig ingeboude outomatiese toetspakket (bv. `runTddSuite()` wat by opstart loop en waarvan die uitslag in ’n `TDD: X/7 PASS`-knoppie en modaal sigbaar is) wat ten minste hierdie 7 kritieke kontroles verifieer:
1. **VIC-II Resolusie & Palet:** Doek is `320×200` en presies 16 kleure bestaan.
2. **Sprite-Rasterisering:** Alle kern-bitmaps (speler, vyand, helikopter, voertuie) is korrek gegenereer met nie-nul afmetings.
3. **Vlakbouer:** Elke vlak het 2 riviere met brûe, vestingmure en vyande.
4. **Koeël-lus Veiligheid:** Wanneer ’n vyandelike koeël die speler tref en `killPlayer()` die koeël-skikking filter, mag die agteruit-lus nooit buite grense lees of ’n `TypeError` gooi nie.
5. **Granaat-meganika:** Gooi van ’n granaat verminder voorraad met 1 en skep ’n aktiewe granaat-entiteit.
6. **Puntetelling & 1UP:** By `10 000` punte styg lewens outomaties van `3` na `4`.
7. **Demo-tydsduur:** Die aantrek-demo se tydskonstante is presies `15.0` sekondes.

### Fase 3 — Kode-oorsig & Foutvoorkoming (Sanity Check)
Kontroleer jou kode spesifiek vir hierdie algemene foute:
* Geen `alert()` of `confirm()` oproepe nie.
* Geen ongedefinieerde veranderlikes of afgesnyde lusse wanneer skikkings binne ’n lus gemuteer word nie (klem altyd lus-indeks `i = Math.min(i, arr.length)` ná ’n skikking-filter).
* Verwyder fokus van kopbalk-knoppies ná klik (`e.target.blur()`) sodat `Spasiebalk` nie per ongeluk knoppies heraktiveer tydens spel nie.
* Vang `localStorage`- en `AudioContext`-uitsonderings netjies met `try/catch`.

### Fase 4 — Volledige Speeltoets-Verifikasie
Verifieer die volledige vloei voor oplewering:
* `TITELSKERM` → outomatiese `AANTREK_DEMO` ná 3.2s → onderbreking met sleutel/klik → Helikopter-landing → Beweging oor brug → M60-vuur & Granaat oor sandsakke → Vestinghek-klimaks → Oorgang na Vlak 2 → Speler-dood & Herlewing → `SPEL_VERBY` met `localStorage`-toptelling.

---

## 7. Lewerbare Uitvoer

* Lewer **slegs** ’n volledige, foutvrye, dadelik speelbare enkel-lêer **`index.html`**.
* Alle speler-sigbare teks (spyskaarte, knoppies, baniere, HUD-etikette, pouse- en spel-verby-skerms) moet in **natuurlike, korrekte Afrikaans** wees.
* Voeg duidelike gestruktureerde kommentaar by elke hoofseksie (`[A]` tot `[I]`) sodat enige ontwikkelaar of KI die speletjie maklik kan onderhou of uitbrei.