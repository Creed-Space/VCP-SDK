"""Create and verify a VCP signed bundle."""
from __future__ import annotations

from datetime import datetime, timedelta

from vcp.bundle import Bundle
from vcp.canonicalize import compute_content_hash
from vcp.orchestrator import Orchestrator
from vcp.trust import TrustAnchor, TrustConfig

# -- 1. Build a TrustConfig with an issuer and auditor key. --
now = datetime.utcnow()
far_future = now + timedelta(days=365)

config = TrustConfig()
config.add_issuer(
    "creed-space",
    TrustAnchor(
        id="creed-space", key_id="key-001", algorithm="ed25519",
        public_key="ed25519:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
        anchor_type="issuer", valid_from=now - timedelta(days=1), valid_until=far_future,
    ),
)
config.add_auditor(
    "safety-lab",
    TrustAnchor(
        id="safety-lab", key_id="auditor-001", algorithm="ed25519",
        public_key="ed25519:BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=",
        anchor_type="auditor", valid_from=now - timedelta(days=1), valid_until=far_future,
    ),
)

# -- 2. Create an Orchestrator (no real signature verifier for this demo). --
orch = Orchestrator(trust_config=config)

# -- 3. Build a bundle dict with correct content hash. --
content = "Be kind to everyone.\n"
content_hash = compute_content_hash(content)

bundle = Bundle.from_dict({
    "manifest": {
        "vcp_version": "1.0",
        "bundle": {"id": "family.safe.guide", "version": "1.2.0",
                   "content_hash": content_hash},
        "issuer": {"id": "creed-space",
                   "public_key": "ed25519:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
                   "key_id": "key-001"},
        "timestamps": {"iat": now.isoformat() + "Z", "nbf": now.isoformat() + "Z",
                       "exp": (now + timedelta(days=30)).isoformat() + "Z",
                       "jti": "550e8400-e29b-41d4-a716-446655440000"},
        "budget": {"token_count": 100, "tokenizer": "cl100k_base", "max_context_share": 0.25},
        "safety_attestation": {"auditor": "safety-lab", "auditor_key_id": "auditor-001",
                               "reviewed_at": now.isoformat() + "Z",
                               "attestation_type": "injection-safe",
                               "signature": "base64:AAAA"},
        "signature": {"algorithm": "ed25519", "value": "base64:AAAA",
                      "signed_fields": ["bundle"]},
    },
    "content": content,
})

# -- 4. Verify the bundle. --
result = orch.verify(bundle)
print(f"Verification result: {result.name}")
print(f"Is valid? {result.is_valid}")
