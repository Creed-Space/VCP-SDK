<script lang="ts">
	/**
	 * Yousician Mock Platform
	 * Shows cross-platform sync and different UI
	 */
	import { vcpContext, vcpConsents, logContextShared } from '$lib/vcp';
	import { gentianProfile } from '$lib/personas/gentian';
	import lessonsData from '$lib/data/lessons.json';
	import { TokenInspector } from '$lib/components/shared';

	// Ensure profile is loaded
	$effect(() => {
		if (!$vcpContext) {
			vcpContext.set(gentianProfile);
		}
	});

	const ctx = $derived($vcpContext);
	let showSyncBanner = $state(true);

	// Check if consent exists (or auto-grant since we're simulating)
	$effect(() => {
		if (!vcpConsents.hasConsent('yousician')) {
			vcpConsents.grantConsent(
				'yousician',
				['skill_level', 'pace'],
				['pressure_tolerance', 'noise_mode']
			);

			logContextShared(
				'yousician',
				['skill_level', 'pace', 'noise_mode', 'skills_acquired', 'display_name'],
				['work_type', 'schedule', 'housing', 'neighbor_situation'],
				2
			);
		}
	});

	// Get lessons, filter for quiet if needed
	const lessons = $derived(() => {
		if (ctx?.constraints?.noise_restricted) {
			return lessonsData.yousician_lessons.filter(
				(l) => l.quiet_friendly || l.alternative_quiet
			);
		}
		return lessonsData.yousician_lessons;
	});

	// Skills synced from JustinGuitar
	const syncedSkills = $derived(() => {
		return ctx?.current_skills?.skills_acquired?.slice(0, 4) || [];
	});
</script>

<svelte:head>
	<title>Yousician - VCP Demo</title>
</svelte:head>

