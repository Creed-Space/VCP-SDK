<script lang="ts">
	/**
	 * Prosaic Context Panel - Interactive controls for the 4 prosaic dimensions
	 * Used across demos to show how immediate user state affects AI adaptation
	 */
	import type { ProsaicDimensions } from '$lib/vcp/types';

	interface Props {
		prosaic: ProsaicDimensions;
		onchange?: (prosaic: ProsaicDimensions) => void;
		compact?: boolean;
		readonly?: boolean;
		title?: string;
		showImpact?: boolean;
		impactSummary?: string[];
	}

	let {
		prosaic = $bindable(),
		onchange,
		compact = false,
		readonly = false,
		title = 'Personal State',
		showImpact = true,
		impactSummary = []
	}: Props = $props();

	const dimensions = [
		{ key: 'urgency', emoji: '⚡', label: 'Urgency', lowLabel: 'Relaxed', highLabel: 'Critical' },
		{ key: 'health', emoji: '💊', label: 'Health Impact', lowLabel: 'Feeling fine', highLabel: 'Unwell' },
		{ key: 'cognitive', emoji: '🧩', label: 'Cognitive Load', lowLabel: 'Clear headed', highLabel: 'Overwhelmed' },
		{ key: 'affect', emoji: '💭', label: 'Emotional State', lowLabel: 'Calm', highLabel: 'Intense' }
	] as const;

	const presets = [
		{ id: 'normal', label: 'Normal', values: { urgency: 0.2, health: 0.1, cognitive: 0.2, affect: 0.2 } },
		{ id: 'hurry', label: 'In a hurry', values: { urgency: 0.9, health: 0.1, cognitive: 0.4, affect: 0.3 } },
		{ id: 'unwell', label: 'Not well', values: { urgency: 0.2, health: 0.7, cognitive: 0.5, affect: 0.4 } },
		{ id: 'overwhelmed', label: 'Overwhelmed', values: { urgency: 0.4, health: 0.3, cognitive: 0.9, affect: 0.6 } },
		{ id: 'grieving', label: 'Grieving', values: { urgency: 0.1, health: 0.4, cognitive: 0.5, affect: 0.9 } },
		{ id: 'crisis', label: 'Crisis mode', values: { urgency: 0.95, health: 0.6, cognitive: 0.8, affect: 0.8 } }
	];

	function updateDimension(key: keyof ProsaicDimensions, value: number) {
		if (readonly) return;
		prosaic = { ...prosaic, [key]: value };
		onchange?.(prosaic);
	}

	function applyPreset(preset: typeof presets[0]) {
		if (readonly) return;
		prosaic = { ...prosaic, ...preset.values };
		onchange?.(prosaic);
	}

	function getHintText(key: string, value: number): string {
		if (key === 'urgency') {
			if (value >= 0.8) return '"I need this NOW"';
			if (value >= 0.5) return 'Some time pressure';
			return 'No rush';
		}
		if (key === 'health') {
			if (value >= 0.7) return '"I\'m not feeling well"';
			if (value >= 0.4) return 'Some fatigue/discomfort';
			return 'Feeling okay';
		}
		if (key === 'cognitive') {
			if (value >= 0.8) return '"Too many options"';
			if (value >= 0.5) return 'Some mental load';
			return 'Clear headed';
		}
		if (key === 'affect') {
			if (value >= 0.8) return 'High emotional intensity';
			if (value >= 0.5) return 'Some stress/emotion';
			return 'Calm, neutral';
		}
		return '';
	}

	function getBarColor(value: number): string {
		if (value >= 0.7) return 'var(--color-danger)';
		if (value >= 0.4) return 'var(--color-warning)';
		return 'var(--color-success)';
	}
</script>

