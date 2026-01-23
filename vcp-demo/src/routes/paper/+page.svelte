<script lang="ts">
	const authors = [
		{ name: 'Nell Watson', affiliation: 'Creed Space' },
		{ name: 'Elena Ajayi', affiliation: 'Creed Space' },
		{ name: 'Filip Alimpic', affiliation: 'Creed Space' },
		{ name: 'Awwab Mahdi', affiliation: 'Creed Space' },
		{ name: 'Blake Wells', affiliation: 'Creed Space' }
	];

	const layers = [
		{
			id: 'I',
			name: 'Identity',
			description: 'Naming conventions, namespace governance, and privacy-preserving registry for constitutional artifacts',
			icon: 'fa-fingerprint'
		},
		{
			id: 'T',
			name: 'Transport',
			description: 'Bundles, cryptographic verification, and audit logging for secure value exchange',
			icon: 'fa-truck-fast'
		},
		{
			id: 'S',
			name: 'Semantics',
			description: 'CSM1 formal grammar with 8 personas, 11 scopes, 6 adherence levels, and composition modes',
			icon: 'fa-code'
		},
		{
			id: 'A',
			name: 'Adaptation',
			description: 'Context encoding via the 9-dimension Enneagram Protocol with transition detection',
			icon: 'fa-sliders'
		}
	];

	const contributions = [
		'First formal protocol stack for inter-agent value communication',
		'CSM1 grammar enabling precise constitutional specification',
		'Latent State Bridge (LSB) for cross-architecture value exchange',
		'MillOS VCL implementation for human-AI workplace contexts',
		'195 passing tests with ≥90% semantic fidelity in round-trip translations'
	];
</script>

<svelte:head>
	<title>VCP Paper | Value Context Protocols</title>
	<meta name="description" content="Value Context Protocols: Standards for Inter-Agent Value Communication - A modular four-layer stack for AI alignment and coordination." />
</svelte:head>

