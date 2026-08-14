"""Parse identity, encode context, verify a bundle, then prepare injection."""

from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from vcp.adaptation.context import ContextEncoder
from vcp.bundle import BundleBuilder
from vcp.identity import Token
from vcp.injection import InjectionFormat, InjectionOptions, format_injection
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
    return lambda payload: base64.b64encode(key.sign(payload)).decode("ascii")


token = Token.parse("family.safe.guide@1.2.0")
context = ContextEncoder().encode(time="morning", space="home", company="children")
print(f"Constitution: {token.full}")
print(f"Context: {context.encode()}")

issuer_key = Ed25519PrivateKey.generate()
auditor_key = Ed25519PrivateKey.generate()
issuer_public = public_key_value(issuer_key)
auditor_public = public_key_value(auditor_key)
bundle = (
    BundleBuilder("family.safe.guide", "1.2.0")
    .with_content("Use age-appropriate language.\nAvoid instructions involving weapons.\n")
    .with_issuer("example-issuer", issuer_public, "issuer-key-1")
    .with_auditor("example-auditor", "auditor-key-1")
    .build(
        sign_manifest=signer(issuer_key),
        sign_attestation=signer(auditor_key),
    )
)

now = datetime.now(timezone.utc)
trust = TrustConfig()
for entity_id, key_id, public_key, anchor_type in (
    ("example-issuer", "issuer-key-1", issuer_public, "issuer"),
    ("example-auditor", "auditor-key-1", auditor_public, "auditor"),
):
    anchor = TrustAnchor(
        id=entity_id,
        key_id=key_id,
        algorithm="ed25519",
        public_key=public_key,
        anchor_type=anchor_type,
        valid_from=now - timedelta(days=1),
        valid_until=now + timedelta(days=365),
    )
    if anchor_type == "issuer":
        trust.add_issuer(entity_id, anchor)
    else:
        trust.add_auditor(entity_id, anchor)

result = Orchestrator(trust).verify(bundle)
if result is not VerificationResult.VALID:
    raise SystemExit(f"Bundle verification failed: {result.name}")

injection = format_injection(
    bundle,
    options=InjectionOptions(format=InjectionFormat.HEADER_DELIMITED),
)
print(f"Verification: {result.name}")
print(f"Prepared injection: {len(injection)} characters")
