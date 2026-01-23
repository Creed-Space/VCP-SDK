<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';

	interface Props {
		children: import('svelte').Snippet;
	}

	let { children }: Props = $props();
	let mobileMenuOpen = $state(false);
	let error = $state<Error | null>(null);
	let logoError = $state(false);

	function handleError(e: Error) {
		error = e;
		console.error('VCP Demo Error:', e);
	}

	function clearError() {
		error = null;
	}

	// Focus main content for skip link
	function focusMain() {
		const main = document.getElementById('main-content');
		main?.focus();
	}

	// Handle logo load error
	function handleLogoError() {
		logoError = true;
	}

	// Global error boundary + navigation listener + service worker
	onMount(() => {
		const handleGlobalError = (event: ErrorEvent) => {
			handleError(event.error || new Error(event.message));
		};

		const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
			handleError(event.reason instanceof Error ? event.reason : new Error(String(event.reason)));
		};

		window.addEventListener('error', handleGlobalError);
		window.addEventListener('unhandledrejection', handleUnhandledRejection);

		// Close mobile menu on navigation (back/forward)
		const unsubscribe = page.subscribe(() => {
			mobileMenuOpen = false;
		});

		// Register service worker for offline support
		if ('serviceWorker' in navigator) {
			navigator.serviceWorker
				.register('/sw.js')
				.then((registration) => {
					console.log('SW registered:', registration.scope);
				})
				.catch((err) => {
					console.log('SW registration failed:', err);
				});
		}

		return () => {
			window.removeEventListener('error', handleGlobalError);
			window.removeEventListener('unhandledrejection', handleUnhandledRejection);
			unsubscribe();
		};
	});
</script>

