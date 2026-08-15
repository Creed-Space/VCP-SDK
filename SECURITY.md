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

Do not open a public issue for a suspected vulnerability. Use the repository's
[private vulnerability report](https://github.com/Creed-Space/VCP-SDK/security/advisories/new).
Email [security@creedspace.com](mailto:security@creedspace.com) if the GitHub
route is unavailable. The hosted private-report setting was enabled and read
back on 15 August 2026; a successful reporter-side test remains operational
evidence rather than source evidence.

Include the affected component, impact, reproduction steps, a minimal proof of
concept where safe, and any proposed mitigation. Do not send live credentials,
personal data, or third-party secrets.

The coordinated severity, embargo, disclosure, advisory, backport, and
revocation process is maintained in the public
[VCP-Spec security response](https://github.com/Creed-Space/VCP-Spec/blob/main/docs/SECURITY_RESPONSE.md).
Its response times are interim targets rather than a service-level agreement.

## Scope

Signature and hash verification, trust anchors, attestation, revocation,
temporal validity, replay defenses, privacy boundaries, hook enforcement,
namespace resolution, parsers, schema bypasses, package supply chain, denial of
service, and unsafe examples are in scope.

The cross-repository
[threat model](https://github.com/Creed-Space/VCP-Spec/blob/main/docs/THREAT_MODEL.md)
maps these surfaces to controls, exercises, and residual gates.

Normative protocol defects should also be coordinated with VCP-Spec. Editorial
or governance proposals without a security impact belong in the public VEP
process.

## Security posture

The orchestrators verify before injection and default to fail-closed decisions.
Applications still own network policy, durable replay storage, trusted-key
provisioning, audit retention, and operational monitoring. A package build or
passing test suite is machine evidence, not a production security approval.
