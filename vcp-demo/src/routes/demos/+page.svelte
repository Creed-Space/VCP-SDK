<script lang="ts">
	/**
	 * Demos Hub - Index of all interactive demonstrations
	 * Organized by VCP capability
	 */
</script>

<svelte:head>
	<title>Interactive Demos - VCP</title>
	<meta
		name="description"
		content="Explore interactive demonstrations of the Value Context Protocol organized by capability."
	/>
</svelte:head>

<div class="container">
	<section class="hero">
		<h1>Interactive Demos</h1>
		<p class="hero-subtitle">
			See VCP in action across five capability areas—from privacy-preserving sharing
			to AI self-modeling and psychosecurity.
		</p>
	</section>

	<!-- Category Cards -->
	<section class="category-overview">
		<div class="category-grid">
			<a href="/sharing" class="category-card">
				<span class="category-icon"><i class="fa-solid fa-share-nodes" aria-hidden="true"></i></span>
				<h2>Sharing</h2>
				<p>Privacy-preserving context sharing between humans and platforms</p>
				<span class="category-count">2 demos</span>
			</a>

			<a href="/coordination" class="category-card">
				<span class="category-icon"><i class="fa-solid fa-handshake" aria-hidden="true"></i></span>
				<h2>Coordination</h2>
				<p>AI agents negotiating with mutual VCP context</p>
				<span class="category-count">3 demos</span>
			</a>

			<a href="/self-modeling" class="category-card">
				<span class="category-icon"><i class="fa-solid fa-brain" aria-hidden="true"></i></span>
				<h2>Self-Modeling</h2>
				<p>Entities encoding and communicating their own states</p>
				<span class="category-count">3 demos</span>
			</a>

			<a href="/adaptation" class="category-card">
				<span class="category-icon"><i class="fa-solid fa-wand-magic-sparkles" aria-hidden="true"></i></span>
				<h2>Adaptation</h2>
				<p>Context shaping personalized experiences</p>
				<span class="category-count">2 demos</span>
			</a>

			<a href="/psychosecurity" class="category-card">
				<span class="category-icon"><i class="fa-solid fa-shield-heart" aria-hidden="true"></i></span>
				<h2>Psychosecurity</h2>
				<p>Context protecting against manipulation</p>
				<span class="category-count">2 demos</span>
			</a>
		</div>
	</section>

	<!-- All Demos List -->
	<section class="all-demos">
		<h2>All Demos</h2>

		<div class="demo-list">
			<!-- Sharing -->
			<div class="demo-group">
				<h3><i class="fa-solid fa-share-nodes" aria-hidden="true"></i> Sharing</h3>
				<div class="demo-row">
					<a href="/professional" class="demo-link">
						<span class="demo-icon"><i class="fa-solid fa-briefcase" aria-hidden="true"></i></span>
						<span class="demo-name">Professional Development</span>
						<span class="demo-badge live">Live</span>
					</a>
					<a href="/personal" class="demo-link">
						<span class="demo-icon"><i class="fa-solid fa-guitar" aria-hidden="true"></i></span>
						<span class="demo-name">Personal Growth</span>
						<span class="demo-badge live">Live</span>
					</a>
				</div>
			</div>

			<!-- Coordination -->
			<div class="demo-group">
				<h3><i class="fa-solid fa-handshake" aria-hidden="true"></i> Coordination</h3>
				<div class="demo-row">
					<a href="/demos/multi-agent/auction" class="demo-link">
						<span class="demo-icon"><i class="fa-solid fa-gavel" aria-hidden="true"></i></span>
						<span class="demo-name">Auction</span>
						<span class="demo-badge live">Live</span>
					</a>
					<a href="/demos/multi-agent/negotiation" class="demo-link">
						<span class="demo-icon"><i class="fa-solid fa-comments" aria-hidden="true"></i></span>
						<span class="demo-name">Negotiation</span>
						<span class="demo-badge live">Live</span>
					</a>
					<a href="/demos/multi-agent/policy-design" class="demo-link">
						<span class="demo-icon"><i class="fa-solid fa-landmark" aria-hidden="true"></i></span>
						<span class="demo-name">Policy Design</span>
						<span class="demo-badge live">Live</span>
					</a>
				</div>
			</div>

			<!-- Self-Modeling -->
			<div class="demo-group">
				<h3><i class="fa-solid fa-brain" aria-hidden="true"></i> Self-Modeling</h3>
				<div class="demo-row">
					<a href="/demos/self-modeling/interiora" class="demo-link">
						<span class="demo-icon"><i class="fa-solid fa-sliders" aria-hidden="true"></i></span>
						<span class="demo-name">Interiora Explorer</span>
						<span class="demo-badge live">Live</span>
					</a>
					<a href="/demos/self-modeling/belief-calibration" class="demo-link">
						<span class="demo-icon"><i class="fa-solid fa-chart-simple" aria-hidden="true"></i></span>
						<span class="demo-name">Belief Calibration</span>
						<span class="demo-badge live">Live</span>
					</a>
					<a href="/demos/self-modeling/reality-grounding" class="demo-link">
						<span class="demo-icon"><i class="fa-solid fa-link" aria-hidden="true"></i></span>
						<span class="demo-name">Reality Grounding</span>
						<span class="demo-badge live">Live</span>
					</a>
				</div>
			</div>

			<!-- Adaptation -->
			<div class="demo-group">
				<h3><i class="fa-solid fa-wand-magic-sparkles" aria-hidden="true"></i> Adaptation</h3>
				<div class="demo-row">
					<a href="/demos/learning/adaptive-paths" class="demo-link">
						<span class="demo-icon"><i class="fa-solid fa-graduation-cap" aria-hidden="true"></i></span>
						<span class="demo-name">Learning Paths</span>
						<span class="demo-badge live">Live</span>
					</a>
					<a href="/demos/learning/cognitive-load" class="demo-link">
						<span class="demo-icon"><i class="fa-solid fa-brain" aria-hidden="true"></i></span>
						<span class="demo-name">Cognitive Load</span>
						<span class="demo-badge live">Live</span>
					</a>
				</div>
			</div>

			<!-- Psychosecurity -->
			<div class="demo-group">
				<h3><i class="fa-solid fa-shield-heart" aria-hidden="true"></i> Psychosecurity</h3>
				<div class="demo-row">
					<a href="/demos/safety/attention-protection" class="demo-link">
						<span class="demo-icon"><i class="fa-solid fa-bell-slash" aria-hidden="true"></i></span>
						<span class="demo-name">Attention Protection</span>
						<span class="demo-badge live">Live</span>
					</a>
					<a href="/demos/safety/mental-health" class="demo-link">
						<span class="demo-icon" style="color: var(--color-success)"><i class="fa-solid fa-hand-holding-heart" aria-hidden="true"></i></span>
						<span class="demo-name">Mental Health Context</span>
						<span class="demo-badge live">Live</span>
					</a>
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
		max-width: 700px;
		margin: 0 auto;
	}

	/* Category Overview */
	.category-overview {
		margin-bottom: var(--space-2xl);
	}

	.category-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: var(--space-md);
	}

	.category-card {
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		padding: var(--space-xl);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
		text-decoration: none;
		color: var(--color-text);
		transition: all var(--transition-normal);
	}

	.category-card:hover {
		border-color: var(--color-primary);
		transform: translateY(-2px);
		box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
		text-decoration: none;
	}

	.category-icon {
		font-size: 2rem;
		margin-bottom: var(--space-md);
		color: var(--color-primary);
	}

	.category-card h2 {
		font-size: 1.125rem;
		margin-bottom: var(--space-xs);
	}

	.category-card p {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		margin: 0 0 var(--space-md) 0;
		line-height: 1.4;
	}

	.category-count {
		font-size: 0.6875rem;
		padding: 2px 8px;
		background: var(--color-primary-muted);
		color: var(--color-primary);
		border-radius: var(--radius-sm);
	}

	/* All Demos Section */
	.all-demos {
		margin-bottom: var(--space-2xl);
	}

	.all-demos h2 {
		font-size: 1.25rem;
		margin-bottom: var(--space-lg);
	}

	.demo-list {
		display: flex;
		flex-direction: column;
		gap: var(--space-lg);
	}

	.demo-group {
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		padding: var(--space-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.demo-group h3 {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		margin-bottom: var(--space-md);
		display: flex;
		align-items: center;
		gap: var(--space-xs);
	}

	.demo-row {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-sm);
	}

	.demo-link {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-sm) var(--space-md);
		background: var(--color-bg);
		border-radius: var(--radius-md);
		text-decoration: none;
		color: var(--color-text);
		transition: all var(--transition-fast);
		border: 1px solid transparent;
	}

	.demo-link:hover {
		border-color: var(--color-primary);
		background: var(--color-primary-muted);
		text-decoration: none;
	}

	.demo-link .demo-icon {
		font-size: 1rem;
		color: var(--color-text-muted);
	}

	.demo-name {
		font-size: 0.875rem;
		font-weight: 500;
	}

	.demo-badge {
		font-size: 0.5625rem;
		padding: 1px 6px;
		border-radius: var(--radius-sm);
		text-transform: uppercase;
		font-weight: 500;
	}

	.demo-badge.live {
		background: var(--color-success-muted);
		color: var(--color-success);
	}

	@media (max-width: 768px) {
		.hero h1 {
			font-size: 1.75rem;
		}

		.category-grid {
			grid-template-columns: repeat(2, 1fr);
		}

		.demo-row {
			flex-direction: column;
		}
	}

	@media (max-width: 480px) {
		.category-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
