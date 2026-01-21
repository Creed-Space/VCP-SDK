<script lang="ts">
	/**
	 * VCP Demo Landing Page
	 * Entry point with demo selector
	 */
	import { HowItWorks } from '$lib/components/shared';
</script>

<svelte:head>
	<title>VCP Demo - Value Context Protocol</title>
</svelte:head>

<div class="container">
	<section class="hero">
		<h1>Value Context Protocol</h1>
		<p class="hero-subtitle">
			Your context. Your control. Private reasons stay private.
		</p>
	</section>

	<section class="demo-selector">
		<h2 class="section-title">Choose Your Demo</h2>
		<p class="section-description">
			Two scenarios showing how VCP protects your privacy while enabling personalized experiences.
		</p>

		<div class="grid grid-2 gap-lg">
			<!-- Professional Demo Card -->
			<a href="/professional" class="card card-hover demo-card demo-card-professional">
				<div class="demo-icon"><i class="fa-solid fa-briefcase" aria-hidden="true"></i></div>
				<h3 class="demo-title">Professional Development</h3>
				<p class="demo-description">
					See how VCP enables enterprise L&D while keeping private life circumstances
					from being exposed to HR. Privacy-preserving career recommendations.
				</p>
				<div class="demo-features">
					<span class="demo-feature">
						<span class="feature-icon"><i class="fa-solid fa-check" aria-hidden="true"></i></span>
						Multi-stakeholder privacy
					</span>
					<span class="demo-feature">
						<span class="feature-icon"><i class="fa-solid fa-check" aria-hidden="true"></i></span>
						Dual audit trail
					</span>
					<span class="demo-feature">
						<span class="feature-icon"><i class="fa-solid fa-check" aria-hidden="true"></i></span>
						Compliance without exposure
					</span>
				</div>
				<div class="demo-cta">
					<span class="btn btn-primary">Start Demo <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></span>
				</div>
			</a>

			<!-- Personal Demo Card -->
			<a href="/personal" class="card card-hover demo-card demo-card-personal">
				<div class="demo-icon"><i class="fa-solid fa-guitar" aria-hidden="true"></i></div>
				<h3 class="demo-title">Personal Growth</h3>
				<p class="demo-description">
					See how VCP enables cross-platform portability while protecting personal
					circumstances from community judgment. Configure once, use everywhere.
				</p>
				<div class="demo-features">
					<span class="demo-feature">
						<span class="feature-icon"><i class="fa-solid fa-check" aria-hidden="true"></i></span>
						Cross-platform portability
					</span>
					<span class="demo-feature">
						<span class="feature-icon"><i class="fa-solid fa-check" aria-hidden="true"></i></span>
						Community privacy
					</span>
					<span class="demo-feature">
						<span class="feature-icon"><i class="fa-solid fa-check" aria-hidden="true"></i></span>
						Configure once, use everywhere
					</span>
				</div>
				<div class="demo-cta">
					<span class="btn btn-primary">Start Demo <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></span>
				</div>
			</a>
		</div>
	</section>

	<HowItWorks />

	<section class="value-props">
		<h2 class="section-title">What VCP Does</h2>
		<div class="grid grid-2 gap-lg">
			<div class="value-card">
				<h4><i class="fa-solid fa-lock" aria-hidden="true"></i> Private Reasons Stay Private</h4>
				<p>
					Your constraints (health, family, work) influence recommendations through boolean flags.
					Platforms see "budget limited: true" not "single parent struggling financially."
				</p>
			</div>
			<div class="value-card">
				<h4><i class="fa-solid fa-mobile-screen" aria-hidden="true"></i> Configure Once, Use Everywhere</h4>
				<p>
					Set your preferences once. Every compatible platform instantly knows how to serve you
					without asking the same questions again.
				</p>
			</div>
			<div class="value-card">
				<h4><i class="fa-solid fa-eye" aria-hidden="true"></i> Full Transparency</h4>
				<p>
					See exactly what each platform received. Audit trails show what was shared, what was
					withheld, and what private context influenced decisions.
				</p>
			</div>
			<div class="value-card">
				<h4><i class="fa-solid fa-handshake" aria-hidden="true"></i> Trust Without Exposure</h4>
				<p>
					Stakeholders (HR, community, coaches) see compliance and progress without accessing your
					personal circumstances. Privacy and accountability coexist.
				</p>
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

	.demo-selector {
		margin-bottom: var(--space-2xl);
	}

	.section-title {
		text-align: center;
		margin-bottom: var(--space-sm);
	}

	.section-description {
		text-align: center;
		color: var(--color-text-muted);
		margin-bottom: var(--space-xl);
		max-width: 600px;
		margin-left: auto;
		margin-right: auto;
	}

	.demo-card {
		display: flex;
		flex-direction: column;
		text-decoration: none;
		color: var(--color-text);
	}

	.demo-card:hover {
		text-decoration: none;
	}

	.demo-card-professional {
		border-color: var(--color-professional);
	}

	.demo-card-professional:hover {
		border-color: var(--color-professional);
		box-shadow: 0 10px 30px rgba(5, 150, 105, 0.2);
	}

	.demo-card-personal {
		border-color: var(--color-primary);
	}

	.demo-card-personal:hover {
		border-color: var(--color-primary);
		box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
	}

	.demo-icon {
		font-size: 3rem;
		margin-bottom: var(--space-md);
	}

	.demo-title {
		font-size: 1.25rem;
		margin-bottom: var(--space-sm);
	}

	.demo-description {
		color: var(--color-text-muted);
		font-size: 0.875rem;
		margin-bottom: var(--space-lg);
		flex: 1;
	}

	.demo-features {
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
		margin-bottom: var(--space-lg);
	}

	.demo-feature {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	.feature-icon {
		color: var(--color-success);
	}

	.demo-cta {
		margin-top: auto;
	}

	.value-props {
		padding-bottom: var(--space-2xl);
	}

	.value-card {
		padding: var(--space-lg);
	}

	.value-card h4 {
		margin-bottom: var(--space-sm);
	}

	.value-card p {
		color: var(--color-text-muted);
		font-size: 0.875rem;
	}

	@media (max-width: 768px) {
		.hero h1 {
			font-size: 1.75rem;
		}

		.hero-subtitle {
			font-size: 1rem;
		}
	}
</style>
