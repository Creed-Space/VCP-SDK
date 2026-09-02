"""Regression tests for the 2026-09 audit fixes."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from vcp.adaptation.context import ContextEncoder, PersonalStateDimension, SituationalDimension
from vcp.adaptation.state import StateTracker, TransitionSeverity
from vcp.bundle import BundleBuilder, Manifest
from vcp.canonicalize import parse_json_strict, parse_rfc3339_utc
from vcp.enforcement import (
    DecisionType,
    EnforcementMode,
    EvaluationContext,
    RefusalBoundaryPlugin,
)
from vcp.extensions.personal import DecayConfig
from vcp.hooks.builtin import _adherence_escalate_action, _persona_select_action
from vcp.hooks.types import HookInput, ResultStatus, TransitionEvent
from vcp.identity.registry import AuthorizationContext, LocalRegistry, PrivacyTier
from vcp.identity.token import Token
from vcp.skill_security import _parse_frontmatter
from vcp.types import TokenType


class TestRegistryPrivacy:
    def test_unauthorised_subscribers_never_see_hidden_registrations(self) -> None:
        registry = LocalRegistry()
        seen: list[tuple[str, str]] = []
        anonymous = AuthorizationContext()
        registry.subscribe("user.alice.**", anonymous, lambda t, e: seen.append((t.full, e)))
        registry.subscribe("**", anonymous, lambda t, e: seen.append((t.full, e)))

        registry.register(
            Token.parse("user.alice.secret"), privacy_tier=PrivacyTier.PERSONAL, owner_id="alice"
        )
        registry.register(Token.parse("company.acme.hr"), privacy_tier=PrivacyTier.ORGANIZATIONAL)
        registry.register(Token.parse("family.safe.guide"))

        assert seen == [("family.safe.guide", "created")]

    def test_owner_subscriber_still_notified(self) -> None:
        registry = LocalRegistry()
        seen: list[str] = []
        owner = AuthorizationContext(requester_id="alice", owned_prefixes={"user.alice"})
        registry.subscribe("user.alice.**", owner, lambda t, e: seen.append(t.full))
        registry.register(
            Token.parse("user.alice.secret"), privacy_tier=PrivacyTier.PERSONAL, owner_id="alice"
        )
        assert seen == ["user.alice.secret"]

    def test_owned_prefix_is_segment_aware(self) -> None:
        registry = LocalRegistry()
        registry.register(
            Token.parse("user.alicex.other"), privacy_tier=PrivacyTier.PERSONAL, owner_id="x"
        )
        alice = AuthorizationContext(requester_id="alice", owned_prefixes={"user.alice"})
        result = registry.find("user.alicex.**", alice)
        assert result.tokens == []
        assert result.redacted_count == 1

    def test_suffix_query_is_segment_aware(self) -> None:
        registry = LocalRegistry()
        registry.register(Token.parse("x.y.another"))
        registry.register(Token.parse("x.y.other"))
        result = registry.find("**.other", AuthorizationContext())
        assert [t.full for t in result.tokens] == ["x.y.other"]


class TestTokenGlob:
    def test_multiple_double_star_segments(self) -> None:
        token = Token.parse("a.b.c")
        assert token.matches_pattern("a.**.**") is True
        assert token.matches_pattern("**.b.**") is True
        assert token.matches_pattern("**.z.**") is False
        assert token.matches_pattern("a.*.c") is True
        assert token.matches_pattern("a.*") is False


class TestStrictJson:
    @pytest.mark.parametrize("payload", ["1e400", "-1e999", "[1e400]", '{"a": 1e400}'])
    def test_overflow_literals_are_rejected(self, payload: str) -> None:
        with pytest.raises(ValueError, match="Non-finite"):
            parse_json_strict(payload)

    def test_ordinary_floats_still_parse(self) -> None:
        assert parse_json_strict("[0.25, 1e3]") == [0.25, 1000.0]


class TestRfc3339:
    def test_nine_digit_fraction_is_accepted(self) -> None:
        parsed = parse_rfc3339_utc("2026-01-01T00:00:00.123456789Z", "ts")
        assert parsed == datetime(2026, 1, 1, 0, 0, 0, 123456, tzinfo=timezone.utc)

    def test_offset_is_normalised_to_utc(self) -> None:
        parsed = parse_rfc3339_utc("2026-01-01T02:00:00+02:00", "ts")
        assert parsed == datetime(2026, 1, 1, tzinfo=timezone.utc)

    @pytest.mark.parametrize("value", ["2026-01-01T00:00:00", "2026-01-01", 7, None, ""])
    def test_untimed_values_are_rejected(self, value: object) -> None:
        with pytest.raises(ValueError, match="ts must"):
            parse_rfc3339_utc(value, "ts")


class TestStateTracker:
    def test_embodiment_emergency_stop_is_emergency(self) -> None:
        tracker = StateTracker()
        encoder = ContextEncoder()
        tracker.record(encoder.encode(embodiment="stationary"))
        transition = tracker.record(encoder.encode(embodiment="emergency_stop"))
        assert transition is not None
        assert transition.severity is TransitionSeverity.EMERGENCY

    def test_personal_band_change_is_detected(self) -> None:
        tracker = StateTracker()
        encoder = ContextEncoder()
        tracker.record(encoder.encode(time="morning", cognitive_state=("focused", 4)))
        transition = tracker.record(
            encoder.encode(time="morning", cognitive_state=("scattered", 1))
        )
        assert transition is not None
        assert transition.severity is TransitionSeverity.MINOR
        assert transition.changed_dimensions == [PersonalStateDimension.COGNITIVE_STATE]


class TestContextEncoderStrict:
    def test_unknown_value_raises_by_default(self) -> None:
        with pytest.raises(ValueError, match="Unknown time value"):
            ContextEncoder().encode(time="afternoon")

    def test_non_strict_drops_unknown_value(self) -> None:
        ctx = ContextEncoder().encode(time="afternoon", space="office", strict=False)
        assert not ctx.has(SituationalDimension.TIME)
        assert ctx.has(SituationalDimension.SPACE)


class TestBuiltinHooksViaStateTracker:
    def test_adherence_escalate_fires_on_trigger(self) -> None:
        event = TransitionEvent(previous_state="🎭🏠", new_state="🎭🚨", trigger="emergency")
        hook_input = HookInput(context={}, constitution=None, event=event)
        result = _adherence_escalate_action(hook_input)
        assert result.status is ResultStatus.MODIFY
        assert result.annotations["adherence_escalated"] is True

    def test_persona_select_reads_to_json_shape(self) -> None:
        context = ContextEncoder().encode(company="children").to_json()
        hook_input = HookInput(context=context, constitution=None, event={})
        result = _persona_select_action(hook_input)
        assert result.status is ResultStatus.MODIFY
        assert result.annotations["persona_selected"] == "nanny"


class TestEnforcementModes:
    @pytest.mark.parametrize(
        ("mode", "expected"),
        [
            (EnforcementMode.FAIL_CLOSED, DecisionType.BLOCK),
            (EnforcementMode.ESCALATE, DecisionType.ESCALATE),
            (EnforcementMode.AUDIT_ONLY, None),
        ],
    )
    def test_missing_bundle_per_mode(self, mode: EnforcementMode, expected: object) -> None:
        decision = RefusalBoundaryPlugin(mode).evaluate(EvaluationContext(bundle=None, content="x"))
        if expected is None:
            assert decision is None
        else:
            assert decision is not None and decision.decision is expected


class TestDecayConfigValidation:
    @pytest.mark.parametrize(
        "kwargs",
        [
            {"half_life_seconds": 0},
            {"half_life_seconds": -1},
            {"half_life_seconds": 60, "baseline": 0},
            {"half_life_seconds": 60, "stale_threshold": 1.5},
            {"half_life_seconds": 60, "fresh_window_seconds": -1},
        ],
    )
    def test_invalid_config_rejected(self, kwargs: dict[str, object]) -> None:
        with pytest.raises(ValueError):
            DecayConfig(**kwargs)  # type: ignore[arg-type]


class TestManifestShape:
    @staticmethod
    def _manifest() -> dict[str, object]:
        return {
            "vcp_version": "2.0",
            "bundle": {
                "id": "creed://creed.space/x",
                "version": "1.0.0",
                "content_hash": "sha256:a",
            },
            "issuer": {"id": "issuer", "public_key": "ed25519:AAAA", "key_id": "k1"},
            "timestamps": {
                "iat": "2026-01-01T00:00:00Z",
                "nbf": "2026-01-01T00:00:00Z",
                "exp": "2026-01-02T00:00:00Z",
                "jti": "550e8400-e29b-41d4-a716-446655440000",
            },
            "budget": {"token_count": 12, "tokenizer": "cl100k_base"},
            "safety_attestation": {
                "auditor": "auditor",
                "auditor_key_id": "a1",
                "reviewed_at": "2026-01-01T00:00:00Z",
                "attestation_type": "full-audit",
                "signature": "base64:AAAA",
            },
            "signature": {
                "algorithm": "ed25519",
                "value": "base64:AAAA",
                "signed_fields": ["bundle"],
            },
        }

    def test_well_formed_manifest_parses(self) -> None:
        assert Manifest.from_dict(self._manifest()).vcp_version == "2.0"

    @pytest.mark.parametrize(
        ("path", "value"),
        [
            (("vcp_version",), "9.9"),
            (("timestamps", "jti"), "not-a-uuid"),
            (("budget", "token_count"), "12"),
            (("budget", "token_count"), True),
            (("budget", "tokenizer"), "unknown"),
            (("bundle", "id"), 7),
        ],
    )
    def test_malformed_manifest_is_rejected(self, path: tuple[str, ...], value: object) -> None:
        data = self._manifest()
        target: dict = data  # type: ignore[type-arg]
        for key in path[:-1]:
            target = target[key]  # type: ignore[assignment]
        target[path[-1]] = value
        with pytest.raises(ValueError, match="manifest"):
            Manifest.from_dict(data)


class TestBundleBuilderExpiry:
    @pytest.mark.parametrize("days", [0, 91, 365, True])
    def test_out_of_range_expiry_rejected(self, days: object) -> None:
        with pytest.raises(ValueError, match="expires_days"):
            BundleBuilder("creed://creed.space/x", "1.0.0").with_expires_days(days)  # type: ignore[arg-type]


class TestSkillFrontmatter:
    def test_dashes_inside_values_do_not_terminate_block(self) -> None:
        parsed = _parse_frontmatter("---\nname: a---b\nversion: '1.10'\n---\nbody\n")
        assert parsed == {"name": "a---b", "version": "1.10"}

    def test_invalid_yaml_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="frontmatter"):
            _parse_frontmatter("---\nname: [unclosed\n---\n")


def test_competence_attestation_wire_value_is_snake_case() -> None:
    assert TokenType.COMPETENCE_ATTESTATION.value == "competence_attestation"
    schema_path = Path(__file__).resolve().parents[3] / "schemas" / "vcp-manifest-v2.schema.json"
    with open(schema_path, encoding="utf-8") as handle:
        schema = json.load(handle)
    assert "competence_attestation" in schema["properties"]["token_type"]["enum"]
