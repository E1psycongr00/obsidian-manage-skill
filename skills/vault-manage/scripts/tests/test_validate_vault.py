import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "validate_vault.py"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
TEMPLATE_PATH = Path(__file__).resolve().parents[2] / "assets" / "validation-report-template.md"


class ValidateVaultCLITests(unittest.TestCase):
    def template_check_names(self):
        names = []
        in_checks = False
        for line in TEMPLATE_PATH.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped == "checks:":
                in_checks = True
                continue
            if in_checks and line.startswith("  - ") and ":" in stripped:
                names.append(stripped[2:].split(":", 1)[0].strip())
                continue
            if in_checks and stripped and not line.startswith("  - "):
                break
        return names

    def run_validator(self, cwd: Path, extra_args=None):
        cmd = [sys.executable, str(SCRIPT_PATH)]
        if extra_args:
            cmd.extend(extra_args)
        return subprocess.run(
            cmd,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

    def test_pass_case(self):
        result = self.run_validator(FIXTURES_DIR / "pass_case")
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("status: PASS", result.stdout)

    def test_missing_required_field_fails(self):
        result = self.run_validator(FIXTURES_DIR / "missing_field_case")
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("missing required field: description", result.stdout)

    def test_bad_date_format_fails(self):
        result = self.run_validator(FIXTURES_DIR / "bad_date_case")
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("invalid date format in created", result.stdout)

    def test_dead_link_fails(self):
        result = self.run_validator(FIXTURES_DIR / "dead_link_case")
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("Dead link", result.stdout)

    def test_cross_module_attachment_fails(self):
        result = self.run_validator(FIXTURES_DIR / "cross_attachment_case")
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("cross-module attachment link", result.stdout)

    def test_git_modified_last_updated_fails(self):
        src = FIXTURES_DIR / "git_modified_case"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp) / "repo"
            shutil.copytree(src, tmp_root)

            subprocess.run(["git", "init"], cwd=str(tmp_root), check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(tmp_root), check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(tmp_root), check=True)
            subprocess.run(["git", "add", "."], cwd=str(tmp_root), check=True)
            subprocess.run(["git", "commit", "-m", "init"], cwd=str(tmp_root), check=True)

            note = tmp_root / "01. Projects/Demo/Git Modified.md"
            note.write_text(note.read_text(encoding="utf-8") + "\n추가 변경.\n", encoding="utf-8")

            result = self.run_validator(
                tmp_root,
                ["--check-git-modified", "--today", "2026-02-23"],
            )
            self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
            self.assertIn("last-updated='2026-02-20'", result.stdout)

    def test_target_scope_ignores_out_of_scope_failures(self):
        root = FIXTURES_DIR / "target_scope_case"
        result = self.run_validator(root, ["--target", "01. Projects/🚀 Good"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("status: PASS", result.stdout)

    def test_json_output_schema(self):
        result = self.run_validator(FIXTURES_DIR / "pass_case", ["--format", "json"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("status", payload)
        self.assertIn("checks", payload)
        self.assertIn("issues", payload)
        self.assertIn("summary", payload)
        self.assertIn("next_action", payload)
        self.assertEqual(payload["status"], "PASS")
        template_checks = set(self.template_check_names())
        output_checks = {item["name"] for item in payload["checks"]}
        self.assertEqual(output_checks, template_checks)


if __name__ == "__main__":
    unittest.main()
