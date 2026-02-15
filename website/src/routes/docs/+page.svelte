<script lang="ts">
	/**
	 * Documentation Hub - Index of all technical documentation
	 */
	import { Breadcrumb } from '$lib/components/shared';

	const breadcrumbItems = [
		{ label: 'Documentation', icon: 'fa-book' }
	];
</script>

<svelte:head>
	<title>Documentation - VCP</title>
	<meta name="description" content="Technical documentation for the Value Context Protocol." />
</svelte:head>

<div class="container">
	<Breadcrumb items={breadcrumbItems} />

	<section class="page-hero">
		<h1>Documentation</h1>
		<p class="page-hero-subtitle">
			Technical guides, API reference, and specifications for implementing VCP.
		</p>
	</section>

	<!-- Available Documentation -->
	<section class="docs-section">
		<h2>Available Guides</h2>
		<div class="docs-grid">
			<!-- Getting Started -->
			<a href="/docs/getting-started" class="doc-card">
				<span class="doc-icon"><i class="fa-solid fa-rocket" aria-hidden="true"></i></span>
				<h3>Getting Started</h3>
				<p>Quick start guide for implementing VCP in your application.</p>
				<span class="doc-time">5 min read</span>
			</a>

			<!-- Core Concepts -->
			<a href="/docs/concepts" class="doc-card">
				<span class="doc-icon"><i class="fa-solid fa-lightbulb" aria-hidden="true"></i></span>
				<h3>Core Concepts</h3>
				<p>Understand the fundamental concepts: context, values profiles, privacy filtering.</p>
				<span class="doc-time">10 min read</span>
			</a>

			<!-- Understanding Personas -->
			<a href="/docs/personas" class="doc-card doc-card-featured">
				<span class="doc-icon"><i class="fa-solid fa-masks-theater" aria-hidden="true"></i></span>
				<h3>Understanding Personas</h3>
				<p>Learn about VCP's 6 personas: Muse, Ambassador, Godparent, Sentinel, Anchor, and Nanny.</p>
				<span class="doc-time">8 min read</span>
			</a>

			<!-- CSM-1 Specification -->
			<a href="/docs/csm1-specification" class="doc-card">
				<span class="doc-icon"><i class="fa-solid fa-file-code" aria-hidden="true"></i></span>
				<h3>Token Format</h3>
				<p>Complete specification for the CSM-1 Compact State Message format.</p>
				<span class="doc-time">15 min read</span>
			</a>

			<!-- Security Model -->
			<a href="/docs/security" class="doc-card">
				<span class="doc-icon"><i class="fa-solid fa-shield-halved" aria-hidden="true"></i></span>
				<h3>Security Model</h3>
				<p>How VCP protects your data: encryption, transmission, and trust boundaries.</p>
				<span class="doc-time">10 min read</span>
			</a>

			<!-- API Reference -->
			<a href="/docs/api-reference" class="doc-card">
				<span class="doc-icon"><i class="fa-solid fa-book" aria-hidden="true"></i></span>
				<h3>API Reference</h3>
				<p>Full API documentation for all VCP library functions.</p>
				<span class="doc-time">Reference</span>
			</a>
		</div>
	</section>

	<!-- Quick Reference -->
	<section class="quick-ref">
		<h2>Quick Reference</h2>
		<div class="quick-ref-grid">
			<div class="quick-ref-card">
				<h4>CSM-1 Token Format</h4>
				<pre class="code-block"><code>VCP:1.0:profile-id
