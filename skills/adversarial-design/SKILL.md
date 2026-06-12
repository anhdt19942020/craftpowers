---
name: adversarial-design
description: "Stress-test a design by grilling every decision. Use when: user says 'grill me' or wants plan challenged."
phase: THINK
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time.

If a question can be answered by exploring the codebase, explore the codebase instead.

## Advanced Adversarial Patterns

For structured iterative quality improvement: `references/gan-adversarial.md` — Generator↔Evaluator loop, use when first-draft quality is insufficient or for critical deliverables.

For multi-expert pre-analysis before risky changes: `references/multi-persona-predict.md` — 5 personas (Architect, Security, Performance, UX, Devil's Advocate), use before architectural decisions or refactors touching >10 files.
