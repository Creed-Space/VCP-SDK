<script lang="ts">
	/**
	 * Coach Interaction Page
	 * Shows how a coach sees a different subset of data than platforms or community
	 * Demonstrates tiered data sharing with appropriate context for coaching
	 */
	import { vcpContext, vcpConsents, logContextShared } from '$lib/vcp';
	import { gentianProfile, gentianChallengeProgress } from '$lib/personas/gentian';
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

	let showConsent = $state(true);
	let consentGranted = $state(false);

	// Check if consent already exists
	$effect(() => {
		if (vcpConsents.hasConsent('coach')) {
			consentGranted = true;
			showConsent = false;
		}
	});

	function grantConsent() {
		vcpConsents.grantConsent(
			'coach',
			['skill_level', 'learning_style', 'struggle_areas', 'goals', 'progress_detailed'],
			['energy_patterns', 'practice_times', 'motivation_details']
		);

		logContextShared(
			'coach',
			[
				'skill_level',
				'learning_style',
				'struggle_areas',
				'goals',
				'progress_detailed',
				'energy_patterns',
				'practice_times'
			],
			['work_schedule', 'housing_details', 'financial_situation', 'neighbor_situation'],
			3 // energy, schedule, and constraints influenced
		);

		consentGranted = true;
		showConsent = false;
	}

	function denyConsent() {
		showConsent = false;
	}

	// Coach-specific view of the student
	const coachView = $derived(() => {
		if (!ctx) return null;

		return {
			student_name: ctx.public_profile.display_name,
			skill_level: ctx.public_profile.experience,
			weeks_learning: ctx.current_skills?.weeks_learning,
			learning_style: ctx.public_profile.learning_style,
			motivation: ctx.public_profile.motivation,
			current_focus: ctx.current_skills?.current_focus,
			skills_acquired: ctx.current_skills?.skills_acquired || [],
			struggle_areas: ctx.current_skills?.struggle_areas || [],
			// Coach sees more than community
			energy_patterns: {
				best_practice_times: ['Saturday afternoon', 'Tuesday evening'],
				avoid_times: ['Post night shift', 'Sunday'],
				typical_session_length: '30-45 minutes'
			},
			practice_consistency: {
				days_practiced: progress.days_completed,
				days_adjusted: progress.days_adjusted,
				current_streak: progress.current_streak,
				best_streak: progress.best_streak,
				// Coach sees adjustment patterns (not reasons)
				adjustment_pattern: 'Clustered around certain days (pattern suggests external factor)'
			},
			goals: {
				short_term: 'Smooth chord transitions',
				medium_term: 'Play 3 full songs',
				long_term: 'Jam with others'
			}
		};
	});

	// Comparison of what different stakeholders see
	const dataComparison = [
		{
			field: 'Progress',
			community: '18/22 days',
			platforms: '18/22 days + skills',
			coach: '18/22 days + patterns + struggles'
		},
		{
			field: 'Adjusted Days',
			community: '3 (count only)',
			platforms: '3 (count only)',
			coach: '3 + pattern analysis'
		},
		{
			field: 'Struggle Areas',
			community: 'Hidden',
			platforms: 'Basic flags',
			coach: 'Detailed: chord transitions, barre chords'
		},
		{
			field: 'Energy Patterns',
			community: 'Hidden',
			platforms: 'Hidden',
			coach: 'Best times, session length'
		},
		{
			field: 'Work Schedule',
			community: 'Hidden',
			platforms: 'Hidden',
			coach: 'Hidden (not relevant)'
		},
		{
			field: 'Housing Situation',
			community: 'Hidden',
			platforms: 'Noise flag only',
			coach: 'Hidden (not relevant)'
		}
	];

	// Transform into AuditPanel entries
	const auditEntries = $derived(() => {
		const entries: {
			field: string;
			category: 'shared' | 'withheld' | 'influenced';
			value?: string;
			reason?: string;
			stakeholder?: string;
		}[] = [];

		// Shared with coach
		const sharedFields = [
			{ field: 'skill_level', value: 'beginner' },
			{ field: 'learning_style', value: 'hands_on' },
			{ field: 'struggle_areas', value: 'chord transitions, barre chords' },
			{ field: 'goals', value: 'play 3 songs, jam with others' },
			{ field: 'progress_detailed', value: '18/22 with patterns' },
			{ field: 'energy_patterns', value: 'Sat afternoon best' },
			{ field: 'practice_times', value: 'Tue/Sat preferred' }
		];
		for (const { field, value } of sharedFields) {
			entries.push({
				field: field.replace(/_/g, ' '),
				category: 'shared',
				value,
				stakeholder: 'Coach'
			});
		}

		// Influenced
		entries.push({
			field: 'adjustment patterns',
			category: 'influenced',
			value: 'detected',
			reason: 'Coach can see patterns without knowing reasons'
		});

		// Withheld from coach (not relevant to coaching)
		const withheldFields = [
			{ field: 'work_schedule', reason: 'Not relevant to guitar coaching' },
			{ field: 'housing_details', reason: 'Not relevant to coaching' },
			{ field: 'financial_situation', reason: 'Private' },
			{ field: 'neighbor_situation', reason: 'Private' },
			{ field: 'adjustment_reasons', reason: 'Only patterns shared, not causes' }
		];
		for (const { field, reason } of withheldFields) {
			entries.push({
				field: field.replace(/_/g, ' '),
				category: 'withheld',
				reason
			});
		}

		return entries;
	});
