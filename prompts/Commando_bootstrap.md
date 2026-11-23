# COMMANDO 64 — Offline Reconstruction Survival Manual

> **Dokument:** `Commando_bootstrap.md`  
> **Status:** Finale herbou-kontrak  
> **Datum:** 23 November 2026  
> **Normatiewe bron:** `Commando_MasterPrompt.md`  
> **Teikenlewering:** een selfstandige `index.html`  
> **Taal van implementasie-UI:** Afrikaans

Hierdie dokument is terselfdertyd ’n tegniese bootstrap, argitektuurbesluitrekord, defekregister, regressiespeelboek, bewyskontrak en ouditspoor. Dit beskryf **hoe** om die speletjie van nul af te bou en te bewys. Die Meesterprompt beskryf **wat** gebou moet word.

---

# 0. Dokumentbeheer en gebruiksinstruksie

## 0.1 Gesagsorde

1. `Commando_MasterPrompt.md` is die normatiewe vereistespesifikasie.
2. `Commando_bootstrap.md` is implementasie- en verifikasiekennis.
3. Die finale `index.html` is die uitvoerbare implementasie.

> **Botsingsreël:** As die Meesterprompt en hierdie Bootstrap bots, **wen die Meesterprompt**. Moenie ’n vereiste stilweg verander omdat ’n vorige implementasie anders gewerk het nie. Teken die botsing aan, herstel die implementasie, en voeg ’n regressietoets by.

## 0.2 Ononderhandelbare afleweringskontrak

```text
LEWER:                    index.html
HTML-lêers:               presies 1
Eksterne JavaScript:      0
Eksterne CSS:             0
Eksterne beelde/sprites:  0
Eksterne klanklêers:      0
Netwerkversoeke:          0
Runtime-afhanklikhede:    0
Bediener nodig:           nee
Internet nodig:           nee
```

Die lêer moet plaaslik met ’n moderne blaaier oopmaak en dadelik kan speel. Alle HTML, CSS, JavaScript, bitmaps, lettertekens, musiekdata en toetskode woon in die een lêer.

## 0.3 Hoe om hierdie dokument te gebruik

1. Lees afdelings 0–3 voordat kode geskryf word.
2. Kopieer die konstantes uit afdeling 3; moenie “naby genoeg”-waardes improviseer nie.
3. Implementeer die kontrakte in afdelings 4–17 deur die hekke in afdeling 18 te volg.
4. Laat die sewe TDD-toetse ná elke betekenisvolle verandering loop.
5. Voer die volle regressiespeelboek in afdeling 20 uit.
6. Vul die bewys- en ouditregisters in afdelings 22–23 in.
7. Verklaar die bouwerk slegs klaar as afdelings 25 en 26 volledig afgemerk is.

## 0.4 Terminologie

- **Wêreldkoördinaat:** posisie in die lang vlak, onafhanklik van kamera.
- **Skermkoördinaat:** finale posisie binne die logiese `320×200`-doek.
- **HUD:** vaste boonste statusbalk, `y=0..17`.
- **Noord:** negatiewe Y-rigting.
- **Aktiveringsvenster:** sigbare skerm plus ’n klein marge waarin vyand-KI mag loop.
- **Palet-suiwer:** elke piksel op die logiese speeldoek kom uit die 16 gesaghebbende C64-kleure.

---

# 1. Die Antarktika-kontrak

Die blinde herbouer ontvang:

- `Commando_MasterPrompt.md`;
- `Commando_bootstrap.md`;
- ’n gewone moderne lessenaar- of mobiele blaaier;
- ’n teksredigeerder.

Die herbouer het **nie**:

- internet, npm, CDN’s of pakketrepositories nie;
- vorige chatgeskiedenis of bestaande COMMANDO-bronkode nie;
- sprites, klanklêers, lettertipes of die oorspronklike C64-ROM nie;
- toegang tot die vorige ontwikkelaar nie;
- ’n plaaslike webbediener as voorvereiste nie.

Gevolglik is die volgende verbode:

```html
<script src="https://voorbeeld/..."> </script>
<link rel="stylesheet" href="...">
<img src="sprites.png">
```

```javascript
fetch(...);
import ... from "https://...";
new Audio("shot.wav");
```

’n Funksie wat weens `file://`-beperkings, ’n ontbrekende netwerkbron of ’n eksterne boustap faal, is ’n vrystellingsblokker.

---

# 2. Requirement Traceability Matrix

Gebruik die ID’s in kommentaar, toetsuitsette, defekinskrywings en die bewysregister. “Handmatig” beteken dat ’n mens die eksplisiete stap in afdeling 20 uitvoer; dit beteken nie “ongeverifieer” nie.

| ID | Normatiewe vereiste | Eienaar/module | Verifikasie |
|---|---|---|---|
| OUT-001 | Een selfstandige `index.html` | Shell/IIFE | statiese inspeksie, REG-01 |
| OUT-002 | Geen eksterne lêers, netwerk of runtime-afhanklikhede | Shell | netwerkpaneel + bronsoektog |
| OUT-003 | Speler-sigbare teks is natuurlike Afrikaans | Font/UI | UI-deurloop |
| ARC-001 | Geïsoleerde IIFE en `'use strict'` | Shell | statiese inspeksie |
| ARC-002 | Hoofseksies `[A]` tot `[I]` | Bronorganisasie | statiese inspeksie |
| VIS-001 | Logiese doek presies `320×200` | Renderer | TDD-01 |
| VIS-002 | Beeldgladmaking af; gepikselde CSS-skalering | Renderer/CSS | inspeksie + skermtoets |
| VIS-003 | Presies die 16 Pepto-kleure op die logiese doek | Palet/renderer | TDD-01 + paletoudit |
| VIS-004 | Skakelbare scanlines/vignet met `C` | Oortreksel | REG-18 |
| VIS-005 | Voorafgerasteriseerde piksel-sprites | SpriteFactory | TDD-02 |
| VIS-006 | HUD is `18` px hoog met ligblou onderlyn | HUD | visuele inspeksie |
| VIS-007 | HUD-volgorde: 1UP, HI, VLAK, GR, LEWENS | HUD | REG-03 |
| VIS-008 | Negenlaags tekenvolgorde en blaredak bo karakters | Renderer | REG-08 |
| CAM-001 | Kamera rol slegs noord/opwaarts | Camera | REG-05 |
| CAM-002 | Begin by `STAGE_LEN-200`; ondergrens `camY>=0` | Camera | eenheid/handmatig |
| MOV-001 | 8-rigting beweging teen ~`74 px/s`, diagonale normalisering | Player | REG-04 |
| INP-001 | WASD/pyle, Q/Ctrl/muisvuur, Spasie/regsklikgranaat | Input | REG-02/06/07 |
| INP-002 | P/Escape, M en C-skakelaars | Input | REG-18 |
| INP-003 | Browser-defaults voorkom; sleutels op `blur` skoon | Input | REG-19 |
| INP-004 | Aanraak-D-pad, VUUR en GRANAAT | Touch UI | REG-20 |
| WPN-001 | M60 onbeperkte ammunisie, `0.13 s` interval | Weapons | tydmeting |
| WPN-002 | Koeëls ~`225 px/s`, ~`0.72 s` leeftyd | Projectile | tyd/afstandtoets |
| WPN-003 | Koeëlrigting volg laaste kyk/beweegrigting | Weapons | REG-06 |
| WPN-004 | Koeëls vonk en sterf teen rots/sandsak/muur | Collision/FX | REG-06 |
| GRN-001 | Nuwe spel: 6; maksimum 9; +3 vlak; +4 kis | Grenades | TDD-05 + REG-11/15 |
| GRN-002 | Spelergranaat beweeg altyd noord oor ~68 px | Grenades | REG-07 |
| GRN-003 | Boog `sin(uπ)×26`; skadu op grond | Grenade renderer | visuele inspeksie |
| GRN-004 | Geen midlug-hindernisbotsing; radius ~35 px | Grenade/collision | REG-07 |
| GRN-005 | Ontploffing, sandsakvernietiging en skermskudding | FX/collision | REG-07 |
| PLY-001 | Twee-raam loopanimasie en rigtingaansigte | Player/Sprites | REG-04 |
| PLY-002 | Begin met 3 lewens | Session | TDD-06-opstelling |
| PLY-003 | Dodelike koeël, ontploffing of vyandbotsing | Damage | REG-16 |
| PLY-004 | Dood wis vyandelike koeëls; 1.25 s tot herlewing | Lifecycle | TDD-04 + REG-16 |
| PLY-005 | 2.4 s knipperende onkwesbaarheid | Lifecycle/renderer | REG-16 |
| SCR-001 | 1UP by 10k, daarna 30k, 50k, ... | Score | TDD-06 |
| HEL-001 | Vlak-1-helikopter sweef en vertrek regs-bo | Intro | REG-03 |
| HEL-002 | Spelerbeheer is onmiddellik beskikbaar | Intro/input | REG-03 |
| LVL-001 | Lang vlak, tipies ~1880 px | LevelBuilder | TDD-03 |
| LVL-002 | Elke vlak het presies twee volle-breedte-riviere | LevelBuilder | TDD-03 |
| LVL-003 | Elke rivier het ’n 48 px houtbrug | LevelBuilder | TDD-03 + REG-05 |
| LVL-004 | Water blokkeer voetgangers; brug laat deur | Collision | REG-05 |
| LVL-005 | Rotse, sandsakke en palmstamme het korrekte semantiek | Collision | matriks + REG-08 |
| AI-001 | Infanterie: 1 HP, 300, jaag/flankeer, enkel skoot | Enemy AI | REG-09 |
| AI-002 | Loopgraafskutter: 1 HP, 300, stil, vinniger vuur | Enemy AI | REG-09 |
| AI-003 | Granaatgooier: 1 HP, 500, middelafstand, booggranaat | Enemy AI | REG-09 |
| AI-004 | Motorfiets: 2 HP, 500, vinnige horisontale patrollie | Enemy AI | REG-10 |
| AI-005 | Pantserjeep: 3 HP, 500, horisontaal en vuur | Enemy AI | REG-10 |
| AI-006 | Offisier: 2 HP, 2000, vinnig, laaste verdediger | Fortress AI | REG-14 |
| AI-007 | Vyande aktiveer net in/naby die sigbare venster | Enemy system | aktiveringsinspeksie |
| PCK-001 | Flitsende granaatkis: 1000 en +4 | Pickup | REG-11 |
| PCK-002 | POW: vas → gered → hardloop sywaarts → weg; +2000 | POW | REG-12 |
| FRT-001 | Vestingmuur `y=74..98`; opening `x=128..192` | Fortress | TDD-03 + REG-13 |
| FRT-002 | Hek aktiveer by `camY<=14` | Fortress | REG-13 |
| FRT-003 | `10 + level×3` verdedigers; offisier laaste | Fortress | REG-14 |
| FRT-004 | Geforseerde hekuitgang voor normale KI | Fortress AI | REG-14 |
| FRT-005 | Voltooi slegs as ry leeg én lewende verdedigers nul | Fortress | REG-15 |
| FRT-006 | Bonus `2000 + grenades×200`; wag 2.9 s | Progression | REG-15 |
| THM-001 | Buitepos, Kloof en Sitadel; lus vanaf vlak 4 | Themes | REG-15 |
| THM-002 | Moeilikheid neem toe: spoed, vuurtempo, verdedigers | Difficulty | vlakvergelyking |
| STA-001 | Presies ses genoemde toestande | StateMachine | toestandoudit |
| STA-002 | 3.2/15.0/2.9/4.5 s timers presies | StateMachine | TDD-07 + REG-02/17 |
| DEM-001 | Demo stuur noord, oor brûe, vuur en gooi granate | Demo AI | REG-02 |
| DEM-002 | Enige sleutel of muisklik begin regte spel | State/input | REG-02 |
| AUD-001 | Web Audio, 3-stem SID-styl; geen lêers | Audio | REG-21 |
| AUD-002 | 64-stap bas teen ~118 ms plus melodie/perkussie | Audio | oudit/luistertoets |
| AUD-003 | Vyf vereiste SFX-families | Audio | REG-21 |
| AUD-004 | Audio begin/hervat op gebruikersgebaar en faal sag | Audio | REG-21 |
| STO-001 | Top-5 in `localStorage`, foutveilig | Storage | REG-17 |
| DET-001 | Vlakbouer gebruik deterministiese RNG per vlak | LevelBuilder | herhaalbaarheidstoets |
| PER-001 | `dt=Math.min(0.05, ...)` | Loop | verborge-oortjie-toets |
| PER-002 | Geen per-raam sprite-rasterisering of vermybare allokasie | Renderer | profiel/bronoudit |
| TDD-001 | Ingeboude `runTddSuite()` en sigbare `X/7 PASS` | Tests/UI | TDD-01..07 |
| REG-001 | Geen `alert()`/`confirm()` of ongevange kernfoute | Hele bouwerk | bronsoektog + konsole |

