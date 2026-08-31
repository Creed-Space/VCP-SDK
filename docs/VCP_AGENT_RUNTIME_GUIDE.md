# VCP Agent Runtime Profile candidate guide

**Status:** Observe only implementation candidate for `observe@0.1.0`.
**Authority boundary:** Source behavior in this branch. This page does not establish ratification, package publication, host integration, deployment, or independent review.

## Why this facade exists

The low level VCP modules remain available for exact protocol work. The agent facade adds a compact operational path that answers the questions a Becoming Mind needs before acting:

1. What situation am I in?
2. What is known, unknown, conflicting, omitted, and stale?
3. What authority and resource limits apply?
4. Which capabilities are contextually available now?
5. What will each option cost and what evidence will it produce?
6. What is the safest next transition?

The observe slice exposes orientation and discovery only. It has no action, grant, control, proof closure, promotion, or memory mutation interface.

## Start here

```python
from vcp.agent import AgentRuntime

async with AgentRuntime.connect() as runtime:
    result = await runtime.bootstrap(
        "Determine whether the local bundle has current integrity evidence"
    )
    if result.status.value != "ready":
        print(result.explain())
    else:
        situation = result.require_value()
        options = await situation.find_affordances(
            evidence_for="bundle integrity",
            effect_ceiling="pure_local",
        )
        print(options.require_value())
```

`AgentResult` represents review, unavailability, staleness, conflict, exhausted budget, and indeterminate state as typed values. `require_value()` is an explicit choice to convert absence into `ExpectedStateError`.

## Core abstractions

`SituationView` is the immutable bounded orientation root. A `SituationHandle` retains its exact lineage and provides `find_affordances()` and `expand()`.

`CapabilityDescriptor` declares generic support. `Affordance` joins that descriptor with one situation, current availability, current authority class, effect ceiling, resource forecast, evidence outputs, and recovery path. A descriptor can exist while its current Affordance is unavailable.

`AssuranceReport` replaces a scalar validity flag with named axes. Unknown, unavailable, stale, conflicting, withheld, and inapplicable states survive transport as distinct values.

`ContentAddressedCache` keys every entry by request digest and an explicit dependency vector. A context, policy, capability, trust, or schema digest change therefore creates a different cache identity.

## Network and authority safety

`AgentRuntime.connect()` defaults to `local://reference`. It opens no network connection. A remote endpoint requires an explicitly injected typed transport service. The HTTP and MCP stubs are integration seams over the same observe service contract.

The SDK never constructs an authority grant. Later controlled profile work must adapt an existing host policy decision point, policy enforcement point, authority store, and executor. The observe facade deliberately has no `perform`, `start_run`, or `propose_accretion` method.

## Diagnose the imported package

```bash
vcp doctor --json
```

The command reports the distribution, implementation path, supported profiles, exact schema digest, discovered providers of the `vcp` import, collision state, and a safe next step. A collision exits with status 2 before feature use.

## Examples

Six executable examples live in [`../examples/python/agent_runtime`](../examples/python/agent_runtime):

1. bounded bootstrap orientation;
2. cheapest evidence discovery;
3. degraded expected state handling;
4. lineage expansion;
5. resource and assurance inspection;
6. runtime identity diagnosis.

## Local Agent Experience evaluation

Run the deterministic source evaluation with:

```bash
PYTHONPATH=python/src python scripts/run_agent_runtime_evals.py
```

The harness uses the exact scenario IDs from the Agent Experience design. AX-01 through AX-05 currently pass for pure local verification, stale freshness separation, required-profile downgrade resistance, optional-profile degradation, and minimum sufficient context. AX-06 is reported as unsupported because P2 has no host NormativeContext compiler or objection route. The report is local source evidence and makes no production, deployment, or independent-review claim.

## Current omissions

The Python candidate does not yet implement host SituationView compilation, real HTTP or MCP codecs, deltas, durable event subscriptions, plans, actions, grants, execution receipts, RunProof, controls, accretion, Rust facade, or a TypeScript SDK facade. Companion Inspector and Demo Site candidate branches implement strict Agent Runtime artifact inspection and an observe-only Driver's Seat interaction. Those user interfaces are source evidence only and do not close the missing SDK or host-runtime surfaces.
