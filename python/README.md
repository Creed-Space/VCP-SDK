# VCP Python SDK

The Python reference implementation for VCP parsing, signed bundles,
orchestration, policy enforcement, privacy filtering, hooks, messaging, and
protocol extensions.

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

## Related surfaces

* [Rust SDK](../rust/)
* [WebMCP SDK](../webmcp/)
* [Conformance fixtures](../conformance/)
* [Compatibility policy](../COMPATIBILITY.md)