## 2.1 Sluitingsregister vir die 25 geïdentifiseerde gapings

| Gaping | Sluiting in hierdie dokument |
|---:|---|
| 1 | Volledige Sprite Factory-kontrak: §5.3 |
| 2 | Presiese HUD-kontrak: §5.4 |
| 3 | Volledige M60-kontrak: §8.2 |
| 4 | Presiese granaatkontrak: §8.3 |
| 5 | Dood/herlewing/lewens: §8.4 |
| 6 | Helikopter-intro: §8.5 |
| 7 | Alle vyandtipes: §9 |
| 8 | Aktiveringsvenster: §9.1 |
| 9 | Granaatkis en POW: §10 |
| 10 | Drie vlaktemas: §11.1 |
| 11 | Vestinggeometrie en hekuitgang: §11.2–§11.4 |
| 12 | Ses state en timers: §12 |
| 13 | Demo-KI-beslisboom: §13 |
| 14 | Top-5 `localStorage`: §15.5 |
| 15 | Browser-invoerveiligheid: §15.2–§15.4 |
| 16 | Aanraakgedrag en afmetings: §15.3 |
| 17 | SID-benadering: §14 |
| 18 | Skermskudding: §8.6 |
| 19 | `dt`-kap as vrystellingshek: §17 en §25 |
| 20 | `[A]`–`[I]`-kommentaar: §4.2 |
| 21 | Sterk enkel-lêer-uitvoerkontrak: §0.2 en §22 |
| 22 | Palet-suiwerheid, nie net `PAL.length` nie: §5.2 |
| 23 | Determinismegrense: §16 |
| 24 | Botsingsverenigbaarheidsmatriks: §7 |
| 25 | Requirement Traceability Matrix: §2 |

---

# 3. 30-minute Technical Bootstrap

## 3.1 Gesaghebbende konstantes

```javascript
const SCREEN_W = 320;
const SCREEN_H = 200;
const HUD_H = 18;
const STAGE_LEN = 1880;          // tipiese/aanbevole vaste lengte

const PLAYER_SPEED = 74;         // px/s
const FIRE_INTERVAL = 0.13;      // s
const BULLET_SPEED = 225;        // px/s
const BULLET_LIFETIME = 0.72;    // s

const START_GRENADES = 6;
const MAX_GRENADES = 9;
const GRENADE_DISTANCE = 68;     // wêreld-px noord
const GRENADE_ARC = 26;          // visuele z-hoogte
const GRENADE_RADIUS = 35;       // ontploffingsradius

const START_LIVES = 3;
const RESPAWN_DELAY = 1.25;
const INVULNERABILITY = 2.4;

const TITLE_IDLE = 3.2;
const DEMO_DURATION = 15.0;
const LEVEL_COMPLETE_DELAY = 2.9;
const GAME_OVER_IDLE = 4.5;

const FORTRESS_Y0 = 74;
const FORTRESS_Y1 = 98;
const GATE_X0 = 128;
const GATE_X1 = 192;
const FORTRESS_TRIGGER_CAMY = 14;

const DT_MAX = 0.05;
```

## 3.2 Puntetelling

| Gebeurtenis | Punte |
|---|---:|
| Infanterie | 300 |
| Loopgraafskutter | 300 |
| Granaatgooier | 500 |
| Motorfiets | 500 |
| Pantserjeep | 500 |
| Vestingoffisier | 2 000 |
| Granaatkis | 1 000 |
| POW bevry | 2 000 |
| Vlak voltooi | `2 000 + oorblywende granate × 200` |

Ekstra lewens: `10 000`, daarna elke `20 000` punte (`30 000`, `50 000`, ...).

## 3.3 Eerste 30 minute

1. **0–5 min:** skep HTML-shell, doek `320×200`, responsiewe gepikselde CSS, IIFE en `[A]–[I]`-kommentaar.
2. **5–10 min:** voeg `PAL`, konstantes, `mulberry32`, vaste toestandname en sentrale `game`-objek by.
3. **10–15 min:** bou bitmap-font en SpriteFactory met offscreen-doeke; laat TDD-01/02 rooi/groen loop.
4. **15–20 min:** bou LevelBuilder-data vir twee riviere, brûe, hindernisse en vesting; laat TDD-03 loop.
5. **20–25 min:** bou `requestAnimationFrame`, `dt`-kap, wêreld/skerm-transformasie en slegs-noord kamera.
6. **25–30 min:** bou StateMachine-skulp, invoerregister, toets-UI en ’n statiese HUD. Stop hier en bevestig G0–G4 voordat spelmeganika begin.

## 3.4 Minimum datamodel

```javascript
const game = {
  state: "TITELSKERM",
  stateTime: 0,
  level: 1,
  score: 0,
  highScores: [],
  lives: 3,
  grenades: 6,
  nextLife: 10000,
  camY: STAGE_LEN - SCREEN_H,
  muted: false,
  crt: true,
  demo: false
};

const world = {
  rivers: [], bridges: [], obstacles: [], enemies: [],
  bullets: [], grenades: [], explosions: [], pickups: [], pows: [],
  particles: [], popups: [], fortress: null
};
```

Elke entiteit se posisie is in wêreldkoördinate. Tydwaardes is sekondes; snelhede is wêreldpiksels per sekonde.

---

# 4. Harde Architecture Contracts

## 4.1 Enkel-lêerstruktuur

```text
index.html
├─ <style> — raam, gepikselde skaal, oortreksels, touch UI
├─ <canvas width="320" height="200">
├─ opsionele HTML-kopbalk/toetsknoppie
└─ <script>
   └─ (function () { 'use strict'; ... boot(); })();
```

Geen modules wat ’n bediener vereis nie. Geen eval, dinamiese kode-aflaai of runtime asset loader nie.

## 4.2 Verpligte bronkommentaar

Die finale script bevat hierdie navigasiebakens, in orde:

```javascript
// [A] KONSTANTES, PALET EN HULPFUNKSIES
// [B] PIKSELFONT EN SPRITE FACTORY
// [C] SID-STYL OUDIO
// [D] INVOER, MUIS EN AANRAAK
// [E] DETERMINISTIESE LEVELBUILDER
// [F] SPELMEGANIKA EN ENTITEITE
// [G] STATE MACHINE EN DEMO-KI
// [H] RENDERING EN OORTREKSELS
// [I] TDD, BOOTSTRAP EN DIAGNOSTIEK
```

Name mag effens verskil, maar `[A]` tot `[I]`, die orde en die skeiding van verantwoordelikhede is ’n leweringsvereiste.

## 4.3 Hooflus

```javascript
function frame(now) {
  const dt = Math.min(DT_MAX, Math.max(0, (now - previousNow) / 1000));
  previousNow = now;
  updateState(dt);
  render();
  requestAnimationFrame(frame);
}
```

- `updateState()` muteer wêrelddata; `render()` nie.
- Pouse vries spelsimulasie maar mag die pouse-oortreksel render.
- Toestandsoorgange gaan deur een funksie, bv. `setState(next)`; geen verspreide magiese strings nie.
- Tydgebaseerde beweging gebruik `dt`; animasie mag nie aan raamtempo vas wees nie.

## 4.4 Veilige skikkingmutasie

Verwyder entiteite met agteruitlusse of merk-en-kompakteer. As `killPlayer()` ’n hele koeëlskikking skoonmaak terwyl ’n lus reeds loop, heranker die indeks en lees nooit blind ’n verwyderde element nie:

```javascript
for (let i = bullets.length - 1; i >= 0; i--) {
  const b = bullets[i];
  if (!b) continue;
  if (hitsPlayer(b)) {
    killPlayer();              // mag bullets leegmaak
    i = Math.min(i, bullets.length - 1);
    if (i < 0) break;
  }
}
```

Hierdie kode is doelbewuste defekvoorkoming, nie “onnodige defensiewe kode” nie.

---

# 5. Visuele, VIC-II, sprite- en HUD-kontrakte

## 5.1 Canvas en skaal

```html
<canvas id="game" width="320" height="200"></canvas>
```

```css
canvas {
  image-rendering: pixelated;
  image-rendering: crisp-edges;
  max-width: 100%;
  height: auto;
}
```

```javascript
ctx.imageSmoothingEnabled = false;
```

Die browser mag die doek met ’n heelgetal of responsiewe faktor vergroot, maar spelberekeninge bly altyd `320×200`.

## 5.2 Gesaghebbende palet en palet-suiwerheid

```javascript
const PAL = Object.freeze([
  "#000000", "#ffffff", "#883932", "#67b6bd",
  "#8b3f96", "#55a049", "#40318d", "#bfce72",
  "#8b5429", "#574200", "#b86962", "#505050",
  "#787878", "#94e089", "#7869c4", "#9f9f9f"
]);
const C = i => PAL[i];
```

| Indeks | Naam | Gebruik |
|---:|---|---|
| 0 | Swart | HUD, skadu, loop/stewels |
| 1 | Wit | syfers, glans, ontploffingskern, POW |
| 2 | Rooi | kopband, granaatgooier, hek, vlamrand |
| 3 | Siaan | waterglans, helikopterruit, HUD-aksent |
| 4 | Pers | beperkte aksente |
| 5 | Groen | speler, palms, jeep |
| 6 | Blou | water, gewone vyande |
| 7 | Geel | pad, spelerkoeëls, kis, offisier |
| 8 | Oranje | vlak-1-grond, sandsak/hout/vuur |
| 9 | Bruin | stamme, brugrand, vlak-2-grond |
| 10/A | Ligrooi/vel | gesigte en hande |
| 11/B | Donkergrys | rotse, mure, vlak-3-grond |
| 12/C | Mediumgrys | helms en klip |
| 13/D | Liggroen | speler/palm-ligpunte |
| 14/E | Ligblou | raam en vyand-ligpunte |
| 15/F | Liggrys | rotor en rots-ligpunte |

