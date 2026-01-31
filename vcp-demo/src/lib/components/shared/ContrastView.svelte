<script lang="ts">
	/**
	 * ContrastView Component
	 * Side-by-side comparison of VCP contexts showing different outcomes
	 */

	interface ContrastItem {
		id: string;
		name: string;
		description?: string;
		context: Record<string, unknown>;
		outcome?: string;
		highlights?: string[];
	}

	interface Props {
		items: ContrastItem[];
		title?: string;
		showOutcomes?: boolean;
		columns?: 2 | 3;
		baseline?: ContrastItem;
	}

	let {
		items,
		title = 'Context Comparison',
		showOutcomes = true,
		columns = 2,
		baseline
	}: Props = $props();

	// Default selection derived from props - recomputes when items/columns change
	const defaultSelection = $derived(items.slice(0, columns).map((i) => i.id));

	// Track user's manual selection separately
	let userSelection = $state<string[] | null>(null);

	// Final selected items: user selection if valid, otherwise default
	const selectedItems = $derived.by(() => {
		if (userSelection === null) {
			return defaultSelection;
		}
		// Filter out any invalid IDs if items changed
		const validIds = new Set(items.map((i) => i.id));
		const validSelection = userSelection.filter((id) => validIds.has(id));
		return validSelection.length > 0 ? validSelection : defaultSelection;
	});

	let showBaseline = $state(false);

	function toggleItem(id: string) {
		const current = selectedItems;
		if (current.includes(id)) {
			if (current.length > 1) {
				userSelection = current.filter((i) => i !== id);
			}
		} else {
			if (current.length >= columns) {
				userSelection = [...current.slice(1), id];
			} else {
				userSelection = [...current, id];
			}
		}
	}

	const displayedItems = $derived(
		showBaseline && baseline
			? [baseline, ...items.filter((i) => selectedItems.includes(i.id))]
			: items.filter((i) => selectedItems.includes(i.id))
	);
</script>

<div class="contrast-view">
	<div class="contrast-header">
		<h3>{title}</h3>
		<div class="contrast-controls">
			{#if baseline}
				<label class="baseline-toggle">
					<input type="checkbox" bind:checked={showBaseline} />
					<span>Show baseline (no VCP)</span>
				</label>
			{/if}
			<div class="item-selector">
				{#each items as item}
					<button
						class="selector-btn"
						class:selected={selectedItems.includes(item.id)}
						onclick={() => toggleItem(item.id)}
						title={item.description}
					>
						{item.name}
					</button>
				{/each}
			</div>
		</div>
	</div>

	<div class="contrast-grid" style="--columns: {displayedItems.length}">
		{#each displayedItems as item (item.id)}
			<div class="contrast-column" class:baseline-column={item === baseline}>
				<div class="column-header">
					<span class="column-name">{item.name}</span>
					{#if item === baseline}
						<span class="baseline-badge">Baseline</span>
					{/if}
				</div>

				{#if item.description}
					<p class="column-description">{item.description}</p>
				{/if}

				<div class="context-display">
					<div class="context-label">Context</div>
					<div class="context-content">
						{#each Object.entries(item.context) as [key, value]}
							<div class="context-row">
								<span class="context-key">{key}</span>
								<span class="context-value">{typeof value === 'object' ? JSON.stringify(value) : value}</span>
							</div>
						{/each}
					</div>
				</div>

				{#if showOutcomes && item.outcome}
					<div class="outcome-display">
						<div class="outcome-label">Outcome</div>
						<div class="outcome-content">{item.outcome}</div>
					</div>
				{/if}

				{#if item.highlights && item.highlights.length > 0}
					<div class="highlights">
						{#each item.highlights as highlight}
							<span class="highlight-tag">{highlight}</span>
						{/each}
					</div>
				{/if}
			</div>
		{/each}
	</div>
</div>

<style>
	.contrast-view {
		display: flex;
		flex-direction: column;
		gap: var(--space-lg);
	}

	.contrast-header {
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
	}

	.contrast-header h3 {
		font-size: 1rem;
		margin: 0;
	}

	.contrast-controls {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: var(--space-md);
	}

	.baseline-toggle {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		cursor: pointer;
	}

	.baseline-toggle input {
		accent-color: var(--color-primary);
	}

	.item-selector {
		display: flex;
		gap: var(--space-xs);
		flex-wrap: wrap;
	}

	.selector-btn {
		padding: var(--space-xs) var(--space-sm);
		background: var(--color-bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-sm);
		font-size: 0.75rem;
		color: var(--color-text-muted);
		cursor: pointer;
		transition: all var(--transition-fast);
	}

	.selector-btn:hover {
		border-color: var(--color-primary);
	}

	.selector-btn.selected {
		background: var(--color-primary-muted);
		border-color: var(--color-primary);
		color: var(--color-primary);
	}

	.contrast-grid {
		display: grid;
		grid-template-columns: repeat(var(--columns), 1fr);
		gap: var(--space-lg);
	}

	.contrast-column {
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.contrast-column.baseline-column {
		background: var(--color-bg-elevated);
		border-color: var(--color-text-subtle);
		opacity: 0.85;
	}

	.column-header {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
	}

	.column-name {
		font-weight: 600;
		font-size: 0.9375rem;
	}

	.baseline-badge {
		font-size: 0.625rem;
		padding: 2px 6px;
		background: var(--color-bg-hover);
		color: var(--color-text-muted);
		border-radius: var(--radius-sm);
		text-transform: uppercase;
	}

	.column-description {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		margin: 0;
	}

	.context-display,
	.outcome-display {
		background: var(--color-bg);
		border-radius: var(--radius-md);
		overflow: hidden;
	}

	.context-label,
	.outcome-label {
		font-size: 0.625rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-muted);
		padding: var(--space-xs) var(--space-sm);
		background: rgba(255, 255, 255, 0.05);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.context-content {
		padding: var(--space-sm);
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
	}

	.context-row {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: var(--space-sm);
		font-size: 0.75rem;
	}

	.context-key {
		color: var(--color-text-muted);
		white-space: nowrap;
	}

	.context-value {
		font-family: var(--font-mono);
		color: var(--color-text);
		text-align: right;
		word-break: break-all;
	}

	.outcome-content {
		padding: var(--space-sm);
		font-size: 0.8125rem;
		line-height: 1.5;
	}

	.highlights {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-xs);
	}

	.highlight-tag {
		font-size: 0.6875rem;
		padding: 2px 8px;
		background: var(--color-primary-muted);
		color: var(--color-primary);
		border-radius: var(--radius-sm);
	}

	@media (max-width: 768px) {
		.contrast-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
