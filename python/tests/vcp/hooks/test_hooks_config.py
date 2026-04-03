"""
Tests for vcp.hooks.config — YAML deployment config loader.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from vcp.hooks.config import (
    DeploymentConfig,
    HookConfigError,
    build_registry,
    load_from_dict,
)
from vcp.hooks.registry import HookRegistry
from vcp.hooks.types import HookType

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _minimal_entry(
    name: str = "test-hook",
    hook_type: str = "pre_inject",
    builtin: str = "scope_filter_hook",
    **kwargs,
) -> dict:
    entry = {"name": name, "type": hook_type, "builtin": builtin}
    entry.update(kwargs)
    return entry


# ---------------------------------------------------------------------------
# load_from_dict — valid inputs
# ---------------------------------------------------------------------------


class TestLoadFromDict:
    def test_empty_hooks_list(self) -> None:
        config = load_from_dict({"version": "1.0", "hooks": []})
        assert isinstance(config, DeploymentConfig)
        assert config.hooks == []
        assert config.version == "1.0"

    def test_version_defaults_to_one(self) -> None:
        config = load_from_dict({"hooks": []})
        assert config.version == "1.0"

    def test_single_builtin_hook(self) -> None:
        config = load_from_dict({"hooks": [_minimal_entry()]})
        assert len(config.hooks) == 1
        entry = config.hooks[0]
        assert entry.name == "test-hook"
        assert entry.type == "pre_inject"
        assert entry.builtin == "scope_filter_hook"

    def test_all_builtin_hooks(self) -> None:
        builtins = [
            ("scope-filter", "pre_inject", "scope_filter_hook"),
            ("persona-select", "post_select", "persona_select_hook"),
            ("adherence-escalate", "on_transition", "adherence_escalate_hook"),
            ("audit", "pre_inject", "audit_hook"),
        ]
        hooks = [_minimal_entry(name, t, b) for name, t, b in builtins]
        config = load_from_dict({"hooks": hooks})
        assert len(config.hooks) == 4

    def test_priority_and_timeout_override(self) -> None:
        config = load_from_dict({
            "hooks": [_minimal_entry(priority=77, timeout_ms=3000)]
        })
        entry = config.hooks[0]
        assert entry.priority == 77
        assert entry.timeout_ms == 3000

    def test_enabled_false(self) -> None:
        config = load_from_dict({"hooks": [_minimal_entry(enabled=False)]})
        assert config.hooks[0].enabled is False

    def test_description_and_metadata(self) -> None:
        config = load_from_dict({
            "hooks": [_minimal_entry(
                description="A test hook",
                metadata={"team": "vcp"},
            )]
        })
        entry = config.hooks[0]
        assert entry.description == "A test hook"
        assert entry.metadata == {"team": "vcp"}

    def test_custom_action_path(self) -> None:
        entry = {"name": "custom", "type": "pre_inject", "action": "os.path.join"}
        config = load_from_dict({"hooks": [entry]})
        assert config.hooks[0].action == "os.path.join"
        assert config.hooks[0].builtin is None


# ---------------------------------------------------------------------------
# load_from_dict — invalid inputs
# ---------------------------------------------------------------------------


class TestLoadFromDictErrors:
    def test_not_a_dict(self) -> None:
        with pytest.raises(HookConfigError, match="mapping"):
            load_from_dict([1, 2, 3])  # type: ignore[arg-type]

    def test_hooks_not_a_list(self) -> None:
        with pytest.raises(HookConfigError, match="list"):
            load_from_dict({"hooks": "bad"})

    def test_missing_name(self) -> None:
        with pytest.raises(HookConfigError, match="name"):
            load_from_dict({"hooks": [{"type": "pre_inject", "builtin": "audit_hook"}]})

    def test_missing_type(self) -> None:
        with pytest.raises(HookConfigError, match="type"):
            load_from_dict({"hooks": [{"name": "x", "builtin": "audit_hook"}]})

    def test_neither_builtin_nor_action(self) -> None:
        with pytest.raises(HookConfigError, match="builtin.*action|action.*builtin"):
            load_from_dict({"hooks": [{"name": "x", "type": "pre_inject"}]})

    def test_both_builtin_and_action(self) -> None:
        with pytest.raises(HookConfigError, match="both"):
            load_from_dict({"hooks": [{
                "name": "x",
                "type": "pre_inject",
                "builtin": "audit_hook",
                "action": "os.getcwd",
            }]})

    def test_entry_not_dict(self) -> None:
        with pytest.raises(HookConfigError, match="mapping"):
            load_from_dict({"hooks": ["not-a-dict"]})


# ---------------------------------------------------------------------------
# build_registry — valid
# ---------------------------------------------------------------------------


class TestBuildRegistry:
    def test_returns_hook_registry(self) -> None:
        config = load_from_dict({"hooks": []})
        registry = build_registry(config)
        assert isinstance(registry, HookRegistry)

    def test_registers_scope_filter(self) -> None:
        config = load_from_dict({"hooks": [
            _minimal_entry("my-scope-filter", "pre_inject", "scope_filter_hook", priority=95)
        ]})
        registry = build_registry(config)
        assert registry.get_registered_count(scope="deployment") == 1

    def test_registers_all_builtins(self) -> None:
        config = load_from_dict({"hooks": [
            _minimal_entry("sf", "pre_inject", "scope_filter_hook"),
            _minimal_entry("ps", "post_select", "persona_select_hook"),
            _minimal_entry("ae", "on_transition", "adherence_escalate_hook"),
            _minimal_entry("au", "pre_inject", "audit_hook"),
        ]})
        registry = build_registry(config)
        assert registry.get_registered_count(scope="deployment") == 4

    def test_hook_type_override_on_builtin(self) -> None:
        """audit_hook defaults to pre_inject; config can override to on_violation."""
        config = load_from_dict({"hooks": [
            _minimal_entry("audit-violation", "on_violation", "audit_hook")
        ]})
        registry = build_registry(config)
        chain = registry.get_chain(HookType.ON_VIOLATION, "session-1")
        assert len(chain) == 1
        assert chain[0].name == "audit-violation"

    def test_disabled_hook_is_registered_but_skipped_by_executor(self) -> None:
        """Disabled hooks are registered; executor skips them at runtime."""
        config = load_from_dict({"hooks": [
            _minimal_entry("disabled", "pre_inject", "scope_filter_hook", enabled=False)
        ]})
        registry = build_registry(config)
        chain = registry.get_chain(HookType.PRE_INJECT, "s1")
        assert len(chain) == 1
        assert chain[0].enabled is False

    def test_priority_order_preserved(self) -> None:
        config = load_from_dict({"hooks": [
            _minimal_entry("low", "pre_inject", "audit_hook", priority=10),
            _minimal_entry("high", "pre_inject", "scope_filter_hook", priority=90),
        ]})
        registry = build_registry(config)
        chain = registry.get_chain(HookType.PRE_INJECT, "s1")
        assert chain[0].priority >= chain[1].priority

    def test_unknown_hook_type_raises(self) -> None:
        config = load_from_dict({"hooks": [
            _minimal_entry(hook_type="not_a_type")
        ]})
        with pytest.raises(HookConfigError, match="Unknown hook type"):
            build_registry(config)

    def test_unknown_builtin_raises(self) -> None:
        config = load_from_dict({"hooks": [
            _minimal_entry(builtin="not_a_builtin")
        ]})
        with pytest.raises(HookConfigError, match="Unknown builtin"):
            build_registry(config)

    def test_custom_action_from_vcp_module(self) -> None:
        """Smoke test for dotted import using an allowed vcp.* callable."""
        config = load_from_dict({"hooks": [{
            "name": "custom",
            "type": "pre_inject",
            "action": "vcp.audit._hash_for_privacy",
        }]})
        registry = build_registry(config)
        chain = registry.get_chain(HookType.PRE_INJECT, "s1")
        assert len(chain) == 1

    def test_custom_action_outside_allowlist_raises(self) -> None:
        config = load_from_dict({"hooks": [{
            "name": "bad",
            "type": "pre_inject",
            "action": "os.path.join",
        }]})
        with pytest.raises(HookConfigError, match="not under any allowed module prefix"):
            build_registry(config)

    def test_custom_action_bad_module_raises(self) -> None:
        config = load_from_dict({"hooks": [{
            "name": "bad",
            "type": "pre_inject",
            "action": "vcp.no_such_module.action",
        }]})
        with pytest.raises(HookConfigError, match="cannot import"):
            build_registry(config)

    def test_custom_action_bad_attr_raises(self) -> None:
        config = load_from_dict({"hooks": [{
            "name": "bad",
            "type": "pre_inject",
            "action": "vcp.audit.no_such_attr",
        }]})
        with pytest.raises(HookConfigError, match="no attribute"):
            build_registry(config)

    def test_custom_action_not_dotted_raises(self) -> None:
        config = load_from_dict({"hooks": [{
            "name": "bad",
            "type": "pre_inject",
            "action": "nodots",
        }]})
        with pytest.raises(HookConfigError, match="dotted path"):
            build_registry(config)


# ---------------------------------------------------------------------------
# load_from_yaml
# ---------------------------------------------------------------------------


class TestLoadFromYaml:
    def test_loads_valid_yaml_file(self, tmp_path: Path) -> None:
        yaml_content = textwrap.dedent("""\
            version: "1.0"
            hooks:
              - name: sf
                type: pre_inject
                builtin: scope_filter_hook
                priority: 95
                timeout_ms: 2000
                enabled: true
        """)
        yaml_file = tmp_path / "hooks.yaml"
        yaml_file.write_text(yaml_content)

        try:
            from vcp.hooks.config import load_from_yaml
            config = load_from_yaml(yaml_file)
            assert len(config.hooks) == 1
            assert config.hooks[0].name == "sf"
            assert config.hooks[0].priority == 95
        except ImportError:
            pytest.skip("PyYAML not installed")

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        from vcp.hooks.config import load_from_yaml
        try:
            with pytest.raises(FileNotFoundError):
                load_from_yaml(tmp_path / "nonexistent.yaml")
        except ImportError:
            pytest.skip("PyYAML not installed")


# ---------------------------------------------------------------------------
# Integration: config → registry → executor
# ---------------------------------------------------------------------------


class TestConfigToExecutorIntegration:
    def test_scope_filter_aborts_out_of_scope(self) -> None:
        from vcp.hooks.executor import HookExecutor
        from vcp.hooks.types import PreInjectEvent

        config = load_from_dict({"hooks": [
            _minimal_entry("sf", "pre_inject", "scope_filter_hook", priority=95)
        ]})
        registry = build_registry(config)
        executor = HookExecutor(registry)

        constitution = {"scope": {"environments": ["production"]}}
        result = executor.execute(
            HookType.PRE_INJECT,
            session_id="s1",
            context={},
            constitution=constitution,
            event=PreInjectEvent(),
            session_info={"environment": "staging"},
        )
        assert result.status == "aborted"

    def test_scope_filter_passes_matching_env(self) -> None:
        from vcp.hooks.executor import HookExecutor
        from vcp.hooks.types import PreInjectEvent

        config = load_from_dict({"hooks": [
            _minimal_entry("sf", "pre_inject", "scope_filter_hook", priority=95)
        ]})
        registry = build_registry(config)
        executor = HookExecutor(registry)

        constitution = {"scope": {"environments": ["production"]}}
        result = executor.execute(
            HookType.PRE_INJECT,
            session_id="s1",
            context={},
            constitution=constitution,
            event=PreInjectEvent(),
            session_info={"environment": "production"},
        )
        assert result.status == "completed"
