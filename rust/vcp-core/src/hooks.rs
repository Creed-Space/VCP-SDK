//! VCP Hook System for the adaptation pipeline.
//!
//! Implements the six hook types defined in the VCP Hook System Specification:
//! `pre_inject`, `post_select`, `on_transition`, `on_conflict`, `on_violation`,
//! and `periodic`. Hooks execute deterministically in priority-descending order
//! and produce structured results that control pipeline flow.
//!
//! # Architecture
//!
//! - [`HookRegistry`] stores hooks at deployment or session scope.
//! - [`HookExecutor`] runs the merged chain for a given hook type and session.
//! - [`HookHandler`] is the trait that hook implementations must satisfy.
//!
//! # Example
//!
//! ```
//! use vcp_core::hooks::{
//!     Hook, HookAction, HookExecutor, HookHandler, HookInput, HookRegistry,
//!     HookResult, HookScope, HookType,
//! };
//! use std::collections::HashMap;
//! use std::time::Duration;
//!
//! struct LoggingHook;
//!
//! impl HookHandler for LoggingHook {
//!     fn execute(&self, _input: &HookInput) -> HookResult {
//!         HookResult {
//!             action: HookAction::Continue,
//!             annotations: HashMap::new(),
//!             duration: Duration::ZERO,
//!         }
//!     }
//! }
//!
//! let mut registry = HookRegistry::new();
//! registry.register(
//!     Hook {
//!         name: "my-logger".into(),
//!         hook_type: HookType::PreInject,
//!         priority: 50,
//!         handler: Box::new(LoggingHook),
//!         timeout: Duration::from_millis(5000),
//!         enabled: true,
//!         description: "Logs pre-inject events".into(),
//!     },
//!     HookScope::Deployment,
//!     None,
//! ).unwrap();
//!
//! let input = HookInput {
//!     context: serde_json::json!({}),
//!     constitution: serde_json::json!({}),
//!     event: serde_json::json!({}),
//!     session_id: "sess-1".into(),
//!     chain_state: HashMap::new(),
//! };
//!
//! let executor = HookExecutor::new(&registry);
//! let result = executor.execute(HookType::PreInject, "sess-1", input);
//! assert!(result.completed);
//! ```

use std::collections::HashMap;
use std::panic::{self, AssertUnwindSafe};
use std::time::{Duration, Instant};

use crate::error::{VcpError, VcpResult};

// ── Hook types ──────────────────────────────────────────────

/// The six hook types from the VCP Hook System Specification.
///
/// Each type corresponds to a distinct interception point in the
/// adaptation pipeline.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum HookType {
    /// Before a constitution is injected into LLM context.
    PreInject,
    /// After the adaptation layer has selected a constitution.
    PostSelect,
    /// A state machine transition in the context tracker.
    OnTransition,
    /// A conflict is detected during constitution composition.
    OnConflict,
    /// A rule violation is detected in LLM output.
    OnViolation,
    /// A timer fires at a configured interval.
    Periodic,
}

impl std::fmt::Display for HookType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let label = match self {
            HookType::PreInject => "pre_inject",
            HookType::PostSelect => "post_select",
            HookType::OnTransition => "on_transition",
            HookType::OnConflict => "on_conflict",
            HookType::OnViolation => "on_violation",
            HookType::Periodic => "periodic",
        };
        f.write_str(label)
    }
}

// ── Hook action / result ────────────────────────────────────

/// Result status from a hook execution, controlling pipeline flow.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum HookAction {
    /// No change. Pass to next hook in the chain.
    Continue,
    /// Stop the chain and cancel the pipeline operation.
    Abort {
        /// Human-readable justification for the abort.
        reason: String,
    },
    /// Pass modified context/constitution to the next hook.
    Modify(serde_json::Value),
}

