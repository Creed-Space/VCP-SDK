"""
Value-Context Protocol (VCP) Reference Implementation

A protocol for transporting constitutional values to AI systems.
"""

# VCP/A (Adaptation Layer)
# VCP v3.1 Extensions
from . import extensions  # noqa: F401
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
from .negotiation import (  # noqa: F401
    VCPAck,
    VCPHello,
    negotiate,
)
from .orchestrator import Orchestrator, VerificationContext, VerificationError  # noqa: F401
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
    AttestationType,
    Budget,
    Composition,
    CompositionMode,
    Scope,
    Timestamps,
    VerificationResult,
)

from . import metrics  # noqa: F401
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

__version__ = "3.1.0"  # VCP v3.1: extensions + negotiation
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
]
