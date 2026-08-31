# VCP Python SDK

The Python project-maintained implementation for VCP parsing, signed bundles,
orchestration, policy enforcement, privacy filtering, hooks, messaging, and
protocol extensions.

## Agent Runtime Profile candidate

The observe-only `vcp.agent` facade provides a bounded `SituationView`, contextual `Affordance` discovery, explicit assurance axes, resource forecasts, typed expected states, lineage expansion, and runtime identity diagnostics. It opens no network connection in local mode and exposes no action or memory mutation interface.

```python
from vcp.agent import AgentRuntime

async with AgentRuntime.connect() as runtime:
    situation = (await runtime.bootstrap("Establish bundle integrity")).require_value()
    options = await situation.find_affordances(evidence_for="bundle integrity")
```

Run `vcp doctor --json` before feature use to detect distribution collisions. See [`../docs/VCP_AGENT_RUNTIME_GUIDE.md`](../docs/VCP_AGENT_RUNTIME_GUIDE.md) for the exact candidate boundary and six executable examples.

## Install for development

Python 3.10 or newer is required.

**Publication state:** source-only candidate. No PyPI release is currently
claimed. Commands below operate on this checkout.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
```

The package distribution is named `value-context-protocol`. Python imports use
the `vcp` namespace.

## Verify the package

```bash
python -m pytest -q
python -m ruff check src tests
python -m ruff format --check src tests
python -m mypy src/vcp
python -m build
python -m pip_audit
```

## Minimal usage

```python
from vcp.identity import Token
from vcp.semantics.csm1 import CSM1Code

token = Token.parse("family.safe.guide@1.2.0")
profile = CSM1Code.parse("N5+F+E")
print(token.full)
print(profile.encode())
```

Real Ed25519 bundle construction and verification are demonstrated in
[`../examples/python/02_verify_bundle.py`](../examples/python/02_verify_bundle.py).
The full pipeline example verifies before preparing model-context injection.

## Optional features

```bash
python -m pip install -e '.[server]'
python -m pip install -e '.[mcp]'
```

Install the MCP extra and run the packaged stdio server with:

```bash
python -m pip install -e '.[mcp]'
vcp-mcp-server
```

The historical host API adapter is archived outside the package source and is
excluded from distributions. Development and CI use the committed lock file. Update it
deliberately through the documented command in
[`../CONTRIBUTING.md`](../CONTRIBUTING.md).

Signed-skill manifests are written as private workspace state by default. On
POSIX platforms the atomic temporary file and installed `manifest.json` use
mode `0600`. Windows does not provide equivalent POSIX mode semantics, so the
application must protect the containing directory with its native access
controls. A separately published manifest is a deliberate export and should
receive only the permissions required by its publication target.

## Related surfaces

* [Rust SDK](../rust/)
* [WebMCP SDK](../webmcp/)
* [Conformance fixtures](../conformance/)
* [Compatibility policy](../COMPATIBILITY.md)
