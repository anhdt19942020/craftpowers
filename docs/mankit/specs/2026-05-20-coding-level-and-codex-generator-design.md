# Design: coding-level skill + /man-generate-codex command

**Date:** 2026-05-20
**Status:** Approved
**Scope:** 2 independent features

---

## Feature A: coding-level skill

### Purpose
Allow users to set response detail level (0-5). Agents adjust explanation depth based on level.

### Levels

| Level | Name | Behavior |
|-------|------|----------|
| 0 | ELI5 | Explain like I'm 5. Analogies, no jargon |
| 1 | Beginner | Step-by-step, define terms |
| 2 | Intermediate | Standard explanations, some assumed knowledge |
| 3 | Advanced | Concise, assumes strong fundamentals |
| 4 | Expert | Terse, domain shorthand OK |
| 5 | God Mode | Minimal prose, code-only answers, fragments |

### Files

| File | Purpose |
|------|---------|
| `skills/coding-level/SKILL.md` | Skill definition with frontmatter |
| `commands/man-level.md` | Slash command `/man-level <0-5>` |

### Behavior
- `/man-level 3` → skill injects level context into session
- Default: no level set (normal behavior)
- Level persists for session duration
- No config file needed — level passed as argument

---

## Feature B: /man-generate-codex command

### Purpose
Generate mankit agents + skills into Codex CLI global format so all mankit capabilities are available in Codex.

### Source → Target Mapping

| Source (mankit) | Target (Codex global) | Transform |
|----------------|----------------------|-----------|
| `agents/*.md` + `agents/roles.json` | `~/.codex/AGENTS.md` | Merge all agent definitions into single markdown |
| `skills/*/SKILL.md` | `~/.agents/skills/*/SKILL.md` | Copy with path adjustment |
| `agents/roles.json` | `~/.codex/config.toml` | Generate `[agents.<name>]` TOML entries |

### Files

| File | Purpose |
|------|---------|
| `commands/man-generate-codex.md` | Slash command definition |
| `scripts/generate-codex.py` | Python script performing generation |

### Script: generate-codex.py

**Input:**
- `agents/*.md` — agent definition files
- `agents/roles.json` — role → agent → model mapping
- `skills/*/SKILL.md` — all skill definitions

**Output:**
```
~/.codex/
├── AGENTS.md          ← merged agent instructions
└── config.toml        ← agent role entries

~/.agents/
└── skills/
    ├── brainstorming/
    │   └── SKILL.md
    ├── writing-plans/
    │   └── SKILL.md
    └── ... (all skills with SKILL.md)
```

**Algorithm:**
1. Resolve `MANKIT_ROOT` (plugin root or CWD)
2. Read `agents/roles.json` → build role map
3. For each `agents/*.md`:
   - Read content
   - Append to AGENTS.md with `## <agent-name>` header
   - Add role metadata from roles.json
4. For each `skills/*/SKILL.md`:
   - Read file
   - Create `~/.agents/skills/<name>/` directory
   - Write SKILL.md (copy content, no transform needed — format is compatible)
   - Also copy `skills/<name>/references/` if exists
5. Generate `~/.codex/config.toml`:
   ```toml
   [agents.debugger]
   description = "5-phase systematic root-cause analysis"
   
   [agents.code-reviewer]
   description = "Code review against plan + coding standards"
   ```
6. Print summary: X agents, Y skills generated

**Edge cases:**
- `~/.codex/` or `~/.agents/` don't exist → create
- Existing files → overwrite with warning
- Skills without SKILL.md → skip with warning
- Large skills with scripts/ → copy scripts/ too

### Command: man-generate-codex.md

```markdown
Invoke generate-codex.py to generate mankit agents and skills
into Codex CLI global format (~/.codex/ and ~/.agents/).

Run: python "$MANKIT_ROOT/scripts/generate-codex.py"

Report results to user.
```

---

## Out of Scope
- Cursor/Windsurf/Gemini support (future — extend with --target flag)
- Project-level Codex config (only global)
- Hooks migration (Codex has different hook system)
- Two-way sync (Codex → mankit)

## Success Criteria
- `/man-level 3` sets coding level, agent responses adjust
- `/man-generate-codex` generates valid Codex-compatible files
- `codex` CLI can discover and use generated skills
- No manual file editing required after generation