`PAL.length===16` alleen is onvoldoende. Elke Canvas-`fillStyle`, `strokeStyle`, spritepiksel, fontpiksel, deeltjie, oortreksel en effek binne die logiese vertoon moet deur `PAL`/`C()` kom. Direkte kleure soos `#ff8800`, RGBA-tussenkleure, gradients, filters en browser-antialiasing op Canvas-teks is verbode. CSS buite die logiese doek mag neutrale bladsy-uitleg doen, maar mag nie as deel van die speelbeeld dien nie.

## 5.3 Sprite Factory-kontrak

Alle kernbeelde is ingeboude pikselmatrikse wat **een keer tydens boot** na offscreen-doeke gerasteriseer en in `SPR` gekas word.

```text
Pikselmatriks → rasterize(matrix, scale=1) → offscreen Canvas → SPR.cache
Runtime → ctx.drawImage(SPR.player.up[frame], x, y)
```

Reëls:

- Geen `document.createElement('canvas')` in die raam-/renderlus nie.
- Deursigtigheid word met ’n sentinel soos `-1` voorgestel; sigbare waardes is slegs paletindekse `0..15`.
- Basiese soldaatmaat: ongeveer `12×14`; sandsak `20×6`; voertuig `16×8`; helikopter ongeveer `30×11`.
- Horisontale links/regs-variante mag vooraf gespieël en gekas word; moenie elke raam transformeer as ’n cache voldoende is nie.

Minimum kas:

- speler: op/af/links/regs × stil/2 looprame;
- gewone infanterie, skutter, granaatgooier, offisier en hul nodige rame;
- motorfiets, jeep en helikopter met rotorvariante;
- sandsak en vernietigde sandsak, rots, palmstam en blaredak;
- brug-/waterteëls waar toepaslik;
- granaatkis se twee flitsrame;
- POW vasgebind en POW-hardlooprame;
- koeëls, granate, skadu, vonk en ontploffingsrame.

Gebruik ’n eie palet-suiwer 5×7- of soortgelyke bitmap-font vir alle speldoekteks. Sluit die Afrikaanse tekens in wat die UI gebruik. Normale `fillText()` is nie aanvaarbaar indien antialiasing nuwe kleure genereer nie.

## 5.4 HUD-kontrak

- Skermkoördinate, nooit wêreldkoördinate nie.
- Reghoek `x=0..319`, `y=0..17`, swart agtergrond.
- Een-piksel ligblou lyn op die onderrand.
- Teken ná die hele wêreld en alle wêreldeffekte.
- Vaste volgorde: `1UP 001500`, `HI 010000`, `VLAK:1`, `GR:6`, `LEWENS:3`.
- Telling en HI is ses syfers met voorloopnulle.
- Waardes word uit dieselfde sessiedata as spelmeganika gelees; geen gedupliseerde HUD-staat nie.

## 5.5 Tekenvolgorde

1. Grondtekstuur en kronkelpad.
2. Riviere, waterglans en brûe.
3. Vestingmure en skuifhek.
4. Rotse, sandsakke en **slegs palmstamme**.
5. Granaatkiste en POW’s.
6. Vyande en speler.
7. Palmblaredakke bo karakters.
8. Koeëls, granate + skaduwees, ontploffings, vonke, helikopter en puntopspringsels.
9. HUD en toestandsoortreksels.

CRT-scanlines/vignet is subtiel, skakelbaar met `C`, en mag nie botsings- of speldata verander nie.

---

# 6. Wêreld-, skerm- en kamerakoördinate

## 6.1 Een waarheid vir posisies

Alle speler-, vyand-, hindernis-, rivier-, projektil-, pickup- en vestingposisies is wêreldkoördinate. Transformeer eers tydens rendering:

```javascript
const screenX = worldX;
const screenY = worldY - camY;
```

Die wêreld is vertikaal langer as die doek. Geen botsing vergelyk `screenY` met `worldY` nie. Die HUD en touch-UI is uitsluitlik skerm/UI-koördinate.

## 6.2 Slegs-noord kamera

```javascript
// Aanvang
camY = STAGE_LEN - SCREEN_H;

// Wanneer speler hoër as 60% van die skerm beweeg:
const desired = player.y - SCREEN_H * 0.60;
camY = Math.max(0, Math.min(camY, desired));
```

Harde invariantes:

- `newCamY <= oldCamY`; die kamera verminder of bly gelyk.
- `camY >= 0`.
- Die speler mag nie onder die sigbare speelrand wegloop nie; klem sy wêreld-Y relatief tot die reeds bereikte kamera.
- ’n Suidwaarts bewegende speler rol nooit die kamera terug nie.
- Vestingaktivering lees die werklike `camY`, nie ’n afgeronde skermposisie nie.

## 6.3 Culling en aktivering

Rendering mag entiteite buite `screenY≈[-32, 232]` oorslaan. KI-aktivering gebruik ’n benoemde marge (aanbeveel: 32–64 px), sodat entiteite net buite die skerm gereed kan word sonder dat verre vyande reeds vuur.

---

# 7. Botsingsverenigbaarheidsmatriks

Die onderstaande tabel is die finale implementasiebesluit. “Oor” beteken ’n granaat se midlugfase ignoreer die vorm; sy landing-ontploffing word apart getoets.

| Wêreldvoorwerp | Speler | Voetvyand | Voertuig | Spelerkoeël | Vyandkoeël | Spelergranaat in vlug | Ontploffing |
|---|---|---|---|---|---|---|---|
| Rivierwater | blok | blok | blok | deur | deur | oor | geen terreinvernietiging |
| Houtbrug | deur | deur | deur indien baan pas | deur | deur | oor | bly heel |
| Palmstam | blok | blok | blok | **deur** | **deur** | oor | bly heel |
| Palmblaredak | deur | deur | deur | deur | deur | oor | visueel onveranderd |
| Rots | blok | blok | blok | blok + wit vonk | blok + vonk | oor | bly heel |
| Sandsak | blok | blok | blok | blok + wit vonk | blok + vonk | oor | spelergranaat vernietig |
| Vestingmuur/geslote hek | blok | blok* | blok | blok + wit vonk | blok + vonk | oor | bly heel |
| Oop hekopening | deur | deur | deur | deur | deur | oor | n.v.t. |

`*` Vestingverdedigers in `FORCED_EXIT` volg §11.3: hulle kry ’n beheerde ontsnappingskorridor deur die oop hek voordat normale botsing/KI oorneem.

Waarom palmstamkoeëls deurlaat: die Meesterprompt lys rots, sandsak en vestingmuur as M60-stoppers en stel dat slegs die onderste stamblok **beweging**; daarom word die stam nie as ’n koeëlstopper bygevoeg nie. As die Meesterprompt later anders bepaal, verander hierdie ry en voeg ’n regressietoets by.

Algemene reëls:

- Gebruik eenvoudige AABB/sirkeltoetse met effens vergewensgesinde voetkaste; die visuele sprite is nie noodwendig die fisiese volume nie.
- Karakter-terreinbotsing toets die voete/onderste liggaam, nie die hele blaredak-oorlap nie.
- Projektilbotsing en bewegingbotsing is afsonderlike maskers.
- ’n Granaat se grondskadu mag geen botsing veroorsaak nie.

---

# 8. Speler-, M60-, granaat-, lewens- en helikopterkontrakte

## 8.1 Speler

- Beweeg in agt rigtings met genormaliseerde invoervektor; diagonale spoed is nie vinniger nie.
- Spoed: ongeveer `74 px/s`.
- Laaste nie-nul bewegingsrigting word as `facing` bewaar.
- Twee looprame wissel net wanneer die speler beweeg; by stilstand bly die laaste rigting sigbaar.
- Aparte op/af/links/regs-aansigte; links kan ’n voorafgekaste spieël van regs wees.
- Normale spelerinvoer werk net in `AKTIEWE_SPEL`; demo voer sintetiese beheer in `AANTREK_DEMO`.

## 8.2 M60-kontrak

```text
Ammunisie:      onbeperk
Interval:       0.13 s tussen skote
Spoed:          ~225 px/s
Leeftyd:        ~0.72 s
Rigting:        laaste kyk-/bewegingsrigting
Skade:          1 per treffer
```

Hou-invoer lewer volgehoue vuur, maar hoogstens een koeël per interval. Gebruik ’n afkoeltyd, nie raammodulo nie. ’n Koeël sterf wanneer sy leeftyd nul bereik, ’n vyand tref, of ’n rots/sandsak/vestingmuur tref. Laasgenoemde skep ’n kort wit vonk. Koeëls ignoreer palmstamme en -blare volgens §7.

## 8.3 Spelergranaat

Voorraad:

- nuwe spel: 6;
- maksimum: 9;
- nuwe vlak: `min(9, huidige + 3)` ná die vlakbonus;
- granaatkis: `min(9, huidige + 4)`.

Gooi is slegs toegelaat as voorraad > 0 en die speler leef. Verminder voorraad presies een keer wanneer die entiteit suksesvol geskep word.

Rigting is **altyd reguit noord**, ongeag `facing`:

```javascript
const startX = player.x;
const startY = player.y;
const endX = startX;
const endY = startY - GRENADE_DISTANCE;

u = clamp(elapsed / duration, 0, 1);
groundX = lerp(startX, endX, u);
groundY = lerp(startY, endY, u);
z = Math.sin(u * Math.PI) * GRENADE_ARC;
drawY = groundY - z;
```

- Teken ’n donker skadu by `(groundX, groundY)`; die sprite by `(groundX, drawY)`.
- Geen midlug-botsing met water, brug, palms, rotse, sandsakke of mure nie.
- By `u>=1`: skep ontploffing, klank en render-only skudding.
- Alle vyande binne ongeveer 35 px neem dodelike/granaatskade soos toepaslik; sandsakke binne die radius word vernietig.
- Die ontploffing gebruik slegs `wit → geel → oranje → rooi` uit `PAL`.

Vyandgranate is ’n aparte tipe: hulle mik na die speler se posisie op die gooi-oomblik, volg ’n boog en is dodelik binne hul ingestelde radius. Hulle verander nooit die speler se granaatvoorraad nie.

## 8.4 Lewens, dood, herlewing en 1UP

Lewensiklus:

```text
ALIVE
  └─ dodelike vyandkoeël / vyandgranaat / liggaamsbotsing
       → DEAD: lives--, dood-FX, vyandelike koeëls skoon
          ├─ lives > 0: wag 1.25 s → RESPAWN → 2.4 s INVULNERABLE → ALIVE
          └─ lives == 0: SPEL_VERBY
```

Reëls:

- `killPlayer()` is idempotent terwyl die speler reeds dood/onkwesbaar is.
- Skoonmaak van vyandelike koeëls mag geen lopende lus laat kraak nie.
- Herleef effens suid/terug van die sterfplek by ’n geldige, nie-soliede posisie en nooit onder die reeds bereikte skermrand nie.
- Onkwesbaarheid word met ’n tydgebaseerde knippering getoon; die speler kan beweeg en vuur.
- Speler-koeëls en permanente wêreldvordering hoef nie by dood herstel te word nie, tensy die Meesterprompt anders bepaal.

