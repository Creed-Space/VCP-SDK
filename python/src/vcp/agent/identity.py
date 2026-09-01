"""Runtime identity and package-collision diagnostics."""

from __future__ import annotations

from importlib import metadata
from pathlib import Path

from .contracts import Contract
from .schema import agent_runtime_schema_digest


class RuntimeIdentity(Contract):
    distribution: str
    version: str
    implementation: str
    module_path: str
    supported_profiles: tuple[str, ...]
    schema_digest: str
    discovered_distributions: tuple[str, ...]
    collision: bool
    safe_next: tuple[str, ...]


def _vcp_distributions() -> tuple[str, ...]:
    discovered = metadata.packages_distributions().get("vcp", [])
    return tuple(sorted({name for name in discovered if name}))


def runtime_identity() -> RuntimeIdentity:
    """Describe the imported runtime before any feature is used."""

    distributions = _vcp_distributions()
    try:
        package_version = metadata.version("value-context-protocol")
    except metadata.PackageNotFoundError:
        package_version = "4.2.0+source"
    collision = len(distributions) > 1
    safe_next = (
        (("Remove one VCP distribution in a clean environment, then rerun `vcp doctor`"),)
        if collision
        else ()
    )
    return RuntimeIdentity(
        distribution="value-context-protocol",
        version=package_version,
        implementation="project-maintained VCP-SDK Python agent runtime candidate",
        module_path=str(Path(__file__).resolve().parents[1]),
        supported_profiles=(
            "observe@0.1.0",
            "controlled@0.1.0",
            "accretive@0.1.0",
        ),
        schema_digest=agent_runtime_schema_digest(),
        discovered_distributions=distributions,
        collision=collision,
        safe_next=safe_next,
    )
