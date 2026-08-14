# Performance regression contract

The cross-language probe measures representative CSM-1 round trips, six-segment
scope globs, 64 KiB content hashing, roughly 48 KiB manifest canonicalization,
Ed25519 manifest verification, WebMCP context round trips, and a
seven-candidate, thirty-ballot Schulze computation. It records p50, p95,
throughput, wall time, and peak RSS in a JSON artifact bound to the Git commit
and a digest of every candidate source file.

The committed envelopes are deliberately coarse. They catch catastrophic
complexity, allocation, and parser regressions on pinned CI environments. They
do not claim that small timing differences on shared runners are meaningful.
Scheduled full runs and Criterion output provide trend evidence for narrower
performance work.

The smoke profile takes 20,000 parser samples and 25 content-hash samples. The
full profile takes 100,000 parser samples and 100 content-hash samples. Content
canonicalization scans the complete 64 KiB payload, so its count is bounded
separately rather than inferred from the much cheaper parser workload. Per-call
p95 and throughput limits still apply to every metric.

Run the pull request profile:

```bash
python3 scripts/run_performance.py \
  --profile smoke \
  --output performance-results/local-smoke.json
```

Run the detailed profile and Rust statistical benchmarks:

```bash
python3 scripts/run_performance.py \
  --profile full \
  --output performance-results/local-full.json
cd rust && cargo bench -p vcp-core --bench core_performance
```

An envelope change requires a benchmark artifact, an explanation tied to the
candidate source digest, and review. Raising thresholds solely to make a red run
green is not acceptable evidence.
