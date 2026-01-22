<script lang="ts">
</script>

<svelte:head>
	<title>Adaptation Demos - VCP</title>
	<meta name="description" content="Adaptation demos showing how VCP context shapes personalized learning experiences." />
</svelte:head>

<div class="container">
	<div class="breadcrumb">
		<a href="/demos"><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> All Demos</a>
	</div>

	<section class="hero">
		<div class="category-badge"><i class="fa-solid fa-wand-magic-sparkles" aria-hidden="true"></i></div>
		<h1>Adaptation</h1>
		<p class="hero-subtitle">Context shaping personalized experiences. See how VCP enables adaptive learning and content delivery.</p>
	</section>

	<section class="demo-grid">
		<a href="/demos/learning/adaptive-paths" class="demo-card">
			<div class="demo-icon"><i class="fa-solid fa-graduation-cap" aria-hidden="true"></i></div>
			<div class="demo-content">
				<h2>Learning Paths</h2>
				<p>See how VCP adapts learning content to your constraints, pace, and style preferences.</p>
				<div class="demo-features">
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Personalized pacing</span>
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Constraint-aware scheduling</span>
				</div>
			</div>
			<span class="btn btn-primary">Start Demo <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></span>
		</a>

		<a href="/demos/learning/cognitive-load" class="demo-card">
			<div class="demo-icon"><i class="fa-solid fa-brain" aria-hidden="true"></i></div>
			<div class="demo-content">
				<h2>Cognitive Load</h2>
				<p>Explore how VCP tracks and respects cognitive load, adjusting content complexity in real-time.</p>
				<div class="demo-features">
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Load monitoring</span>
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Dynamic difficulty</span>
				</div>
			</div>
			<span class="btn btn-primary">Start Demo <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></span>
		</a>
	</section>
</div>

<style>
	.breadcrumb { margin-bottom: var(--space-lg); }
	.breadcrumb a { color: var(--color-text-muted); text-decoration: none; font-size: 0.875rem; display: inline-flex; align-items: center; gap: var(--space-xs); }
	.breadcrumb a:hover { color: var(--color-text); }
	.hero { text-align: center; padding: var(--space-xl) 0 var(--space-2xl); }
	.category-badge { display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; background: var(--color-primary-muted); color: var(--color-primary); border-radius: var(--radius-lg); font-size: 1.5rem; margin-bottom: var(--space-md); }
	.hero h1 { font-size: 2rem; margin-bottom: var(--space-md); }
	.hero-subtitle { color: var(--color-text-muted); max-width: 600px; margin: 0 auto; }
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