<div class="platform-frame platform-frame-yousician">
	<div class="platform-header platform-header-yousician">
		<div class="platform-brand">
			<span class="platform-logo">🎮</span>
			<span class="platform-name">Yousician</span>
		</div>
		<div class="vcp-badge">VCP Connected + Synced</div>
	</div>

	<div class="platform-content">
		{#if ctx}
			<!-- Sync Banner -->
			{#if showSyncBanner}
				<div class="sync-banner">
					<div class="sync-content">
						<span class="sync-icon">🔄</span>
						<div>
							<strong>Skills Synced from JustinGuitar!</strong>
							<p class="text-sm">
								We found {syncedSkills().length} skills you've already learned. You can skip the basics!
							</p>
						</div>
					</div>
					<button class="btn btn-ghost btn-sm" onclick={() => (showSyncBanner = false)}>
						Dismiss
					</button>
				</div>
			{/if}

			<div class="welcome-banner">
				<h1>Ready to play, {ctx.public_profile.display_name}?</h1>
				<p class="text-muted">
					Level: {ctx.public_profile.experience} • Pace: {ctx.public_profile.pace}
				</p>
			</div>

			<!-- Synced Skills -->
			<section class="synced-skills card">
				<h3>🎯 Your Skills (Via VCP)</h3>
				<div class="skills-grid">
					{#each syncedSkills() as skill}
						<div class="skill-item">
							<span class="skill-check">✓</span>
							<span>{skill.replace(/_/g, ' ')}</span>
						</div>
					{/each}
				</div>
				<p class="text-sm text-muted" style="margin-top: 1rem;">
					These skills were imported from your VCP profile - no need to prove them again!
				</p>
			</section>

			<!-- Gamified challenges -->
			<section class="challenges-section">
				<h2>🏆 Today's Challenges</h2>
				<div class="challenge-cards">
					<div class="challenge-card">
						<div class="challenge-icon">🎸</div>
						<h3>Chord Hero: G C D</h3>
						<p class="text-sm text-muted">Rock out with chords you know!</p>
						<div class="challenge-reward">
							<span>🌟 +50 XP</span>
						</div>
						<button class="btn btn-primary">Play Now</button>
					</div>

					<div class="challenge-card">
						<div class="challenge-icon">🎵</div>
						<h3>Rhythm Challenge</h3>
						<p class="text-sm text-muted">Test your timing skills</p>
						<div class="challenge-reward">
							<span>🌟 +30 XP</span>
						</div>
						<button class="btn btn-secondary">Play Now</button>
					</div>

					{#if ctx.constraints?.noise_restricted}
						<div class="challenge-card quiet-mode">
							<div class="challenge-icon">🎧</div>
							<h3>Tone Trainer Mode</h3>
							<p class="text-sm text-muted">
								Practice with headphones - perfect for your quiet setting!
							</p>
							<div class="challenge-reward">
								<span class="badge badge-success">🔇 Quiet Friendly</span>
							</div>
							<button class="btn btn-primary">Start Training</button>
						</div>
					{/if}
				</div>
			</section>

			<!-- Lessons -->
			<section class="lessons-section">
				<h2>📚 Lessons for You</h2>
				<div class="lessons-grid">
					{#each lessons() as lesson}
						<div class="lesson-card">
							<div class="lesson-header">
								<h3>{lesson.title}</h3>
								<span class="badge badge-primary">{lesson.module}</span>
							</div>
							<p class="text-sm text-muted">{lesson.description}</p>
							<div class="lesson-meta">
								<span>⏱️ {lesson.duration_minutes} min</span>
								{#if lesson.quiet_friendly}
									<span class="badge badge-success text-xs">🔇 Quiet OK</span>
								{:else if lesson.alternative_quiet}
									<span class="badge badge-warning text-xs">
										🎧 {lesson.alternative_quiet}
									</span>
								{/if}
							</div>
						</div>
					{/each}
				</div>
			</section>

			<!-- What was shared -->
			<section class="shared-info card">
				<h3>What Yousician Received</h3>
				<div class="shared-comparison">
					<div class="shared-column">
						<h4 class="text-success">Shared:</h4>
						<div class="field-list">
							<span class="field-tag field-tag-shared">skill_level</span>
							<span class="field-tag field-tag-shared">skills_acquired</span>
							<span class="field-tag field-tag-shared">pace</span>
							<span class="field-tag field-tag-shared">noise_mode</span>
							<span class="field-tag field-tag-shared">display_name</span>
						</div>
					</div>
					<div class="shared-column">
						<h4 class="text-danger">Not Shared:</h4>
						<div class="field-list">
							<span class="field-tag field-tag-withheld">work_type</span>
							<span class="field-tag field-tag-withheld">schedule</span>
							<span class="field-tag field-tag-withheld">housing</span>
							<span class="field-tag field-tag-withheld">neighbor_situation</span>
						</div>
					</div>
				</div>
				<div class="privacy-note" style="margin-top: 1rem;">
					<span class="privacy-note-icon">🔄</span>
					<span>
						Same VCP profile, different platform. Your skills transferred, your privacy remained.
					</span>
				</div>
			</section>

			<!-- VCP Token Inspector -->
			<section class="token-section">
				<TokenInspector context={ctx} showLegend={true} showSummary={true} />
			</section>
		{/if}
	</div>
</div>

<div class="container-narrow" style="margin-top: 2rem;">
	<div class="nav-links">
		<a href="/personal/platforms/justinguitar" class="btn btn-ghost">← JustinGuitar</a>
		<a href="/personal/community" class="btn btn-primary">
			View Community →
		</a>
	</div>
</div>

<style>
	.platform-brand {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
	}

	.platform-logo {
		font-size: 1.5rem;
	}

	.platform-name {
		font-weight: 600;
		color: var(--color-yousician);
	}

	.sync-banner {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: var(--space-md);
		background: linear-gradient(135deg, rgba(123, 104, 238, 0.2), rgba(99, 102, 241, 0.2));
		border: 1px solid var(--color-yousician);
		border-radius: var(--radius-md);
		margin-bottom: var(--space-xl);
	}

	.sync-content {
		display: flex;
		align-items: flex-start;
		gap: var(--space-md);
	}

	.sync-icon {
		font-size: 1.5rem;
	}

	.welcome-banner {
		margin-bottom: var(--space-xl);
	}

	.welcome-banner h1 {
		color: var(--color-yousician);
	}

	.synced-skills {
		margin-bottom: var(--space-xl);
	}

	.skills-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: var(--space-sm);
		margin-top: var(--space-md);
	}

	.skill-item {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-sm);
		background: var(--color-success-muted);
		border-radius: var(--radius-sm);
		font-size: 0.875rem;
		text-transform: capitalize;
	}

	.skill-check {
		color: var(--color-success);
		font-weight: bold;
	}

	.challenges-section {
		margin-bottom: var(--space-xl);
	}

	.challenge-cards {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: var(--space-md);
		margin-top: var(--space-md);
	}

	.challenge-card {
		background: var(--color-bg-elevated);
		border-radius: var(--radius-lg);
		padding: var(--space-lg);
		text-align: center;
		border: 1px solid rgba(255, 255, 255, 0.1);
		transition: all var(--transition-normal);
	}

	.challenge-card:hover {
		border-color: var(--color-yousician);
		transform: translateY(-2px);
	}

	.challenge-card.quiet-mode {
		border-color: var(--color-success);
		background: var(--color-success-muted);
	}

	.challenge-icon {
		font-size: 2.5rem;
		margin-bottom: var(--space-md);
	}

	.challenge-reward {
		margin: var(--space-md) 0;
		color: var(--color-warning);
	}

	.lessons-section {
		margin-bottom: var(--space-xl);
	}

	.lessons-grid {
		display: grid;
		gap: var(--space-md);
		margin-top: var(--space-md);
	}

	.lesson-card {
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		padding: var(--space-md);
	}

	.lesson-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: var(--space-sm);
	}

	.lesson-meta {
		display: flex;
		gap: var(--space-md);
		font-size: 0.875rem;
		color: var(--color-text-muted);
		margin-top: var(--space-sm);
	}

	.shared-info {
		margin-bottom: var(--space-xl);
	}

	.shared-comparison {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--space-lg);
		margin-top: var(--space-md);
	}

	.shared-column h4 {
		font-size: 0.875rem;
		margin-bottom: var(--space-sm);
	}

	.text-success {
		color: var(--color-success);
	}

	.text-danger {
		color: var(--color-danger);
	}

	.nav-links {
		display: flex;
		justify-content: space-between;
	}

	.token-section {
		margin-bottom: var(--space-xl);
	}

	@media (max-width: 640px) {
		.skills-grid {
			grid-template-columns: 1fr;
		}

		.shared-comparison {
			grid-template-columns: 1fr;
		}
	}
</style>
