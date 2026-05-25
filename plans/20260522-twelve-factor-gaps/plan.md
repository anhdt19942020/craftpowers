# 12-Factor Agent Gaps — Implementation Plan

## Background

Compared mankit agent system against [12-Factor Agents](https://github.com/humanlayer/12-factor-agents).
3 gaps identified. This plan fixes them while preserving mankit's existing strengths (security gates, quality gates, team coordination).

## Phases

| Phase | Name | Status | Priority | Files |
|-------|------|--------|----------|-------|
| 1 | [Unified Workflow State](phase-01-unified-state.md) | ✅ DONE | High | 4 new, 3 modified |
| 2 | [Error Self-Healing](phase-02-error-self-healing.md) | ✅ DONE | High | 2 new, 2 modified |
| 3 | [Stateless Reducer Pattern](phase-03-stateless-reducer.md) | ✅ DONE | Medium | 2 new, 3 modified |

## Dependencies

```
Phase 1 (Unified State) ──► Phase 3 (Stateless Reducer)
                              ▲
Phase 2 (Error Self-Healing) ─┘
```

Phase 1 + 2 parallel. Phase 3 depends on both.

## Design Constraints

- Zero breaking changes to existing agent definitions
- Hooks-based — no Claude harness modifications needed
- State files = JSON, human-readable
- Backward compatible — agents work without state file (graceful degrade)
