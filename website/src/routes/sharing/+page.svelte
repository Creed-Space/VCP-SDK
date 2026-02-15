<script lang="ts">
	/**
	 * Sharing Category Landing
	 * Privacy-preserving context sharing demos
	 */
</script>

<svelte:head>
	<title>Sharing Demos - VCP</title>
	<meta name="description" content="Privacy-preserving context sharing demos showing how VCP protects your personal context while enabling personalized experiences." />
</svelte:head>

<div class="container">
	<div class="breadcrumb">
		<a href="/demos"><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> All Demos</a>
	</div>

	<section class="page-hero">
		<div class="category-badge category-badge-sharing">
			<i class="fa-solid fa-share-nodes" aria-hidden="true"></i>
		</div>
		<h1>Sharing</h1>
		<p class="page-hero-subtitle">
			Privacy-preserving context sharing between humans and platforms.
			See how VCP lets you share what you want while keeping private reasons private.
		</p>
	</section>

	<section class="demo-grid">
		<a href="/professional" class="demo-card">
			<div class="demo-icon"><i class="fa-solid fa-briefcase" aria-hidden="true"></i></div>
			<div class="demo-content">
				<h2>Professional Development</h2>
				<p>
					Follow Campion, a senior engineer, through a morning of course recommendations.
					See how VCP enables HR compliance without exposing personal circumstances.
				</p>
				<div class="demo-features">
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Multi-stakeholder privacy</span>
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Dual audit trails</span>
				</div>
			</div>
			<span class="btn btn-primary">Start Demo <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></span>
		</a>

		<a href="/personal" class="demo-card">
			<div class="demo-icon" style="color: var(--color-primary)"><i class="fa-solid fa-guitar" aria-hidden="true"></i></div>
			<div class="demo-content">
				<h2>Personal Growth</h2>
				<p>
					Follow Gentian learning guitar across multiple platforms.
					See how VCP carries context without exposing work schedule or living situation.
				</p>
				<div class="demo-features">
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Cross-platform portability</span>
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Community privacy</span>
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
	.demo-icon { font-size: 2rem; color: var(--color-success); flex-shrink: 0; }
	.demo-content { flex: 1; }
	.demo-content h2 { font-size: 1.25rem; margin-bottom: var(--space-sm); }
	.demo-content p { color: var(--color-text-muted); font-size: 0.875rem; margin-bottom: var(--space-md); line-height: 1.6; }
	.demo-features { display: flex; flex-wrap: wrap; gap: var(--space-sm); }
	.feature { font-size: 0.75rem; color: var(--color-text-muted); display: flex; align-items: center; gap: var(--space-xs); }
	.feature i { color: var(--color-success); }
	@media (max-width: 768px) { .demo-card { flex-direction: column; text-align: center; } .demo-features { justify-content: center; } }
</style>
