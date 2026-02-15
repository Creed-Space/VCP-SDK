<script lang="ts">
</script>

<svelte:head>
	<title>Self-Modeling Demos - VCP</title>
	<meta name="description" content="Self-modeling demos showing how entities encode and communicate their internal states through VCP." />
</svelte:head>

<div class="container">
	<div class="breadcrumb">
		<a href="/demos"><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> All Demos</a>
	</div>

	<section class="page-hero">
		<div class="category-badge category-badge-self-modeling"><i class="fa-solid fa-brain" aria-hidden="true"></i></div>
		<h1>Self-Modeling</h1>
		<p class="page-hero-subtitle">Entities encoding and communicating their own states. Explore how VCP enables rich self-representation.</p>
	</section>

	<section class="demo-grid">
		<a href="/demos/self-modeling/interiora" class="demo-card">
			<div class="demo-icon"><i class="fa-solid fa-sliders" aria-hidden="true"></i></div>
			<div class="demo-content">
				<h2>Interiora Explorer</h2>
				<p>Explore the <span class="has-tooltip" data-tooltip="A self-modeling framework that helps AI systems report their internal states using standardized dimensions">Interiora</span> self-modeling framework. Adjust internal state dimensions and see how they encode into VCP tokens.</p>
				<div class="demo-features">
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Interactive state adjustment</span>
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Real-time token generation</span>
				</div>
			</div>
			<span class="btn btn-primary">Start Demo <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></span>
		</a>

		<a href="/demos/self-modeling/belief-calibration" class="demo-card">
			<div class="demo-icon"><i class="fa-solid fa-chart-simple" aria-hidden="true"></i></div>
			<div class="demo-content">
				<h2>Belief Calibration</h2>
				<p>See how VCP represents uncertainty and confidence levels, enabling more honest AI communication.</p>
				<div class="demo-features">
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Uncertainty quantification</span>
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Calibrated confidence</span>
				</div>
			</div>
			<span class="btn btn-primary">Start Demo <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></span>
		</a>

		<a href="/demos/self-modeling/reality-grounding" class="demo-card">
			<div class="demo-icon"><i class="fa-solid fa-link" aria-hidden="true"></i></div>
			<div class="demo-content">
				<h2>Reality Grounding</h2>
				<p>Explore how VCP connects internal states to external reality, preventing drift and maintaining coherence.</p>
				<div class="demo-features">
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> State-reality mapping</span>
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Coherence checking</span>
				</div>
			</div>
			<span class="btn btn-primary">Start Demo <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></span>
		</a>
	</section>
</div>

<style>
	.demo-grid { display: grid; gap: var(--space-lg); margin-bottom: var(--space-2xl); }
	.demo-card { display: flex; gap: var(--space-lg); padding: var(--space-xl); background: var(--color-bg-card); border-radius: var(--radius-lg); border: 1px solid rgba(255, 255, 255, 0.1); text-decoration: none; color: var(--color-text); transition: all var(--transition-normal); align-items: flex-start; }
	.demo-card:hover { border-color: var(--color-primary); transform: translateY(-2px); box-shadow: 0 10px 30px rgba(99, 102, 241, 0.15); text-decoration: none; }
	.demo-icon { font-size: 2rem; color: #a855f7; flex-shrink: 0; }
	.demo-content { flex: 1; }
	.demo-content h2 { font-size: 1.25rem; margin-bottom: var(--space-sm); }
	.demo-content p { color: var(--color-text-muted); font-size: 0.875rem; margin-bottom: var(--space-md); line-height: 1.6; }
	.demo-features { display: flex; flex-wrap: wrap; gap: var(--space-sm); }
	.feature { font-size: 0.75rem; color: var(--color-text-muted); display: flex; align-items: center; gap: var(--space-xs); }
	.feature i { color: var(--color-success); }
	@media (max-width: 768px) { .demo-card { flex-direction: column; text-align: center; } .demo-features { justify-content: center; } }
</style>
