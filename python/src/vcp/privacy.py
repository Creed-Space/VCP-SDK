"""
VCP Privacy Filtering

Core privacy mechanism for filtering context before sharing with platforms.
Private field VALUES are never exposed to AI systems; they influence only
boolean constraint flags. The AI knows THAT constraints apply, never WHY.

Three field tiers:
    PUBLIC_FIELDS           — always shared; safe for any platform
    CONSENT_REQUIRED_FIELDS — shared only with explicit user consent
    PRIVATE_FIELDS          — NEVER shared directly; influence boolean flags only

Key invariant::

    private_fields_exposed == 0  # always, by design

Usage::

    from vcp.privacy import filter_context_for_platform, PlatformManifest, ConsentRecord

    manifest = PlatformManifest(
        platform_id="guitar-learning-app",
        required_fields=["noise_mode", "session_length"],
        optional_fields=["feedback_style"],
    )
    consent = ConsentRecord(
        required_fields=["noise_mode"],
        optional_fields=["feedback_style"],
    )
    filtered = filter_context_for_platform(full_context, manifest, consent)
    # filtered.constraints.time_limited may be True (single parent context)
    # but "family_status" is never in filtered.public or filtered.preferences

Reference: Learning path demo — Gentian, Campion, Marta scenarios.
TypeScript reference: VCP-Demo-Site/src/lib/vcp/privacy.ts
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Field tier constants
# ---------------------------------------------------------------------------

PUBLIC_FIELDS: list[str] = [
    "display_name",
    "goal",
    "experience",
    "learning_style",
    "pace",
    "motivation",
    "role",
    "team",
    "career_goal",
]

CONSENT_REQUIRED_FIELDS: list[str] = [
    "noise_mode",
    "session_length",
    "pressure_tolerance",
    "budget_range",
    "feedback_style",
    "skills_acquired",
    "current_focus",
    "struggle_areas",
    "best_times",
    "avoid_times",
    "budget_remaining_eur",
    "workload_level",
]

PRIVATE_FIELDS: frozenset[str] = frozenset([
    "family_status",
    "dependents",
    "dependent_ages",
    "childcare_hours",
    "health_conditions",
    "health_appointments",
    "financial_constraint",
    "evening_available_after",
    "work_type",
    "schedule",
    "housing",
    "neighbor_situation",
])


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class PrivacyTier(str, Enum):
    """Privacy tier for a context field."""

    PUBLIC = "public"
    CONSENT_REQUIRED = "consent-required"
    PRIVATE = "private"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class ConstraintFlags:
    """
    Boolean constraint flags derived from private context.

    These are the ONLY representation of private data that leaves the
    private context. The underlying reason (e.g. family_status, health
    conditions) is never exposed — only the behavioural implication (True/False).
    """

    time_limited: bool = False
    budget_limited: bool = False
    noise_restricted: bool = False
    energy_variable: bool = False
    schedule_irregular: bool = False
    mobility_limited: bool = False
    health_considerations: bool = False

    def as_dict(self) -> dict[str, bool]:
        """Return all flags as a plain dict."""
        return {
            "time_limited": self.time_limited,
            "budget_limited": self.budget_limited,
            "noise_restricted": self.noise_restricted,
            "energy_variable": self.energy_variable,
            "schedule_irregular": self.schedule_irregular,
            "mobility_limited": self.mobility_limited,
            "health_considerations": self.health_considerations,
        }

    @property
    def active_count(self) -> int:
        """Number of active (True) constraint flags."""
        return sum(self.as_dict().values())


@dataclass
class FilteredContext:
    """
    Context filtered for platform sharing.

    Attributes:
        public:      Fields always visible — display_name, goal, etc.
        preferences: Consented preference fields — noise_mode, session_length, etc.
        constraints: Boolean flags derived from private data (never the WHY).
    """

    public: dict[str, Any] = field(default_factory=dict)
    preferences: dict[str, Any] = field(default_factory=dict)
    constraints: ConstraintFlags = field(default_factory=ConstraintFlags)


@dataclass
class PlatformManifest:
    """Manifest declaring what context fields a platform requires or accepts."""

    platform_id: str
    required_fields: list[str] = field(default_factory=list)
    optional_fields: list[str] = field(default_factory=list)


@dataclass
class ConsentRecord:
    """Explicit user consent for sharing specific named fields."""

    required_fields: list[str] = field(default_factory=list)
    optional_fields: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Field access helpers
# ---------------------------------------------------------------------------


def get_field_value(ctx: dict[str, Any], field_name: str) -> Any:
    """
    Extract a field value from nested context structure.

    Searches across public context sub-sections in priority order.
    The ``constraints`` dict is excluded because it holds boolean flags
    derived from private data; including it could leak private values
    if a public field name collides with a constraints key.

    Returns None if the field is not present in any section.
    """
    sources = [
        ctx.get("public_profile"),
        ctx.get("portable_preferences"),
        ctx.get("current_skills"),
        ctx.get("availability"),
        ctx.get("shared_with_manager"),
    ]
    for source in sources:
        if isinstance(source, dict) and field_name in source:
            return source[field_name]
    return None


def is_private_field(ctx: dict[str, Any], field_name: str) -> bool:
    """
    Return True if this field is classified as private.

    A field is private if it appears in PRIVATE_FIELDS, or if it is a key
    in the context's private_context sub-dict.
    """
    if field_name in PRIVATE_FIELDS:
        return True
    private_ctx = ctx.get("private_context")
    if isinstance(private_ctx, dict) and field_name in private_ctx:
        return True
    return False


# ---------------------------------------------------------------------------
# Constraint flag extraction — core privacy mechanism
# ---------------------------------------------------------------------------

# Schedule values that imply irregular/shift patterns (energy + scheduling
# impact).  Regular schedules like "9-5" should NOT trigger these flags.
_IRREGULAR_SCHEDULE_KEYWORDS = frozenset({
    "shift", "rotating", "night", "variable", "irregular", "on-call",
})


def _is_irregular_schedule(schedule_value: Any) -> bool:
    """Return True if *schedule_value* indicates an irregular schedule."""
    if not isinstance(schedule_value, str):
        return bool(schedule_value)
    return any(kw in schedule_value.lower() for kw in _IRREGULAR_SCHEDULE_KEYWORDS)


def extract_constraint_flags(ctx: dict[str, Any]) -> ConstraintFlags:
    """
    Extract boolean constraint flags from context.

    This is the core privacy mechanism: private field values are never
    exposed. Instead, their existence influences a set of boolean flags.
    The AI system knows THAT constraints apply, never WHY.

    Examples from learning path demo:
        Gentian (single parent, childcare_hours set)
            → time_limited=True, schedule_irregular=True
        Gentian (fatigue health condition)
            → energy_variable=True, health_considerations=True
        Campion (financial_constraint, shift schedule)
            → budget_limited=True, energy_variable=True, schedule_irregular=True

    Args:
        ctx: Full user context dict (may contain private_context sub-dict).

    Returns:
        ConstraintFlags — all boolean values, no private data.
    """
    constraints = ctx.get("constraints") or {}
    private = ctx.get("private_context") or {}
    schedule_val = private.get("schedule")

    return ConstraintFlags(
        time_limited=(
            bool(constraints.get("time_limited"))
            or bool(private.get("childcare_hours"))
            or bool(private.get("schedule_irregular"))
        ),
        budget_limited=(
            bool(constraints.get("budget_limited"))
            or bool(private.get("financial_constraint"))
        ),
        noise_restricted=(
            bool(constraints.get("noise_restricted"))
            or bool(private.get("noise_sensitive"))
            or bool(private.get("neighbor_situation"))
        ),
        energy_variable=(
            bool(constraints.get("energy_variable"))
            or bool(private.get("health_conditions"))
            or _is_irregular_schedule(schedule_val)
        ),
        schedule_irregular=(
            bool(constraints.get("schedule_irregular"))
            or _is_irregular_schedule(schedule_val)
            or bool(private.get("childcare_hours"))
        ),
        mobility_limited=(
            bool(constraints.get("mobility_limited"))
            or bool(private.get("mobility_limited"))
        ),
        health_considerations=(
            bool(constraints.get("health_considerations"))
            or bool(private.get("health_conditions"))
            or bool(private.get("health_appointments"))
        ),
    )


# ---------------------------------------------------------------------------
# Core privacy filter
# ---------------------------------------------------------------------------


def filter_context_for_platform(
    full_context: dict[str, Any],
    manifest: PlatformManifest,
    consent: ConsentRecord,
) -> FilteredContext:
    """
    Filter context for a platform, respecting consent and privacy rules.

    Algorithm:
        1. Always include PUBLIC_FIELDS (if present in context).
        2. For each required field in manifest:
           - If private → withheld (never shared directly).
           - If consented → added to preferences.
           - Otherwise → withheld.
        3. For each optional field in manifest: same private/consent logic.
        4. Extract boolean constraint flags from private context.
        5. Log audit entry (private_fields_exposed is always 0).

    Args:
        full_context: Complete user context dict.
        manifest:     Platform's declared field requirements.
        consent:      User's explicit consent record.

    Returns:
        FilteredContext with public fields, consented preferences, and
        boolean constraint flags. Private field values are never present.
    """
    result = FilteredContext()
    shared: list[str] = []
    withheld: list[str] = []

    # Step 1: Always include public fields
    for f in PUBLIC_FIELDS:
        value = get_field_value(full_context, f)
        if value is not None:
            result.public[f] = value
            shared.append(f)

    # Step 2: Required fields from manifest
    for f in manifest.required_fields:
        if is_private_field(full_context, f):
            withheld.append(f)
            continue
        if f in consent.required_fields:
            value = get_field_value(full_context, f)
            if value is not None:
                result.preferences[f] = value
                shared.append(f)
        else:
            withheld.append(f)

    # Step 3: Optional fields from manifest
    for f in manifest.optional_fields:
        if is_private_field(full_context, f):
            withheld.append(f)
            continue
        if f in consent.optional_fields:
            value = get_field_value(full_context, f)
            if value is not None:
                result.preferences[f] = value
                shared.append(f)
        else:
            withheld.append(f)

    # Step 4: Boolean constraint flags (private data → booleans only)
    result.constraints = extract_constraint_flags(full_context)

    # Step 5: Audit log — private_fields_exposed is always 0 by design
    logger.info(
        "vcp.privacy.context_shared: platform=%s shared=%d withheld=%d "
        "private_flags_active=%d private_fields_exposed=0",
        manifest.platform_id,
        len(set(shared)),
        len(set(withheld)),
        result.constraints.active_count,
    )

    return result


# ---------------------------------------------------------------------------
# Stakeholder filtering
# ---------------------------------------------------------------------------


def get_stakeholder_visible_fields(
    ctx: dict[str, Any],
    stakeholder: str,
) -> list[str]:
    """
    Get fields visible to a specific stakeholder type (e.g. "manager", "hr").

    Falls back to PUBLIC_FIELDS only if no sharing_settings configured.
    Private fields are never added regardless of sharing_settings.

    Args:
        ctx:         Full user context dict (may contain sharing_settings).
        stakeholder: Stakeholder type string (e.g. "manager", "hr", "team").

    Returns:
        List of field names visible to this stakeholder.
    """
    sharing_settings = ctx.get("sharing_settings") or {}
    stakeholder_settings = sharing_settings.get(stakeholder)

    if not stakeholder_settings:
        return list(PUBLIC_FIELDS)

    visible = list(PUBLIC_FIELDS)

    share_list = stakeholder_settings.get("share") or []
    for f in share_list:
        if not is_private_field(ctx, f) and f not in visible:
            visible.append(f)

    hide_list = stakeholder_settings.get("hide") or []
    if hide_list:
        visible = [f for f in visible if f not in hide_list]

    return visible


def get_stakeholder_hidden_fields(
    ctx: dict[str, Any],
    stakeholder: str,
) -> list[str]:
    """
    Get fields hidden from a specific stakeholder type.

    Private fields are always hidden.
    Consent-required fields not in the visible list are also hidden.

    Args:
        ctx:         Full user context dict.
        stakeholder: Stakeholder type string.

    Returns:
        List of field names hidden from this stakeholder.
    """
    visible = get_stakeholder_visible_fields(ctx, stakeholder)
    hidden = list(PRIVATE_FIELDS)

    for f in CONSENT_REQUIRED_FIELDS:
        if f not in visible and f not in hidden:
            hidden.append(f)

    return hidden


# ---------------------------------------------------------------------------
# Share preview — before consent is given
# ---------------------------------------------------------------------------


def get_share_preview(
    ctx: dict[str, Any],
    manifest: PlatformManifest,
) -> dict[str, list[str]]:
    """
    Preview what would be shared/withheld for a platform (before consent).

    Useful for showing users a "what will be shared" confirmation dialog
    before they grant consent.

    Args:
        ctx:      Full user context dict.
        manifest: Platform's declared field requirements.

    Returns:
        Dict with keys:
            would_share:      Fields shared unconditionally.
            would_withhold:   Fields that will be withheld.
            requires_consent: Non-private required fields needing user consent.
    """
    would_share = list(PUBLIC_FIELDS)
    would_withhold: list[str] = []
    requires_consent: list[str] = []

    sharing_settings = ctx.get("sharing_settings") or {}
    platform_settings = sharing_settings.get("platforms") or {}
    platform_hide = platform_settings.get("hide") or []
    platform_share = platform_settings.get("share") or []

    for f in manifest.required_fields:
        if is_private_field(ctx, f):
            would_withhold.append(f)
        elif f in platform_hide:
            would_withhold.append(f)
        else:
            requires_consent.append(f)

    for f in manifest.optional_fields:
        if is_private_field(ctx, f):
            would_withhold.append(f)
        elif f in platform_share:
            would_share.append(f)
        else:
            would_withhold.append(f)

    # Private context keys are always withheld
    private_ctx = ctx.get("private_context") or {}
    for key in private_ctx:
        if key != "_note" and key not in would_withhold:
            would_withhold.append(key)

    return {
        "would_share": list(dict.fromkeys(would_share)),
        "would_withhold": list(dict.fromkeys(would_withhold)),
        "requires_consent": list(dict.fromkeys(requires_consent)),
    }


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def format_field_name(field_name: str) -> str:
    """Format a snake_case field name for display ('family_status' → 'Family Status')."""
    return field_name.replace("_", " ").title()


def get_field_privacy_level(field_name: str) -> PrivacyTier:
    """Return the privacy tier for a field name."""
    if field_name in PUBLIC_FIELDS:
        return PrivacyTier.PUBLIC
    if field_name in PRIVATE_FIELDS:
        return PrivacyTier.PRIVATE
    return PrivacyTier.CONSENT_REQUIRED


def generate_privacy_summary(
    shared: list[str],
    withheld: list[str],
    private_influenced: int,
) -> str:
    """Generate a human-readable privacy summary string."""
    parts: list[str] = []
    if shared:
        parts.append(f"{len(shared)} fields shared")
    if withheld:
        parts.append(f"{len(withheld)} fields kept private")
    if private_influenced > 0:
        parts.append(
            f"{private_influenced} private constraints influenced "
            "recommendations (details not exposed)"
        )
    return " \u2022 ".join(parts)
