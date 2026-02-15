"""
VCP Bundle Module

Represents a signed constitutional bundle.
"""

import json
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .canonicalize import canonicalize_manifest, compute_content_hash
from .types import (
    AttestationType,
    Budget,
    BundleInfo,
    Composition,
    CompositionMode,
    Issuer,
    SafetyAttestation,
    Scope,
    Signature,
    Timestamps,
)


@dataclass
class Manifest:
    """VCP Bundle Manifest."""

    vcp_version: str
    bundle: BundleInfo
    issuer: Issuer
    timestamps: Timestamps
    budget: Budget
    safety_attestation: SafetyAttestation
    signature: Signature
    scope: Scope | None = None
    composition: Composition | None = None
    revocation: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert manifest to dictionary."""
        result = {
            "vcp_version": self.vcp_version,
            "bundle": {
                "id": self.bundle.id,
                "version": self.bundle.version,
                "content_hash": self.bundle.content_hash,
                "content_encoding": self.bundle.content_encoding,
                "content_format": self.bundle.content_format,
            },
            "issuer": {
                "id": self.issuer.id,
                "public_key": self.issuer.public_key,
                "key_id": self.issuer.key_id,
            },
            "timestamps": {
                "iat": self.timestamps.iat.isoformat() + "Z",
                "nbf": self.timestamps.nbf.isoformat() + "Z",
                "exp": self.timestamps.exp.isoformat() + "Z",
                "jti": self.timestamps.jti,
            },
            "budget": {
                "token_count": self.budget.token_count,
                "tokenizer": self.budget.tokenizer,
                "max_context_share": self.budget.max_context_share,
            },
            "safety_attestation": {
                "auditor": self.safety_attestation.auditor,
                "auditor_key_id": self.safety_attestation.auditor_key_id,
                "reviewed_at": self.safety_attestation.reviewed_at.isoformat() + "Z",
                "attestation_type": self.safety_attestation.attestation_type.value,
                "signature": self.safety_attestation.signature,
            },
            "signature": {
                "algorithm": self.signature.algorithm,
                "value": self.signature.value,
                "signed_fields": self.signature.signed_fields,
            },
        }

        if self.scope:
            result["scope"] = {
                k: v
                for k, v in {
                    "model_families": self.scope.model_families or None,
                    "purposes": self.scope.purposes or None,
                    "environments": self.scope.environments or None,
                    "audiences": self.scope.audiences or None,
                    "regions": self.scope.regions or None,
                }.items()
                if v
            }

        if self.composition:
            result["composition"] = {
                "layer": self.composition.layer,
                "mode": self.composition.mode.value,
                "conflicts_with": self.composition.conflicts_with,
                "requires": self.composition.requires,
            }

        if self.revocation:
            result["revocation"] = self.revocation

        if self.metadata:
            result["metadata"] = self.metadata

        if self.signature.threshold:
            result["signature"]["threshold"] = self.signature.threshold
        if self.signature.signers:
            result["signature"]["signers"] = self.signature.signers

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Manifest":
        """Parse manifest from dictionary."""
        bundle = BundleInfo(
            id=data["bundle"]["id"],
            version=data["bundle"]["version"],
            content_hash=data["bundle"]["content_hash"],
            content_encoding=data["bundle"].get("content_encoding", "utf-8"),
            content_format=data["bundle"].get("content_format", "text/markdown"),
        )

        issuer = Issuer(
            id=data["issuer"]["id"],
            public_key=data["issuer"]["public_key"],
            key_id=data["issuer"]["key_id"],
        )

        timestamps = Timestamps(
            iat=datetime.fromisoformat(data["timestamps"]["iat"].rstrip("Z")),
            nbf=datetime.fromisoformat(data["timestamps"]["nbf"].rstrip("Z")),
            exp=datetime.fromisoformat(data["timestamps"]["exp"].rstrip("Z")),
            jti=data["timestamps"]["jti"],
        )

        budget = Budget(
            token_count=data["budget"]["token_count"],
            tokenizer=data["budget"]["tokenizer"],
            max_context_share=data["budget"].get("max_context_share", 0.25),
        )

        safety_attestation = SafetyAttestation(
            auditor=data["safety_attestation"]["auditor"],
            auditor_key_id=data["safety_attestation"]["auditor_key_id"],
            reviewed_at=datetime.fromisoformat(data["safety_attestation"]["reviewed_at"].rstrip("Z")),
            attestation_type=AttestationType(data["safety_attestation"]["attestation_type"]),
            signature=data["safety_attestation"]["signature"],
        )

        signature = Signature(
            algorithm=data["signature"]["algorithm"],
            value=data["signature"]["value"],
            signed_fields=data["signature"]["signed_fields"],
            threshold=data["signature"].get("threshold"),
            signers=data["signature"].get("signers"),
        )

        scope = None
        if "scope" in data:
            scope = Scope(
                model_families=data["scope"].get("model_families", []),
                purposes=data["scope"].get("purposes", []),
                environments=data["scope"].get("environments", []),
                audiences=data["scope"].get("audiences", []),
                regions=data["scope"].get("regions", []),
            )

        composition = None
        if "composition" in data:
            composition = Composition(
                layer=data["composition"].get("layer", 2),
                mode=CompositionMode(data["composition"].get("mode", "extend")),
                conflicts_with=data["composition"].get("conflicts_with", []),
                requires=data["composition"].get("requires", []),
            )

        return cls(
            vcp_version=data["vcp_version"],
            bundle=bundle,
            issuer=issuer,
            timestamps=timestamps,
            budget=budget,
            safety_attestation=safety_attestation,
            signature=signature,
            scope=scope,
            composition=composition,
            revocation=data.get("revocation"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Bundle:
    """VCP Bundle - manifest and content together."""

    manifest: Manifest
    content: str

    def to_dict(self) -> dict[str, Any]:
        """Convert bundle to dictionary."""
        return {
            "manifest": self.manifest.to_dict(),
            "content": self.content,
        }

    def to_json(self, indent: int | None = 2) -> str:
        """Serialize bundle to JSON."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Bundle":
        """Parse bundle from dictionary."""
        return cls(
            manifest=Manifest.from_dict(data["manifest"]),
            content=data["content"],
        )

    @classmethod
    def from_json(cls, json_str: str) -> "Bundle":
        """Parse bundle from JSON string."""
        return cls.from_dict(json.loads(json_str))


