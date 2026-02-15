<script lang="ts">
	/**
	 * DemoContainer - Consistent wrapper for all interactive demos
	 */
	import TokenInspector from '../shared/TokenInspector.svelte';
	import type { VCPContext } from '$lib/vcp/types';

	interface Props {
		title: string;
		description: string;
		showTokenInspector?: boolean;
		showAuditTrail?: boolean;
		context?: VCPContext | null;
		onReset?: () => void;
		children: import('svelte').Snippet;
		controls?: import('svelte').Snippet;
	}

	let {
		title,
		description,
		showTokenInspector = true,
		showAuditTrail = false,
		context = null,
		onReset,
		children,
		controls
	}: Props = $props();

	let tokenInspectorOpen = $state(false);
	let auditTrailOpen = $state(false);
</script>

<div class="demo-container">
	<header class="demo-header">
		<div class="demo-header-content">
			<h1>{title}</h1>
			<p class="demo-description">{description}</p>
		</div>

		<div class="demo-controls">
			{#if showTokenInspector && context}
				<button
					class="control-btn"
					class:active={tokenInspectorOpen}
					onclick={() => (tokenInspectorOpen = !tokenInspectorOpen)}
				>
					<span class="control-icon">🔍</span>
					<span>Token</span>
				</button>
			{/if}

			{#if showAuditTrail}
				<button
					class="control-btn"
					class:active={auditTrailOpen}
					onclick={() => (auditTrailOpen = !auditTrailOpen)}
				>
					<span class="control-icon">📋</span>
					<span>Audit</span>
				</button>
			{/if}

			{#if onReset}
				<button class="control-btn control-btn-reset" onclick={onReset}>
					<span class="control-icon">↺</span>
					<span>Reset</span>
				</button>
			{/if}

			{#if controls}
				{@render controls()}
			{/if}
		</div>
	</header>

	<div class="demo-layout" class:with-sidebar={tokenInspectorOpen || auditTrailOpen}>
		<main class="demo-main">
			{@render children()}
		</main>

		{#if tokenInspectorOpen && context}
			<aside class="demo-sidebar animate-slide-in">
				<div class="sidebar-header">
					<h3>Token Inspector</h3>
					<button
						class="close-btn"
						onclick={() => (tokenInspectorOpen = false)}
						aria-label="Close token inspector"
					>
						×
					</button>
				</div>
				<TokenInspector {context} />
			</aside>
		{/if}

		{#if auditTrailOpen}
			<aside class="demo-sidebar animate-slide-in">
				<div class="sidebar-header">
					<h3>Audit Trail</h3>
					<button
						class="close-btn"
						onclick={() => (auditTrailOpen = false)}
						aria-label="Close audit trail"
					>
						×
					</button>
				</div>
				<div class="audit-placeholder">
					<p class="text-muted">Audit entries will appear here as actions occur.</p>
				</div>
			</aside>
		{/if}
	</div>
</div>

<style>
	.demo-container {
		min-height: calc(100vh - 80px);
		display: flex;
		flex-direction: column;
	}

	.demo-header {
		background: var(--color-bg-elevated);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
		padding: var(--space-lg) var(--space-xl);
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: var(--space-lg);
		flex-wrap: wrap;
	}

	.demo-header h1 {
		font-size: 1.5rem;
		margin-bottom: var(--space-xs);
	}

	.demo-description {
		color: var(--color-text-muted);
		font-size: 0.9375rem;
		max-width: 600px;
	}

	.demo-controls {
		display: flex;
		gap: var(--space-sm);
		flex-wrap: wrap;
	}

	.control-btn {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		padding: var(--space-sm) var(--space-md);
		background: var(--color-bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-md);
		color: var(--color-text-muted);
		font-size: 0.8125rem;
		cursor: pointer;
		transition: all var(--transition-fast);
	}

	.control-btn:hover {
		border-color: var(--color-primary);
		color: var(--color-text);
	}

	.control-btn.active {
		background: var(--color-primary-muted);
		border-color: var(--color-primary);
		color: var(--color-primary);
	}

	.control-btn-reset:hover {
		border-color: var(--color-warning);
		color: var(--color-warning);
	}

	.control-icon {
		font-size: 1rem;
	}

	.demo-layout {
		flex: 1;
		display: grid;
		grid-template-columns: 1fr;
		transition: grid-template-columns var(--transition-normal);
	}

	.demo-layout.with-sidebar {
		grid-template-columns: 1fr 360px;
	}

	.demo-main {
		padding: var(--space-xl);
		overflow-y: auto;
	}

	.demo-sidebar {
		background: var(--color-bg-elevated);
		border-left: 1px solid rgba(255, 255, 255, 0.1);
		overflow-y: auto;
		max-height: calc(100vh - 160px);
	}

	.sidebar-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: var(--space-md) var(--space-lg);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
		position: sticky;
		top: 0;
		background: var(--color-bg-elevated);
		z-index: 10;
	}

	.sidebar-header h3 {
		font-size: 0.875rem;
		font-weight: 600;
	}

	.close-btn {
		background: none;
		border: none;
		color: var(--color-text-muted);
		font-size: 1.25rem;
		cursor: pointer;
		padding: var(--space-xs);
		border-radius: var(--radius-sm);
		line-height: 1;
	}

	.close-btn:hover {
		color: var(--color-text);
		background: rgba(255, 255, 255, 0.05);
	}

	.audit-placeholder {
		padding: var(--space-lg);
		text-align: center;
	}

	.animate-slide-in {
		animation: slideIn 0.2s ease-out;
	}

	@keyframes slideIn {
		from {
			transform: translateX(20px);
			opacity: 0;
		}
		to {
			transform: translateX(0);
			opacity: 1;
		}
	}

	@media (max-width: 1024px) {
		.demo-layout.with-sidebar {
			grid-template-columns: 1fr;
		}

		.demo-sidebar {
			position: fixed;
			right: 0;
			top: 60px;
			bottom: 0;
			width: 320px;
			z-index: 100;
			box-shadow: -4px 0 20px rgba(0, 0, 0, 0.3);
		}
	}

	@media (max-width: 640px) {
		.demo-header {
			padding: var(--space-md);
		}

		.demo-header h1 {
			font-size: 1.25rem;
		}

		.demo-main {
			padding: var(--space-md);
		}

		.demo-sidebar {
			width: 100%;
		}
	}
</style>