<div class="paper-page">
	<!-- Hero Section -->
	<section class="hero">
		<div class="container">
			<div class="badge">Research Paper</div>
			<h1>Value Context Protocols</h1>
			<p class="subtitle">Standards for Inter-Agent Value Communication</p>

			<div class="authors">
				{#each authors as author, i}
					<span class="author">{author.name}</span>{#if i < authors.length - 1}<span class="separator">,</span>{/if}
				{/each}
			</div>
			<p class="date">January 2026</p>

			<div class="cta-buttons">
				<a href="/Value Context Protocol Paper I1D1.pdf" class="btn btn-primary" target="_blank" rel="noopener noreferrer">
					<i class="fa-solid fa-file-pdf"></i>
					Download PDF
				</a>
			</div>
		</div>
	</section>

	<!-- Abstract Section -->
	<section class="abstract">
		<div class="container">
			<h2>Abstract</h2>
			<div class="abstract-content">
				<p>
					As AI systems assume increasingly autonomous roles, the absence of a shared representational
					substrate for values risks compounding cultural bias, semantic drift, and coordination failure.
					Current alignment methods optimize for compliance in limited contexts rather than mutual
					interpretability across pluralistic systems.
				</p>
				<p>
					We introduce <strong>Value Context Protocols (VCP)</strong>: a modular four-layer stack for
					inter-agent value communication. The protocol enables AI systems to exchange, negotiate, and
					adapt value representations while preserving semantic fidelity across architectural boundaries.
				</p>
			</div>
		</div>
	</section>

	<!-- I-T-S-A Stack Section -->
	<section class="stack">
		<div class="container">
			<h2>The I-T-S-A Stack</h2>
			<p class="section-intro">Four layers working together to enable robust value communication</p>

			<div class="layers-grid">
				{#each layers as layer}
					<div class="layer-card">
						<div class="layer-header">
							<div class="layer-icon">
								<i class="fa-solid {layer.icon}"></i>
							</div>
							<div class="layer-id">VCP/{layer.id}</div>
						</div>
						<h3>{layer.name}</h3>
						<p>{layer.description}</p>
					</div>
				{/each}
			</div>
		</div>
	</section>

	<!-- Key Contributions Section -->
	<section class="contributions">
		<div class="container">
			<h2>Key Contributions</h2>
			<ul class="contribution-list">
				{#each contributions as contribution}
					<li>
						<i class="fa-solid fa-check"></i>
						<span>{contribution}</span>
					</li>
				{/each}
			</ul>
		</div>
	</section>

	<!-- Implementations Section -->
	<section class="implementations">
		<div class="container">
			<h2>Reference Implementations</h2>
			<div class="impl-grid">
				<div class="impl-card">
					<div class="impl-icon">
						<i class="fa-solid fa-bridge"></i>
					</div>
					<h3>Latent State Bridge (LSB)</h3>
					<p>Cross-architecture value exchange between AI systems with different internal representations</p>
				</div>
				<div class="impl-card">
					<div class="impl-icon">
						<i class="fa-solid fa-building"></i>
					</div>
					<h3>MillOS VCL</h3>
					<p>Human-AI workplace contexts with constitutional governance and preference learning</p>
				</div>
			</div>
		</div>
	</section>

	<!-- CTA Section -->
	<section class="final-cta">
		<div class="container">
			<h2>Read the Full Paper</h2>
			<p>Dive into the technical specification and implementation details</p>
			<div class="cta-buttons">
				<a href="/Value Context Protocol Paper I1D1.pdf" class="btn btn-primary btn-lg" target="_blank" rel="noopener noreferrer">
					<i class="fa-solid fa-file-pdf"></i>
					Download PDF
				</a>
				<a href="/playground" class="btn btn-secondary btn-lg">
					<i class="fa-solid fa-play"></i>
					Try the Playground
				</a>
			</div>
		</div>
	</section>
</div>

<style>
	.paper-page {
		--accent: var(--color-primary);
	}

	/* Hero */
	.hero {
		text-align: center;
		padding: var(--space-3xl) 0;
		background: linear-gradient(180deg, var(--color-bg-elevated) 0%, var(--color-bg) 100%);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.badge {
		display: inline-block;
		padding: var(--space-xs) var(--space-md);
		background: var(--color-primary-muted);
		color: var(--color-primary);
		border-radius: var(--radius-full);
		font-size: 0.875rem;
		font-weight: 500;
		margin-bottom: var(--space-lg);
	}

	.hero h1 {
		font-size: clamp(2rem, 5vw, 3.5rem);
		font-weight: 700;
		margin-bottom: var(--space-sm);
		background: linear-gradient(135deg, var(--color-text) 0%, var(--color-primary) 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.subtitle {
		font-size: clamp(1.125rem, 2.5vw, 1.5rem);
		color: var(--color-text-muted);
		margin-bottom: var(--space-xl);
	}

	.authors {
		font-size: 1rem;
		color: var(--color-text);
		margin-bottom: var(--space-xs);
	}

	.author {
		font-weight: 500;
	}

	.separator {
		color: var(--color-text-muted);
		margin: 0 var(--space-xs);
	}

	.date {
		color: var(--color-text-muted);
		font-size: 0.875rem;
		margin-bottom: var(--space-xl);
	}

	.cta-buttons {
		display: flex;
		gap: var(--space-md);
		justify-content: center;
		flex-wrap: wrap;
	}

	.btn {
		display: inline-flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-sm) var(--space-lg);
		border-radius: var(--radius-md);
		font-weight: 500;
		text-decoration: none;
		transition: all var(--transition-fast);
	}

	.btn-primary {
		background: var(--color-primary);
		color: var(--color-bg);
	}

	.btn-primary:hover {
		background: var(--color-primary-hover);
		transform: translateY(-2px);
	}

	.btn-secondary {
		background: rgba(255, 255, 255, 0.1);
		color: var(--color-text);
		border: 1px solid rgba(255, 255, 255, 0.2);
	}

	.btn-secondary:hover {
		background: rgba(255, 255, 255, 0.15);
		transform: translateY(-2px);
	}

	.btn-lg {
		padding: var(--space-md) var(--space-xl);
		font-size: 1.125rem;
	}

	/* Abstract */
	.abstract {
		padding: var(--space-3xl) 0;
	}

	.abstract h2 {
		font-size: 1.75rem;
		margin-bottom: var(--space-lg);
	}

	.abstract-content {
		max-width: 800px;
		margin: 0 auto;
		font-size: 1.125rem;
		line-height: 1.8;
		color: var(--color-text-muted);
	}

	.abstract-content p {
		margin-bottom: var(--space-md);
	}

	.abstract-content strong {
		color: var(--color-primary);
	}

	/* Stack */
	.stack {
		padding: var(--space-3xl) 0;
		background: var(--color-bg-elevated);
	}

	.stack h2 {
		text-align: center;
		font-size: 1.75rem;
		margin-bottom: var(--space-sm);
	}

	.section-intro {
		text-align: center;
		color: var(--color-text-muted);
		margin-bottom: var(--space-2xl);
	}

	.layers-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: var(--space-lg);
	}

	.layer-card {
		background: var(--color-bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-lg);
		padding: var(--space-xl);
		transition: all var(--transition-fast);
	}

	.layer-card:hover {
		border-color: var(--color-primary);
		transform: translateY(-4px);
	}

	.layer-header {
		display: flex;
		align-items: center;
		gap: var(--space-md);
		margin-bottom: var(--space-md);
	}

	.layer-icon {
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

	.layer-id {
		font-family: var(--font-mono);
		font-size: 0.875rem;
		color: var(--color-primary);
		background: var(--color-primary-muted);
		padding: var(--space-xs) var(--space-sm);
		border-radius: var(--radius-sm);
	}

	.layer-card h3 {
		font-size: 1.25rem;
		margin-bottom: var(--space-sm);
	}

	.layer-card p {
		color: var(--color-text-muted);
		font-size: 0.9375rem;
		line-height: 1.6;
	}

	/* Contributions */
	.contributions {
		padding: var(--space-3xl) 0;
	}

	.contributions h2 {
		text-align: center;
		font-size: 1.75rem;
		margin-bottom: var(--space-2xl);
	}

	.contribution-list {
		max-width: 700px;
		margin: 0 auto;
		list-style: none;
		padding: 0;
	}

	.contribution-list li {
		display: flex;
		align-items: flex-start;
		gap: var(--space-md);
		padding: var(--space-md) 0;
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
		font-size: 1.0625rem;
	}

	.contribution-list li:last-child {
		border-bottom: none;
	}

	.contribution-list i {
		color: var(--color-success);
		margin-top: 4px;
		flex-shrink: 0;
	}

	/* Implementations */
	.implementations {
		padding: var(--space-3xl) 0;
		background: var(--color-bg-elevated);
	}

	.implementations h2 {
		text-align: center;
		font-size: 1.75rem;
		margin-bottom: var(--space-2xl);
	}

	.impl-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
		gap: var(--space-xl);
		max-width: 800px;
		margin: 0 auto;
	}

	.impl-card {
		text-align: center;
		padding: var(--space-2xl);
		background: var(--color-bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-lg);
	}

	.impl-icon {
		width: 64px;
		height: 64px;
		margin: 0 auto var(--space-lg);
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-primary-muted);
		color: var(--color-primary);
		border-radius: var(--radius-lg);
		font-size: 1.5rem;
	}

	.impl-card h3 {
		font-size: 1.25rem;
		margin-bottom: var(--space-sm);
	}

	.impl-card p {
		color: var(--color-text-muted);
		font-size: 0.9375rem;
		line-height: 1.6;
	}

	/* Final CTA */
	.final-cta {
		padding: var(--space-3xl) 0;
		text-align: center;
	}

	.final-cta h2 {
		font-size: 2rem;
		margin-bottom: var(--space-sm);
	}

	.final-cta > .container > p {
		color: var(--color-text-muted);
		margin-bottom: var(--space-xl);
		font-size: 1.125rem;
	}

	/* Responsive */
	@media (max-width: 768px) {
		.hero {
			padding: var(--space-2xl) 0;
		}

		.layers-grid {
			grid-template-columns: 1fr;
		}

		.impl-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
