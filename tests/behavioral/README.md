# Behavioral Compliance Tests

Automated tests that verify agents follow skill instructions.

## Running

```bash
/man-compliance <skill-name>                        # Run all scenarios for a skill
/man-compliance <skill-name> --scenario <name>      # Run one scenario
```

## Adding Tests

1. Create `tests/behavioral/<skill-name>/test-<scenario>.md`
2. Define the prompt, expected behavior, and compliance checks
3. Run `/man-compliance <skill-name>` to verify

## File Structure

```
tests/behavioral/
├── README.md
├── council/
│   └── test-writes-position-first.md
├── santa-method/
└── writing-plans/
```

## Philosophy

Unit tests verify code correctness. Behavioral tests verify agent compliance.
A skill can have perfect code but agents may still not follow its instructions.
These tests close that gap.
