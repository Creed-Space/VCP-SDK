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

	const markerSymbols: Record<InterioraMarker, string> = {
		resonance: '<i class="fa-solid fa-check" aria-hidden="true"></i>',
		hollow: '○',
		na: '∅',
		flow: '→',
		blocked: '×',
		dancing: '∿',
		reaching: '>',
		resistance: '<',
		urgent: '!',
		uncertain: '?',
		significant: '*',
		grateful: '+'
	};

	const arcSymbols: Record<SessionArc, string> = {
		opening: '◇',
		middle: '◆',
		closing: '◈'
	};

	function getStars(value: number | undefined): string {
		if (value === undefined) return '—';
		const filled = Math.round((value / 9) * 5);
		return '<i class="fa-solid fa-star" aria-hidden="true"></i>'.repeat(filled) + '<i class="fa-regular fa-star" aria-hidden="true"></i>'.repeat(5 - filled);
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
				{@html state.markers.map((m) => markerSymbols[m]).join('')}
			</span>
		{/if}
	</div>

	<div class="dimensions-grid">
		{#each dimensions as dim}
			{@const value = state[dim.key as keyof InterioraState] as number | undefined}
			{#if value !== undefined}
				<div class="dimension">
					<span class="dim-icon"><i class={dim.icon} aria-hidden="true"></i></span>
					<span class="dim-stars">{@html getStars(value)}</span>
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
