# Amptelike Bronne en Verwysingsregister

## 1. Amptelike Arturia Ondersteuningsartikels
- **Arturia deïnstallering & macOS plugin-paaie**:  
  https://support.arturia.com/hc/en-us/articles/4405741261714-How-to-properly-uninstall-an-Arturia-software
- **Arturia Software Center (ASC) handmatige deïnstallering**:  
  https://support.arturia.com/hc/en-us/articles/8095970969628-Arturia-Software-Center-ASC-Manual-uninstall-and-reinstall
- **Ontbrekende presets & db.db3 indeksering**:  
  https://support.arturia.com/hc/en-us/articles/12635564332316-Missing-presets-Cannot-browse-presets
- **Aanpassing van Arturia hulpbronpad (Resource folder & simskakels)**:  
  https://support.arturia.com/hc/en-us/articles/4405741448850-Arturia-Software-Center-ASC-Customise-your-resource-folder-location
- **ASC voorkeure herstel (verlies van pasgemaakte ligging)**:  
  https://support.arturia.com/hc/en-us/articles/26778537272988-Arturia-Software-Center-ASC-How-to-delete-ASC-preferences-files
- **Volledige skyftoegang (Full Disk Access) & macOS sekuriteit**:  
  https://support.arturia.com/hc/en-us/articles/4405748231442-Software-Bug-issue-or-crash-What-can-I-do

---

