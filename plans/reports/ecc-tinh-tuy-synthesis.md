# ECC Tinh Túy — Top Patterns Worth Adopting for Mankit

**Date:** 2026-05-24
**Based on:** 3 deep-dive reports (~1800 lines total) + existing 12 proposals

---

## Tổng quan

Sau khi đào sâu toàn bộ ECC (232 skills, 60 agents, 72 commands, 45 hooks), đã lọc ra **9 pattern MỚI** chưa có trong 12 proposals hiện tại. Xếp theo ROI (impact ÷ effort).

**Lưu ý:** 4 quick wins đã implement xong (Prompt Defense, Gateguard, Catalog CI, Cost Tracker). 8 proposals còn lại (5-12) vẫn valid — document này bổ sung thêm, KHÔNG thay thế.

---

## Tier 1: Implement Ngay (< 2h mỗi cái, ROI cực cao) ✅ DONE

### 1. Description-as-Dispatch-Directive

**ECC làm gì:** Agent descriptions chứa imperative directives — "MUST BE USED for Python projects", "TRIGGER when: user requests a plan". Claude dùng description để route, nên directive = dispatch signal.

**Mankit hiện tại:** Descriptions passive, descriptive. Ví dụ: `"Implements ONE task from a plan"` — không nói khi nào PHẢI dùng.

**Thay đổi cụ thể:** Thêm `MUST BE USED when:` và `DO NOT USE when:` vào description của 14 agents.

**Files:** `agents/*.md` — sửa frontmatter `description` field

**Ví dụ:**
```yaml
# Trước:
description: "Implements ONE task from a plan"

# Sau:
description: "Implements ONE task from a plan. MUST BE USED when executing plan tasks. DO NOT USE for debugging, review, or exploration."
```

**Effort:** 30 phút | **Impact:** Routing accuracy tăng đáng kể

---

### 2. Build Resolver Stop Conditions

**ECC làm gì:** Mọi build resolver có explicit stop: "Halt after 3 failed fix attempts on same error." Prevent infinite retry loops.

**Mankit hiện tại:** `debugger` agent không có hard stop condition — có thể loop vô hạn.

**Thay đổi cụ thể:** Thêm stop conditions vào `debugger.md` và `implementer.md`:
```markdown
## Stop Conditions
- STOP after 3 failed attempts on the same error
- STOP if the same test fails with identical output 2 consecutive times
- STOP if total tool calls exceed 50 without progress
- Report BLOCKED status with root cause analysis
```

**Files:** `agents/debugger.md`, `agents/implementer.md`

**Effort:** 15 phút | **Impact:** Prevent token waste từ infinite loops

---

### 3. Strategic Compact Hook

**ECC làm gì:** `suggest-compact.js` — PreToolUse hook đếm tool calls, suggest `/compact` ở phase boundary (default threshold: 50 calls, remind mỗi 25 calls sau đó). Decision table cho phase transitions.

**Mankit hiện tại:** `context-management` skill advisory, không automated. Không có hook tự suggest.

**Thay đổi cụ thể:** Thêm PreToolUse hook đếm tool calls, inject suggestion khi vượt threshold.

**Files:** `hooks/suggest-compact.py` (new), `hooks/claude/hooks.json` (update)

**Logic:**
```python
# Count tool calls in session via env/state file
# At 50 calls: stdout "⚠️ Context budget: 50+ tool calls. Consider /compact at next phase boundary."
# Every 25 after: remind again
```

**Effort:** 1h | **Impact:** Prevent mid-implementation auto-compaction breaking state

---

## Tier 2: Medium Effort (4h-1d, high value)

### 4. Anti-Anchoring Protocol (Council Pattern)

**ECC làm gì:** Trong `council` skill — main Claude viết position TRƯỚC, rồi mới spawn Skeptic + Pragmatist + Critic. Subagents không thấy main position → prevent anchoring bias. Subagents chỉ nhận question + compact context, KHÔNG full conversation.

**Mankit hiện tại:** `adversarial-design` và `multi-persona-predict` không có anti-anchoring. Main agent có thể bị bias bởi subagent output.

**Thay đổi cụ thể:** Tạo `council` skill hoặc update `adversarial-design`:
1. Main agent viết position trước (save to file)
2. Spawn 3 subagents parallel với minimal context
3. Synthesize all 4 positions with explicit bias guardrails
4. Output limited, actionable

**Files:** `skills/council/SKILL.md` (new) hoặc update `skills/adversarial-design/SKILL.md`

**Effort:** 4h | **Impact:** Better decision quality cho architectural choices

---

### 5. Santa-Method Binary Gate

**ECC làm gì:** 2 independent reviewers launched parallel, identical rubric, no shared context. BOTH must pass → output ships. Nếu either fails → fix → re-run BOTH. Anti-anchoring: fresh context mỗi lần.

**Mankit hiện tại:** `code-reviewer` là advisory. `final-approver` là advisory (APPROVE/FLAG). Không có binary gate.

**Thay đổi cụ thể:** Tạo `santa-method` skill cho pre-merge gate:
1. Spawn 2 reviewer agents parallel (isolated context)
2. Identical rubric passed to both
3. Both return PASS/FAIL verdict
4. If either FAIL → apply fixes → re-run BOTH (convergence loop)
5. Max 3 convergence iterations

**Files:** `skills/santa-method/SKILL.md` (new)

**Effort:** 4-8h | **Impact:** Stronger quality gate than advisory review. Giảm false-positive approvals.

---

### 6. Iterative Retrieval Loop

