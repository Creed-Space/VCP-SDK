<script lang="ts">
	/**
	 * Skip Day Flow
	 * Shows how VCP handles private skip reasons
	 */
	import { goto } from '$app/navigation';
	import { vcpContext, logAdjustment } from '$lib/vcp';
	import { gentianProfile, getSkipDayContext } from '$lib/personas/gentian';

	// Ensure profile is loaded
	$effect(() => {
		if (!$vcpContext) {
			vcpContext.set(gentianProfile);
		}
	});

	const ctx = $derived($vcpContext);
	const skipContext = getSkipDayContext();

	let isSkipping = $state(false);
	let skipComplete = $state(false);

	function handleSkip() {
		isSkipping = true;

		// Log the adjustment with private reason
		logAdjustment('guitar-community', 'Day adjusted', {
			reason: 'post_night_shift',
			energy_level: 'low',
			shift_type: 'night_recovery'
		});

		setTimeout(() => {
			isSkipping = false;
			skipComplete = true;
		}, 1500);
	}

	function handlePracticeAnyway() {
		goto('/personal/community');
	}

	function returnToCommunity() {
		goto('/personal/community');
	}
</script>

<svelte:head>
	<title>Skip Day - VCP Demo</title>
</svelte:head>

<div class="container-narrow">
	<div class="breadcrumb">
		<a href="/personal/community">← Back to challenge</a>
	</div>

	{#if !skipComplete}
		<section class="skip-header">
			<h1>Need a Break?</h1>
			<p class="text-muted">
				VCP detected context that might affect today's practice.
			</p>
		</section>

		<!-- Context Detection -->
		<section class="context-card card">
			<h3>🔍 Context Detected</h3>
			<div class="context-details">
				<div class="context-item">
					<span class="context-label">Trigger:</span>
					<span class="context-value">{skipContext.detected.trigger.replace(/_/g, ' ')}</span>
				</div>
				<div class="context-item">
					<span class="context-label">Energy State:</span>
					<span class="context-value">{skipContext.detected.energy_state}</span>
				</div>
				<div class="context-item">
					<span class="context-label">Current Streak:</span>
					<span class="context-value">{skipContext.detected.current_streak} days</span>
				</div>
			</div>
		</section>

		<!-- Recommendation -->
		<section class="recommendation-card card">
			<h3>💡 VCP Recommendation</h3>
			<p class="recommendation-text">
				{skipContext.recommendation.reasoning}
			</p>
		</section>

		<!-- What Happens -->
		<section class="outcomes-card card">
			<h3>What Happens If You Skip?</h3>
			<div class="outcome-list">
				<div class="outcome-item">
					<span class="outcome-icon">🔥</span>
					<div>
						<strong>Your Streak</strong>
						<p class="text-sm text-muted">
							{skipContext.recommendation.what_happens.streak}
						</p>
					</div>
				</div>
				<div class="outcome-item">
					<span class="outcome-icon">📊</span>
					<div>
						<strong>Leaderboard</strong>
						<p class="text-sm text-muted">
							{skipContext.recommendation.what_happens.leaderboard}
						</p>
					</div>
				</div>
				<div class="outcome-item outcome-private">
					<span class="outcome-icon">🔒</span>
					<div>
						<strong>Your Private Reason</strong>
						<p class="text-sm text-muted">
							{skipContext.recommendation.what_happens.private_reason}
						</p>
					</div>
				</div>
			</div>
		</section>

		<!-- Privacy Comparison -->
		<section class="privacy-card card">
			<h3>Privacy Preview</h3>
			<div class="comparison-grid">
				<div class="comparison-column comparison-column-user">
					<h4>👤 You Will See:</h4>
					<ul class="comparison-list">
						<li>Today: Adjusted (night shift recovery)</li>
						<li>Days: 18/22 (4 adjusted)</li>
						<li>Full skip history with reasons</li>
					</ul>
				</div>
				<div class="comparison-column comparison-column-stakeholder">
					<h4>👥 Community Will See:</h4>
					<ul class="comparison-list">
						<li>Today: Adjusted</li>
						<li>Days: 18/22 (4 adjusted)</li>
						<li>No reason, no judgment</li>
					</ul>
				</div>
			</div>
		</section>

		<!-- Action Buttons -->
		<section class="actions">
			<button
				class="btn btn-secondary btn-lg"
				onclick={handlePracticeAnyway}
				disabled={isSkipping}
			>
				Practice Anyway 💪
			</button>
			<button
				class="btn btn-primary btn-lg"
				onclick={handleSkip}
				disabled={isSkipping}
			>
				{#if isSkipping}
					Adjusting...
				{:else}
					Skip Today (Adjusted) ✓
				{/if}
			</button>
		</section>

		<p class="text-center text-sm text-muted" style="margin-top: 1rem;">
			Either choice is valid. Your wellbeing matters more than a streak.
		</p>
	{:else}
		<!-- Skip Complete -->
		<section class="complete-card card">
			<div class="complete-icon">✅</div>
			<h2>Day Adjusted</h2>
			<p class="text-muted">
				Your skip has been recorded privately. The community sees only that you took an adjusted day.
			</p>

			<div class="audit-preview">
				<h4>Audit Entry Created</h4>
				<div class="audit-entry">
					<div class="audit-row">
						<span class="audit-label">Event:</span>
						<span>adjustment_recorded</span>
					</div>
					<div class="audit-row">
						<span class="audit-label">Public:</span>
						<span class="badge badge-primary">Day adjusted</span>
					</div>
					<div class="audit-row">
						<span class="audit-label">Private (you only):</span>
						<span class="badge badge-warning">post_night_shift, energy_low</span>
					</div>
					<div class="audit-row">
						<span class="audit-label">Shared with community:</span>
						<span class="badge badge-success">No</span>
					</div>
				</div>
			</div>

			<div class="updated-stats">
				<h4>Your Updated Progress</h4>
				<div class="stats-row">
					<span>Days Practiced:</span>
					<span class="stat-value">18</span>
				</div>
				<div class="stats-row">
					<span>Days Adjusted:</span>
					<span class="stat-value">4 ← (was 3)</span>
				</div>
				<div class="stats-row">
					<span>Leaderboard Display:</span>
					<span class="stat-value">18/22 (4 adjusted)</span>
				</div>
			</div>

			<button class="btn btn-primary btn-lg" onclick={returnToCommunity}>
				Return to Community →
			</button>
		</section>
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

	.skip-header {
		text-align: center;
		margin-bottom: var(--space-xl);
	}

	.context-card {
		margin-bottom: var(--space-lg);
	}

	.context-details {
		margin-top: var(--space-md);
	}

	.context-item {
		display: flex;
		justify-content: space-between;
		padding: var(--space-sm);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-sm);
		margin-bottom: var(--space-xs);
	}

	.context-label {
		color: var(--color-text-muted);
	}

	.context-value {
		font-weight: 500;
		text-transform: capitalize;
	}

	.recommendation-card {
		margin-bottom: var(--space-lg);
		background: var(--color-primary-muted);
		border: 1px solid var(--color-primary);
	}

	.recommendation-text {
		font-size: 1.125rem;
		line-height: 1.6;
	}

	.outcomes-card {
		margin-bottom: var(--space-lg);
	}

	.outcome-list {
		margin-top: var(--space-md);
	}

	.outcome-item {
		display: flex;
		align-items: flex-start;
		gap: var(--space-md);
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		margin-bottom: var(--space-sm);
	}

	.outcome-item.outcome-private {
		background: var(--color-success-muted);
		border: 1px solid var(--color-success);
	}

	.outcome-icon {
		font-size: 1.25rem;
	}

	.privacy-card {
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

	.actions {
		display: flex;
		gap: var(--space-md);
		justify-content: center;
	}

	.complete-card {
		text-align: center;
		padding: var(--space-2xl);
	}

	.complete-icon {
		font-size: 4rem;
		margin-bottom: var(--space-md);
	}

	.audit-preview {
		margin: var(--space-xl) 0;
		text-align: left;
	}

	.audit-preview h4 {
		margin-bottom: var(--space-md);
	}

	.audit-entry {
		background: var(--color-bg-elevated);
		padding: var(--space-md);
		border-radius: var(--radius-md);
		border-left: 3px solid var(--color-primary);
	}

	.audit-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: var(--space-xs) 0;
		font-size: 0.875rem;
	}

	.audit-label {
		color: var(--color-text-muted);
	}

	.updated-stats {
		margin: var(--space-xl) 0;
		text-align: left;
	}

	.updated-stats h4 {
		margin-bottom: var(--space-md);
	}

	.stats-row {
		display: flex;
		justify-content: space-between;
		padding: var(--space-sm);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-sm);
		margin-bottom: var(--space-xs);
	}

	.stats-row .stat-value {
		font-weight: 500;
	}

	@media (max-width: 640px) {
		.actions {
			flex-direction: column;
		}
	}
</style>
