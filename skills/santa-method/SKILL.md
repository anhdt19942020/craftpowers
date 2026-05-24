---
name: santa-method
description: Binary quality gate — 2 independent reviewers must both PASS. Stronger than advisory review. MUST BE USED when: pre-merge gate for critical PRs, pre-ship validation, after major refactors. DO NOT USE when: quick fixes (1-2 lines), draft/WIP code, exploratory prototypes.
---

# Santa Method — Binary Quality Gate

Hai independent reviewers, identical rubric, không shared context. CẢ HAI phải pass thì output mới được ship. Nếu một trong hai fail, fix rồi chạy lại CẢ HAI (fresh context mỗi lần).

## Usage

```
/man-santa <target> [--rubric <path>]
```

Trong đó `<target>` là file path, directory, branch diff, hoặc PR number.

## Protocol

### Phase 1: Chuẩn bị Rubric

Nếu `--rubric` được cung cấp, đọc rubric file. Nếu không, build default rubric từ context:

**Default rubric categories:**
1. **Correctness** — Code có làm đúng những gì nó tuyên bố không? Edge cases được xử lý?
2. **Safety** — Không có security vulnerabilities, không có data loss paths, không có credential exposure
3. **Conventions** — Theo project patterns (từ CLAUDE.md, existing code style)
4. **Completeness** — Tất cả acceptance criteria đã được đáp ứng, không có half-finished implementations
5. **Side effects** — Không có regressions trong adjacent code, không có broken contracts

Mỗi category: PASS hoặc FAIL với evidence cụ thể.

### Phase 2: Spawn Reviewers (Song song)

Spawn 2 reviewer agents đồng thời. Mỗi reviewer nhận:
- Rubric (giống hệt nhau cho cả hai)
- Target files/diff để review
- Instruction: "Review độc lập. Trả về PASS hoặc FAIL cho mỗi rubric category với evidence cụ thể."

**Anti-anchoring:** Reviewers được spawn với minimal context (không có conversation history, không có prior review results).

**Mỗi reviewer PHẢI trả về:**
```
VERDICT: PASS | FAIL
Categories:
- Correctness: PASS/FAIL — [evidence]
- Safety: PASS/FAIL — [evidence]
- Conventions: PASS/FAIL — [evidence]
- Completeness: PASS/FAIL — [evidence]
- Side effects: PASS/FAIL — [evidence]
Blocking issues: [danh sách hoặc "none"]
```

### Phase 3: Gate Decision

| Reviewer 1 | Reviewer 2 | Quyết định |
|-----------|-----------|----------|
| PASS | PASS | ✅ SHIP — output được approved |
| PASS | FAIL | ❌ FIX — áp dụng findings của Reviewer 2 |
| FAIL | PASS | ❌ FIX — áp dụng findings của Reviewer 1 |
| FAIL | FAIL | ❌ FIX — merge cả hai sets của findings |

### Phase 4: Convergence Loop (nếu FAIL)

1. Trình bày blocking issues cho user
2. Fix issues (user hoặc agent)
3. Chạy lại CẢ HAI reviewers với FRESH context (không nhớ lần chạy trước)
4. Tối đa 3 convergence iterations
5. Nếu vẫn fail sau 3 lần: báo cáo BLOCKED với tất cả unresolved issues

**Lý do cần fresh context:** Reviewers đã thấy version trước có thể anchor vào "nó gần đúng rồi" và bỏ sót issues mới được đưa vào bởi fix.

## Khi nào dùng

- Pre-merge gate cho critical PRs
- Pre-ship validation (`/man-ship` pipeline)
- Sau major refactors
- Khi advisory review cảm thấy không đủ

## Khi nào KHÔNG dùng

- Quick fixes (thay đổi 1-2 dòng)
- Draft/WIP code
- Exploratory prototypes
