# ssh-tunnel v0.3.0 · Ronde 5
Release ChatID MCP-R5-20261111-ACCEPT

One Python script, no third-party Python dependencies. Python 3.7+.

## Installation
Copy the skill folder to a folder supported by the current coding agent, or directly run `python scripts/lan_mcp_manager.py --help`. The skill invocation syntax differs between agent hosts.

## Spelen02 Windows setup
Run from a local PowerShell console on Spelen02:

```
python scripts/lan_mcp_manager.py ssh-server-setup
python scripts/lan_mcp_manager.py ssh-server-setup --apply
python scripts/lan_mcp_manager.py publish-check 3900/mcp --name voicestudio
python scripts/lan_mcp_manager.py publish-check 8791/mcp --name yue2
```

Windows will ask for UAC authorization when necessary. Firewall rule scope is set to Private / LocalSubnet. Beware: this may restrict prior external SSH access.

## On KodeklopperM4 client

```
python3 scripts/lan_mcp_manager.py ssh-client-setup
python3 scripts/lan_mcp_manager.py ssh-check spelen02_local
python3 scripts/lan_mcp_manager.py start spelen02_local
```

In another terminal:

```
python3 scripts/lan_mcp_manager.py tools-list http://127.0.0.1:13900/mcp/
python3 scripts/lan_mcp_manager.py acceptance spelen02_local
```

A client tunnel requires verified hostkeys and SSH credentials/authorized keys. If a check fails, run `ssh-check` and review the error. No remote tunnel can start merely by enabling the server.

## Acceptance status
In-container tests are not real LAN integration tests. Unit results are recorded in `ACCEPTATIE.md`. Do not mark remote SSH/MCP, client integration, or reboot persistence PASS until demonstrated on the actual computers.
