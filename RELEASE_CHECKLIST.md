# Coordinated Release Evidence

Complete this checklist against exact commit hashes. Evidence from one hash does
not transfer to a changed candidate.

## Candidate identity

* Spec commit:
* SDK commit:
* Demo commit:
* Protocol baseline and amendment status:
* Python, Rust, npm, and Demo versions:

## Machine gate

* [ ] Spec `make check`
* [ ] SDK repository validation and strict schema compilation
* [ ] Common schema synchronization against the selected Spec commit
* [ ] Python lint, type check, tests, examples, build, package inspection, and audit
* [ ] Rust format, clippy, tests, docs, examples, package inspection, and audit
* [ ] After the exact-version `vcp-core` crate is published, rerun verified
      `cargo package -p vcp-cli` and `cargo package -p vcp-wasm`
* [ ] WebMCP type check, tests, build, package inspection, and audit
* [ ] Checked cross-language conformance runner
* [ ] Demo lint, type check, tests, links, build, budgets, and audit
* [ ] Secret scan and files-over-50-MiB check
* [ ] Two clean SDK builders produce byte-identical release directories
* [ ] Wheel, sdist, crates, CLI, WASM, npm tarball, SBOMs, checksums, and final
      manifest have retained GitHub artifact attestations

## Human gate

* [ ] Accessibility and assistive-technology review
* [ ] Protocol and cryptographic review
* [ ] Examples reviewed for safe production interpretation
* [ ] Governance approval for normative and maturity changes

## Rights and policy gate

* [ ] Asset and document provenance reviewed
* [ ] Licence, trademark, patent, contribution, and privacy posture approved
* [ ] Package metadata and notices approved

## Deployment and publication gate

* [ ] Authorized release owner approves the exact hashes and release order
* [ ] Registry and hosting credentials are used only by the authorized publisher
* [ ] Signed artifacts and provenance attestations are recorded
* [ ] PyPI, npm, and crates.io trusted-publisher identities match the exact
      repository, workflow file, protected environment, and release tag
* [ ] Production smoke tests pass against deployed URLs and registry packages
* [ ] Rollback owners and instructions are confirmed

Use `release/COORDINATED_RELEASE_RUNBOOK.md` for sequencing and the validated
`release/review-ledger.template.json` for the 13 cross-repository decisions.
Use `reviews/SDK_SECURITY_SEMVER_PUBLICATION_REVIEW.md` for K044 through K046.
