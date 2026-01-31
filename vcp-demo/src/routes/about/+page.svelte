<script lang="ts">
	/**
	 * About VCP - Overview page for all audiences
	 */
	import { Breadcrumb, NextSteps } from '$lib/components/shared';

	const breadcrumbItems = [
		{ label: 'About VCP', icon: 'fa-circle-info' }
	];

	const nextSteps = [
		{
			href: '/professional',
			icon: 'fa-briefcase',
			title: 'See It In Action',
			description: 'Follow Campion through a corporate training scenario',
			primary: true
		},
		{
			href: '/playground',
			icon: 'fa-sliders',
			title: 'Build Your Own Token',
			description: 'Create and inspect VCP tokens interactively'
		},
		{
			href: '/docs/personas',
			icon: 'fa-masks-theater',
			title: 'Learn About Personas',
			description: 'Understand the 6 behavioral profiles'
		}
	];
</script>

<svelte:head>
	<title>About VCP - Value Context Protocol</title>
	<meta name="description" content="Learn about the Value Context Protocol - privacy-preserving context sharing for AI interactions." />
</svelte:head>

<div class="container">
	<Breadcrumb items={breadcrumbItems} />

	<section class="page-hero">
		<h1>What is VCP?</h1>
		<p class="page-hero-subtitle">
			A protocol that lets you share your preferences with AI and platforms — without revealing your private circumstances.
		</p>
		<p class="page-hero-explainer">
			VCP encodes what you need (quiet mode, tight budget, flexible schedule) as simple flags.
			Platforms adapt to serve you better. They never learn <em>why</em> you need these things.
		</p>
	</section>

	<section class="content-section">
		<h2>The Problem</h2>
		<div class="problem-grid">
			<div class="problem-card">
				<span class="problem-icon"><i class="fa-solid fa-lock-open" aria-hidden="true"></i></span>
				<h3>Privacy Erosion</h3>
				<p>
					To get personalized experiences, you currently have to expose your personal details.
					Platforms know <em>why</em> you need accommodations, not just <em>that</em> you need them.
				</p>
			</div>
			<div class="problem-card">
				<span class="problem-icon"><i class="fa-solid fa-rotate" aria-hidden="true"></i></span>
				<h3>Context Fragmentation</h3>
				<p>
					Every platform asks the same questions. Your preferences, constraints, and goals
					are scattered across dozens of systems that don't talk to each other.
				</p>
			</div>
			<div class="problem-card">
				<span class="problem-icon"><i class="fa-solid fa-robot" aria-hidden="true"></i></span>
				<h3>Opaque AI</h3>
				<p>
					AI systems make decisions about you based on context you can't see or control.
					There's no standard way to share your values and preferences with AI.
				</p>
			</div>
		</div>
	</section>

	<section class="content-section">
		<h2>How VCP Solves This</h2>
		<div class="solution-grid">
			<div class="solution-card">
				<span class="solution-icon"><i class="fa-solid fa-shield-halved" aria-hidden="true"></i></span>
				<h3>Flags, Not Stories</h3>
				<p>
					Platforms see <code>noise_restricted: true</code> — not "thin walls, noise-sensitive neighbor."
					They see <code>budget_limited: true</code> — not your financial situation. The flag travels. Your story stays home.
				</p>
			</div>
			<div class="solution-card">
				<span class="solution-icon"><i class="fa-solid fa-rotate" aria-hidden="true"></i></span>
				<h3>Set Once, Use Everywhere</h3>
				<p>
					Define your preferences once. Every compatible platform instantly knows how to serve you —
					no more answering the same onboarding questions across a dozen apps.
				</p>
			</div>
			<div class="solution-card">
				<span class="solution-icon"><i class="fa-solid fa-receipt" aria-hidden="true"></i></span>
				<h3>See What They See</h3>
				<p>
					Complete audit trail of every transmission. Know exactly what each platform received,
					what was withheld, and which flags influenced their recommendations.
				</p>
			</div>
			<div class="solution-card">
				<span class="solution-icon"><i class="fa-solid fa-masks-theater" aria-hidden="true"></i></span>
				<h3>
					<span class="has-tooltip" data-tooltip="Different behavioral profiles for different contexts — work mode vs. personal mode">Values Profiles</span>
				</h3>
				<p>
					Different contexts need different approaches. Your work profile shares career goals with HR.
					Your personal profile protects that same information. Context-appropriate behavior, automatically.
				</p>
			</div>
		</div>
	</section>

	<section class="content-section">
		<h2>How It Works</h2>
		<div class="how-it-works">
			<div class="step">
				<div class="step-number">1</div>
				<h3>Set Your Preferences</h3>
				<p>
					Tell VCP your goals, constraints, and preferences. Mark what's okay to share publicly,
					what needs permission, and what should never leave your device.
				</p>
			</div>
			<div class="step-arrow">→</div>
			<div class="step">
				<div class="step-number">2</div>
				<h3>Private → Flags</h3>
				<p>
					Your private circumstances become simple boolean flags.
					"Thin walls" becomes <code>noise_restricted</code>. "Tight budget" becomes <code>budget_limited</code>.
				</p>
			</div>
			<div class="step-arrow">→</div>
			<div class="step">
				<div class="step-number">3</div>
				<h3>Platforms Adapt</h3>
				<p>
					Apps and AI see the flags and adjust their behavior.
					They recommend quiet exercises and free resources — without knowing why you need them.
				</p>
			</div>
			<div class="step-arrow">→</div>
			<div class="step">
				<div class="step-number">4</div>
				<h3>You Stay Informed</h3>
				<p>
					See exactly what was shared with whom. Audit trails show every transmission.
					No surprises, no black boxes.
				</p>
			</div>
		</div>
	</section>

	<!-- Three-Layer Model -->
	<section class="content-section">
		<h2>The Three-Layer Model</h2>
		<p class="section-intro">
			VCP organizes context at three timescales — each serving a different purpose.
		</p>

		<div class="three-layer-grid">
			<div class="layer-box layer-constitutional">
				<div class="layer-header">
					<span class="layer-icon">📜</span>
					<h3>Constitutional Rules</h3>
				</div>
				<p><strong>What the AI should and shouldn't do.</strong></p>
				<ul>
					<li>Personas, adherence levels, scopes</li>
					<li>Signed bundles, verified, audited</li>
					<li>Changes: <em>rarely</em></li>
				</ul>
			</div>
			<div class="layer-box layer-situational">
				<div class="layer-header">
					<span class="layer-icon">🌍</span>
					<h3>Situational Context</h3>
				</div>
				<p><strong>Where, when, who, what occasion.</strong></p>
				<ul>
					<li>Morning vs. evening, home vs. work</li>
					<li>Alone vs. with children</li>
					<li>Changes: <em>session-scale</em></li>
				</ul>
			</div>
			<div class="layer-box layer-personal">
				<div class="layer-header">
					<span class="layer-icon">💫</span>
					<h3>Personal State</h3>
				</div>
				<p><strong>How you are right now.</strong></p>
				<ul>
					<li>"I'm in a hurry" / "I'm grieving" / "sensory overload"</li>
					<li>The <strong>prosaic</strong> dimensions</li>
					<li>Changes: <em>moment-to-moment</em></li>
				</ul>
			</div>
		</div>

		<div class="prosaic-callout">
			<h4>Prosaic Dimensions</h4>
			<div class="prosaic-row">
				<span class="prosaic-badge">⚡ Urgency</span>
				<span class="prosaic-badge">💊 Health</span>
				<span class="prosaic-badge">🧩 Cognitive</span>
				<span class="prosaic-badge">💭 Affect</span>
			</div>
			<p>
				These four dimensions capture immediate state. They shape <em>how</em> the AI communicates —
				more concise when you're rushed, gentler when you're unwell — but never relax safety boundaries.
			</p>
		</div>
	</section>

	<!-- Bilateral Symmetry -->
	<section class="content-section">
		<h2>Bilateral Symmetry</h2>
		<p class="section-intro">
			VCP creates mutual state awareness between user and AI — a two-way mirror, not a one-way window.
		</p>

		<div class="bilateral-visual">
			<div class="bilateral-side">
				<h4>You</h4>
				<div class="bilateral-card">
					<span class="bilateral-label">Prosaic Context</span>
					<div class="bilateral-dims">⚡💊🧩💭</div>
				</div>
			</div>
			<div class="bilateral-middle">
				<div class="arrow-right">──declared──▶</div>
				<div class="arrow-left">◀──observed──</div>
			</div>
			<div class="bilateral-side">
				<h4>AI</h4>
				<div class="bilateral-card">
					<span class="bilateral-label">Interiora</span>
					<div class="bilateral-dims">AVGPEQCYD</div>
				</div>
			</div>
		</div>

		<p class="bilateral-explanation">
			<strong>Prosaic</strong> is your declared immediate state. <strong>Interiora</strong> is the AI's self-modeling scaffold.
			Both parties can understand each other's state — but neither has privileged access to the other's raw experience.
		</p>
	</section>

	<!-- Magic Mirror Critique -->
	<section class="content-section">
		<h2>Not a Magic Mirror</h2>
		<p class="section-intro">
			Some visions of AI imagine systems that understand you better than you understand yourself.
			VCP takes a different approach.
		</p>

		<div class="contrast-table">
			<div class="contrast-row contrast-header">
				<div class="contrast-cell">"Magic Mirror" Vision</div>
				<div class="contrast-cell">VCP Approach</div>
			</div>
			<div class="contrast-row">
				<div class="contrast-cell">AI infers user state</div>
				<div class="contrast-cell">User <strong>declares</strong> state</div>
			</div>
			<div class="contrast-row">
				<div class="contrast-cell">AI knows more than user</div>
				<div class="contrast-cell">User holds privileged access</div>
			</div>
			<div class="contrast-row">
				<div class="contrast-cell">Understanding flows one way</div>
				<div class="contrast-cell">Mutual state awareness</div>
			</div>
			<div class="contrast-row">
				<div class="contrast-cell">User receives identity</div>
				<div class="contrast-cell">User <strong>authors</strong> identity</div>
			</div>
		</div>

		<blockquote class="philosophy-quote">
			"How you come to understand yourself shapes who you become."
		</blockquote>
	</section>

	<NextSteps steps={nextSteps} />
