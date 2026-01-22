<script lang="ts">
	/**
	 * Community Challenge Page
	 * Shows leaderboard with adjusted days privacy
	 */
	import { vcpContext } from '$lib/vcp';
	import {
		gentianProfile,
		challengeLeaderboard,
		gentianChallengeProgress,
		getGentianPrivacyComparison
	} from '$lib/personas/gentian';
	import challengeData from '$lib/data/challenge.json';
	import AuditPanel from '$lib/components/shared/AuditPanel.svelte';

	// Audit panel visibility state
	let showAuditPanel = $state(true);

	// Ensure profile is loaded
	$effect(() => {
		if (!$vcpContext) {
			vcpContext.set(gentianProfile);
		}
	});

	const ctx = $derived($vcpContext);
	const progress = gentianChallengeProgress;
	const leaderboard = challengeLeaderboard;
	const comparison = getGentianPrivacyComparison();
	const badges = challengeData.badges;

	function getProgressPercent(completed: number, total: number): number {
		return Math.round((completed / total) * 100);
	}

	// Transform privacy context into AuditPanel entries
	const auditEntries = $derived(() => {
		const entries: { field: string; category: 'shared' | 'withheld' | 'influenced'; value?: string; reason?: string; stakeholder?: string }[] = [];

		// Shared fields (what community sees)
		const sharedFields = [
			{ field: 'display_name', value: ctx?.public_profile?.display_name },
			{ field: 'days_completed', value: String(progress.days_completed) },
			{ field: 'days_adjusted', value: `${progress.days_adjusted} (count only)` },
			{ field: 'badges', value: `${progress.badges?.length ?? 0} earned` },
			{ field: 'rank', value: '#3' }
		];
		for (const { field, value } of sharedFields) {
			entries.push({
				field: field.replace(/_/g, ' '),
				category: 'shared',
				value: String(value ?? '—'),
				stakeholder: 'Community'
			});
		}

		// Influenced fields (private context affecting participation)
		entries.push({
			field: 'adjusted days policy',
			category: 'influenced',
			value: 'active',
			reason: 'Private reasons accepted without penalty'
		});

		// Withheld fields (reasons for adjustments never exposed)
		const withheldFields = [
			{ field: 'Jan 18 adjustment reason', reason: 'Night shift recovery' },
			{ field: 'Jan 14 adjustment reason', reason: 'Double shift exhaustion' },
			{ field: 'Jan 10 adjustment reason', reason: 'Night shift recovery' },
			{ field: 'work schedule', reason: 'Rotating shift details' },
			{ field: 'housing situation', reason: 'Apartment noise constraints' }
		];
		for (const { field, reason } of withheldFields) {
			entries.push({
				field: field,
				category: 'withheld',
				reason: reason
			});
		}

		return entries;
	});
</script>

<svelte:head>
	<title>30-Day Challenge - VCP Demo</title>
</svelte:head>

