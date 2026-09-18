"""Automated metadata, contract, and workflow integrity tests for PythonBox.

Validates:
- PEP 621 compliance in pyproject.toml
- Version parity across codebase, docs, and configurations
- CI/CD workflow hardening (concurrency, timeout-minutes, matrices)
- .gitignore multi-host cloud-sync and lock protection guardrails
- SECURITY.md SLAs and supported versions
- THIRD_PARTY_LICENSES.md SBOM and invariant guarantees (INV-LOCAL-01..INV-SLA-10)
- llms.txt context index freshness
"""

import sys
import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        tomllib = None


REPO_ROOT = Path(__file__).resolve().parent.parent


class TestPEP621Metadata(unittest.TestCase):
    """Verify pyproject.toml compliance with PEP 621."""

    @classmethod
    def setUpClass(cls):
        cls.pyproject_path = REPO_ROOT / "pyproject.toml"
        if not cls.pyproject_path.exists():
            raise unittest.SkipTest("pyproject.toml not found")
        if tomllib is not None:
            with open(cls.pyproject_path, "rb") as f:
                cls.data = tomllib.load(f)
        else:
            cls.data = {}

    def test_pyproject_exists(self):
        self.assertTrue(self.pyproject_path.is_file(), "pyproject.toml must exist")

    def test_project_core_fields(self):
        if tomllib is None:
            text = self.pyproject_path.read_text(encoding="utf-8")
            self.assertIn('name = "pythonbox"', text)
            self.assertIn('version = "1.0.1"', text)
            return

        proj = self.data.get("project", {})
        self.assertEqual(proj.get("name"), "pythonbox")
        self.assertEqual(proj.get("version"), "1.0.1")
        self.assertEqual(proj.get("requires-python"), ">=3.10")
        self.assertEqual(proj.get("license", {}).get("text"), "MIT")
        self.assertTrue(len(proj.get("description", "")) > 10)

    def test_dependencies(self):
        if tomllib is None:
            text = self.pyproject_path.read_text(encoding="utf-8")
            self.assertIn("PySide6>=6.5.0", text)
            return

        proj = self.data.get("project", {})
        deps = proj.get("dependencies", [])
        self.assertTrue(any("PySide6" in dep for dep in deps), "PySide6 must be listed in dependencies")

    def test_project_urls(self):
        if tomllib is None:
            text = self.pyproject_path.read_text(encoding="utf-8")
            self.assertIn("[project.urls]", text)
            self.assertIn("Security", text)
            return

        urls = self.data.get("project", {}).get("urls", {})
        required_keys = ["Homepage", "Repository", "Issues", "Security", "Third-Party Licenses", "Changelog"]
        for key in required_keys:
            self.assertIn(key, urls, f"project.urls must include {key}")

    def test_pytest_and_ruff_configs(self):
        if tomllib is None:
            text = self.pyproject_path.read_text(encoding="utf-8")
            self.assertIn("[tool.pytest.ini_options]", text)
            self.assertIn("[tool.ruff]", text)
            return

        tools = self.data.get("tool", {})
        self.assertIn("pytest", tools)
        self.assertIn("ruff", tools)
        self.assertIn("tests", tools["pytest"]["ini_options"]["testpaths"])


