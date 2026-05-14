---
name: pr-babysitter
schedule: "0 9 * * *"
description: "Daily nudge on stale non-draft PRs with no review approval."
---

# PR Babysitter

Every day, flag pull requests that have been open for more than 3 days, are not drafts, and have no review approval. Comment on each to prompt attention. Do not re-comment on the same PR within 7 days.

## Steps

1. **List open PRs:**
   ```
   gh pr list --json number,title,createdAt,isDraft,reviewDecision
   ```

2. **Filter for stale PRs** — keep only PRs where ALL of the following are true:
   - `isDraft` is `false`
   - `reviewDecision` is NOT `"APPROVED"` (i.e. `null`, `"REVIEW_REQUIRED"`, `"CHANGES_REQUESTED"`)
   - PR was created more than **3 days** ago (compare `createdAt` to now)

3. **For each stale PR, check for recent babysitter comments:**
   ```
   gh pr view <number> --json comments --jq '.comments[].body'
   ```
   Look for the babysitter comment signature: `⏰ This PR has been open for`. If a comment with this signature was posted within the last **7 days**, skip this PR.

4. **Comment on PRs that pass the check:**
   ```
   gh pr comment <number> --body "⏰ This PR has been open for X days without approval — needs attention."
   ```
   Replace `X` with the actual number of days since `createdAt`.

5. **If no stale PRs found:** Stop. Do not comment anywhere.

## Notes

- Run from the repository root.
- `gh` CLI must be authenticated.
- Days are calculated in whole days (floor of hours / 24).
- The 7-day deduplication window prevents comment spam on long-lived PRs.
- This routine does not close or label PRs — it only comments.
