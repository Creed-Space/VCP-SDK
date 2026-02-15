<script lang="ts">
	/**
	 * Breadcrumb Navigation Component
	 * Provides consistent wayfinding across all pages
	 */

	interface BreadcrumbItem {
		label: string;
		href?: string;
		icon?: string;
	}

	interface Props {
		items: BreadcrumbItem[];
	}

	let { items }: Props = $props();
</script>

<nav class="breadcrumb" aria-label="Breadcrumb navigation">
	<ol class="breadcrumb-list">
		<li class="breadcrumb-item">
			<a href="/" class="breadcrumb-link breadcrumb-home" aria-label="Home">
				<i class="fa-solid fa-house" aria-hidden="true"></i>
			</a>
		</li>
		{#each items as item, index}
			<li class="breadcrumb-separator" aria-hidden="true">
				<i class="fa-solid fa-chevron-right"></i>
			</li>
			<li class="breadcrumb-item">
				{#if item.href && index < items.length - 1}
					<a href={item.href} class="breadcrumb-link">
						{#if item.icon}
							<i class="fa-solid {item.icon}" aria-hidden="true"></i>
						{/if}
						{item.label}
					</a>
				{:else}
					<span class="breadcrumb-current" aria-current="page">
						{#if item.icon}
							<i class="fa-solid {item.icon}" aria-hidden="true"></i>
						{/if}
						{item.label}
					</span>
				{/if}
			</li>
		{/each}
	</ol>
</nav>

<style>
	.breadcrumb {
		margin-bottom: var(--space-lg);
	}

	.breadcrumb-list {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		list-style: none;
		margin: 0;
		padding: 0;
		flex-wrap: wrap;
	}

	.breadcrumb-item {
		display: flex;
		align-items: center;
	}

	.breadcrumb-link {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		color: var(--color-text-muted);
		text-decoration: none;
		font-size: var(--text-sm);
		padding: var(--space-xs) var(--space-sm);
		border-radius: var(--radius-sm);
		transition: all var(--transition-fast);
	}

	.breadcrumb-link:hover {
		color: var(--color-text);
		background: rgba(255, 255, 255, 0.05);
		text-decoration: none;
	}

	.breadcrumb-home {
		padding: var(--space-xs);
	}

	.breadcrumb-separator {
		color: var(--color-text-subtle);
		font-size: 0.625rem;
	}

	.breadcrumb-current {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		color: var(--color-text);
		font-size: var(--text-sm);
		font-weight: 500;
		padding: var(--space-xs) var(--space-sm);
	}

	@media (max-width: 640px) {
		.breadcrumb-list {
			gap: var(--space-xs);
		}

		.breadcrumb-link,
		.breadcrumb-current {
			font-size: var(--text-xs);
			padding: var(--space-xs);
		}
	}
</style>
