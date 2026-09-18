# Security Policy

## Supported Versions

The following versions of PythonBox currently receive security updates:

| Version | Supported | Notes |
|---|---|---|
| `1.0.x` | :white_check_mark: | Current active release branch (`master`) |
| `< 1.0.0` | :x: | Legacy development snapshots; upgrade to 1.0.1+ recommended |

---

## Reporting a Vulnerability

Please report security vulnerabilities privately through GitHub's advisory system:

1. Open the repository's **Security** tab at [https://github.com/dev-bricks/pythonbox/security](https://github.com/dev-bricks/pythonbox/security).
2. Click **Report a vulnerability** to open a private draft advisory.
3. Include detailed information:
   - Affected version(s) and operating system environment
   - Step-by-step reproduction steps or proof of concept
   - Potential impact and threat model analysis
   - Any suggested remediations or workarounds

> [!IMPORTANT]
> **Please do not open public issues or pull requests for unresolved security vulnerabilities.** Never include proprietary source code, private user paths, or confidential material in reproduction scripts.

---

## Response Timeline & Service Level Agreements (SLA)

| Milestone | Commitment Window | Action Taken |
|---|---|---|
| **Initial Acknowledgment** | Within **48 hours** | Triage team confirms receipt of the private advisory. |
| **Triage & Impact Assessment** | Within **5 business days** | Reproducibility confirmed; CVSS rating and remediation roadmap assigned. |
| **Remediation & Patching** | Within **30 calendar days** | Patch developed, reviewed, and tested against regression suites. |
| **Coordinated Disclosure** | By mutual agreement | CVE identifier published alongside patch release and CHANGELOG entry. |

---

## Security Architecture & Invariants

PythonBox adheres to strict local-first security boundaries:

- **RunAsInvoker (Unprivileged User Mode):** PythonBox executes under standard user rights and never requests Windows UAC administrative elevation.
- **Zero Telemetry / Zero Egress:** The editor does not transmit metrics, crash dumps, or usage analytics over the internet.
- **Sanitized Process Execution:** Integrations with Git, linters (flake8, pylint, pyflakes), debuggers (PDB), and packaging utilities (PyInstaller) execute via structured parameter arrays (`List[str]`), strictly avoiding vulnerable shell concatenation (`shell=False`).
- **Atomic File Persistence:** Source file updates employ safe write-and-replace patterns to prevent partial-write corruption on sudden power loss or process termination.
- **Path Traversal Protection:** Relative file operations are strictly resolved against validated project roots.