1UP:

```javascript
let nextLife = 10000;
function addScore(points) {
  score += points;
  while (score >= nextLife) {
    lives += 1;
    nextLife += 20000;
    playBonusSfx();
  }
}
```

Die `while` hanteer ’n enkele groot puntetoekenning wat meer as een drempel kruis.

## 8.5 Helikopterintro

Slegs op vlak 1:

1. Spawn ’n groen helikopter naby die invoegpunt bo/om die speler.
2. `HOVER`: rotor wissel, romp sweef subtiel.
3. `DEPART`: beweeg skuins regs-bo (`vx>0`, `vy<0`) totdat dit buite die skerm is.
4. Verwyder dit; dit is nie ’n botsingsentiteit nie.

Spelerbeheer is vanaf die begin van `AKTIEWE_SPEL` beskikbaar; die intro is geen input lock of aparte sewende toestand nie. Die neus/sprite-oriëntasie moet by die vertrekbewegingsrigting pas.

## 8.6 Skermskudding

Skudding is uitsluitlik ’n tydelike wêreld-renderoffset:

```javascript
renderX = worldX + shakeX;
renderY = worldY - camY + shakeY;
```

Pas dit op die wêreldlaag toe, nie die HUD nie. Moet nooit `player.x`, `camY`, projektilposisies of botsingsvorms met `shakeX/Y` muteer nie. Gebruik klein heelgetal-offsets (bv. `-2..2`) wat vinnig uitsterf.

---

# 9. Volledige vyand-KI-katalogus

## 9.1 Gemeenskaplike kontrak en aktiveringsvenster

Elke vyand het minstens:

```text
type, x, y, hp, score, active, state,
speed, fireCooldown, facing, fortressDefender
```

Aktiveer KI slegs indien die vyand in of net buite die sigbare venster is, bv.:

```javascript
active = screenY >= -48 && screenY <= SCREEN_H + 48;
```

Voor aktivering:

- geen beweging, skote of granate nie;
- afkoeltye mag gevries wees;
- vlakposisies bly deterministies en onversteurd.

Na aktivering mag ’n vyand aktief bly totdat hy dood of doelbewus verwyder is; dokumenteer die gekose beleid. Verre offscreen-vyande mag nooit die speler skiet nie. Alle beweging respekteer water/brug en soliede hindernisse. Gebruik goedkoop stuurgedrag, nie ’n vereiste A*-stelsel nie.

## 9.2 Infanteriesoldaat

| Eienskap | Kontrak |
|---|---|
| Uniform | blou |
| HP | 1 |
| Punte | 300 |
| Beweging | jaag speler met klein, tydgebaseerde flankvariasie |
| Wapen | enkele gerigte vyandkoeël |
| Hindernisgedrag | probeer primêre vektor; dan X/Y; dan kort sydelingse stuur |

Moenie elke raam willekeurige rigting kies nie; dit skep jitter. Hou ’n flankdoel vir ’n kort tydperk.

## 9.3 Loopgraafskutter

| Eienskap | Kontrak |
|---|---|
| HP | 1 |
| Punte | 300 |
| Beweging | geen; vas agter gekoppelde sandsak |
| Wapen | gerigte koeël, vinniger as infanterie |
| Taktiek | voorste spelerkoeëls tref sandsak; flankeer of gooi granaat |

As die sandsak vernietig word, bly die skutter geldig en blootgestel; moenie hom saam met die sandsak per ongeluk verwyder nie.

## 9.4 Granaatgooier

| Eienskap | Kontrak |
|---|---|
| Uniform | rooi |
| HP | 1 |
| Punte | 500 |
| Beweging | nader as te ver; onttrek as te naby; hou middelafstand |
| Wapen | paraboliese vyandgranaat na spelerposisie by loslaat |

Die speler kan die boog visueel lees deur ’n skadu en duidelike landingstyd. ’n Vyandgranaatontploffing is dodelik, maar vernietig nie noodwendig sandsakke nie; spelergranaat-terreinvernietiging is die normatiewe vereiste.

## 9.5 Motorfietspatrollie

| Eienskap | Kontrak |
|---|---|
| HP | 2 |
| Punte | 500 |
| Beweging | vinnig horisontaal, links→regs of regs→links |
| Gebied | periodiek oor die boonste helfte van die sigbare skerm |
| Wapen | skote tydens die lopie |

Spawn net buite ’n skermsy; kies rigting deterministies of uit die aktiewe sessie-RNG. Despawn nadat dit die teenoorgestelde kant verlaat as dit nie dood is nie.

## 9.6 Pantserjeep

| Eienskap | Kontrak |
|---|---|
| HP | 3 |
| Punte | 500 |
| Beweging | horisontale, vinnige voertuigpatrollie |
| Wapen | gerigte skote |
| Visueel | groen gepantserde voertuig |

Die jeep is taaier as die motorfiets maar gee volgens die Meesterprompt dieselfde 500 punte.

## 9.7 Vestingoffisier

| Eienskap | Kontrak |
|---|---|
| Uniform | geel/goud |
| HP | 2 |
| Punte | 2 000 |
| Beweging | vinniger as gewone infanterie |
| Spawn | laaste item in die vestingry |

Die offisier tel as ’n lewende vestingverdediger totdat hy dood is; die vlak kan nie net ná sy spawn voltooi nie.

## 9.8 Skiet- en mikveiligheid

- Normaliseer mikvektore; hanteer nulafstand veilig.
- Projektilspoed en cooldown skaal met vlakmoeilikheid, maar bly speelbaar.
- Vyande mag nie deur soliede dekking skiet nie.
- Slegs aktiewe vyande vuur.
- Doodtoekenning en punte gebeur presies een keer.

---

# 10. Pickups, POW en bonusse

## 10.1 Granaatkis

Toestande: `VISIBLE → COLLECTED/REMOVED`.

- Wissel tydgebaseerd tussen twee gekaste kleurrame.
- By spelernabyheid/oorlap: `score += 1000`; `grenades=min(9, grenades+4)`; speel bonusklank; wys puntopspring; verwyder presies een keer.
- ’n Kis op 8 granate gee 1 effektiewe granaat, maar steeds 1 000 punte.
- Plaas dit deterministies op bereikbare grond, nooit in water of soliede geometrie nie.

## 10.2 Krygsgevangene (POW)

```text
TIED
  └─ speler binne bevrydingsafstand
      → RESCUED: +2000, bonusklank, banier
          → RUN_SIDEWAYS: kies kortste/veilige skermsy
              → GONE wanneer buite skerm
```

Banier: `KRYGSGEVANGENE GERED! +2000`.

Die POW is nie ’n vyand of dekking nie. Punte word by `RESCUED` gegee, nie weer by `GONE` nie. Die hardloopfase gebruik wêreldkoördinate maar kies ’n sigbare skermsy as doel.

---

# 11. Drie vlaktemas, vesting en vordering

## 11.1 Temas

| Tema | Vlakke | Grond | Pad | Water | Mure |
|---|---|---|---|---|---|
| Buitepos | 1, 4, 7, ... | oranje-bruin | geel | blou | klipgrys |
| Kloof | 2, 5, 8, ... | donkerbruin | grys | siaan | rooi |
| Sitadel | 3, 6, 9, ... | donkergrys klip | grys | blou | blou |

```javascript
const theme = THEMES[(level - 1) % 3];
```

Vlak 4+ herhaal visuele temas, nie moeilikheid nie. Verhoog geleidelik vyandspoed, vyandelike vuurtempo en die formulegedrewe aantal vestingverdedigers. Moenie die spelerkoeëlkonstantes stilweg skaal nie.

## 11.2 Vestinggeometrie

Die Meesterprompt se koördinate is wêreldkoördinate naby die noordpunt:

```text
muurband:          y = 74..98
sentrale opening: x = 128..192
hek:               twee rooi skuifdeure
aktivering:        camY <= 14
```

Wanneer aktivering eenmalig plaasvind:

1. wys `VESTINGHEK MAAK OOP!`;
2. animeer twee deurhelftes weg van die middel;
3. skep ’n verdediger-ry van `10 + level*3`;
4. lewer verdedigers in beheerde sarsies;
5. plaas die offisier laaste.

## 11.3 Geforseerde hekuitgang — verpligte defekregstelling

Elke verdediger gebruik:

```text
QUEUED → SPAWN → FORCED_EXIT → NORMAL_AI → DEAD/REMOVED
```

In `FORCED_EXIT`:

- spawn binne die geldige oop hek-korridor;
- beweeg eers reguit suid totdat die volle voet-botsingskas buite die muur-/hekband is;
- ignoreer normale hindernisvermijding wat hom terug teen die hek kan stuur;
- behou wêreldgrense en botsing met die speler waar veilig;
- skakel dan eenmalig na `NORMAL_AI`.

**Moenie** normale jaag-/hindernis-KI op die spawnraam aktiveer nie. Dit was ’n bekende werklike defek: verdedigers het by ’n muurhoek vasgehaak omdat spawngeometrie en normale navigasie oorvleuel het.

## 11.4 Voltooiingspredikaat en oorgang

```javascript
const cleared = fortress.queue.length === 0 &&
  enemies.every(e => !e.fortressDefender || e.dead);
```

By `cleared`:

1. wys `VESTING VEROORWIN!`;
2. ken `2000 + grenades*200` toe;
3. gaan na `VLAK_VOLTOOI` vir presies 2.9 s;
4. verhoog vlaknommer;
5. gee `+3` granate, gekap op 9;
6. bou volgende deterministiese vlak en gaan na `AKTIEWE_SPEL`.

Moenie voltooi omdat slegs die spawnry leeg is terwyl verdedigers nog leef nie.

---

# 12. Presiese ses-state-toestandsmasjien en timers

Daar is presies hierdie ses topvlaktoestande:

| Toestand | Ingang | Gedrag | Uitgang |
|---|---|---|---|
| `TITELSKERM` | boot of demo klaar | titel, Top-5, knipperprompt | invoer → spel; 3.2 s idle → demo |
| `AANTREK_DEMO` | titel-/spel-verby-idle | outonome speelsessie + aftelbanier | enige sleutel/klik → nuwe regte spel; 15.0 s → titel |
| `AKTIEWE_SPEL` | nuwe spel, hervat of nuwe vlak | volle simulasie en beheer | P/Esc → pouse; vesting skoon → vlak voltooi; 0 lewens → spel verby |
| `GEPOUSEER` | P/Esc tydens spel | simulasie gevries, oortreksel | P/Esc → aktiewe spel |
| `VLAK_VOLTOOI` | vesting skoon | vieringsboodskap en vaste 2.9 s | volgende vlak → aktiewe spel |
| `SPEL_VERBY` | lewens word 0 | finale telling, vlak, moontlike nuwe rekord | invoer → titel; 4.5 s idle → demo |

Oorgangskaart:

