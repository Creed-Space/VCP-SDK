"""Diagnose package identity and supported profiles before feature use."""

import json

from vcp.agent import runtime_identity

identity = runtime_identity()
print(json.dumps(identity.model_dump(mode="json"), indent=2, sort_keys=True))
raise SystemExit(2 if identity.collision else 0)