</script>

<svelte:head>
	<title>Coach View - VCP Demo</title>
</svelte:head>

<!-- Consent Dialog -->
{#if showConsent && !consentGranted}
	<div class="consent-overlay">
		<div class="consent-dialog card">
			<div class="coach-icon">
				<i class="fa-solid fa-user-tie" aria-hidden="true"></i>
			</div>
			<h2>Connect with Guitar Coach</h2>
			<p class="text-muted">
				Maria (your coach) would like access to help guide your learning
			</p>

			<div class="consent-sections">
				<div class="consent-section">
					<h4>Coach will see:</h4>
					<ul class="consent-list">
						<li class="consent-item consent-required">
							<span>Detailed progress & patterns</span>
						</li>
						<li class="consent-item consent-required">
							<span>Struggle areas & current focus</span>
						</li>
						<li class="consent-item consent-required">
							<span>Learning style & goals</span>
						</li>
						<li class="consent-item consent-optional">
							<span>Energy patterns & best practice times</span>
						</li>
					</ul>
				</div>

				<div class="consent-section">
					<h4>Coach will NOT see:</h4>
					<ul class="consent-list consent-list-hidden">
						<li class="consent-item consent-hidden">
							<span>Work schedule details</span>
						</li>
						<li class="consent-item consent-hidden">
							<span>Housing/living situation</span>
						</li>
						<li class="consent-item consent-hidden">
							<span>Financial information</span>
						</li>
						<li class="consent-item consent-hidden">
							<span>WHY days were adjusted</span>
						</li>
					</ul>
				</div>
			</div>

			<div class="privacy-note">
				<span class="privacy-note-icon">💡</span>
				<span>
					Coaches see MORE than platforms (to help you effectively) but LESS than you see
					yourself. They get learning-relevant context without personal life details.
				</span>
			</div>

			<div class="consent-actions">
				<button class="btn btn-secondary" onclick={denyConsent}>Not Now</button>
				<button class="btn btn-primary" onclick={grantConsent}>Connect Coach</button>
			</div>
		</div>
	</div>
{/if}

<div class="page-layout" class:audit-open={showAuditPanel}>
	<div class="main-content">
		{#if consentGranted && coachView()}
			<div class="platform-frame platform-frame-coach">
				<div class="platform-header platform-header-coach">
					<div class="platform-brand">
						<span class="platform-logo">
							<i class="fa-solid fa-chalkboard-user" aria-hidden="true"></i>
						</span>
						<span class="platform-name">Coach Dashboard</span>
					</div>
					<div class="header-actions">
						<div class="vcp-badge">VCP Connected</div>
						<button
							class="audit-toggle-btn"
							onclick={() => (showAuditPanel = !showAuditPanel)}
							aria-label={showAuditPanel ? 'Hide audit panel' : 'Show audit panel'}
						>
							<i class="fa-solid fa-clipboard-list" aria-hidden="true"></i>
							{showAuditPanel ? 'Hide' : 'Show'} Audit
						</button>
					</div>
				</div>

				<div class="platform-content">
					<div class="coach-header">
						<div class="coach-avatar">
							<i class="fa-solid fa-user-tie" aria-hidden="true"></i>
						</div>
						<div>
							<h1>Student: {coachView()?.student_name}</h1>
							<p class="text-muted">Coach Maria's view of this student</p>
						</div>
					</div>

					<!-- Student Overview -->
					<section class="card student-overview">
						<h2>Student Profile</h2>
						<div class="overview-grid">
							<div class="overview-item">
								<span class="overview-label">Level</span>
								<span class="overview-value">{coachView()?.skill_level}</span>
							</div>
							<div class="overview-item">
								<span class="overview-label">Weeks Learning</span>
								<span class="overview-value">{coachView()?.weeks_learning}</span>
							</div>
							<div class="overview-item">
								<span class="overview-label">Learning Style</span>
								<span class="overview-value">{coachView()?.learning_style?.replace(/_/g, ' ')}</span>
							</div>
							<div class="overview-item">
								<span class="overview-label">Motivation</span>
								<span class="overview-value">{coachView()?.motivation?.replace(/_/g, ' ')}</span>
							</div>
						</div>
					</section>

					<!-- Progress Analysis -->
					<section class="card progress-analysis">
						<h2>Progress Analysis</h2>
						<div class="progress-stats">
							<div class="stat-card">
								<span class="stat-value">{coachView()?.practice_consistency.days_practiced}</span>
								<span class="stat-label">Days Practiced</span>
							</div>
							<div class="stat-card">
								<span class="stat-value">{coachView()?.practice_consistency.current_streak}</span>
								<span class="stat-label">Current Streak</span>
							</div>
							<div class="stat-card">
								<span class="stat-value">{coachView()?.practice_consistency.best_streak}</span>
								<span class="stat-label">Best Streak</span>
							</div>
							<div class="stat-card stat-card-muted">
								<span class="stat-value">{coachView()?.practice_consistency.days_adjusted}</span>
								<span class="stat-label">Adjusted Days</span>
							</div>
						</div>

						<div class="pattern-note">
							<span class="pattern-icon">📊</span>
							<div>
								<strong>Pattern Detected:</strong>
								<p class="text-sm">{coachView()?.practice_consistency.adjustment_pattern}</p>
								<p class="text-sm text-muted">
									Note: As coach, I see patterns but not the personal reasons.
									This helps me adapt without overstepping.
								</p>
							</div>
						</div>
					</section>

					<!-- Struggle Areas (Coach-specific insight) -->
					<section class="card struggle-section">
						<h2>
							<i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i>
							Areas Needing Attention
						</h2>
						<div class="struggle-list">
							{#each coachView()?.struggle_areas || [] as area}
								<div class="struggle-item">
									<span class="struggle-icon">🎯</span>
									<span class="struggle-name">{area.replace(/_/g, ' ')}</span>
								</div>
							{/each}
						</div>
						<div class="coach-note">
							<p>
								<strong>Coaching Focus:</strong> Based on struggle areas and learning style (hands-on),
								recommend exercise-based drills over theory lectures.
							</p>
						</div>
					</section>

					<!-- Energy & Timing -->
					<section class="card energy-section">
						<h2>
							<i class="fa-solid fa-clock" aria-hidden="true"></i>
							Optimal Practice Windows
						</h2>
						<div class="timing-grid">
							<div class="timing-card timing-best">
								<h4>Best Times</h4>
								<ul>
									{#each coachView()?.energy_patterns.best_practice_times || [] as time}
										<li>{time}</li>
									{/each}
								</ul>
							</div>
							<div class="timing-card timing-avoid">
								<h4>Avoid</h4>
								<ul>
									{#each coachView()?.energy_patterns.avoid_times || [] as time}
										<li>{time}</li>
									{/each}
								</ul>
							</div>
							<div class="timing-card timing-length">
								<h4>Session Length</h4>
								<p>{coachView()?.energy_patterns.typical_session_length}</p>
							</div>
						</div>
						<p class="text-sm text-muted" style="margin-top: 1rem;">
							I can see WHEN to schedule sessions, but not WHY certain times don't work.
							That's appropriate - I don't need to know about work schedules.
						</p>
					</section>

					<!-- Goals -->
					<section class="card goals-section">
						<h2>
							<i class="fa-solid fa-bullseye" aria-hidden="true"></i>
							Student Goals
						</h2>
						<div class="goals-timeline">
							<div class="goal-item">
								<span class="goal-timeframe">Short-term</span>
								<span class="goal-text">{coachView()?.goals.short_term}</span>
							</div>
							<div class="goal-item">
								<span class="goal-timeframe">Medium-term</span>
								<span class="goal-text">{coachView()?.goals.medium_term}</span>
							</div>
							<div class="goal-item">
								<span class="goal-timeframe">Long-term</span>
								<span class="goal-text">{coachView()?.goals.long_term}</span>
							</div>
						</div>
					</section>

					<!-- Data Tier Comparison -->
					<section class="card comparison-section">
						<h2>What Different Stakeholders See</h2>
						<p class="text-sm text-muted" style="margin-bottom: 1rem;">
							VCP provides tiered access - coaches see more than community but less than the user
						</p>

						<div class="comparison-table-wrapper">
							<table class="comparison-table">
								<thead>
									<tr>
										<th>Field</th>
										<th>Community</th>
										<th>Platforms</th>
										<th>Coach</th>
									</tr>
								</thead>
								<tbody>
									{#each dataComparison as row}
										<tr>
											<td class="field-name">{row.field}</td>
											<td class="access-cell">{row.community}</td>
											<td class="access-cell">{row.platforms}</td>
											<td class="access-cell access-coach">{row.coach}</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					</section>

					<!-- Privacy Note -->
					<section class="privacy-section">
						<div class="privacy-note">
							<span class="privacy-note-icon">🔒</span>
							<div>
								<strong>Coach Privacy Boundary</strong>
								<p class="text-sm">
									As a coach, I have access to learning-relevant information to help effectively.
									I can see energy patterns and practice consistency, but NOT the personal life
									details that cause them. This is intentional - I don't need to know about
									work shifts or housing situations to teach guitar.
								</p>
							</div>
						</div>
					</section>
				</div>
			</div>
		{:else if !showConsent}
			<div class="container-narrow">
				<div class="no-coach">
					<h2>Coach Access Not Granted</h2>
					<p class="text-muted">You can connect with a coach anytime to get personalized guidance.</p>
					<button class="btn btn-primary" onclick={() => (showConsent = true)}>
						Connect Coach
					</button>
				</div>
			</div>
		{/if}

		<div class="container-narrow" style="margin-top: 2rem;">
			<div class="nav-links">
				<a href="/personal" class="btn btn-ghost">← Back to Profile</a>
				<a href="/personal/audit" class="btn btn-primary">View Full Audit →</a>
			</div>
		</div>
	</div>

	<!-- Audit Sidebar -->
	{#if showAuditPanel && consentGranted}
		<aside class="audit-sidebar">
			<AuditPanel
				entries={auditEntries()}
				title="Coach Audit"
				compact={true}
				showTimestamps={false}
			/>
		</aside>
	{/if}
</div>

<style>
	/* Page Layout */
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

	/* Consent Dialog */
	.consent-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.9);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
		padding: var(--space-lg);
	}

	.consent-dialog {
		max-width: 500px;
		width: 100%;
		text-align: center;
	}

	.coach-icon {
		font-size: 3rem;
		color: var(--color-coach, #10b981);
		margin-bottom: var(--space-md);
	}

	.consent-sections {
		margin: var(--space-lg) 0;
		text-align: left;
	}

	.consent-section {
		margin-bottom: var(--space-lg);
	}

	.consent-section h4 {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		margin-bottom: var(--space-sm);
	}

	.consent-list {
		list-style: none;
	}

	.consent-item {
		padding: var(--space-sm);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-sm);
		margin-bottom: var(--space-xs);
		font-size: 0.875rem;
	}

	.consent-required {
		border-left: 3px solid var(--color-success);
	}

	.consent-optional {
		border-left: 3px solid var(--color-text-subtle);
	}

	.consent-hidden {
		border-left: 3px solid var(--color-danger);
		opacity: 0.7;
	}

	.consent-actions {
		display: flex;
		gap: var(--space-md);
		justify-content: flex-end;
		margin-top: var(--space-lg);
	}

	/* Platform Frame */
	.platform-frame-coach {
		--platform-color: var(--color-coach, #10b981);
	}

	.platform-header-coach {
		background: var(--color-bg-card);
		padding: var(--space-md) var(--space-lg);
		border-bottom: 2px solid var(--color-coach, #10b981);
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.platform-brand {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
	}

	.platform-logo {
		font-size: 1.5rem;
		color: var(--color-coach, #10b981);
	}

	.platform-name {
		font-weight: 600;
		color: var(--color-coach, #10b981);
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
	}

	.platform-content {
		padding: var(--space-lg);
	}

	/* Coach Header */
	.coach-header {
		display: flex;
		align-items: center;
		gap: var(--space-lg);
		margin-bottom: var(--space-xl);
	}

	.coach-avatar {
		width: 64px;
		height: 64px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-coach, #10b981);
		color: white;
		border-radius: 50%;
		font-size: 1.5rem;
	}

	.coach-header h1 {
		color: var(--color-coach, #10b981);
	}

	/* Student Overview */
	.student-overview {
		margin-bottom: var(--space-lg);
	}

	.overview-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: var(--space-md);
		margin-top: var(--space-md);
	}

	.overview-item {
		text-align: center;
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
	}

	.overview-label {
		display: block;
		font-size: 0.6875rem;
		text-transform: uppercase;
		color: var(--color-text-subtle);
		margin-bottom: var(--space-xs);
	}

	.overview-value {
		font-weight: 500;
		text-transform: capitalize;
	}

	/* Progress Analysis */
	.progress-analysis {
		margin-bottom: var(--space-lg);
	}

	.progress-stats {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: var(--space-md);
		margin: var(--space-md) 0;
	}

	.stat-card {
		text-align: center;
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
	}

	.stat-card-muted {
		opacity: 0.7;
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

	.pattern-note {
		display: flex;
		align-items: flex-start;
		gap: var(--space-md);
		padding: var(--space-md);
		background: var(--color-warning-muted);
		border-radius: var(--radius-md);
		margin-top: var(--space-md);
	}

	.pattern-icon {
		font-size: 1.5rem;
	}

	/* Struggle Section */
	.struggle-section {
		margin-bottom: var(--space-lg);
	}

	.struggle-section h2 {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
	}

	.struggle-list {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-sm);
		margin: var(--space-md) 0;
	}

	.struggle-item {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-sm) var(--space-md);
		background: var(--color-danger-muted);
		border: 1px solid var(--color-danger);
		border-radius: var(--radius-md);
	}

	.coach-note {
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		border-left: 3px solid var(--color-coach, #10b981);
	}

	/* Energy Section */
	.energy-section {
		margin-bottom: var(--space-lg);
	}

	.energy-section h2 {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
	}

	.timing-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: var(--space-md);
		margin-top: var(--space-md);
	}

	.timing-card {
		padding: var(--space-md);
		border-radius: var(--radius-md);
	}

	.timing-card h4 {
		margin-bottom: var(--space-sm);
		font-size: 0.875rem;
	}

	.timing-card ul {
		margin: 0;
		padding-left: var(--space-lg);
		font-size: 0.875rem;
	}

	.timing-best {
		background: var(--color-success-muted);
		border: 1px solid var(--color-success);
	}

	.timing-avoid {
		background: var(--color-danger-muted);
		border: 1px solid var(--color-danger);
	}

	.timing-length {
		background: var(--color-bg-elevated);
	}

	/* Goals Section */
	.goals-section {
		margin-bottom: var(--space-lg);
	}

	.goals-section h2 {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
	}

	.goals-timeline {
		margin-top: var(--space-md);
	}

	.goal-item {
		display: flex;
		align-items: center;
		gap: var(--space-lg);
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		margin-bottom: var(--space-sm);
	}

	.goal-timeframe {
		min-width: 100px;
		font-size: 0.75rem;
		text-transform: uppercase;
		color: var(--color-text-subtle);
	}

	.goal-text {
		font-weight: 500;
	}

	/* Comparison Section */
	.comparison-section {
		margin-bottom: var(--space-lg);
	}

	.comparison-table-wrapper {
		overflow-x: auto;
	}

	.comparison-table {
		width: 100%;
		border-collapse: collapse;
	}

	.comparison-table th,
	.comparison-table td {
		padding: var(--space-sm);
		text-align: left;
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.comparison-table th {
		font-size: 0.75rem;
		text-transform: uppercase;
		color: var(--color-text-muted);
	}

	.field-name {
		font-weight: 500;
	}

	.access-cell {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
	}

	.access-coach {
		color: var(--color-coach, #10b981);
		font-weight: 500;
	}

	/* Privacy Section */
	.privacy-section {
		margin-bottom: var(--space-lg);
	}

	/* No Coach State */
	.no-coach {
		text-align: center;
		padding: var(--space-2xl);
	}

	/* Navigation */
	.nav-links {
		display: flex;
		justify-content: space-between;
	}

	@media (max-width: 1024px) {
		.page-layout {
			flex-direction: column;
		}

		.audit-sidebar {
			width: 100%;
			position: static;
			order: -1;
			margin-bottom: var(--space-lg);
		}
	}

	@media (max-width: 768px) {
		.overview-grid,
		.progress-stats {
			grid-template-columns: repeat(2, 1fr);
		}

		.timing-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
