<script lang="ts">
	/**
	 * PresetLoader Component
	 * Quick-load example configurations for demos
	 */

	interface Preset<T = Record<string, unknown>> {
		id: string;
		name: string;
		description?: string;
		icon?: string;
		data: T;
		tags?: string[];
	}

	interface Props<T = Record<string, unknown>> {
		presets: Preset<T>[];
		selected?: string;
		title?: string;
		showDescriptions?: boolean;
		layout?: 'cards' | 'list' | 'chips';
		onselect: (preset: Preset<T>) => void;
	}

	let {
		presets,
		selected,
		title = 'Presets',
		showDescriptions = true,
		layout = 'cards',
		onselect
	}: Props = $props();

	function handleSelect(preset: Preset) {
		onselect(preset);
	}
</script>

<div class="preset-loader layout-{layout}">
	{#if title}
		<div class="loader-header">
			<h4><i class="fa-solid fa-bookmark" aria-hidden="true"></i> {title}</h4>
		</div>
	{/if}

	{#if layout === 'cards'}
		<div class="preset-cards">
			{#each presets as preset (preset.id)}
				<button
					class="preset-card"
					class:selected={selected === preset.id}
					onclick={() => handleSelect(preset)}
				>
					{#if preset.icon}
						<span class="preset-icon"><i class="fa-solid {preset.icon}" aria-hidden="true"></i></span>
					{/if}
					<div class="preset-content">
						<span class="preset-name">{preset.name}</span>
						{#if showDescriptions && preset.description}
							<span class="preset-description">{preset.description}</span>
						{/if}
					</div>
					{#if preset.tags && preset.tags.length > 0}
						<div class="preset-tags">
							{#each preset.tags as tag}
								<span class="preset-tag">{tag}</span>
							{/each}
						</div>
					{/if}
				</button>
			{/each}
		</div>
	{:else if layout === 'list'}
		<div class="preset-list">
			{#each presets as preset (preset.id)}
				<button
					class="preset-item"
					class:selected={selected === preset.id}
					onclick={() => handleSelect(preset)}
				>
					{#if preset.icon}
						<span class="preset-icon"><i class="fa-solid {preset.icon}" aria-hidden="true"></i></span>
					{/if}
					<span class="preset-name">{preset.name}</span>
					{#if showDescriptions && preset.description}
						<span class="preset-description">{preset.description}</span>
					{/if}
					{#if selected === preset.id}
						<span class="selected-check"><i class="fa-solid fa-check" aria-hidden="true"></i></span>
					{/if}
				</button>
			{/each}
		</div>
	{:else}
		<div class="preset-chips">
			{#each presets as preset (preset.id)}
				<button
					class="preset-chip"
					class:selected={selected === preset.id}
					onclick={() => handleSelect(preset)}
					title={preset.description}
				>
					{#if preset.icon}
						<i class="fa-solid {preset.icon}" aria-hidden="true"></i>
					{/if}
					{preset.name}
				</button>
			{/each}
		</div>
	{/if}
</div>

<style>
	.preset-loader {
		display: flex;
		flex-direction: column;
		gap: var(--space-sm);
	}

	.loader-header h4 {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		font-size: 0.875rem;
		margin: 0;
		color: var(--color-text-muted);
	}

	/* Cards Layout */
	.preset-cards {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
		gap: var(--space-sm);
	}

	.preset-card {
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
		padding: var(--space-md);
		background: var(--color-bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-md);
		cursor: pointer;
		text-align: left;
		transition: all var(--transition-fast);
	}

	.preset-card:hover {
		border-color: var(--color-primary);
	}

	.preset-card.selected {
		background: var(--color-primary-muted);
		border-color: var(--color-primary);
	}

	.preset-card .preset-icon {
		font-size: 1.25rem;
		color: var(--color-text-muted);
	}

	.preset-card.selected .preset-icon {
		color: var(--color-primary);
	}

	.preset-content {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.preset-name {
		font-weight: 500;
		font-size: 0.875rem;
		color: var(--color-text);
	}

	.preset-description {
		font-size: 0.75rem;
		color: var(--color-text-muted);
		line-height: 1.4;
	}

	.preset-tags {
		display: flex;
		flex-wrap: wrap;
		gap: 4px;
		margin-top: var(--space-xs);
	}

	.preset-tag {
		font-size: 0.625rem;
		padding: 1px 6px;
		background: rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-sm);
		color: var(--color-text-subtle);
	}

	/* List Layout */
	.preset-list {
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
	}

	.preset-item {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-sm) var(--space-md);
		background: var(--color-bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-md);
		cursor: pointer;
		text-align: left;
		transition: all var(--transition-fast);
	}

	.preset-item:hover {
		border-color: var(--color-primary);
	}

	.preset-item.selected {
		background: var(--color-primary-muted);
		border-color: var(--color-primary);
	}

	.preset-item .preset-icon {
		font-size: 1rem;
		color: var(--color-text-muted);
		width: 24px;
		text-align: center;
	}

	.preset-item .preset-name {
		font-weight: 500;
		font-size: 0.8125rem;
	}

	.preset-item .preset-description {
		flex: 1;
		font-size: 0.75rem;
		color: var(--color-text-subtle);
		margin-left: auto;
	}

	.selected-check {
		color: var(--color-primary);
		font-size: 0.875rem;
	}

	/* Chips Layout */
	.preset-chips {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-xs);
	}

	.preset-chip {
		display: inline-flex;
		align-items: center;
		gap: var(--space-xs);
		padding: var(--space-xs) var(--space-sm);
		background: var(--color-bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-full);
		font-size: 0.75rem;
		color: var(--color-text-muted);
		cursor: pointer;
		transition: all var(--transition-fast);
	}

	.preset-chip:hover {
		border-color: var(--color-primary);
		color: var(--color-text);
	}

	.preset-chip.selected {
		background: var(--color-primary-muted);
		border-color: var(--color-primary);
		color: var(--color-primary);
	}

	@media (max-width: 640px) {
		.preset-cards {
			grid-template-columns: 1fr;
		}
	}
</style>
