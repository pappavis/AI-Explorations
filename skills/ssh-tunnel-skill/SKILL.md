---
name: ssh-tunnel
description: Automatically discover and safely prepare SSH transport for MCP endpoints on a LAN. Check/install/enable OS-native SSH tools on the local host, connect clients, validate tools/list, and optionally use local Ollama for diagnostics.
---

# SSH Tunnel — MCP Service Publisher and Connector

Version 0.3.0 · Ronde 5 · Release ChatID MCP-R5-20261111-ACCEPT

## Contract

Act as a friendly system administrator for a novice user. Do not require the user to understand networking. The Python engine is the **single** file `scripts/lan_mcp_manager.py`. No second Python runtime or global application state. Commands must execute on the appropriate computer; a client cannot configure a server machine unless the agent has approved remote access.

The user authorizes an automatic *local* SSH setup workflow. The engine's `--apply` is its explicit authorization boundary; the agent may invoke it after checking the plan in contexts where that authorization is present. Never bypass OS permission checks: Windows UAC and macOS/Linux administrator permissions may prompt. If OS permissions or remote login configuration requires user action, give one short natural-language instruction, not a command dump. Never silently obtain credentials, disable host-key checking, or expose SSH/MCP to the public internet. Use system-native GUI Computer Use when available for OS dialogs, otherwise follow the CLI plan. Avoid repeated confirmations for harmless discovery steps.

## First action: discover

- `python scripts/lan_mcp_manager.py inventory`
- `python scripts/lan_mcp_manager.py deploy-inventory`
- `python scripts/lan_mcp_manager.py ssh-server-setup` — shows plan, no writes.
- `python scripts/lan_mcp_manager.py ssh-client-setup` — shows plan, no writes.

The presence of the sshd binary is not proof of an active SSH service; on Windows, an absent PATH entry does not prove the optional Windows component is absent. The remote host returns "Connection refused" when the port is not accepting a connection. Investigate on the **destination** machine.

## Automatic local SSH prerequisite repair

On the computer where the MCP server runs, invoke:

`python scripts/lan_mcp_manager.py ssh-server-setup --apply`

- Windows: use built-in Windows OpenSSH.Server feature; enable/start sshd; scope the Windows built-in inbound firewall rule to Private and LocalSubnet. UAC elevation may be shown; cannot be bypassed. Changing the firewall rule may restrict previously wider SSH access. No public MCP port opened.
- macOS: use built-in Remote Login; requires admin approval / relevant macOS privacy permission. Restrict allowed users in System Settings if necessary.
- Linux: use distro package manager (apt/dnf/pacman), systemctl to enable/start. Firewall remains unchanged; report that as a possible BLOCKED dependency.

On the client machine, invoke:

`python scripts/lan_mcp_manager.py ssh-client-setup --apply`

This action is idempotent and skips installation when the ssh client is found. Never install third-party SSH software on macOS automatically.

**After enabling SSH:** The agent still needs a verified host fingerprint, an account on the target machine, and working SSH authorization. Setting up SSH keys must never be performed by disabling host-key verification. If the connection does not authenticate, report what is missing rather than guessing a password.

## Command intents

`@ssh-tunnel add 3900/mcp` or `$ssh-tunnel add 3900/mcp`: register a local address; use `publish-check 3900/mcp --name voicestudio` to validate MCP initialize. Publishing metadata is NOT exposing an HTTP port.

`@ssh-tunnel add http://localhost:3900/mcp`: same workflow.

`@ssh-tunnel add http://xyz-abc:1234`: register metadata but do not claim it is a local MCP or expose it without checking.

`@ssh-tunnel connect spelen02 voicestudio`: on the **client** host use e.g.

`python scripts/lan_mcp_manager.py connect spelen02.local voicestudioSpelen02 --user pappa --address 3900/mcp/`

Add YuE2 as another endpoint of the same profile:

`python scripts/lan_mcp_manager.py connect spelen02.local yue2Spelen02 --user pappa --address 8791/mcp`

Check SSH: `python scripts/lan_mcp_manager.py ssh-check spelen02_local`

Start client-side tunnel in its own terminal/service: `python scripts/lan_mcp_manager.py start spelen02_local`

Test real tools: `python scripts/lan_mcp_manager.py tools-list http://127.0.0.1:13900/mcp/`

`python scripts/lan_mcp_manager.py client-plan spelen02_local --client codex`

`python scripts/lan_mcp_manager.py client-apply spelen02_local --apply` (Codex only; modifies Codex configuration)

For OpenCode use `client-plan ... --client opencode`, merge rather than overwrite existing config.

The exact `$skill` / `@skill` trigger depends on the agent host, not on SSH itself.

## Local Ollama

Prefer locally installed Gemma 4, then another Gemma, then another local Ollama model. No model is downloaded automatically. Without Ollama, continue with deterministic Python logic. Never execute LLM-produced shell commands.

## Persistence and acceptance

`deploy-plan PROFILE` generates service configuration. On macOS, `deploy-install PROFILE --apply` installs a LaunchAgent file without starting it. Move the Python script to a permanent location first. Windows/Linux autostart remains manual until separately validated.

`acceptance PROFILE` checks SSH and MCP tools/list through a running tunnel. The overall report remains `accepted: false` until actual Codex/OpenCode invocation and reboot persistence are independently checked; absent evidence = BLOCKED, not PASS. Do not claim end-to-end success based on unit tests.

`test` runs all built-in standard-library tests; Windows Python 3.7 is supported.

## Sources

- Microsoft Windows OpenSSH: https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse
- Apple Remote Login: https://support.apple.com/en-mt/guide/mac-help/mchlp1066/27/mac/27
- MCP: https://modelcontextprotocol.io/specification/
- OpenCode MCP: https://opencode.ai/docs/mcp-servers
