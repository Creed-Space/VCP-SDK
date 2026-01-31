<script lang="ts">
	/**
	 * Context Indicator Component
	 * Shows the current VCP context with emoji encoding and allows switching
	 */

	interface Props {
		contextType: 'professional' | 'personal';
		contextEncoding?: string;
		onSwitch?: (newContext: 'professional' | 'personal') => void;
		allowSwitch?: boolean;
		compact?: boolean;
	}

	let {
		contextType,
		contextEncoding,
		onSwitch,
		allowSwitch = true,
		compact = false
	}: Props = $props();

	// Default encodings from spec
	const defaultEncodings = {
		professional: '⏰📅|📍🏢|👥👔|🔶⏱️💸',
		personal: '⏰🌆|📍🏡|👥👶|🧠😴|🔶⏱️💸🏥'
	};

	const encoding = $derived(contextEncoding || defaultEncodings[contextType]);

	// Context metadata
	const contextMeta = $derived(
		contextType === 'professional'
			? {
					label: 'Professional',
					icon: 'fa-briefcase',
					color: 'var(--color-primary)',
					persona: 'Ambassador',
					constitution: 'techcorp.career.advisor'
				}
			: {
					label: 'Personal',
					icon: 'fa-home',
					color: 'var(--color-warning)',
					persona: 'Godparent',
					constitution: 'personal.balanced.guide'
				}
	);

	function handleSwitch() {
		const newContext = contextType === 'professional' ? 'personal' : 'professional';
		onSwitch?.(newContext);
	}
</script>

{#if compact}
	<div class="context-indicator-compact" style="--context-color: {contextMeta.color}">
		<span class="context-icon">
			<i class="fa-solid {contextMeta.icon}" aria-hidden="true"></i>
		</span>
		<code class="context-encoding">{encoding}</code>
		{#if allowSwitch && onSwitch}
			<button class="switch-btn-compact" onclick={handleSwitch} aria-label="Switch context">
				<i class="fa-solid fa-shuffle" aria-hidden="true"></i>
			</button>
		{/if}
	</div>
{:else}
	<div class="context-indicator" style="--context-color: {contextMeta.color}">
		<div class="context-header">
			<span class="context-icon">
				<i class="fa-solid {contextMeta.icon}" aria-hidden="true"></i>
			</span>
			<div class="context-info">
				<span class="context-label">{contextMeta.label} Context</span>
				<span class="context-persona">{contextMeta.persona} mode</span>
			</div>
			{#if allowSwitch && onSwitch}
				<button class="switch-btn" onclick={handleSwitch}>
					<i class="fa-solid fa-shuffle" aria-hidden="true"></i>
					Switch
				</button>
			{/if}
		</div>

		<div class="context-encoding-box">
			<span class="encoding-label">VCP/A Encoding:</span>
			<code class="encoding-value">{encoding}</code>
		</div>

		<div class="context-details">
			<div class="detail-item">
				<span class="detail-label">Constitution:</span>
				<span class="detail-value">{contextMeta.constitution}</span>
			</div>
		</div>
	</div>
{/if}

<style>
	.context-indicator {
		background: var(--color-bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-left: 3px solid var(--context-color);
		border-radius: var(--radius-md);
		padding: var(--space-md);
	}

	.context-header {
		display: flex;
		align-items: center;
		gap: var(--space-md);
		margin-bottom: var(--space-md);
	}

	.context-icon {
		width: 40px;
		height: 40px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--context-color);
		color: var(--color-bg);
		border-radius: var(--radius-md);
		font-size: 1.25rem;
	}

	.context-info {
		flex: 1;
	}

	.context-label {
		display: block;
		font-weight: 600;
		color: var(--context-color);
	}

	.context-persona {
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.switch-btn {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		padding: var(--space-xs) var(--space-sm);
		background: var(--color-bg-elevated);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-md);
		color: var(--color-text-muted);
		font-size: 0.75rem;
		cursor: pointer;
		transition: all var(--transition-fast);
	}

	.switch-btn:hover {
		background: var(--color-bg);
		color: var(--color-text);
		border-color: var(--context-color);
	}

	.context-encoding-box {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-sm);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-sm);
		margin-bottom: var(--space-md);
	}

	.encoding-label {
		font-size: 0.6875rem;
		color: var(--color-text-subtle);
		text-transform: uppercase;
	}

	.encoding-value {
		font-family: var(--font-mono);
		font-size: 1rem;
		letter-spacing: 0.05em;
	}

	.context-details {
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
	}

	.detail-item {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-size: 0.75rem;
	}

	.detail-label {
		color: var(--color-text-subtle);
	}

	.detail-value {
		font-family: var(--font-mono);
		color: var(--color-text-muted);
	}

	/* Compact variant */
	.context-indicator-compact {
		display: inline-flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-xs) var(--space-sm);
		background: var(--color-bg-elevated);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-left: 3px solid var(--context-color);
		border-radius: var(--radius-md);
	}

	.context-indicator-compact .context-icon {
		width: auto;
		height: auto;
		background: transparent;
		color: var(--context-color);
		font-size: 0.875rem;
	}

	.context-indicator-compact .context-encoding {
		font-family: var(--font-mono);
		font-size: 0.8125rem;
		letter-spacing: 0.02em;
	}

	.switch-btn-compact {
		padding: var(--space-xs);
		background: transparent;
		border: none;
		color: var(--color-text-muted);
		cursor: pointer;
		border-radius: var(--radius-sm);
		transition: all var(--transition-fast);
	}

	.switch-btn-compact:hover {
		background: var(--color-bg);
		color: var(--context-color);
	}
</style>
