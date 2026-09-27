#!/usr/bin/env python3
"""Negative controls: the supervision checks must reject deliberate drift."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from repo import ROOT, remove_comments, tracked_and_new_files


class SupervisionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="candle-supervision-")
        self.root = Path(self.temp.name)
        for relative in tracked_and_new_files():
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)

    def tearDown(self):
        self.temp.cleanup()

    def command(self, command):
        return subprocess.run([sys.executable, "tools/repo.py", command], cwd=self.root,
                              capture_output=True, text=True, check=False)

    def assert_rejected(self, fragment, command="check"):
        result = self.command(command)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(fragment, result.stderr)

    def test_unchanged_tree_passes(self):
        result = self.command("check")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_instruction_copy_fails(self):
        (self.root / "src/AGENTS.md").unlink()
        self.assert_rejected("Missing/divergent AGENTS.md")

    def test_new_directory_needs_instructions_but_ignored_build_does_not(self):
        (self.root / "target/nested").mkdir(parents=True)
        (self.root / "target/nested/cache").write_text("ignored")
        self.assertEqual(self.command("check").returncode, 0)
        (self.root / "new source").mkdir()
        (self.root / "new source/file.rs").write_text("// source")
        self.assert_rejected("new source/AGENTS.md")
        self.assertEqual(self.command("sync-agents").returncode, 0)
        self.assertEqual(self.command("check").returncode, 0)

    def test_stale_generated_output_fails(self):
        with (self.root / "src/generated.rs").open("a") as file:
            file.write("// unauthorized edit\n")
        self.assert_rejected("Generated drift")

    def test_upstream_edit_cannot_be_laundered_by_regeneration(self):
        with (self.root / "spec/upstream/holKernelScript.sml").open("a") as file:
            file.write("(* drift *)\n")
        self.assert_rejected("Upstream SHA-256 mismatch", command="generate")

    def test_harness_deletion_fails(self):
        path = self.root / "src/proofs.rs"
        path.write_text(path.read_text().replace("#[kani::proof]", "", 1))
        self.assert_rejected("harness/manifest mismatch")

    def test_unregistered_bound_change_fails(self):
        path = self.root / "src/proofs.rs"
        path.write_text(path.read_text().replace("#[kani::unwind(8)]", "#[kani::unwind(9)]", 1))
        self.assert_rejected("harness/manifest mismatch")

    def test_nested_comments_are_not_definitions(self):
        self.assertEqual(remove_comments("a(* x (* nested *) y *)b"), "a b")


if __name__ == "__main__":
    unittest.main()
