<script lang="ts">
	/**
	 * Personal Demo Landing
	 * Shows Gentian's profile and path options
	 */
	import { vcpContext } from '$lib/vcp';
	import { gentianProfile, gentianChallengeProgress } from '$lib/personas/gentian';

	// Load Gentian profile on mount
	$effect(() => {
		vcpContext.set(gentianProfile);
	});

	const ctx = $derived($vcpContext);
	const progress = gentianChallengeProgress;
</script>

<svelte:head>
	<title>Personal Demo - VCP</title>
	<meta name="description" content="See how VCP enables cross-platform portability while protecting personal circumstances from community judgment. Configure once, use everywhere." />
	<meta property="og:title" content="Personal Growth Demo - VCP" />
	<meta property="og:description" content="Follow Gentian learning guitar across platforms. See how VCP protects work schedule and living situation from the community." />
</svelte:head>

<div class="container-narrow">
	<div class="breadcrumb">
		<a href="/demos"><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> All Demos</a>
	</div>

	<header class="demo-header">
		<div class="demo-badge">
			<span class="badge badge-primary">Personal Growth Demo</span>
		</div>
		<h1>Meet Gentian</h1>
		<p class="demo-intro">
			Gentian works factory shifts in Barcelona and is learning guitar for stress relief.
			He practices across multiple platforms — JustinGuitar for lessons, Yousician for exercises,
			and a local community challenge. Each platform adapts to his constraints (shift work schedule,
			thin-walled apartment, limited budget) without knowing the reasons behind them.
		</p>
	</header>

	{#if ctx}
		<section class="profile-card card">
			<div class="profile-header">
				<div class="profile-avatar">🎸</div>
				<div class="profile-info">
					<h2>{ctx.public_profile.display_name}</h2>
					<p class="text-muted">{ctx.public_profile.goal?.replace(/_/g, ' ')}</p>
					<p class="text-subtle text-sm">
						{ctx.public_profile.experience} • {ctx.current_skills?.weeks_learning} weeks learning
					</p>
				</div>
				<div class="vcp-badge">VCP Connected</div>
			</div>

			<div class="profile-details">
				<div class="detail-group">
					<h4>Motivation</h4>
					<p>{ctx.public_profile.motivation?.replace(/_/g, ' ')}</p>
				</div>

				<div class="detail-group">
					<h4>Learning Style</h4>
					<p>{ctx.public_profile.learning_style?.replace(/_/g, ' ')}</p>
				</div>

				<div class="detail-group">
					<h4>Pace</h4>
					<p>{ctx.public_profile.pace}</p>
				</div>
			</div>

			<div class="skills-section">
				<h4>Skills Acquired</h4>
				<div class="skills-list">
					{#each ctx.current_skills?.skills_acquired || [] as skill}
						<span class="skill-tag">{skill.replace(/_/g, ' ')}</span>
					{/each}
				</div>
			</div>

			<div class="constitution-info">
				<span class="text-subtle text-sm">
					Active <span class="has-tooltip" data-tooltip="A constitution defines values and behavioral guidelines that shape how AI interacts with you">Constitution</span>:
				</span>
				<span class="badge badge-primary">{ctx.constitution.id}@{ctx.constitution.version}</span>
				<span class="constitution-persona">
					<span class="has-tooltip" data-tooltip="Muse: AI persona focused on creative growth, inspiration, and gentle encouragement">
						<i class="fa-solid fa-palette" aria-hidden="true"></i> Muse
					</span>
				</span>
			</div>
		</section>

		<section class="constraints-preview card">
			<h3>Private Context (What VCP Knows)</h3>
			<p class="text-muted text-sm constraints-intro">
				These constraints affect recommendations and community participation,
				but are <strong>never</strong> exposed to platforms or other users.
			</p>

			<div class="constraint-flags">
				{#if ctx.constraints?.time_limited}
					<div class="constraint-flag">
						<span class="flag-indicator flag-active"></span>
						<span>Time Limited</span>
						<span class="flag-private">(shift work)</span>
					</div>
				{/if}
				{#if ctx.constraints?.noise_restricted}
					<div class="constraint-flag">
						<span class="flag-indicator flag-active"></span>
						<span>Noise Restricted</span>
						<span class="flag-private">(apartment)</span>
					</div>
				{/if}
				{#if ctx.constraints?.budget_limited}
					<div class="constraint-flag">
						<span class="flag-indicator flag-active"></span>
						<span>Budget Limited</span>
						<span class="flag-private">(factory wages)</span>
					</div>
				{/if}
				{#if ctx.constraints?.energy_variable}
					<div class="constraint-flag">
						<span class="flag-indicator flag-active"></span>
						<span>Energy Variable</span>
						<span class="flag-private">(rotating shifts)</span>
					</div>
				{/if}
				{#if ctx.constraints?.schedule_irregular}
					<div class="constraint-flag">
						<span class="flag-indicator flag-active"></span>
						<span>Schedule Irregular</span>
						<span class="flag-private">(night/day rotation)</span>
					</div>
				{/if}
			</div>

			<div class="privacy-note">
				<span class="privacy-note-icon">🔒</span>
				<span>
					Community members see "18/21 (3 adjusted)" — they don't know <em>why</em> days were adjusted.
					Gentian's work schedule and living situation stay private.
				</span>
			</div>
		</section>

		<section class="challenge-preview card">
			<h3><i class="fa-solid fa-trophy" aria-hidden="true"></i> 30-Day Challenge Progress</h3>
			<div class="challenge-stats">
				<div class="stat">
					<span class="stat-value">{progress.days_completed}</span>
					<span class="stat-label">Days Practiced</span>
				</div>
				<div class="stat">
					<span class="stat-value">{progress.days_adjusted}</span>
					<span class="stat-label">Adjusted</span>
				</div>
				<div class="stat">
					<span class="stat-value">{progress.current_streak}</span>
					<span class="stat-label">Current Streak</span>
				</div>
			</div>
			<div class="progress challenge-progress">
				<div
					class="progress-bar progress-bar-success"
					style="width: {(progress.days_completed / progress.total_days) * 100}%"
				></div>
			</div>
			<p class="text-sm text-muted text-center challenge-rank">
				{progress.days_completed}/{progress.total_days} days • Rank #3 in community
			</p>
		</section>

		<section class="demo-paths">
			<h2>Choose Your Path</h2>
			<div class="grid grid-3 gap-md">
				<a href="/personal/platforms/justinguitar" class="card card-hover path-card">
					<div class="path-icon"><i class="fa-solid fa-mobile-screen" aria-hidden="true"></i></div>
					<h3>Portability Demo</h3>
					<p class="text-muted text-sm">
						Same profile across JustinGuitar and Yousician —
						configure once, use everywhere.
					</p>
					<span class="btn btn-secondary btn-sm path-btn">
						Try Platforms <i class="fa-solid fa-arrow-right" aria-hidden="true"></i>
					</span>
				</a>

				<a href="/personal/platforms/musicshop" class="card card-hover path-card path-card-shop">
					<div class="path-icon"><i class="fa-solid fa-store" aria-hidden="true"></i></div>
					<h3>Physical Retail</h3>
					<p class="text-muted text-sm">
						VCP at a Barcelona guitar shop —
						scan QR code, get personalized gear recs.
					</p>
					<span class="btn btn-secondary btn-sm path-btn">
						Visit Shop <i class="fa-solid fa-arrow-right" aria-hidden="true"></i>
					</span>
				</a>

				<a href="/personal/community" class="card card-hover path-card">
					<div class="path-icon"><i class="fa-solid fa-users" aria-hidden="true"></i></div>
					<h3>Privacy Demo</h3>
					<p class="text-muted text-sm">
						Community challenges with adjusted days —
						participate without exposing personal life.
					</p>
					<span class="btn btn-secondary btn-sm path-btn">
						View Community <i class="fa-solid fa-arrow-right" aria-hidden="true"></i>
					</span>
				</a>
			</div>

			<!-- Coach & Audit Links -->
			<div class="extra-links">
				<a href="/personal/coach" class="btn btn-ghost">
					<i class="fa-solid fa-user-tie" aria-hidden="true"></i>
					Connect with Coach
				</a>
				<a href="/personal/audit" class="btn btn-ghost">
					<i class="fa-solid fa-clipboard-list" aria-hidden="true"></i>
					Unified Audit Trail
				</a>
			</div>
			<p class="text-xs text-muted text-center extra-note">
				See tiered data sharing with a coach, or view all platform data flow
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
		max-width: 600px;
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

	.skills-section {
		margin-bottom: var(--space-lg);
	}

	.skills-section h4 {
		font-size: 0.875rem;
		margin-bottom: var(--space-sm);
	}

	.skills-list {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-xs);
	}

	.skill-tag {
		padding: var(--space-xs) var(--space-sm);
		background: var(--color-success-muted);
		color: var(--color-success);
		border-radius: var(--radius-sm);
		font-size: 0.75rem;
		text-transform: capitalize;
	}

	.constitution-info {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		flex-wrap: wrap;
	}

	.constitution-persona {
		font-size: 0.75rem;
		color: var(--color-primary);
	}

	.constraints-preview {
		margin-bottom: var(--space-lg);
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

	.challenge-preview {
		margin-bottom: var(--space-xl);
	}

	.challenge-preview h3 {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
	}

	.challenge-stats {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: var(--space-md);
		margin-top: var(--space-md);
	}

	.stat {
		text-align: center;
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
	}

	.stat-value {
		display: block;
		font-size: 1.5rem;
		font-weight: 600;
	}

	.stat-label {
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.challenge-progress {
		margin-top: var(--space-md);
	}

	.challenge-rank {
		margin-top: var(--space-sm);
	}

	.demo-paths {
		margin-bottom: var(--space-xl);
	}

	.demo-paths h2 {
		text-align: center;
		margin-bottom: var(--space-lg);
	}

	.path-card {
		display: flex;
		flex-direction: column;
		text-decoration: none;
		color: var(--color-text);
	}

	.path-card:hover {
		text-decoration: none;
	}

	.path-icon {
		font-size: 2.5rem;
		margin-bottom: var(--space-md);
		color: var(--color-primary);
	}

	.path-card h3 {
		margin-bottom: var(--space-sm);
	}

	.path-btn {
		margin-top: auto;
	}

	.extra-links {
		margin-top: var(--space-lg);
		display: flex;
		gap: var(--space-md);
		justify-content: center;
		flex-wrap: wrap;
	}

	.extra-note {
		margin-top: var(--space-sm);
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

		.profile-details,
		.challenge-stats {
			grid-template-columns: 1fr;
		}

		.extra-links {
			flex-direction: column;
			align-items: stretch;
		}
	}
</style>
