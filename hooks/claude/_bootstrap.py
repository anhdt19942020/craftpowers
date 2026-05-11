"""Make `hooks.lib` importable from entry-point scripts."""
import os
import sys


def plugin_root() -> str:
    return (
        os.environ.get("CLAUDE_PLUGIN_ROOT")
        or os.environ.get("CURSOR_PLUGIN_ROOT")
        or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    )


_root = plugin_root()
if _root not in sys.path:
    sys.path.insert(0, _root)
