<script lang="ts">
	/**
	 * Personas Documentation
	 * Comprehensive guide to VCP's 6 AI personas
	 */
	import { Breadcrumb } from '$lib/components/shared';

	const breadcrumbItems = [
		{ label: 'Docs', href: '/docs' },
		{ label: 'Understanding Personas', icon: 'fa-masks-theater' }
	];

	interface Persona {
		id: string;
		name: string;
		icon: string;
		tagline: string;
		description: string;
		bestFor: string[];
		example: string;
		color: string;
	}

	const personas: Persona[] = [
		{
			id: 'muse',
			name: 'Muse',
			icon: 'fa-palette',
			tagline: 'Creative exploration and personal growth',
			description: 'The Muse encourages experimentation, celebrates small wins, and adapts to your creative rhythm. It prioritizes intrinsic motivation over external metrics.',
			bestFor: ['Learning hobbies', 'Creative projects', 'Self-expression', 'Exploration without pressure'],
			example: 'Gentian uses Muse when learning guitar — it suggests practice exercises based on mood and energy, not just a rigid curriculum.',
			color: 'var(--color-primary)'
		},
		{
			id: 'ambassador',
			name: 'Ambassador',
			icon: 'fa-handshake',
			tagline: 'Professional representation',
			description: 'The Ambassador represents your interests in professional contexts. It shares work-appropriate information while protecting personal details from colleagues and managers.',
			bestFor: ['Corporate training', 'Professional development', 'Workplace interactions', 'Career advancement'],
			example: 'Campion uses Ambassador for corporate L&D — HR sees her career goals, not her health situation.',
			color: 'var(--color-professional)'
		},
		{
			id: 'godparent',
			name: 'Godparent',
			icon: 'fa-shield-heart',
			tagline: 'Wellbeing-focused guidance',
			description: 'The Godparent prioritizes your long-term wellbeing over short-term productivity. It knows when to suggest rest, recognizes burnout patterns, and protects against overcommitment.',
			bestFor: ['Health management', 'Work-life balance', 'Burnout prevention', 'Personal struggles'],
			example: 'Campion switches to Godparent at home — it checks her energy levels and suggests lighter activities when needed.',
			color: 'var(--color-warning)'
		},
		{
			id: 'sentinel',
			name: 'Sentinel',
			icon: 'fa-eye',
			tagline: 'Privacy and security watchdog',
			description: 'The Sentinel actively monitors what information is being shared and alerts you to potential privacy risks. It defaults to maximum privacy and requires explicit consent for sharing.',
			bestFor: ['Sensitive contexts', 'Data-conscious users', 'High-stakes decisions', 'Privacy-first scenarios'],
			example: 'When connecting to a new platform, Sentinel reviews the data request and flags anything unusual.',
			color: 'var(--color-danger)'
		},
		{
			id: 'anchor',
			name: 'Anchor',
			icon: 'fa-anchor',
			tagline: 'Stability and consistency',
			description: 'The Anchor maintains consistency across platforms and time. It remembers your preferences, ensures continuity, and prevents context-switching fatigue.',
			bestFor: ['Multi-platform users', 'Long-term projects', 'Consistent experience', 'Preference persistence'],
			example: 'Anchor ensures your quiet-mode preference follows you from JustinGuitar to Yousician to community challenges.',
			color: 'var(--color-success)'
		},
		{
			id: 'nanny',
			name: 'Nanny',
			icon: 'fa-child',
			tagline: 'Protective guidance for vulnerable users',
			description: 'The Nanny provides extra guardrails for users who need more protection — whether due to age, experience level, or specific vulnerabilities. It filters content and limits exposure.',
			bestFor: ['Young users', 'New learners', 'Vulnerable populations', 'Controlled environments'],
			example: 'For a teenager learning to code, Nanny filters out advanced topics and maintains age-appropriate boundaries.',
			color: '#ec4899'
		}
	];
</script>

