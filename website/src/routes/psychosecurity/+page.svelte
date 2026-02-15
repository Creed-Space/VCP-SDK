<script lang="ts">
</script>

<svelte:head>
	<title>Psychosecurity Demos - VCP</title>
	<meta name="description" content="Psychosecurity demos showing how VCP context protects against manipulation and dark patterns." />
</svelte:head>

<div class="container">
	<div class="breadcrumb">
		<a href="/demos"><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> All Demos</a>
	</div>

	<section class="page-hero">
		<div class="category-badge category-badge-psychosecurity"><i class="fa-solid fa-shield-heart" aria-hidden="true"></i></div>
		<h1>Psychosecurity</h1>
		<p class="page-hero-subtitle">Context protecting against manipulation. See how VCP shields users from dark patterns and exploitative design.</p>
	</section>

	<section class="demo-grid">
		<a href="/demos/safety/attention-protection" class="demo-card">
			<div class="demo-icon"><i class="fa-solid fa-bell-slash" aria-hidden="true"></i></div>
			<div class="demo-content">
				<h2>Attention Protection</h2>
				<p>See how VCP helps protect your attention from infinite scroll, notification spam, and engagement hacking.</p>
				<div class="demo-features">
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Pattern detection</span>
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Boundary enforcement</span>
				</div>
			</div>
			<span class="btn btn-primary">Start Demo <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></span>
		</a>

		<a href="/demos/safety/mental-health" class="demo-card">
			<div class="demo-icon" style="color: var(--color-success)"><i class="fa-solid fa-hand-holding-heart" aria-hidden="true"></i></div>
			<div class="demo-content">
				<h2>Mental Health Context</h2>
				<p>Explore how VCP can carry mental health context to enable supportive, non-harmful interactions.</p>
				<div class="demo-features">
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Sensitive context handling</span>
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Harm prevention</span>
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
	.demo-icon { font-size: 2rem; color: var(--color-primary); flex-shrink: 0; }
	.demo-content { flex: 1; }
	.demo-content h2 { font-size: 1.25rem; margin-bottom: var(--space-sm); }
	.demo-content p { color: var(--color-text-muted); font-size: 0.875rem; margin-bottom: var(--space-md); line-height: 1.6; }
	.demo-features { display: flex; flex-wrap: wrap; gap: var(--space-sm); }
	.feature { font-size: 0.75rem; color: var(--color-text-muted); display: flex; align-items: center; gap: var(--space-xs); }
	.feature i { color: var(--color-success); }
	@media (max-width: 768px) { .demo-card { flex-direction: column; text-align: center; } .demo-features { justify-content: center; } }
</style>