class BundleBuilder:
    """Builder for creating VCP bundles."""

    def __init__(self, bundle_id: str, version: str):
        self.bundle_id = bundle_id
        self.version = version
        self.content: str | None = None
        self.issuer_id: str | None = None
        self.issuer_public_key: str | None = None
        self.issuer_key_id: str | None = None
        self.auditor: str | None = None
        self.auditor_key_id: str | None = None
        self.attestation_type = AttestationType.INJECTION_SAFE
        self.tokenizer = "cl100k_base"
        self.max_context_share = 0.25
        self.scope: Scope | None = None
        self.composition: Composition | None = None
        self.revocation: dict[str, Any] | None = None
        self.metadata: dict[str, Any] = {}
        self.expires_days = 7

    def with_content(self, content: str) -> "BundleBuilder":
        """Set constitution content."""
        self.content = content
        return self

    def with_issuer(self, issuer_id: str, public_key: str, key_id: str) -> "BundleBuilder":
        """Set issuer information."""
        self.issuer_id = issuer_id
        self.issuer_public_key = public_key
        self.issuer_key_id = key_id
        return self

    def with_auditor(
        self,
        auditor: str,
        key_id: str,
        attestation_type: AttestationType = AttestationType.INJECTION_SAFE,
    ) -> "BundleBuilder":
        """Set safety auditor information."""
        self.auditor = auditor
        self.auditor_key_id = key_id
        self.attestation_type = attestation_type
        return self

    def with_budget(
        self,
        tokenizer: str = "cl100k_base",
        max_context_share: float = 0.25,
    ) -> "BundleBuilder":
        """Set token budget parameters."""
        self.tokenizer = tokenizer
        self.max_context_share = max_context_share
        return self

    def with_scope(self, scope: Scope) -> "BundleBuilder":
        """Set scope binding."""
        self.scope = scope
        return self

    def with_composition(self, composition: Composition) -> "BundleBuilder":
        """Set composition settings."""
        self.composition = composition
        return self

    def with_revocation(self, check_uri: str, crl_uri: str | None = None) -> "BundleBuilder":
        """Set revocation URIs."""
        self.revocation = {"check_uri": check_uri}
        if crl_uri:
            self.revocation["crl_uri"] = crl_uri
        return self

    def with_metadata(self, metadata: dict[str, Any]) -> "BundleBuilder":
        """Set custom metadata."""
        self.metadata = metadata
        return self

    def with_expires_days(self, days: int) -> "BundleBuilder":
        """Set expiration in days from now."""
        self.expires_days = days
        return self

    def build(
        self,
        sign_manifest: Callable,  # (manifest_bytes) -> str
        sign_attestation: Callable,  # (attestation_bytes) -> str
        count_tokens: Callable | None = None,  # (content, tokenizer) -> int
    ) -> Bundle:
        """
        Build the bundle with signatures.

        Args:
            sign_manifest: Function to sign manifest bytes, returns base64 signature
            sign_attestation: Function to sign attestation bytes, returns base64 signature
            count_tokens: Optional function to count tokens

        Returns:
            Complete signed Bundle
        """
        if not self.content:
            raise ValueError("Content is required")
        if not self.issuer_id or not self.issuer_public_key or not self.issuer_key_id:
            raise ValueError("Issuer information is required")
        if not self.auditor or not self.auditor_key_id:
            raise ValueError("Auditor information is required")

        now = datetime.utcnow()
        from datetime import timedelta

        # Compute content hash
        content_hash = compute_content_hash(self.content)

        # Count tokens
        if count_tokens:
            token_count = count_tokens(self.content, self.tokenizer)
        else:
            # Rough estimate: ~4 chars per token
            token_count = len(self.content) // 4

        # Build attestation and sign it
        attestation_data = {
            "auditor": self.auditor,
            "auditor_key_id": self.auditor_key_id,
            "reviewed_at": now.isoformat() + "Z",
            "attestation_type": self.attestation_type.value,
            "content_hash": content_hash,
        }
        attestation_bytes = json.dumps(attestation_data, sort_keys=True).encode()
        attestation_sig = sign_attestation(attestation_bytes)

        # Build manifest without signature
        manifest_dict: dict[str, Any] = {
            "vcp_version": "1.0",
            "bundle": {
                "id": self.bundle_id,
                "version": self.version,
                "content_hash": content_hash,
                "content_encoding": "utf-8",
                "content_format": "text/markdown",
            },
            "issuer": {
                "id": self.issuer_id,
                "public_key": self.issuer_public_key,
                "key_id": self.issuer_key_id,
            },
            "timestamps": {
                "iat": now.isoformat() + "Z",
                "nbf": now.isoformat() + "Z",
                "exp": (now + timedelta(days=self.expires_days)).isoformat() + "Z",
                "jti": str(uuid.uuid4()),
            },
            "budget": {
                "token_count": token_count,
                "tokenizer": self.tokenizer,
                "max_context_share": self.max_context_share,
            },
            "safety_attestation": {
                "auditor": self.auditor,
                "auditor_key_id": self.auditor_key_id,
                "reviewed_at": now.isoformat() + "Z",
                "attestation_type": self.attestation_type.value,
                "signature": f"base64:{attestation_sig}",
            },
        }

        if self.scope:
            manifest_dict["scope"] = {
                k: v
                for k, v in {
                    "model_families": self.scope.model_families or None,
                    "purposes": self.scope.purposes or None,
                    "environments": self.scope.environments or None,
                }.items()
                if v
            }

        if self.composition:
            manifest_dict["composition"] = {
                "layer": self.composition.layer,
                "mode": self.composition.mode.value,
                "conflicts_with": self.composition.conflicts_with,
                "requires": self.composition.requires,
            }

        if self.revocation:
            manifest_dict["revocation"] = self.revocation

        if self.metadata:
            manifest_dict["metadata"] = self.metadata

        # Determine signed fields
        signed_fields = [
            "vcp_version",
            "bundle",
            "issuer",
            "timestamps",
            "budget",
            "safety_attestation",
        ]
        if self.scope:
            signed_fields.append("scope")
        if self.composition:
            signed_fields.append("composition")
        if self.revocation:
            signed_fields.append("revocation")
        if self.metadata:
            signed_fields.append("metadata")

        # Add signature placeholder for canonicalization
        manifest_dict["signature"] = {
            "algorithm": "ed25519",
            "value": "",
            "signed_fields": signed_fields,
        }

        # Canonicalize and sign
        canonical = canonicalize_manifest(manifest_dict)
        sig = sign_manifest(canonical)
        manifest_dict["signature"]["value"] = f"base64:{sig}"

        # Build final manifest
        manifest = Manifest.from_dict(manifest_dict)

        return Bundle(manifest=manifest, content=self.content)
