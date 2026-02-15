<script lang="ts">
</script>

<svelte:head>
	<title>Coordination Demos - VCP</title>
	<meta name="description" content="AI agent coordination demos showing how multiple agents negotiate and collaborate using shared VCP context." />
</svelte:head>

<div class="container">
	<div class="breadcrumb">
		<a href="/demos"><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> All Demos</a>
	</div>

	<section class="page-hero">
		<div class="category-badge category-badge-coordination"><i class="fa-solid fa-handshake" aria-hidden="true"></i></div>
		<h1>Coordination</h1>
		<p class="page-hero-subtitle">AI agents negotiating with mutual VCP context. See how shared context enables better multi-agent collaboration.</p>
	</section>

	<section class="demo-grid">
		<a href="/demos/multi-agent/auction" class="demo-card">
			<div class="demo-icon"><i class="fa-solid fa-gavel" aria-hidden="true"></i></div>
			<div class="demo-content">
				<h2>Multi-Agent Auction</h2>
				<p>Watch AI agents bid in an auction while respecting each other's constraints and preferences through VCP context.</p>
				<div class="demo-features">
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Real-time bidding</span>
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Constraint-aware agents</span>
				</div>
			</div>
			<span class="btn btn-primary">Start Demo <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></span>
		</a>

		<a href="/demos/multi-agent/negotiation" class="demo-card">
			<div class="demo-icon"><i class="fa-solid fa-comments" aria-hidden="true"></i></div>
			<div class="demo-content">
				<h2>Negotiation</h2>
				<p>See how agents negotiate agreements while maintaining private strategic context through VCP.</p>
				<div class="demo-features">
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Private strategies</span>
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Mutual benefit finding</span>
				</div>
			</div>
			<span class="btn btn-primary">Start Demo <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></span>
		</a>

		<a href="/demos/multi-agent/policy-design" class="demo-card">
			<div class="demo-icon"><i class="fa-solid fa-landmark" aria-hidden="true"></i></div>
			<div class="demo-content">
				<h2>Policy Design</h2>
				<p>Explore how multiple stakeholders can design policies together using VCP to represent diverse values.</p>
				<div class="demo-features">
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Multi-stakeholder input</span>
					<span class="feature"><i class="fa-solid fa-check" aria-hidden="true"></i> Value alignment</span>
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
	.demo-icon { font-size: 2rem; color: #3b82f6; flex-shrink: 0; }
	.demo-content { flex: 1; }
	.demo-content h2 { font-size: 1.25rem; margin-bottom: var(--space-sm); }
	.demo-content p { color: var(--color-text-muted); font-size: 0.875rem; margin-bottom: var(--space-md); line-height: 1.6; }
	.demo-features { display: flex; flex-wrap: wrap; gap: var(--space-sm); }
	.feature { font-size: 0.75rem; color: var(--color-text-muted); display: flex; align-items: center; gap: var(--space-xs); }
	.feature i { color: var(--color-success); }
	@media (max-width: 768px) { .demo-card { flex-direction: column; text-align: center; } .demo-features { justify-content: center; } }
</style>
