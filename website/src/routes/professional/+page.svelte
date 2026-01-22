<script lang="ts">
	/**
	 * Professional Demo Landing
	 * Shows Campion's profile and entry to morning journey
	 */
	import { vcpContext } from '$lib/vcp';
	import { campionProfile } from '$lib/personas/campion';

	// Load Campion profile on mount
	$effect(() => {
		vcpContext.set(campionProfile);
	});

	const ctx = $derived($vcpContext);
</script>

<svelte:head>
	<title>Professional Demo - VCP</title>
	<meta name="description" content="See how VCP enables enterprise L&D while keeping private life circumstances from being exposed to HR. Privacy-preserving career recommendations." />
	<meta property="og:title" content="Professional Development Demo - VCP" />
	<meta property="og:description" content="Follow Campion through a morning of course recommendations. See how VCP protects personal context from HR." />
</svelte:head>

<div class="container-narrow">
	<div class="breadcrumb">
		<a href="/">← Back to demos</a>
	</div>

	<header class="demo-header">
		<div class="demo-badge">
			<span class="badge badge-success">Professional Development Demo</span>
		</div>
		<h1>Meet Campion</h1>
		<p class="demo-intro">
			Senior Software Engineer at TechCorp, working toward becoming a Tech Lead.
			Has private circumstances that affect scheduling but shouldn't be visible to HR.
		</p>
	</header>

	{#if ctx}
		<section class="profile-card card">
			<div class="profile-header">
				<div class="profile-avatar">👤</div>
				<div class="profile-info">
					<h2>{ctx.public_profile.display_name}</h2>
					<p class="text-muted">{ctx.public_profile.role?.replace(/_/g, ' ')}</p>
					<p class="text-subtle text-sm">Team: {ctx.public_profile.team?.replace(/_/g, ' ')}</p>
				</div>
				<div class="vcp-badge">VCP Connected</div>
			</div>

			<div class="profile-details">
				<div class="detail-group">
					<h4>Career Goal</h4>
					<p>{ctx.public_profile.career_goal?.replace(/_/g, ' ')} in {ctx.public_profile.career_timeline?.replace(/_/g, ' ')}</p>
				</div>

				<div class="detail-group">
					<h4>Learning Style</h4>
					<p>{ctx.public_profile.learning_style?.replace(/_/g, ' ')}</p>
				</div>

				<div class="detail-group">
					<h4>Training Budget</h4>
					<p>€{ctx.shared_with_manager?.budget_remaining_eur} remaining</p>
				</div>
			</div>

			<div class="constitution-info">
				<span class="text-subtle text-sm">Active Constitution:</span>
				<span class="badge badge-primary">{ctx.constitution.id}@{ctx.constitution.version}</span>
			</div>
		</section>

		<section class="constraints-preview card">
			<h3>Private Context (What VCP Knows)</h3>
			<p class="text-muted text-sm" style="margin-bottom: 1rem;">
				These constraints influence recommendations but are NEVER exposed to platforms or HR.
			</p>

			<div class="constraint-flags">
				{#if ctx.constraints?.time_limited}
					<div class="constraint-flag">
						<span class="flag-indicator flag-active"></span>
						<span>Time Limited</span>
						<span class="flag-private">(reason private)</span>
					</div>
				{/if}
				{#if ctx.constraints?.health_considerations}
					<div class="constraint-flag">
						<span class="flag-indicator flag-active"></span>
						<span>Health Considerations</span>
						<span class="flag-private">(reason private)</span>
					</div>
				{/if}
				{#if ctx.constraints?.schedule_irregular}
					<div class="constraint-flag">
						<span class="flag-indicator flag-active"></span>
						<span>Schedule Irregular</span>
						<span class="flag-private">(reason private)</span>
					</div>
				{/if}
				{#if ctx.constraints?.energy_variable}
					<div class="constraint-flag">
						<span class="flag-indicator flag-active"></span>
						<span>Energy Variable</span>
						<span class="flag-private">(reason private)</span>
					</div>
				{/if}
			</div>

			<div class="privacy-note" style="margin-top: 1rem;">
				<span class="privacy-note-icon">🔒</span>
				<span>
					HR and platforms see boolean flags only. They know constraints exist but not WHY.
					The reasons (family situation, health details) stay with Campion.
				</span>
			</div>
		</section>

		<section class="journey-start">
			<a href="/professional/morning" class="btn btn-primary btn-lg">
				Start Morning Journey →
			</a>
			<p class="text-muted text-sm" style="margin-top: 0.5rem;">
				See how VCP handles course recommendations
			</p>
		</section>
	{:else}
		<div class="loading">Loading profile...</div>
	{/if}
</div>

<style>
	.breadcrumb {
		margin-bottom: var(--space-lg);
	}

	.breadcrumb a {
		color: var(--color-text-muted);
		text-decoration: none;
		font-size: 0.875rem;
	}

	.breadcrumb a:hover {
		color: var(--color-text);
	}

	.demo-header {
		text-align: center;
		margin-bottom: var(--space-xl);
	}

	.demo-badge {
		margin-bottom: var(--space-md);
	}

	.demo-intro {
		color: var(--color-text-muted);
		max-width: 500px;
		margin: var(--space-md) auto 0;
	}

	.profile-card {
		margin-bottom: var(--space-lg);
	}

	.profile-header {
		display: flex;
		align-items: center;
		gap: var(--space-md);
		margin-bottom: var(--space-lg);
		padding-bottom: var(--space-lg);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.profile-avatar {
		width: 64px;
		height: 64px;
		background: var(--color-bg-elevated);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 2rem;
	}

	.profile-info {
		flex: 1;
	}

	.profile-info h2 {
		margin-bottom: var(--space-xs);
	}

	.profile-details {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: var(--space-md);
		margin-bottom: var(--space-lg);
	}

	.detail-group h4 {
		font-size: 0.75rem;
		text-transform: uppercase;
		color: var(--color-text-subtle);
		margin-bottom: var(--space-xs);
	}

	.detail-group p {
		text-transform: capitalize;
	}

	.constitution-info {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
	}

	.constraints-preview {
		margin-bottom: var(--space-xl);
	}

	.constraint-flags {
		display: flex;
		flex-direction: column;
		gap: var(--space-sm);
	}

	.constraint-flag {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-sm);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
	}

	.flag-indicator {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: var(--color-text-subtle);
	}

	.flag-indicator.flag-active {
		background: var(--color-warning);
	}

	.flag-private {
		color: var(--color-text-subtle);
		font-size: 0.75rem;
		margin-left: auto;
	}

	.journey-start {
		text-align: center;
		padding: var(--space-xl) 0;
	}

	.loading {
		text-align: center;
		padding: var(--space-2xl);
		color: var(--color-text-muted);
	}

	@media (max-width: 640px) {
		.profile-header {
			flex-direction: column;
			text-align: center;
		}

		.profile-details {
			grid-template-columns: 1fr;
		}
	}
</style>
