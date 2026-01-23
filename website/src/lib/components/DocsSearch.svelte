<script lang="ts">
	/**
	 * DocsSearch - Documentation search component
	 */
	import { searchDocs, type SearchResult } from '$lib/search';

	interface Props {
		onSelect?: (path: string) => void;
	}

	let { onSelect }: Props = $props();

	let query = $state('');
	let results = $state<SearchResult[]>([]);
	let isOpen = $state(false);
	let selectedIndex = $state(-1);
	let inputElement: HTMLInputElement;

	$effect(() => {
		if (query.length >= 2) {
			results = searchDocs(query);
			isOpen = results.length > 0;
			selectedIndex = -1;
		} else {
			results = [];
			isOpen = false;
		}
	});

	function handleKeydown(event: KeyboardEvent) {
		if (!isOpen) return;

		switch (event.key) {
			case 'ArrowDown':
				event.preventDefault();
				selectedIndex = Math.min(selectedIndex + 1, results.length - 1);
				break;
			case 'ArrowUp':
				event.preventDefault();
				selectedIndex = Math.max(selectedIndex - 1, -1);
				break;
			case 'Enter':
				event.preventDefault();
				if (selectedIndex >= 0 && results[selectedIndex]) {
					selectResult(results[selectedIndex]);
				}
				break;
			case 'Escape':
				isOpen = false;
				inputElement?.blur();
				break;
		}
	}

	function selectResult(result: SearchResult) {
		query = '';
		isOpen = false;
		if (onSelect) {
			onSelect(result.path);
		} else {
			window.location.href = result.path;
		}
	}

	function handleBlur() {
		// Delay to allow click on results
		setTimeout(() => {
			isOpen = false;
		}, 200);
	}
</script>

<div class="docs-search">
	<div class="search-input-wrapper">
		<i class="fa-solid fa-magnifying-glass search-icon" aria-hidden="true"></i>
		<input
			bind:this={inputElement}
			type="search"
			placeholder="Search docs..."
			bind:value={query}
			onkeydown={handleKeydown}
			onblur={handleBlur}
			onfocus={() => query.length >= 2 && results.length > 0 && (isOpen = true)}
			aria-label="Search documentation"
			aria-haspopup="listbox"
			aria-autocomplete="list"
		/>
		{#if query}
			<button
				class="clear-btn"
				onclick={() => {
					query = '';
					inputElement?.focus();
				}}
				aria-label="Clear search"
			>
				<i class="fa-solid fa-xmark" aria-hidden="true"></i>
			</button>
		{/if}
	</div>

	{#if isOpen}
		<div id="search-results" class="search-results" role="listbox">
			{#each results as result, i}
				<button
					class="search-result"
					class:selected={i === selectedIndex}
					onclick={() => selectResult(result)}
					role="option"
					aria-selected={i === selectedIndex}
				>
					<div class="result-header">
						<span class="result-title">{result.title}</span>
						{#if result.section}
							<span class="result-section">{result.section}</span>
						{/if}
					</div>
					<p class="result-excerpt">{result.excerpt}</p>
				</button>
			{/each}
			{#if results.length === 0}
				<div class="no-results">No results found</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	.docs-search {
		position: relative;
		width: 100%;
		max-width: 400px;
	}

	.search-input-wrapper {
		position: relative;
		display: flex;
		align-items: center;
	}

	.search-icon {
		position: absolute;
		left: var(--space-sm);
		color: var(--color-text-muted);
		font-size: 0.875rem;
		pointer-events: none;
	}

	input {
		width: 100%;
		padding: var(--space-sm) var(--space-md);
		padding-left: calc(var(--space-sm) + 1.5rem);
		padding-right: calc(var(--space-sm) + 1.5rem);
		background: var(--color-bg-elevated);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-md);
		color: var(--color-text);
		font-size: 0.875rem;
		transition: all var(--transition-fast);
	}

	input:focus {
		outline: none;
		border-color: var(--color-primary);
		box-shadow: 0 0 0 2px var(--color-primary-muted);
	}

	input::placeholder {
		color: var(--color-text-subtle);
	}

	.clear-btn {
		position: absolute;
		right: var(--space-xs);
		padding: var(--space-xs);
		background: none;
		border: none;
		color: var(--color-text-muted);
		cursor: pointer;
		border-radius: var(--radius-sm);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.clear-btn:hover {
		color: var(--color-text);
		background: rgba(255, 255, 255, 0.1);
	}

	.search-results {
		position: absolute;
		top: 100%;
		left: 0;
		right: 0;
		margin-top: var(--space-xs);
		background: var(--color-bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-md);
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
		max-height: 400px;
		overflow-y: auto;
		z-index: 100;
	}

	.search-result {
		display: block;
		width: 100%;
		padding: var(--space-md);
		text-align: left;
		background: none;
		border: none;
		border-bottom: 1px solid rgba(255, 255, 255, 0.05);
		cursor: pointer;
		transition: background var(--transition-fast);
	}

	.search-result:last-child {
		border-bottom: none;
	}

	.search-result:hover,
	.search-result.selected {
		background: rgba(255, 255, 255, 0.05);
	}

	.search-result:focus-visible {
		outline: 2px solid var(--color-primary);
		outline-offset: -2px;
	}

	.result-header {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-xs);
	}

	.result-title {
		font-weight: 500;
		color: var(--color-text);
	}

	.result-section {
		font-size: 0.6875rem;
		padding: 2px 6px;
		background: var(--color-primary-muted);
		color: var(--color-primary);
		border-radius: var(--radius-sm);
	}

	.result-excerpt {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		margin: 0;
		line-height: 1.4;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.no-results {
		padding: var(--space-lg);
		text-align: center;
		color: var(--color-text-muted);
		font-size: 0.875rem;
	}
</style>