## 2. macOS Stelsel- en Installeerder-argitektuur
- **Apple PackageKit (`shove`)**:  
  Die interne macOS-komponent wat lêers vanaf tydelike installeringsandkaste (`/Library/InstallerSandboxes/`) na hul teikenbestemmings skuif. Op moderne macOS verhoed `shove` die volg van simboliese skakels wat oor lêerstelselgrense heen wys (*cross-device symlinks*, bv. vanaf die APFS-stelselvolume na 'n eksterne volume soos `/Volumes/data1`), wat lei tot `Operation not permitted` foutboodskappe in `/var/log/install.log`.
- **Apple Audio Unit Validering (`auval`)**:  
  Die amptelike macOS opdraglyn-nutsding (`/usr/bin/auval`) wat gebruik word deur Logic Pro, GarageBand en ander CoreAudio DAWs om inprop-argitektuur, versoenbaarheid en parameter-validering te toets.
- **SQLite 3 (`sqlite3`)**:  
  Arturia gebruik SQLite 3 databasisse (`db.db3`) om preset-metadata, kategorieë, etikette en gunstelinge te indekseer vir hul in-inprop blaaier.

---

## 3. Gevalgeskiedenis en Chronologie
- **22 September**: Rev LX-24 hulpbronne was onvolledig; 'n skoon herinstallering plus die herstel van 101 fabrieks-presets en databasis-indeksering het die probleem tydelik opgelos. Destyds is 'n tweede Mac as bron gebruik. Hierdie vaardigheid vereis NIE 'n tweede rekenaar nie.
- **29 Oktober**: `db.db3` is hergebou (~20 MB), maar Delay BRIGADE het steeds 0 presets getoon. Ondersoek na vouernesting het getoon dat databasis-herbouing alleen nie kan werk as die onderliggende preset-lêers fisies van die skyf afwesig is nie.
- **5 November (Definitiewe Deurbraak)**:  
  - **Oorsaak bewys**: Die `preinstall`-skrifte wis die bestaande presets uit (`rm -rf ...`), waarna Apple PackageKit se `shove` faal om die nuwe presets oor die `cross-device symlink` te skuif (`Operation not permitted`). Dit laat die gidse leeg en genereer `postdbc_ko.info`.
  - **Oplossing geïmplementeer**: Amptelike Arturia resources-pakkette is direk vanaf Arturia se CDN afgelaai, met `pkgutil --expand-full` buite Apple se sandkas uitgepak, die 3-vlak geneste gidse reggestel, die 2.309 fabrieks-presets herstel en `databaseCreator` uitgevoer. Alle 39 FX-inproppe is suksesvol in Logic Pro getoets en geverifieer.

---

## 4. Arturia FX Collection CDN Register (39 Produkte)
Basis-URL formaat: `https://dl.arturia.net/products/{slug}/soft/components/{package}`

| FX Naam | CDN Slug | Amptelike Hulpbronpakket |
|:---|:---|:---|
| Filter MINI | `mini-filter` | `Filter_MINI__1_9_1_6566__resources.pkg` |
| Filter SEM | `sem-filter` | `Filter_SEM__1_8_1_6566__resources.pkg` |
| Filter M12 | `m12-filter` | `Filter_M12__1_8_1_6566__resources.pkg` |
| Pre 1973 | `1973-pre` | `Pre_1973__1_9_1_6566__resources.pkg` |
| Pre TridA | `trida-pre` | `Pre_TridA__1_8_1_6566__resources.pkg` |
| Pre V76 | `v76-pre` | `Pre_V76__1_8_1_6566__resources.pkg` |
| Comp TUBE-STA | `comp-tubesta` | `Comp_TUBE-STA__1_7_1_6566__resources.pkg` |
| Comp VCA-65 | `comp-vca65` | `Comp_VCA-65__1_7_1_6566__resources.pkg` |
| Comp FET-76 | `comp-fet76` | `Comp_FET-76__1_7_1_6566__resources.pkg` |
| Delay TAPE-201 | `delay-tape201` | `Delay_TAPE-201__1_7_1_6566__resources.pkg` |
| Delay BRIGADE | `delay-brigade` | `Delay_BRIGADE__1_7_1_6566__resources.pkg` |
| Delay ETERNITY | `delay-eternity` | `Delay_ETERNITY__1_7_1_6566__resources.pkg` |
| Rev SPRING-636 | `rev-spring636` | `Rev_SPRING-636__1_6_1_6566__resources.pkg` |
| Rev PLATE-140 | `rev-plate140` | `Rev_PLATE-140__1_7_1_6566__resources.pkg` |
| Rev INTENSITY | `rev-intensity` | `Rev_INTENSITY__1_6_1_6566__resources.pkg` |
| Chorus DIMENSION-D | `chorus-dimension-d` | `Chorus_DIMENSION-D__1_5_1_6566__resources.pkg` |
| Phaser BI-TRON | `phaser-bi-tron` | `Phaser_BI-TRON__1_5_1_6566__resources.pkg` |
| Flanger BL-20 | `flanger-bl-20` | `Flanger_BL-20__1_5_1_6566__resources.pkg` |
| Chorus JUN-6 | `chorus-jun-6` | `Chorus_JUN-6__1_5_1_6566__resources.pkg` |
| Bus FORCE | `bus-force` | `Bus_FORCE__1_4_1_6566__resources.pkg` |
| Comp DIODE-609 | `comp-diode-609` | `Comp_DIODE-609__1_4_1_6566__resources.pkg` |
| EQ SITRAL-295 | `eq-sitral-295` | `EQ_SITRAL-295__1_4_1_6566__resources.pkg` |
| Tape MELLO-FI | `tape-mello-fi` | `Tape_MELLO-FI__1_4_1_6566__resources.pkg` |
| Efx FRAGMENTS | `efx-fragments` | `Efx_FRAGMENTS__1_3_1_6566__resources.pkg` |
| Dist TUBE-CULTURE | `dist-tube-culture` | `Dist_TUBE-CULTURE__1_2_1_6566__resources.pkg` |
| Dist OPAMP-21 | `dist-opamp-21` | `Dist_OPAMP-21__1_2_1_6566__resources.pkg` |
| Dist COLDFIRE | `dist-coldfire` | `Dist_COLDFIRE__1_2_1_6566__resources.pkg` |
| Filter MS-20 | `filter-ms-20` | `Filter_MS-20__1_2_1_6566__resources.pkg` |
| Efx MOTIONS | `efx-motions` | `Efx_MOTIONS__1_1_1_6566__resources.pkg` |
| Bus PEAK | `bus-peak` | `Bus_PEAK__1_0_1_6566__resources.pkg` |
| Rev LX-24 | `rev-lx-24` | `Rev_LX-24__1_2_1_6567__resources.pkg` |
| Rotary CLS-222 | `rotary-cls-222` | `Rotary_CLS-222__1_2_1_6566__resources.pkg` |
| Efx REFRACT | `efx-refract` | `Efx_REFRACT__1_1_1_6566__resources.pkg` |
| Bus EXCITER-104 | `bus-exciter-104` | `Bus_EXCITER-104__1_0_1_6566__resources.pkg` |
| Tape J-37 | `tape-j37` | `Tape_J-37__1_1_0_6566__resources.pkg` |
| Mix DRUMS | `mix-drums` | `Mix_DRUMS__1_0_1_6566__resources.pkg` |
| Pitch SHIFTER-910 | `pitch-shifter-910` | `Pitch_SHIFTER-910__1_0_0_6566__resources.pkg` |
| Bus TRANSIENT | `bus-transient` | `Bus_TRANSIENT__1_0_1_6566__resources.pkg` |
| Efx AMBIENT | `efx-ambient` | `Efx_AMBIENT__1_0_0_6577__resources.pkg` |
