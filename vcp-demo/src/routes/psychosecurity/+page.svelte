<script lang="ts">
	/**
	 * Psychosecurity Category Index
	 * Context protecting against manipulation
	 */
</script>

<svelte:head>
	<title>Psychosecurity - VCP</title>
	<meta
		name="description"
		content="See how VCP context protects against manipulation—attention budgets, dark pattern detection, and safe mental health disclosure."
	/>
</svelte:head>

<div class="container">
	<section class="category-hero">
		<div class="category-badge">
			<i class="fa-solid fa-shield-heart" aria-hidden="true"></i>
			Psychosecurity
		</div>
		<h1>Psychosecurity</h1>
		<p class="hero-subtitle">
			VCP context that protects rather than exploits—attention budgets,
			manipulation detection, and graduated disclosure for sensitive states.
		</p>
	</section>

	<section class="capability-explainer">
		<div class="explainer-card">
			<h2>What VCP Enables</h2>
			<div class="capability-grid">
				<div class="capability-item">
					<span class="capability-icon"><i class="fa-solid fa-eye" aria-hidden="true"></i></span>
					<div>
						<h3>Attention Protection</h3>
						<p>
							Track daily attention budget. Detect manipulation patterns:
							false urgency, variable rewards, outrage bait. Shield yourself
							from Sirens; welcome the Muses.
						</p>
					</div>
				</div>
				<div class="capability-item">
					<span class="capability-icon"><i class="fa-solid fa-heart" aria-hidden="true"></i></span>
					<div>
						<h3>Safe Disclosure</h3>
						<p>
							Mental health context with graduated visibility. Share enough
							for helpful adaptation without surveillance. Support without exposure.
						</p>
					</div>
				</div>
				<div class="capability-item">
					<span class="capability-icon"><i class="fa-solid fa-user-shield" aria-hidden="true"></i></span>
					<div>
						<h3>Manipulation Resistance</h3>
						<p>
							VCP context includes vulnerability state. Systems that care
							can protect you. Systems that would exploit you get blocked.
						</p>
					</div>
				</div>
			</div>
		</div>
	</section>

	<section class="demo-section">
		<h2>Interactive Demos</h2>
		<div class="demo-grid">
			<a href="/demos/safety/attention-protection" class="demo-card">
				<div class="demo-status live">Live</div>
				<span class="demo-icon"><i class="fa-solid fa-bell-slash" aria-hidden="true"></i></span>
				<h3>Attention Protection</h3>
				<p>
					Explore the Siren vs. Muse framework. See manipulation patterns
					detected and blocked. Manage your attention budget across platforms.
				</p>
				<ul class="demo-features">
					<li>Pattern detection</li>
					<li>Attention budget</li>
					<li>Protection modes</li>
				</ul>
			</a>

			<a href="/demos/safety/mental-health" class="demo-card">
				<div class="demo-status live">Live</div>
				<span class="demo-icon" style="color: var(--color-success)"><i class="fa-solid fa-hand-holding-heart" aria-hidden="true"></i></span>
				<h3>Mental Health Context</h3>
				<p>
					Configure sensitive context with graduated visibility. See exactly
					what different stakeholders would learn. Privacy guarantees displayed.
				</p>
				<ul class="demo-features">
					<li>Graduated disclosure</li>
					<li>Stakeholder views</li>
					<li>Crisis protocols</li>
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
					The same context that enables personalization can also enable exploitation.
					Psychosecurity flips the script: VCP context that <em>protects</em> rather than
					<em>targets</em>. Your vulnerability signals become shields, not vulnerabilities.
					Platforms that respect VCP work with your context to help; those that don't
					get less access, not more.
				</p>
			</div>
		</div>
	</section>

	<section class="warning-section">
		<div class="warning-card">
			<span class="warning-icon"><i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i></span>
			<div>
				<h3>A Note on Sensitive Topics</h3>
				<p>
					The Mental Health Context demo discusses sensitive topics including
					crisis situations. All examples are simulated for educational purposes.
					If you're experiencing a mental health crisis, please contact a crisis
					helpline in your region.
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
		grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
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
		margin-bottom: var(--space-xl);
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

	.warning-section {
		margin-bottom: var(--space-2xl);
	}

	.warning-card {
		display: flex;
		align-items: flex-start;
		gap: var(--space-lg);
		padding: var(--space-lg);
		background: var(--color-warning-muted);
		border-radius: var(--radius-lg);
		border: 1px solid var(--color-warning);
	}

	.warning-icon {
		flex-shrink: 0;
		font-size: 1.5rem;
		color: var(--color-warning);
	}

	.warning-card h3 {
		font-size: 0.875rem;
		margin-bottom: var(--space-xs);
	}

	.warning-card p {
		margin: 0;
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		line-height: 1.5;
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

		.insight-card,
		.warning-card {
			flex-direction: column;
		}
	}
</style>
