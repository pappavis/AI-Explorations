---
name: mcp-connect-verify
description: Voeg MCP-servers toe aan Codex, Antigravity en OpenCode en controleer configuratie, protocol, authenticatie en daadwerkelijk toolgebruik. Gebruik voor MCP-installatie, verbindingstests en herstel van clientregistraties.
---

# MCP Connect & Verify

Voer het toevoegen en verifiëren van een MCP-server uit met zo weinig mogelijk vragen. Gebruik elke opgegeven HTTP(S)-URL; `http://127.0.0.1:3900/` is alleen een voorbeeld. Installeer geen serverapplicatie uitsluitend omdat een URL is opgegeven.

## Werkwijze

1. Leid servernaam, URL, gewenste clients en scope af uit de opdracht en bestaande context. Bij “mijn clients” configureer aanwezige clients, standaard globaal. Vraag alleen om ontbrekende noodzakelijke gegevens zoals de URL of een onvermijdelijke login. Wijzig geen niet-gevraagde clients.
2. Gebruik `scripts/bootstrap.sh doctor` op macOS/Linux of `scripts/bootstrap.ps1 doctor` op Windows (vanuit de skillmap). Deze scripts gebruiken Python >=3.11 en een eigen cache-venv. Bij ontbrekende Python installeren ze via aanwezige uv/Homebrew/winget zonder extra inhoudelijke vragen. Bij ontbrekende pakketbeheerder: inventariseer de officiële OS-installatiemethode en voer de benodigde installatie uit binnen de opdracht; vraag alleen om onvermijdelijke systeemtoestemming. Installeer geen pakketbeheerder of gebruik geen sudo zonder noodzaak. Een sandboxweigering vereist de normale escalatie, geen omweg.
3. Inventariseer clientversies en effectieve configlocaties, inclusief projectoverrides. Lees bij configuratie of authenticatie [references/clients.md](references/clients.md). Een gevonden config bewijst niet dat de client is geïnstalleerd; een GUI-app kan wel bestaan zonder CLI.
4. Controleer het endpoint:
   ```bash
   scripts/bootstrap.sh probe --url 'http://127.0.0.1:3900/' --discover
   ```
   De SDK doet protocolonderhandeling, initialisatie en gepagineerde inventarisatie van aangekondigde tools/resources/prompts. `--discover` probeert alleen bij een basis-URL ook `/mcp` en `/mcp/`. Gebruik het endpoint dat daadwerkelijk slaagt. Bij legacy SSE expliciet `--transport sse`; verifieer of de client dat transport ondersteunt. De HTTP-configadapter hieronder is voor Streamable HTTP. Een SSE-probe bewijst geen compatibele clientconfiguratie.
5. Bij auth-fouten: gebruik de eigen OAuth-flow van de client of reeds beschikbare omgevingsvariabelen. `probe --token-env VARIABLE` leest een bearer token zonder de waarde af te drukken. Vraag geen geheimen in de chat. De directe probe hergebruikt geen client-OAuth-tokens; als alleen client-auth beschikbaar is, verifieer via de client en rapporteer dat de onafhankelijke probe niet is voltooid.
6. Maak eerst het configuratieplan en pas het vervolgens toe binnen de opdracht, zonder aanvullende bevestiging:
   ```bash
   scripts/bootstrap.sh configure --client codex --name voorbeeld --url 'http://127.0.0.1:3900/mcp'
   scripts/bootstrap.sh configure --client codex --name voorbeeld --url 'http://127.0.0.1:3900/mcp' --apply
   ```
   Herhaal alleen voor gevraagde/aanwezige clients. Beschikbaar: `codex`, `antigravity`, `opencode`. `--config PAD` kiest een vastgestelde afwijkende locatie. OpenCode gebruikt de geïnstalleerde versie; bij onduidelijke detectie bepaal zelf het schema uit de lokale CLI/documentatie en geef `--opencode-schema v1|v2`. `--token-env` schrijft alleen een variabelereferentie voor Codex/OpenCode. Antigravity-auth verloopt via de client.
7. Bestaande afwijkende registratie: inspecteer alleen relevante velden en behoud aanvullende instellingen. Gebruik `--replace` alleen als volledige vervanging van juist die registratie de opdracht is; het vervangt het hele serverobject. De helper maakt een backup en schrijft atomair. JSONC/commenthoudende JSON, symlinks of afwijkende schemas: maak zelf eerst een backup, pas gericht aan met behoud van comments en valideer met `check-config --client CLIENT --config PAD`. De helper weigert wijzigingen die comments zouden wissen. Bij tijdelijke onbereikbaarheid mag de aangevraagde registratie worden opgeslagen, maar rapporteer verificatie als mislukt/openstaand.
8. Controleer de echte client: lees de registratie terug met de beschikbare CLI/UI, controleer projectoverrides, herlaad waar mogelijk en zoek de tools. Voer één passende, onschadelijke read-only tool uit als de opdracht dit toestaat. `probe --call TOOL --arguments '{}'` test de server rechtstreeks; dit bewijst nog geen gebruik vanuit Codex/Antigravity/OpenCode. Kies geen willekeurige tool op basis van alleen zijn naam. Bij ontbrekende veilige tool is een toolaanroep niet van toepassing. Herstart geen app met onopgeslagen werk; meld de benodigde herstart als dat niet autonoom kan.

## Skill vindbaar maken

Deze skill staat standaard in `~/.agents/skills/mcp-connect-verify`. Een skill installeren en een MCP-server registreren zijn twee aparte handelingen. Alleen `SKILL.md` maakt geen MCP-tools beschikbaar. Controleer de skillcatalogus van de huidige client. Als de gebruiker ook andere clients vraagt deze skill te zien: installeer dezelfde skillmap op hun ondersteunde locatie uit de referentie, met behoud van bestaande afwijkende kopieën. Wijzig geen andere skillroots op basis van deze skill alleen. Onbekende agents krijgen pas een adapter na controle van hun gedocumenteerde formaat; gok niet wat een clientnaam betekent.

## Rapportage

Rapporteer per client afzonderlijk: skill ontdekt, config opgeslagen, MCP-handshake, authenticatie geaccepteerd, tools geïnventariseerd, tools in client geladen, toolaanroep vanuit client. Gebruik **geslaagd**, **mislukt**, **niet gecontroleerd**, **niet van toepassing** of **herstart nodig**, met concreet bewijs. Een HTTP 200, geldige JSON/TOML, lege toolcatalogus of opgeslagen registratie is geen end-to-end succes. Een lege catalogus kan geldig zijn bij een resources-only server.

Geef bij problemen het beperkte volgende herstelpunt: proces/poort, endpoint/transport, auth, clientconfig of herladen. Bewaar geen tokens of toolinhoud in rapporten. Herhaal geen mislukte installatie onbeperkt; los de concrete oorzaak op of meld de blokkade.

## Onderhoud en tests

`scripts/test_manager.py` test configuraties in een tijdelijk home en een lokale MCP-testserver. Voer uit met de door bootstrap gemaakte venv-Python; verander echte clientconfiguraties niet tijdens tests. Hercontroleer veranderlijke clientformaten tegen de officiële documentatie voordat je onbekende versies configureert.
