<script lang="ts">
	/**
	 * Demos Hub - Index of all interactive demonstrations
	 * Organized by VCP capability
	 */
	import { Breadcrumb } from '$lib/components/shared';

	const breadcrumbItems = [
		{ label: 'Interactive Demos', icon: 'fa-play-circle' }
	];
</script>

<svelte:head>
	<title>Interactive Demos - VCP</title>
	<meta
		name="description"
		content="Explore interactive demonstrations of the Value Context Protocol organized by capability."
	/>
</svelte:head>

<div class="container">
	<Breadcrumb items={breadcrumbItems} />

	<section class="page-hero">
		<h1>Interactive Demos</h1>
		<p class="page-hero-subtitle">
			See VCP in action. Each demo shows a different aspect of privacy-preserving context sharing.
		</p>
		<div class="prosaic-mention">
			<span class="prosaic-dims">⚡ 💊 🧩 💭</span>
			<span>Many demos now show <strong>prosaic dimensions</strong> — how urgency, health, cognitive load, and affect shape AI adaptation.</span>
		</div>
	</section>

	<!-- Featured Demos -->
	<section class="featured-demos">
		<h2>Start Here</h2>
		<p class="section-intro">These two demos show the core VCP experience — real scenarios where privacy matters.</p>
		<div class="featured-grid">
			<a href="/professional" class="featured-card featured-professional">
				<div class="featured-badge"><span class="badge badge-success">Enterprise</span></div>
				<div class="featured-content">
					<span class="featured-icon"><i class="fa-solid fa-briefcase" aria-hidden="true"></i></span>
					<div>
						<h3>Campion's Corporate Training</h3>
						<p>HR sees career goals, not health circumstances. Dual profiles protect personal boundaries at work.</p>
					</div>
				</div>
				<span class="featured-cta">Start demo <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></span>
			</a>

			<a href="/personal" class="featured-card featured-personal">
				<div class="featured-badge"><span class="badge badge-primary">Consumer</span></div>
				<div class="featured-content">
					<span class="featured-icon"><i class="fa-solid fa-guitar" aria-hidden="true"></i></span>
					<div>
						<h3>Gentian's Guitar Journey</h3>
						<p>Four apps adapt to his constraints. None know about thin walls, shift work, or tight budget.</p>
					</div>
				</div>
				<span class="featured-cta">Start demo <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></span>
			</a>
		</div>
	</section>

	<!-- Category Cards -->
	<section class="category-overview">
		<h2>Explore by Capability</h2>
		<div class="category-grid">
			<div class="category-card category-sharing">
				<span class="category-icon"><i class="fa-solid fa-share-nodes" aria-hidden="true"></i></span>
				<h3>Sharing</h3>
				<p>Privacy-preserving context sharing between humans and platforms</p>
				<div class="category-demos">
					<a href="/professional">Professional</a>
					<a href="/personal">Personal</a>
				</div>
			</div>

			<div class="category-card category-coordination">
				<span class="category-icon"><i class="fa-solid fa-handshake" aria-hidden="true"></i></span>
				<h3>Coordination</h3>
				<p>AI agents negotiating with mutual VCP context</p>
				<div class="category-demos">
					<a href="/demos/multi-agent/auction">Auction</a>
					<a href="/demos/multi-agent/negotiation">Negotiation</a>
					<a href="/demos/multi-agent/policy-design">Policy</a>
				</div>
			</div>

			<div class="category-card category-self-modeling">
				<span class="category-icon"><i class="fa-solid fa-brain" aria-hidden="true"></i></span>
				<h3>Self-Modeling</h3>
				<p>AI systems encoding and communicating their own states</p>
				<div class="category-demos">
					<a href="/demos/self-modeling/interiora">Interiora</a>
					<a href="/demos/self-modeling/belief-calibration">Beliefs</a>
					<a href="/demos/self-modeling/reality-grounding">Grounding</a>
				</div>
			</div>

			<div class="category-card category-adaptation">
				<span class="category-icon"><i class="fa-solid fa-wand-magic-sparkles" aria-hidden="true"></i></span>
				<h3>Adaptation</h3>
				<p>Context shaping personalized learning experiences</p>
				<div class="category-demos">
					<a href="/demos/learning/adaptive-paths">Learning Paths</a>
					<a href="/demos/learning/cognitive-load">Cognitive Load</a>
				</div>
			</div>

			<div class="category-card category-psychosecurity">
				<span class="category-icon"><i class="fa-solid fa-shield-heart" aria-hidden="true"></i></span>
				<h3>Psychosecurity</h3>
				<p>Context protecting against manipulation and harm</p>
				<div class="category-demos">
					<a href="/demos/safety/attention-protection">Attention</a>
					<a href="/demos/safety/mental-health">Mental Health</a>
				</div>
			</div>
		</div>
	</section>

	<!-- Tools -->
	<section class="tools-section">
		<h2>Tools</h2>
		<div class="tools-grid">
			<a href="/playground" class="tool-card">
				<span class="tool-icon"><i class="fa-solid fa-sliders" aria-hidden="true"></i></span>
				<div>
					<h3>Playground</h3>
					<p>Build and inspect VCP tokens interactively</p>
				</div>
			</a>
			<a href="/docs" class="tool-card">
				<span class="tool-icon"><i class="fa-solid fa-book" aria-hidden="true"></i></span>
				<div>
					<h3>Documentation</h3>
					<p>Technical guides and API reference</p>
				</div>
			</a>
		</div>
	</section>
