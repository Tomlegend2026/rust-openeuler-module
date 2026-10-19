"""Tests for the saved kernel-log summary utility."""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "summarize_log", Path(__file__).resolve().parents[1] / "scripts/summarize-log.py"
)
summary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summary)


class LogSummaryTests(unittest.TestCase):
    def test_summarizes_extended_statistics(self):
        result = summary.summarize(
            "[rust_team2] event=loaded count=6 sum=23 min=1 max=9\n"
            "[rust_team2] event=stats_detail average=3 range=8\n"
            "[rust_team2] event=unload_begin retained=6 sum=23\n"
        )
        self.assertEqual(result["loaded_events"], 1)
        self.assertEqual(result["stats_detail_events"], 1)
        self.assertEqual(result["unload_events"], 1)
        self.assertEqual(result["extended_statistics"], {"average": 3, "range": 8})

    def test_handles_old_logs_without_extended_line(self):
        result = summary.summarize(
            "[rust_team2] event=loaded count=6 sum=23 min=1 max=9\n"
            "[rust_team2] event=unload_begin retained=6 sum=23\n"
        )
        self.assertIsNone(result["extended_statistics"])
        self.assertEqual(result["statistics"]["sum"], 23)

    def test_ignores_unrelated_kernel_lines(self):
        result = summary.summarize("<6> unrelated\n<4> warning from another device\n")
        self.assertEqual(result["loaded_events"], 0)
        self.assertIsNone(result["statistics"])


if __name__ == "__main__":
    unittest.main()
