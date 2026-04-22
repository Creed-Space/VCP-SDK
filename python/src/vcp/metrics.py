"""
VCP Metrics Module

Optional Prometheus instrumentation for all four VCP layers.
Falls back to no-ops if prometheus_client is not installed.

Usage::

    from vcp.metrics import (
        vcp_bundle_verifications_total,
        vcp_context_encodes_total,
        track_duration,
    )

Install optional dependency::

    uv add prometheus_client
"""

from __future__ import annotations

import contextlib
from collections.abc import Generator
from typing import Any

# ---------------------------------------------------------------------------
# Optional prometheus_client import with no-op fallback
# ---------------------------------------------------------------------------

try:
    import prometheus_client as _prom

    _PROMETHEUS_AVAILABLE: bool = True
except ImportError:
    _prom = None
    _PROMETHEUS_AVAILABLE = False


class _NoOpMetric:
    """No-op metric that silently discards all observations."""

    def inc(self, amount: float = 1) -> None:  # noqa: ARG002
        pass

    def dec(self, amount: float = 1) -> None:  # noqa: ARG002
        pass

    def set(self, value: float) -> None:  # noqa: ARG002
        pass

    def observe(self, value: float) -> None:  # noqa: ARG002
        pass

    def labels(self, **kwargs: Any) -> _NoOpMetric:  # noqa: ARG002
        return self


_NOOP = _NoOpMetric()


def _counter(name: str, documentation: str, labelnames: list[str] | None = None) -> Any:
    if _PROMETHEUS_AVAILABLE:
        return _prom.Counter(name, documentation, labelnames or [])
    return _NOOP


def _histogram(
    name: str,
    documentation: str,
    labelnames: list[str] | None = None,
    buckets: tuple[float, ...] | None = None,
) -> Any:
    if _PROMETHEUS_AVAILABLE:
        kwargs: dict[str, Any] = {}
        if buckets:
            kwargs["buckets"] = buckets
        return _prom.Histogram(name, documentation, labelnames or [], **kwargs)
    return _NOOP


def _gauge(name: str, documentation: str, labelnames: list[str] | None = None) -> Any:
    if _PROMETHEUS_AVAILABLE:
        return _prom.Gauge(name, documentation, labelnames or [])
    return _NOOP


# ---------------------------------------------------------------------------
# VCP/A — Adaptation Layer (Layer 4)
# ---------------------------------------------------------------------------

vcp_context_encodes_total = _counter(
    "vcp_context_encodes_total",
    "Total number of VCP context encode operations.",
)

vcp_context_encode_duration_seconds = _histogram(
    "vcp_context_encode_duration_seconds",
    "Duration of VCP context encode operations in seconds.",
    buckets=(0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0),
)

vcp_transitions_total = _counter(
    "vcp_transitions_total",
    "Total number of VCP context transitions detected.",
    labelnames=["severity"],
)

vcp_active_sessions = _gauge(
    "vcp_active_sessions",
    "Number of currently active VCP sessions.",
)

# ---------------------------------------------------------------------------
# VCP/T — Transport Layer (Layer 2)
# ---------------------------------------------------------------------------

vcp_bundle_verifications_total = _counter(
    "vcp_bundle_verifications_total",
    "Total number of VCP bundle verification attempts.",
    labelnames=["result"],
)

vcp_bundle_verify_duration_seconds = _histogram(
    "vcp_bundle_verify_duration_seconds",
    "Duration of VCP bundle verification in seconds.",
    buckets=(0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5),
)

# ---------------------------------------------------------------------------
# VCP/S — Semantics Layer (Layer 3)
# ---------------------------------------------------------------------------

vcp_csm1_parses_total = _counter(
    "vcp_csm1_parses_total",
    "Total number of CSM1 parse operations.",
    labelnames=["status"],
)

vcp_compositions_total = _counter(
    "vcp_compositions_total",
    "Total number of VCP persona composition operations.",
    labelnames=["status"],
)

# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------

vcp_hook_executions_total = _counter(
    "vcp_hook_executions_total",
    "Total number of VCP hook executions.",
    labelnames=["hook_type", "status"],
)

vcp_hook_duration_seconds = _histogram(
    "vcp_hook_duration_seconds",
    "Duration of individual VCP hook executions in seconds.",
    labelnames=["hook_type"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5),
)

# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

vcp_audit_events_total = _counter(
    "vcp_audit_events_total",
    "Total number of VCP audit log events.",
    labelnames=["event_type"],
)

# ---------------------------------------------------------------------------
# Identity Layer (Layer 1)
# ---------------------------------------------------------------------------

vcp_registry_size = _gauge(
    "vcp_registry_size",
    "Number of entries in the VCP token registry.",
)

vcp_token_lookups_total = _counter(
    "vcp_token_lookups_total",
    "Total number of VCP token lookup operations.",
    labelnames=["status"],
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@contextlib.contextmanager
def track_duration(metric: Any) -> Generator[None, None, None]:
    """Context manager to record elapsed wall-clock time on a histogram metric.

    Works with any object that has an ``observe(float)`` method, including
    Prometheus Histogram/Summary and :class:`_NoOpMetric`.

    Example::

        with track_duration(vcp_bundle_verify_duration_seconds):
            result = orchestrator.verify(bundle)
    """
    import time

    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        metric.observe(elapsed)


def is_prometheus_available() -> bool:
    """Return True if prometheus_client is installed and metrics are active."""
    return _PROMETHEUS_AVAILABLE


def get_metrics_summary() -> dict[str, Any]:
    """Return a dict of metric names and their current values (best-effort).

    When prometheus_client is not available, all values are ``None``.
    Useful for health-check endpoints or debug logging.
    """
    if not _PROMETHEUS_AVAILABLE:
        return {
            "prometheus_available": False,
            "note": "Install prometheus_client to enable metrics.",
        }

    return {
        "prometheus_available": True,
        "metrics": [
            "vcp_context_encodes_total",
            "vcp_context_encode_duration_seconds",
            "vcp_transitions_total",
            "vcp_active_sessions",
            "vcp_bundle_verifications_total",
            "vcp_bundle_verify_duration_seconds",
            "vcp_csm1_parses_total",
            "vcp_compositions_total",
            "vcp_hook_executions_total",
            "vcp_hook_duration_seconds",
            "vcp_audit_events_total",
            "vcp_registry_size",
            "vcp_token_lookups_total",
        ],
    }
