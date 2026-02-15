"""End-to-end: parse token, build context, verify bundle, format injection."""
from __future__ import annotations

from datetime import datetime, timedelta

from vcp.adaptation.context import ContextEncoder
from vcp.bundle import Bundle
from vcp.canonicalize import compute_content_hash
from vcp.identity import Token
from vcp.injection import InjectionFormat, InjectionOptions, format_injection
from vcp.orchestrator import Orchestrator
from vcp.trust import TrustAnchor, TrustConfig

# -- 1. Parse the identity token. --
token = Token.parse("family.safe.guide@1.2.0")
print(f"Constitution: {token.full}")

# -- 2. Encode situational context. --
encoder = ContextEncoder()
ctx = encoder.encode(time="morning", space="home", company="children")
print(f"Context: {ctx.encode()}")

# -- 3. Set up trust and build a minimal bundle. --
now = datetime.utcnow()
far_future = now + timedelta(days=365)

config = TrustConfig()
config.add_issuer(
    "creed-space",
    TrustAnchor(
        id="creed-space", key_id="k1", algorithm="ed25519",
        public_key="ed25519:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
        anchor_type="issuer", valid_from=now - timedelta(days=1), valid_until=far_future,
    ),
)
config.add_auditor(
    "safety-lab",
    TrustAnchor(
        id="safety-lab", key_id="a1", algorithm="ed25519",
        public_key="ed25519:BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=",
        anchor_type="auditor", valid_from=now - timedelta(days=1), valid_until=far_future,
    ),
)

content = "Always use age-appropriate language.\nNever discuss weapons.\n"
content_hash = compute_content_hash(content)

bundle = Bundle.from_dict({
    "manifest": {
        "vcp_version": "1.0",
        "bundle": {"id": "family.safe.guide", "version": "1.2.0",
                   "content_hash": content_hash},
        "issuer": {"id": "creed-space",
                   "public_key": "ed25519:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
                   "key_id": "k1"},
        "timestamps": {"iat": now.isoformat() + "Z", "nbf": now.isoformat() + "Z",
                       "exp": (now + timedelta(days=30)).isoformat() + "Z",
                       "jti": "550e8400-e29b-41d4-a716-446655440001"},
        "budget": {"token_count": 50, "tokenizer": "cl100k_base"},
        "safety_attestation": {"auditor": "safety-lab", "auditor_key_id": "a1",
                               "reviewed_at": now.isoformat() + "Z",
                               "attestation_type": "injection-safe",
                               "signature": "base64:AAAA"},
        "signature": {"algorithm": "ed25519", "value": "base64:AAAA",
                      "signed_fields": ["bundle"]},
    },
    "content": content,
})

# -- 4. Verify the bundle. --
orch = Orchestrator(trust_config=config)
result = orch.verify(bundle)
print(f"Verification: {result.name} (valid={result.is_valid})")

# -- 5. Format for injection into a model's context window. --
injection = format_injection(
    bundle,
    options=InjectionOptions(format=InjectionFormat.HEADER_DELIMITED),
)
print(f"\n--- Injection output ({len(injection)} chars) ---")
print(injection[:200], "..." if len(injection) > 200 else "")
