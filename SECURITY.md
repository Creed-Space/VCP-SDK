# Security Policy

## Supported versions

| Surface | Status |
|:---|:---|
| Python, Rust, and WebMCP SDK 4.2.x | Supported candidate |
| VCP v3.1 protocol baseline | Supported |
| v3.2 amendments and VEP-0004 | Pre-release review candidate |
| Older SDK and protocol versions | Considered case by case |

Package support and protocol support are separate. Reports should name the
affected package, protocol surface, and commit hash.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability. Use
[GitHub private vulnerability reporting](https://github.com/Creed-Space/VCP-SDK/security/advisories/new)
or email [security@creedspace.com](mailto:security@creedspace.com).

Include the affected component, impact, reproduction steps, a minimal proof of
concept where safe, and any proposed mitigation. Do not send live credentials,
personal data, or third-party secrets.

## Scope

Signature and hash verification, trust anchors, attestation, revocation,
temporal validity, replay defenses, privacy boundaries, hook enforcement,
namespace resolution, parsers, schema bypasses, package supply chain, denial of
service, and unsafe examples are in scope.

Normative protocol defects should also be coordinated with VCP-Spec. Editorial
or governance proposals without a security impact belong in the public VEP
process.

## Security posture

The orchestrators verify before injection and default to fail-closed decisions.
Applications still own network policy, durable replay storage, trusted-key
provisioning, audit retention, and operational monitoring. A package build or
passing test suite is machine evidence, not a production security approval.
