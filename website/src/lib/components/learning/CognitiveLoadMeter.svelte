<script lang="ts">
	/**
	 * CognitiveLoadMeter - Visual cognitive load indicator
	 */
	import type { CognitiveLoadState } from '$lib/vcp/learning';

	interface Props {
		state: CognitiveLoadState;
		showBreakdown?: boolean;
		compact?: boolean;
	}

	let { state, showBreakdown = true, compact = false }: Props = $props();

	function getLoadColor(load: number): string {
		if (load <= 0.4) return '#2ecc71';
		if (load <= 0.7) return '#f39c12';
		return '#e74c3c';
	}

	function getLoadLabel(load: number): string {
		if (load <= 0.3) return 'Light';
		if (load <= 0.5) return 'Moderate';
		if (load <= 0.7) return 'Heavy';
		return 'Overloaded';
	}

	function formatDuration(minutes: number): string {
		if (minutes < 60) return `${Math.round(minutes)}m`;
		const hours = Math.floor(minutes / 60);
		const mins = Math.round(minutes % 60);
		return `${hours}h ${mins}m`;
	}
</script>

<div class="cognitive-load-meter" class:compact role="region" aria-label="Cognitive load status">
	<!-- Main gauge -->
	<div class="main-gauge">
		<div
			class="gauge-track"
			role="progressbar"
			aria-valuenow={Math.round(state.current_load * 100)}
			aria-valuemin="0"
			aria-valuemax="100"
			aria-label="Current cognitive load: {Math.round(state.current_load * 100)}% - {getLoadLabel(state.current_load)}"
		>
			<div
				class="gauge-fill"
				style="width: {state.current_load * 100}%; background: {getLoadColor(state.current_load)}"
			></div>
		</div>
		<div class="gauge-labels">
			<span class="gauge-label">{getLoadLabel(state.current_load)}</span>
			<span class="gauge-value" style="color: {getLoadColor(state.current_load)}" aria-hidden="true">
				{Math.round(state.current_load * 100)}%
			</span>
		</div>
	</div>

	{#if showBreakdown && !compact}
		<!-- Load breakdown -->
		<div class="breakdown">
			<div class="breakdown-item">
				<span class="breakdown-label">Intrinsic</span>
				<div class="breakdown-bar">
					<div
						class="breakdown-fill intrinsic"
						style="width: {state.intrinsic_load * 100}%"
					></div>
				</div>
				<span class="breakdown-value">{Math.round(state.intrinsic_load * 100)}%</span>
			</div>

			<div class="breakdown-item">
				<span class="breakdown-label">Extraneous</span>
				<div class="breakdown-bar">
					<div
						class="breakdown-fill extraneous"
						style="width: {state.extraneous_load * 100}%"
					></div>
				</div>
				<span class="breakdown-value">{Math.round(state.extraneous_load * 100)}%</span>
			</div>

			<div class="breakdown-item">
				<span class="breakdown-label">Germane</span>
				<div class="breakdown-bar">
					<div
						class="breakdown-fill germane"
						style="width: {state.germane_load * 100}%"
					></div>
				</div>
				<span class="breakdown-value">{Math.round(state.germane_load * 100)}%</span>
			</div>
		</div>

		<!-- Session info -->
		<div class="session-info">
			<div class="info-item">
				<span class="info-icon"><i class="fa-solid fa-stopwatch" aria-hidden="true"></i></span>
				<span>Session: {formatDuration(state.session_duration_minutes)}</span>
			</div>
			<div class="info-item">
				<span class="info-icon"><i class="fa-solid fa-battery-half" aria-hidden="true"></i></span>
				<span>Capacity: {Math.round(state.capacity_remaining * 100)}%</span>
			</div>
			{#if state.fatigue_factor > 0.3}
				<div class="info-item fatigue">
					<span class="info-icon"><i class="fa-solid fa-bed" aria-hidden="true"></i></span>
					<span>Fatigue: {Math.round(state.fatigue_factor * 100)}%</span>
				</div>
			{/if}
		</div>

		<!-- Overload indicators -->
		{#if state.overload_indicators.length > 0}
			<div class="overload-warning">
				<span class="warning-icon"><i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i></span>
				<span>Overload signals detected:</span>
				<div class="indicator-chips">
					{#each state.overload_indicators as indicator}
						<span class="indicator-chip">{indicator.type.replace(/_/g, ' ')}</span>
					{/each}
				</div>
			</div>
		{/if}
	{/if}
</div>

<style>
	.cognitive-load-meter {
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
	}

	.cognitive-load-meter.compact {
		padding: var(--space-md);
	}

	.main-gauge {
		margin-bottom: var(--space-lg);
	}

	.compact .main-gauge {
		margin-bottom: 0;
	}

	.gauge-track {
		height: 12px;
		background: var(--color-bg-elevated);
		border-radius: var(--radius-full);
		overflow: hidden;
	}

	.gauge-fill {
		height: 100%;
		border-radius: var(--radius-full);
		transition: width var(--transition-normal);
	}

	.gauge-labels {
		display: flex;
		justify-content: space-between;
		margin-top: var(--space-xs);
	}

	.gauge-label {
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	.gauge-value {
		font-family: var(--font-mono);
		font-weight: 700;
		font-size: 1rem;
	}

	.breakdown {
		display: flex;
		flex-direction: column;
		gap: var(--space-sm);
		margin-bottom: var(--space-lg);
	}

	.breakdown-item {
		display: grid;
		grid-template-columns: 80px 1fr 40px;
		align-items: center;
		gap: var(--space-sm);
	}

	.breakdown-label {
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.breakdown-bar {
		height: 6px;
		background: var(--color-bg-elevated);
		border-radius: var(--radius-full);
		overflow: hidden;
	}

	.breakdown-fill {
		height: 100%;
		border-radius: var(--radius-full);
	}

	.breakdown-fill.intrinsic {
		background: #3498db;
	}

	.breakdown-fill.extraneous {
		background: #e74c3c;
	}

	.breakdown-fill.germane {
		background: #2ecc71;
	}

	.breakdown-value {
		font-family: var(--font-mono);
		font-size: 0.75rem;
		text-align: right;
		color: var(--color-text-muted);
	}

	.session-info {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-md);
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		margin-bottom: var(--space-md);
	}

	.info-item {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		font-size: 0.8125rem;
	}

	.info-item.fatigue {
		color: var(--color-warning);
	}

	.overload-warning {
		padding: var(--space-md);
		background: var(--color-danger-muted);
		border-radius: var(--radius-md);
		border-left: 3px solid var(--color-danger);
	}

	.overload-warning > span {
		display: block;
		font-size: 0.875rem;
		color: var(--color-danger);
		margin-bottom: var(--space-xs);
	}

	.warning-icon {
		margin-right: var(--space-xs);
	}

	.indicator-chips {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-xs);
	}

	.indicator-chip {
		font-size: 0.6875rem;
		padding: 2px 8px;
		background: rgba(231, 76, 60, 0.2);
		color: var(--color-danger);
		border-radius: var(--radius-sm);
		text-transform: capitalize;
	}
</style>
