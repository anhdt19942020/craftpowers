---
name: cloud-routines
description: Guide for setting up Anthropic Routines — cloud-scheduled autonomous Claude tasks
phase: OPERATE
---

# Cloud Routines

Set up and manage Anthropic Routines — autonomous Claude tasks that run on Anthropic's infrastructure on a schedule or via API trigger. No local machine required.

## What Are Routines?

Routines are Claude Code sessions that run in the cloud on a cron schedule or triggered by external events (GitHub webhooks, API calls). They are configured at [claude.ai/code/routines](https://claude.ai/code/routines).

**Key differences from local `/schedule`:**
- Runs on Anthropic infrastructure — no local machine needed
- Survives machine shutoff, restarts, sleep
- Triggered by cron OR external events (GitHub, API)
- Full Claude Code session with tool access
- Billed per execution

## When to Use

```
Need recurring automation? → Yes
├── Must run without local machine? → Routine (cloud)
├── Must access local files/tools? → /schedule (local)
└── One-time delayed task? → /schedule (local)
```

**Use Routines for:**
- Daily PR review triage
- Weekly dependency audit
- Nightly test suite run on staging
- Auto-respond to GitHub issues with initial triage
- Periodic code quality reports

**Use local /schedule for:**
- Follow-up on a specific task in this session
- Reminders tied to local work context
- Tasks needing local file access

## Setup

1. Go to [claude.ai/code/routines](https://claude.ai/code/routines)
2. Connect your GitHub repository
3. Configure:
   - **Trigger**: cron schedule (`0 9 * * 1` = every Monday 9am) or GitHub event
   - **Prompt**: what Claude should do each run
   - **Repository**: which repo to operate on
   - **Branch**: which branch to target

## Routine Patterns

### Pattern 1: Daily PR Review

```
Trigger: 0 9 * * 1-5 (weekdays 9am)
Prompt: |
  Review all open PRs. For each:
  1. Check if CI passes
  2. Review code changes for obvious issues
  3. Comment with a summary and any concerns
  4. Label as 'needs-review' or 'looks-good'
```

### Pattern 2: Weekly Dependency Audit

```
Trigger: 0 10 * * 1 (Monday 10am)
Prompt: |
  Audit dependencies:
  1. Check for known vulnerabilities (npm audit / pip-audit)
  2. List outdated packages with breaking changes
  3. Create an issue summarizing findings
  4. If critical vulnerabilities found, create a fix PR
```

### Pattern 3: GitHub Issue Triage

```
Trigger: GitHub event (issue opened)
Prompt: |
  Triage this new issue:
  1. Read the issue description
  2. Search codebase for related files
  3. Label with area (frontend/backend/infra)
  4. Estimate complexity (small/medium/large)
  5. Comment with initial analysis and relevant file pointers
```

### Pattern 4: Nightly Test + Report

```
Trigger: 0 2 * * * (daily 2am)
Prompt: |
  Run full test suite on main branch.
  If any tests fail:
  1. Identify which tests broke
  2. Check recent commits for likely cause
  3. Create an issue with findings
  If all pass: update the test-health badge/comment.
```

## Cost Awareness

Each Routine execution is a full Claude Code session. Optimize:

- **Keep prompts focused** — don't ask for 10 things in one Routine
- **Use Sonnet** for mechanical tasks (PR labeling, issue triage)
- **Use Opus** only for tasks requiring judgment (architecture review)
- **Set reasonable frequency** — daily for active repos, weekly for stable ones
- **Monitor usage** at claude.ai/code/billing

## Integration with mankit

- Routines can invoke mankit skills if the repo has craftpowers installed
- Use `man:release-prep` in a pre-merge Routine for automated audit
- Use `man:requesting-code-review` pattern in PR review Routines
- Journal entries from Routine runs appear in `docs/mankit/journal/`

## Limitations

- Cannot access local machine files or tools
- Repository must be on GitHub (currently)
- Each execution starts fresh — no persistent session state
- Rate limited by your plan's API quota
