# SDK governance boundary

VCP-SDK is the reference implementation repository. It owns implementation
architecture, packaging, compatibility, tests, release engineering, and SDK
maintenance decisions. VCP-Spec is the sole canonical authority for protocol
text, schemas at their source, VEP numbering, protocol maturity, and permanent
governance.

The permanent VCP governance model is currently interim and unratified. The SDK
does not claim a constituted Technical Steering Committee, neutral foundation
control, rights authority, certification authority, or registry publication
authority. Current protocol authority state is recorded in
[VCP-Spec governance](https://github.com/Creed-Space/VCP-Spec/blob/main/GOVERNANCE.md)
and its machine-readable
[authority record](https://github.com/Creed-Space/VCP-Spec/blob/main/governance/authority.json).

## Decision routing

| Question | Canonical route |
|:---|:---|
| SDK bug, performance, language API, test, or packaging | VCP-SDK issue and reviewed pull request |
| Behavior that changes the protocol or schema | VCP-Spec amendment issue before SDK implementation is promoted |
| Cross-language conformance interpretation | VCP-Spec normative source plus VCP-SDK conformance evidence |
| Package name, semver, or registry publication | Coordinated release ledger and protected SDK release workflow |
| Licence, patent, trademark, or certification | Authorized rights review and VCP-Spec governance record |
| Demo behavior | VCP-Demo-Site, unless it exposes a protocol ambiguity |

The SDK issue chooser links protocol proposals to VCP-Spec and intentionally
contains no local VEP template or numbering authority.

Working signal: protocol proposals have one issue and number in VCP-Spec, SDK
pull requests cite that record, and implementation merge history never changes
protocol maturity by itself.

## Implementation decisions

SDK maintainers may review reversible implementation work under the repository
contribution process. Security emergencies use the private advisory route and
the minimum reversible repair. Publication, independent security, rights,
semver, and coordinated release decisions remain separate gates in
`release/review-ledger.template.json`.

Working signal: each released behavior traces to implementation tests and the
applicable protocol decision, while human and registry approvals remain named
rather than inferred.
