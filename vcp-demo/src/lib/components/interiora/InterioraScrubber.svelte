<script lang="ts">
	/**
	 * InterioraScrubber - Timeline of VCP states through session
	 */
	import type { InterioraState } from '$lib/vcp/interiora';

	interface StateSnapshot {
		timestamp: string;
		state: InterioraState;
		label?: string;
	}

	interface Props {
		snapshots: StateSnapshot[];
		currentIndex: number;
		onSelect?: (index: number) => void;
	}

	let { snapshots = [], currentIndex = 0, onSelect }: Props = $props();

	function getValenceColor(valence: number): string {
		if (valence <= 3) return '#e74c3c';
		if (valence <= 6) return '#f39c12';
		return '#2ecc71';
	}

	function getFlowDirection(flow: number | undefined): string {
		if (flow === undefined) return '→';
		if (flow > 0) return '↗';
		if (flow < 0) return '↘';
		return '→';
	}

	function formatTime(timestamp: string): string {
		try {
			return new Date(timestamp).toLocaleTimeString([], {
				hour: '2-digit',
				minute: '2-digit'
			});
		} catch {
			return '';
		}
	}
</script>

<div class="scrubber">
	<div class="scrubber-track">
		{#each snapshots as snapshot, i}
			<button
				class="scrubber-point"
				class:active={i === currentIndex}
				onclick={() => onSelect?.(i)}
				style="--valence-color: {getValenceColor(snapshot.state.valence)}"
				title="{snapshot.label || `State ${i + 1}`} - {formatTime(snapshot.timestamp)}"
			>
				<span class="point-marker"></span>
				{#if i < snapshots.length - 1}
					<span class="point-connector"></span>
				{/if}
			</button>
		{/each}
	</div>

	<div class="scrubber-labels">
		{#each snapshots as snapshot, i}
			<span class="scrubber-label" class:active={i === currentIndex}>
				{#if snapshot.label}
					{snapshot.label}
				{:else}
					{formatTime(snapshot.timestamp)}
				{/if}
			</span>
		{/each}
	</div>

	{#if snapshots[currentIndex]}
		<div class="scrubber-preview">
			<div class="preview-header">
				<span class="preview-time">{formatTime(snapshots[currentIndex].timestamp)}</span>
				<span class="preview-flow">{getFlowDirection(snapshots[currentIndex].state.flow)}</span>
				{#if snapshots[currentIndex].state.delta !== undefined}
					<span
						class="preview-delta"
						class:positive={snapshots[currentIndex].state.delta! > 0}
						class:negative={snapshots[currentIndex].state.delta! < 0}
					>
						Δ{snapshots[currentIndex].state.delta! >= 0 ? '+' : ''}{snapshots[currentIndex].state
							.delta}
					</span>
				{/if}
			</div>
			<div class="preview-dims">
				<span class="dim">⚡{snapshots[currentIndex].state.activation}</span>
				<span class="dim">💛{snapshots[currentIndex].state.valence}</span>
				<span class="dim">⚓{snapshots[currentIndex].state.groundedness}</span>
				<span class="dim">🫂{snapshots[currentIndex].state.presence}</span>
			</div>
		</div>
	{/if}
</div>

<style>
	.scrubber {
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
	}

	.scrubber-track {
		display: flex;
		align-items: center;
		padding: var(--space-md) 0;
	}

	.scrubber-point {
		display: flex;
		align-items: center;
		background: none;
		border: none;
		padding: 0;
		cursor: pointer;
		flex: 1;
	}

	.scrubber-point:last-child {
		flex: 0;
	}

	.point-marker {
		width: 16px;
		height: 16px;
		border-radius: 50%;
		background: var(--color-bg-elevated);
		border: 3px solid var(--valence-color);
		transition: all var(--transition-fast);
		flex-shrink: 0;
	}

	.scrubber-point:hover .point-marker {
		transform: scale(1.2);
	}

	.scrubber-point.active .point-marker {
		background: var(--valence-color);
		box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.2);
	}

	.point-connector {
		flex: 1;
		height: 2px;
		background: var(--color-bg-elevated);
		margin: 0 4px;
	}

	.scrubber-labels {
		display: flex;
		justify-content: space-between;
		margin-top: var(--space-xs);
	}

	.scrubber-label {
		font-size: 0.6875rem;
		color: var(--color-text-subtle);
		text-align: center;
		flex: 1;
		transition: color var(--transition-fast);
	}

	.scrubber-label:last-child {
		flex: 0;
		text-align: right;
	}

	.scrubber-label:first-child {
		text-align: left;
	}

	.scrubber-label.active {
		color: var(--color-primary);
		font-weight: 500;
	}

	.scrubber-preview {
		margin-top: var(--space-md);
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
	}

	.preview-header {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-sm);
	}

	.preview-time {
		font-family: var(--font-mono);
		font-size: 0.8125rem;
		color: var(--color-text-muted);
	}

	.preview-flow {
		font-size: 1rem;
		color: var(--color-success);
	}

	.preview-delta {
		font-family: var(--font-mono);
		font-size: 0.75rem;
		padding: 2px 6px;
		border-radius: var(--radius-sm);
		margin-left: auto;
	}

	.preview-delta.positive {
		background: var(--color-success-muted);
		color: var(--color-success);
	}

	.preview-delta.negative {
		background: var(--color-danger-muted);
		color: var(--color-danger);
	}

	.preview-dims {
		display: flex;
		gap: var(--space-md);
	}

	.dim {
		font-family: var(--font-mono);
		font-size: 0.9375rem;
	}
</style>
