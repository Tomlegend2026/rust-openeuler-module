"""Host-side tests only; no kernel module is loaded."""
import importlib.util
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "scripts" / "extract-new-log.py"
spec = importlib.util.spec_from_file_location("extract_new_log", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ExtractionTests(unittest.TestCase):
    def test_only_new_lines_are_reported(self):
        self.assertEqual(module.extract_new("a\nb\nc\n", "a\nb\nc\nd\n"), "d\n")

    def test_ring_can_lose_older_lines_while_preserving_cursor(self):
        self.assertEqual(module.extract_new("old\na\nb\nc\n", "a\nb\nc\nd\n"), "d\n")

    def test_lost_cursor_is_not_silently_accepted(self):
        with self.assertRaises(ValueError):
            module.extract_new("a\nb\nc\n", "d\ne\nf\n")

    def test_ambiguous_cursor_is_rejected(self):
        with self.assertRaises(ValueError):
            module.extract_new("a\n", "a\nb\na\n")

    def test_empty_initial_log(self):
        self.assertEqual(module.extract_new("", "new\n"), "new\n")

    def test_no_new_lines(self):
        self.assertEqual(module.extract_new("a\nb\nc\n", "a\nb\nc\n"), "")


if __name__ == "__main__":
    unittest.main()