class TestVersionParity(unittest.TestCase):
    """Verify version numbers are synchronized across files."""

    def test_version_in_pythonbox_v8(self):
        src = (REPO_ROOT / "PythonBox_v8.py").read_text(encoding="utf-8")
        self.assertIn('__version__ = "1.0.1"', src, "PythonBox_v8.py must declare __version__ = '1.0.1'")

    def test_version_in_changelog(self):
        changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("## [1.0.1]", changelog, "CHANGELOG.md must contain release entry for 1.0.1")

    def test_version_in_llms_txt(self):
        llms = (REPO_ROOT / "llms.txt").read_text(encoding="utf-8")
        self.assertIn("Version: 1.0.1", llms, "llms.txt must state Version: 1.0.1")

    def test_version_in_readmes(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
        self.assertIn("version-1.0.1", readme)
        self.assertIn("Version-1.0.1", readme_de)


class TestWorkflowHardening(unittest.TestCase):
    """Verify GitHub Actions workflows have concurrency and timeouts."""

    def test_workflows_exist_and_hardened(self):
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        expected_workflows = {
            "tests.yml": 15,
            "source-platform-smoke.yml": 15,
            "stale.yml": 10,
            "welcome.yml": 5,
        }

        for fname, expected_timeout in expected_workflows.items():
            wf_path = workflows_dir / fname
            self.assertTrue(wf_path.is_file(), f"Workflow {fname} must exist")
            content = wf_path.read_text(encoding="utf-8")
            self.assertIn("concurrency:", content, f"{fname} must specify concurrency")
            self.assertIn("cancel-in-progress: true", content, f"{fname} must set cancel-in-progress: true")
            self.assertIn(f"timeout-minutes: {expected_timeout}", content,
                          f"{fname} must set timeout-minutes: {expected_timeout}")

    def test_tests_workflow_matrix(self):
        tests_wf = (REPO_ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
        for py_ver in ["'3.10'", "'3.11'", "'3.12'", "'3.13'"]:
            self.assertIn(py_ver, tests_wf, f"tests.yml matrix must contain {py_ver}")


class TestGitignoreGuardrails(unittest.TestCase):
    """Verify .gitignore contains multi-host cloud-sync, lock, and cache protections."""

    def test_gitignore_patterns(self):
        gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        required_patterns = [
            "*conflicted copy*",
            "*-ASUS-GEI*",
            "*-WORKSTATION-LG*",
            "LOCK",
            "LOCK.*",
            "LOCK*.txt",
            "LOCK.permissions.json",
            "uv.lock",
            "!package-lock.json",
            ".hypothesis/",
            ".turbo/",
            ".coverage*",
        ]
        for pat in required_patterns:
            self.assertIn(pat, gitignore, f".gitignore must contain guardrail pattern: {pat}")


class TestSecurityPolicyAndSLA(unittest.TestCase):
    """Verify SECURITY.md contains versions table, response SLA, and RunAsInvoker."""

    def test_security_policy_contents(self):
        sec = (REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")
        self.assertIn("| `1.0.x` | :white_check_mark: |", sec, "Supported versions table missing")
        self.assertIn("48 hours", sec, "48h response SLA missing")
        self.assertIn("5 business days", sec, "5-day triage commitment missing")
        self.assertIn("RunAsInvoker", sec, "RunAsInvoker declaration missing")


class TestThirdPartyLicensesAndInvariants(unittest.TestCase):
    """Verify THIRD_PARTY_LICENSES.md contains SBOM, LGPL compliance, and INV-LOCAL-01..10."""

    def test_sbom_and_invariants(self):
        licenses_file = REPO_ROOT / "THIRD_PARTY_LICENSES.md"
        self.assertTrue(licenses_file.is_file(), "THIRD_PARTY_LICENSES.md must exist")
        content = licenses_file.read_text(encoding="utf-8")
        self.assertIn("PySide6", content)
        self.assertIn("LGPL-3.0-only", content)
        self.assertIn("Dynamic Linking", content)
        self.assertIn("Zero-Copyleft Contagion Guarantee", content)

        for i in range(1, 11):
            inv_id = f"INV-LOCAL-{i:02d}" if i <= 8 else f"INV-SLA-{i:02d}"
            self.assertIn(inv_id, content, f"Invariant {inv_id} must be defined in THIRD_PARTY_LICENSES.md")


class TestLLMsTxtFreshness(unittest.TestCase):
    """Verify llms.txt is fresh and complete."""

    def test_llms_content(self):
        llms = (REPO_ROOT / "llms.txt").read_text(encoding="utf-8")
        self.assertIn("Last-checked: 2026-09-18", llms)
        self.assertIn("dev-bricks/pythonbox", llms)
        self.assertIn("pyproject.toml", llms)
        self.assertIn("THIRD_PARTY_LICENSES.md", llms)


if __name__ == "__main__":
    unittest.main()
