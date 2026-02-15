# VCP Conformance Test Suite

Language-agnostic test fixtures for validating any Value-Context Protocol (VCP) implementation.

## What is Conformance?

A VCP implementation is **conformant** if it passes all test vectors at the claimed conformance level. Each test vector specifies an input, a procedure, and an expected output. If your implementation produces the expected output for every vector, it is conformant.

## Directory Structure

```
conformance/
  identity/           VCP/I - Identity layer
    token_parsing.json
    token_canonicalization.json
  transport/          VCP/T - Transport layer
    content_canonicalization.json
    content_hashing.json
    manifest_canonicalization.json
    signature_verification.json
    bundle_verification.json
  semantics/          VCP/S - Semantics layer
    csm1_parsing.json
    csm1_encoding.json
    persona_resolution.json
    composition.json
  adaptation/         VCP/A - Adaptation layer
    context_encoding.json
    state_machine.json
    messaging.json
  interop/            Cross-implementation
    cross_impl_roundtrip.json
    complete_bundle.json
```

## Conformance Levels

| Level | Layers | Suites Required | Description |
|-------|--------|-----------------|-------------|
| **Minimal** | Identity + Transport | `identity/*`, `transport/*` | Can parse tokens, canonicalize content, verify hashes and signatures |
| **Standard** | + Semantics | + `semantics/*` | Can parse CSM-1 codes, resolve personas, compose constitutions |
| **Full** | + Adaptation + Interop | + `adaptation/*`, `interop/*` | Full protocol support including context encoding, state machine, and cross-implementation roundtrips |

## Fixture Format

Every JSON fixture follows this schema:

```json
{
  "suite": "layer/test_name",
  "version": "1.0.0",
  "description": "Human-readable description",
  "vectors": [
    {
      "id": "unique-id",
      "description": "What this vector tests",
      "input": "...",
      "expected": {
        "valid": true,
        "field": "expected_value"
      }
    }
  ]
}
```

## How to Validate Your Implementation

### Pseudocode

```python
import json

def run_conformance(suite_path, implementation):
    with open(suite_path) as f:
        suite = json.load(f)

    results = []
    for vector in suite["vectors"]:
        try:
            actual = implementation.execute(vector)
            passed = matches_expected(actual, vector["expected"])
            results.append({"id": vector["id"], "passed": passed})
        except Exception as e:
            results.append({"id": vector["id"], "passed": False, "error": str(e)})

    return results

def matches_expected(actual, expected):
    """Compare actual output to expected values.
    Only check fields present in expected; ignore extra fields in actual."""
    for key, value in expected.items():
        if key == "note":
            continue  # Notes are informational, not assertions
        if actual.get(key) != value:
            return False
    return True
```

### Test Vector Types

1. **Direct vectors**: Have `input` and `expected` fields. Parse/process the input and compare to expected.
2. **Procedural vectors**: Have a `procedure` field describing steps to execute (e.g., signature tests that require keypair generation).
3. **Comparison vectors**: Have `input_a` and `input_b` fields with `hashes_equal` or similar comparison expectations.

### Running the Suite

```bash
# Example: run all identity tests
for f in conformance/identity/*.json; do
  your_test_runner --fixture "$f"
done

# Example: run minimal conformance
for f in conformance/identity/*.json conformance/transport/*.json; do
  your_test_runner --fixture "$f"
done

# Example: run full conformance
for f in conformance/**/*.json; do
  your_test_runner --fixture "$f"
done
```

## Key Implementation Notes

### Persona Set: NZGAMDC

The canonical persona set is **NZGAMDC** (6+1):

| Code | Name | Focus |
|------|------|-------|
| N | Nanny | Child safety |
| Z | Sentinel | Security |
| G | Godparent | Ethics |
| A | Ambassador | Professional |
| M | Muse | Creative |
| D | Mediator | Fair resolution |
| C | Custom | User-defined |

Old personas R (Anchor) and H (Hot-Rod) are **no longer valid** persona codes. They remain valid as scope codes.

### Content Canonicalization Rules

1. Normalize line endings: CRLF and CR to LF
2. Strip trailing whitespace from each line
3. Remove trailing empty lines
4. Ensure trailing newline
5. Reject forbidden characters: control chars (except LF, TAB), bidi overrides, zero-width spaces, BOM

### Manifest Canonicalization Rules (JCS / RFC 8785)

1. Remove the `signature` field
2. Sort object keys alphabetically at all nesting levels
3. No whitespace between tokens
4. Arrays preserve element order

### Ed25519 Signature Test Keys

Procedural signature tests use deterministic keypairs generated from seed bytes:
```
seed = [N; 32]  // 32 bytes, all set to value N
keypair = Ed25519::from_seed(seed)
```

## Reporting Issues

If you believe a test vector is incorrect:

1. Check the source specification referenced in the fixture description
2. Verify your implementation against the reference implementations in `python/` and `rust/`
3. File an issue at the vcp-sdk repository with:
   - The fixture file and vector ID
   - Your implementation's output
   - The expected output from the fixture
   - Your reasoning for why the fixture may be wrong

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-15 | Initial conformance suite: identity, transport, semantics, adaptation, interop |

## License

These test fixtures are released under CC BY 4.0. Implementations may use them freely for conformance testing.