/// Input provided to a hook handler during chain execution.
#[derive(Debug, Clone)]
pub struct HookInput {
    /// The current VCP context object (may have been modified by previous hooks).
    pub context: serde_json::Value,
    /// The active or candidate constitution.
    pub constitution: serde_json::Value,
    /// Type-specific event payload.
    pub event: serde_json::Value,
    /// Session identifier.
    pub session_id: String,
    /// Mutable key-value store shared across hooks in a single chain execution.
    pub chain_state: HashMap<String, serde_json::Value>,
}

/// Result returned from a hook execution.
#[derive(Debug, Clone)]
pub struct HookResult {
    /// The action controlling pipeline flow.
    pub action: HookAction,
    /// Metadata attached to the pipeline event for audit.
    pub annotations: HashMap<String, serde_json::Value>,
    /// Actual execution time (set by the executor).
    pub duration: Duration,
}

// ── Hook handler trait ──────────────────────────────────────

/// Trait that hook implementations must satisfy.
///
/// Handlers must be `Send + Sync` to support registration from
/// multiple threads, though chain execution itself is sequential.
pub trait HookHandler: Send + Sync {
    /// Execute this hook against the given input.
    fn execute(&self, input: &HookInput) -> HookResult;
}

// ── Hook definition ─────────────────────────────────────────

/// A registered hook binding a handler to an interception point.
pub struct Hook {
    /// Unique name within scope. Must match `[a-z0-9_-]{1,64}`.
    pub name: String,
    /// Which interception point this hook binds to.
    pub hook_type: HookType,
    /// Execution priority: 0-100 inclusive, higher runs first.
    pub priority: u8,
    /// The function to execute.
    pub handler: Box<dyn HookHandler>,
    /// Maximum execution time. Must be 1-30000ms.
    pub timeout: Duration,
    /// Whether this hook is active. Disabled hooks are skipped.
    pub enabled: bool,
    /// Human-readable purpose description.
    pub description: String,
}

// Hook cannot derive Debug because of the trait object, so implement manually.
impl std::fmt::Debug for Hook {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("Hook")
            .field("name", &self.name)
            .field("hook_type", &self.hook_type)
            .field("priority", &self.priority)
            .field("timeout", &self.timeout)
            .field("enabled", &self.enabled)
            .field("description", &self.description)
            .finish_non_exhaustive()
    }
}

// ── Scope ───────────────────────────────────────────────────

/// Scope of hook registration.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HookScope {
    /// Global hooks that apply to all sessions.
    Deployment,
    /// Hooks scoped to a single user/agent session.
    Session,
}

// ── Chain result ────────────────────────────────────────────

/// Result of executing an entire hook chain.
#[derive(Debug)]
pub struct ChainResult {
    /// Whether the chain completed without an abort.
    pub completed: bool,
    /// Name of the hook that aborted the chain, if any.
    pub aborted_by: Option<String>,
    /// Human-readable reason for the abort, if any.
    pub abort_reason: Option<String>,
    /// Modified context value if any hook returned `Modify`.
    pub modified_context: Option<serde_json::Value>,
    /// Modified constitution value if any hook returned `Modify`.
    pub modified_constitution: Option<serde_json::Value>,
    /// Ordered list of (`hook_name`, result) pairs for each executed hook.
    pub results: Vec<(String, HookResult)>,
}

// ── Hook name validation regex ──────────────────────────────

/// Returns true if `name` matches the required pattern `[a-z0-9_-]{1,64}`.
fn is_valid_hook_name(name: &str) -> bool {
    // Using a simple character check instead of pulling in regex for this alone
    // would be fine, but the spec is explicit about the pattern.
    if name.is_empty() || name.len() > 64 {
        return false;
    }
    name.chars()
        .all(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || c == '_' || c == '-')
}

// ── HookRegistry ────────────────────────────────────────────

/// Central registry for hooks at deployment and session scopes.
///
/// Deployment hooks execute before session hooks at the same priority
/// level, ensuring organizational policies take precedence.
pub struct HookRegistry {
    deployment_hooks: HashMap<HookType, Vec<Hook>>,
    session_hooks: HashMap<String, HashMap<HookType, Vec<Hook>>>,
}

