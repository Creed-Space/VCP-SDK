<script lang="ts">
	/**
	 * DimensionSlider - Individual dimension control with 1-9 scale
	 */

	interface Props {
		label: string;
		value: number;
		min?: number;
		max?: number;
		emoji?: string;
		lowLabel?: string;
		highLabel?: string;
		uncertain?: boolean;
		onchange?: (value: number) => void;
	}

	let {
		label,
		value = 5,
		min = 1,
		max = 9,
		emoji = '',
		lowLabel = '',
		highLabel = '',
		uncertain = false,
		onchange
	}: Props = $props();

	function handleChange(e: Event) {
		const target = e.target as HTMLInputElement;
		onchange?.(parseInt(target.value, 10));
	}

	function getColorClass(val: number): string {
		if (val <= 3) return 'low';
		if (val <= 6) return 'mid';
		return 'high';
	}
</script>

<div class="dimension-slider">
	<div class="slider-header">
		<span class="slider-label">
			{#if emoji}<span class="slider-emoji">{emoji}</span>{/if}
			{label}
			{#if uncertain}<span class="uncertain-marker">?</span>{/if}
		</span>
		<span class="slider-value {getColorClass(value)}">{value}</span>
	</div>

	<div class="slider-track">
		<input
			type="range"
			{min}
			{max}
			{value}
			oninput={handleChange}
			class="slider-input"
			aria-label="{label} slider"
		/>
		<div
			class="slider-fill {getColorClass(value)}"
			style="width: {((value - min) / (max - min)) * 100}%"
		></div>
	</div>

	{#if lowLabel || highLabel}
		<div class="slider-labels">
			<span class="label-low">{lowLabel}</span>
			<span class="label-high">{highLabel}</span>
		</div>
	{/if}
</div>

<style>
	.dimension-slider {
		padding: var(--space-sm) 0;
	}

	.slider-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--space-xs);
	}

	.slider-label {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		font-size: 0.875rem;
		font-weight: 500;
	}

	.slider-emoji {
		font-size: 1rem;
	}

	.uncertain-marker {
		font-size: 0.75rem;
		color: var(--color-warning);
		margin-left: 2px;
	}

	.slider-value {
		font-size: 1rem;
		font-weight: 700;
		font-family: var(--font-mono);
		width: 24px;
		text-align: center;
	}

	.slider-value.low {
		color: #e74c3c;
	}

	.slider-value.mid {
		color: #f39c12;
	}

	.slider-value.high {
		color: #2ecc71;
	}

	.slider-track {
		position: relative;
		height: 8px;
		background: var(--color-bg-elevated);
		border-radius: var(--radius-full);
		overflow: hidden;
	}

	.slider-input {
		position: absolute;
		width: 100%;
		height: 100%;
		opacity: 0;
		cursor: pointer;
		z-index: 2;
		margin: 0;
	}

	.slider-fill {
		position: absolute;
		height: 100%;
		border-radius: var(--radius-full);
		transition: width var(--transition-fast);
		pointer-events: none;
	}

	.slider-fill.low {
		background: linear-gradient(90deg, #e74c3c, #c0392b);
	}

	.slider-fill.mid {
		background: linear-gradient(90deg, #f39c12, #e67e22);
	}

	.slider-fill.high {
		background: linear-gradient(90deg, #2ecc71, #27ae60);
	}

	.slider-labels {
		display: flex;
		justify-content: space-between;
		margin-top: 4px;
		font-size: 0.6875rem;
		color: var(--color-text-subtle);
	}
</style>
