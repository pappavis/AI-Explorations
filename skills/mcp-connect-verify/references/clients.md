# Clientadapters

Gecontroleerd op 17 november 2026. Controleer lokale versies/CLI-help en effectieve config; projectinstellingen kunnen globale entries overschrijven. Druk geen complete configuraties met credentials af.

| Client | Globale MCP-config | Streamable HTTP | Globale skilllocatie |
|---|---|---|---|
| Codex | `$CODEX_HOME/config.toml`, standaard `~/.codex/config.toml` | `[mcp_servers.NAME]`, `url`, `enabled = true` | `~/.agents/skills/`; controleer geladen catalogus |
| Antigravity | `~/.gemini/config/mcp_config.json`; oudere IDE-installaties kunnen `~/.gemini/antigravity/mcp_config.json` gebruiken | `mcpServers.NAME.serverUrl` | `~/.gemini/config/skills/`; oudere IDE-versies kunnen `~/.gemini/antigravity/skills/` gebruiken |
| OpenCode v1 | `$XDG_CONFIG_HOME/opencode/opencode.json[c]`, standaard `~/.config/opencode/opencode.json[c]` | `mcp.NAME = {type: "remote", url: "…", enabled: true}` | `~/.agents/skills/` of `~/.config/opencode/skills/` |
| OpenCode v2 | dezelfde locatie | `mcp.servers.NAME = {type: "remote", url: "…", disabled: false}` | dezelfde locaties; controleer exacte versie |

De helper kiest een bestaand bekend bestand. Wanneer meerdere configuratiebestanden bestaan of de client elders beheerd wordt, bepaal de effectieve locatie en gebruik `--config`. JSONC en JSON met comments worden niet door de helper herschreven: maak een backup en gebruik een gerichte edit. `check-config` controleert syntax, niet het client-schema of de geladen tools.

## Native verificatie en auth

- Codex: `codex mcp --help`, `codex mcp get NAME`, `codex mcp list`, `codex mcp login NAME` waar ondersteund. `codex mcp add NAME --url URL` is een alternatief voor de adapter; ook dan eerst een backup. Bearer-tokenconfig gebruikt `bearer_token_env_var`. Na wijziging moet een bestaande sessie mogelijk herladen/herstarten. Gebruik de MCP-toolcatalogus en een echte aanroep voor runtimebewijs.
- Antigravity: controleer of CLI `agy`, oudere CLI of GUI aanwezig is. Gebruik Customizations/MCP Servers voor status, authenticatie en herladen. Huidige remote configuratie ondersteunt Streamable HTTP; legacy SSE en `httpUrl` zijn niet ondersteund. Gebruik OAuth of gedocumenteerde credentialinvoer; neem niet aan dat willekeurige `${VAR}`-syntax wordt uitgebreid. Workspaceconfig: `.agents/mcp_config.json`.
- OpenCode: controleer `opencode --version` en `opencode mcp --help`. V2 heeft `opencode mcp add NAME --global --url URL`, `opencode mcp list` en `opencode mcp auth NAME`; oudere versies kunnen andere opdrachten hebben. Voor bearer-auth: `headers.Authorization = "Bearer {env:VARIABLE}"`, `oauth = false`. Laat OAuth standaard actief bij OAuth-servers. `/mcps` kan in de client status en login bieden.
- Skillbeschikbaarheid: een directory/hashcontrole bewijst installatie; alleen de clientcatalogus of expliciete skill-invocation bewijst dat de client hem ontdekt heeft. Maak geen nieuwe MCP-config wanneer de server al door een plugin wordt beheerd zonder die bron te inspecteren.

## Netwerk en geheimen

`127.0.0.1` verwijst naar de machine waarop de client/probe draait. Bij een andere computer, container of sandbox is dezelfde URL niet noodzakelijk bereikbaar. Gebruik bestaande SSH-tunnels waar passend, maar publiceer geen lokale poort om een verbindingstest te laten slagen.

De probe doet geen OAuth-login. Een 401 tijdens de directe probe kan naast een geslaagde client-OAuth-sessie bestaan. Gebruik geen `--call` tijdens endpoint-discovery: bepaal eerst het juiste endpoint, voer daarna de geautoriseerde read-only aanroep precies één keer uit. Timeout tijdens een toolcall geeft een onbekende uitvoeringsstatus; herhaal geen muterende aanroep automatisch.

## Officiële bronnen

- https://developers.openai.com/codex/mcp
- https://developers.openai.com/codex/skills
- https://antigravity.google/docs/mcp
- https://antigravity.google/docs/skills
- https://opencode.ai/docs/mcp-servers
- https://opencode.ai/docs/skills
- https://github.com/modelcontextprotocol/python-sdk