**ECC làm gì:** DISPATCH → EVALUATE → REFINE → CONVERGE loop cho subagent context gathering. Giải quyết "context problem" — agent không biết cần context gì upfront.

**Mankit hiện tại:** Không có equivalent. Subagents nhận context cố định từ prompt.

**Thay đổi cụ thể:** Tạo `iterative-retrieval` skill:
1. DISPATCH: broad query → subagent searches codebase
2. EVALUATE: score relevance 0-1 cho mỗi result
3. REFINE: update search criteria dựa trên evaluation (fix terminology mismatches)
4. CONVERGE: exit khi đủ high-relevance context
5. Max 3 iterations

**Files:** `skills/iterative-retrieval/SKILL.md` (new)

**Effort:** 4-8h | **Impact:** Subagents get better context → better output. RAG-for-agents không cần vector DB.

---

### 7. Write-Time Quality (Plankton Pattern)

**ECC làm gì:** PostToolUse hooks trên Edit/Write:
1. Auto-format silently (biome/prettier)
2. Collect violations as JSON
3. Spawn subprocess để fix — route to Haiku (style) / Sonnet (logic) / Opus (type reasoning)
4. Config protection: block LLM from editing linter configs
5. Main agent chỉ thấy violations subprocess không fix được

**Mankit hiện tại:** `setup-pre-commit` chỉ pre-commit. Không có write-time enforcement.

**Thay đổi cụ thể:** PostToolUse hook trên Edit/Write events:
1. Run formatter on modified file
2. Run linter, collect violations
3. Auto-fix simple violations silently
4. Report unfixable violations to agent

**Files:** `hooks/write-quality.py` (new), `hooks/claude/hooks.json` (update)

**Effort:** 1 day | **Impact:** Code quality enforcement at write time, not commit time. Faster feedback loop.

---

## Tier 3: Strategic (cần plan riêng, 1-2 tuần)

### 8. Hookify Declarative Abstraction

**ECC làm gì:** Hook rules viết bằng markdown + YAML frontmatter thay vì raw JSON. File `.claude/hookify.{rule-name}.local.md` chứa:
```yaml
---
event: bash
action: block
pattern: "rm -rf /"
---
Block dangerous recursive delete at root.
```
Kèm companion commands: `/hookify`, `/hookify-list`, `/hookify-configure`.

**Mankit hiện tại:** Hooks configured trực tiếp trong `settings.json` JSON. Không ergonomic cho non-engineers.

**Why strategic:** Cần thay đổi hook discovery + registration flow. Không phải sửa 1-2 file.

**Impact:** Hook authoring accessible cho mọi user, không chỉ developer.

---

### 9. Blueprint Cold-Execution Constraint

**ECC làm gì:** Trong `blueprint` skill — mỗi step trong plan PHẢI self-contained. Fresh agent có thể execute bất kỳ step nào mà không cần đọc steps trước. Mỗi step có: context brief, task list, verification commands, exit criteria.

**Mankit hiện tại:** `writing-plans` skill yêu cầu steps có context nhưng không enforce cold-execution constraint. Plan steps thường reference prior steps.

**Thay đổi cụ thể:** Update `writing-plans` skill thêm cold-execution validation:
- Mỗi task PHẢI include full context — imports, types, function signatures từ prior tasks
- Self-review step kiểm tra: "Could a fresh agent execute this task without reading any other task?"
- Nếu không → revise task để self-contained

**Files:** `skills/writing-plans/SKILL.md` (update)

**Effort:** Nửa ngày implement, nhưng thay đổi mọi plan output → test kỹ

---

## So Sánh: Proposals Mới vs Proposals Cũ (5-12)

| Pattern Mới | Overlap với Proposal Cũ? | Khác biệt |
|---|---|---|
| 1. Description-as-dispatch | Không | Hoàn toàn mới |
| 2. Stop conditions | Không | Hoàn toàn mới |
| 3. Strategic compact | Không | Mới (khác context-management skill) |
| 4. Anti-anchoring | Liên quan P12 (GAN) | Nhưng áp dụng rộng hơn, cho mọi multi-agent deliberation |
| 5. Santa-method | Liên quan P12 (GAN) | Khác: binary gate vs adversarial generation loop |
| 6. Iterative retrieval | Không | Hoàn toàn mới |
| 7. Write-time quality | Không | Mới (khác pre-commit hooks) |
| 8. Hookify | Liên quan P10 (Hook Profiles) | Khác: declarative format vs profile system |
| 9. Blueprint cold-execution | Không | Update existing skill |

---

## Khuyến Nghị Thứ Tự Implement

```
Tuần này (< 3h total):
  1. Description-as-dispatch-directive     (30 phút)
  2. Build resolver stop conditions         (15 phút)
  3. Strategic compact hook                 (1h)

Tuần sau:
  4. Anti-anchoring protocol               (4h)
  5. Santa-method binary gate              (4-8h)
  6. Iterative retrieval loop              (4-8h)

Sprint sau:
  7. Write-time quality (plankton)         (1 day)
  9. Blueprint cold-execution              (0.5 day)

Backlog:
  8. Hookify declarative abstraction       (1-2 weeks)
```

**Kết hợp với proposals cũ:** Instinct System (P5) vẫn là P0 — nên làm song song với Tier 1 ở trên.

---

## Sources

- `plans/reports/ecc-deep-workflow-analysis.md` (675 lines)
- `plans/reports/ecc-deep-agents-analysis.md` (437 lines)
- `plans/reports/ecc-deep-commands-skills.md` (707 lines)
- `plans/reports/ecc-improvement-proposals.md` (275 lines)
- ECC source: `D:\Projects\_research\ecc` (cloned 2026-05-24)
