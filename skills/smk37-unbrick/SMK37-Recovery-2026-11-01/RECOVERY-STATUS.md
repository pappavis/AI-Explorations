# SMK-37 Pro Recovery Dossier & Overdracht

**Datum:** 2026-11-01  
**Doelapparaat:** M-VAVE SMK-37 Pro (Unit ID: `4150354433333615`)  
**Status:** Fysieke hardware-blokkade (USB-laag niet responsief, scherm zwart). Softwarepogingen gestaakt conform de skill.

---

## 1. Wat daadwerkelijk is uitgevoerd en geverifieerd

1. **Detectie & Uitlezing:**
   - Apparaat werd initieel via USB MIDI gedetecteerd als `Felucca`.
   - Geschakeld naar downloadmodus (`WL82 UBOOT1.00`).
   - M-Flasher 0.7.0 loader (1.2) identificeerde de eenheid:
     - **Model:** SMK-37 Pro / Elite
     - **Bootloader:** stock (M-VAVE)
     - **Flash chip:** 0x856014 (1 MiB)
     - **Chip key:** 0x980F
     - **Unit ID:** 4150354433333615

2. **Volledige flash-rugsteun (veiliggesteld):**
   - Twee opeenvolgende, onafhankelijke 1 MiB flash-dumps gemaakt met 100% chip-CRC32 verificatie:
     - `smk37-20261101-225139.bin`
     - `smk37-20261101-225152.bin`
   - **Grootte:** exact 1.048.576 bytes (1 MiB).
   - **SHA-256:** `2b01d2e8bf84a43992ae6636cf7c540b1f66ca0914700a53b2d732374f980cc4`
   - *Deze dump bevat de unieke fabriekskalibratie en hardware-instellingen.*

3. **Schrijfstatus:**
   - **Er is GEEN firmware geschreven.** De chipflash is niet gewijzigd.
   - Na de downloadmodus-sessie reageerde het apparaat niet meer op de softwarematige herstart en verschijnt het niet meer op de USB-bus (`ioreg` toont geen entry).
   - Knoppencombinaties (`OCTAVE −` / `OCTAVE +`) en heraansluiten wekken geen USB-enumeratie meer op. Scherm blijft leeg.

---

## 2. Herstelpakket & Bestanden

Map: `/Users/michiele/Downloads/SMK37-Recovery-2026-11-01/`

- `smk37-20261101-225139.bin` & `smk37-20261101-225152.bin`: Volledige 1 MiB veilige back-ups.
- `SMK-37_Pro_016.fwsc`: Officiële Pro V016 firmware van fabrikant (SHA-256: `2d98ce72530e71d617384963423820536f094501299e2cfec0a8d3c3fb6bcfb0`).
- `M-Flasher.app` (v0.7.0).

---

## 3. Conclusie en Noodzakelijke Vervolgstap

Omdat de USB-controller in de microcontroller (JieLi) niet meer opstart in softwarematige bootloader/MIDI-modus en het scherm leeg blijft, kan software op de Mac dit op afstand niet meer aansturen.

**Vervolgstap:**
Fysieke **USB_KEY / Raspberry Pi Pico ROM-recovery** via de hardware-testpunten/USB-key van de JieLi-chip (zoals gedocumenteerd in de [m-bootloader specificatie](https://github.com/jvitkauskas/m-bootloader/blob/main/docs/SPEC.md)). Hierbij kan met de opgeslagen flash-rugsteun (`smk37-20261101-225139.bin`) de fabriekskalibratie behouden blijven.