```text
TITELSKERM ──3.2s──> AANTREK_DEMO ──15.0s──> TITELSKERM
     │ invoer              │ invoer
     └──────────────> nuwe AKTIEWE_SPEL

AKTIEWE_SPEL <──P/Esc──> GEPOUSEER
AKTIEWE_SPEL ──vesting skoon──> VLAK_VOLTOOI ──2.9s──> AKTIEWE_SPEL
AKTIEWE_SPEL ──0 lewens──> SPEL_VERBY ──4.5s──> AANTREK_DEMO
                                         └─invoer──> TITELSKERM
```

Reëls:

- `stateTime=0` op elke oorgang.
- Demo se duurkonstante is presies `15.0`, nie ’n afgeronde UI-aftelling nie.
- “Idle” word deur geldige gebruikersinvoer teruggestel; demo onderbreking begin ’n skoon regte sessie, nie die demo se telling/wêreld nie.
- `GEPOUSEER` voeg geen simulasietyd by nie.
- Helikopter, dood/herlewing, hekopening en POW is substates/entiteitstoestande, nie ekstra topvlaktoestande nie.

---

# 13. Aantrek-demo-KI

Die demo gebruik dieselfde spelreëls en renderer as ’n regte sessie, maar met sintetiese invoer. Dit is ’n demonstrasie-agent, nie ’n volwaardige optimale bot nie.

Beslisboom, elke kort besluitinterval (bv. 0.1–0.2 s):

```text
1. Standaarddoel = noord.
2. Is ’n rivier/waterband kort voor die speler?
      Doel = middelpunt van daardie rivier se brug.
3. Is ’n aktiewe vyand sigbaar en binne vuurafstand?
      Stel facing/mik na teiken en hou vuur.
4. Is ’n sandsak of vyandgroep noord binne granaatreik en voorraad > 0?
      Gooi een noordwaartse granaat; pas cooldown toe.
5. Het posisie vir langer as die vassteekdrempel skaars verander?
      Kies ’n tydelike links-/regs-systap, daarna hervat noord.
6. Anders: beweeg na huidige noord-/brugdoel.
```

Verpligte eienskappe:

- stuur werklik na 48 px-brugopenings; moenie deur water “cheat” nie;
- vuur via dieselfde `tryFire()` as die speler;
- gooi via dieselfde voorraad- en noordrigtingkode;
- hou noordwaartse vordering;
- wys `DEMO (15s) — DRUK ENIGE SLEUTEL OM TE SPEEL` met oorblywende sekondes;
- enige sleutel of muisklik onderbreek onmiddellik; aanraking tel ook as invoer;
- na presies 15.0 s keer dit terug na die titel.

Gebruik ’n deterministiese besluitvolgorde waar prakties, sodat demo-regressies herhaalbaar is. A* is nie nodig nie.

---

# 14. SID-styl Web Audio-kontrak

Die doel is ’n geloofwaardige 8-bis/MOS 6581-styl klankbeeld, nie siklusakkurate SID-hardeware-emulasie nie.

## 14.1 Veilige lewensiklus

- Skep of hervat `AudioContext` slegs binne die eerste gebruikersgebaar.
- `M` skakel alle spelmusiek/SFX aan of af sonder om spelstaat te raak.
- Omvou skepping, hervatting en nodes in `try/catch`.
- Oudiofaling is nooit dodelik vir die spel nie; gaan stil voort.
- Stop/oudit ou nodes by toestandwisselings om opeenhoping te voorkom.

## 14.2 Drie stemme

1. **Bas:** `sawtooth`, militêre 16de-nootpatroon, 64 stappe, ongeveer `118 ms` per stap.
2. **Hoofmelodie:** `square`, heroïese 8-bis frase wat met die patroon herhaal.
3. **Perkussie/SFX:** een voorafgegenereerde witruisbuffer; banddeurlaat/hoëdeurlaat vir snare/hi-hat, plus gefiltreerde effekte.

Hou melodie- en basnote as ingeboude frekwensie-/MIDI-skikkings. Geen klanklêers of dekodeerders nie.

## 14.3 Verpligte SFX

| Gebeurtenis | Sintese |
|---|---|
| Speler-M60 | kort dalende vierkantpuls; hoër toon |
| Vyandskoot | kort dalende vierkantpuls; laer toon |
| Granaatontploffing | laedeurlaat-witruis wat oor ~0.38 s uitdoof |
| Bonus/1UP/POW | vinnige stygende viernoot-arpeggio |
| Spelerdood | dalende saagtandtoon oor ~0.45 s |

Gebruik kort gain-envelopes om klikgeluide en lang hangende oscillators te voorkom. Musiektempo moet tydgebaseerd wees, nie raamgebaseerd nie.

---

# 15. Invoer, aanraking, browserveiligheid en berging

## 15.1 Beheermatriks

| Aksie | Sleutelbord | Muis | Touch |
|---|---|---|---|
| Beweeg | WASD of pyle | — | D-pad |
| M60 | Q, linker-/regter-Ctrl | linkerknop hou | VUUR hou |
| Granaat | Spasie | regsklik | GRANAAT tik |
| Pouse | P of Escape | opsionele UI | opsionele UI |
| Klank | M | UI-knop | UI-knop |
| CRT | C | UI-knop | UI-knop |

## 15.2 Sleutelbord- en muisveiligheid

- Roep `preventDefault()` vir pyle, Spasie en spelrelevante Ctrl-kombinasies wanneer die speletjie fokus/aktief is.
- Moenie onnodig browserkritieke kombinasies wêreldwyd kaap nie; hanteer presies die speltoetse (`Ctrl+W/A/S/D/Q` waar van toepassing).
- Onderdruk die `contextmenu` op die speelarea sodat regsklik ’n granaat kan gooi.
- Gebruik `keydown`/`keyup`-toestand vir hou-aksies; ignoreer sleutelherhaling vir eenmalige toggles.
- Op `window.blur`, `visibilitychange` na hidden en verlies van pointer/touch: `clearAllInputs()`.
- Enige HTML-knoppie verloor fokus ná klik:

```javascript
button.addEventListener("click", e => {
  action();
  e.currentTarget.blur();
});
```

Anders kan Spasie later die gefokusde knoppie heraktiveer in plaas van ’n granaat gooi.

## 15.3 Aanraakbeheer

Wys touch UI slegs wanneer aanraking of ’n growwe wyser beskikbaar is, bv. `@media (pointer: coarse)` plus ’n runtime-aanraaksein.

Aanbevole konsekwente CSS-afmetings relatief tot die **vertoonde** doek:

- D-pad-area: ongeveer `112×112 CSS px`, links onder, vier knoppies van minstens `44×44 CSS px`;
- VUUR: ronde knoppie ongeveer `64×64 CSS px`, regs onder;
- GRANAAT: ronde knoppie ongeveer `56×56 CSS px`, effens links/bo van VUUR;
- dekking/opacity: sigbaar maar deursigtig (`~0.35–0.55`), sonder om die HUD te bedek;
- minimum raakdoel: 44 CSS px;
- `touch-action: none; user-select: none;` op die spelomhulsel;
- gebruik pointer events en `setPointerCapture()` waar beskikbaar;
- ondersteun meerdere gelyktydige pointers: beweeg + vuur;
- `pointerup`, `pointercancel` en blur stel die betrokke toestand terug.

Touch UI is HTML/CSS buite die `320×200`-spelbeeld en hoef nie deel van die C64-palet te wees nie; die spelbeeld self bly palet-suiwer.

## 15.4 Begin- en demo-invoer

Op titel of demo begin enige sleutel, muisklik of primêre aanraking ’n nuwe regte spel. Verhoed dat dieselfde gebeurtenis ook onmiddellik ’n skoot/granaat in die eerste spelraam veroorsaak; verbruik die begin-gebeurtenis of stel aksies een raam later vry.

## 15.5 Top-5 `localStorage`

Aanbevole sleutel: `commando64.top5.v1`.

Datakontrak:

```json
[
  {"s": 52300, "l": 3},
  {"s": 41100, "l": 2}
]
```

Lees:

1. `try/catch` om `getItem` en `JSON.parse`;
2. bevestig dat dit ’n skikking is;
3. sanitiseer elke rekord na nie-negatiewe heelgetalle `s` en `l`;
4. sorteer dalend op `s` en neem `slice(0,5)`;
5. gebruik `[]` by enige fout.

Skryf slegs aan einde van ’n regte spel, nooit ’n demo nie. Voeg huidige `{s:score,l:level}` by, sorteer dalend en hou vyf. `setItem` bly in `try/catch`. Privaatmodus, kwota- of sekuriteitsfoute mag nooit die spel laat kraak nie. Toon `★ NUWE REKORD! ★` indien die nuwe telling die vorige eerste plek oortref.

---

# 16. Determinismekontrak

Gebruik ’n bekende plaaslike PRNG, bv. `mulberry32`, met ’n vaste afleiding van vlaknommer:

```javascript
function mulberry32(seed) {
  return function () {
    let t = seed += 0x6D2B79F5;
    t = Math.imul(t ^ t >>> 15, t | 1);
    t ^= t + Math.imul(t ^ t >>> 7, t | 61);
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
const rng = mulberry32((BASE_SEED ^ level) >>> 0);
```

Moet deterministies wees vir dieselfde vlaknommer en bouweergawe:

- rivier-Y-posisies en brug-X-posisies;
- padkontrolepunte;
- rotse, palms en sandsakke;
- aanvanklike vyandklasse en spawnposisies;
- granaatkiste en POW-liggings;
- vestinggeometrie en verdediger-rygrootte.

Mag nie presies deterministies wees nie, mits dit spelvereistes nie beïnvloed nie:

- kosmetiese ontploffingsdeeltjies;
- CRT-ruis;
- sommige tydelike KI-flankbesluite;
- skermskudding-offsets.

Vir maksimum regressieherhaalbaarheid is ’n tweede sessie-RNG vir runtime-KI/FX beter as direkte `Math.random()`. Moet nooit wêreldbou met ongekontroleerde `Math.random()` doen nie. Die bouer moet ook geldigheid afdwing: twee nie-oorvleuelende riviere, elke brug bereikbaar, geen kritieke pickup in water/rots nie, en ’n deurlopende roete van invoegpunt tot vesting.

---

# 17. Werkverrigting en geheuereëls

Harde reëls:

- kap elke raam se `dt` by `0.05 s`;
- rasteriseer sprites en fontgliewe by boot, nie per raam nie;
- hergebruik witruisbuffer en waar moontlik deeltjie-/projektilvoorwerpe;
- gebruik agteruitlusse of kompakteer-fases vir verwydering;
- cull ver-af rendering en deaktiveer verre KI;
- vermy `getImageData`, groot stringbou en nuwe canvasse in die hooflus;
- hou water-/padpatrone goedkoop en tydgebaseerd;
- geen onbeperkte skikkings vir deeltjies, popups, koeëls of oudio-nodes nie.

Verborge-oortjie-regressie: versteek die blad vir minstens 10 s en keer terug. Die speler mag nie honderde piksels spring, deur ’n hindernis teleporteer of onmiddellik sterf weens ’n reuse-`dt` nie.

---

# 18. Implementasiehekke

Werk streng in hierdie volgorde. ’n Hek is groen slegs as sy aanvaardingskriteria loop én bewys aangeteken is.