<div class="page-layout" class:audit-open={showAuditPanel}>
	<div class="main-content">
		<div class="platform-frame platform-frame-community">
			<div class="platform-header platform-header-community">
				<div class="platform-brand">
					<span class="platform-logo">👥</span>
					<span class="platform-name">Guitar Community</span>
				</div>
				<div class="header-actions">
					<div class="vcp-badge">VCP Connected</div>
					<button
						class="audit-toggle-btn"
						onclick={() => showAuditPanel = !showAuditPanel}
						aria-label={showAuditPanel ? 'Hide audit panel' : 'Show audit panel'}
					>
						<i class="fa-solid fa-clipboard-list" aria-hidden="true"></i>
						{showAuditPanel ? 'Hide' : 'Show'} Audit
					</button>
				</div>
			</div>

	<div class="platform-content">
		<header class="challenge-header">
			<h1>🏆 {challengeData.challenge.name}</h1>
			<p class="text-muted">
				Day {challengeData.challenge.current_day} of {challengeData.challenge.total_days}
			</p>
		</header>

		<!-- Leaderboard -->
		<section class="leaderboard-section card">
			<h2>Leaderboard</h2>

			<table class="table">
				<thead>
					<tr>
						<th>Rank</th>
						<th>Player</th>
						<th>Progress</th>
						<th>Badges</th>
					</tr>
				</thead>
				<tbody>
					{#each leaderboard as entry}
						<tr class:highlighted={entry.is_current_user}>
							<td class="rank-cell">
								{#if entry.rank === 1}
									🥇
								{:else if entry.rank === 2}
									🥈
								{:else if entry.rank === 3}
									🥉
								{:else}
									#{entry.rank}
								{/if}
							</td>
							<td>
								<span class="player-name">
									{entry.display_name}
									{#if entry.is_current_user}
										<span class="badge badge-primary text-xs">You</span>
									{/if}
								</span>
							</td>
							<td>
								<div class="progress-cell">
									<span class="progress-text">
										{entry.days_completed}/{entry.total_days}
										{#if entry.days_adjusted > 0}
											<span class="adjusted-count">
												({entry.days_adjusted} adjusted)
											</span>
										{/if}
									</span>
									<div class="progress" style="height: 4px;">
										<div
											class="progress-bar progress-bar-success"
											style="width: {getProgressPercent(entry.days_completed, entry.total_days)}%"
										></div>
									</div>
								</div>
							</td>
							<td>
								<span class="badges-count">
									{challengeData.leaderboard.find(l => l.display_name === entry.display_name)?.badges.length || 0}
								</span>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</section>

		<!-- Adjusted Days Explainer -->
		<section class="explainer-card card">
			<h3>ℹ️ What are "Adjusted" Days?</h3>
			<p class="text-muted">
				{challengeData.privacy_explainer.adjusted_days_explanation}
			</p>
			<div class="privacy-note" style="margin-top: 1rem;">
				<span class="privacy-note-icon">🔒</span>
				<span>
					<strong>Community cannot see:</strong>
					{challengeData.privacy_explainer.what_community_cannot_see.join(', ')}
				</span>
			</div>
		</section>

		<!-- Your Stats -->
		<section class="your-stats card">
			<h2>Your Stats</h2>
			<div class="stats-grid">
				<div class="stat-card">
					<span class="stat-value">{progress.days_completed}</span>
					<span class="stat-label">Days Practiced</span>
				</div>
				<div class="stat-card">
					<span class="stat-value">{progress.days_adjusted}</span>
					<span class="stat-label">Adjusted Days</span>
				</div>
				<div class="stat-card">
					<span class="stat-value">{progress.current_streak}</span>
					<span class="stat-label">Current Streak</span>
				</div>
				<div class="stat-card">
					<span class="stat-value">{progress.best_streak}</span>
					<span class="stat-label">Best Streak</span>
				</div>
			</div>

			<!-- Badges -->
			<div class="badges-section">
				<h4>Your Badges</h4>
				<div class="badges-list">
					{#each progress.badges || [] as badgeId}
						{@const badge = badges.available.find(b => b.id === badgeId)}
						{#if badge}
							<div class="badge-item">
								<span class="badge-icon">{badge.icon}</span>
								<div>
									<span class="badge-name">{badge.name}</span>
									<span class="badge-desc">{badge.description}</span>
								</div>
							</div>
						{/if}
					{/each}
				</div>
			</div>
		</section>

		<!-- Privacy Comparison -->
		<section class="privacy-comparison card">
			<h2>What Others See vs What You See</h2>
			<div class="comparison-grid">
				<div class="comparison-column comparison-column-stakeholder">
					<h4>👥 Community Sees:</h4>
					<ul class="comparison-list">
						<li>Your display name: <strong>Gentian</strong></li>
						<li>Days completed: <strong>18</strong></li>
						<li>Days adjusted: <strong>3</strong> (count only)</li>
						<li>Badges earned: <strong>3</strong></li>
						<li>Rank: <strong>#3</strong></li>
					</ul>
				</div>
				<div class="comparison-column comparison-column-user">
					<h4>👤 You See:</h4>
					<ul class="comparison-list">
						<li>All of the above, plus:</li>
						<li>Why Jan 18 was adjusted: <em>Night shift recovery</em></li>
						<li>Why Jan 14 was adjusted: <em>Double shift exhaustion</em></li>
						<li>Why Jan 10 was adjusted: <em>Night shift recovery</em></li>
						<li>Your full schedule constraints</li>
					</ul>
				</div>
			</div>
		</section>

		<!-- Skip Today -->
		<section class="skip-section">
			<a href="/personal/skip" class="btn btn-secondary btn-lg">
				Need to Skip Today? →
			</a>
			<p class="text-sm text-muted" style="margin-top: 0.5rem;">
				See how VCP handles private skip reasons
			</p>
		</section>
		</div>
	</div>

	<div class="container-narrow" style="margin-top: 2rem;">
		<div class="nav-links">
			<a href="/personal/platforms/yousician" class="btn btn-ghost">← Yousician</a>
			<a href="/personal" class="btn btn-primary">Back to Profile →</a>
		</div>
	</div>
	</div>

	<!-- Audit Sidebar -->
	{#if showAuditPanel && ctx}
		<aside class="audit-sidebar">
			<AuditPanel
				entries={auditEntries()}
				title="Privacy Audit"
				compact={true}
				showTimestamps={false}
			/>
		</aside>
	{/if}
</div>

<style>
	/* Page Layout with Sidebar */
	.page-layout {
		display: flex;
		gap: var(--space-lg);
		max-width: 1400px;
		margin: 0 auto;
		padding: 0 var(--space-md);
	}

	.main-content {
		flex: 1;
		min-width: 0;
	}

	.audit-sidebar {
		width: 320px;
		flex-shrink: 0;
		position: sticky;
		top: var(--space-lg);
		height: fit-content;
		max-height: calc(100vh - var(--space-xl));
		overflow-y: auto;
	}

	.header-actions {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
	}

	.audit-toggle-btn {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		padding: var(--space-xs) var(--space-sm);
		background: var(--color-bg-elevated);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-md);
		color: var(--color-text-muted);
		font-size: 0.75rem;
		cursor: pointer;
		transition: all var(--transition-fast);
	}

	.audit-toggle-btn:hover {
		background: var(--color-bg-card);
		color: var(--color-text);
	}

	@media (max-width: 1024px) {
		.page-layout {
			flex-direction: column;
		}

		.audit-sidebar {
			width: 100%;
			position: static;
			max-height: none;
			order: -1;
			margin-bottom: var(--space-lg);
		}
	}

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
		color: var(--color-community);
	}

	.challenge-header {
		text-align: center;
		margin-bottom: var(--space-xl);
	}

	.challenge-header h1 {
		color: var(--color-community);
	}

	.leaderboard-section {
		margin-bottom: var(--space-xl);
	}

	.rank-cell {
		font-size: 1.25rem;
		width: 60px;
	}

	.player-name {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
	}

	.progress-cell {
		min-width: 150px;
	}

	.progress-text {
		font-size: 0.875rem;
		margin-bottom: var(--space-xs);
		display: block;
	}

	.adjusted-count {
		color: var(--color-text-subtle);
		font-size: 0.75rem;
	}

	.badges-count {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 24px;
		height: 24px;
		background: var(--color-warning-muted);
		color: var(--color-warning);
		border-radius: 50%;
		font-size: 0.75rem;
		font-weight: bold;
	}

	.explainer-card {
		margin-bottom: var(--space-xl);
	}

	.your-stats {
		margin-bottom: var(--space-xl);
	}

	.stats-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: var(--space-md);
		margin-top: var(--space-md);
		margin-bottom: var(--space-lg);
	}

	.stat-card {
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

	.badges-section h4 {
		margin-bottom: var(--space-md);
	}

	.badges-list {
		display: grid;
		gap: var(--space-sm);
	}

	.badge-item {
		display: flex;
		align-items: center;
		gap: var(--space-md);
		padding: var(--space-sm);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
	}

	.badge-icon {
		font-size: 1.5rem;
	}

	.badge-name {
		display: block;
		font-weight: 500;
	}

	.badge-desc {
		display: block;
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.privacy-comparison {
		margin-bottom: var(--space-xl);
	}

	.comparison-list {
		list-style: none;
		padding: 0;
	}

	.comparison-list li {
		padding: var(--space-xs) 0;
		font-size: 0.875rem;
		border-bottom: 1px solid rgba(255, 255, 255, 0.05);
	}

	.comparison-list li em {
		color: var(--color-success);
		font-style: normal;
	}

	.skip-section {
		text-align: center;
		padding: var(--space-xl) 0;
	}

	.nav-links {
		display: flex;
		justify-content: space-between;
	}

	@media (max-width: 768px) {
		.stats-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}
</style>
