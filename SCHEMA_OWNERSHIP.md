# Schema Ownership and Synchronization

VCP-Spec is the canonical source for protocol schemas. VCP-SDK carries reviewed
copies only where runtime packages or tests need them.

## Exact synchronized copies

These files must be byte-identical between the selected Spec and SDK commits:

* `vcp-adaptation-context.schema.json`
* `vcp-agent-runtime-profile-v0.1.schema.json`
* `vcp-identity-token.schema.json`
* `vcp-manifest-v1.schema.json`
* `vcp-semantics-csm1.schema.json`

Check them with:

```bash
python3 scripts/check_schema_sync.py --spec /path/to/VCP-Spec --sdk .
```

## Intentionally one-sided schemas

| Owner | Schema | Reason |
|:---|:---|:---|
| VCP-Spec | `vcp-capability-handshake.schema.json` | Normative capability handshake |
| VCP-Spec | `vcp-messaging-v1.2.schema.json` | Published messaging baseline |
| VCP-SDK | `vcp-manifest-v2.schema.json` | SDK implementation candidate |
| VCP-SDK | `vcp-messaging-v2.0.schema.json` | SDK implementation candidate |

An intentional split is a compatibility boundary, not permission for silent
drift. Any ownership change requires a VEP or a recorded cross-repository
decision, fixtures, and compatibility notes.

## Update procedure

1. Change the canonical Spec source and its valid and invalid fixtures.
2. Pass Spec validation.
3. Copy the exact reviewed file into the SDK.
4. Pass strict schema compilation, schema synchronization, conformance checks,
   and all affected language tests.
5. Record both commit hashes in release evidence.
