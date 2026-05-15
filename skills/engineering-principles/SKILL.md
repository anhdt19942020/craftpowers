---
name: engineering-principles
description: Apply SOLID, DRY, KISS, Clean Code, Design Patterns. Use when: writing or reviewing non-trivial code.
phase: BUILD
---

# Engineering Principles

Foundation for code quality. **Apply by default; deviate only with stated reason.**

## Overview

Five layers, used in this order when reading/writing code:

1. **KISS** — does the simplest thing that could work
2. **DRY** — don't repeat yourself, but don't pre-abstract either
3. **SOLID** — object/module responsibility boundaries
4. **Clean Code** — naming, function size, comment hygiene
5. **Design Patterns** — pull from catalog only when a recurring problem appears

Skipping a layer is fine. Adding a layer that isn't earning its weight is not.

## KISS — Keep It Simple, Stupid

The simplest code that solves the stated problem wins.

**Apply when:**
- Choosing between two implementations: pick the shorter, more direct one unless the other is measurably better
- Adding configuration / flags / strategy objects — ask "is this used today, or speculative?"
- Tempted to write a framework when you need one function

**Red flags:**
- Abstract base class with one concrete subclass
- Config option no caller sets to a non-default value
- Builder/factory for an object with 2 fields
- "We might need..." — future-proofing without a concrete user

## DRY — Don't Repeat Yourself, but...

Repetition of **knowledge** is the enemy. Repetition of **code** is sometimes fine.

**Rule of three:** Three similar lines is better than a premature abstraction. Wait for the third occurrence before extracting.

**Apply when:**
- The same business rule lives in 3+ places — extract
- The same magic number appears in 3+ files — constant
- Two functions diverge only by a flag they both branch on — likely one function, not two

**Red flags:**
- Helper used by exactly one caller
- "Generic" utility that only handles one shape
- Extracted abstraction where the two call sites will evolve independently — false DRY

## SOLID

**S — Single Responsibility.** A module has one reason to change. If two unrelated callers force edits to the same file, split it.

**O — Open/Closed.** Extend behavior by adding code, not editing existing code — *when extension points are already justified*. Don't add hooks speculatively (violates KISS).

**L — Liskov Substitution.** Subtypes must be usable wherever the base type is used, without surprises. If `Subclass.method()` throws where `Base.method()` doesn't, the hierarchy is wrong.

**I — Interface Segregation.** Don't force clients to depend on methods they don't use. A 12-method interface where each caller uses 2 is usually 3 interfaces.

**D — Dependency Inversion.** Depend on abstractions at module boundaries (DB, network, clock). Don't invert dependencies inside one module — that's ceremony.

**Application order:** SRP first (catches the most bugs). DIP at system boundaries. Others as code grows.

## Clean Code

**Naming.**
- Functions: verbs (`computeTotal`, `parseRequest`)
- Booleans: predicates (`isReady`, `hasAccess`)
- Avoid abbreviations except universally-known ones (`url`, `id`, `db`)
- Name reveals intent; if you need a comment to explain a name, rename

**Functions.**
- One level of abstraction per function — top-level orchestrates, lower-level executes
- ≤20 lines is a target, not a law; flag at 50+
- Arguments: 0–2 ideal, 3 OK, 4+ suspicious (consider an options object or splitting)
- No side effects in functions named like queries (`get*`, `find*`, `is*`)

**Comments.**
- Default: write none. Names should carry the meaning.
- Acceptable: hidden constraint, subtle invariant, workaround for a specific bug, surprising behavior
- Forbidden: WHAT the code does (the code says it), references to current PR/task (rots), commented-out code (delete it)

**Errors.**
- Throw at boundaries; catch where you can act
- Empty `catch {}` is a bug — log or rethrow
- Don't validate internal-only inputs; trust your own code

## Design Patterns — pull, not push

Patterns are vocabulary for recurring problems. **Don't apply a pattern unless the problem has already appeared.**

**Common, useful patterns:**

| Problem | Pattern |
|---|---|
| Algorithm varies, structure fixed | Strategy |
| One-to-many notification | Observer / pub-sub |
| Object creation depends on context | Factory |
| Add behavior without touching class | Decorator |
| Incompatible interfaces must collaborate | Adapter |
| Sequence of operations on a request | Chain of Responsibility / middleware |
| Encapsulate request as object (undo, queue, log) | Command |
| Traverse a structure | Iterator (usually language built-in) |
| Object behavior depends on state | State machine |
| Operation over a structure varies | Visitor (rarely worth it) |

**Anti-uses:**
- Singleton — usually a global in disguise; prefer dependency injection
- Visitor — almost always over-engineered in dynamic languages
- Abstract Factory of Factories — design smell

**Decision rule:** If you can name the pattern but cannot name *the recurring problem in this codebase* it solves, you're pattern-pushing. Stop.

## Apply Order — quick reference

When writing new code:

1. Get it working (KISS, ignore everything else)
2. Make it pass review: rename, shrink functions, kill dead branches (Clean Code)
3. Notice the third repetition → extract (DRY)
4. Notice the module has two reasons to change → split (SRP)
5. Notice a recurring shape → name the pattern, apply intentionally

When reviewing code:

1. Does it work? Tests passing, edge cases handled
2. Can a new reader understand it in one pass? (Clean Code: names, function size)
3. Is there hidden duplication? Same rule in 3+ places? (DRY)
4. Is responsibility clear? Does the file/module have one reason to change? (SRP)
5. Are abstractions earning their weight, or speculative? (KISS, OCP)
6. Are patterns used because the problem demands them, or because they're familiar? (Patterns — pull, not push)

## Red Flags Table

| Symptom | Likely violation |
|---|---|
| File >500 lines doing 3 things | SRP |
| `if (type === "x") {...} else if (type === "y") {...}` repeated in 4 files | Strategy / polymorphism |
| Helper with one caller | Premature DRY |
| Comment explains the name | Clean Code (rename) |
| Config option with no production caller | KISS |
| Subclass overrides every parent method | LSP / wrong hierarchy |
| 8-arg function | Clean Code (options object) or SRP split |
| Empty catch block | Error handling |
| Builder for 2-field object | KISS |
| Interface with 15 methods, no caller uses more than 3 | ISP |

## When NOT to apply

- Throwaway prototype: KISS only; ignore the rest
- Generated code: don't reformat
- One-off script <50 lines: clean naming is enough
- Codebase already has strong conventions: match them, don't impose these

## Related skills

- `test-driven-development` — tests drive the API; principles shape what's behind it
- `structured-refactoring` — apply these principles as the *direction* of refactors
- `api-and-interface-design` — ISP and DIP in detail at module boundaries
- `architecture-decision-records` — record principle trade-offs you made deliberately