| Hek | Bouwerk | Groen wanneer |
|---|---|---|
| G0 | Shell + presiese Canvas | een plaaslike HTML open; `320×200`; geen konsolefout |
| G1 | Palet + bitmap-font | alle doekkleure uit `PAL`; geen browserfont op speldoek |
| G2 | Sprite Factory | kernsprites gekas; TDD-02 slaag |
| G3 | Ses-state-skulp | alle oorgange en timers benoem; titel werk |
| G4 | Speler + wêreld/skerm + kamera | 8-rigting; kamera nooit suid nie |
| G5 | LevelBuilder + terreinbotsing | twee riviere/brûe; bereikbare roete; TDD-03 |
| G6 | M60 | tempo, rigting, snelheid, leeftyd en dekking korrek |
| G7 | Granate + skudding | voorraad, noordboog, radius, sandsakke korrek; TDD-05 |
| G8 | Infanterie + dood | skade, punte, veilige koeëllus; TDD-04 |
| G9 | Alle KI-klasse | katalogusgedrag en aktiveringsvenster sigbaar |
| G10 | Kis + POW | beide toestandmasjiene en punte werk |
| G11 | Vesting | geometrie, hek, sarsies, forced-exit en offisier werk |
| G12 | Lewens + telling + rekord | 1UP, herlewing en Top-5 werk; TDD-06 |
| G13 | Demo-KI | brug, vuur, granaat, vassteekherstel; TDD-07 |
| G14 | SID-styl oudio | 3 stemme/SFX; gebruikersgebaar; sagte mislukking |
| G15 | Rendering/politoer | tekenvolgorde, temas, HUD, CRT en touch voltooi |
| G16 | Ingeboude TDD | `TDD: 7/7 PASS` sigbaar; geen versteekte skip nie |
| G17 | Volle regressie | afdeling 20 groen; nul ongevange JS-foute |

> **Geen hekvordering terwyl die huidige hek rooi is nie.** Moenie ’n latere kenmerk gebruik om ’n vroeë fundamentele defek weg te steek nie.

Vir elke hek: teken datum/bou-ID, toets, resultaat, defek-ID’s en hertoets in die bewysregister aan.

---

# 19. Ingeboude TDD-spesifikasie

`runTddSuite()` loop by boot teen geïsoleerde data waar moontlik. Toon `TDD: X/7 PASS` in ’n nie-blokkerende knoppie/paneel; ’n klik open besonderhede sonder `alert()` of `confirm()`. ’n Toets is groen slegs as ’n werklike assert uitgevoer is; geen “pass by default” of `try { } catch { pass }` nie.

## TDD-01 — VIC-II-resolusie en palet

- **Doel:** Bewys die vaste logiese vertoon en gesaghebbende 16-kleurbron.
- **Setup:** Boot Canvas, konteks en `PAL`.
- **Aksie:** Lees `canvas.width/height`; vergelyk `PAL` element-vir-element met die 16 vereiste hexwaardes; bevestig `imageSmoothingEnabled===false`; laat ’n bron-/rendereroudit bevestig dat spelkleurtoegang deur `PAL` gaan.
- **Verwag:** `320`, `200`, presies 16 unieke verwagte kleure en smoothing af.
- **Bestaansrede:** ’n 16-lange skikking alleen bewys nie die regte kleure of palet-suiwer rendering nie; verkeerde resolusie/smoothing vernietig die C64-voorkoms.

## TDD-02 — Sprite-rasterisering

- **Doel:** Bewys dat kernbitmaps by boot gegenereer en bruikbaar gekas is.
- **Setup:** Laat SpriteFactory voltooi.
- **Aksie:** Enumerate die vereiste speler-, vyand-, helikopter- en voertuigkas-sleutels; bevestig elke waarde is ’n Canvas/bitmap met breedte en hoogte > 0 en dat rasterdata minstens een nie-deursigtige piksel bevat.
- **Verwag:** Alle verpligte kernsprites bestaan; geen nulafmetings of ontbrekende rigtingrame nie.
- **Bestaansrede:** Vang tikfoute, leë matryse en per-raam noodgegenerering voordat spel begin.

## TDD-03 — Vlakbouer

- **Doel:** Bewys die minimum speelbare wêreldstruktuur.
- **Setup:** Bou ’n vars vlak 1 met die vaste seed.
- **Aksie:** Tel riviere, valideer een 48 px-brug per rivier, kontroleer vestingmuur/opening, en bevestig minstens een vyand plus geldige begin-/eindroete. Herbou vlak 1 en vergelyk kerngeometrie.
- **Verwag:** Presies twee riviere; twee geldige brûe; muur `y=74..98`; opening `x=128..192`; vyande > 0; identiese herbougeometrie.
- **Bestaansrede:** Voorkom onoorsteekbare of nie-deterministiese vlakke en ontbrekende klimaksgeometrie.

## TDD-04 — Koeël-lus-mutasiestabiliteit

- **Doel:** Bewys dat `killPlayer()` ’n vyandelike koeëlskikking kan skoonmaak sonder buitegrenslees of `TypeError`.
- **Setup:** Lewende speler met meer as een vyandelike koeël; een tref in ’n agteruit-update-lus. Instrumenteer om ongeldige reads/uitsonderings te vang.
- **Aksie:** Loop die regte projektil-update; laat die treffer `killPlayer()` roep en die skikking filter/leegmaak.
- **Verwag:** Geen uitsondering; speler verloor presies een lewe; vyandelike koeëls is leeg; lus eindig veilig.
- **Bestaansrede:** Dit reproduseer ’n werklike failure mode waar ’n lus ná mutasie ’n nie-bestaande koeël gelees het. Moenie die indeksherankering verwyder nie.

## TDD-05 — Granaatvoorraad en entiteit

- **Doel:** Bewys atoomse gooi-gedrag.
- **Setup:** Lewende speler, `grenades=6`, geen aktiewe spelergranaat; stel `facing` doelbewus oos.
- **Aksie:** Roep die werklike `tryThrowGrenade()` een keer.
- **Verwag:** Voorraad is 5; presies een granaat bestaan; sy eindpunt het dieselfde X en `startY-68`, dus noord ongeag ooswaartse facing.
- **Bestaansrede:** Vang dubbele aftrekking, entiteitskepping sonder voorraad en die algemene fout “granaat volg facing”.

## TDD-06 — 10 000-punt-1UP

- **Doel:** Bewys die eerste ekstralewedrempel en volgende drempel.
- **Setup:** `score=9900`, `lives=3`, `nextLife=10000`.
- **Aksie:** Voeg 100 punte met die werklike `addScore()` by.
- **Verwag:** `score=10000`, `lives=4`, `nextLife=30000`; een bonusgebeurtenis.
- **Bestaansrede:** Verhoed `>` in plaas van `>=`, herhaalde 1UP’s en verkeerde 20k-reeks.

## TDD-07 — Demo presies 15.0 sekondes

- **Doel:** Bewys die normatiewe demo-duur en uitgang.
- **Setup:** Gaan na `AANTREK_DEMO`, `stateTime=0`, geen invoer; bevestig `DEMO_DURATION===15.0`.
- **Aksie:** Simuleer tyd tot net onder 15.0 s en dan tot/op 15.0 s met gekapte stappe.
- **Verwag:** Demo bly aktief voor 15.0; gaan by 15.0 na `TITELSKERM`; geen demo-staat lek na ’n regte sessie nie.
- **Bestaansrede:** UI-aftelling, drywende punt en foutiewe timerreset kan anders ’n korter/langer demo gee.

## 19.1 TDD-uitvoerformaat

```text
TDD: 7/7 PASS
TDD-01 PASS — canvas/palette
TDD-02 PASS — sprite cache
TDD-03 PASS — deterministic level
TDD-04 PASS — bullet mutation safety
TDD-05 PASS — north grenade
TDD-06 PASS — 10k 1UP
TDD-07 PASS — 15.0s demo
```

’n TDD-mislukking keer nie noodwendig die toets-UI se rendering nie, maar maak die vrystelling rooi.

---

# 20. Full-flow regressiespeelboek

Voer dit in ’n werklike moderne Chromium/Chrome-klas blaaier uit met DevTools-konsole oop. Herhaal kernstappe met vars berging en bestaande Top-5.

| ID | Setup en aksie | Verwagte bewys |
|---|---|---|
| REG-01 | Open `index.html` direk en herlaai | Titel verskyn; geen netwerkafhanklikheid; 0 ongevange foute |
| REG-02 | Wag 3.2 s; kyk demo; druk ’n sleutel/klik voor 15 s | Titel→demo; aftelling; KI beweeg/vuur; invoer begin skoon regte spel |
| REG-03 | Begin vlak 1 en kyk HUD/helikopter | Afrikaanse HUD; 3 lewens/6 granate; helikopter sweef, neus korrek, vertrek regs-bo; beheer dadelik |
| REG-04 | Beweeg 8 rigtings, ook diagonaal | konstante ~74 px/s; geen vinniger diagonaal; 2-raam animasie |
| REG-05 | Loop teen water, dan oor brug; beweeg terug suid | water blokkeer; 48 px-brug werk; kamera het slegs noord gerol en rol nie terug nie |
| REG-06 | Hou M60 in; draai; skiet vyand, rots, sandsak, muur en palm | 0.13 s; laaste facing; beperkte reik; vonk/stop by 3 soliede tipes; palm laat deur |
| REG-07 | Kyk oos, gooi granaat by sandsakgroep | voorraad -1; granaat steeds noord; boog/skadu; spring oor; sandsak vernietig; radius/skudding werk |
| REG-08 | Loop onder palmblaredak en om stam | stam blokkeer voete; blare nie; blaredak teken bo speler/vyand |
| REG-09 | Ontmoet infanterie, skutter en granaatgooier | HP/punte, beweging, dekking en wapenpatrone pas katalogus |
| REG-10 | Ontmoet motorfiets en jeep | horisontale lopies, 2/3 HP, skote en 500 punte elk |
| REG-11 | Versamel kis by lae en by 8 granate | +1000; +4 gekap op 9; flits; eenmalige verwydering |
| REG-12 | Bevry POW | +2000; presiese banier; hardloop sywaarts; verdwyn; geen dubbele punte |
| REG-13 | Bereik `camY<=14` | waarskuwing; korrekte muur/opening; twee deure skuif oop |
| REG-14 | Laat hele vestinggolf kom | `10+level×3`; sarsies; niemand haak in hek; offisier laaste en 2 HP/2000 |
| REG-15 | Dood laaste verdediger en wag | voltooi net ry én verdedigers leeg; bonus korrek; 2.9 s; +3 granate cap; vlak 2, dan vlak 3 se temas |
| REG-16 | Laat speler deur elke dodelike tipe sterf | presies een lewe; koeëls skoon; 1.25 s; geldige herlewing; 2.4 s knipper/onkwesbaar |
| REG-17 | Kry 10k; verloor alle lewens; herlaai | 1UP op 10k; spel-verby; rekord/Top-5 veilig; 4.5 s→demo; data oor herlaai |
| REG-18 | P/Esc, M en C; toets knoppie en dan Spasie | pouse vries; klank/CRT toggle; gefokusde knoppie steel nie granaat nie |
| REG-19 | Hou beweging/vuur; wissel venster/oortjie vir 10 s | sleutels reset; geen vasgeloopte invoer; geen `dt`-teleport of massaskade |
| REG-20 | Werklike growwe-pointer/toestel: beweeg+vuur gelyk, kanselleer aanraking | touch UI verskyn; ≥44px teikens; geen scroll/zoom; multi-touch; cancel reset |
| REG-21 | Begin met klank, mute/unmute; simuleer geweierde AudioContext | musiek/SFX soos gespesifiseer; geen spelcrash as oudio faal nie |
| REG-22 | Laat demo ononderbroke loop | by presies 15.0 s terug titel; geen regte rekordskryf nie |
| REG-23 | Bou dieselfde vlak twee keer | riviere/brûe/hindernisse/spawns/pickups identies |
| REG-24 | Profiel ’n besige skerm | geen per-raam spritecanvasse; skikkings bly begrens; aanvaarbare gladheid |

