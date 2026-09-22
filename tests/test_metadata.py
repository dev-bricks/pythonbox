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
        self.assertTrue("Last-checked: 2026-09-22" in llms or "Last-checked: 2026-09-" in llms)
        self.assertIn("dev-bricks/pythonbox", llms)
        self.assertIn("pyproject.toml", llms)
        self.assertIn("NOTICE", llms)
        self.assertIn("THIRD_PARTY_LICENSES.md", llms)


class TestNoticeAndAttribution(unittest.TestCase):
    """Verify canonical root NOTICE attribution file."""

    def test_notice_file_exists(self):
        notice = REPO_ROOT / "NOTICE"
        self.assertTrue(notice.is_file(), "NOTICE file must exist in repo root")

    def test_notice_contents(self):
        text = (REPO_ROOT / "NOTICE").read_text(encoding="utf-8")
        self.assertIn("Lukas Geiger", text)
        self.assertIn("dev-bricks", text)
        self.assertIn("open-bricks", text)
        for i in range(1, 11):
            inv_id = f"INV-LOCAL-{i:02d}" if i <= 8 else f"INV-SLA-{i:02d}"
            self.assertIn(inv_id, text, f"{inv_id} must be listed in NOTICE")


class TestBilingualNavigationParity(unittest.TestCase):
    """Verify 18-point navigation parity and reciprocal HTML anchors."""

    def test_18_point_anchors_in_both_readmes(self):
        readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
        for i in range(1, 19):
            anchor = f'<a id="sec-{i:02d}"></a>'
            self.assertIn(anchor, readme_en, f"README.md missing {anchor}")
            self.assertIn(anchor, readme_de, f"README_de.md missing {anchor}")

    def test_table_of_contents_in_both_readmes(self):
        readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
        self.assertIn("## Table of Contents", readme_en)
        self.assertIn("## Inhaltsverzeichnis", readme_de)
        for i in range(1, 19):
            self.assertIn(f"(#sec-{i:02d})", readme_en)
            self.assertIn(f"(#sec-{i:02d})", readme_de)


class TestDualMermaidDiagrams(unittest.TestCase):
    """Verify dual Mermaid diagrams (flowchart and sequenceDiagram)."""

    def test_diagrams_exist_in_readmes(self):
        readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
        for doc, name in [(readme_en, "README.md"), (readme_de, "README_de.md")]:
            self.assertIn("```mermaid\nflowchart TD", doc, f"{name} must contain flowchart TD")
            self.assertIn("```mermaid\nsequenceDiagram", doc, f"{name} must contain sequenceDiagram")
            self.assertIn("autonumber", doc, f"{name} sequenceDiagram must declare autonumber")

    def test_sequence_diagrams_clean_syntax(self):
        for fname in ["README.md", "README_de.md"]:
            content = (REPO_ROOT / fname).read_text(encoding="utf-8")
            in_seq = False
            for line in content.splitlines():
                if "sequenceDiagram" in line:
                    in_seq = True
                elif in_seq and line.strip().startswith("```"):
                    in_seq = False
                elif in_seq:
                    self.assertNotIn(";", line, f"Found unquoted semicolon in sequence diagram line in {fname}: {line}")


class TestPersonasAndComparativeMatrix(unittest.TestCase):
    """Verify target personas and 10-dimension comparative matrix."""

    def test_personas_in_readmes(self):
        readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
        for i in range(1, 5):
            persona = f"[PERSONA-{i:02d}]"
            self.assertIn(persona, readme_en, f"README.md missing {persona}")
            self.assertIn(persona, readme_de, f"README_de.md missing {persona}")

    def test_comparative_matrix_in_readmes(self):
        readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
        for doc in [readme_en, readme_de]:
            self.assertIn("IDLE", doc)
            self.assertIn("VS Code", doc)
            self.assertIn("PyCharm", doc)
            self.assertIn("PythonBox", doc)


class TestStatutoryNoticeAndSLA(unittest.TestCase):
    """Verify German statutory notice (§ 521 BGB) and 48h SLA."""

    def test_bgb_521_and_sla_references(self):
        readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
        sec = (REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")
        self.assertIn("521 BGB", readme_en)
        self.assertIn("521 BGB", readme_de)
        self.assertIn("48 hours", readme_en)
        self.assertIn("48 Stunden", readme_de)
        self.assertIn("48 hours", sec)


class TestPEP621LicenseFilesAndKeywords(unittest.TestCase):
    """Verify PEP 621 license-files, Notice URL, and 20 keywords."""

    def test_pyproject_license_files_and_notice(self):
        text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('"NOTICE"', text)
        self.assertIn('"LICENSE"', text)
        self.assertIn('"THIRD_PARTY_LICENSES.md"', text)
        self.assertIn('"Notice" =', text)

    def test_pyproject_keywords_count(self):
        if tomllib is not None:
            with open(REPO_ROOT / "pyproject.toml", "rb") as f:
                data = tomllib.load(f)
            keywords = data.get("project", {}).get("keywords", [])
            self.assertEqual(len(keywords), 20, f"Expected 20 keywords, got {len(keywords)}")


class TestMarketingLogRecency(unittest.TestCase):
    """Verify MARKETING-LOG.txt contains Pfad B audit."""

    def test_marketing_log_has_pfad_b(self):
        text = (REPO_ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")
        self.assertIn("Pfad B Marketing & Discoverability Audit (2026-09-22)", text)
        self.assertIn("Antigravity@ASUS-GEI", text)


if __name__ == "__main__":
    unittest.main()
