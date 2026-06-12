# User Permissions Sync — Design Spec

**Date:** 2026-05-05
**Scope:** Add user-permissions.json support to install.py for syncing personal Claude Code settings across machines
**Backward-compatible:** Yes — no file means no change in behavior

---

## 1. Problem Statement

Craftpowers' `install.py` sets up hooks, agents, skills, and a base set of permissions (`SAFE_PERMISSIONS`). However, senior devs accumulate additional permissions, env vars, and other personal config that must be manually replicated across machines. There is no mechanism to define personal settings once and have them applied automatically on every machine via `/man-update`.

---

## 2. Solution

### 2.1 User Permissions File

A new optional file `~/.claude/user-permissions.json` stores personal settings that `install.py` merges into `settings.json` during setup.

**Format:**

```json
{
  "_source": "https://gist.githubusercontent.com/<user>/<id>/raw/user-permissions.json",
  "permissions": [
    "WebSearch",
    "WebFetch(domain:github.com)",
    "Bash(git add *)",
    "Bash(git commit *)",
    "Bash(git push *)",
    "Bash(npm install*)",
    "Bash(npm run *)",
    "Bash(npx *)",
    "Bash(pnpm install*)",
    "Bash(pnpm run *)",
    "Bash(pnpm add*)",
    "Bash(pnpm remove*)",
    "Bash(yarn install*)",
    "Bash(yarn run *)",
    "Bash(yarn add*)",
    "Bash(pip install*)",
    "Bash(pip3 install*)",
    "Bash(pip list*)",
    "Bash(pip show*)",
    "Bash(pip --version*)",
    "Bash(prettier *)",
    "Bash(biome *)",
    "Bash(cargo run*)",
    "Bash(cargo fmt*)",
    "Bash(cargo doc*)",
    "Bash(go run *)",
    "Bash(go mod *)",
    "Bash(go fmt*)",
    "Bash(golint*)",
    "Bash(golangci-lint*)",
    "Bash(python *.py*)",
    "Bash(python3 *.py*)",
    "Bash(python -c *)",
    "Bash(python3 -c *)",
    "Bash(python -m pylint*)",
    "Bash(python -m mypy*)",
    "Bash(ruff *)",
    "Bash(node *.js*)",
    "Bash(node -e *)",
    "Bash(docker ps*)",
    "Bash(docker images*)",
    "Bash(docker logs*)",
    "Bash(docker inspect*)",
    "Bash(docker compose ps*)",
    "Bash(docker compose logs*)",
    "Bash(type *)",
    "Bash(whoami*)",
    "Bash(hostname*)",
    "Bash(env)",
    "Bash(printenv*)",
    "Bash(date*)",
    "Bash(uname*)",
    "Bash(du *)",
    "Bash(df *)",
    "Bash(tree *)",
    "Bash(curl *)",
    "Bash(gh *)",
    "Bash(rtk cargo*)",
    "Bash(rtk go*)",
    "Bash(rtk pytest*)",
    "Bash(rtk docker*)",
    "Bash(rtk pnpm*)",
    "Bash(rtk npm*)",
    "Bash(rtk jest*)",
    "Bash(rtk vitest*)",
    "Bash(rtk tsc*)",
    "Bash(rtk lint*)",
    "Bash(rtk prettier*)",
    "Bash(rtk curl*)",
    "Bash(rtk err*)",
    "Bash(rtk log*)",
    "Bash(rtk summary*)",
    "Bash(rtk gh*)",
    "PowerShell(git *)",
    "PowerShell(node *)",
    "PowerShell(npm *)",
    "PowerShell(pnpm *)",
    "PowerShell(python *)",
    "PowerShell(cargo *)",
    "PowerShell(go *)",
    "PowerShell(docker *)",
    "PowerShell(rtk *)",
    "PowerShell(Get-ChildItem *)",
    "PowerShell(Get-Content *)",
    "PowerShell(Test-Path *)",
    "PowerShell(Get-Process *)",
    "PowerShell(gh *)",
    "mcp__github__search_repositories",
    "mcp__github__get_file_contents"
  ],
  "env": {
    "CLAUDE_CODE_DISABLE_1M_CONTEXT": "1",
    "CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING": "1",
    "CLAUDE_CODE_NO_FLICKER": "1"
  }
}
```

**Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `_source` | No | URL to fetch latest version from. If present, `install.py` fetches before merging. If absent, only local file is used. |
| `permissions` | No | Array of permission rules to merge into `settings.json` `permissions.allow`. Merged idempotently (no duplicates). |
| `env` | No | Object of env vars to merge into `settings.json` `env`. User values overwrite existing keys. |

### 2.2 Changes to install.py

Add `setup_user_permissions(settings_path)` function, called after `setup_permissions()` in `main()`.

**Logic:**

```
user_config_path = ~/.claude/user-permissions.json

1. If file does not exist → log "[SKIP] No user-permissions.json found" → return
2. Read file as JSON
3. If "_source" field exists:
   a. Try HTTP GET to _source URL (timeout 10s)
   b. If success → parse JSON → overwrite local file with fetched content
   c. If fail → log "[WARN] Could not fetch user-permissions, using cached version"
   d. Re-read file (may have been updated)
4. If "permissions" array exists → merge into settings.permissions.allow (skip duplicates)
5. If "env" object exists → merge into settings.env (overwrite existing keys)
6. Write settings.json
7. Log "[OK] User permissions: added N rules, M env vars"
```

### 2.3 --sync Flag

Add optional `--sync <url>` argument to `install.py`.

**Behavior:**

```
python scripts/install.py --sync <url>
```

1. Fetch JSON from URL (timeout 10s, fail if error)
2. Add `"_source": "<url>"` field to the fetched JSON
3. Write to `~/.claude/user-permissions.json`
4. Continue with normal install flow (which will now pick up the new file)

This is a one-time bootstrap for new machines. After this, `/man-update` auto-syncs via `_source`.

### 2.4 Changes to verify.py

Add one check:

```
[PASS] user-permissions.json found (N permissions, M env vars, source: <url|local-only>)
[SKIP] user-permissions.json not found (optional)
```

Not a failure — just informational.

---

## 3. Flow Diagrams

### First machine (current):

```
1. Create user-permissions.json with all personal permissions + env
2. Upload to GitHub Gist (get raw URL)
3. Add "_source" field pointing to gist URL
4. Run /man-update → install.py merges into settings.json
```

### New machine:

```
1. Install craftpowers (plugin install or clone)
2. Run: python scripts/install.py --sync <gist-url>
3. Done — permissions + env applied
4. Future /man-update calls auto-fetch latest from gist
```

### Updating permissions:

```
1. Edit gist on GitHub (add/remove permissions)
2. Run /man-update on any machine → fetches latest, merges
```

---

## 4. Out of Scope

- Syncing hooks config (already handled by install.py based on craftpowers_root)
- Syncing model preference (machine-specific, may vary)
- Syncing plugins list (plugin system handles this)
- Syncing settings.local.json (should remain empty per our earlier optimization)
- Two-way sync (user-permissions.json is source of truth, not settings.json)

---

## 5. Risk Assessment

- **Low risk:** Additive change, backward-compatible. No file = no change.
- **Network failure safe:** Falls back to cached local file.
- **No secrets:** Permission rules and env vars are not sensitive data.
- **Idempotent:** Safe to run multiple times.
- **Upstream-friendly:** General-purpose feature, not personal config. Could be accepted as PR.
