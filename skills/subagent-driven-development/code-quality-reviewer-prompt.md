# Code Quality Reviewer Prompt Template

Use this template when dispatching a code quality reviewer subagent.

**Purpose:** Verify implementation is well-built (clean, tested, maintainable)

**Only dispatch after spec compliance review passes.**

```
Task tool (man:code-reviewer):
  model: sonnet
  Use template at requesting-code-review/code-reviewer.md

  WHAT_WAS_IMPLEMENTED: [from implementer's report]
  PLAN_OR_REQUIREMENTS: Task N from [plan-file]
  BASE_SHA: [commit before task]
  HEAD_SHA: [current commit]
  DESCRIPTION: [task summary]
```

**In addition to standard code quality concerns, the reviewer should check:**
- Does each file have one clear responsibility with a well-defined interface?
- Are units decomposed so they can be understood and tested independently?
- Is the implementation following the file structure from the plan?
- Did this implementation create new files that are already large, or significantly grow existing files? (Don't flag pre-existing file sizes — focus on what this change contributed.)
- Did the diff reformat or restyle lines that weren't functionally changed? Only changed code should be formatted — flag whole-file reformatting as Important.

**Code reviewer returns:** Strengths, Issues (Critical/Important/Minor), Assessment

## Reference checklists (conditional)

Sau khi review code, load checklist phù hợp diff:

- **Diff có FE file** (`.tsx/.jsx/.vue/.svelte`) → load `references/accessibility-checklist.md`. Check WCAG.
- **Diff đụng auth/input/network/storage** → load `references/security-checklist.md`. OWASP Top 10.
- **Diff đụng hot path / build size / DB query** → load `references/performance-checklist.md`. Core Web Vitals + backend.
- **Diff thêm/sửa test** → load `references/testing-patterns.md`. Structure, naming, mocking.

Find ≥1 issue per loaded checklist HOẶC explicit pass với lý do.
