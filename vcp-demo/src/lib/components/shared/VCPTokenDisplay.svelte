<script lang="ts">
	/**
	 * VCPTokenDisplay Component
	 * Live token encoding view - shows current state as a VCP token
	 */

	interface TokenSection {
		label: string;
		value: string;
		color?: 'primary' | 'success' | 'warning' | 'danger' | 'muted';
	}

	interface Props {
		token: string;
		version?: string;
		sections?: TokenSection[];
		title?: string;
		showCopy?: boolean;
		animated?: boolean;
		compact?: boolean;
	}

	let {
		token,
		version = '2.0',
		sections = [],
		title = 'VCP Token',
		showCopy = true,
		animated = true,
		compact = false
	}: Props = $props();

	let copied = $state(false);
	let prevToken = $state(token);
	let isUpdating = $state(false);

	$effect(() => {
		if (token !== prevToken && animated) {
			isUpdating = true;
			const timeout = setTimeout(() => {
				isUpdating = false;
			}, 300);
			prevToken = token;
			return () => clearTimeout(timeout);
		}
		prevToken = token;
	});

	async function copyToken() {
		try {
			await navigator.clipboard.writeText(token);
			copied = true;
			setTimeout(() => {
				copied = false;
			}, 2000);
		} catch {
			console.error('Failed to copy token');
		}
	}
</script>

<div class="token-display" class:compact class:updating={isUpdating}>
	<div class="token-header">
		<span class="token-title">
			<i class="fa-solid fa-code" aria-hidden="true"></i>
			{title}
		</span>
		<span class="token-version">v{version}</span>
		{#if showCopy}
			<button class="copy-btn" onclick={copyToken} title="Copy token">
				{#if copied}
					<i class="fa-solid fa-check" aria-hidden="true"></i>
				{:else}
					<i class="fa-solid fa-copy" aria-hidden="true"></i>
				{/if}
			</button>
		{/if}
	</div>

	<div class="token-body">
		<pre class="token-code" class:animated>{token}</pre>
	</div>

	{#if sections.length > 0}
		<div class="token-sections">
			{#each sections as section}
				<div class="token-section section-{section.color ?? 'muted'}">
					<span class="section-label">{section.label}</span>
					<span class="section-value">{section.value}</span>
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	.token-display {
		background: var(--color-bg-elevated);
		border-radius: var(--radius-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
		overflow: hidden;
		transition: border-color var(--transition-fast);
	}

	.token-display.updating {
		border-color: var(--color-primary);
	}

	.token-display.compact {
		border-radius: var(--radius-md);
	}

	.token-header {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-sm) var(--space-md);
		background: rgba(255, 255, 255, 0.05);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.token-title {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		font-size: 0.75rem;
		font-weight: 500;
		color: var(--color-text-muted);
	}

	.token-version {
		font-size: 0.625rem;
		padding: 1px 6px;
		background: var(--color-primary-muted);
		color: var(--color-primary);
		border-radius: var(--radius-sm);
		font-family: var(--font-mono);
	}

	.copy-btn {
		margin-left: auto;
		padding: var(--space-xs);
		background: transparent;
		border: none;
		color: var(--color-text-muted);
		cursor: pointer;
		border-radius: var(--radius-sm);
		transition: all var(--transition-fast);
	}

	.copy-btn:hover {
		background: rgba(255, 255, 255, 0.1);
		color: var(--color-text);
	}

	.token-body {
		padding: var(--space-md);
	}

	.token-code {
		font-family: var(--font-mono);
		font-size: 0.8125rem;
		line-height: 1.6;
		margin: 0;
		white-space: pre-wrap;
		word-break: break-all;
		color: var(--color-text);
	}

	.token-code.animated {
		transition: color var(--transition-fast);
	}

	.updating .token-code {
		color: var(--color-primary);
	}

	.token-sections {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-xs);
		padding: var(--space-sm) var(--space-md);
		background: rgba(255, 255, 255, 0.03);
		border-top: 1px solid rgba(255, 255, 255, 0.05);
	}

	.token-section {
		display: inline-flex;
		align-items: center;
		gap: var(--space-xs);
		padding: 2px 8px;
		border-radius: var(--radius-sm);
		font-size: 0.6875rem;
	}

	.section-label {
		opacity: 0.7;
	}

	.section-value {
		font-family: var(--font-mono);
		font-weight: 500;
	}

	.section-primary {
		background: var(--color-primary-muted);
		color: var(--color-primary);
	}

	.section-success {
		background: var(--color-success-muted);
		color: var(--color-success);
	}

	.section-warning {
		background: var(--color-warning-muted);
		color: var(--color-warning);
	}

	.section-danger {
		background: var(--color-danger-muted);
		color: var(--color-danger);
	}

	.section-muted {
		background: rgba(255, 255, 255, 0.1);
		color: var(--color-text-muted);
	}

	.compact .token-header {
		padding: var(--space-xs) var(--space-sm);
	}

	.compact .token-body {
		padding: var(--space-sm);
	}

	.compact .token-code {
		font-size: 0.75rem;
	}

	.compact .token-sections {
		padding: var(--space-xs) var(--space-sm);
	}
</style>
