"""
Tests for vcp.metrics — Prometheus instrumentation layer.

Verifies no-op fallback behaviour, metric existence, track_duration helper,
and the get_metrics_summary / is_prometheus_available helpers.  All tests run
whether or not prometheus_client is installed.
"""

from __future__ import annotations

import time
import unittest.mock as mock

import pytest

import vcp.metrics as m


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _has_observe(obj: object) -> bool:
    return callable(getattr(obj, "observe", None))


def _has_inc(obj: object) -> bool:
    return callable(getattr(obj, "inc", None))


def _has_labels(obj: object) -> bool:
    return callable(getattr(obj, "labels", None))


# ---------------------------------------------------------------------------
# No-op metric tests
# ---------------------------------------------------------------------------


class TestNoOpMetric:
    def test_inc_does_not_raise(self) -> None:
        noop = m._NoOpMetric()
        noop.inc()
        noop.inc(5)

    def test_dec_does_not_raise(self) -> None:
        noop = m._NoOpMetric()
        noop.dec()
        noop.dec(2)

    def test_set_does_not_raise(self) -> None:
        noop = m._NoOpMetric()
        noop.set(42.0)

    def test_observe_does_not_raise(self) -> None:
        noop = m._NoOpMetric()
        noop.observe(0.001)

    def test_labels_returns_self(self) -> None:
        noop = m._NoOpMetric()
        assert noop.labels(result="VALID") is noop


# ---------------------------------------------------------------------------
# Metric existence — all public metric objects must expose the right interface
# ---------------------------------------------------------------------------


COUNTER_METRICS = [
    m.vcp_context_encodes_total,
    m.vcp_transitions_total,
    m.vcp_bundle_verifications_total,
    m.vcp_csm1_parses_total,
    m.vcp_compositions_total,
    m.vcp_hook_executions_total,
    m.vcp_audit_events_total,
    m.vcp_token_lookups_total,
]

HISTOGRAM_METRICS = [
    m.vcp_context_encode_duration_seconds,
    m.vcp_bundle_verify_duration_seconds,
    m.vcp_hook_duration_seconds,
]

GAUGE_METRICS = [
    m.vcp_active_sessions,
    m.vcp_registry_size,
]


@pytest.mark.parametrize("metric", COUNTER_METRICS)
def test_counter_has_inc(metric: object) -> None:
    assert _has_inc(metric) or _has_labels(metric)


@pytest.mark.parametrize("metric", HISTOGRAM_METRICS)
def test_histogram_has_observe(metric: object) -> None:
    assert _has_observe(metric) or _has_labels(metric)


@pytest.mark.parametrize("metric", GAUGE_METRICS)
def test_gauge_has_set(metric: object) -> None:
    assert callable(getattr(metric, "set", None)) or _has_labels(metric)


# ---------------------------------------------------------------------------
# Labelled counter smoke tests (no-op path always works)
# ---------------------------------------------------------------------------


def test_bundle_verifications_with_label() -> None:
    labelled = m.vcp_bundle_verifications_total.labels(result="VALID")
    labelled.inc()  # must not raise


def test_transitions_with_label() -> None:
    labelled = m.vcp_transitions_total.labels(severity="MAJOR")
    labelled.inc()


def test_hook_executions_with_label() -> None:
    labelled = m.vcp_hook_executions_total.labels(hook_type="pre_inject", status="completed")
    labelled.inc()


# ---------------------------------------------------------------------------
# track_duration context manager
# ---------------------------------------------------------------------------


class TestTrackDuration:
    def test_calls_observe_with_elapsed(self) -> None:
        fake_metric = mock.MagicMock()
        with m.track_duration(fake_metric):
            time.sleep(0.01)
        fake_metric.observe.assert_called_once()
        elapsed = fake_metric.observe.call_args[0][0]
        assert elapsed >= 0.005, f"elapsed={elapsed} seems too short"

    def test_calls_observe_even_on_exception(self) -> None:
        fake_metric = mock.MagicMock()
        with pytest.raises(ValueError):
            with m.track_duration(fake_metric):
                raise ValueError("boom")
        fake_metric.observe.assert_called_once()

    def test_works_with_noop_metric(self) -> None:
        noop = m._NoOpMetric()
        with m.track_duration(noop):
            pass  # must not raise


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class TestHelpers:
    def test_is_prometheus_available_returns_bool(self) -> None:
        result = m.is_prometheus_available()
        assert isinstance(result, bool)

    def test_get_metrics_summary_returns_dict(self) -> None:
        summary = m.get_metrics_summary()
        assert isinstance(summary, dict)
        assert "prometheus_available" in summary

    def test_get_metrics_summary_without_prometheus(self) -> None:
        with mock.patch.object(m, "_PROMETHEUS_AVAILABLE", False):
            summary = m.get_metrics_summary()
        assert summary["prometheus_available"] is False
        assert "note" in summary

    def test_get_metrics_summary_with_prometheus(self) -> None:
        with mock.patch.object(m, "_PROMETHEUS_AVAILABLE", True):
            summary = m.get_metrics_summary()
        assert summary["prometheus_available"] is True
        assert "metrics" in summary
        assert len(summary["metrics"]) > 0


# ---------------------------------------------------------------------------
# Import from top-level vcp package
# ---------------------------------------------------------------------------


def test_importable_from_vcp_package() -> None:
    from vcp import (
        get_metrics_summary,
        is_prometheus_available,
        track_duration,
        vcp_bundle_verifications_total,
        vcp_context_encodes_total,
        vcp_transitions_total,
    )

    assert callable(is_prometheus_available)
    assert callable(get_metrics_summary)
    assert callable(track_duration)
    assert _has_inc(vcp_context_encodes_total) or _has_labels(vcp_context_encodes_total)
