<script lang="ts">
	import '../app.css';
	import { page } from '$app/stores';

	interface Props {
		children: import('svelte').Snippet;
	}

	let { children }: Props = $props();
	let mobileMenuOpen = $state(false);

	// Derive current path for nav active states
	const currentPath = $derived($page.url.pathname);

	// Check if a nav link is active (matches current path or is a parent)
	function isActive(href: string): boolean {
		if (href === '/') return currentPath === '/';
		return currentPath === href || currentPath.startsWith(href + '/');
	}
</script>

<div class="app">
	<!-- Skip to main content for keyboard users -->
	<a href="#main-content" class="skip-link">Skip to main content</a>

	<header class="app-header">
		<nav class="container flex items-center justify-between">
			<a href="/" class="logo" aria-label="VCP Demo Home">
				<span class="logo-icon" aria-hidden="true"><i class="fa-solid fa-shield-halved"></i></span>
				<span class="logo-text">VCP</span>
				<span class="logo-badge">Demo</span>
			</a>

			<!-- Desktop Nav -->
			<div class="nav-links desktop-nav" role="navigation" aria-label="Main navigation">
				<a href="/about" class="nav-link" class:active={isActive('/about')}>About</a>
				<a href="/demos" class="nav-link" class:active={isActive('/demos') || isActive('/professional') || isActive('/personal') || isActive('/sharing') || isActive('/coordination') || isActive('/self-modeling') || isActive('/adaptation') || isActive('/psychosecurity')}>Demos</a>
				<a href="/docs" class="nav-link" class:active={isActive('/docs')}>Docs</a>
				<a href="/playground" class="nav-link" class:active={isActive('/playground')}>Playground</a>
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
				<a href="/about" class="mobile-nav-link" class:active={isActive('/about')} onclick={() => (mobileMenuOpen = false)}>
					About VCP
				</a>
				<a href="/demos" class="mobile-nav-link" class:active={isActive('/demos')} onclick={() => (mobileMenuOpen = false)}>
					Interactive Demos
				</a>
				<a href="/docs" class="mobile-nav-link" class:active={isActive('/docs')} onclick={() => (mobileMenuOpen = false)}>
					Documentation
				</a>
				<a href="/playground" class="mobile-nav-link" class:active={isActive('/playground')} onclick={() => (mobileMenuOpen = false)}>
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
		{@render children()}
	</main>

	<footer class="app-footer">
		<div class="container">
			<div class="footer-content">
				<div class="footer-brand">
					<span class="footer-logo" aria-hidden="true"><i class="fa-solid fa-shield-halved"></i></span>
					<div>
						<p class="footer-title">Value Context Protocol</p>
						<p class="footer-tagline">Your context stays yours. Private reasons stay private.</p>
					</div>
				</div>

				<div class="footer-links">
					<div class="footer-section">
						<h4>Explore</h4>
						<a href="/about">About VCP</a>
						<a href="/demos">All Demos</a>
						<a href="/playground">Playground</a>
						<a href="/docs">Documentation</a>
					</div>
					<div class="footer-section">
						<h4>Featured Demos</h4>
						<a href="/professional">Professional</a>
						<a href="/personal">Personal Growth</a>
						<a href="/demos/self-modeling/interiora">Interiora</a>
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
					Built with <span aria-label="love">♡</span> by
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

	.logo-icon {
		font-size: 1.5rem;
	}

	.logo-text {
		font-weight: 700;
		font-size: 1.25rem;
		background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
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
		gap: 5px;
		width: 22px;
		height: 18px;
		position: relative;
	}

	.hamburger span {
		display: block;
		height: 2px;
		width: 100%;
		background: var(--color-text);
		border-radius: 2px;
		transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
		position: absolute;
		left: 0;
	}

	.hamburger span:nth-child(1) {
		top: 0;
	}

	.hamburger span:nth-child(2) {
		top: 8px;
	}

	.hamburger span:nth-child(3) {
		top: 16px;
	}

	.hamburger.open span:nth-child(1) {
		transform: rotate(45deg);
		top: 8px;
	}

	.hamburger.open span:nth-child(2) {
		opacity: 0;
		transform: translateX(-10px);
	}

	.hamburger.open span:nth-child(3) {
		transform: rotate(-45deg);
		top: 8px;
	}

	/* Mobile Nav */
	.mobile-nav {
		display: none;
		flex-direction: column;
		padding: var(--space-md);
		background: var(--color-bg-card);
		border-top: 1px solid rgba(255, 255, 255, 0.1);
		animation: slideDown 0.3s ease;
	}

	@keyframes slideDown {
		from {
			opacity: 0;
			transform: translateY(-10px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
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

	.footer-logo {
		font-size: 2rem;
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
			display: grid;
			grid-template-columns: repeat(3, 1fr);
			gap: var(--space-lg);
		}

		.footer-bottom {
			flex-direction: column;
			gap: var(--space-sm);
			text-align: center;
		}

		.footer-brand {
			text-align: center;
			flex-direction: column;
		}
	}

	@media (max-width: 480px) {
		.footer-links {
			grid-template-columns: 1fr;
			text-align: center;
		}

		.footer-section a {
			display: inline-block;
		}
	}
</style>