<svelte:head>
	<title>Understanding Personas - VCP Documentation</title>
	<meta name="description" content="Learn about VCP's 6 AI personas: Muse, Ambassador, Godparent, Sentinel, Anchor, and Nanny. Each shapes how AI interacts with you." />
</svelte:head>

<div class="container">
	<Breadcrumb items={breadcrumbItems} />

	<section class="page-hero">
		<h1>Understanding Personas</h1>
		<p class="page-hero-subtitle">
			Personas are behavioral profiles that shape how AI interacts with you. Think of them as different "modes" your AI assistant can operate in.
		</p>
	</section>

	<!-- Quick comparison -->
	<section class="comparison-section">
		<h2>At a Glance</h2>
		<div class="comparison-table-wrapper">
			<table class="comparison-table">
				<thead>
					<tr>
						<th>Persona</th>
						<th>Focus</th>
						<th>Best For</th>
					</tr>
				</thead>
				<tbody>
					{#each personas as persona}
						<tr>
							<td>
								<span class="persona-name-cell">
									<i class="fa-solid {persona.icon}" style="color: {persona.color}" aria-hidden="true"></i>
									{persona.name}
								</span>
							</td>
							<td class="tagline-cell">{persona.tagline}</td>
							<td class="best-for-cell">{persona.bestFor[0]}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</section>

	<!-- Detailed cards -->
	<section class="personas-detail">
		<h2>Detailed Guide</h2>
		<div class="personas-grid">
			{#each personas as persona}
				<article class="persona-card" style="--persona-color: {persona.color}">
					<header class="persona-header">
						<span class="persona-icon">
							<i class="fa-solid {persona.icon}" aria-hidden="true"></i>
						</span>
						<div>
							<h3>{persona.name}</h3>
							<p class="persona-tagline">{persona.tagline}</p>
						</div>
					</header>

					<p class="persona-description">{persona.description}</p>

					<div class="persona-best-for">
						<h4>Best for:</h4>
						<ul>
							{#each persona.bestFor as use}
								<li>{use}</li>
							{/each}
						</ul>
					</div>

					<div class="persona-example">
						<h4>Example:</h4>
						<p>{persona.example}</p>
					</div>
				</article>
			{/each}
		</div>
	</section>

	<!-- Switching personas -->
	<section class="switching-section">
		<h2>Switching Between Personas</h2>
		<div class="switching-content">
			<div class="switching-card">
				<h4><i class="fa-solid fa-clock" aria-hidden="true"></i> Automatic Switching</h4>
				<p>
					VCP can automatically switch personas based on context. Campion uses Ambassador during work hours and Godparent in the evening — no manual intervention needed.
				</p>
			</div>
			<div class="switching-card">
				<h4><i class="fa-solid fa-hand-pointer" aria-hidden="true"></i> Manual Override</h4>
				<p>
					You can always override the automatic selection. Need Sentinel mode for a sensitive conversation? Just switch. Your choice always takes precedence.
				</p>
			</div>
			<div class="switching-card">
				<h4><i class="fa-solid fa-layer-group" aria-hidden="true"></i> Multiple Constitutions</h4>
				<p>
					Different areas of life can have different personas. Campion has a work constitution (Ambassador) and a personal constitution (Godparent) that activate based on context.
				</p>
			</div>
		</div>
	</section>

	<!-- Try it -->
	<section class="try-section">
		<h2>See Personas in Action</h2>
		<p class="try-description">Experience how different personas affect AI behavior in our interactive demos.</p>
		<div class="try-links">
			<a href="/professional" class="try-link">
				<i class="fa-solid fa-briefcase" aria-hidden="true"></i>
				<span>Campion's dual personas</span>
			</a>
			<a href="/playground" class="try-link">
				<i class="fa-solid fa-sliders" aria-hidden="true"></i>
				<span>Build your own context</span>
			</a>
		</div>
	</section>
</div>

<style>
	/* Comparison table */
	.comparison-section {
		margin-bottom: var(--space-2xl);
	}

	.comparison-section h2 {
		margin-bottom: var(--space-lg);
	}

	.comparison-table-wrapper {
		overflow-x: auto;
	}

	.comparison-table {
		width: 100%;
		border-collapse: collapse;
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		overflow: hidden;
	}

	.comparison-table th,
	.comparison-table td {
		padding: var(--space-md) var(--space-lg);
		text-align: left;
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.comparison-table th {
		background: rgba(255, 255, 255, 0.05);
		font-size: var(--text-xs);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-muted);
	}

	.comparison-table tr:last-child td {
		border-bottom: none;
	}

	.persona-name-cell {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-weight: 500;
	}

	.tagline-cell {
		color: var(--color-text-muted);
		font-size: var(--text-sm);
	}

	.best-for-cell {
		font-size: var(--text-sm);
	}

	/* Personas detail */
	.personas-detail {
		margin-bottom: var(--space-2xl);
	}

	.personas-detail h2 {
		margin-bottom: var(--space-lg);
	}

	.personas-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
		gap: var(--space-lg);
	}

	.persona-card {
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		padding: var(--space-xl);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-top: 3px solid var(--persona-color);
	}

	.persona-header {
		display: flex;
		align-items: flex-start;
		gap: var(--space-md);
		margin-bottom: var(--space-lg);
	}

	.persona-icon {
		width: 48px;
		height: 48px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		font-size: 1.5rem;
		color: var(--persona-color);
		flex-shrink: 0;
	}

	.persona-header h3 {
		font-size: var(--text-xl);
		margin-bottom: var(--space-xs);
	}

	.persona-tagline {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.persona-description {
		color: var(--color-text-muted);
		font-size: var(--text-sm);
		line-height: var(--leading-relaxed);
		margin-bottom: var(--space-lg);
	}

	.persona-best-for h4,
	.persona-example h4 {
		font-size: var(--text-xs);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-subtle);
		margin-bottom: var(--space-sm);
	}

	.persona-best-for ul {
		list-style: none;
		padding: 0;
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-xs);
		margin-bottom: var(--space-lg);
	}

	.persona-best-for li {
		font-size: var(--text-xs);
		padding: var(--space-xs) var(--space-sm);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-sm);
	}

	.persona-example p {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		font-style: italic;
		padding-left: var(--space-md);
		border-left: 2px solid var(--persona-color);
	}

	/* Switching section */
	.switching-section {
		margin-bottom: var(--space-2xl);
	}

	.switching-section h2 {
		margin-bottom: var(--space-lg);
	}

	.switching-content {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: var(--space-lg);
	}

	.switching-card {
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		padding: var(--space-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.switching-card h4 {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-sm);
	}

	.switching-card h4 i {
		color: var(--color-primary);
	}

	.switching-card p {
		color: var(--color-text-muted);
		font-size: var(--text-sm);
		line-height: var(--leading-relaxed);
	}

	/* Try section */
	.try-section {
		text-align: center;
		padding: var(--space-xl) 0;
	}

	.try-section h2 {
		margin-bottom: var(--space-sm);
	}

	.try-description {
		color: var(--color-text-muted);
		margin-bottom: var(--space-lg);
	}

	.try-links {
		display: flex;
		justify-content: center;
		gap: var(--space-md);
		flex-wrap: wrap;
	}

	.try-link {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-md) var(--space-lg);
		background: var(--color-bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-md);
		color: var(--color-text);
		text-decoration: none;
		transition: all var(--transition-fast);
	}

	.try-link:hover {
		border-color: var(--color-primary);
		color: var(--color-primary);
		text-decoration: none;
	}

	.try-link i {
		color: var(--color-primary);
	}

	@media (max-width: 768px) {
		.personas-grid {
			grid-template-columns: 1fr;
		}

		.comparison-table th:nth-child(3),
		.comparison-table td:nth-child(3) {
			display: none;
		}
	}
</style>