Volledige pad wat in een sessie bewys moet word:

```text
TITELSKERM → 3.2 s → AANTREK_DEMO → invoer → AKTIEWE_SPEL
→ helikopter → beweging → brug → M60 → noordgranaat oor sandsak
→ hek aktiveer/oop → sarsies → offisier → VLAK_VOLTOOI
→ Vlak 2 → Vlak 3-tema → dood → herlewing → lewens 0
→ SPEL_VERBY → Top-5 → 4.5 s → AANTREK_DEMO
```

---

# 21. Bekende failure modes en valstrikke

| ID | Valstrik / simptoom | Worteloorsaak | Verpligte voorkoming/regressie |
|---|---|---|---|
| V-001 | Canvas-teks lyk sag of bevat nuwe kleure | browserfont-antialiasing | bitmap-font; paletoudit; TDD-01 |
| V-002 | Botsings skuif wanneer kamera rol | wêreld- en skerm-Y gemeng | bots alles in wêreldruimte; §6; REG-05 |
| V-003 | Kamera rol terug suid | gewone volgkamera/`lerp` sonder monotone klem | `newCamY<=oldCamY`; REG-05 |
| V-004 | Granaat vlieg in facing-rigting | M60-rigting hergebruik | eind-Y altyd `startY-68`; TDD-05 |
| V-005 | Blaredak is ’n onsigbare muur | spritegrens as collision gebruik | aparte stamvoetkas; REG-08 |
| V-006 | M60 vernietig sandsakke | generiese skade op alle obstacles | koeël stop/vonk; slegs spelergranaat vernietig |
| V-007 | Vestingverdedigers haak by muurhoek | normale KI begin binne spawngeometrie | `FORCED_EXIT`; REG-14 |
| V-008 | `TypeError` ná speler getref is | `killPlayer()` wis koeëls binne lopende lus | agteruitlus + indeksherankering; TDD-04 |
| V-009 | Speler teleporteer ná tabwissel | ongekapte delta-tyd | `dt<=0.05`; REG-19 |
| V-010 | Geen klank of `AudioContext`-fout | konteks voor gebruikersgebaar | lazy create/resume + `try/catch`; REG-21 |
| V-011 | Spasie klik UI-knoppie i.p.v. granaat | HTML-knoppie behou fokus | `currentTarget.blur()`; REG-18 |
| V-012 | Dieselfde vlak verskil per herlaai | `Math.random()` in LevelBuilder | seeded RNG; TDD-03/REG-23 |
| V-013 | Demo loop vas teen rivier | blinde noord-beweging | brugmiddelpuntprioriteit + vassteeksystap |
| V-014 | Demo se eerste sleutel gooi dadelik ’n granaat | begin-event lek na spelaksie | verbruik begin-event; §15.4 |
| V-015 | Vlak voltooi terwyl vyande leef | slegs spawnry getoets | ry leeg **en** lewende defenders nul |
| V-016 | Offisier kom nie laaste nie | generiese shuffle/spawn | voeg offisier eksplisiet laaste by |
| V-017 | Dubbele punte/1UP/pickup | dooie/versamelde entiteit meermaals verwerk | toestand/`awarded`-vlag; verwyder een keer |
| V-018 | Herlewing binne rots/water | rou sterfposisie hergebruik | soek geldige terugwaartse spawn |
| V-019 | Touch hou beweging ná vinger lig | `pointercancel`/blur ontbreek | capture + alle eind-/cancel-paaie reset |
| V-020 | Palet het 16 inskrywings maar doek bevat ander kleure | direkte hex/RGBA/gradient elders | sentrale `C()` + bron-/pikseloudit |
| V-021 | Hek lyk oop maar botsing bly toe | render- en collision-state verskil | een `gate.openAmount/state` as bron |
| V-022 | Skudding verander botsing/kamera | world data gemuteer vir effek | renderoffset alleen; §8.6 |
| V-023 | Vyande skiet van ver buite skerm | geen aktiveringsvenster | KI en cooldown slegs naby sigbaar |
| V-024 | Rekordfout kraak spel | ongevange `localStorage`/JSON | sanitiseer + `try/catch`; §15.5 |
| V-025 | Prestasie sak met tyd | onbeperkte deeltjies/oudionodes/sprites | limiete, cleanup, caches, profiel |
| V-026 | Helikopter vlieg “agteruit” | spriteoriëntasie pas nie snelheid nie | neus en `vx/vy` saam verifieer; REG-03 |
| V-027 | Vyandkoeëls raak deur dekking | trefvolgorde toets speler voor muur | naaste botsing/obstacle eerste |
| V-028 | Diagonale beweging is 1.414× vinniger | invoervektor nie genormaliseer nie | normaliseer voor `PLAYER_SPEED` |

Wanneer ’n nuwe defek gevind word: gee dit ’n ID, reproduksiestappe, worteloorsaak, regstelling, toets en hertoetsbewys. “Fixed AI” is nie ’n voldoende inskrywing nie.

---

# 22. Bewys- en artefakkontrak

## 22.1 Vrystellingsartefak

Die enigste runtime-artefak is `index.html`. Dit moet saam met hierdie dokument en die Meesterprompt oorgedra kan word, maar mag hulle nie tydens runtime nodig hê nie.

Minimum vrystellingsmanifest:

```text
BUILD
  version:             __________
  build/chat ID:       __________
  timestamp:           __________
  file:                index.html
  SHA-256 (opsioneel): __________

STATIC
  parse/syntax:        PASS / FAIL
  external URLs:       0
  external assets:     0
  alert/confirm:       0
  [A]..[I]:            PASS / FAIL

TDD
  result:              __/7 PASS

BROWSER
  naam/weergawe:       __________
  direkte file-open:   PASS / FAIL
  uncaught console:    0

REGRESSION
  REG-01..24:          PASS / FAIL / NVT met rede
```

## 22.2 Skermbewys

Aanbevole plaaslike bewyslêers (nie runtime-afhanklikhede nie):

```text
title.png
demo.png
bridge.png
grenade_sandbag.png
gate_open.png
gate_defenders.png
level2.png
level3.png
respawn.png
gameover.png
tdd_7of7.png
console_zero_errors.png
```

Vir ’n blinde Antarktika-herboutoets hoef hierdie nie vooraf meegestuur te word nie; die ontvanger genereer nuwe bewyse. ’n Screenshot bewys voorkoms, nie gedrag alleen nie; koppel dit aan die relevante REG-ID en toetsnotas.

## 22.3 Verbode bewyspraktyke

- “Dit behoort te werk” sonder werklike blaaierloop.
- Slegs TDD 7/7 sonder die volle regressiepad.
- Slegs screenshots sonder aksie/verwagte resultaat.
- Om bekende ongetoetste touch/klank as PASS te merk.
- Om ’n konsole met foute weg te sny.

---

# 23. Volledige ouditspoor en engineering decision record

## 23.1 Historiese besluit- en defekregister

Hierdie register bewaar die kennis wat die herbouer andersins sou verloor. “Bewys vereis” beteken die nuwe herbouwerk moet die genoemde regressie self uitvoer; ’n vorige bou se bewering is nie outomaties nuwe bewys nie.

### A-001 — Enkel-lêer, nul-afhanklikheid

- **Intent:** Maak die spel sonder internet of toolchain uitvoerbaar.
- **Besluit:** Alle CSS, JS, sprites, font, musiekdata en toetse in `index.html` binne ’n IIFE.
- **Rede:** Die Antarktika-ontvanger het geen npm/CDN/assets nie.
- **Gevolg:** Runtime asset loaders en ES-modules wat ’n bediener nodig het, is verbode.
- **Bewys:** OUT-001/002, REG-01.

### A-002 — Eie bitmap-font

- **Intent:** Bewaar presies die C64-palet.
- **Aanvanklike risiko:** Gewone browserfonts kan antialiased tussenkleure skep.
- **Besluit:** Kas ’n eie palet-suiwer pikselfont, insluitend gebruikte Afrikaanse tekens.
- **Bewys:** TDD-01 plus palet-/visuele oudit.

### A-003 — Boot-time Sprite Factory

- **Intent:** Reproduseer assets sonder eksterne spriteblaaie en vermy per-raam allokasie.
- **Besluit:** Ingeboude indeksmatrikse → offscreen-doeke → `SPR`-kas.
- **Bewys:** TDD-02 en profiel in REG-24.

### A-004 — Wêreldruimte as fisikawaarheid

- **Intent:** Hou botsing korrek terwyl ’n lang wêreld rol.
- **Besluit:** Alle fisika in wêreldkoördinate; `screenY=worldY-camY` net vir rendering.
- **Bewys:** REG-05/08.

### A-005 — Monotone noordkamera

- **Intent:** Bewaar eenrigting-arkadevordering.
- **Besluit:** `camY` mag net afneem en word by 0 geklem.
- **Bewys:** REG-05 plus invariantlog.

### A-006 — Noord-only spelergranate

- **Intent:** Volg die oorspronklike kernreël, al kyk die speler elders.
- **Besluit:** Granaat-eindpunt gebruik dieselfde X en Y minus 68.
- **Bewys:** TDD-05/REG-07.

### A-007 — Palmstamprojektilbesluit

- **Intent:** Los die vorige dubbelsinnigheid eksplisiet op.
- **Besluit:** Stam blokkeer voet-/voertuigbeweging maar nie koeëls nie; blaredak is uitsluitlik ’n visuele oorlaag.
- **Rede:** Die Meesterprompt noem net rots, sandsak en muur as M60-stoppers en sê die stamblok keer beweging.
- **Bewys:** Botsingsmatriks en REG-06/08.

### D-001 — Vestingverdedigers sit vas

- **Waargenome simptoom:** Sommige verdedigers het by ’n vestingmuurhoek vasgehaak en die golf kon stol.
- **Worteloorsaak:** Normale hindernisvermijding het onmiddellik binne/teen spawngeometrie begin.
- **Verwerpte pleister:** Groter willekeur of teleportasie sonder toestand.
- **Regstelling:** `SPAWN → FORCED_EXIT → NORMAL_AI`; eers suid deur die oop korridor.
- **Bewys:** REG-14; voltooi ook REG-15.
- **Les:** Spesiale spawnsones benodig ’n eksplisiete oorgangstoestand.

### D-002 — Koeëlskikking muteer tydens iterasie

