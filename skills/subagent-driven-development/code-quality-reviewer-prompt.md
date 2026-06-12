# Code Quality Reviewer Prompt Template

Use this template when dispatching a code quality reviewer subagent.

**Purpose:** Verify implementation is well-built (clean, tested, maintainable)

**Only dispatch after spec compliance review passes.**

```
Task tool (man:code-reviewer):
  model: sonnet
  Use template at skills/subagent-driven-development/code-quality-reviewer-prompt.md

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

**SOLID principles check** (apply where OOP is used):
- **S — Single Responsibility:** Does each class/module have one reason to change? Flag god classes.
- **O — Open/Closed:** Can behavior be extended without modifying existing code? Flag switch/if-chains that grow with each new type.
- **L — Liskov Substitution:** Can subtypes replace their parent without breaking behavior? Flag overrides that change contracts.
- **I — Interface Segregation:** Are interfaces focused? Flag interfaces forcing implementers to stub unused methods.
- **D — Dependency Inversion:** Do high-level modules depend on abstractions, not concretions? Flag direct instantiation of dependencies that should be injected.

**OOP & Clean Code check:**
- Was the right paradigm chosen? (OOP vs functional vs procedural — flag unnecessary class ceremony for simple data transformations, or procedural spaghetti where OOP would clarify)
- Encapsulation: is internal state properly hidden? Flag public fields that should be private with accessors.
- Composition vs inheritance: flag deep inheritance hierarchies (>2 levels) where composition would be simpler.
- Naming: do class/method names reveal intent? Flag generic names (Manager, Handler, Processor, Utils) without clear domain meaning.
- Function size: flag functions >30 lines or with >3 levels of nesting — likely need decomposition.
- Abstraction levels: does each function operate at one level of abstraction? Flag functions mixing high-level orchestration with low-level details.

**Code reviewer returns:** Strengths, Issues (Critical/Important/Minor), Assessment

## Reference checklists (conditional)

Sau khi review code, load checklist phù hợp diff:

- **Diff có FE file** (`.tsx/.jsx/.vue/.svelte`) → load `references/accessibility-checklist.md`. Check WCAG.
- **Diff đụng auth/input/network/storage** → load `references/security-checklist.md`. OWASP Top 10.
- **Diff đụng hot path / build size / DB query** → load `references/performance-checklist.md`. Core Web Vitals + backend.
- **Diff thêm/sửa test** → load `references/testing-patterns.md`. Structure, naming, mocking.

Find ≥1 issue per loaded checklist HOẶC explicit pass với lý do.
