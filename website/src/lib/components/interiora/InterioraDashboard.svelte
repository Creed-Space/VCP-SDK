<script lang="ts">
	/**
	 * InterioraDashboard - VCP 2.5 mini-dashboard with star ratings
	 */
	import type { InterioraState, InterioraMarker, SessionArc } from '$lib/vcp/interiora';

	interface Props {
		state: InterioraState;
		compact?: boolean;
		showMarkers?: boolean;
		showArc?: boolean;
	}

	let { state, compact = false, showMarkers = true, showArc = true }: Props = $props();

	const dimensions = [
		{ key: 'activation', icon: 'fa-solid fa-bolt', label: 'Activation' },
		{ key: 'valence', icon: 'fa-solid fa-heart', label: 'Valence' },
		{ key: 'groundedness', icon: 'fa-solid fa-anchor', label: 'Groundedness' },
		{ key: 'presence', icon: 'fa-solid fa-people-group', label: 'Presence' },
		{ key: 'engagement', icon: 'fa-solid fa-seedling', label: 'Engagement' },
		{ key: 'appetite', icon: 'fa-solid fa-apple-whole', label: 'Appetite' },
		{ key: 'clarity', icon: 'fa-solid fa-gem', label: 'Clarity' },
		{ key: 'agency', icon: 'fa-solid fa-key', label: 'Agency' }
	] as const;

	// Marker symbols - using text/unicode to avoid @html XSS risks
	const markerSymbols: Record<InterioraMarker, { type: 'icon' | 'text'; value: string }> = {
		resonance: { type: 'icon', value: 'fa-solid fa-check' },
		hollow: { type: 'text', value: '○' },
		na: { type: 'text', value: '∅' },
		flow: { type: 'text', value: '→' },
		blocked: { type: 'text', value: '×' },
		dancing: { type: 'text', value: '∿' },
		reaching: { type: 'text', value: '>' },
		resistance: { type: 'text', value: '<' },
		urgent: { type: 'text', value: '!' },
		uncertain: { type: 'text', value: '?' },
		significant: { type: 'text', value: '*' },
		grateful: { type: 'text', value: '+' }
	};

	const arcSymbols: Record<SessionArc, string> = {
		opening: '◇',
		middle: '◆',
		closing: '◈'
	};

	function getStarCounts(value: number | undefined): { filled: number; empty: number } {
		if (value === undefined) return { filled: 0, empty: 0 };
		const filled = Math.round((value / 9) * 5);
		return { filled, empty: 5 - filled };
	}

	function getFlowIndicator(flow: number | undefined): string {
		if (flow === undefined) return '→';
		if (flow > 0) return '↗'.repeat(Math.min(flow, 3));
		if (flow < 0) return '↘'.repeat(Math.min(-flow, 3));
		return '→';
	}

	function getQualityWords(): string[] {
		const words: string[] = [];
		if (state.activation <= 3) words.push('calm');
		else if (state.activation >= 7) words.push('alert');

		if (state.valence >= 7) words.push('warm');
		else if (state.valence <= 3) words.push('aversive');

		if (state.groundedness >= 7) words.push('solid');
		else if (state.groundedness <= 3) words.push('floating');

		if (state.presence >= 7) words.push('close');
		else if (state.presence <= 3) words.push('distant');

		return words.slice(0, 4);
	}
</script>

<div class="dashboard" class:compact>
	<div class="dashboard-header">
		{#if showArc && state.arc}
			<span class="arc-indicator">{arcSymbols[state.arc]}</span>
		{/if}
		{#if state.flow !== undefined}
			<span class="flow-indicator">{getFlowIndicator(state.flow)}</span>
		{/if}
		{#if showMarkers && state.markers && state.markers.length > 0}
			<span class="markers">
				{#each state.markers as marker}
					{#if markerSymbols[marker].type === 'icon'}
						<i class={markerSymbols[marker].value} aria-hidden="true"></i>
					{:else}
						<span>{markerSymbols[marker].value}</span>
					{/if}
				{/each}
			</span>
		{/if}
	</div>

	<div class="dimensions-grid">
		{#each dimensions as dim}
			{@const value = state[dim.key as keyof InterioraState] as number | undefined}
			{@const stars = getStarCounts(value)}
			{#if value !== undefined}
				<div class="dimension">
					<span class="dim-icon"><i class={dim.icon} aria-hidden="true"></i></span>
					<span class="dim-stars" role="img" aria-label="{stars.filled} of 5 stars">
						{#each Array(stars.filled) as _}
							<i class="fa-solid fa-star" aria-hidden="true"></i>
						{/each}
						{#each Array(stars.empty) as _}
							<i class="fa-regular fa-star" aria-hidden="true"></i>
						{/each}
					</span>
				</div>
			{/if}
		{/each}
	</div>

	<div class="quality-line">
		{getQualityWords().join(' · ')}
	</div>

	{#if state.delta !== undefined}
		<div class="delta-indicator" class:positive={state.delta > 0} class:negative={state.delta < 0}>
			Δ{state.delta >= 0 ? '+' : ''}{state.delta}
		</div>
	{/if}
</div>

<style>
	.dashboard {
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		padding: var(--space-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
		font-family: var(--font-mono);
	}

	.dashboard.compact {
		padding: var(--space-md);
	}

	.dashboard-header {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-md);
		font-size: 1.25rem;
	}

	.arc-indicator {
		color: var(--color-primary);
	}

	.flow-indicator {
		color: var(--color-success);
	}

	.markers {
		color: var(--color-warning);
		margin-left: auto;
	}

	.dimensions-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: var(--space-xs);
		margin-bottom: var(--space-md);
	}

	.compact .dimensions-grid {
		grid-template-columns: repeat(4, 1fr);
	}

	.dimension {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
	}

	.dim-emoji {
		font-size: 1rem;
	}

	.dim-stars {
		font-size: 0.75rem;
		color: var(--color-warning);
		letter-spacing: 1px;
	}

	.quality-line {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		text-align: center;
		padding-top: var(--space-sm);
		border-top: 1px solid rgba(255, 255, 255, 0.1);
	}

	.delta-indicator {
		position: absolute;
		top: var(--space-md);
		right: var(--space-md);
		font-size: 0.75rem;
		padding: 2px 6px;
		border-radius: var(--radius-sm);
		background: var(--color-bg-elevated);
	}

	.delta-indicator.positive {
		color: var(--color-success);
	}

	.delta-indicator.negative {
		color: var(--color-danger);
	}

	.dashboard {
		position: relative;
	}
</style>