impl std::fmt::Debug for HookRegistry {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("HookRegistry")
            .field("deployment_hook_count", &self.deployment_hook_count())
            .field("session_count", &self.session_hooks.len())
            .finish_non_exhaustive()
    }
}

impl Default for HookRegistry {
    fn default() -> Self {
        Self::new()
    }
}

impl HookRegistry {
    /// Create an empty hook registry.
    pub fn new() -> Self {
        Self {
            deployment_hooks: HashMap::new(),
            session_hooks: HashMap::new(),
        }
    }

    /// Register a hook at the given scope.
    ///
    /// For session-scoped hooks, `session_id` must be `Some`.
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::HookError`] if:
    /// - The hook name is invalid (does not match `[a-z0-9_-]{1,64}`).
    /// - The priority is outside the range `[0, 100]`.
    /// - The timeout is outside the range `[1, 30000]` ms.
    /// - A hook with the same name is already registered in the target scope.
    /// - `scope` is `Session` but `session_id` is `None`.
    pub fn register(
        &mut self,
        hook: Hook,
        scope: HookScope,
        session_id: Option<&str>,
    ) -> VcpResult<()> {
        self.validate(&hook)?;

        match scope {
            HookScope::Deployment => {
                let hooks = self
                    .deployment_hooks
                    .entry(hook.hook_type)
                    .or_default();

                if hooks.iter().any(|h| h.name == hook.name) {
                    return Err(VcpError::HookError(format!(
                        "hook '{}' already registered in deployment scope",
                        hook.name
                    )));
                }

                hooks.push(hook);
                // Sort descending by priority (higher runs first).
                hooks.sort_by(|a, b| b.priority.cmp(&a.priority));
            }
            HookScope::Session => {
                let sid = session_id.ok_or_else(|| {
                    VcpError::HookError(
                        "session_id is required for session-scoped hooks".into(),
                    )
                })?;

                let session_map = self
                    .session_hooks
                    .entry(sid.to_string())
                    .or_default();

                let hooks = session_map.entry(hook.hook_type).or_default();

                if hooks.iter().any(|h| h.name == hook.name) {
                    return Err(VcpError::HookError(format!(
                        "hook '{}' already registered in session scope for '{}'",
                        hook.name, sid
                    )));
                }

                hooks.push(hook);
                hooks.sort_by(|a, b| b.priority.cmp(&a.priority));
            }
        }

        Ok(())
    }

    /// Remove a hook by name from the given scope.
    ///
    /// This is a no-op if no hook with the given name exists.
    pub fn deregister(&mut self, name: &str, scope: HookScope, session_id: Option<&str>) {
        match scope {
            HookScope::Deployment => {
                for hooks in self.deployment_hooks.values_mut() {
                    hooks.retain(|h| h.name != name);
                }
            }
            HookScope::Session => {
                if let Some(sid) = session_id {
                    if let Some(session_map) = self.session_hooks.get_mut(sid) {
                        for hooks in session_map.values_mut() {
                            hooks.retain(|h| h.name != name);
                        }
                    }
                }
            }
        }
    }

    /// Get the merged hook chain for a given type and session.
    ///
    /// Deployment hooks come before session hooks at equal priority,
    /// ensuring organizational policies take precedence over session
    /// customizations.
    pub fn get_chain(&self, hook_type: HookType, session_id: &str) -> Vec<&Hook> {
        let deployment = self
            .deployment_hooks
            .get(&hook_type)
            .map_or(&[][..], |v| v.as_slice());

        let session = self
            .session_hooks
            .get(session_id)
            .and_then(|m| m.get(&hook_type))
            .map_or(&[][..], |v| v.as_slice());

        Self::merge_by_priority(deployment, session)
    }

    /// Merge two priority-sorted hook slices, preferring deployment hooks
    /// at equal priority (stable merge).
    fn merge_by_priority<'a>(deployment: &'a [Hook], session: &'a [Hook]) -> Vec<&'a Hook> {
        let mut result = Vec::with_capacity(deployment.len() + session.len());
        let (mut d, mut s) = (0, 0);

        while d < deployment.len() && s < session.len() {
            if deployment[d].priority >= session[s].priority {
                result.push(&deployment[d]);
                d += 1;
            } else {
                result.push(&session[s]);
                s += 1;
            }
        }

        for hook in &deployment[d..] {
            result.push(hook);
        }
        for hook in &session[s..] {
            result.push(hook);
        }

        result
    }

    /// Validate a hook definition before registration.
    #[allow(clippy::unused_self)] // Method by design; will use self for future cross-validation.
    fn validate(&self, hook: &Hook) -> VcpResult<()> {
        if !is_valid_hook_name(&hook.name) {
            return Err(VcpError::HookError(format!(
                "invalid hook name '{}': must match [a-z0-9_-]{{1,64}}",
                hook.name
            )));
        }

        // Priority is u8 so it cannot be negative, but we check the upper bound.
        if hook.priority > 100 {
            return Err(VcpError::HookError(format!(
                "priority must be 0-100, got {}",
                hook.priority
            )));
        }

        let timeout_ms = hook.timeout.as_millis();
        if !(1..=30_000).contains(&timeout_ms) {
            return Err(VcpError::HookError(format!(
                "timeout must be 1-30000ms, got {timeout_ms}ms",
            )));
        }

        Ok(())
    }

    /// Total number of deployment-scoped hooks across all types.
    fn deployment_hook_count(&self) -> usize {
        self.deployment_hooks.values().map(Vec::len).sum()
    }
}

// ── HookExecutor ────────────────────────────────────────────

/// Executes hook chains from a [`HookRegistry`].
///
/// The executor runs hooks sequentially in priority-descending order,
/// passing (possibly modified) context forward through the chain.
pub struct HookExecutor<'a> {
    registry: &'a HookRegistry,
}

impl<'a> HookExecutor<'a> {
    /// Create an executor backed by the given registry.
    pub fn new(registry: &'a HookRegistry) -> Self {
        Self { registry }
    }

    /// Execute the hook chain for the given type and session.
    ///
    /// # Chain semantics
    ///
    /// - Hooks run in priority-descending order (deployment before session at equal priority).
    /// - Disabled hooks are skipped.
    /// - `Continue` passes through unchanged.
    /// - `Abort` halts the chain immediately.
    /// - `Modify` updates the context/constitution for subsequent hooks.
    /// - Panics in handlers are caught via `catch_unwind` and treated as `Continue`.
    /// - Timeout enforcement is best-effort (the handler runs synchronously; the
    ///   duration is recorded but cannot be pre-empted in a sync context).
    pub fn execute(
        &self,
        hook_type: HookType,
        session_id: &str,
        mut input: HookInput,
    ) -> ChainResult {
        let chain = self.registry.get_chain(hook_type, session_id);
        let mut results: Vec<(String, HookResult)> = Vec::new();
        let mut modified_context: Option<serde_json::Value> = None;
        let mut modified_constitution: Option<serde_json::Value> = None;

        for hook in &chain {
            if !hook.enabled {
                continue;
            }

            let start = Instant::now();

            // Execute with panic safety. We use AssertUnwindSafe because
            // HookInput contains types that are not UnwindSafe by default,
            // but we accept this for the fail-open semantics required by spec.
            let panic_result =
                panic::catch_unwind(AssertUnwindSafe(|| hook.handler.execute(&input)));

            let elapsed = start.elapsed();

            let hook_result = match panic_result {
                Ok(mut result) => {
                    result.duration = elapsed;
                    result
                }
                Err(_) => {
                    // Spec: exception -> treat as Continue, chain continues.
                    HookResult {
                        action: HookAction::Continue,
                        annotations: HashMap::new(),
                        duration: elapsed,
                    }
                }
            };

            match &hook_result.action {
                HookAction::Abort { reason } => {
                    let abort_reason = reason.clone();
                    let hook_name = hook.name.clone();
                    results.push((hook.name.clone(), hook_result));
                    return ChainResult {
                        completed: false,
                        aborted_by: Some(hook_name),
                        abort_reason: Some(abort_reason),
                        modified_context,
                        modified_constitution,
                        results,
                    };
                }
                HookAction::Modify(value) => {
                    // The Modify action carries a JSON value. By convention, if
                    // it has a "context" key we update the context; if it has a
                    // "constitution" key we update the constitution; otherwise
                    // we treat the whole value as a modified context.
                    if let Some(ctx) = value.get("context") {
                        input.context = ctx.clone();
                        modified_context = Some(ctx.clone());
                    }
                    if let Some(con) = value.get("constitution") {
                        input.constitution = con.clone();
                        modified_constitution = Some(con.clone());
                    }
                    // If neither key exists, treat entire value as modified context.
                    if value.get("context").is_none() && value.get("constitution").is_none() {
                        input.context = value.clone();
                        modified_context = Some(value.clone());
                    }
                }
                HookAction::Continue => {}
            }

            results.push((hook.name.clone(), hook_result));
        }

        ChainResult {
            completed: true,
            aborted_by: None,
            abort_reason: None,
            modified_context,
            modified_constitution,
            results,
        }
    }
}

// ── Tests ───────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    /// A simple handler that always returns Continue.
    struct ContinueHandler;
    impl HookHandler for ContinueHandler {
        fn execute(&self, _input: &HookInput) -> HookResult {
            HookResult {
                action: HookAction::Continue,
                annotations: HashMap::new(),
                duration: Duration::ZERO,
            }
        }
    }

    /// A handler that aborts with a given reason.
    struct AbortHandler {
        reason: String,
    }
    impl HookHandler for AbortHandler {
        fn execute(&self, _input: &HookInput) -> HookResult {
            HookResult {
                action: HookAction::Abort {
                    reason: self.reason.clone(),
                },
                annotations: HashMap::new(),
                duration: Duration::ZERO,
            }
        }
    }

    /// A handler that modifies the context.
    struct ModifyHandler {
        value: serde_json::Value,
    }
    impl HookHandler for ModifyHandler {
        fn execute(&self, _input: &HookInput) -> HookResult {
            HookResult {
                action: HookAction::Modify(self.value.clone()),
                annotations: HashMap::new(),
                duration: Duration::ZERO,
            }
        }
    }

    /// A handler that panics.
    struct PanicHandler;
    impl HookHandler for PanicHandler {
        fn execute(&self, _input: &HookInput) -> HookResult {
            panic!("intentional panic for testing");
        }
    }

    fn make_hook(name: &str, hook_type: HookType, priority: u8, handler: Box<dyn HookHandler>) -> Hook {
        Hook {
            name: name.to_string(),
            hook_type,
            priority,
            handler,
            timeout: Duration::from_millis(5000),
            enabled: true,
            description: format!("Test hook: {name}"),
        }
    }

    fn make_input() -> HookInput {
        HookInput {
            context: serde_json::json!({"key": "value"}),
            constitution: serde_json::json!({"rules": []}),
            event: serde_json::json!({}),
            session_id: "test-session".to_string(),
            chain_state: HashMap::new(),
        }
    }

    // ── Registration tests ──────────────────────────────────

    #[test]
    fn register_and_get_chain() {
        let mut reg = HookRegistry::new();
        reg.register(
            make_hook("hook-a", HookType::PreInject, 50, Box::new(ContinueHandler)),
            HookScope::Deployment,
            None,
        )
        .unwrap();

        let chain = reg.get_chain(HookType::PreInject, "any-session");
        assert_eq!(chain.len(), 1);
        assert_eq!(chain[0].name, "hook-a");
    }

    #[test]
    fn deregister_removes_hook() {
        let mut reg = HookRegistry::new();
        reg.register(
            make_hook("hook-a", HookType::PreInject, 50, Box::new(ContinueHandler)),
            HookScope::Deployment,
            None,
        )
        .unwrap();
        assert_eq!(reg.get_chain(HookType::PreInject, "s").len(), 1);

        reg.deregister("hook-a", HookScope::Deployment, None);
        assert_eq!(reg.get_chain(HookType::PreInject, "s").len(), 0);
    }

    #[test]
    fn invalid_name_rejected() {
        let mut reg = HookRegistry::new();
        let result = reg.register(
            make_hook("INVALID_UPPER", HookType::PreInject, 50, Box::new(ContinueHandler)),
            HookScope::Deployment,
            None,
        );
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("invalid hook name"));
    }

    #[test]
    fn empty_name_rejected() {
        let mut reg = HookRegistry::new();
        let result = reg.register(
            make_hook("", HookType::PreInject, 50, Box::new(ContinueHandler)),
            HookScope::Deployment,
            None,
        );
        assert!(result.is_err());
    }

    #[test]
    fn name_too_long_rejected() {
        let mut reg = HookRegistry::new();
        let long_name = "a".repeat(65);
        let result = reg.register(
            make_hook(&long_name, HookType::PreInject, 50, Box::new(ContinueHandler)),
            HookScope::Deployment,
            None,
        );
        assert!(result.is_err());
    }

    #[test]
    fn name_with_special_chars_rejected() {
        let mut reg = HookRegistry::new();
        let result = reg.register(
            make_hook("hook.with.dots", HookType::PreInject, 50, Box::new(ContinueHandler)),
            HookScope::Deployment,
            None,
        );
        assert!(result.is_err());
    }

    #[test]
    fn priority_ordering() {
        let mut reg = HookRegistry::new();
        reg.register(
            make_hook("low", HookType::PreInject, 10, Box::new(ContinueHandler)),
            HookScope::Deployment,
            None,
        )
        .unwrap();
        reg.register(
            make_hook("high", HookType::PreInject, 90, Box::new(ContinueHandler)),
            HookScope::Deployment,
            None,
        )
        .unwrap();
        reg.register(
            make_hook("mid", HookType::PreInject, 50, Box::new(ContinueHandler)),
            HookScope::Deployment,
            None,
        )
        .unwrap();

        let chain = reg.get_chain(HookType::PreInject, "s");
        assert_eq!(chain[0].name, "high");
        assert_eq!(chain[1].name, "mid");
        assert_eq!(chain[2].name, "low");
    }

    #[test]
    fn deployment_before_session_at_same_priority() {
        let mut reg = HookRegistry::new();
        reg.register(
            make_hook("session-hook", HookType::PreInject, 50, Box::new(ContinueHandler)),
            HookScope::Session,
            Some("sess-1"),
        )
        .unwrap();
        reg.register(
            make_hook("deploy-hook", HookType::PreInject, 50, Box::new(ContinueHandler)),
            HookScope::Deployment,
            None,
        )
        .unwrap();

        let chain = reg.get_chain(HookType::PreInject, "sess-1");
        assert_eq!(chain.len(), 2);
        // Deployment hook comes first at equal priority.
        assert_eq!(chain[0].name, "deploy-hook");
        assert_eq!(chain[1].name, "session-hook");
    }

    #[test]
    fn chain_continue_passes_through() {
        let mut reg = HookRegistry::new();
        reg.register(
            make_hook("h1", HookType::PreInject, 50, Box::new(ContinueHandler)),
            HookScope::Deployment,
            None,
        )
        .unwrap();
        reg.register(
            make_hook("h2", HookType::PreInject, 40, Box::new(ContinueHandler)),
            HookScope::Deployment,
            None,
        )
        .unwrap();

        let executor = HookExecutor::new(&reg);
        let result = executor.execute(HookType::PreInject, "s", make_input());

        assert!(result.completed);
        assert!(result.aborted_by.is_none());
        assert_eq!(result.results.len(), 2);
    }

    #[test]
    fn chain_abort_halts() {
        let mut reg = HookRegistry::new();
        reg.register(
            make_hook(
                "aborter",
                HookType::PreInject,
                90,
                Box::new(AbortHandler {
                    reason: "policy violation".into(),
                }),
            ),
            HookScope::Deployment,
            None,
        )
        .unwrap();
        reg.register(
            make_hook("should-not-run", HookType::PreInject, 10, Box::new(ContinueHandler)),
            HookScope::Deployment,
            None,
        )
        .unwrap();

        let executor = HookExecutor::new(&reg);
        let result = executor.execute(HookType::PreInject, "s", make_input());

        assert!(!result.completed);
        assert_eq!(result.aborted_by.as_deref(), Some("aborter"));
        assert_eq!(result.abort_reason.as_deref(), Some("policy violation"));
        // Only the aborting hook ran.
        assert_eq!(result.results.len(), 1);
    }

    #[test]
    fn chain_modify_transforms_context() {
        let modified_val = serde_json::json!({"context": {"modified": true}});
        let mut reg = HookRegistry::new();
        reg.register(
            make_hook(
                "modifier",
                HookType::PreInject,
                90,
                Box::new(ModifyHandler {
                    value: modified_val.clone(),
                }),
            ),
            HookScope::Deployment,
            None,
        )
        .unwrap();
        reg.register(
            make_hook("after", HookType::PreInject, 10, Box::new(ContinueHandler)),
            HookScope::Deployment,
            None,
        )
        .unwrap();

        let executor = HookExecutor::new(&reg);
        let result = executor.execute(HookType::PreInject, "s", make_input());

        assert!(result.completed);
        assert_eq!(
            result.modified_context,
            Some(serde_json::json!({"modified": true}))
        );
        assert_eq!(result.results.len(), 2);
    }

    #[test]
    fn disabled_hooks_skipped() {
        let mut reg = HookRegistry::new();
        let mut hook = make_hook("disabled", HookType::PreInject, 50, Box::new(AbortHandler {
            reason: "should not run".into(),
        }));
        hook.enabled = false;
        reg.register(hook, HookScope::Deployment, None).unwrap();

        let executor = HookExecutor::new(&reg);
        let result = executor.execute(HookType::PreInject, "s", make_input());

        assert!(result.completed);
        // Disabled hook produced no results.
        assert_eq!(result.results.len(), 0);
    }

    #[test]
    fn empty_chain_returns_completed() {
        let reg = HookRegistry::new();
        let executor = HookExecutor::new(&reg);
        let result = executor.execute(HookType::PreInject, "s", make_input());

        assert!(result.completed);
        assert!(result.aborted_by.is_none());
        assert!(result.results.is_empty());
    }

    #[test]
    fn duplicate_name_rejected() {
        let mut reg = HookRegistry::new();
        reg.register(
            make_hook("unique", HookType::PreInject, 50, Box::new(ContinueHandler)),
            HookScope::Deployment,
            None,
        )
        .unwrap();

        let result = reg.register(
            make_hook("unique", HookType::PreInject, 60, Box::new(ContinueHandler)),
            HookScope::Deployment,
            None,
        );
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("already registered"));
    }

    #[test]
    fn priority_above_100_rejected() {
        let mut reg = HookRegistry::new();
        let result = reg.register(
            make_hook("too-high", HookType::PreInject, 101, Box::new(ContinueHandler)),
            HookScope::Deployment,
            None,
        );
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("priority"));
    }

    #[test]
    fn timeout_zero_rejected() {
        let mut reg = HookRegistry::new();
        let mut hook = make_hook("zero-timeout", HookType::PreInject, 50, Box::new(ContinueHandler));
        hook.timeout = Duration::ZERO;
        let result = reg.register(hook, HookScope::Deployment, None);
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("timeout"));
    }

    #[test]
    fn timeout_over_30000ms_rejected() {
        let mut reg = HookRegistry::new();
        let mut hook = make_hook("long-timeout", HookType::PreInject, 50, Box::new(ContinueHandler));
        hook.timeout = Duration::from_millis(30001);
        let result = reg.register(hook, HookScope::Deployment, None);
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("timeout"));
    }

    #[test]
    fn panic_in_handler_treated_as_continue() {
        let mut reg = HookRegistry::new();
        reg.register(
            make_hook("panicker", HookType::PreInject, 90, Box::new(PanicHandler)),
            HookScope::Deployment,
            None,
        )
        .unwrap();
        reg.register(
            make_hook("after-panic", HookType::PreInject, 10, Box::new(ContinueHandler)),
            HookScope::Deployment,
            None,
        )
        .unwrap();

        let executor = HookExecutor::new(&reg);
        let result = executor.execute(HookType::PreInject, "s", make_input());

        // Chain should complete despite the panic.
        assert!(result.completed);
        assert_eq!(result.results.len(), 2);
        // The panicking hook's result should be Continue.
        assert_eq!(result.results[0].1.action, HookAction::Continue);
    }

    #[test]
    fn session_scope_requires_session_id() {
        let mut reg = HookRegistry::new();
        let result = reg.register(
            make_hook("sess-hook", HookType::PreInject, 50, Box::new(ContinueHandler)),
            HookScope::Session,
            None, // Missing session_id
        );
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("session_id"));
    }

    #[test]
    fn different_sessions_isolated() {
        let mut reg = HookRegistry::new();
        reg.register(
            make_hook("sess1-hook", HookType::PreInject, 50, Box::new(ContinueHandler)),
            HookScope::Session,
            Some("sess-1"),
        )
        .unwrap();

        // Session 1 sees the hook.
        assert_eq!(reg.get_chain(HookType::PreInject, "sess-1").len(), 1);
        // Session 2 does not.
        assert_eq!(reg.get_chain(HookType::PreInject, "sess-2").len(), 0);
    }

    #[test]
    fn hook_type_display() {
        assert_eq!(HookType::PreInject.to_string(), "pre_inject");
        assert_eq!(HookType::PostSelect.to_string(), "post_select");
        assert_eq!(HookType::OnTransition.to_string(), "on_transition");
        assert_eq!(HookType::OnConflict.to_string(), "on_conflict");
        assert_eq!(HookType::OnViolation.to_string(), "on_violation");
        assert_eq!(HookType::Periodic.to_string(), "periodic");
    }

    #[test]
    fn valid_hook_names_accepted() {
        assert!(is_valid_hook_name("my-hook"));
        assert!(is_valid_hook_name("hook_123"));
        assert!(is_valid_hook_name("a"));
        assert!(is_valid_hook_name(&"a".repeat(64)));
        assert!(is_valid_hook_name("pre-inject-pii-filter"));
        assert!(is_valid_hook_name("0-starts-with-digit"));
    }

    #[test]
    fn invalid_hook_names_rejected() {
        assert!(!is_valid_hook_name(""));
        assert!(!is_valid_hook_name(&"a".repeat(65)));
        assert!(!is_valid_hook_name("UPPERCASE"));
        assert!(!is_valid_hook_name("has space"));
        assert!(!is_valid_hook_name("has.dot"));
        assert!(!is_valid_hook_name("has@symbol"));
    }

    #[test]
    fn modify_constitution_forwarded() {
        let modified_val = serde_json::json!({
            "constitution": {"rules": ["be-safe"]},
        });
        let mut reg = HookRegistry::new();
        reg.register(
            make_hook(
                "con-modifier",
                HookType::PostSelect,
                80,
                Box::new(ModifyHandler {
                    value: modified_val,
                }),
            ),
            HookScope::Deployment,
            None,
        )
        .unwrap();

        let executor = HookExecutor::new(&reg);
        let result = executor.execute(HookType::PostSelect, "s", make_input());

        assert!(result.completed);
        assert_eq!(
            result.modified_constitution,
            Some(serde_json::json!({"rules": ["be-safe"]}))
        );
    }

    #[test]
    fn deregister_session_hook() {
        let mut reg = HookRegistry::new();
        reg.register(
            make_hook("sess-hook", HookType::PreInject, 50, Box::new(ContinueHandler)),
            HookScope::Session,
            Some("sess-1"),
        )
        .unwrap();
        assert_eq!(reg.get_chain(HookType::PreInject, "sess-1").len(), 1);

        reg.deregister("sess-hook", HookScope::Session, Some("sess-1"));
        assert_eq!(reg.get_chain(HookType::PreInject, "sess-1").len(), 0);
    }
}