<div class="app">
	<!-- Skip to main content for keyboard users -->
	<a href="#main-content" class="skip-link" onclick={focusMain}>Skip to main content</a>

	<header class="app-header">
		<nav class="container flex items-center justify-between">
			<a href="/" class="logo" aria-label="VCP Demo Home">
				{#if logoError}
					<span class="logo-text">VCP</span>
				{:else}
					<img src="/vcp-logo.png" alt="VCP" class="logo-img" onerror={handleLogoError} />
				{/if}
				<span class="logo-badge">Demo</span>
			</a>

			<!-- Desktop Nav -->
			<div class="nav-links desktop-nav" role="navigation" aria-label="Main navigation">
				<a href="/about" class="nav-link">About</a>
				<a href="/demos" class="nav-link">Demos</a>
				<a href="/docs" class="nav-link">Docs</a>
				<a href="/playground" class="nav-link">Playground</a>
				<span class="nav-divider" aria-hidden="true"></span>
				<a
					href="https://creed.space"
					target="_blank"
					rel="noopener noreferrer"
					class="nav-link nav-link-brand"
					aria-label="Learn more about Creed Space (opens in new tab)"
				>
					<span class="brand-icon" aria-hidden="true">◈</span>
					Creed Space
				</a>
			</div>

			<!-- Mobile Menu Button -->
			<button
				class="mobile-menu-btn"
				onclick={() => (mobileMenuOpen = !mobileMenuOpen)}
				aria-expanded={mobileMenuOpen}
				aria-controls="mobile-nav"
				aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
			>
				<span class="hamburger" class:open={mobileMenuOpen}>
					<span></span>
					<span></span>
					<span></span>
				</span>
			</button>
		</nav>

		<!-- Mobile Nav -->
		{#if mobileMenuOpen}
			<div
				id="mobile-nav"
				class="mobile-nav animate-fade-in"
				role="navigation"
				aria-label="Mobile navigation"
			>
				<a href="/about" class="mobile-nav-link" onclick={() => (mobileMenuOpen = false)}>
					About VCP
				</a>
				<a href="/demos" class="mobile-nav-link" onclick={() => (mobileMenuOpen = false)}>
					Interactive Demos
				</a>
				<a href="/docs" class="mobile-nav-link" onclick={() => (mobileMenuOpen = false)}>
					Documentation
				</a>
				<a href="/playground" class="mobile-nav-link" onclick={() => (mobileMenuOpen = false)}>
					Playground
				</a>
				<hr class="mobile-nav-divider" />
				<a
					href="https://creed.space"
					target="_blank"
					rel="noopener noreferrer"
					class="mobile-nav-link mobile-nav-brand"
				>
					<span class="brand-icon" aria-hidden="true">◈</span>
					Creed Space
				</a>
			</div>
		{/if}
	</header>

	<main id="main-content" tabindex="-1">
		{#if error}
			<div class="error-boundary container" role="alert">
				<div class="error-content">
					<span class="error-icon" aria-hidden="true"><i class="fa-solid fa-triangle-exclamation"></i></span>
					<h2>Something went wrong</h2>
					<p class="text-muted">{error.message || 'An unexpected error occurred'}</p>
					<button class="btn btn-primary" onclick={clearError}>
						Try Again
					</button>
				</div>
			</div>
		{:else}
			{@render children()}
		{/if}
	</main>

	<footer class="app-footer">
		<div class="container">
			<div class="footer-content">
				<div class="footer-brand">
					{#if logoError}
						<span class="footer-logo-text">VCP</span>
					{:else}
						<img src="/vcp-logo.png" alt="VCP" class="footer-logo-img" onerror={handleLogoError} />
					{/if}
					<div>
						<p class="footer-title">Value Context Protocol</p>
						<p class="footer-tagline">Your context stays yours. Private reasons stay private.</p>
					</div>
				</div>

				<div class="footer-links">
					<div class="footer-section">
						<h4>Demos</h4>
						<a href="/sharing">Sharing</a>
						<a href="/coordination">Coordination</a>
						<a href="/self-modeling">Self-Modeling</a>
						<a href="/adaptation">Adaptation</a>
						<a href="/psychosecurity">Psychosecurity</a>
					</div>
					<div class="footer-section">
						<h4>Learn More</h4>
						<a href="https://creed.space" target="_blank" rel="noopener noreferrer">
							Creed Space
						</a>
						<a href="https://github.com/creed-space" target="_blank" rel="noopener noreferrer">
							GitHub
						</a>
					</div>
				</div>
			</div>

			<div class="footer-bottom">
				<p>
					Built with <span aria-label="love"><i class="fa-solid fa-heart" aria-hidden="true"></i></span> by
					<a href="https://creed.space" target="_blank" rel="noopener noreferrer">Creed Space</a>
				</p>
				<p class="footer-version">VCP Demo v0.1</p>
			</div>
		</div>
	</footer>
</div>

<style>
	.app {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}

	/* ============================================
	   Header
	   ============================================ */

	.app-header {
		background: var(--color-bg-elevated);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
		padding: var(--space-md) 0;
		position: sticky;
		top: 0;
		z-index: 100;
		backdrop-filter: blur(8px);
	}

	.logo {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		text-decoration: none;
		color: var(--color-text);
	}

	.logo:hover {
		text-decoration: none;
	}

	.logo-img {
		height: 96px;
		width: auto;
	}

	.logo-text {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--color-primary);
	}

	.logo-badge {
		font-size: 0.625rem;
		padding: 2px 6px;
		background: var(--color-primary-muted);
		color: var(--color-primary);
		border-radius: var(--radius-sm);
		font-weight: 500;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	/* Desktop Nav */
	.desktop-nav {
		display: flex;
		align-items: center;
		gap: var(--space-lg);
	}

	.nav-link {
		color: var(--color-text-muted);
		text-decoration: none;
		font-size: 0.875rem;
		font-weight: 500;
		transition: color var(--transition-fast);
		padding: var(--space-xs) var(--space-sm);
		border-radius: var(--radius-sm);
	}

	.nav-link:hover {
		color: var(--color-text);
		text-decoration: none;
		background: rgba(255, 255, 255, 0.05);
	}

	.nav-link:focus-visible {
		outline: 2px solid var(--color-primary);
		outline-offset: 2px;
	}

	.nav-divider {
		width: 1px;
		height: 16px;
		background: rgba(255, 255, 255, 0.2);
	}

	.nav-link-brand {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		color: var(--color-primary);
	}

	.brand-icon {
		font-size: 0.75rem;
	}

	/* Mobile Menu Button */
	.mobile-menu-btn {
		display: none;
		background: none;
		border: none;
		padding: var(--space-sm);
		cursor: pointer;
		border-radius: var(--radius-sm);
	}

	.mobile-menu-btn:hover {
		background: rgba(255, 255, 255, 0.05);
	}

	.mobile-menu-btn:focus-visible {
		outline: 2px solid var(--color-primary);
		outline-offset: 2px;
	}

	.hamburger {
		display: flex;
		flex-direction: column;
		gap: 4px;
		width: 20px;
	}

	.hamburger span {
		display: block;
		height: 2px;
		background: var(--color-text);
		border-radius: 1px;
		transition: all var(--transition-fast);
	}

	.hamburger.open span:nth-child(1) {
		transform: rotate(45deg) translate(4px, 4px);
	}

	.hamburger.open span:nth-child(2) {
		opacity: 0;
	}

	.hamburger.open span:nth-child(3) {
		transform: rotate(-45deg) translate(4px, -4px);
	}

	/* Mobile Nav */
	.mobile-nav {
		display: none;
		flex-direction: column;
		padding: var(--space-md);
		background: var(--color-bg-card);
		border-top: 1px solid rgba(255, 255, 255, 0.1);
	}

	.mobile-nav-link {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-md);
		color: var(--color-text);
		text-decoration: none;
		font-weight: 500;
		border-radius: var(--radius-md);
		transition: background var(--transition-fast);
	}

	.mobile-nav-link:hover {
		background: rgba(255, 255, 255, 0.05);
		text-decoration: none;
	}

	.mobile-nav-brand {
		color: var(--color-primary);
	}

	.mobile-nav-divider {
		border: none;
		border-top: 1px solid rgba(255, 255, 255, 0.1);
		margin: var(--space-sm) 0;
	}

	/* ============================================
	   Main Content
	   ============================================ */

	main {
		flex: 1;
	}

	/* Error Boundary */
	.error-boundary {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 400px;
		padding: var(--space-2xl);
	}

	.error-content {
		text-align: center;
		max-width: 400px;
	}

	.error-icon {
		font-size: 3rem;
		display: block;
		margin-bottom: var(--space-lg);
	}

	.error-content h2 {
		margin-bottom: var(--space-sm);
	}

	.error-content p {
		margin-bottom: var(--space-lg);
	}

	/* ============================================
	   Footer
	   ============================================ */

	.app-footer {
		background: var(--color-bg-elevated);
		border-top: 1px solid rgba(255, 255, 255, 0.1);
		padding: var(--space-xl) 0 var(--space-lg);
		margin-top: var(--space-2xl);
	}

	.footer-content {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: var(--space-xl);
		margin-bottom: var(--space-xl);
	}

	.footer-brand {
		display: flex;
		align-items: flex-start;
		gap: var(--space-md);
	}

	.footer-logo-img {
		height: 112px;
		width: auto;
	}

	.footer-logo-text {
		font-size: 2rem;
		font-weight: 700;
		color: var(--color-primary);
	}

	.footer-title {
		font-weight: 600;
		font-size: 1rem;
		margin-bottom: var(--space-xs);
	}

	.footer-tagline {
		color: var(--color-text-muted);
		font-size: 0.8125rem;
	}

	.footer-links {
		display: flex;
		gap: var(--space-2xl);
	}

	.footer-section h4 {
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-muted);
		margin-bottom: var(--space-sm);
	}

	.footer-section a {
		display: block;
		color: var(--color-text);
		text-decoration: none;
		font-size: 0.875rem;
		padding: var(--space-xs) 0;
		transition: color var(--transition-fast);
	}

	.footer-section a:hover {
		color: var(--color-primary);
		text-decoration: none;
	}

	.footer-bottom {
		padding-top: var(--space-lg);
		border-top: 1px solid rgba(255, 255, 255, 0.1);
		display: flex;
		justify-content: space-between;
		align-items: center;
		font-size: 0.8125rem;
		color: var(--color-text-muted);
	}

	.footer-bottom a {
		color: var(--color-primary);
	}

	.footer-version {
		font-family: var(--font-mono);
		font-size: 0.75rem;
	}

	/* ============================================
	   Responsive
	   ============================================ */

	@media (max-width: 768px) {
		.desktop-nav {
			display: none;
		}

		.mobile-menu-btn {
			display: block;
		}

		.mobile-nav {
			display: flex;
		}

		.footer-content {
			flex-direction: column;
			gap: var(--space-xl);
		}

		.footer-links {
			width: 100%;
			justify-content: space-between;
		}

		.footer-bottom {
			flex-direction: column;
			gap: var(--space-sm);
			text-align: center;
		}
	}

	@media (max-width: 480px) {
		.footer-links {
			flex-direction: column;
			gap: var(--space-lg);
		}
	}
</style>
