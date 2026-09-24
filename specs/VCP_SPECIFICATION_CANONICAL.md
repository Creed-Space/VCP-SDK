# VCP Specification — Canonical Location

The VCP specification suite lives in the
[VCP-Spec](https://github.com/Creed-Space/VCP-Spec) repository. VCP v3.1 is the
current source baseline; it has not been issued as an immutable, ratified
protocol release.

## Canonical Files

Paths are relative to the root of a VCP-Spec checkout.

| Document | Path |
|---|---|
| VCP v3.1 master specification (current source baseline) | `specs/VCP_SPECIFICATION_v3.1.md` |
| VCP/I Identity v2.0 (Draft) | `specs/VCP_IDENTITY_v2.0.md` |
| VCP/T Transport (v1.0 §4 Bundle Format, §7 Transport, §8 Verification) | `specs/VCP_SPECIFICATION_v1.0.md` |
| VCP/S Semantics v2.0 (Draft) | `specs/VCP_SEMANTICS_v2.0.md` |
| VCP/A Adaptation v2.0 (Draft, revision 2.1.0) | `specs/VCP_ADAPTATION_v2.0.md` |
| VCP/M Inter-Agent Messaging v1.2 (schema-backed baseline) | `specs/VCP_INTER_AGENT_MESSAGING_v1.2.md` |
| VCP/M Messaging v2.0 (Draft; the version this SDK implements) | `specs/VCP_MESSAGING_v2.0.md` |
| VCP/E Economic Governance v2.0 (Draft) | `specs/VCP_ECONOMIC_GOVERNANCE_v2.0.md` |
| VCP Core v2.0 (superseded by v3.1) | `specs/VCP_SPECIFICATION_v2.0.md` |

## SDK Version

This SDK (v4.2.0) implements the VCP v2.0 bundle baseline, plus capability
negotiation (a v3.1 Core feature, not a layer) and the v3.2 candidate adaptation
dimensions (VEP-0004, experimental).

## Archived

This repository's former copies of the v1.x specs are archived. Do not create
new VCP spec files in this repo. Edit the canonical files in VCP-Spec.
