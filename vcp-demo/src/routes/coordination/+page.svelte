<script lang="ts">
	/**
	 * Coordination Category Index
	 * AI-to-AI coordination with shared VCP context
	 */
</script>

<svelte:head>
	<title>Bilateral Coordination - VCP</title>
	<meta
		name="description"
		content="See how VCP enables AI agents to coordinate, negotiate, and make collective decisions while protecting private interests."
	/>
</svelte:head>

<div class="container">
	<section class="category-hero">
		<div class="category-badge">
			<i class="fa-solid fa-handshake" aria-hidden="true"></i>
			Coordination
		</div>
		<h1>Bilateral Coordination</h1>
		<p class="hero-subtitle">
			AI agents negotiating, competing, and collaborating—each with their own
			private interests, shared through VCP's graduated disclosure.
		</p>
	</section>

	<section class="capability-explainer">
		<div class="explainer-card">
			<h2>What VCP Enables</h2>
			<div class="capability-grid">
				<div class="capability-item">
					<span class="capability-icon"><i class="fa-solid fa-scale-balanced" aria-hidden="true"></i></span>
					<div>
						<h3>Graduated Disclosure</h3>
						<p>
							Agents reveal interests incrementally based on trust and stakes.
							Position first, interests later, red lines only when necessary.
						</p>
					</div>
				</div>
				<div class="capability-item">
					<span class="capability-icon"><i class="fa-solid fa-shield-halved" aria-hidden="true"></i></span>
					<div>
						<h3>Strategic Privacy</h3>
						<p>
							Private valuations remain private. Agents signal intent without
							revealing exact numbers. Fair competition without exploitation.
						</p>
					</div>
				</div>
				<div class="capability-item">
					<span class="capability-icon"><i class="fa-solid fa-clipboard-check" aria-hidden="true"></i></span>
					<div>
						<h3>Auditable Outcomes</h3>
						<p>
							Every decision has a clear audit trail. See what was shared,
							withheld, and how it influenced the final outcome.
						</p>
					</div>
				</div>
			</div>
		</div>
	</section>

	<section class="demo-section">
		<h2>Interactive Demos</h2>
		<div class="demo-grid">
			<a href="/demos/multi-agent/auction" class="demo-card">
				<div class="demo-status live">Live</div>
				<span class="demo-icon"><i class="fa-solid fa-gavel" aria-hidden="true"></i></span>
				<h3>Auction</h3>
				<p>
					Watch AI agents bid on artwork with hidden valuations.
					See how VCP enables strategic competition without exposing maximum budgets.
				</p>
				<ul class="demo-features">
					<li>Private valuations</li>
					<li>Trust signals</li>
					<li>Fair competition</li>
				</ul>
			</a>

			<a href="/demos/multi-agent/negotiation" class="demo-card">
				<div class="demo-status live">Live</div>
				<span class="demo-icon"><i class="fa-solid fa-comments" aria-hidden="true"></i></span>
				<h3>Negotiation</h3>
				<p>
					Two agents resolve a resource conflict with a mediator.
					Interests emerge gradually; red lines stay protected until necessary.
				</p>
				<ul class="demo-features">
					<li>Interest discovery</li>
					<li>Mediated dialogue</li>
					<li>Protected red lines</li>
				</ul>
			</a>

			<a href="/demos/multi-agent/policy-design" class="demo-card">
				<div class="demo-status live">Live</div>
				<span class="demo-icon"><i class="fa-solid fa-landmark" aria-hidden="true"></i></span>
				<h3>Policy Design</h3>
				<p>
					Multiple agents with different values design collective policy.
					Aggregate preferences without exposing individual reasoning.
				</p>
				<ul class="demo-features">
					<li>Value aggregation</li>
					<li>Reasoning privacy</li>
					<li>Influence audit</li>
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
					Multi-agent systems need the same privacy considerations humans do.
					Full transparency leads to exploitation; zero context leads to adversarial dynamics.
					VCP enables the <em>right amount</em> of mutual understanding—enough to cooperate,
					not enough to manipulate.
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
