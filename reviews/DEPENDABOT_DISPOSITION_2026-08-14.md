# Dependabot disposition, 2026-08-14

Status: candidate-bound review complete
External pull request state: unchanged
Candidate branch: `codex/all-improvements-20260812`

This record reconciles every Dependabot pull request that was open in
`Creed-Space/VCP-SDK` when queried on 2026-08-14. No pull request was closed,
rebased, merged, or otherwise modified. “Superseded” means only that this local
candidate contains an equal or newer version and has passed the cited local
checks.

| PR | Requested update | Candidate disposition | Candidate evidence |
|---:|---|---|---|
| [#65](https://github.com/Creed-Space/VCP-SDK/pull/65) | TypeScript 6.0.3 to 7.0.2 | Superseded at 7.0.2 | `npm run check`, 164 WebMCP tests, package validation, and production dependency audit passed |
| [#64](https://github.com/Creed-Space/VCP-SDK/pull/64) | Vitest 4.1.0 to 4.1.10 | Superseded at 4.1.10 | 10 test files and 164 tests passed |
| [#63](https://github.com/Creed-Space/VCP-SDK/pull/63) | rand 0.10.1 to 0.10.2 | Superseded at 0.10.2 | Locked workspace tests and strict all-target Clippy passed |
| [#62](https://github.com/Creed-Space/VCP-SDK/pull/62) | wasm-bindgen-test 0.3.68 to 0.3.76 | Superseded at 0.3.77 | Coordinated wasm-bindgen family update; locked workspace tests and strict all-target Clippy passed |
| [#61](https://github.com/Creed-Space/VCP-SDK/pull/61) | actions/cache 5.0.5 to 6.1.0 | Superseded at 6.1.0 | All workflow references use the immutable v6.1.0 commit; repository validation and Actionlint passed |
| [#59](https://github.com/Creed-Space/VCP-SDK/pull/59) | actions/checkout 6.0.2 to 7.0.0 | Superseded at 7.0.1 | All workflow references use the immutable v7.0.1 commit; repository validation and Actionlint passed |
| [#58](https://github.com/Creed-Space/VCP-SDK/pull/58) | regex 1.12.3 to 1.12.4 | Superseded at 1.12.4 | Locked workspace tests and strict all-target Clippy passed |
| [#55](https://github.com/Creed-Space/VCP-SDK/pull/55) | chrono 0.4.44 to 0.4.45 | Superseded at 0.4.45 | Locked workspace tests and strict all-target Clippy passed |
| [#52](https://github.com/Creed-Space/VCP-SDK/pull/52) | serde_json 1.0.149 to 1.0.150 | Superseded at 1.0.150 | Locked workspace tests and strict all-target Clippy passed |
| [#46](https://github.com/Creed-Space/VCP-SDK/pull/46) | PyNaCl minimum 1.5.0 to 1.6.2 | Obsolete rather than merged | PyNaCl is absent from the Python manifest, hash-locked requirements, source, and tests; the maintained implementation uses `cryptography` |
| [#45](https://github.com/Creed-Space/VCP-SDK/pull/45) | actions/setup-node 6.3.0 to 6.4.0 | Superseded at 7.0.0 | All workflow references use the immutable v7.0.0 commit; repository validation and Actionlint passed |

## Verification boundary

The local dependency candidates were verified on macOS. The repository also
defines hosted Linux, Windows, macOS, Node 22 and 24, Rust MSRV, WASM, and
installed-artifact jobs. Those hosted jobs have not run against this unpushed
candidate, so this record does not claim hosted CI proof.

External closure is intentionally deferred until the candidate is reviewed and
published to GitHub. At that point, each pull request can be closed as
superseded with a link to the merged candidate and its hosted checks.

Working if: every open dependency request has an exact disposition, no request
is called resolved merely because it is old, and external closure occurs only
after the superseding candidate and hosted evidence are visible.
