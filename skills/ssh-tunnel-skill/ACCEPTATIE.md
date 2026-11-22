# Ronde 5 acceptatie — bewijsstatus

Release ChatID MCP-R5-20261111-ACCEPT

| Check | Resultaat | Bewijs |
|---|---|---|
| Python syntaxis | PASS | py_compile in sandbox |
| 55 ingebouwde regressietests | PASS | Python unittest in sandbox |
| Windows Spelen02: VoiceStudio MCP initialize | PASS (R2 door gebruiker) | Transcript: 200 + protocol 2025-03-26 |
| Windows Spelen02: YuE2 MCP initialize | PASS (R2 door gebruiker) | Transcript: 200 + protocol 2025-03-26 |
| KodeklopperM4: R3 tests | PASS (door gebruiker) | 37 tests |
| Windows Spelen02: R3 tests | FAIL (vorige versie) | 1 error + 1 failure, verbeterd in R4 maar nog niet opnieuw aangetoond |
| Windows OpenSSH-server draait | BLOCKED | Laatste client SSH-test: Connection refused |
| LAN SSH hostkey en auth | BLOCKED | Nog geen succesvolle sessie |
| Live SSH-tunnel op KodeklopperM4 | BLOCKED | Geen bewijs |
| MCP tools/list over tunnel | BLOCKED | Geen bewijs |
| Codex/OpenCode echte tool-aanroep | BLOCKED | Geen bewijs |
| Herstart / autostart | BLOCKED | Geen bewijs |
| Externe onafhankelijke review | BLOCKED | Niet uitgevoerd |

**Eindoordeel: CONDITIONAL / NOT YET ACCEPTED.** Nieuwe OS-setup is geautomatiseerd waar ondersteund, met expliciete --apply en UAC/sudo. Geen claims over handelingen op de echte computers.
