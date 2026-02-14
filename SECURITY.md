# Security Policy

## Supported Versions

| Version | Supported |
|:---|:---|
| Python SDK 1.0.x | Yes |
| Rust SDK 0.1.x | Yes |
| WebMCP SDK 0.1.x | Yes |
| VCP Specification 1.1 | Yes |
| VCP Specification 1.0 | Security fixes only |

## Reporting a Vulnerability

The VCP-SDK team takes security seriously. If you discover a security vulnerability, we appreciate your responsible disclosure.

### How to Report

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please report vulnerabilities via one of the following channels:

1. **Email:** Send a detailed report to **[security@creedspace.com](mailto:security@creedspace.com)**
2. **GitHub Security Advisories:** Use the [private vulnerability reporting](https://github.com/Creed-Space/VCP-SDK/security/advisories/new) feature

### What to Include

Please include the following in your report:

- **Description** of the vulnerability and its potential impact
- **Affected component** (Python SDK, Rust SDK, WebMCP SDK, specification, schemas)
- **Steps to reproduce** the issue
- **Proof of concept** code or payload, if applicable
- **Suggested fix**, if you have one

### Response Timeline

| Stage | Timeframe |
|:---|:---|
| Acknowledgment | Within 48 hours |
| Initial assessment | Within 5 business days |
| Fix development | Depends on severity |
| Public disclosure | After fix is released, coordinated with reporter |

### Severity Classification

| Severity | Description | Example |
|:---|:---|:---|
| **Critical** | Remote code execution, signature bypass | Forged bundle accepted as valid |
| **High** | Authentication bypass, data exfiltration | Private context fields leaked |
| **Medium** | Denial of service, information disclosure | Malformed token causes crash |
| **Low** | Minor issues with limited impact | Verbose error messages |

### Scope

The following are in scope for security reports:

- Cryptographic signature verification (bundle signing, hash integrity)
- Identity token parsing and validation
- Privacy level enforcement (public/consent/private boundaries)
- Transport layer security
- Schema validation bypass
- Dependency vulnerabilities in SDK packages

### Recognition

We are grateful to security researchers who help keep VCP safe. With your permission, we will acknowledge your contribution in our release notes and security advisories.

## Security Design

VCP's security model is built on:

- **Ed25519 signatures** for bundle authentication
- **SHA-256 content hashes** for integrity verification
- **Three-tier privacy architecture** (public/consent/private)
- **Verify-then-Inject pattern** — verification at the orchestration layer, not the LLM
- **Deterministic hooks** — constitutional rules enforced outside probabilistic model behavior

For details, see Section 13 (Security Considerations) of the [VCP Specification](./specs/VCP_SPECIFICATION_v1.0_COMPLETE.md).
