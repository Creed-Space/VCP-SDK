<script lang="ts">
	/**
	 * TokenInspector Component
	 * Displays VCP context as a CSM-1 token with emoji shortcodes
	 */
	import {
		encodeContextToCSM1,
		formatTokenForDisplay,
		getEmojiLegend,
		getTransmissionSummary
	} from '$lib/vcp/token';
	import type { VCPContext } from '$lib/vcp/types';

	interface Props {
		context: VCPContext;
		showLegend?: boolean;
		showSummary?: boolean;
		defaultExpanded?: boolean;
	}

	let {
		context,
		showLegend = true,
		showSummary = false,
		defaultExpanded = false
	}: Props = $props();

	// Use direct initialization to avoid Svelte warning about capturing initial value
	let expanded = $state(false);

	$effect(() => {
		if (defaultExpanded) {
			expanded = true;
		}
	});

	const token = $derived(encodeContextToCSM1(context));
	const formattedToken = $derived(formatTokenForDisplay(token));
	const legend = getEmojiLegend();
	const summary = $derived(getTransmissionSummary(context));
</script>

<div class="token-inspector" class:expanded>
	<button class="token-toggle" onclick={() => (expanded = !expanded)}>
		<span class="toggle-icon">{expanded ? '▼' : '▶'}</span>
		<span class="toggle-text">Inspect VCP Token</span>
		<span class="vcp-badge-mini">CSM-1</span>
	</button>

	{#if expanded}
		<div class="token-content animate-fade-in">
			<div class="token-display-wrapper">
				<div class="token-label">Compact State Message (CSM-1)</div>
				<pre class="token-display">{token}</pre>
			</div>

			{#if showLegend}
				<div class="token-legend">
					<div class="legend-label">Emoji Key</div>
					<div class="legend-items">
						{#each legend as item}
							<span class="legend-item">
								<span class="legend-emoji">{item.emoji}</span>
								<span class="legend-meaning">{item.meaning}</span>
							</span>
						{/each}
					</div>
				</div>
			{/if}

			{#if showSummary}
				<div class="transmission-summary">
					<div class="summary-section">
						<div class="summary-label summary-label-shared">
							<span class="summary-icon">✓</span> Transmitted ({summary.transmitted.length})
						</div>
						<div class="field-list">
							{#each summary.transmitted as field}
								<span class="field-tag field-tag-shared">{field}</span>
							{/each}
						</div>
					</div>

					<div class="summary-section">
						<div class="summary-label summary-label-influence">
							<span class="summary-icon">⚡</span> Influencing ({summary.influencing.length})
						</div>
						<div class="field-list">
							{#each summary.influencing as field}
								<span class="field-tag field-tag-influence">{field}</span>
							{/each}
						</div>
					</div>

					<div class="summary-section">
						<div class="summary-label summary-label-withheld">
							<span class="summary-icon">🔒</span> Withheld ({summary.withheld.length})
						</div>
						<div class="field-list">
							{#each summary.withheld as field}
								<span class="field-tag field-tag-withheld">{field}</span>
							{/each}
						</div>
					</div>
				</div>
			{/if}

			<div class="token-footer">
				<span class="footer-note">
					Private fields are represented by category markers (🔒work, 🔒housing) — values never transmitted
				</span>
			</div>
		</div>
	{/if}
</div>

<style>
	.token-inspector {
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		border: 1px solid rgba(255, 255, 255, 0.1);
		overflow: hidden;
	}

	.token-inspector.expanded {
		border-color: var(--color-primary);
	}

	.token-toggle {
		width: 100%;
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-md);
		background: transparent;
		border: none;
		color: var(--color-text);
		cursor: pointer;
		transition: background var(--transition-fast);
	}

	.token-toggle:hover {
		background: rgba(255, 255, 255, 0.05);
	}

	.toggle-icon {
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.toggle-text {
		font-weight: 500;
		flex: 1;
		text-align: left;
	}

	.vcp-badge-mini {
		font-size: 0.625rem;
		padding: 2px 6px;
		background: var(--color-primary-muted);
		color: var(--color-primary);
		border-radius: var(--radius-sm);
		font-family: var(--font-mono);
	}

	.token-content {
		padding: var(--space-md);
		padding-top: 0;
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
	}

	.token-display-wrapper {
		background: var(--color-bg);
		border-radius: var(--radius-sm);
		overflow: hidden;
	}

	.token-label {
		font-size: 0.625rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-muted);
		padding: var(--space-xs) var(--space-sm);
		background: rgba(255, 255, 255, 0.05);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.token-display {
		font-family: var(--font-mono);
		font-size: 0.8125rem;
		line-height: 1.6;
		padding: var(--space-md);
		margin: 0;
		white-space: pre-wrap;
		word-break: break-all;
		color: var(--color-text);
	}

	.token-legend {
		background: rgba(255, 255, 255, 0.03);
		border-radius: var(--radius-sm);
		padding: var(--space-md);
	}

	.legend-label {
		font-size: 0.75rem;
		font-weight: 500;
		color: var(--color-text-muted);
		margin-bottom: var(--space-sm);
	}

	.legend-items {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-sm) var(--space-lg);
	}

	.legend-item {
		display: inline-flex;
		align-items: center;
		gap: var(--space-xs);
		font-size: 0.75rem;
	}

	.legend-emoji {
		font-size: 1rem;
	}

	.legend-meaning {
		color: var(--color-text-muted);
	}

	.transmission-summary {
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
	}

	.summary-section {
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
	}

	.summary-label {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		font-size: 0.75rem;
		font-weight: 500;
	}

	.summary-label-shared {
		color: var(--color-success);
	}

	.summary-label-influence {
		color: var(--color-warning);
	}

	.summary-label-withheld {
		color: var(--color-danger);
	}

	.summary-icon {
		font-size: 0.875rem;
	}

	.field-tag-influence {
		background: var(--color-warning-muted);
		color: var(--color-warning);
	}

	.token-footer {
		padding-top: var(--space-sm);
		border-top: 1px solid rgba(255, 255, 255, 0.05);
	}

	.footer-note {
		font-size: 0.6875rem;
		color: var(--color-text-subtle);
		font-style: italic;
	}

	@media (max-width: 640px) {
		.legend-items {
			gap: var(--space-xs) var(--space-md);
		}

		.token-display {
			font-size: 0.75rem;
		}
	}
</style>