C:constitution@version
P:persona:adherence
G:goal:experience:style
X:🔇:💰low:⚡var
F:time_limited|noise_restricted
S:🔒work|🔒housing</code></pre>
			</div>

			<div class="quick-ref-card">
				<h4>Emoji Shortcodes</h4>
				<div class="emoji-table">
					<div class="emoji-row"><span>🔇</span> quiet mode</div>
					<div class="emoji-row"><span>💰</span> budget tier</div>
					<div class="emoji-row"><span>⚡</span> energy variable</div>
					<div class="emoji-row"><span>⏰</span> time limited</div>
					<div class="emoji-row"><span>🔒</span> private (hidden)</div>
				</div>
			</div>

			<div class="quick-ref-card">
				<h4>Privacy Levels</h4>
				<div class="privacy-levels">
					<div class="level level-public">
						<span class="level-badge">Public</span>
						<span>Always shared</span>
					</div>
					<div class="level level-consent">
						<span class="level-badge">Consent</span>
						<span>Requires permission</span>
					</div>
					<div class="level level-private">
						<span class="level-badge">Private</span>
						<span>Never transmitted</span>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- Roadmap -->
	<section class="roadmap-section">
		<h2>Coming Soon</h2>
		<p class="roadmap-description">These guides are in development and will be available soon.</p>
		<div class="roadmap-grid">
			<div class="roadmap-item">
				<i class="fa-solid fa-scale-balanced" aria-hidden="true"></i>
				<span>Constitutional AI</span>
			</div>
			<div class="roadmap-item">
				<i class="fa-solid fa-shield-halved" aria-hidden="true"></i>
				<span>Privacy Architecture</span>
			</div>
			<div class="roadmap-item">
				<i class="fa-solid fa-brain" aria-hidden="true"></i>
				<span>Interiora Specification</span>
			</div>
			<div class="roadmap-item">
				<i class="fa-solid fa-robot" aria-hidden="true"></i>
				<span>Multi-Agent Patterns</span>
			</div>
		</div>
	</section>
</div>

<style>
	.docs-section {
		margin-bottom: var(--space-2xl);
	}

	.docs-section h2 {
		margin-bottom: var(--space-lg);
	}

	.docs-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: var(--space-lg);
	}

	.doc-card {
		display: block;
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		padding: var(--space-xl);
		border: 1px solid rgba(255, 255, 255, 0.1);
		text-decoration: none;
		color: var(--color-text);
		transition: all var(--transition-normal);
	}

	.doc-card:hover {
		border-color: var(--color-primary);
		transform: translateY(-2px);
		text-decoration: none;
	}

	.doc-icon {
		font-size: 2rem;
		display: block;
		margin-bottom: var(--space-md);
		color: var(--color-primary);
	}

	.doc-card h3 {
		margin-bottom: var(--space-sm);
	}

	.doc-card p {
		color: var(--color-text-muted);
		font-size: 0.875rem;
		line-height: 1.5;
		margin-bottom: var(--space-md);
	}

	.doc-time {
		font-size: 0.75rem;
		color: var(--color-text-subtle);
	}

	.doc-card-featured {
		border-color: var(--color-primary);
		background: linear-gradient(135deg, var(--color-bg-card), rgba(99, 102, 241, 0.1));
	}

	/* Quick Reference */
	.quick-ref {
		margin-bottom: var(--space-2xl);
	}

	.quick-ref h2 {
		margin-bottom: var(--space-lg);
	}

	.quick-ref-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
		gap: var(--space-lg);
	}

	.quick-ref-card {
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		padding: var(--space-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.quick-ref-card h4 {
		margin-bottom: var(--space-md);
		font-size: 0.9375rem;
	}

	.code-block {
		background: var(--color-bg);
		border-radius: var(--radius-sm);
		padding: var(--space-md);
		overflow-x: auto;
		font-family: var(--font-mono);
		font-size: 0.75rem;
		line-height: 1.6;
	}

	.emoji-table {
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
	}

	.emoji-row {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-size: 0.875rem;
	}

	.emoji-row span:first-child {
		font-size: 1.25rem;
		width: 28px;
	}

	.privacy-levels {
		display: flex;
		flex-direction: column;
		gap: var(--space-sm);
	}

	.level {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-size: 0.875rem;
	}

	.level-badge {
		font-size: 0.6875rem;
		padding: 2px 8px;
		border-radius: var(--radius-sm);
		font-weight: 500;
	}

	.level-public .level-badge {
		background: var(--color-success-muted);
		color: var(--color-success);
	}

	.level-consent .level-badge {
		background: var(--color-warning-muted);
		color: var(--color-warning);
	}

	.level-private .level-badge {
		background: var(--color-danger-muted);
		color: var(--color-danger);
	}

	/* Roadmap Section */
	.roadmap-section {
		margin-bottom: var(--space-2xl);
	}

	.roadmap-section h2 {
		margin-bottom: var(--space-sm);
	}

	.roadmap-description {
		color: var(--color-text-muted);
		font-size: 0.875rem;
		margin-bottom: var(--space-lg);
	}

	.roadmap-grid {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-md);
	}

	.roadmap-item {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-sm) var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	.roadmap-item i {
		color: var(--color-text-subtle);
	}

	@media (max-width: 768px) {
		.roadmap-grid {
			flex-direction: column;
		}
	}
</style>
