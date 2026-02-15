<script lang="ts">
	/**
	 * DocsLayout - Documentation page layout with sidebar navigation
	 */
	import { page } from '$app/stores';

	interface Props {
		title: string;
		description?: string;
		children: import('svelte').Snippet;
	}

	let { title, description, children }: Props = $props();

	const navSections = [
		{
			title: 'Getting Started',
			items: [
				{ href: '/docs/getting-started', label: 'Quick Start', time: '5 min' },
				{ href: '/docs/concepts', label: 'Core Concepts', time: '10 min' }
			]
		},
		{
			title: 'Specifications',
			items: [
				{ href: '/docs/csm1-specification', label: 'CSM-1 Format', time: '15 min' },
				{ href: '/docs/api-reference', label: 'API Reference', time: 'Ref' }
			]
		}
	];

	let currentPath = $derived($page.url.pathname);
	let sidebarOpen = $state(false);
</script>

<div class="docs-layout">
	<!-- Mobile sidebar toggle -->
	<button
		class="sidebar-toggle"
		onclick={() => (sidebarOpen = !sidebarOpen)}
		aria-expanded={sidebarOpen}
		aria-controls="docs-sidebar"
	>
		<span class="toggle-icon">{sidebarOpen ? '✕' : '☰'}</span>
		<span class="toggle-text">Menu</span>
	</button>

	<!-- Sidebar -->
	<aside id="docs-sidebar" class="sidebar" class:open={sidebarOpen}>
		<nav class="sidebar-nav" aria-label="Documentation navigation">
			<a href="/docs" class="sidebar-home" class:active={currentPath === '/docs'}>
				<span class="home-icon">📚</span>
				Documentation Home
			</a>

			{#each navSections as section}
				<div class="nav-section">
					<h3 class="nav-section-title">{section.title}</h3>
					<ul class="nav-list">
						{#each section.items as item}
							<li>
								<a
									href={item.href}
									class="nav-link"
									class:active={currentPath === item.href}
									onclick={() => (sidebarOpen = false)}
								>
									<span class="nav-link-label">{item.label}</span>
									<span class="nav-link-time">{item.time}</span>
								</a>
							</li>
						{/each}
					</ul>
				</div>
			{/each}
		</nav>
	</aside>

	<!-- Main content -->
	<main class="docs-content">
		<header class="docs-header">
			<nav class="breadcrumbs" aria-label="Breadcrumb">
				<a href="/docs">Docs</a>
				<span class="breadcrumb-sep" aria-hidden="true">/</span>
				<span class="breadcrumb-current">{title}</span>
			</nav>
			<h1>{title}</h1>
			{#if description}
				<p class="docs-description">{description}</p>
			{/if}
		</header>

		<article class="docs-article">
			{@render children()}
		</article>

		<footer class="docs-footer">
			<div class="footer-nav">
				<a href="/docs" class="footer-link">
					<span class="footer-link-direction">←</span>
					<span>Back to Docs</span>
				</a>
				<a href="/playground" class="footer-link">
					<span>Try the Playground</span>
					<span class="footer-link-direction">→</span>
				</a>
			</div>
		</footer>
	</main>
</div>

<!-- Overlay for mobile -->
{#if sidebarOpen}
	<button
		class="sidebar-overlay"
		onclick={() => (sidebarOpen = false)}
		aria-label="Close sidebar"
	></button>
{/if}

<style>
	.docs-layout {
		display: grid;
		grid-template-columns: 280px 1fr;
		min-height: calc(100vh - 80px);
	}

	/* ============================================
	   Sidebar
	   ============================================ */

	.sidebar {
		background: var(--color-bg-elevated);
		border-right: 1px solid rgba(255, 255, 255, 0.1);
		padding: var(--space-lg);
		position: sticky;
		top: 60px;
		height: calc(100vh - 60px);
		overflow-y: auto;
	}

	.sidebar-home {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-md);
		border-radius: var(--radius-md);
		color: var(--color-text);
		text-decoration: none;
		font-weight: 500;
		margin-bottom: var(--space-lg);
		transition: all var(--transition-fast);
	}

	.sidebar-home:hover {
		background: rgba(255, 255, 255, 0.05);
		text-decoration: none;
	}

	.sidebar-home.active {
		background: var(--color-primary-muted);
		color: var(--color-primary);
	}

	.home-icon {
		font-size: 1.25rem;
	}

	.nav-section {
		margin-bottom: var(--space-lg);
	}

	.nav-section-title {
		font-size: 0.6875rem;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--color-text-subtle);
		padding: 0 var(--space-md);
		margin-bottom: var(--space-sm);
	}

	.nav-list {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.nav-link {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: var(--space-sm) var(--space-md);
		border-radius: var(--radius-sm);
		color: var(--color-text-muted);
		text-decoration: none;
		font-size: 0.875rem;
		transition: all var(--transition-fast);
	}

	.nav-link:hover {
		color: var(--color-text);
		background: rgba(255, 255, 255, 0.05);
		text-decoration: none;
	}

	.nav-link.active {
		color: var(--color-primary);
		background: var(--color-primary-muted);
	}

	.nav-link-time {
		font-size: 0.6875rem;
		color: var(--color-text-subtle);
	}

	.nav-link.active .nav-link-time {
		color: var(--color-primary);
		opacity: 0.7;
	}

	/* ============================================
	   Content
	   ============================================ */

	.docs-content {
		padding: var(--space-xl) var(--space-2xl);
		max-width: 900px;
	}

	.docs-header {
		margin-bottom: var(--space-2xl);
		padding-bottom: var(--space-xl);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.breadcrumbs {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-size: 0.8125rem;
		margin-bottom: var(--space-md);
	}

	.breadcrumbs a {
		color: var(--color-text-muted);
		text-decoration: none;
	}

	.breadcrumbs a:hover {
		color: var(--color-primary);
	}

	.breadcrumb-sep {
		color: var(--color-text-subtle);
	}

	.breadcrumb-current {
		color: var(--color-text);
	}

	.docs-header h1 {
		font-size: 2rem;
		margin-bottom: var(--space-sm);
	}

	.docs-description {
		color: var(--color-text-muted);
		font-size: 1.125rem;
		line-height: 1.6;
	}

	.docs-article {
		line-height: 1.7;
	}

	/* Article typography */
	.docs-article :global(h2) {
		font-size: 1.5rem;
		margin-top: var(--space-2xl);
		margin-bottom: var(--space-md);
		padding-bottom: var(--space-sm);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.docs-article :global(h3) {
		font-size: 1.25rem;
		margin-top: var(--space-xl);
		margin-bottom: var(--space-sm);
	}

	.docs-article :global(h4) {
		font-size: 1rem;
		margin-top: var(--space-lg);
		margin-bottom: var(--space-sm);
		color: var(--color-text-muted);
	}

	.docs-article :global(p) {
		margin-bottom: var(--space-md);
	}

	.docs-article :global(ul),
	.docs-article :global(ol) {
		margin-bottom: var(--space-md);
		padding-left: var(--space-xl);
	}

	.docs-article :global(li) {
		margin-bottom: var(--space-sm);
	}

	.docs-article :global(code) {
		font-family: var(--font-mono);
		font-size: 0.875em;
		background: var(--color-bg-elevated);
		padding: 2px 6px;
		border-radius: var(--radius-sm);
	}

	.docs-article :global(pre) {
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		padding: var(--space-lg);
		overflow-x: auto;
		margin-bottom: var(--space-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.docs-article :global(pre code) {
		background: none;
		padding: 0;
		font-size: 0.8125rem;
		line-height: 1.6;
	}

	.docs-article :global(table) {
		width: 100%;
		border-collapse: collapse;
		margin-bottom: var(--space-lg);
	}

	.docs-article :global(th),
	.docs-article :global(td) {
		padding: var(--space-sm) var(--space-md);
		border: 1px solid rgba(255, 255, 255, 0.1);
		text-align: left;
	}

	.docs-article :global(th) {
		background: var(--color-bg-elevated);
		font-weight: 600;
	}

	.docs-article :global(blockquote) {
		border-left: 3px solid var(--color-primary);
		padding-left: var(--space-lg);
		margin: var(--space-lg) 0;
		color: var(--color-text-muted);
		font-style: italic;
	}

	/* ============================================
	   Footer
	   ============================================ */

	.docs-footer {
		margin-top: var(--space-2xl);
		padding-top: var(--space-xl);
		border-top: 1px solid rgba(255, 255, 255, 0.1);
	}

	.footer-nav {
		display: flex;
		justify-content: space-between;
	}

	.footer-link {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		color: var(--color-text-muted);
		text-decoration: none;
		font-size: 0.875rem;
		padding: var(--space-sm) var(--space-md);
		border-radius: var(--radius-md);
		transition: all var(--transition-fast);
	}

	.footer-link:hover {
		color: var(--color-primary);
		background: var(--color-primary-muted);
		text-decoration: none;
	}

	.footer-link-direction {
		font-size: 1.25rem;
	}

	/* ============================================
	   Mobile Toggle
	   ============================================ */

	.sidebar-toggle {
		display: none;
		position: fixed;
		bottom: var(--space-lg);
		right: var(--space-lg);
		z-index: 200;
		background: var(--color-primary);
		color: white;
		border: none;
		border-radius: var(--radius-full);
		padding: var(--space-md) var(--space-lg);
		font-weight: 500;
		cursor: pointer;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
	}

	.sidebar-toggle:hover {
		background: var(--color-primary-hover);
	}

	.toggle-icon {
		margin-right: var(--space-xs);
	}

	.sidebar-overlay {
		display: none;
	}

	/* ============================================
	   Responsive
	   ============================================ */

	@media (max-width: 1024px) {
		.docs-layout {
			grid-template-columns: 1fr;
		}

		.sidebar {
			position: fixed;
			left: -280px;
			top: 60px;
			height: calc(100vh - 60px);
			z-index: 150;
			transition: left var(--transition-normal);
		}

		.sidebar.open {
			left: 0;
		}

		.sidebar-toggle {
			display: flex;
			align-items: center;
		}

		.sidebar-overlay {
			display: block;
			position: fixed;
			inset: 0;
			background: rgba(0, 0, 0, 0.5);
			z-index: 140;
			border: none;
			cursor: pointer;
		}

		.docs-content {
			padding: var(--space-lg);
		}
	}

	@media (max-width: 640px) {
		.docs-header h1 {
			font-size: 1.5rem;
		}

		.docs-description {
			font-size: 1rem;
		}

		.footer-nav {
			flex-direction: column;
			gap: var(--space-sm);
		}
	}
</style>
