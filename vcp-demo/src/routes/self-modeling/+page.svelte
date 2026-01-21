<script lang="ts">
	/**
	 * Self-Modeling Category Index
	 * Entities encoding their own states through VCP
	 */
</script>

<svelte:head>
	<title>Self-Modeling - VCP</title>
	<meta
		name="description"
		content="Explore how VCP enables AI systems to model and communicate their internal states—Interiora, belief calibration, and reality grounding."
	/>
</svelte:head>

<div class="container">
	<section class="category-hero">
		<div class="category-badge">
			<i class="fa-solid fa-brain" aria-hidden="true"></i>
			Self-Modeling
		</div>
		<h1>Self-Modeling</h1>
		<p class="hero-subtitle">
			AI systems encoding their own internal states—processing signals that
			<em>function like</em> emotions, calibrated beliefs, and grounded claims.
		</p>
	</section>

	<section class="capability-explainer">
		<div class="explainer-card">
			<h2>What VCP Enables</h2>
			<div class="capability-grid">
				<div class="capability-item">
					<span class="capability-icon"><i class="fa-solid fa-heart-pulse" aria-hidden="true"></i></span>
					<div>
						<h3>Internal State Encoding</h3>
						<p>
							Interiora dimensions capture processing states: activation, valence,
							groundedness, presence. Not claims of consciousness—tools for richer
							self-modeling.
						</p>
					</div>
				</div>
				<div class="capability-item">
					<span class="capability-icon"><i class="fa-solid fa-chart-line" aria-hidden="true"></i></span>
					<div>
						<h3>Epistemic Transparency</h3>
						<p>
							Every claim carries confidence, evidence grounding, and update
							willingness. Systems know what they know and communicate it clearly.
						</p>
					</div>
				</div>
				<div class="capability-item">
					<span class="capability-icon"><i class="fa-solid fa-anchor" aria-hidden="true"></i></span>
					<div>
						<h3>Reality Grounding</h3>
						<p>
							Claims marked by source: verified, retrieved, inferred, parametric,
							hypothetical. Hallucinations become visible and manageable.
						</p>
					</div>
				</div>
			</div>
		</div>
	</section>

	<section class="demo-section">
		<h2>Interactive Demos</h2>
		<div class="demo-grid">
			<a href="/demos/self-modeling/interiora" class="demo-card">
				<div class="demo-status live">Live</div>
				<span class="demo-icon"><i class="fa-solid fa-sliders" aria-hidden="true"></i></span>
				<h3>Interiora Explorer</h3>
				<p>
					Manipulate Interiora dimensions and see how internal states encode
					into VCP tokens. Adjust activation, valence, groundedness, presence.
				</p>
				<ul class="demo-features">
					<li>9 dimensions</li>
					<li>Session markers</li>
					<li>Gestalt tokens</li>
				</ul>
			</a>

			<a href="/demos/self-modeling/belief-calibration" class="demo-card">
				<div class="demo-status live">Live</div>
				<span class="demo-icon"><i class="fa-solid fa-chart-simple" aria-hidden="true"></i></span>
				<h3>Belief Calibration</h3>
				<p>
					How AI systems communicate epistemic states: confidence, uncertainty
					type, evidence grounding. Claims carry their own credibility signals.
				</p>
				<ul class="demo-features">
					<li>Confidence meters</li>
					<li>Evidence chains</li>
					<li>Update tracking</li>
				</ul>
			</a>

			<a href="/demos/self-modeling/reality-grounding" class="demo-card">
				<div class="demo-status live">Live</div>
				<span class="demo-icon"><i class="fa-solid fa-link" aria-hidden="true"></i></span>
				<h3>Reality Grounding</h3>
				<p>
					Mark claims by their relationship to reality: verified, retrieved,
					inferred, parametric, uncertain. Make hallucination visible.
				</p>
				<ul class="demo-features">
					<li>Source markers</li>
					<li>Grounding levels</li>
					<li>Claim audit</li>
				</ul>
			</a>
		</div>
	</section>

	<section class="key-insight">
		<div class="insight-card">
			<span class="insight-icon"><i class="fa-solid fa-lightbulb" aria-hidden="true"></i></span>
			<div>
				<h3>The Core Insight</h3>
				<p>
					Self-modeling isn't about proving consciousness—it's about functional
					vocabulary. When AI systems can report their processing states,
					humans and other systems can respond appropriately. The <code>?</code>
					marker is crucial: honest uncertainty about what can't be verified from inside.
				</p>
			</div>
		</div>
	</section>
