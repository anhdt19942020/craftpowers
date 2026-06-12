# Mankit Simplification Plan

**Goal:** Cut complexity in mankit (craftpowers). Purge junk, dedup vs ClaudeKit (ck), adopt ck strengths (progressive disclosure, intent routing, lean catalog), shrink agents/commands/hooks surface.

**Audit date:** 2026-06-12 | **Repo:** D:/projects/craftpowers @ master (v6.60.3)

## Audit Snapshot

| Surface | README claims | Reality |
|---------|--------------|---------|
| Skills | 38 | 63 git-tracked + ~124 untracked junk dirs |
| Agents | 10 | 18 |
| Hooks | 4 | ~20 Python hook scripts + 3 profiles |
| Commands | — | 23 (many thin wrappers) |
| Disk junk | — | .venv 289MB, show-off 70MB, sequential-thinking 32MB, bash.exe.stackdump, `nul` |

Key context: mankit NOT currently installed in Claude Code (absent from enabledPlugins/marketplaces). Global ~/.claude runs ClaudeKit. Mankit = dev repo for a standalone plugin.

## Phases

| # | Phase | Status | Risk |
|---|-------|--------|------|
| 1 | [Purge untracked junk + gitignore hardening](phase-01-purge-untracked-junk-and-gitignore.md) | ✅ Done | None (untracked only) |
| 2 | [Dedup overlapping skills](phase-02-dedup-overlapping-skills.md) | ✅ Done | Low |
| 3 | [Slim mega SKILL.md files (ck progressive disclosure)](phase-03-slim-mega-skill-files.md) | ✅ Done | Medium (content moves) |
| 4 | [Rationalize agents 18→10, commands 23→~14](phase-04-rationalize-agents-and-commands.md) | ✅ Done | Medium |
| 5 | [Hooks diet — default minimal profile](phase-05-hooks-diet.md) | ✅ Done | Medium |
| 6 | [Docs sync + identity fix](phase-06-docs-sync-and-identity.md) | ✅ Done | Low |

## Dependencies

- Phase 1 independent — run first (pure deletion).
- Phase 2 before 3 (don't slim files that get deleted).
- Phase 4 after 2 (agent/command cuts follow skill cuts).
- Phase 6 last (docs reflect final state).

## ck Strengths Being Adopted

1. **Progressive disclosure** — SKILL.md < 10KB, detail in `references/` (phase 3)
2. **Single intent-routing map** — one routing doc instead of 23 wrapper commands + quiz (phase 4)
3. **Lean catalog** — every skill description costs tokens each session; fewer, sharper entries (phase 2)
4. **Machine-state checkpoints** — keep mankit's `loop-checkpoint`; aligns with ck CLI plan check model (no change needed)
5. **Description quality** — "MUST BE USED when / DO NOT USE when" pattern already good; extend to all agents (phase 4)

## Resolved Questions (2026-06-12)

1. ~~Codex CLI export~~ → **CUT.** Not using Codex. Delete `man-generate-codex` command + `scripts/generate-codex.py`.
2. ~~Standalone vs personal kit~~ → **Personal kit alongside ck (for now).** Keep mankit twin skills (cook, research-playbook, scenario-saturation, autoresearch-loop); don't aggressively dedup vs ck. Phase 2 dedup = internal-only overlap.
3. ~~docs/mankit/ gitignore~~ → **Un-ignore. Version it.** Remove `docs/mankit/` from `.gitignore`, `git add` specs+plans.
