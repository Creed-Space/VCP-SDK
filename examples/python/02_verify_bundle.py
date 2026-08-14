"""Create and cryptographically verify a VCP signed bundle."""

from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from vcp.bundle import BundleBuilder
from vcp.orchestrator import Orchestrator
from vcp.trust import TrustAnchor, TrustConfig
from vcp.types import VerificationResult


def public_key_value(key: Ed25519PrivateKey) -> str:
    raw = key.public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
    return f"ed25519:{base64.b64encode(raw).decode('ascii')}"


def signer(key: Ed25519PrivateKey):
    def sign(payload: bytes) -> str:
        return base64.b64encode(key.sign(payload)).decode("ascii")

    return sign


issuer_key = Ed25519PrivateKey.generate()
auditor_key = Ed25519PrivateKey.generate()
issuer_public = public_key_value(issuer_key)
auditor_public = public_key_value(auditor_key)

bundle = (
    BundleBuilder("family.safe.guide", "1.2.0")
    .with_content("Be kind to everyone.\n")
    .with_issuer("example-issuer", issuer_public, "issuer-key-1")
    .with_auditor("example-auditor", "auditor-key-1")
    .build(
        sign_manifest=signer(issuer_key),
        sign_attestation=signer(auditor_key),
    )
)

now = datetime.now(timezone.utc)
trust = TrustConfig()
trust.add_issuer(
    "example-issuer",
    TrustAnchor(
        id="example-issuer",
        key_id="issuer-key-1",
        algorithm="ed25519",
        public_key=issuer_public,
        anchor_type="issuer",
        valid_from=now - timedelta(days=1),
        valid_until=now + timedelta(days=365),
    ),
)
trust.add_auditor(
    "example-auditor",
    TrustAnchor(
        id="example-auditor",
        key_id="auditor-key-1",
        algorithm="ed25519",
        public_key=auditor_public,
        anchor_type="auditor",
        valid_from=now - timedelta(days=1),
        valid_until=now + timedelta(days=365),
    ),
)

result = Orchestrator(trust).verify(bundle)
if result is not VerificationResult.VALID:
    raise SystemExit(f"Bundle verification failed: {result.name}")
print(f"Verification result: {result.name}")
