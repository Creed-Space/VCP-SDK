<script lang="ts">
	/**
	 * Documentation Hub - Index of all technical documentation
	 */
</script>

<svelte:head>
	<title>Documentation - VCP</title>
	<meta name="description" content="Technical documentation for the Value Context Protocol." />
</svelte:head>

<div class="container">
	<section class="hero">
		<h1>Documentation</h1>
		<p class="hero-subtitle">
			Technical guides, API reference, and specifications for implementing VCP.
		</p>
	</section>

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
			<p>Understand the fundamental concepts: context, constitutions, privacy filtering.</p>
			<span class="doc-time">10 min read</span>
		</a>

		<!-- CSM-1 Specification -->
		<a href="/docs/csm1-specification" class="doc-card">
			<span class="doc-icon"><i class="fa-solid fa-pen" aria-hidden="true"></i></span>
			<h3>CSM-1 Specification</h3>
			<p>Complete specification for the Compact State Message format.</p>
			<span class="doc-time">15 min read</span>
		</a>

		<!-- API Reference -->
		<a href="/docs/api-reference" class="doc-card">
			<span class="doc-icon"><i class="fa-solid fa-book" aria-hidden="true"></i></span>
			<h3>API Reference</h3>
			<p>Full API documentation for all VCP library functions.</p>
			<span class="doc-time">Reference</span>
		</a>

		<!-- Constitutional AI (Coming Soon) -->
		<div class="doc-card doc-card-coming-soon">
			<span class="doc-icon"><i class="fa-solid fa-scale-balanced" aria-hidden="true"></i></span>
			<h3>Constitutional AI</h3>
			<p>How VCP integrates with constitution-based AI alignment.</p>
			<span class="doc-time coming-soon-badge">Coming Soon</span>
		</div>

		<!-- Privacy Architecture (Coming Soon) -->
		<div class="doc-card doc-card-coming-soon">
			<span class="doc-icon"><i class="fa-solid fa-lock" aria-hidden="true"></i></span>
			<h3>Privacy Architecture</h3>
			<p>Deep dive into privacy filtering, consent, and audit trails.</p>
			<span class="doc-time coming-soon-badge">Coming Soon</span>
		</div>

		<!-- Interiora Specification (Coming Soon) -->
		<div class="doc-card doc-card-coming-soon">
			<span class="doc-icon"><i class="fa-solid fa-brain" aria-hidden="true"></i></span>
			<h3>Interiora Specification</h3>
			<p>VCP 2.5 self-modeling framework for AI embodied states.</p>
			<span class="doc-time coming-soon-badge">Coming Soon</span>
		</div>

		<!-- Multi-Agent Patterns (Coming Soon) -->
		<div class="doc-card doc-card-coming-soon">
			<span class="doc-icon"><i class="fa-solid fa-robot" aria-hidden="true"></i></span>
			<h3>Multi-Agent Patterns</h3>
			<p>Implementing VCP in multi-agent coordination scenarios.</p>
			<span class="doc-time coming-soon-badge">Coming Soon</span>
		</div>
	</div>

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
X:<i class="fa-solid fa-volume-xmark" aria-hidden="true"></i>:<i class="fa-solid fa-coins" aria-hidden="true"></i>low:<i class="fa-solid fa-bolt" aria-hidden="true"></i>var
F:time_limited|noise_restricted
S:<i class="fa-solid fa-lock" aria-hidden="true"></i>work|<i class="fa-solid fa-lock" aria-hidden="true"></i>housing</code></pre>
			</div>

			<div class="quick-ref-card">
				<h4>Emoji Shortcodes</h4>
				<div class="emoji-table">
					<div class="emoji-row"><span><i class="fa-solid fa-volume-xmark" aria-hidden="true"></i></span> quiet mode</div>
					<div class="emoji-row"><span><i class="fa-solid fa-coins" aria-hidden="true"></i></span> budget tier</div>
					<div class="emoji-row"><span><i class="fa-solid fa-bolt" aria-hidden="true"></i></span> energy variable</div>
					<div class="emoji-row"><span>⏰</span> time limited</div>
					<div class="emoji-row"><span><i class="fa-solid fa-lock" aria-hidden="true"></i></span> private (hidden)</div>
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
</div>

<style>
	.hero {
		text-align: center;
		padding: var(--space-2xl) 0;
	}

	.hero h1 {
		font-size: 2.5rem;
		margin-bottom: var(--space-md);
	}

	.hero-subtitle {
		color: var(--color-text-muted);
		font-size: 1.25rem;
		max-width: 500px;
		margin: 0 auto;
	}

	.docs-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: var(--space-lg);
		margin-bottom: var(--space-2xl);
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

	.doc-card-coming-soon {
		opacity: 0.6;
		cursor: default;
	}

	.doc-card-coming-soon:hover {
		border-color: rgba(255, 255, 255, 0.1);
		transform: none;
	}

	.coming-soon-badge {
		background: var(--color-warning-muted);
		color: var(--color-warning);
		padding: 2px 8px;
		border-radius: var(--radius-sm);
		font-weight: 500;
	}

	.doc-icon {
		font-size: 2rem;
		display: block;
		margin-bottom: var(--space-md);
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

	@media (max-width: 768px) {
		.hero h1 {
			font-size: 1.75rem;
		}
	}
</style>
