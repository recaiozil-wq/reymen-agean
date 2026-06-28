---
skill_id: e13229abfaf6
usage_count: 1
last_used: 2026-06-16
---
## Step 1: Determine Execution Environment

**Mandatory: Ask the user for the Kali SSH password before any connection.**
Wait for their response. Do not proceed without it. This is a security requirement.

Check the user's message for other connection details. If not provided, ask the user.

| Available | Mode | Command pattern |
|-----------|------|-----------------|
| Kali is the local system | **Local** (direct) | `{command}` (no wrapper needed) |
| SSH credentials | **SSH** (preferred for remote) | `ssh {CONNECT_CMD} "{command}"` |
| Running container | **Docker exec** | `docker exec {CONTAINER} {command}` |
| Docker only | **Docker persistent container** | Create or start `kali-pentest`, then run `docker exec kali-pentest {command}` |

**Environment initialization:**
- New task: `mkdir -p /tmp/kali-pentest-state/<target>/` on the Agent's host. Read `references/environment/state-files.md` for naming rules and file formats.
- Continuing task: re-read existing state files to recover progress.
- Before starting any testing, update Kali tools: `apt-get update && apt-get upgrade -y`.

### Capability Check

Use the environment that matches the task:

| Requirement | Preferred environment | Rule |
|-------------|----------------------|------|
| Full assessment, internal LAN, raw sockets, service daemons, database-backed tools | SSH to a full Kali VM/server | Prefer SSH when available |
| CLI-only reconnaissance, web testing, basic scanning, reporting | Persistent Docker container | Acceptable if tools and network reachability are verified |
| Wireless monitor mode, USB adapters, hardware-dependent tests | Physical/VM Kali over SSH | Do not use Docker |
| GPU password cracking | Full Kali with GPU access | Verify `hashcat -I` before planning GPU work |
| GVM/OpenVAS, Neo4j/BloodHound, ZAP daemon, Metasploit database | Full Kali preferred | Docker is acceptable only if the service stack is already configured |

If the selected task requires unsupported capabilities, stop and explain the limitation instead of forcing the tool to run.

Before heavy work, run the readiness checks for the selected environment:

- Local mode: `references/environment/local-mode.md`
- Full Kali/server mode: `references/environment/server-mode.md`
- Docker mode: `references/environment/docker-mode.md`

Missing optional tools are not an environment failure. Install the required package after selecting the playbook, or choose an alternative from the category README.

### SSH Patterns

```bash
ssh {CONNECT_CMD} "whoami && uname -a" # verify connection
ssh {CONNECT_CMD} "nohup {cmd} </dev/null > /tmp/{task}.log 2>&1 & echo \$!" # background task
scp {USER}@{HOST}:/tmp/{output_file} /tmp/ # retrieve results
```

### Docker Mode

Use Docker only as a persistent Kali execution environment. Do not use one-shot temporary containers for assessments.

Read `references/environment/docker-mode.md` first. Read `references/environment/docker-mode-persistent-container.md` only when creating, starting, or installing tools into the container. Read `references/environment/docker-mode-networking.md` only for raw-socket behavior, Docker Desktop limitations, or reachability/routing problems.