<div class="prosaic-panel" class:compact class:readonly>
	<div class="panel-header">
		<h3>{title}</h3>
		<span class="prosaic-badge">⚡💊🧩💭</span>
	</div>

	{#if !compact}
		<div class="presets">
			{#each presets as preset}
				<button
					class="preset-btn"
					onclick={() => applyPreset(preset)}
					disabled={readonly}
				>
					{preset.label}
				</button>
			{/each}
		</div>
	{/if}

	<div class="dimensions">
		{#each dimensions as dim}
			{@const value = prosaic[dim.key as keyof ProsaicDimensions] as number ?? 0}
			<div class="dimension" class:high={value >= 0.7} class:medium={value >= 0.4 && value < 0.7}>
				<div class="dim-header">
					<span class="dim-emoji">{dim.emoji}</span>
					<span class="dim-label">{dim.label}</span>
					<span class="dim-value">{value.toFixed(1)}</span>
				</div>
				{#if !readonly}
					<input
						type="range"
						min="0"
						max="1"
						step="0.1"
						value={value}
						oninput={(e) => updateDimension(dim.key as keyof ProsaicDimensions, parseFloat(e.currentTarget.value))}
						class="dim-slider"
					/>
				{:else}
					<div class="dim-bar">
						<div class="dim-bar-fill" style="width: {value * 100}%; background: {getBarColor(value)}"></div>
					</div>
				{/if}
				{#if !compact}
					<div class="dim-hint">{getHintText(dim.key, value)}</div>
				{/if}
			</div>
		{/each}
	</div>

	{#if showImpact && impactSummary.length > 0}
		<div class="impact-section">
			<h4>How this affects adaptation:</h4>
			<ul class="impact-list">
				{#each impactSummary as impact}
					<li>{impact}</li>
				{/each}
			</ul>
		</div>
	{/if}
</div>

<style>
	.prosaic-panel {
		background: var(--color-bg-card);
		border: 1px solid rgba(16, 185, 129, 0.3);
		border-radius: var(--radius-lg);
		padding: var(--space-lg);
	}

	.prosaic-panel.compact {
		padding: var(--space-md);
	}

	.prosaic-panel.readonly {
		background: linear-gradient(135deg, rgba(16, 185, 129, 0.05), transparent);
	}

	.panel-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--space-md);
	}

	.panel-header h3 {
		margin: 0;
		font-size: 1rem;
		color: var(--color-success);
	}

	.prosaic-badge {
		font-size: 0.875rem;
		opacity: 0.7;
	}

	.presets {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-xs);
		margin-bottom: var(--space-md);
		padding-bottom: var(--space-md);
		border-bottom: 1px solid rgba(255, 255, 255, 0.05);
	}

	.preset-btn {
		padding: var(--space-xs) var(--space-sm);
		font-size: 0.6875rem;
		background: var(--color-bg);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-sm);
		cursor: pointer;
		transition: all var(--transition-fast);
		color: var(--color-text);
	}

	.preset-btn:hover:not(:disabled) {
		border-color: var(--color-success);
		background: rgba(16, 185, 129, 0.1);
	}

	.preset-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.dimensions {
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
	}

	.compact .dimensions {
		gap: var(--space-sm);
	}

	.dimension {
		padding: var(--space-sm);
		background: rgba(255, 255, 255, 0.02);
		border-radius: var(--radius-md);
		border-left: 3px solid var(--color-success);
		transition: border-color var(--transition-fast);
	}

	.dimension.medium {
		border-left-color: var(--color-warning);
	}

	.dimension.high {
		border-left-color: var(--color-danger);
	}

	.dim-header {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-xs);
	}

	.dim-emoji {
		font-size: 1rem;
	}

	.dim-label {
		flex: 1;
		font-size: var(--text-sm);
	}

	.compact .dim-label {
		font-size: var(--text-xs);
	}

	.dim-value {
		font-family: var(--font-mono);
		font-size: var(--text-sm);
		color: var(--color-primary);
		min-width: 2rem;
		text-align: right;
	}

	.dim-slider {
		width: 100%;
		accent-color: var(--color-success);
	}

	.dim-bar {
		height: 6px;
		background: var(--color-bg);
		border-radius: 3px;
		overflow: hidden;
	}

	.dim-bar-fill {
		height: 100%;
		border-radius: 3px;
		transition: width var(--transition-normal);
	}

	.dim-hint {
		font-size: 0.6875rem;
		color: var(--color-text-muted);
		font-style: italic;
		margin-top: var(--space-xs);
		min-height: 1rem;
	}

	.impact-section {
		margin-top: var(--space-md);
		padding-top: var(--space-md);
		border-top: 1px solid rgba(255, 255, 255, 0.05);
	}

	.impact-section h4 {
		font-size: var(--text-xs);
		color: var(--color-text-muted);
		margin: 0 0 var(--space-sm);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.impact-list {
		margin: 0;
		padding-left: var(--space-md);
		font-size: var(--text-sm);
	}

	.impact-list li {
		margin: var(--space-xs) 0;
		color: var(--color-text-muted);
	}
</style>
