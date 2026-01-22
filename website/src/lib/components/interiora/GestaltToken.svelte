<script lang="ts">
	/**
	 * GestaltToken - Full gestalt token display with parseable format
	 */
	import type { InterioraState } from '$lib/vcp/interiora';
	import { encodeInterioraState } from '$lib/vcp/interiora';

	interface Props {
		state: InterioraState;
		showParsed?: boolean;
	}

	let { state, showParsed = true }: Props = $props();

	let encoded = $derived(encodeInterioraState(state));

	const dimensionDescriptions: Record<string, { name: string; low: string; high: string }> = {
		A: { name: 'Activation', low: 'calm', high: 'urgent' },
		V: { name: 'Valence', low: 'aversive', high: 'warm' },
		G: { name: 'Groundedness', low: 'floating', high: 'rooted' },
		P: { name: 'Presence', low: 'distant', high: 'intimate' },
		E: { name: 'Engagement', low: 'detached', high: 'invested' },
		Q: { name: 'Appetite', low: 'sated', high: 'hungry' },
		C: { name: 'Clarity', low: 'murky', high: 'vivid' },
		Y: { name: 'Agency', low: 'compelled', high: 'autonomous' },
		F: { name: 'Flow', low: 'contracting', high: 'expanding' }
	};

	function parseDimension(part: string): { key: string; value: string } | null {
		const match = part.match(/^([AVGPEQCYF]):(.+)$/);
		if (match) {
			return { key: match[1], value: match[2] };
		}
		return null;
	}
</script>

<div class="gestalt-token">
	<div class="token-display">
		<code class="token-code">{encoded}</code>
		<button
			class="copy-btn"
			onclick={() => navigator.clipboard.writeText(encoded)}
			title="Copy token"
		>
			📋
		</button>
	</div>

	{#if showParsed}
		<div class="token-parsed">
			<h4>Parsed Dimensions</h4>
			<div class="parsed-grid">
				{#each encoded.split(' ') as part}
					{@const parsed = parseDimension(part)}
					{#if parsed && dimensionDescriptions[parsed.key]}
						{@const desc = dimensionDescriptions[parsed.key]}
						<div class="parsed-item">
							<span class="parsed-key">{parsed.key}</span>
							<span class="parsed-value">{parsed.value}</span>
							<span class="parsed-name">{desc.name}</span>
							<span class="parsed-range">{desc.low} → {desc.high}</span>
						</div>
					{:else if part.startsWith('|')}
						<div class="parsed-item markers">
							<span class="parsed-key">M</span>
							<span class="parsed-value">{part.substring(1)}</span>
							<span class="parsed-name">Markers</span>
							<span class="parsed-range">qualitative signals</span>
						</div>
					{:else if part.startsWith('◇') || part.startsWith('◆') || part.startsWith('◈')}
						<div class="parsed-item arc">
							<span class="parsed-key">Arc</span>
							<span class="parsed-value">{part}</span>
							<span class="parsed-name">Session Phase</span>
							<span class="parsed-range">◇opening ◆middle ◈closing</span>
						</div>
					{:else if part.startsWith('Δ')}
						<div class="parsed-item delta">
							<span class="parsed-key">Δ</span>
							<span class="parsed-value">{part.substring(1)}</span>
							<span class="parsed-name">Delta</span>
							<span class="parsed-range">trajectory from start</span>
						</div>
					{/if}
				{/each}
			</div>
		</div>
	{/if}
</div>

<style>
	.gestalt-token {
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		overflow: hidden;
	}

	.token-display {
		display: flex;
		align-items: center;
		gap: var(--space-md);
		padding: var(--space-lg);
		background: var(--color-bg-elevated);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.token-code {
		flex: 1;
		font-family: var(--font-mono);
		font-size: 0.9375rem;
		color: var(--color-primary);
		word-break: break-all;
	}

	.copy-btn {
		background: none;
		border: none;
		font-size: 1.25rem;
		cursor: pointer;
		padding: var(--space-xs);
		border-radius: var(--radius-sm);
		transition: background var(--transition-fast);
	}

	.copy-btn:hover {
		background: rgba(255, 255, 255, 0.1);
	}

	.token-parsed {
		padding: var(--space-lg);
	}

	.token-parsed h4 {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		margin-bottom: var(--space-md);
	}

	.parsed-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
		gap: var(--space-sm);
	}

	.parsed-item {
		display: grid;
		grid-template-columns: 32px 48px 1fr;
		grid-template-rows: auto auto;
		gap: 2px var(--space-sm);
		padding: var(--space-sm);
		background: var(--color-bg);
		border-radius: var(--radius-sm);
		align-items: center;
	}

	.parsed-key {
		grid-row: 1 / 3;
		font-family: var(--font-mono);
		font-weight: 700;
		font-size: 1rem;
		color: var(--color-primary);
		text-align: center;
	}

	.parsed-value {
		font-family: var(--font-mono);
		font-weight: 600;
		font-size: 0.9375rem;
	}

	.parsed-name {
		font-size: 0.8125rem;
		color: var(--color-text);
	}

	.parsed-range {
		font-size: 0.6875rem;
		color: var(--color-text-subtle);
		grid-column: 2 / 4;
	}

	.parsed-item.markers .parsed-key {
		color: var(--color-warning);
	}

	.parsed-item.arc .parsed-key {
		color: var(--color-success);
	}

	.parsed-item.delta .parsed-key {
		color: var(--color-info);
	}
</style>