- **Waargenome simptoom:** ’n Treffer kon die speler doodmaak, alle vyandelike koeëls wis en die lopende lus ’n ongeldige element laat lees.
- **Worteloorsaak:** Skikkinglengte het binne iterasie verander.
- **Regstelling:** Agteruitlus, indeksherankering, nulwag en vroeë breek.
- **Bewys:** TDD-04.
- **Les:** Dodelike side effects moet in die toets se werklike update-pad nageboots word.

### D-003 — Helikopteroriëntasie

- **Waargenome simptoom:** Die helikopter kon visueel agteruit vlieg.
- **Worteloorsaak:** Vertreksnelheid en sprite-neus het nie ooreengestem nie.
- **Regstelling:** Vlak-1 vertrek is regs-bo en die sprite wys in daardie rigting.
- **Bewys:** REG-03.

### A-008 — Render-only skermskudding

- **Intent:** Gee impak sonder nie-deterministiese fisika.
- **Besluit:** Klein uitsterwende offset op wêreldrendering; HUD en wêrelddata onveranderd.
- **Bewys:** REG-07 en koördinaatinspeksie.

### A-009 — Ses topvlaktoestande, substates vir detail

- **Intent:** Vermy verborge sewende/agtste toestande en timerlekkasies.
- **Besluit:** Presies ses normatiewe topvlaktoestande; dood, helikopter, hek en POW bly substates.
- **Bewys:** toestandoudit en TDD-07.

### A-010 — Foutverdraagsame browserdienste

- **Intent:** Speelbaarheid behou as berging of oudio geweier word.
- **Besluit:** `localStorage` en `AudioContext` is opsionele vermoëns agter `try/catch` en veilige verstekke.
- **Bewys:** REG-17/21.

### A-011 — Deterministiese wêreld, begrensde kosmetika

- **Intent:** Maak vlakdefekte herhaalbaar sonder om alle effekte rigied te maak.
- **Besluit:** Geometrie/spawns/pickups seeded per vlak; sekondêre FX mag ’n aparte RNG gebruik.
- **Bewys:** TDD-03/REG-23.

### A-012 — Toetsbaarheid sonder blokkerende dialoë

- **Intent:** Toon TDD-bewys sonder om spelvloei te versteur.
- **Besluit:** Nie-blokkerende `TDD: X/7 PASS`-paneel/modaal; geen `alert()`/`confirm()`.
- **Bewys:** bronsoektog en G16.

## 23.2 Sjabloon vir nuwe inskrywings

```markdown
### D-___ — Kort titel
- Intent/vereiste:
- Reproduksie:
- Aanvanklike implementasie:
- Waargenome mislukking:
- Worteloorsaak:
- Regstelling:
- Verwante requirement-ID's:
- Bewys/REG/TDD:
- Hertoetsresultaat:
- Les:
```

Geen betekenisvolle verandering word slegs as “fixed”, “polished” of “refactored” aangeteken nie.

---

# 24. Bekende beperkings en nie-doelwitte

Hierdie bouwerk is doelbewus **nie**:

- siklusakkurate MOS 6581 SID- of volledige C64-hardeware-emulasie nie;
- ’n ROM-poort of binêre emulasielaag nie;
- netwerk-, wolk-, telemetrie- of multiplayer-sagteware nie;
- ’n npm-/bundler-/serverprojek nie;
- afhanklik van eksterne sprites, fonts, musiek, biblioteke of CDN’s nie;
- ’n moderne fisika-, deeltjie- of padvind-enjin nie;
- ’n savegame-stelsel buiten foutveilige Top-5-tellings nie;
- ’n belofte van pixel-perfekte ooreenkoms met elke historiese C64-weergawe buite die Meesterprompt se gespesifiseerde gedrag nie;
- ’n vereiste vir A* of masjienleer in die demo-KI nie.

Klankkwaliteit en touch-gevoel moet op werklike hardeware getoets word; ’n koplose of stil toetsblaaier kan dit nie bewys nie. Browser-`localStorage` kan in privaat-/beperkte omgewings onbeskikbaar wees; die spel moet dan steeds werk sonder volgehoue rekord.

---

# 25. Definition of Done

Merk niks af op grond van bedoeling of kode-inspeksie alleen waar ’n runtime-toets beskikbaar is nie.

## Artefak en argitektuur

- [ ] Presies een dadelik speelbare `index.html`.
- [ ] Geen eksterne assets, imports, netwerkversoeke of runtime-afhanklikhede.
- [ ] IIFE met `'use strict'` en duidelike `[A]`–`[I]`-hoofkommentaar.
- [ ] Geen `alert()`/`confirm()`; 0 ongevange JavaScript-foute.
- [ ] Alle speler-sigbare teks is natuurlike Afrikaans.

## Beeld en UI

- [ ] Logiese doek is presies `320×200`; smoothing af; CSS pixelated.
- [ ] Presies die gespesifiseerde 16 paletkleure en palet-suiwer speldoek.
- [ ] Gekaste ingeboude sprites en bitmap-font; geen per-raam rasterisering.
- [ ] HUD is 18 px met korrekte volgorde, syfers en onderlyn.
- [ ] Negenlaag-tekenvolgorde, insluitend blaredak bo karakters.
- [ ] CRT-effek skakel met `C` en verander geen speldata nie.

## Wêreld en speler

- [ ] 8-rigting ~74 px/s met diagonale normalisering en 2-raam animasie.
- [ ] Wêreld/skermkoördinate word nooit in botsing gemeng nie.
- [ ] Kamera begin onder, rol net noord en word by 0 geklem.
- [ ] Elke vlak het twee riviere, elk met ’n 48 px bereikbare brug.
- [ ] Botsingsmatriks vir water, brug, palms, rots, sandsak en vesting is geïmplementeer.

## Wapens en lewens

- [ ] M60: onbeperk, 0.13 s, ~225 px/s, ~0.72 s, laaste facing.
- [ ] M60 stop/vonk teen rots/sandsak/muur en vlieg deur palms.
- [ ] Granate: 6 begin, max 9, +3 vlak, +4 kis; voorraad atooms.
- [ ] Granate vlieg altyd noord ~68 px, boog 26 px, radius ~35 px.
- [ ] Granate spring oor hindernisse, vernietig sandsakke en veroorsaak render-only skudding.
- [ ] 3 beginlewens; dodelike tipes, koeëlskoonmaak, 1.25 s en 2.4 s korrek.
- [ ] 1UP by 10k en elke daaropvolgende 20k-drempel.
- [ ] Vlak-1-helikopter sweef en vertrek korrek sonder input lock.

## KI, items en vordering

- [ ] Al ses vyandklasse se HP, punte, beweging, wapens en spawnreëls pas §9.
- [ ] Aktiveringsvenster voorkom verre offscreen-KI/skote.
- [ ] Flitsende granaatkis en volledige POW-toestandmasjien werk.
- [ ] Drie temas lus korrek; moeilikheid neem toe.
- [ ] Vestinggeometrie, `camY<=14`, `10+level×3`, sarsies en laaste offisier werk.
- [ ] Alle hekverdedigers gebruik `FORCED_EXIT`; geen hekvassteek nie.
- [ ] Vlak voltooi net met leë ry én nul lewende verdedigers.
- [ ] Bonus, 2.9 s oorgang en granaatcap is korrek.

## Toestande, demo, oudio en invoer

- [ ] Presies ses topvlaktoestande en 3.2/15.0/2.9/4.5 s timers.
- [ ] Demo stuur oor brûe, vuur, gooi granate, herstel uit vassteek en duur presies 15.0 s.
- [ ] Drie-stem SID-styl musiek en vyf SFX-families; oudio faal sag.
- [ ] Sleutelbord, muis en touch werk; browserdefaults/blur/fokus/cancel is veilig.
- [ ] Touch-doelwitte en multi-touch is op werklike growwe-pointerhardeware getoets.
- [ ] Top-5 lees/skryf/sorteer/sny/sanitiseer foutveilig; demo skryf nie.

## Ingenieursbewys

- [ ] Vlakbouer is seeded en dieselfde vlak herbou identies.
- [ ] `dt` is hard gekap by 0.05 s en die verborge-oortjie-toets slaag.
- [ ] `runTddSuite()` toon werklike `7/7 PASS`.
- [ ] REG-01 tot REG-24 is uitgevoer; enige NVT het ’n eerlike rede.
- [ ] Volle een-sessie-pad van titel tot demo, vlak 3, dood/herlewing en spel-verby slaag.
- [ ] Bewysmanifest, defekregister en ouditspoor is bygewerk.

Die bouwerk is slegs **KLAAR** wanneer alle toepaslike blokkies groen is, nul vrystellingsblokkers oop is, TDD 7/7 slaag en die volle regressie nul ongevange foute lewer.

---

# 26. Offline handover checklist

## 26.1 Blinde herboutoets-pakket

```text
STUUR:
[ ] Commando_MasterPrompt.md
[ ] Commando_bootstrap.md
[ ] README_FIRST.txt (opsioneel; wys na die twee dokumente)

MOENIE STUUR VIR DIE BLINDE HERBOUFASE NIE:
[ ] bestaande index.html/bronkode
[ ] vorige chatgeskiedenis
[ ] vorige screenshots of opname
[ ] aanlyn verwysings/URLs
[ ] sprite-, font- of klanklêers

VERWAGTE UITVOER:
[ ] index.html

EERSTE AANVAARDINGSHEK:
[ ] TDD 7/7 PASS

FINALE AANVAARDING:
[ ] REG-01..24 en volle vloei groen
[ ] 0 ongevange JavaScript-foute
[ ] 0 runtime-netwerkversoeke
```

## 26.2 Finale ontvangerkontrole

- [ ] Beide dokumente open in ’n gewone teksredigeerder.
- [ ] Die botsingsreël “Meesterprompt wen” is verstaan.
- [ ] Geen stap veronderstel npm, CDN, internet of vorige bron nie.
- [ ] Die ontvanger kan binne 30 minute G0–G4 se skulp begin.
- [ ] Alle konstantes, paletwaardes, geometrie en timers is plaaslik beskikbaar.
- [ ] Die 25-gapingsregister wys waar elke voorheen ontbrekende kontrak nou woon.
- [ ] Die sewe toetse bevat doel, setup, aksie, verwagte resultaat en bestaansrede.
- [ ] Bekende defekte (hekvassteek, koeëlmutasie, helikopteroriëntasie) het eksplisiete regressies.
- [ ] Die bewysformaat laat ’n onafhanklike beoordelaar PASS/FAIL bepaal.

## 26.3 Handover-verklaring

```text
Ek bevestig dat hierdie pakket genoegsame plaaslike kennis bevat om
COMMANDO 64 van nul af te herbou sonder internet, bestaande bronkode,
eksterne assets of toegang tot die vorige ontwikkelaar.

Bou-ID:        ____________________
Oordraer:      ____________________
Ontvanger:     ____________________
Datum:         ____________________
TDD:           ____ / 7
Regressie:     PASS / FAIL
Oop blokkers:  ____________________
```

---

## Slotbeginsel

> Bou die Meesterprompt, gebruik hierdie Bootstrap om dit korrek en herhaalbaar te bou, en aanvaar geen kenmerk as voltooi voordat die gedrag in ’n werklike blaaier bewys is nie.
