"""Tests for hooks.lib.hook_logger — structured log writer for mankit hooks."""
import json
import os
import tempfile
import unittest
from unittest.mock import patch


class TestLogHook(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.log_path = os.path.join(self.tmp, "mankit-hooks.log")

    def _patch_log_path(self):
        import hooks.lib.hook_logger as mod
        return patch.object(mod, "_LOG_PATH", self.log_path)

    def test_writes_json_line(self):
        with self._patch_log_path():
            from hooks.lib.hook_logger import log_hook
            log_hook("stop", "ok")

        lines = open(self.log_path, encoding="utf-8").readlines()
        self.assertEqual(len(lines), 1)
        entry = json.loads(lines[0])
        self.assertEqual(entry["hook"], "stop")
        self.assertEqual(entry["status"], "ok")
        self.assertIn("ts", entry)

    def test_includes_detail_when_provided(self):
        with self._patch_log_path():
            from hooks.lib.hook_logger import log_hook
            log_hook("pre_tool_use", "block", "dangerous command")

        entry = json.loads(open(self.log_path, encoding="utf-8").read())
        self.assertEqual(entry["detail"], "dangerous command")

    def test_omits_detail_when_empty(self):
        with self._patch_log_path():
            from hooks.lib.hook_logger import log_hook
            log_hook("stop", "ok", "")

        entry = json.loads(open(self.log_path, encoding="utf-8").read())
        self.assertNotIn("detail", entry)

    def test_caps_detail_at_500_chars(self):
        long_detail = "x" * 1000
        with self._patch_log_path():
            from hooks.lib.hook_logger import log_hook
            log_hook("stop", "ok", long_detail)

        entry = json.loads(open(self.log_path, encoding="utf-8").read())
        self.assertEqual(len(entry["detail"]), 500)

    def test_log_error_formats_exception(self):
        with self._patch_log_path():
            from hooks.lib.hook_logger import log_error
            try:
                raise ValueError("something went wrong")
            except ValueError as exc:
                log_error("session_start", exc)

        entry = json.loads(open(self.log_path, encoding="utf-8").read())
        self.assertEqual(entry["status"], "error")
        self.assertIn("ValueError", entry["detail"])
        self.assertIn("something went wrong", entry["detail"])

    def test_appends_multiple_entries(self):
        with self._patch_log_path():
            from hooks.lib.hook_logger import log_hook
            log_hook("stop", "ok")
            log_hook("pre_tool_use", "block", "reason")

        lines = open(self.log_path, encoding="utf-8").readlines()
        self.assertEqual(len(lines), 2)

    def test_never_raises_on_unwritable_path(self):
        import hooks.lib.hook_logger as mod
        with patch.object(mod, "_LOG_PATH", "/no/such/dir/mankit-hooks.log"):
            from hooks.lib.hook_logger import log_hook
            # must not raise
            log_hook("stop", "ok")

    def test_rotates_when_over_size_limit(self):
        # Pre-fill the log file beyond _MAX_LOG_SIZE
        import hooks.lib.hook_logger as mod
        with self._patch_log_path():
            big_entry = json.dumps({"ts": "2024-01-01", "hook": "x", "status": "ok"}) + "\n"
            # Write enough to exceed 1MB
            over_limit = big_entry * (mod._MAX_LOG_SIZE // len(big_entry.encode()) + 10)
            with open(self.log_path, "w", encoding="utf-8") as f:
                f.write(over_limit)

            from hooks.lib.hook_logger import log_hook
            log_hook("stop", "ok")

        size = os.path.getsize(self.log_path)
        self.assertLess(size, mod._MAX_LOG_SIZE)

    def test_ts_is_utc_iso_format(self):
        with self._patch_log_path():
            from hooks.lib.hook_logger import log_hook
            log_hook("stop", "ok")

        entry = json.loads(open(self.log_path, encoding="utf-8").read())
        ts = entry["ts"]
        # UTC ISO format ends with +00:00 or Z
        self.assertTrue(ts.endswith("+00:00") or ts.endswith("Z"), f"Not UTC: {ts}")


if __name__ == "__main__":
    unittest.main()
