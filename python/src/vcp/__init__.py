"""
Value-Context Protocol (VCP) Reference Implementation

A protocol for transporting constitutional values to AI systems.
"""

# VCP/A (Adaptation Layer)
# VCP v3.1 Extensions
from . import (
    extensions,  # noqa: F401
    metrics,  # noqa: F401
)
from .adaptation import (  # noqa: F401
    ContextEncoder,
    Dimension,
    StateTracker,
    Transition,
    TransitionSeverity,
    VCPContext,
)
from .audit import AuditEntry, AuditLevel, AuditLogger  # noqa: F401
from .bundle import Bundle, BundleBuilder, Manifest  # noqa: F401
from .enforcement import (  # noqa: F401
    AdherenceLevelPlugin,
    BundleExpiryPlugin,
    DecisionType,
    EnforcementResult,
    EvaluationContext,
    PDPDecision,
    PDPEnforcer,
    PDPPlugin,
    RefusalBoundaryPlugin,
)
from .canonicalize import (  # noqa: F401
    canonicalize_content,
    canonicalize_manifest,
    compute_content_hash,
    verify_content_hash,
)

# VCP/I (Identity Layer)
from .identity import (  # noqa: F401
    NamespaceConfig,
    NamespaceTier,
    Token,
    validate_namespace_access,
)
from .injection import (  # noqa: F401
    InjectionFormat,
    InjectionOptions,
    format_injection,
    format_multi_constitution_injection,
)

# VCP Inter-Agent Messaging
from .messaging import (  # noqa: F401
    VcpMessage,
    check_version_compatibility,
    create_message,
    sign_message,
    validate_message,
    verify_message,
)
from .metrics import (  # noqa: F401
    get_metrics_summary,
    is_prometheus_available,
    track_duration,
    vcp_active_sessions,
    vcp_audit_events_total,
    vcp_bundle_verifications_total,
    vcp_bundle_verify_duration_seconds,
    vcp_compositions_total,
    vcp_context_encode_duration_seconds,
    vcp_context_encodes_total,
    vcp_csm1_parses_total,
    vcp_hook_duration_seconds,
    vcp_hook_executions_total,
    vcp_registry_size,
    vcp_token_lookups_total,
    vcp_transitions_total,
)
from .negotiation import (  # noqa: F401
    VCPAck,
    VCPHello,
    negotiate,
)
from .orchestrator import Orchestrator, VerificationContext, VerificationError  # noqa: F401
from .privacy import (  # noqa: F401
    CONSENT_REQUIRED_FIELDS,
    PRIVATE_FIELDS,
    PUBLIC_FIELDS,
    ConsentRecord,
    ConstraintFlags,
    FilteredContext,
    PlatformManifest,
    PrivacyTier,
    extract_constraint_flags,
    filter_context_for_platform,
    format_field_name,
    generate_privacy_summary,
    get_field_privacy_level,
    get_field_value,
    get_share_preview,
    get_stakeholder_hidden_fields,
    get_stakeholder_visible_fields,
    is_private_field,
)
from .revocation import RevocationChecker, RevocationError, RevocationStatus  # noqa: F401

# VCP/S (Semantics Layer)
from .semantics import (  # noqa: F401
    Composer,
    CompositionConflictError,
    CompositionResult,
    Conflict,
    CSM1Code,
    Persona,
)
from .semantics import Scope as CSM1Scope  # noqa: F401 - aliased to avoid conflict
from .trust import TrustAnchor, TrustConfig  # noqa: F401
from .types import (  # noqa: F401
    AdoptionStatus,
    AttestationType,
    Budget,
    CompetenceClaim,
    CompetenceCriterion,
    CompetenceMeasurementBasis,
    CompetenceProfile,
    Composition,
    CompositionMode,
    EnforcementMode,
    Scope,
    SelfRegulationCommitment,
    TestimonyType,
    Timestamps,
    TokenType,
    VerificationResult,
    apply_decay,
)

__version__ = "4.0.0"  # VCP v4.0: v2.0 spec + robustness layer
__all__ = [
    # Bundle
    "Bundle",
    "BundleBuilder",
    "Manifest",
    # Types
    "VerificationResult",
    "CompositionMode",
    "AttestationType",
    "Timestamps",
    "Budget",
    "Scope",
    "Composition",
    # Orchestrator
    "Orchestrator",
    "VerificationError",
    "VerificationContext",
    # Trust
    "TrustConfig",
    "TrustAnchor",
    # Canonicalize
    "canonicalize_content",
    "canonicalize_manifest",
    "compute_content_hash",
    "verify_content_hash",
    # Injection
    "format_injection",
    "format_multi_constitution_injection",
    "InjectionFormat",
    "InjectionOptions",
    # Audit
    "AuditLogger",
    "AuditEntry",
    "AuditLevel",
    # VCP/I (Identity Layer)
    "Token",
    "NamespaceTier",
    "NamespaceConfig",
    "validate_namespace_access",
    # VCP/S (Semantics Layer)
    "CSM1Code",
    "Persona",
    "CSM1Scope",
    "Composer",
    "CompositionResult",
    "Conflict",
    "CompositionConflictError",
    # VCP/A (Adaptation Layer)
    "VCPContext",
    "ContextEncoder",
    "Dimension",
    "StateTracker",
    "Transition",
    "TransitionSeverity",
    # Revocation
    "RevocationChecker",
    "RevocationStatus",
    "RevocationError",
    # VCP v3.1 Extensions
    "extensions",
    "VCPHello",
    "VCPAck",
    "negotiate",
    # VCP v2.0 Types
    "TokenType",
    "EnforcementMode",
    "TestimonyType",
    "AdoptionStatus",
    # Competence
    "CompetenceCriterion",
    "CompetenceMeasurementBasis",
    "CompetenceClaim",
    "SelfRegulationCommitment",
    "CompetenceProfile",
    "apply_decay",
    # VCP Inter-Agent Messaging
    "VcpMessage",
    "create_message",
    "validate_message",
    "sign_message",
    "verify_message",
    "check_version_compatibility",
    # Privacy field filtering
    "PUBLIC_FIELDS",
    "CONSENT_REQUIRED_FIELDS",
    "PRIVATE_FIELDS",
    "PrivacyTier",
    "ConstraintFlags",
    "FilteredContext",
    "PlatformManifest",
    "ConsentRecord",
    "extract_constraint_flags",
    "filter_context_for_platform",
    "get_stakeholder_visible_fields",
    "get_stakeholder_hidden_fields",
    "get_share_preview",
    "get_field_value",
    "is_private_field",
    "get_field_privacy_level",
    "format_field_name",
    "generate_privacy_summary",
    # PDP Enforcement
    "PDPPlugin",
    "PDPEnforcer",
    "PDPDecision",
    "DecisionType",
    "EnforcementResult",
    "EvaluationContext",
    "RefusalBoundaryPlugin",
    "AdherenceLevelPlugin",
    "BundleExpiryPlugin",
]
