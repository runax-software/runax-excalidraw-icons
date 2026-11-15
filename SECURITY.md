# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in runax-excalidraw-icons, please report it responsibly.

**Do not open a public issue.**

Instead, [open a private security advisory](https://github.com/runax-software/runax-excalidraw-icons/security/advisories/new) on GitHub.

Please include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Response

We will acknowledge your report within 48 hours and aim to provide a fix or mitigation within 7 days for critical issues.

## Supported Versions

| Version | Supported |
| ------- | --------- |
| latest  | Yes       |

## Scope

This policy covers the build code (`runax_icons/`) and the icons and libraries this
repository publishes. In scope, for example:

- An SVG in a pack's `src/`, or a generated `.excalidrawlib` / `.excalidraw`, that carries
  active content: scripts, event handlers, external references or anything else that runs or
  loads when the icon is opened in Excalidraw or a browser.
- An `import:` URL that could be swapped for a malicious file, or the build writing outside the
  pack's `src/` when it imports an archive.

Third-party dependencies (PyYAML, the GitHub Actions used by CI) are kept up to date through
Dependabot. A vulnerability in Excalidraw itself is reportable to the
[Excalidraw project](https://github.com/excalidraw/excalidraw).

Requests to change or remove an icon for trademark or licensing reasons are not security issues:
please open a regular issue.
