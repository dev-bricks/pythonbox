# Security Policy

## Supported Versions

The current `master` branch is the supported development line.

## Reporting a Vulnerability

Please report security issues privately through GitHub:

1. Open the repository's **Security** tab.
2. Choose **Report a vulnerability**.
3. Include affected files or versions, reproduction steps, impact, and any suggested mitigation.

Do not open public issues for vulnerabilities or include private data in screenshots, logs, or examples.

## Scope

Relevant security areas include:

- Local file opening, saving, and execution workflows
- Temporary files under the user's home directory
- Linter, debugger, Git, VS Code, PyCharm, and PyInstaller integrations
- Handling of paths, command arguments, and project files

PythonBox does not include telemetry, bundled credentials, cloud sync, or external service API tokens.

## Updates

Confirmed vulnerabilities are fixed on the default branch and documented in the changelog or release notes when applicable.
