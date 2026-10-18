"""Exercise failure detection without touching a kernel or historical evidence."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("audit", Path(__file__).resolve().parents[1] / "scripts/verify-evidence.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.run = Path(self.directory.name)
        self.before = "<6>[1] boot\n"
        self.new = ("<6>[2] [rust_team2] event=loaded count=6 sum=23 min=1 max=9\n"
                    "<6>[3] [rust_team2] event=unload_begin retained=6 sum=23\n")
        for name, text in {"before.log": self.before, "after.log": self.before + self.new,
                           "new.log": self.new, "final.log": self.before + self.new,
                           "result.txt": "EXIT_STATUS=0\n", "commands.log": "fixture only\n",
                           "rounds.tsv": "round\tload\tlisted_after_load\tunload\tabsent_after_unload\n1\t0\tyes\t0\tyes\n"}.items():
            (self.run / name).write_text(text)

    def test_consistent_evidence_passes(self):
        self.assertEqual(audit.audit(self.run, 1)["status"], "PASS")

    def test_missing_file_fails(self):
        (self.run / "final.log").unlink()
        with self.assertRaisesRegex(ValueError, "missing evidence"):
            audit.audit(self.run, 1)

    def test_failed_exit_is_not_success(self):
        (self.run / "result.txt").write_text("EXIT_STATUS=1\n")
        with self.assertRaisesRegex(ValueError, "did not report success"):
            audit.audit(self.run, 1)

    def test_missing_round_fails(self):
        with self.assertRaisesRegex(ValueError, "expected 10 rounds"):
            audit.audit(self.run, 10)

    def test_modified_incremental_log_fails(self):
        (self.run / "new.log").write_text(self.new + "extra\n")
        with self.assertRaisesRegex(ValueError, "boundary"):
            audit.audit(self.run, 1)

    def test_failed_unload_fails(self):
        p = self.run / "rounds.tsv"
        p.write_text(p.read_text().replace("\t0\tyes\n", "\t1\tno\n"))
        with self.assertRaisesRegex(ValueError, "invalid lifecycle row"):
            audit.audit(self.run, 1)

    def test_warning_in_new_log_fails(self):
        new = self.new + "<4>[4] WARNING: fixture\n"
        (self.run / "after.log").write_text(self.before + new)
        (self.run / "new.log").write_text(new)
        with self.assertRaisesRegex(ValueError, "warning/error"):
            audit.audit(self.run, 1)


if __name__ == "__main__":
    unittest.main()
