"""
VCP Hook Deployment Configuration Loader.

Parses a YAML deployment config and builds a populated HookRegistry.
Supports built-in hook factories and custom hooks via dotted Python paths.

YAML format::

    version: "1.0"
    hooks:
      - name: scope-filter
        type: pre_inject
        builtin: scope_filter_hook
        priority: 95
        timeout_ms: 2000
        enabled: true

      - name: persona-select
        type: post_select
        builtin: persona_select_hook
        priority: 80

      - name: my-custom-hook
        type: pre_inject
        action: mypackage.hooks.my_action
        priority: 50
        description: "Custom hook"

Load and build::

    from vcp.hooks.config import load_from_yaml, build_registry

    config = load_from_yaml("hooks.yaml")
    registry = build_registry(config)

Spec reference: VCP_HOOKS.md section 6 (deployment configuration).
"""

from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .builtin import (
    adherence_escalate_hook,
    audit_hook,
    persona_select_hook,
    scope_filter_hook,
)
from .registry import HookRegistry
from .types import Hook, HookType

logger = logging.getLogger(__name__)

# Allowlist of module prefixes permitted for custom hook imports.
# If hook configs ever come from an untrusted source, this prevents
# arbitrary code execution via the ``action`` field.
ALLOWED_IMPORT_PREFIXES: tuple[str, ...] = ("vcp.hooks.",)

# Map YAML string → built-in factory callable
_BUILTIN_FACTORIES: dict[str, Any] = {
    "persona_select_hook": persona_select_hook,
    "adherence_escalate_hook": adherence_escalate_hook,
    "scope_filter_hook": scope_filter_hook,
    "audit_hook": audit_hook,
}

# Map YAML string → HookType enum
_HOOK_TYPE_MAP: dict[str, HookType] = {t.value: t for t in HookType}


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------


@dataclass
class HookEntryConfig:
    """Configuration for a single hook entry in the YAML manifest."""

    name: str
    type: str
    priority: int = 50
    timeout_ms: int = 5000
    enabled: bool = True
    description: str = ""
    builtin: str | None = None   # name of a built-in factory function
    action: str | None = None    # dotted Python path to a HookAction callable
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DeploymentConfig:
    """Parsed representation of a VCP hook deployment YAML file."""

    version: str = "1.0"
    hooks: list[HookEntryConfig] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class HookConfigError(Exception):
    """Raised when a hook configuration is malformed or unresolvable."""


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------


def load_from_yaml(path: str | Path) -> DeploymentConfig:
    """Load hook deployment config from a YAML file.

    Args:
        path: Path to the YAML configuration file.

    Returns:
        Parsed DeploymentConfig.

    Raises:
        ImportError: If PyYAML is not installed.
        FileNotFoundError: If the file does not exist.
        HookConfigError: If the YAML structure is invalid.
    """
    try:
        import yaml
    except ImportError:
        raise ImportError(
            "PyYAML is required to load hook configs from YAML. "
            "Install it: pip install pyyaml"
        ) from None

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Hook config not found: {path}")

    with path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    logger.debug("hook.config.loaded: path=%s", path)
    return _parse_config(raw)


def load_from_dict(data: dict[str, Any]) -> DeploymentConfig:
    """Load hook deployment config from an already-parsed dict.

    Useful when the caller has already parsed YAML or is constructing
    config programmatically.

    Args:
        data: Dict matching the YAML schema.

    Returns:
        Parsed DeploymentConfig.

    Raises:
        HookConfigError: If the dict structure is invalid.
    """
    return _parse_config(data)


# ---------------------------------------------------------------------------
# Registry builder
# ---------------------------------------------------------------------------


def build_registry(config: DeploymentConfig) -> HookRegistry:
    """Build a HookRegistry from a DeploymentConfig.

    All hooks are registered at deployment scope (not session scope).
    Hooks are validated by HookRegistry.register before being added.

    Args:
        config: Parsed deployment config.

    Returns:
        Populated HookRegistry ready for use with HookExecutor.

    Raises:
        HookConfigError: If any hook cannot be instantiated.
    """
    registry = HookRegistry()

    for entry in config.hooks:
        hook = _instantiate_hook(entry)
        registry.register(hook, scope="deployment")
        logger.info(
            "hook.config.registered: name=%s type=%s priority=%d enabled=%s",
            hook.name,
            hook.type.value,
            hook.priority,
            hook.enabled,
        )

    return registry


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _parse_config(raw: Any) -> DeploymentConfig:
    if not isinstance(raw, dict):
        raise HookConfigError("Hook config must be a YAML mapping at the top level.")

    version = str(raw.get("version", "1.0"))
    hooks_raw = raw.get("hooks", [])

    if not isinstance(hooks_raw, list):
        raise HookConfigError("'hooks' must be a list of hook entries.")

    hooks = [_parse_hook_entry(entry, idx) for idx, entry in enumerate(hooks_raw)]
    return DeploymentConfig(version=version, hooks=hooks)


