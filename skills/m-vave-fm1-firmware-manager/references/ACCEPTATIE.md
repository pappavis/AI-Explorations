# Acceptatiecontract — v1.5.0
Version: 1.5.0 | Release ChatID: B6D9A420

## Gebruiker
- "FM-1 Firmware Manager update" betekent alleen ontbrekende of gewijzigde VIBE FM-conversies downloaden en installeren.
- "Update alles" betekent alle ontdekte VIBE FM-conversies opnieuw downloaden.
- "Status" verandert geen firmwarebestanden.
- Geen handmatige firmware-ID's, download-URL's, doelmappen of ZIP-verwerking vragen.
- Terminal én GUI tonen naam, websiteversie, lokale versie, URL, bestand, omvang, validatie, voortgang en eindresultaat.
- De gebruiker kan de VIBE FM-plugin daarna openen en de bibliotheek gebruiken. **Daadwerkelijk laden in de plugin is geen geautomatiseerde acceptatietest.**

## Veiligheid
- Geen fysieke FM-1/SMK-37 hardware benaderen of flashen.
- Geen installatie vóór alle geselecteerde ZIP's zijn gevalideerd.
- Geen installatie als de FM-1-catalogus niet betrouwbaar kan worden opgehaald.
- Geen verwijdering van andere firmwarebestanden.
- Rollback van aangeraakte bestanden bij installatiefout.
- Debuglog wordt per run vervangen; fouten blijven erin leesbaar.

## Technische review (huidige status)
- Kernfuncties voor discovery/download/validatie/installatie uit v1.4.2 behouden.
- Nieuwe ProgressView en FirmwareGUI zijn class-based.
- **Openstaand:** bestaande fm1_update.py is nog niet volledig class-based en bevat moduleconstanten; geen cosmetische claim dat dit klaar is.
- **Openstaand:** de site is niet live bereikbaar via de bouwcontainer (DNS-fout), dus echte download/integratie met plugin niet bewezen.
- **Openstaand:** grafische vensterwerking niet op echte macOS/Windows desktop getest.
- **Openstaand:** SMK-37-versieparser kan namen en versies nog samenvoegen.

## Verificatie
- Unit- en mock-integratietests controleren selectie, veilige ZIP, manifest, opnieuw uitvoeren zonder dubbel downloaden, geen wijziging bij corrupte ZIP en voortgangsoutput.
- Handmatige eindacceptatie op Mac: `./scripts/run.sh refresh`, open VIBE FM in Logic Pro, controleer dat firmware zichtbaar en laadbaar is.