</div>

<style>
	/* Prosaic mention */
	.prosaic-mention {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: var(--space-md);
		margin-top: var(--space-md);
		padding: var(--space-sm) var(--space-lg);
		background: rgba(16, 185, 129, 0.1);
		border: 1px solid rgba(16, 185, 129, 0.3);
		border-radius: var(--radius-md);
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		flex-wrap: wrap;
	}

	.prosaic-dims {
		font-size: 1.125rem;
	}

	/* Section intro text */
	.section-intro {
		color: var(--color-text-muted);
		margin-bottom: var(--space-lg);
	}

	/* Featured Demos */
	.featured-demos {
		margin-bottom: var(--space-2xl);
	}

	.featured-demos h2 {
		margin-bottom: var(--space-sm);
	}

	.featured-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: var(--space-lg);
	}

	.featured-card {
		display: flex;
		flex-direction: column;
		padding: var(--space-xl);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		border: 2px solid rgba(255, 255, 255, 0.1);
		text-decoration: none;
		color: var(--color-text);
		transition: all var(--transition-normal);
	}

	.featured-professional {
		border-color: var(--color-professional);
		background: linear-gradient(135deg, var(--color-bg-card), rgba(5, 150, 105, 0.1));
	}

	.featured-personal {
		border-color: var(--color-primary);
		background: linear-gradient(135deg, var(--color-bg-card), rgba(99, 102, 241, 0.1));
	}

	.featured-card:hover {
		transform: translateY(-4px);
		box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
		text-decoration: none;
	}

	.featured-badge {
		margin-bottom: var(--space-md);
	}

	.featured-content {
		display: flex;
		gap: var(--space-lg);
		flex: 1;
		margin-bottom: var(--space-lg);
	}

	.featured-icon {
		font-size: 2.5rem;
		flex-shrink: 0;
	}

	.featured-professional .featured-icon {
		color: var(--color-professional);
	}

	.featured-personal .featured-icon {
		color: var(--color-primary);
	}

	.featured-content h3 {
		font-size: var(--text-xl);
		margin-bottom: var(--space-sm);
	}

	.featured-content p {
		color: var(--color-text-muted);
		font-size: var(--text-sm);
		line-height: var(--leading-relaxed);
	}

	.featured-cta {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		color: var(--color-primary);
		font-weight: 500;
		font-size: var(--text-sm);
	}

	/* Category Overview */
	.category-overview {
		margin-bottom: var(--space-2xl);
	}

	.category-overview h2 {
		margin-bottom: var(--space-lg);
	}

	.category-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
		gap: var(--space-md);
	}

	.category-card {
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-top: 3px solid var(--color-primary);
	}

	/* Category-specific colors */
	.category-sharing { border-top-color: var(--color-success); }
	.category-coordination { border-top-color: #3b82f6; }
	.category-self-modeling { border-top-color: #a855f7; }
	.category-adaptation { border-top-color: var(--color-warning); }
	.category-psychosecurity { border-top-color: var(--color-danger); }

	.category-sharing .category-icon { color: var(--color-success); }
	.category-coordination .category-icon { color: #3b82f6; }
	.category-self-modeling .category-icon { color: #a855f7; }
	.category-adaptation .category-icon { color: var(--color-warning); }
	.category-psychosecurity .category-icon { color: var(--color-danger); }

	.category-icon {
		font-size: 1.5rem;
		margin-bottom: var(--space-md);
		display: block;
	}

	.category-card h3 {
		font-size: var(--text-lg);
		margin-bottom: var(--space-xs);
	}

	.category-card p {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		margin: 0 0 var(--space-md) 0;
		line-height: var(--leading-relaxed);
	}

	.category-demos {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-xs);
	}

	.category-demos a {
		font-size: var(--text-xs);
		padding: var(--space-xs) var(--space-sm);
		background: var(--color-bg);
		border-radius: var(--radius-sm);
		color: var(--color-text);
		text-decoration: none;
		transition: all var(--transition-fast);
	}

	.category-demos a:hover {
		background: var(--color-primary-muted);
		color: var(--color-primary);
		text-decoration: none;
	}

	/* Tools Section */
	.tools-section {
		margin-bottom: var(--space-2xl);
	}

	.tools-section h2 {
		margin-bottom: var(--space-lg);
	}

	.tools-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: var(--space-md);
	}

	.tool-card {
		display: flex;
		align-items: center;
		gap: var(--space-lg);
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
		text-decoration: none;
		color: var(--color-text);
		transition: all var(--transition-fast);
	}

	.tool-card:hover {
		border-color: var(--color-primary);
		text-decoration: none;
	}

	.tool-icon {
		font-size: 2rem;
		color: var(--color-primary);
	}

	.tool-card h3 {
		font-size: var(--text-base);
		margin-bottom: var(--space-xs);
	}

	.tool-card p {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	@media (max-width: 768px) {
		.featured-grid {
			grid-template-columns: 1fr;
		}

		.tools-grid {
			grid-template-columns: 1fr;
		}
	}

	@media (max-width: 480px) {
		.featured-content {
			flex-direction: column;
			gap: var(--space-md);
		}
	}
</style>
