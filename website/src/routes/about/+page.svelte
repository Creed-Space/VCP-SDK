<script lang="ts">
	/**
	 * About VCP - Overview page for all audiences
	 */
	import { audience, AUDIENCE_META } from '$lib/stores/audience';
</script>

<svelte:head>
	<title>About VCP - Value Context Protocol</title>
	<meta name="description" content="Learn about the Value Context Protocol - privacy-preserving context sharing for AI interactions." />
</svelte:head>

<div class="container">
	<section class="hero">
		<h1>What is VCP?</h1>
		<p class="hero-subtitle">
			The Value Context Protocol enables privacy-preserving context sharing between humans, AI systems, and platforms.
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
		<h2>The VCP Solution</h2>
		<div class="solution-grid">
			<div class="solution-card">
				<span class="solution-icon"><i class="fa-solid fa-lock" aria-hidden="true"></i></span>
				<h3>Privacy by Design</h3>
				<p>
					Share <strong>flags</strong>, not <strong>details</strong>. Platforms see "noise_restricted: true"
					not "lives in thin-walled apartment with noise-sensitive elderly neighbors."
				</p>
			</div>
			<div class="solution-card">
				<span class="solution-icon"><i class="fa-solid fa-mobile-screen" aria-hidden="true"></i></span>
				<h3>Portable Context</h3>
				<p>
					Configure once, use everywhere. Your VCP context travels with you across compatible
					platforms, eliminating repetitive setup.
				</p>
			</div>
			<div class="solution-card">
				<span class="solution-icon"><i class="fa-solid fa-eye" aria-hidden="true"></i></span>
				<h3>Full Transparency</h3>
				<p>
					See exactly what each platform receives. Audit trails show what was shared,
					what was withheld, and how private context influenced decisions.
				</p>
			</div>
			<div class="solution-card">
				<span class="solution-icon"><i class="fa-solid fa-handshake" aria-hidden="true"></i></span>
				<h3>Bilateral Alignment</h3>
				<p>
					VCP isn't just for humans sharing with AI—it enables AI systems to share their
					own context, preferences, and constraints with each other and with humans.
				</p>
			</div>
		</div>
	</section>

	<section class="content-section">
		<h2>How It Works</h2>
		<div class="how-it-works">
			<div class="step">
				<div class="step-number">1</div>
				<h3>Define Your Context</h3>
				<p>
					Build your VCP context with goals, preferences, constraints, and values using
					any compatible tool. Mark what's public, what requires consent, and what's always private.
				</p>
			</div>
			<div class="step-arrow">→</div>
			<div class="step">
				<div class="step-number">2</div>
				<h3>Encode as Token</h3>
				<p>
					Your context becomes a compact CSM-1 token with emoji shortcodes.
					Private details become boolean flags that influence without exposing.
				</p>
			</div>
			<div class="step-arrow">→</div>
			<div class="step">
				<div class="step-number">3</div>
				<h3>Share Selectively</h3>
				<p>
					Platforms receive only what you've consented to share.
					Different stakeholders see different views of the same context.
				</p>
			</div>
			<div class="step-arrow">→</div>
			<div class="step">
				<div class="step-number">4</div>
				<h3>Audit Everything</h3>
				<p>
					Full audit trail of what was shared, when, and with whom.
					You always know how your context influenced decisions.
				</p>
			</div>
		</div>
	</section>

	<section class="content-section cta-section">
		<h2>See It In Action</h2>
		<p class="cta-description">
			Explore interactive demos showing VCP in different scenarios.
		</p>
		<div class="cta-grid">
			<a href="/professional" class="cta-card">
				<span class="cta-icon"><i class="fa-solid fa-briefcase" aria-hidden="true"></i></span>
				<h3>Professional Development</h3>
				<p>Enterprise L&D with multi-stakeholder privacy</p>
			</a>
			<a href="/personal" class="cta-card">
				<span class="cta-icon"><i class="fa-solid fa-guitar" aria-hidden="true"></i></span>
				<h3>Personal Growth</h3>
				<p>Cross-platform portability and community privacy</p>
			</a>
			<a href="/demos/multi-agent/negotiation" class="cta-card">
				<span class="cta-icon"><i class="fa-solid fa-robot" aria-hidden="true"></i></span>
				<h3>Multi-Agent Scenarios</h3>
				<p>AI-to-AI negotiation and coordination</p>
			</a>
			<a href="/demos/self-modeling/interiora" class="cta-card">
				<span class="cta-icon"><i class="fa-solid fa-brain" aria-hidden="true"></i></span>
				<h3>AI Self-Modeling</h3>
				<p>Interiora and embodied AI context</p>
			</a>
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
		max-width: 600px;
		margin: 0 auto;
	}

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

	.cta-section {
		text-align: center;
	}

	.cta-description {
		color: var(--color-text-muted);
		margin-bottom: var(--space-xl);
	}

	.cta-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
		gap: var(--space-lg);
	}

	.cta-card {
		display: block;
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		padding: var(--space-xl);
		border: 1px solid rgba(255, 255, 255, 0.1);
		text-decoration: none;
		color: var(--color-text);
		transition: all var(--transition-normal);
	}

	.cta-card:hover {
		border-color: var(--color-primary);
		transform: translateY(-2px);
		text-decoration: none;
	}

	.cta-icon {
		font-size: 2rem;
		display: block;
		margin-bottom: var(--space-md);
	}

	.cta-card h3 {
		margin-bottom: var(--space-xs);
		font-size: 1rem;
	}

	.cta-card p {
		color: var(--color-text-muted);
		font-size: 0.8125rem;
	}

	@media (max-width: 768px) {
		.hero h1 {
			font-size: 1.75rem;
		}

		.how-it-works {
			flex-direction: column;
		}

		.step-arrow {
			transform: rotate(90deg);
			padding: var(--space-sm) 0;
		}
	}
</style>