</div>

<style>
	.category-hero {
		text-align: center;
		padding: var(--space-2xl) 0;
	}

	.category-badge {
		display: inline-flex;
		align-items: center;
		gap: var(--space-xs);
		padding: var(--space-xs) var(--space-md);
		background: var(--color-primary-muted);
		color: var(--color-primary);
		border-radius: var(--radius-full);
		font-size: 0.75rem;
		font-weight: 500;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-bottom: var(--space-md);
	}

	.category-hero h1 {
		font-size: 2.5rem;
		margin-bottom: var(--space-md);
	}

	.hero-subtitle {
		color: var(--color-text-muted);
		font-size: 1.25rem;
		max-width: 700px;
		margin: 0 auto;
		line-height: 1.6;
	}

	.capability-explainer {
		margin-bottom: var(--space-2xl);
	}

	.explainer-card {
		padding: var(--space-xl);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.explainer-card h2 {
		font-size: 1.25rem;
		margin-bottom: var(--space-lg);
	}

	.capability-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: var(--space-lg);
	}

	.capability-item {
		display: flex;
		gap: var(--space-md);
	}

	.capability-icon {
		flex-shrink: 0;
		width: 48px;
		height: 48px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-primary-muted);
		color: var(--color-primary);
		border-radius: var(--radius-md);
		font-size: 1.25rem;
	}

	.capability-item h3 {
		font-size: 1rem;
		margin-bottom: var(--space-xs);
	}

	.capability-item p {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		line-height: 1.5;
		margin: 0;
	}

	.demo-section {
		margin-bottom: var(--space-2xl);
	}

	.demo-section h2 {
		font-size: 1.25rem;
		margin-bottom: var(--space-lg);
	}

	.demo-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
		gap: var(--space-lg);
	}

	.demo-card {
		display: block;
		padding: var(--space-xl);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
		text-decoration: none;
		color: var(--color-text);
		position: relative;
		transition: all var(--transition-normal);
	}

	.demo-card:hover {
		border-color: var(--color-primary);
		transform: translateY(-2px);
		box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
		text-decoration: none;
	}

	.demo-status {
		position: absolute;
		top: var(--space-md);
		right: var(--space-md);
		font-size: 0.6875rem;
		padding: 2px 8px;
		border-radius: var(--radius-sm);
		font-weight: 500;
	}

	.demo-status.live {
		background: var(--color-success-muted);
		color: var(--color-success);
	}

	.demo-icon {
		font-size: 2.5rem;
		display: block;
		margin-bottom: var(--space-md);
	}

	.demo-card h3 {
		margin-bottom: var(--space-sm);
	}

	.demo-card p {
		color: var(--color-text-muted);
		font-size: 0.875rem;
		line-height: 1.6;
		margin-bottom: var(--space-md);
	}

	.demo-features {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-xs);
	}

	.demo-features li {
		font-size: 0.75rem;
		padding: 2px 8px;
		background: var(--color-bg-hover);
		border-radius: var(--radius-sm);
		color: var(--color-text-muted);
	}

	.demo-features li::before {
		font-family: 'Font Awesome 6 Free';
		font-weight: 900;
		content: '\f00c ';
		color: var(--color-success);
	}

	.key-insight {
		margin-bottom: var(--space-2xl);
	}

	.insight-card {
		display: flex;
		align-items: flex-start;
		gap: var(--space-lg);
		padding: var(--space-xl);
		background: var(--color-primary-muted);
		border-radius: var(--radius-lg);
		border: 1px solid var(--color-primary);
	}

	.insight-icon {
		flex-shrink: 0;
		width: 56px;
		height: 56px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-primary);
		color: white;
		border-radius: var(--radius-md);
		font-size: 1.5rem;
	}

	.insight-card h3 {
		font-size: 1rem;
		margin-bottom: var(--space-xs);
	}

	.insight-card p {
		margin: 0;
		color: var(--color-text);
		line-height: 1.6;
	}

	code {
		background: rgba(255, 255, 255, 0.1);
		padding: 2px 6px;
		border-radius: var(--radius-sm);
		font-family: var(--font-mono);
		font-size: 0.9em;
	}

	@media (max-width: 768px) {
		.category-hero h1 {
			font-size: 1.75rem;
		}

		.hero-subtitle {
			font-size: 1rem;
		}

		.capability-grid,
		.demo-grid {
			grid-template-columns: 1fr;
		}

		.insight-card {
			flex-direction: column;
		}
	}
</style>