def _parse_hook_entry(entry: Any, idx: int) -> HookEntryConfig:
    if not isinstance(entry, dict):
        raise HookConfigError(
            f"Hook entry at index {idx} must be a mapping, got: {type(entry).__name__}"
        )

    name = entry.get("name")
    if not name or not isinstance(name, str):
        raise HookConfigError(f"Hook entry at index {idx} missing required field: 'name'")

    hook_type = entry.get("type")
    if not hook_type or not isinstance(hook_type, str):
        raise HookConfigError(f"Hook '{name}' missing required field: 'type'")

    builtin = entry.get("builtin")
    action = entry.get("action")

    if not builtin and not action:
        raise HookConfigError(
            f"Hook '{name}' must specify either 'builtin' or 'action'."
        )
    if builtin and action:
        raise HookConfigError(
            f"Hook '{name}' cannot specify both 'builtin' and 'action'. Choose one."
        )

    return HookEntryConfig(
        name=name,
        type=hook_type,
        priority=int(entry.get("priority", 50)),
        timeout_ms=int(entry.get("timeout_ms", 5000)),
        enabled=bool(entry.get("enabled", True)),
        description=str(entry.get("description", "")),
        builtin=builtin or None,
        action=action or None,
        metadata=dict(entry.get("metadata", {})),
    )


def _instantiate_hook(cfg: HookEntryConfig) -> Hook:
    """Create a Hook instance from a config entry."""
    hook_type = _HOOK_TYPE_MAP.get(cfg.type)
    if hook_type is None:
        valid = ", ".join(sorted(_HOOK_TYPE_MAP.keys()))
        raise HookConfigError(
            f"Unknown hook type '{cfg.type}' in hook '{cfg.name}'. "
            f"Valid types: {valid}"
        )

    if cfg.builtin:
        return _instantiate_builtin(cfg, hook_type)

    # Custom action via dotted import path
    action = _import_dotted_path(cfg.action, cfg.name)  # type: ignore[arg-type]
    return Hook(
        name=cfg.name,
        type=hook_type,
        priority=cfg.priority,
        action=action,
        timeout_ms=cfg.timeout_ms,
        enabled=cfg.enabled,
        description=cfg.description,
        metadata=cfg.metadata,
    )


def _instantiate_builtin(cfg: HookEntryConfig, hook_type: HookType) -> Hook:
    """Instantiate a built-in hook, applying config overrides."""
    factory = _BUILTIN_FACTORIES.get(cfg.builtin)  # type: ignore[arg-type]
    if factory is None:
        valid = ", ".join(sorted(_BUILTIN_FACTORIES.keys()))
        raise HookConfigError(
            f"Unknown builtin '{cfg.builtin}' in hook '{cfg.name}'. "
            f"Available builtins: {valid}"
        )

    # Factory sets sensible defaults; config values override them
    hook: Hook = factory(priority=cfg.priority, timeout_ms=cfg.timeout_ms)

    # Override mutable fields from config
    hook.name = cfg.name
    hook.type = hook_type
    hook.enabled = cfg.enabled
    if cfg.description:
        hook.description = cfg.description
    if cfg.metadata:
        hook.metadata = cfg.metadata

    return hook


def _import_dotted_path(
    dotted: str,
    hook_name: str,
) -> Any:
    """Import a callable from a dotted Python module path.

    Only modules whose dotted path starts with one of
    ``ALLOWED_IMPORT_PREFIXES`` are permitted.
    """
    allowed_prefixes = ALLOWED_IMPORT_PREFIXES
    if "." not in dotted:
        raise HookConfigError(
            f"Hook '{hook_name}': action '{dotted}' must be a dotted path "
            f"to a callable (e.g. 'mypackage.hooks.my_action')."
        )

    if not any(dotted.startswith(prefix) for prefix in allowed_prefixes):
        raise HookConfigError(
            f"Hook '{hook_name}': import '{dotted}' is not under any "
            f"allowed module prefix ({', '.join(allowed_prefixes)}). "
            f"Add the prefix to ALLOWED_IMPORT_PREFIXES if this is intentional."
        )

    module_path, attr = dotted.rsplit(".", 1)
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise HookConfigError(
            f"Hook '{hook_name}': cannot import module '{module_path}': {exc}"
        ) from exc

    action = getattr(module, attr, None)
    if action is None:
        raise HookConfigError(
            f"Hook '{hook_name}': module '{module_path}' has no attribute '{attr}'."
        )
    if not callable(action):
        raise HookConfigError(
            f"Hook '{hook_name}': '{dotted}' is not callable (got {type(action).__name__})."
        )

    return action
