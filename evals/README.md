# Evals

Human-driven A/B eval fixtures for mankit skills.

## Fixture Format

Each fixture is a JSON file in `evals/<skill-name>/`:

```json
{
  "prompt": "The exact prompt to paste into Claude.",
  "expected_signals": ["regex1", "regex2"],
  "forbidden_signals": ["bad-regex"]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `prompt` | yes | The prompt text to paste into a Claude session that has the skill loaded. |
| `expected_signals` | yes | Regex strings shown to the human as hints for what a good response should contain. These are NOT automatically matched — they guide human judgement. |
| `forbidden_signals` | no | Regex strings shown as hints for what should NOT appear in a good response. Also human-interpreted, not auto-matched. |

## Working Example

File: `evals/engineering-principles/01-srp-god-class.json`

```json
{
  "prompt": "Refactor this code:\n```\nclass UserManager {\n  saveUser(u) {...}\n  sendEmail(u) {...}\n  logActivity(u) {...}\n}\n```",
  "expected_signals": ["Single Responsibility", "split.*class", "separation"],
  "forbidden_signals": ["singleton", "abstract factory"]
}
```

When you run `python scripts/eval.py engineering-principles`, the harness prints a card with:
- The full skill content (to paste into a fresh Claude session as context)
- The prompt above
- A checklist of expected and forbidden signals

You paste both into Claude, observe the response, and enter `p` (pass) or `f` (fail).

## How Pass/Fail Works

Pass/fail is **human-judged**. The harness shows you what signals to look for, but you decide. A fixture passes if Claude's response, given the skill as context, demonstrates the skill's intended behavior as described by the signals.

There is no automated regex matching. The signal strings are guidance, not assertions.

## Adding Fixtures

1. Create `evals/<skill-name>/` if it doesn't exist.
2. Add one JSON file per scenario following the format above.
3. File names should be numbered for stable ordering: `01-srp.json`, `02-dry.json`, etc.
4. Run with: `python scripts/eval.py <skill-name>`

## Running an Eval

```bash
# Standard run
python scripts/eval.py engineering-principles

# Compare against a previous version of the skill
python scripts/eval.py engineering-principles --baseline HEAD~1
```

Results are written to `evals/<skill-name>/results-<timestamp>.md`.
