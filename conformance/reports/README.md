# Generated conformance evidence

`conformance/runners/run_all.py` writes `latest.json`, one structured profile
report under `profiles/`, and `badge.json` here. These files are ignored build
evidence because they describe the exact local candidate and execution
environment. CI uploads them as immutable workflow artifacts.

The source-controlled coverage authority is
[`../coverage-manifest.json`](../coverage-manifest.json). It distinguishes
`checked`, `unsupported`, and `not_applicable` per vector and implementation.
The generated badge is a projection of runner output. It cannot claim
certification, independent implementation, registry publication, or
attestation merely because it exists locally. The protected release workflow
generates a fresh aggregate and badge for the exact primary candidate, uploads
them as retained evidence, and creates GitHub artifact attestations for both.

Run:

```bash
python3 scripts/generate_conformance_coverage.py --check
python3 conformance/runners/run_all.py
```
