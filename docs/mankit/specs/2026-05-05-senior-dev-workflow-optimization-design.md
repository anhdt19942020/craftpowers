# Senior Dev Workflow Optimization — Design Spec

**Date:** 2026-05-05
**Scope:** Personal setup optimization for high-autonomy senior dev workflow
**Approach:** Trim & Accelerate — reduce friction, keep existing plugin intact

---

## 1. Problem Statement

Craftpowers plugin workflow is mature and covers the full dev lifecycle. However, the personal setup has friction points that slow down a senior dev who expects high autonomy:

- Permission prompts interrupt flow for routine commands
- `settings.local.json` accumulates ad-hoc rules from past sessions, creating noise
- Missing allow rules for common multi-language tooling (Python, Go, Rust, Docker)
- RTK (token optimizer) is configured but not hooked into shell for automatic usage

---

## 2. Changes

### 2.1 Expand Global Permission Allowlist

**File:** `~/.claude/settings.json` → `permissions.allow`

Add missing common commands grouped by category:

**Package managers (install/run):**
- `Bash(pnpm install*)`, `Bash(pnpm add*)`, `Bash(pnpm remove*)`
- `Bash(npm install*)`, `Bash(npm ci*)`, `Bash(npm uninstall*)`
- `Bash(yarn install*)`, `Bash(yarn add*)`
- `Bash(pip install*)`, `Bash(pip3 install*)`
- `Bash(pip list*)`, `Bash(pip show*)`, `Bash(pip3 list*)`, `Bash(pip3 show*)`

**Runtime execution:**
- `Bash(python *.py*)`, `Bash(python3 *.py*)`
- `Bash(python -c *)`, `Bash(python3 -c *)`
- `Bash(node *.js*)`, `Bash(node -e *)`
- `Bash(go run *)`, `Bash(go mod *)`
- `Bash(cargo run*)`
- `Bash(npx *)`

**Docker (read-only):**
- `Bash(docker ps*)`, `Bash(docker images*)`, `Bash(docker logs*)`
- `Bash(docker inspect*)`, `Bash(docker compose ps*)`
- `Bash(docker compose logs*)`

**Build & quality (missing ones):**
- `Bash(pnpm run *)`, `Bash(yarn run *)`
- `Bash(cargo fmt*)`, `Bash(cargo doc*)`
- `Bash(go fmt*)`, `Bash(golint*)`, `Bash(golangci-lint*)`
- `Bash(python -m pylint*)`, `Bash(python -m mypy*)`, `Bash(ruff *)`
- `Bash(prettier *)`, `Bash(biome *)`

**Utilities:**
- `Bash(type *)`, `Bash(whoami*)`, `Bash(hostname*)`
- `Bash(env)`, `Bash(printenv*)`
- `Bash(date*)`, `Bash(uname*)`
- `Bash(du *)`, `Bash(df *)`
- `Bash(tree *)`

**RTK wrappers:**
- `Bash(rtk cargo*)`, `Bash(rtk go*)`, `Bash(rtk pytest*)`
- `Bash(rtk docker*)`, `Bash(rtk pnpm*)`, `Bash(rtk npm*)`
- `Bash(rtk jest*)`, `Bash(rtk vitest*)`
- `Bash(rtk tsc*)`, `Bash(rtk lint*)`
- `Bash(rtk prettier*)`, `Bash(rtk curl*)`
- `Bash(rtk err*)`, `Bash(rtk log*)`, `Bash(rtk summary*)`

**PowerShell equivalents:**
- `PowerShell(git *)`, `PowerShell(node *)`, `PowerShell(npm *)`
- `PowerShell(pnpm *)`, `PowerShell(python *)`, `PowerShell(cargo *)`
- `PowerShell(go *)`, `PowerShell(docker *)`, `PowerShell(rtk *)`
- `PowerShell(Get-ChildItem *)`, `PowerShell(Get-Content *)`
- `PowerShell(Test-Path *)`, `PowerShell(Get-Process *)`

### 2.2 Clean Up settings.local.json

**File:** `~/.claude/settings.local.json`

**Current state:** 44 ad-hoc rules accumulated from past sessions, including:
- Project-specific paths (`scp /tmp/... root@180.93.1.160:...`)
- One-off tool installs (`pip install *`, `pipenv install *`)
- Hardcoded file paths (`python C:/temp/Speechat/...`)
- Session-specific commands (`unzip -o harvard.wav.zip`)

**Action:**
- **Promote to global:** `WebSearch`, `WebFetch(domain:github.com)`, `mcp__github__*`, `Bash(curl *)`, `Bash(git add *)`, `Bash(git commit *)`, `Bash(git push *)`
- **Remove:** All project-specific paths, one-off commands, and hardcoded paths
- **Keep in local only:** Nothing — all useful rules move to global

### 2.3 RTK Shell Hook

**Current state:** RTK is installed but not hooked into shell (`[rtk] /!\ No hook installed`).

**Action:** Run `rtk init -g` to add RTK instructions to global CLAUDE.md (already done) and install shell hook for automatic token savings tracking.

---

## 3. Out of Scope

- Adding new skills or hooks to craftpowers plugin (upstream, not ours to modify)
- MCP server setup (separate task, depends on specific project needs)
- Auto-test hooks (useful but project-specific, not global config)
- Cost tracking dashboard (nice-to-have, separate initiative)

---

## 4. Implementation Order

1. Expand `~/.claude/settings.json` permissions
2. Promote useful rules from `settings.local.json` to global
3. Clean `settings.local.json` to empty or near-empty
4. Install RTK shell hook
5. Verify with `/man-check`

---

## 5. Risk Assessment

- **Low risk:** All changes are to personal config files, fully reversible
- **No upstream impact:** Nothing in craftpowers repo is modified
- **Rollback:** `git` not involved — settings files can be manually restored