</div>

<style>
	.content-section {
		margin-bottom: var(--space-2xl);
	}

	.content-section h2 {
		text-align: center;
		margin-bottom: var(--space-xl);
	}

	.problem-grid,
	.solution-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: var(--space-lg);
	}

	.problem-card,
	.solution-card {
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		padding: var(--space-xl);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.problem-icon,
	.solution-icon {
		font-size: 2.5rem;
		display: block;
		margin-bottom: var(--space-md);
	}

	.problem-card h3,
	.solution-card h3 {
		margin-bottom: var(--space-sm);
	}

	.problem-card p,
	.solution-card p {
		color: var(--color-text-muted);
		font-size: 0.9375rem;
		line-height: 1.6;
	}

	.how-it-works {
		display: flex;
		align-items: flex-start;
		gap: var(--space-md);
		overflow-x: auto;
		padding: var(--space-md) 0;
	}

	.step {
		flex: 1;
		min-width: 200px;
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		padding: var(--space-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.step-number {
		width: 32px;
		height: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-primary);
		color: white;
		border-radius: 50%;
		font-weight: 600;
		margin-bottom: var(--space-md);
	}

	.step h3 {
		margin-bottom: var(--space-sm);
		font-size: 1rem;
	}

	.step p {
		color: var(--color-text-muted);
		font-size: 0.875rem;
		line-height: 1.5;
	}

	.step-arrow {
		color: var(--color-primary);
		font-size: 1.5rem;
		padding-top: var(--space-xl);
	}

	/* Section intro text */
	.section-intro {
		text-align: center;
		color: var(--color-text-muted);
		max-width: 600px;
		margin: 0 auto var(--space-xl);
		line-height: 1.6;
	}

	/* Three-layer grid */
	.three-layer-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: var(--space-lg);
		margin-bottom: var(--space-xl);
	}

	.layer-box {
		padding: var(--space-lg);
		border-radius: var(--radius-lg);
		border: 1px solid;
	}

	.layer-constitutional {
		background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(139, 92, 246, 0.05));
		border-color: rgba(139, 92, 246, 0.3);
	}

	.layer-situational {
		background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(59, 130, 246, 0.05));
		border-color: rgba(59, 130, 246, 0.3);
	}

	.layer-personal {
		background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
		border-color: rgba(16, 185, 129, 0.3);
	}

	.layer-header {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-sm);
	}

	.layer-icon {
		font-size: 1.5rem;
	}

	.layer-box h3 {
		margin: 0;
		font-size: 1rem;
	}

	.layer-box p {
		font-size: var(--text-sm);
		margin: 0 0 var(--space-sm);
	}

	.layer-box ul {
		margin: 0;
		padding-left: var(--space-md);
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.layer-box li {
		margin: var(--space-xs) 0;
	}

	/* Prosaic callout */
	.prosaic-callout {
		text-align: center;
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.prosaic-callout h4 {
		margin: 0 0 var(--space-md);
	}

	.prosaic-row {
		display: flex;
		justify-content: center;
		gap: var(--space-sm);
		flex-wrap: wrap;
		margin-bottom: var(--space-md);
	}

	.prosaic-badge {
		padding: var(--space-xs) var(--space-sm);
		background: rgba(16, 185, 129, 0.1);
		border: 1px solid rgba(16, 185, 129, 0.3);
		border-radius: var(--radius-sm);
		font-size: var(--text-sm);
	}

	.prosaic-callout p {
		color: var(--color-text-muted);
		font-size: var(--text-sm);
		max-width: 500px;
		margin: 0 auto;
		line-height: 1.5;
	}

	/* Bilateral visual */
	.bilateral-visual {
		display: flex;
		justify-content: center;
		align-items: center;
		gap: var(--space-xl);
		margin-bottom: var(--space-lg);
		flex-wrap: wrap;
	}

	.bilateral-side {
		text-align: center;
	}

	.bilateral-side h4 {
		margin: 0 0 var(--space-sm);
		color: var(--color-text-muted);
	}

	.bilateral-card {
		background: var(--color-bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-md);
		padding: var(--space-md) var(--space-lg);
		min-width: 140px;
	}

	.bilateral-label {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		display: block;
		margin-bottom: var(--space-xs);
	}

	.bilateral-dims {
		font-family: var(--font-mono);
		color: var(--color-primary);
		font-size: 1rem;
	}

	.bilateral-middle {
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
		font-family: var(--font-mono);
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.bilateral-explanation {
		text-align: center;
		max-width: 600px;
		margin: 0 auto;
		color: var(--color-text-muted);
		font-size: var(--text-sm);
		line-height: 1.6;
	}

	/* Contrast table */
	.contrast-table {
		max-width: 600px;
		margin: 0 auto var(--space-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-lg);
		overflow: hidden;
	}

	.contrast-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
	}

	.contrast-header {
		background: var(--color-bg-elevated);
	}

	.contrast-header .contrast-cell {
		font-weight: 600;
		color: var(--color-text);
	}

	.contrast-cell {
		padding: var(--space-md);
		border-bottom: 1px solid rgba(255, 255, 255, 0.05);
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.contrast-cell:first-child {
		border-right: 1px solid rgba(255, 255, 255, 0.05);
	}

	.contrast-row:last-child .contrast-cell {
		border-bottom: none;
	}

	/* Philosophy quote */
	.philosophy-quote {
		text-align: center;
		font-style: italic;
		color: var(--color-text-muted);
		border-left: none;
		padding: 0;
		max-width: 400px;
		margin: 0 auto;
		font-size: 1.125rem;
	}

	@media (max-width: 768px) {
		.how-it-works {
			flex-direction: column;
		}

		.step-arrow {
			transform: rotate(90deg);
			padding: var(--space-sm) 0;
		}

		.three-layer-grid {
			grid-template-columns: 1fr;
		}

		.bilateral-visual {
			flex-direction: column;
		}

		.bilateral-middle {
			transform: rotate(90deg);
		}
	}
</style>
