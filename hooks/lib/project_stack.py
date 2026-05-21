"""Detect project technology stack from file markers in the working directory."""
from __future__ import annotations

import os
from pathlib import Path

STACK_MARKERS: dict[str, list[str]] = {
    "php": ["composer.json"],
    "laravel": ["artisan", "app/Http/Kernel.php", "bootstrap/app.php"],
    "node": ["package.json"],
    "typescript": ["tsconfig.json"],
    "python": ["pyproject.toml", "requirements.txt", "setup.py"],
    "go": ["go.mod"],
    "rust": ["Cargo.toml"],
    "ruby": ["Gemfile"],
    "java": ["pom.xml", "build.gradle"],
    "dotnet": ["*.csproj", "*.sln"],
}

FRAMEWORK_MARKERS: dict[str, list[str]] = {
    "nextjs": ["next.config.js", "next.config.mjs", "next.config.ts"],
    "nuxt": ["nuxt.config.js", "nuxt.config.ts"],
    "django": ["manage.py", "django.conf"],
    "fastapi": ["main.py"],
    "nestjs": ["nest-cli.json"],
    "react": ["src/App.tsx", "src/App.jsx"],
    "vue": ["vue.config.js", "src/App.vue"],
    "svelte": ["svelte.config.js"],
}

LINTER_MAP: dict[str, dict[str, str]] = {
    "php": {
        "static": "./vendor/bin/phpstan analyse",
        "format": "./vendor/bin/pint --test --dirty",
    },
    "typescript": {
        "static": "tsc --noEmit",
        "lint": "eslint",
    },
    "node": {
        "lint": "eslint",
    },
    "python": {
        "static": "mypy",
        "lint": "ruff check",
    },
    "go": {
        "static": "go vet ./...",
        "lint": "golangci-lint run",
    },
    "rust": {
        "static": "cargo check",
        "lint": "cargo clippy",
    },
}


def detect_stack(cwd: str | None = None) -> list[str]:
    """Return list of detected stack identifiers sorted alphabetically."""
    cwd = cwd or os.getcwd()
    root = Path(cwd)
    found: list[str] = []

    for stack, markers in STACK_MARKERS.items():
        for marker in markers:
            if "*" in marker:
                if list(root.glob(marker)):
                    found.append(stack)
                    break
            elif (root / marker).exists():
                found.append(stack)
                break

    for framework, markers in FRAMEWORK_MARKERS.items():
        for marker in markers:
            if (root / marker).exists():
                found.append(framework)
                break

    return sorted(set(found))


def get_linters(stacks: list[str]) -> dict[str, str]:
    """Return relevant linter commands for detected stacks."""
    result: dict[str, str] = {}
    for stack in stacks:
        if stack in LINTER_MAP:
            result.update(LINTER_MAP[stack])
    return result


def format_stack_context(stacks: list[str]) -> str:
    """Format stack detection result for injection into agent context."""
    if not stacks:
        return "[project-stack: unknown]"

    linters = get_linters(stacks)
    lines = [f"[project-stack: {','.join(stacks)}]"]

    if linters:
        linter_parts = [f"{k}: `{v}`" for k, v in sorted(linters.items())]
        lines.append(f"[project-linters: {', '.join(linter_parts)}]")

    lines.append(
        "Apply ONLY verify/lint/format steps matching detected stack. "
        "Skip language-specific sections for other stacks."
    )
    return "\n".join(lines)
