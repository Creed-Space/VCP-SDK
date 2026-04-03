"""
Tests for vcp.privacy — privacy field filtering.

Core invariant under test: PRIVATE_FIELDS are never exposed in FilteredContext,
regardless of what manifest or consent records claim. Private data influences
only boolean ConstraintFlags.
"""

from __future__ import annotations

import logging

import pytest

from vcp.privacy import (
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

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _gentian_context() -> dict:
    """Gentian (guitar learner) from learning path demo — single parent with fatigue."""
    return {
        "public_profile": {
            "display_name": "Gentian",
            "goal": "guitar",
            "experience": "beginner",
            "learning_style": "visual",
            "pace": "relaxed",
        },
        "portable_preferences": {
            "session_length": 30,
            "noise_mode": "quiet",
            "feedback_style": "encouragement",
        },
        "constraints": {},
        "private_context": {
            "family_status": "single_parent",
            "dependents": 2,
            "childcare_hours": "18:00-20:00",
            "health_conditions": "fatigue",
        },
    }


def _campion_context() -> dict:
    """Campion (career advisor) from learning path demo — shift worker, financial constraint."""
    return {
        "public_profile": {
            "display_name": "Campion",
            "role": "software engineer",
            "career_goal": "lead engineer",
        },
        "portable_preferences": {
            "workload_level": "high",
            "budget_range": "limited",
        },
        "constraints": {},
        "private_context": {
            "financial_constraint": True,
            "schedule": "shift",
        },
    }


def _make_manifest(
    required: list[str] | None = None,
    optional: list[str] | None = None,
    pid: str = "platform-x",
) -> PlatformManifest:
    return PlatformManifest(
        platform_id=pid,
        required_fields=required or [],
        optional_fields=optional or [],
    )


def _make_consent(
    required: list[str] | None = None,
    optional: list[str] | None = None,
) -> ConsentRecord:
    return ConsentRecord(
        required_fields=required or [],
        optional_fields=optional or [],
    )


# ---------------------------------------------------------------------------
# Field tier constants
# ---------------------------------------------------------------------------


class TestFieldConstants:
    def test_public_fields_non_empty(self) -> None:
        assert len(PUBLIC_FIELDS) > 0

    def test_private_fields_non_empty(self) -> None:
        assert len(PRIVATE_FIELDS) > 0

    def test_consent_required_fields_non_empty(self) -> None:
        assert len(CONSENT_REQUIRED_FIELDS) > 0

    def test_no_overlap_public_private(self) -> None:
        assert not set(PUBLIC_FIELDS) & set(PRIVATE_FIELDS)

    def test_no_overlap_public_consent(self) -> None:
        assert not set(PUBLIC_FIELDS) & set(CONSENT_REQUIRED_FIELDS)

    def test_family_status_is_private(self) -> None:
        assert "family_status" in PRIVATE_FIELDS

    def test_health_conditions_is_private(self) -> None:
        assert "health_conditions" in PRIVATE_FIELDS

    def test_financial_constraint_is_private(self) -> None:
        assert "financial_constraint" in PRIVATE_FIELDS

    def test_goal_is_public(self) -> None:
        assert "goal" in PUBLIC_FIELDS

    def test_display_name_is_public(self) -> None:
        assert "display_name" in PUBLIC_FIELDS

    def test_noise_mode_is_consent_required(self) -> None:
        assert "noise_mode" in CONSENT_REQUIRED_FIELDS

    def test_session_length_is_consent_required(self) -> None:
        assert "session_length" in CONSENT_REQUIRED_FIELDS


# ---------------------------------------------------------------------------
# get_field_value
# ---------------------------------------------------------------------------


class TestGetFieldValue:
    def test_finds_in_public_profile(self) -> None:
        ctx = {"public_profile": {"goal": "guitar"}}
        assert get_field_value(ctx, "goal") == "guitar"

    def test_finds_in_portable_preferences(self) -> None:
        ctx = {"portable_preferences": {"noise_mode": "quiet"}}
        assert get_field_value(ctx, "noise_mode") == "quiet"

    def test_finds_in_current_skills(self) -> None:
        ctx = {"current_skills": {"chord_changes": "beginner"}}
        assert get_field_value(ctx, "chord_changes") == "beginner"

    def test_returns_none_when_missing(self) -> None:
        assert get_field_value({}, "nonexistent") is None

    def test_public_profile_takes_priority_over_constraints(self) -> None:
        ctx = {
            "public_profile": {"field": "a"},
            "constraints": {"field": "b"},
        }
        assert get_field_value(ctx, "field") == "a"

    def test_empty_context_returns_none(self) -> None:
        assert get_field_value({}, "goal") is None


# ---------------------------------------------------------------------------
# is_private_field
# ---------------------------------------------------------------------------


class TestIsPrivateField:
    def test_private_field_name_returns_true(self) -> None:
        assert is_private_field({}, "family_status") is True

    def test_health_conditions_returns_true(self) -> None:
        assert is_private_field({}, "health_conditions") is True

    def test_public_field_returns_false(self) -> None:
        assert is_private_field({}, "goal") is False

    def test_consent_required_field_returns_false(self) -> None:
        assert is_private_field({}, "noise_mode") is False

    def test_field_in_private_context_returns_true(self) -> None:
        ctx = {"private_context": {"secret_field": "value"}}
        assert is_private_field(ctx, "secret_field") is True

    def test_field_not_in_private_context_returns_false(self) -> None:
        ctx = {"private_context": {"other": "x"}}
        assert is_private_field(ctx, "goal") is False


# ---------------------------------------------------------------------------
# extract_constraint_flags — core privacy mechanism
# ---------------------------------------------------------------------------


class TestExtractConstraintFlags:
    def test_empty_context_all_false(self) -> None:
        flags = extract_constraint_flags({})
        assert flags.time_limited is False
        assert flags.budget_limited is False
        assert flags.noise_restricted is False
        assert flags.energy_variable is False
        assert flags.schedule_irregular is False
        assert flags.mobility_limited is False
        assert flags.health_considerations is False

    def test_returns_constraint_flags_type(self) -> None:
        assert isinstance(extract_constraint_flags({}), ConstraintFlags)

    def test_explicit_constraint_flag_preserved(self) -> None:
        ctx = {"constraints": {"time_limited": True}}
        assert extract_constraint_flags(ctx).time_limited is True

    def test_childcare_implies_time_limited(self) -> None:
        ctx = {"private_context": {"childcare_hours": "18:00-20:00"}}
        assert extract_constraint_flags(ctx).time_limited is True

    def test_childcare_implies_schedule_irregular(self) -> None:
        ctx = {"private_context": {"childcare_hours": "18:00-20:00"}}
        assert extract_constraint_flags(ctx).schedule_irregular is True

    def test_financial_constraint_implies_budget_limited(self) -> None:
        ctx = {"private_context": {"financial_constraint": True}}
        assert extract_constraint_flags(ctx).budget_limited is True

    def test_neighbor_situation_implies_noise_restricted(self) -> None:
        ctx = {"private_context": {"neighbor_situation": "noisy"}}
        assert extract_constraint_flags(ctx).noise_restricted is True

    def test_noise_sensitive_implies_noise_restricted(self) -> None:
        ctx = {"private_context": {"noise_sensitive": True}}
        assert extract_constraint_flags(ctx).noise_restricted is True

    def test_health_conditions_implies_energy_variable(self) -> None:
        ctx = {"private_context": {"health_conditions": "fatigue"}}
        assert extract_constraint_flags(ctx).energy_variable is True

    def test_health_conditions_implies_health_considerations(self) -> None:
        ctx = {"private_context": {"health_conditions": "fatigue"}}
        assert extract_constraint_flags(ctx).health_considerations is True

    def test_health_appointments_implies_health_considerations(self) -> None:
        ctx = {"private_context": {"health_appointments": True}}
        assert extract_constraint_flags(ctx).health_considerations is True

    def test_shift_schedule_implies_energy_variable(self) -> None:
        ctx = {"private_context": {"schedule": "shift"}}
        assert extract_constraint_flags(ctx).energy_variable is True

    def test_shift_schedule_implies_schedule_irregular(self) -> None:
        ctx = {"private_context": {"schedule": "shift"}}
        assert extract_constraint_flags(ctx).schedule_irregular is True

    def test_mobility_limited_in_private_context(self) -> None:
        ctx = {"private_context": {"mobility_limited": True}}
        assert extract_constraint_flags(ctx).mobility_limited is True

    def test_mobility_limited_in_constraints(self) -> None:
        ctx = {"constraints": {"mobility_limited": True}}
        assert extract_constraint_flags(ctx).mobility_limited is True

    def test_gentian_context_flags(self) -> None:
        """Single parent + fatigue → time/schedule/energy/health flags."""
        flags = extract_constraint_flags(_gentian_context())
        assert flags.time_limited is True        # childcare_hours
        assert flags.schedule_irregular is True  # childcare_hours
        assert flags.energy_variable is True     # health_conditions
        assert flags.health_considerations is True  # health_conditions
        assert flags.budget_limited is False

    def test_campion_context_flags(self) -> None:
        """Shift worker + financial constraint → budget/energy/schedule flags."""
        flags = extract_constraint_flags(_campion_context())
        assert flags.budget_limited is True       # financial_constraint
        assert flags.energy_variable is True      # schedule=shift
        assert flags.schedule_irregular is True   # schedule=shift
        assert flags.health_considerations is False

    def test_active_count_zero_on_empty(self) -> None:
        assert extract_constraint_flags({}).active_count == 0

    def test_active_count_increments(self) -> None:
        ctx = {
            "private_context": {
                "childcare_hours": "18:00",
                "financial_constraint": True,
            }
        }
        flags = extract_constraint_flags(ctx)
        # time_limited, schedule_irregular, budget_limited → at least 3
        assert flags.active_count >= 3

    def test_as_dict_all_booleans(self) -> None:
        flags = extract_constraint_flags(_gentian_context())
        for v in flags.as_dict().values():
            assert isinstance(v, bool)


# ---------------------------------------------------------------------------
# filter_context_for_platform
# ---------------------------------------------------------------------------


class TestFilterContextForPlatform:
    def test_returns_filtered_context_type(self) -> None:
        result = filter_context_for_platform({}, _make_manifest(), _make_consent())
        assert isinstance(result, FilteredContext)

    def test_public_fields_always_included(self) -> None:
        ctx = {"public_profile": {"display_name": "Alice", "goal": "learn guitar"}}
        result = filter_context_for_platform(ctx, _make_manifest(), _make_consent())
        assert result.public["display_name"] == "Alice"
        assert result.public["goal"] == "learn guitar"

    def test_missing_public_field_not_in_output(self) -> None:
        result = filter_context_for_platform({}, _make_manifest(), _make_consent())
        assert "display_name" not in result.public

    def test_private_required_field_never_exposed(self) -> None:
        """Even if manifest requires a private field AND user consents, it must be withheld."""
        ctx = {"private_context": {"family_status": "single_parent"}}
        manifest = _make_manifest(required=["family_status"])
        consent = _make_consent(required=["family_status"])
        result = filter_context_for_platform(ctx, manifest, consent)
        assert "family_status" not in result.public
        assert "family_status" not in result.preferences

    def test_private_optional_field_never_exposed(self) -> None:
        ctx = {"private_context": {"health_conditions": "chronic fatigue"}}
        manifest = _make_manifest(optional=["health_conditions"])
        consent = _make_consent(optional=["health_conditions"])
        result = filter_context_for_platform(ctx, manifest, consent)
        assert "health_conditions" not in result.public
        assert "health_conditions" not in result.preferences

    def test_consented_required_field_included(self) -> None:
        ctx = {"portable_preferences": {"noise_mode": "quiet"}}
        manifest = _make_manifest(required=["noise_mode"])
        consent = _make_consent(required=["noise_mode"])
        result = filter_context_for_platform(ctx, manifest, consent)
        assert result.preferences["noise_mode"] == "quiet"

    def test_unconsented_required_field_withheld(self) -> None:
        ctx = {"portable_preferences": {"noise_mode": "quiet"}}
        manifest = _make_manifest(required=["noise_mode"])
        consent = _make_consent()  # no consent granted
        result = filter_context_for_platform(ctx, manifest, consent)
        assert "noise_mode" not in result.preferences

    def test_consented_optional_field_included(self) -> None:
        ctx = {"portable_preferences": {"session_length": 45}}
        manifest = _make_manifest(optional=["session_length"])
        consent = _make_consent(optional=["session_length"])
        result = filter_context_for_platform(ctx, manifest, consent)
        assert result.preferences["session_length"] == 45

    def test_unconsented_optional_field_withheld(self) -> None:
        ctx = {"portable_preferences": {"session_length": 45}}
        manifest = _make_manifest(optional=["session_length"])
        consent = _make_consent()  # no consent granted
        result = filter_context_for_platform(ctx, manifest, consent)
        assert "session_length" not in result.preferences

    def test_constraints_always_populated(self) -> None:
        result = filter_context_for_platform(
            _gentian_context(), _make_manifest(), _make_consent()
        )
        assert isinstance(result.constraints, ConstraintFlags)
        assert result.constraints.time_limited is True

    def test_private_fields_exposed_always_zero_in_log(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.INFO, logger="vcp.privacy"):
            filter_context_for_platform(
                _gentian_context(), _make_manifest(), _make_consent()
            )
        assert any("private_fields_exposed=0" in r.message for r in caplog.records)

    def test_gentian_full_scenario(self) -> None:
        ctx = _gentian_context()
        manifest = _make_manifest(
            required=["noise_mode", "session_length"],
            optional=["feedback_style"],
            pid="guitar-platform",
        )
        consent = _make_consent(
            required=["noise_mode"],
            optional=["feedback_style"],
        )
        result = filter_context_for_platform(ctx, manifest, consent)

        # Public fields present
        assert result.public["display_name"] == "Gentian"
        assert result.public["goal"] == "guitar"

        # Consented required field present
        assert result.preferences["noise_mode"] == "quiet"

        # Unconsented required field absent
        assert "session_length" not in result.preferences

        # Consented optional field present
        assert result.preferences["feedback_style"] == "encouragement"

        # Private data NEVER present in any output
        assert "family_status" not in result.public
        assert "family_status" not in result.preferences
        assert "health_conditions" not in result.public
        assert "health_conditions" not in result.preferences

        # Boolean constraint flags reflect private reality
        assert result.constraints.time_limited is True
        assert result.constraints.health_considerations is True

    def test_campion_full_scenario(self) -> None:
        ctx = _campion_context()
        manifest = _make_manifest(
            required=["workload_level", "budget_range"],
            pid="career-platform",
        )
        consent = _make_consent(required=["workload_level", "budget_range"])
        result = filter_context_for_platform(ctx, manifest, consent)

        assert result.public["display_name"] == "Campion"
        assert result.preferences["workload_level"] == "high"
        assert result.preferences["budget_range"] == "limited"

        # Financial constraint and schedule never directly exposed
        assert "financial_constraint" not in result.public
        assert "financial_constraint" not in result.preferences
        assert "schedule" not in result.public
        assert "schedule" not in result.preferences

        # But boolean flags reflect them
        assert result.constraints.budget_limited is True
        assert result.constraints.schedule_irregular is True

    def test_empty_manifest_only_public_fields(self) -> None:
        ctx = {"public_profile": {"display_name": "Test", "goal": "test"}}
        result = filter_context_for_platform(ctx, _make_manifest(), _make_consent())
        assert "display_name" in result.public
        assert result.preferences == {}


# ---------------------------------------------------------------------------
# Stakeholder filtering
# ---------------------------------------------------------------------------


class TestStakeholderFiltering:
    def test_no_settings_returns_public_fields_only(self) -> None:
        visible = get_stakeholder_visible_fields({}, "manager")
        assert set(visible) == set(PUBLIC_FIELDS)

    def test_sharing_settings_adds_non_private_fields(self) -> None:
        ctx = {"sharing_settings": {"manager": {"share": ["workload_level"]}}}
        visible = get_stakeholder_visible_fields(ctx, "manager")
        assert "workload_level" in visible
        assert "display_name" in visible  # public always present

    def test_private_field_never_added_via_sharing_settings(self) -> None:
        ctx = {"sharing_settings": {"manager": {"share": ["family_status"]}}}
        visible = get_stakeholder_visible_fields(ctx, "manager")
        assert "family_status" not in visible

    def test_hide_removes_public_field(self) -> None:
        ctx = {"sharing_settings": {"hr": {"hide": ["goal"]}}}
        visible = get_stakeholder_visible_fields(ctx, "hr")
        assert "goal" not in visible

    def test_unknown_stakeholder_returns_public_fields(self) -> None:
        visible = get_stakeholder_visible_fields({}, "unknown-stakeholder")
        assert set(visible) == set(PUBLIC_FIELDS)

    def test_hidden_fields_contains_all_private(self) -> None:
        hidden = get_stakeholder_hidden_fields({}, "manager")
        for pf in PRIVATE_FIELDS:
            assert pf in hidden

    def test_hidden_fields_contains_unconsented_consent_required(self) -> None:
        hidden = get_stakeholder_hidden_fields({}, "manager")
        for cf in CONSENT_REQUIRED_FIELDS:
            assert cf in hidden

    def test_hidden_does_not_contain_public_fields(self) -> None:
        get_stakeholder_hidden_fields({}, "manager")
        visible = get_stakeholder_visible_fields({}, "manager")
        # Public fields should be visible, not in hidden
        for pf in PUBLIC_FIELDS:
            assert pf in visible


# ---------------------------------------------------------------------------
# get_share_preview
# ---------------------------------------------------------------------------


class TestGetSharePreview:
    def test_returns_three_lists(self) -> None:
        preview = get_share_preview({}, _make_manifest())
        assert "would_share" in preview
        assert "would_withhold" in preview
        assert "requires_consent" in preview

    def test_public_fields_in_would_share(self) -> None:
        ctx = {"public_profile": {"goal": "learn"}}
        preview = get_share_preview(ctx, _make_manifest())
        assert "goal" in preview["would_share"]

    def test_private_required_field_in_would_withhold(self) -> None:
        ctx = {"private_context": {"family_status": "single_parent"}}
        manifest = _make_manifest(required=["family_status"])
        preview = get_share_preview(ctx, manifest)
        assert "family_status" in preview["would_withhold"]
        assert "family_status" not in preview["requires_consent"]

    def test_non_private_required_in_requires_consent(self) -> None:
        manifest = _make_manifest(required=["noise_mode"])
        preview = get_share_preview({}, manifest)
        assert "noise_mode" in preview["requires_consent"]

    def test_private_optional_in_would_withhold(self) -> None:
        ctx = {"private_context": {"health_conditions": "fatigue"}}
        manifest = _make_manifest(optional=["health_conditions"])
        preview = get_share_preview(ctx, manifest)
        assert "health_conditions" in preview["would_withhold"]

    def test_private_context_keys_in_would_withhold(self) -> None:
        ctx = {"private_context": {"secret_key": "value"}}
        preview = get_share_preview(ctx, _make_manifest())
        assert "secret_key" in preview["would_withhold"]

    def test_note_key_skipped(self) -> None:
        ctx = {"private_context": {"_note": "internal annotation"}}
        preview = get_share_preview(ctx, _make_manifest())
        assert "_note" not in preview["would_withhold"]

    def test_no_duplicates_in_output(self) -> None:
        manifest = _make_manifest(required=["goal", "noise_mode"])
        preview = get_share_preview({}, manifest)
        for key in ("would_share", "would_withhold", "requires_consent"):
            assert len(preview[key]) == len(set(preview[key]))

    def test_empty_manifest_empty_consent_lists(self) -> None:
        preview = get_share_preview({}, _make_manifest())
        assert preview["requires_consent"] == []
        assert preview["would_withhold"] == []


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


class TestDisplayHelpers:
    def test_format_field_name_underscored(self) -> None:
        assert format_field_name("family_status") == "Family Status"

    def test_format_field_name_single_word(self) -> None:
        assert format_field_name("goal") == "Goal"

    def test_format_field_name_multiple_words(self) -> None:
        assert format_field_name("health_appointments") == "Health Appointments"

    def test_get_field_privacy_level_public(self) -> None:
        assert get_field_privacy_level("goal") == PrivacyTier.PUBLIC

    def test_get_field_privacy_level_private(self) -> None:
        assert get_field_privacy_level("family_status") == PrivacyTier.PRIVATE

    def test_get_field_privacy_level_consent_required(self) -> None:
        assert get_field_privacy_level("noise_mode") == PrivacyTier.CONSENT_REQUIRED

    def test_get_field_privacy_level_unknown_defaults_to_consent(self) -> None:
        assert get_field_privacy_level("unknown_field") == PrivacyTier.CONSENT_REQUIRED

    def test_generate_privacy_summary_all_parts(self) -> None:
        summary = generate_privacy_summary(["goal"], ["family_status"], 2)
        assert "1 fields shared" in summary
        assert "1 fields kept private" in summary
        assert "2 private constraints" in summary

    def test_generate_privacy_summary_no_private_influenced(self) -> None:
        summary = generate_privacy_summary(["goal"], [], 0)
        assert "private constraints" not in summary

    def test_generate_privacy_summary_empty(self) -> None:
        assert generate_privacy_summary([], [], 0) == ""

    def test_generate_privacy_summary_uses_bullet_separator(self) -> None:
        summary = generate_privacy_summary(["goal"], ["family_status"], 1)
        assert "\u2022" in summary  # bullet separator


# ---------------------------------------------------------------------------
# Privacy guarantee — exhaustive checks
# ---------------------------------------------------------------------------


class TestPrivacyGuarantee:
    """Core invariant: no PRIVATE_FIELD value appears in FilteredContext output."""

    def test_private_field_blocked_even_if_in_public_profile(self) -> None:
        """If someone stuffs a private field into public_profile, it's still blocked."""
        ctx = {
            "public_profile": {"family_status": "single_parent"},
            "private_context": {"family_status": "single_parent"},
        }
        manifest = _make_manifest(required=PRIVATE_FIELDS)
        consent = _make_consent(required=PRIVATE_FIELDS)
        result = filter_context_for_platform(ctx, manifest, consent)
        for pf in PRIVATE_FIELDS:
            assert pf not in result.preferences

    def test_constraint_flags_are_all_booleans(self) -> None:
        ctx = {"private_context": {f: "secret" for f in PRIVATE_FIELDS}}
        flags = extract_constraint_flags(ctx)
        for v in flags.as_dict().values():
            assert isinstance(v, bool), f"Expected bool, got {type(v)}: {v}"

    def test_no_private_value_leaks_through_constraints_dict(self) -> None:
        ctx = {"private_context": {"family_status": "single_parent"}}
        flags = extract_constraint_flags(ctx)
        constraint_dict = flags.as_dict()
        for k, v in constraint_dict.items():
            assert v != "single_parent", f"{k} leaked private value"

    def test_full_private_context_no_exposure(self) -> None:
        ctx = {
            "public_profile": {"display_name": "Test", "goal": "test"},
            "private_context": {f: f"private-{f}" for f in PRIVATE_FIELDS},
        }
        private_list = sorted(PRIVATE_FIELDS)
        manifest = _make_manifest(
            required=private_list[:5],
            optional=private_list[5:],
        )
        consent = _make_consent(
            required=private_list[:5],
            optional=private_list[5:],
        )
        result = filter_context_for_platform(ctx, manifest, consent)
        for pf in PRIVATE_FIELDS:
            assert pf not in result.public
            assert pf not in result.preferences
