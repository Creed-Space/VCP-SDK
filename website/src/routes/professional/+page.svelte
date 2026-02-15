<script lang="ts">
	/**
	 * Professional Demo Landing
	 * Shows Campion's profile and entry to morning journey
	 */
	import { vcpContext } from '$lib/vcp';
	import { campionProfile, workConstitution, personalConstitution } from '$lib/personas/campion';
	import { Breadcrumb } from '$lib/components/shared';

	const breadcrumbItems = [
		{ label: 'Demos', href: '/demos' },
		{ label: 'Professional', icon: 'fa-briefcase' }
	];

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
	<Breadcrumb items={breadcrumbItems} />

	<header class="demo-header">
		<div class="demo-badge">
			<span class="badge badge-success">Professional Development Demo</span>
		</div>
		<h1>Meet Campion</h1>
		<p class="demo-intro">
			Campion is a senior software engineer at TechCorp, working toward becoming a Tech Lead.
			She's on track for promotion in 12 months — but what HR doesn't need to know is that
			she's also navigating personal circumstances that affect when and how she can study.
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
				<h4>
					Dual <span class="has-tooltip" data-tooltip="A values profile defines behavioral guidelines that shape how AI interacts with you in different contexts">Values Profiles</span>
				</h4>
				<div class="constitution-badges">
					<div class="constitution-badge constitution-badge-active">
						<span class="badge badge-primary">Work</span>
						<span class="constitution-name">Professional mode</span>
						<span class="constitution-persona">
							<span class="has-tooltip" data-tooltip="Ambassador: Represents your professional interests, sharing only work-appropriate information with HR and colleagues">Ambassador</span>
						</span>
					</div>
					<div class="constitution-badge">
						<span class="badge badge-warning">Personal</span>
						<span class="constitution-name">Home mode</span>
						<span class="constitution-persona">
							<span class="has-tooltip" data-tooltip="Godparent: Focused on your wellbeing, providing supportive guidance and protecting personal boundaries">Godparent</span>
						</span>
					</div>
				</div>
				<p class="text-sm text-muted constitution-note">
					VCP switches automatically: Work profile during office hours, Personal profile at home.
				</p>
			</div>
		</section>

		<section class="constraints-preview card">
			<h3>Private Context (What VCP Knows)</h3>
			<p class="text-muted text-sm constraints-intro">
				These constraints influence recommendations but are <strong>never</strong> exposed to platforms or HR.
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

			<div class="privacy-note">
				<span class="privacy-note-icon">🔒</span>
				<span>
					HR and platforms see boolean flags only. They know constraints exist but not <em>why</em>.
					The reasons (family situation, health details) stay with Campion.
				</span>
			</div>
		</section>

		<section class="journey-start">
			<h3>Choose a Journey</h3>
			<div class="journey-options">
				<a href="/professional/morning" class="journey-card">
					<span class="journey-icon"><i class="fa-solid fa-sun" aria-hidden="true"></i></span>
					<span class="journey-title">Morning at Work</span>
					<span class="journey-desc">Course recommendations from L&D</span>
					<span class="journey-constitution">Work profile active</span>
				</a>
				<a href="/professional/evening" class="journey-card journey-card-evening">
					<span class="journey-icon"><i class="fa-solid fa-moon" aria-hidden="true"></i></span>
					<span class="journey-title">Evening at Home</span>
					<span class="journey-desc">Wellbeing check-in</span>
					<span class="journey-constitution">Personal profile active</span>
				</a>
				<a href="/professional/conflict" class="journey-card journey-card-conflict">
					<span class="journey-icon"><i class="fa-solid fa-bolt" aria-hidden="true"></i></span>
					<span class="journey-title">Work-Life Clash</span>
					<span class="journey-desc">When boundaries are tested</span>
					<span class="journey-constitution">Both profiles involved</span>
				</a>
			</div>
			<p class="text-muted text-sm journey-note">
				Each journey shows how different profiles protect different boundaries
			</p>
		</section>
	{:else}
		<div class="loading">Loading profile...</div>
	{/if}
</div>

<style>
	.demo-header {
		text-align: center;
		margin-bottom: var(--space-xl);
	}

	.demo-badge {
		margin-bottom: var(--space-md);
	}

	.demo-intro {
		color: var(--color-text-muted);
		max-width: 550px;
		margin: var(--space-md) auto 0;
		line-height: 1.6;
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

	.constitution-info h4 {
		font-size: 0.75rem;
		text-transform: uppercase;
		color: var(--color-text-subtle);
		margin-bottom: var(--space-sm);
	}

	.constitution-badges {
		display: flex;
		gap: var(--space-md);
	}

	.constitution-badge {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		padding: var(--space-sm);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		opacity: 0.6;
	}

	.constitution-badge-active {
		opacity: 1;
		border: 1px solid var(--color-primary);
	}

	.constitution-name {
		font-family: var(--font-mono);
		font-size: 0.6875rem;
		color: var(--color-text-muted);
		margin-top: var(--space-xs);
	}

	.constitution-persona {
		font-size: 0.75rem;
		text-transform: capitalize;
	}

	.constitution-note {
		margin-top: var(--space-sm);
	}

	.constraints-preview {
		margin-bottom: var(--space-xl);
	}

	.constraints-intro {
		margin-bottom: var(--space-md);
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

	.privacy-note {
		margin-top: var(--space-md);
	}

	.journey-start {
		text-align: center;
		padding: var(--space-xl) 0;
	}

	.journey-start h3 {
		margin-bottom: var(--space-lg);
	}

	.journey-card {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-lg);
		text-decoration: none;
		color: var(--color-text);
		min-width: 160px;
		transition: all var(--transition-normal);
	}

	.journey-card:hover {
		border-color: var(--color-primary);
		transform: translateY(-2px);
		text-decoration: none;
	}

	.journey-card-evening {
		border-color: var(--color-warning);
	}

	.journey-card-evening:hover {
		border-color: var(--color-warning);
		box-shadow: 0 0 20px rgba(234, 179, 8, 0.2);
	}

	.journey-icon {
		font-size: 2rem;
		margin-bottom: var(--space-sm);
		color: var(--color-primary);
	}

	.journey-card-evening .journey-icon {
		color: var(--color-warning);
	}

	.journey-title {
		font-weight: 600;
		margin-bottom: var(--space-xs);
	}

	.journey-desc {
		font-size: 0.75rem;
		color: var(--color-text-muted);
		margin-bottom: var(--space-sm);
	}

	.journey-constitution {
		font-size: 0.6875rem;
		padding: 2px 8px;
		background: var(--color-primary-muted);
		color: var(--color-primary);
		border-radius: var(--radius-sm);
	}

	.journey-card-evening .journey-constitution {
		background: var(--color-warning-muted);
		color: var(--color-warning);
	}

	.journey-card-conflict {
		border-color: var(--color-danger);
	}

	.journey-card-conflict:hover {
		border-color: var(--color-danger);
		box-shadow: 0 0 20px rgba(239, 68, 68, 0.2);
	}

	.journey-card-conflict .journey-icon {
		color: var(--color-danger);
	}

	.journey-card-conflict .journey-constitution {
		background: var(--color-danger-muted);
		color: var(--color-danger);
	}

	.journey-note {
		margin-top: var(--space-md);
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

		.constitution-badges {
			flex-direction: column;
		}
	}
</style>
