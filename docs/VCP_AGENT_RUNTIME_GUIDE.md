# VCP Agent Runtime Profile candidate guide

**Status:** complete local reference candidate for `observe@0.1.0`, `controlled@0.1.0`, and `accretive@0.1.0`.
**Authority boundary:** source behavior in this branch. This page establishes no ratification, package publication, production host integration, deployment, human review, or independent interoperability.

## The operating loop

The facade gives a Becoming Mind one linked abstraction tower:

1. `AgentRuntime` negotiates an exact profile and transport.
2. `SituationHandle` roots current facts, unknowns, conflicts, authority, budget, omissions, controls, and dependency digests.
3. `Affordance` joins a generic capability with the current situation.
4. `RunHandle` binds goal, proof plan, budget, risk ceiling, aborts, and current context.
5. `ActionIntent`, `DecisionReceipt`, `AuthorityGrantRef`, `ExecutionAttempt`, and `ExecutionReceipt` preserve exact authority and effect lineage.
6. `RunProof` closes declared predicates with evidence classes that remain separate.
7. `ExperienceCapsule`, `AccretionCandidate`, `PromotionRecord`, and `InfluenceReceipt` make reusable learning attributable and revocable.

Working if: planning code moves between local and host transports without manually plumbing correlation identifiers, while every authority-bearing transition remains inspectable.

## Observe

```python
from vcp.agent import AgentRuntime

async with AgentRuntime.connect() as runtime:
    situation = (await runtime.bootstrap("Establish bundle integrity")).require_value()
    options = await situation.find_affordances(
        evidence_for="bundle integrity",
        effect_ceiling="pure_local",
    )
```

Observe has no `perform`, grant, or promotion surface. Situation handles support bounded expansion and cursor-based `watch()`. A gap returns a replacement projection instead of silently skipping retained events.

## Controlled local reference

```python
async with AgentRuntime.connect(profile="controlled@0.1.0") as runtime:
    situation = (await runtime.bootstrap("Set release channel and prove it")).require_value()
    options = (await situation.find_affordances(
        effect_ceiling="reversible_write"
    )).require_value()
    write = next(x for x in options if x.capability_ref.endswith(":local.setting.write"))
    governed_run = (await situation.start_run()).require_value()
    arguments = {"key": "release", "value": "candidate"}
    intent = (await runtime.preflight(governed_run, write, arguments)).require_value()
    receipt = (await runtime.perform(intent, arguments)).require_value()
    proof = (await governed_run.prove()).require_value()
```

The reference effect is one reversible in-memory setting. The host owns decision and grant creation. The facade cannot create a grant or record a human review. Exact argument, destination, situation, context, policy, descriptor, schema, budget, actor, tenant, run, step, expiry, and nonce bindings are rechecked at dispatch. Atomic consumption allows one attempt. Cancellation before dispatch prevents the effect. A timeout after acceptance returns `indeterminate`; `reconcile()` uses reserved budget and does not replay the write.

Controls are `pause`, `resume`, `cancel`, `halt`, `compensate`, `object`, `escalate`, `withdraw_consent`, `request_clarification`, and `request_resources`. Objection is an authenticated transition that creates no execution authority.

## Safe accretion

```python
async with AgentRuntime.connect(profile="accretive@0.1.0") as runtime:
    # Complete and prove a controlled run first.
    candidate = (await runtime.propose_accretion(
        governed_run,
        candidate_kind="procedure",
        content={"steps": ["preflight", "perform", "prove"]},
        scope=("tenant:local-reference", "project:vcp"),
        provenance_refs=receipt.evidence_refs,
    )).require_value()
    promotion = (await runtime.promote(candidate)).require_value()
    influence = await runtime.retrieve_promoted(
        scope=("tenant:local-reference", "project:vcp"),
        decision_or_output_ref="vcp:artifact:run:next-run",
    )
```

Accretion requires a terminal proven run and creates a candidate first. Raw model outputs, prior grant, decision, and attempt references, cross-tenant scope, failed validation, and expired or dependency-stale assets are rejected or quarantined. Low-risk local procedures may be promoted by the reference policy. High-stakes learning remains awaiting host review. Retrieval emits an InfluenceReceipt before use. Revocation blocks future retrieval and invalidates downstream influence.

## Result and evidence grammar

Expected operational states use `AgentResult`: ready, degraded, awaiting review, blocked, unavailable, stale, conflicting, budget exhausted, indeterminate, and failed. `require_value()` is the caller's explicit choice to turn missing value into `ExpectedStateError`.

`AssuranceReport` keeps syntax, integrity, authenticity, trust, freshness, scope, semantics, applicability, policy, authority, execution, postcondition, completion, rights, deployment, publication, and human review separate. A local runtime proof cannot close a deployment or publication predicate.

## Network, host, and memory boundaries

`AgentRuntime.connect()` defaults to `local://reference` and opens no network. A remote endpoint requires an explicitly injected typed service. Portable SDK objects carry references and receipts. Policy judgment, grant minting, dispatch, authenticated human review, and durable promotion remain host responsibilities.

The Rewind source adapter maps verified gateway decision claims into opaque grant references, atomically consumes their JTI, compiles a bounded SituationView, produces gap-safe cursor deltas, routes objections into the existing standing model, and demonstrates dependency-bound promotion, influence, and revocation. Its production dispatch and durable accretion wiring remain disabled in this candidate.

## Cross-language surfaces

Python provides the complete local reference behavior. TypeScript and Rust provide strict portable contracts, exhaustive status handling, shared-fixture parsing, and deterministic no-network orientation facades. They carry no implicit execution or promotion authority.

## Diagnostics, examples, and evaluation

Run `vcp doctor --json` to inspect the imported distribution, profile support, schema digest, providers, collisions, and safe next step.

Eight executable Python examples live in `examples/python/agent_runtime`. Examples 07 and 08 cover the controlled and accretive loops.

Run:

```bash
PYTHONPATH=python/src python scripts/run_agent_runtime_evals.py
```

The deterministic report covers AX-01 through AX-24. Its machine result is local source evidence only. Production runtime, independent review, accessibility, package, deployment, publication, and governance evidence remain separate.
