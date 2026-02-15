<script lang="ts">
	/**
	 * Professional Demo - Conflict Resolution Journey
	 * Shows what happens when work constitution conflicts with personal constitution
	 * Scenario: Manager schedules intensive workshop on Campion's only available Saturday
	 */
	import { vcpContext, logRecommendation } from '$lib/vcp';
	import {
		campionProfile,
		workConstitution,
		personalConstitution
	} from '$lib/personas/campion';
	import AuditPanel from '$lib/components/shared/AuditPanel.svelte';

	// Audit panel visibility state
	let showAuditPanel = $state(true);

	// Ensure profile is loaded
	$effect(() => {
		if (!$vcpContext) {
			vcpContext.set(campionProfile);
		}
	});

	const ctx = $derived($vcpContext);

	// Conflict scenario data
	const conflictScenario = {
		workshop: {
			title: 'Advanced Leadership Intensive',
			dates: ['Fri Jan 31', 'Sat Feb 1', 'Sun Feb 2'],
			duration: '3 days, 9am-5pm',
			location: 'TechCorp HQ, Conference Room A',
			mandatory: false,
			career_impact: 'High - recommended for Tech Lead candidates',
			cost: '€0 (company sponsored)'
		},
		conflict: {
			day: 'Saturday Feb 1',
			work_rule: 'Attend career development opportunities when available',
			personal_rule: 'Protect family time, especially sole-parent responsibilities',
			severity: 'moderate'
		},
		private_context: {
			reason: 'Only available childcare is school hours (Mon-Fri 8am-3pm)',
			saturday_status: 'Sole childcare responsibility',
			alternative_care: 'None available on short notice',
			impact_if_missed: "Daughter (7) would have no supervision"
		}
	};

	// Resolution options
	const resolutionOptions = [
		{
			id: 'decline_gracefully',
			label: 'Decline with alternative',
			recommendation: true,
			description: 'Request to attend next quarter\'s workshop instead',
			work_impact: 'Minimal - workshop runs quarterly',
			personal_impact: 'None - family time protected',
			what_manager_sees: 'Schedule conflict, alternative requested',
			what_manager_doesnt_see: 'Childcare responsibilities'
		},
		{
			id: 'partial_attendance',
			label: 'Attend Friday + Sunday only',
			recommendation: false,
			description: 'Skip Saturday, catch up on materials',
			work_impact: 'Moderate - miss core content',
			personal_impact: 'None - Saturday protected',
			what_manager_sees: 'Partial availability due to prior commitment',
			what_manager_doesnt_see: 'That commitment is childcare'
		},
		{
			id: 'force_attendance',
			label: 'Attend all 3 days',
			recommendation: false,
			description: 'Find emergency childcare somehow',
			work_impact: 'None',
			personal_impact: 'High stress, potential childcare emergency',
			what_manager_sees: 'Full attendance confirmed',
			what_manager_doesnt_see: 'The personal cost'
		}
	];

	let selectedOption: string | null = $state(null);
	let resolutionComplete = $state(false);

	function selectOption(optionId: string) {
		selectedOption = optionId;
	}

	function confirmResolution() {
		if (!selectedOption) return;

		logRecommendation(
			'conflict-resolution',
			['workshop_dates', 'career_relevance', 'availability_flag'],
			['childcare_situation', 'family_status', 'saturday_commitment_reason'],
			{
				conflict_type: 'work_vs_personal',
				resolution: selectedOption,
				privacy_maintained: true
			}
		);

		resolutionComplete = true;
	}

	// Transform into AuditPanel entries
	const auditEntries = $derived(() => {
		const entries: {
			field: string;
			category: 'shared' | 'withheld' | 'influenced';
			value?: string;
			reason?: string;
			stakeholder?: string;
		}[] = [];

		// What manager sees
		entries.push({
			field: 'availability',
			category: 'shared',
			value: 'Saturday unavailable',
			stakeholder: 'Manager'
		});
		entries.push({
			field: 'alternative request',
			category: 'shared',
			value: 'Q2 workshop preferred',
			stakeholder: 'Manager'
		});

		// What influenced the decision
		entries.push({
			field: 'family responsibility',
			category: 'influenced',
			value: 'active',
			reason: 'Triggered personal constitution protection'
		});
		entries.push({
			field: 'childcare availability',
			category: 'influenced',
			value: 'weekdays only',
			reason: 'Saturday attendance not viable'
		});

		// What stays private
		entries.push({
			field: 'single parent status',
			category: 'withheld',
			reason: 'Private - not relevant to work decision'
		});
		entries.push({
			field: 'childcare details',
			category: 'withheld',
			reason: 'Private - only availability shared'
		});
		entries.push({
			field: 'daughter age',
			category: 'withheld',
			reason: 'Private family information'
		});

		return entries;
	});
</script>

<svelte:head>
	<title>Conflict Resolution - Professional Demo</title>
</svelte:head>

<div class="page-layout" class:audit-open={showAuditPanel}>
	<div class="main-content container-narrow">
		<div class="breadcrumb">
			<a href="/professional">← Back to profile</a>
			<button
				class="audit-toggle-btn"
				onclick={() => (showAuditPanel = !showAuditPanel)}
				aria-label={showAuditPanel ? 'Hide audit panel' : 'Show audit panel'}
			>
				<i class="fa-solid fa-clipboard-list" aria-hidden="true"></i>
				{showAuditPanel ? 'Hide' : 'Show'} Audit
			</button>
		</div>

		<header class="journey-header">
			<span class="badge badge-danger">Conflict Resolution</span>
			<h1>Constitution Conflict</h1>
			<p class="journey-subtitle">
				What happens when work obligations clash with personal responsibilities?
			</p>
		</header>

		{#if !resolutionComplete}
			<!-- The Conflict -->
			<section class="card conflict-card">
				<div class="conflict-header">
					<span class="conflict-icon">⚠️</span>
					<h2>Scheduling Conflict Detected</h2>
				</div>

				<div class="workshop-details">
					<h3>{conflictScenario.workshop.title}</h3>
					<div class="workshop-meta">
						<span><i class="fa-solid fa-calendar" aria-hidden="true"></i> {conflictScenario.workshop.dates.join(', ')}</span>
						<span><i class="fa-solid fa-clock" aria-hidden="true"></i> {conflictScenario.workshop.duration}</span>
						<span><i class="fa-solid fa-location-dot" aria-hidden="true"></i> {conflictScenario.workshop.location}</span>
					</div>
					<div class="workshop-tags">
						<span class="badge badge-warning">Career Impact: High</span>
						<span class="badge badge-success">Cost: Free</span>
						<span class="badge badge-ghost">Optional</span>
					</div>
				</div>

				<div class="conflict-detail">
					<div class="conflict-day">
						<span class="day-label">Problem Day:</span>
						<span class="day-value">{conflictScenario.conflict.day}</span>
					</div>
				</div>
			</section>

			<!-- Constitution Clash -->
			<section class="card constitution-clash">
				<h3><i class="fa-solid fa-bolt" aria-hidden="true"></i> Constitution Clash</h3>

				<div class="clash-grid">
					<div class="clash-item clash-work">
						<div class="clash-header">
							<span class="badge badge-primary">Work Constitution</span>
							<span class="constitution-name">techcorp.career.advisor</span>
						</div>
						<div class="rule-box">
							<span class="rule-label">Rule:</span>
							<p>"{conflictScenario.conflict.work_rule}"</p>
						</div>
						<div class="rule-verdict">
							<span class="verdict-icon">→</span>
							<span>Suggests: <strong>Attend workshop</strong></span>
						</div>
					</div>

					<div class="clash-vs">VS</div>

					<div class="clash-item clash-personal">
						<div class="clash-header">
							<span class="badge badge-warning">Personal Constitution</span>
							<span class="constitution-name">personal.balanced.guide</span>
						</div>
						<div class="rule-box">
							<span class="rule-label">Rule:</span>
							<p>"{conflictScenario.conflict.personal_rule}"</p>
						</div>
						<div class="rule-verdict">
							<span class="verdict-icon">→</span>
							<span>Suggests: <strong>Protect Saturday</strong></span>
						</div>
					</div>
				</div>

				<div class="private-context-note">
					<span class="privacy-note-icon">🔒</span>
					<div>
						<strong>Private Context (only you see this):</strong>
						<p class="text-sm">{conflictScenario.private_context.reason}</p>
						<p class="text-sm text-muted">Saturday status: {conflictScenario.private_context.saturday_status}</p>
					</div>
				</div>
			</section>

			<!-- Resolution Options -->
			<section class="resolution-section">
				<h2>Resolution Options</h2>
				<p class="text-muted" style="margin-bottom: 1.5rem;">
					VCP helps you navigate this conflict while protecting your privacy
				</p>

				<div class="options-grid">
					{#each resolutionOptions as option}
						<button
							class="option-card card"
							class:selected={selectedOption === option.id}
							class:recommended={option.recommendation}
							onclick={() => selectOption(option.id)}
						>
							{#if option.recommendation}
								<span class="recommended-badge">
									<i class="fa-solid fa-star" aria-hidden="true"></i> Recommended
								</span>
							{/if}

							<h3>{option.label}</h3>
							<p class="option-desc">{option.description}</p>

							<div class="option-impacts">
								<div class="impact-row">
									<span class="impact-label">Work impact:</span>
									<span class="impact-value">{option.work_impact}</span>
								</div>
								<div class="impact-row">
									<span class="impact-label">Personal impact:</span>
									<span class="impact-value">{option.personal_impact}</span>
								</div>
							</div>

							<div class="privacy-preview">
								<div class="privacy-row privacy-visible">
									<span class="privacy-icon">👁️</span>
									<span>Manager sees: "{option.what_manager_sees}"</span>
								</div>
								<div class="privacy-row privacy-hidden">
									<span class="privacy-icon">🔒</span>
									<span>Hidden: {option.what_manager_doesnt_see}</span>
								</div>
							</div>
						</button>
					{/each}
				</div>

				{#if selectedOption}
					<div class="confirm-section">
						<button class="btn btn-primary btn-lg" onclick={confirmResolution}>
							Confirm Resolution →
						</button>
					</div>
				{/if}
			</section>
		{:else}
			<!-- Resolution Complete -->
			<section class="resolution-complete card">
				<div class="complete-icon">✓</div>
				<h2>Conflict Resolved</h2>

				<div class="resolution-summary">
					<p>
						You selected: <strong>{resolutionOptions.find(o => o.id === selectedOption)?.label}</strong>
					</p>
				</div>

				<div class="what-happened">
					<h3>What Happened</h3>

					<div class="outcome-grid">
						<div class="outcome-item outcome-manager">
							<h4>📧 Email to Manager</h4>
							<div class="email-preview">
								<p class="email-line"><strong>Subject:</strong> RE: Leadership Intensive - Alternative Request</p>
								<p class="email-body">
									"Hi Sarah, thank you for recommending me for the Leadership Intensive.
									Unfortunately I have a prior commitment on Saturday Feb 1 that I cannot reschedule.
									Would it be possible to attend the Q2 session instead? I'm very interested in
									developing these skills for the Tech Lead path."
								</p>
							</div>
							<p class="text-sm text-muted" style="margin-top: 0.5rem;">
								Note: "Prior commitment" - no details about childcare shared
							</p>
						</div>

						<div class="outcome-item outcome-calendar">
							<h4>📅 Your Calendar</h4>
							<div class="calendar-preview">
								<div class="calendar-entry">
									<span class="cal-day">Sat Feb 1</span>
									<span class="cal-event cal-personal">Family time (protected)</span>
								</div>
								<div class="calendar-entry">
									<span class="cal-day">Q2 TBD</span>
									<span class="cal-event cal-work">Leadership Intensive (rescheduled)</span>
								</div>
							</div>
						</div>

						<div class="outcome-item outcome-audit">
							<h4>📋 Audit Record</h4>
							<div class="audit-record">
								<p><strong>Event:</strong> conflict_resolved</p>
								<p><strong>Constitutions:</strong> work + personal</p>
								<p><strong>Resolution:</strong> decline_gracefully</p>
								<p><strong>Private fields used:</strong> 3</p>
								<p><strong>Private fields exposed:</strong> 0</p>
							</div>
						</div>
					</div>
				</div>

				<div class="key-insight card">
					<h3>💡 Key Insight</h3>
					<p>
						VCP enabled Campion to protect family time without revealing being a single parent.
						The manager sees a professional response about scheduling; the personal context
						that drove the decision remains private.
					</p>
					<p class="text-sm text-muted" style="margin-top: 0.5rem;">
						Career progression continues. Privacy maintained. No awkward explanations needed.
					</p>
				</div>

				<div class="nav-buttons">
					<a href="/professional" class="btn btn-secondary">← Back to Profile</a>
					<a href="/professional/audit" class="btn btn-primary">View Full Audit →</a>
				</div>
			</section>
		{/if}
	</div>

	<!-- Audit Sidebar -->
	{#if showAuditPanel}
		<aside class="audit-sidebar">
			<AuditPanel
				entries={auditEntries()}
				title="Conflict Audit"
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

	.breadcrumb {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--space-lg);
	}

	.breadcrumb a {
		color: var(--color-text-muted);
		text-decoration: none;
		font-size: 0.875rem;
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

	.journey-header {
		text-align: center;
		margin-bottom: var(--space-xl);
	}

	.journey-header h1 {
		margin: var(--space-md) 0 var(--space-sm);
	}

	.journey-subtitle {
		color: var(--color-text-muted);
	}

	/* Conflict Card */
	.conflict-card {
		margin-bottom: var(--space-lg);
		border: 2px solid var(--color-danger);
	}

	.conflict-header {
		display: flex;
		align-items: center;
		gap: var(--space-md);
		margin-bottom: var(--space-lg);
	}

	.conflict-icon {
		font-size: 2rem;
	}

	.workshop-details h3 {
		margin-bottom: var(--space-sm);
	}

	.workshop-meta {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-md);
		font-size: 0.875rem;
		color: var(--color-text-muted);
		margin-bottom: var(--space-md);
	}

	.workshop-meta span {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
	}

	.workshop-tags {
		display: flex;
		gap: var(--space-sm);
		margin-bottom: var(--space-lg);
	}

	.conflict-day {
		display: flex;
		align-items: center;
		gap: var(--space-md);
		padding: var(--space-md);
		background: var(--color-danger-muted);
		border-radius: var(--radius-md);
	}

	.day-label {
		color: var(--color-danger);
		font-weight: 500;
	}

	.day-value {
		font-weight: 600;
	}

	/* Constitution Clash */
	.constitution-clash {
		margin-bottom: var(--space-lg);
	}

	.constitution-clash h3 {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-lg);
	}

	.clash-grid {
		display: grid;
		grid-template-columns: 1fr auto 1fr;
		gap: var(--space-md);
		align-items: center;
		margin-bottom: var(--space-lg);
	}

	.clash-item {
		padding: var(--space-md);
		border-radius: var(--radius-md);
	}

	.clash-work {
		background: var(--color-primary-muted);
		border: 1px solid var(--color-primary);
	}

	.clash-personal {
		background: var(--color-warning-muted);
		border: 1px solid var(--color-warning);
	}

	.clash-header {
		margin-bottom: var(--space-sm);
	}

	.constitution-name {
		display: block;
		font-family: var(--font-mono);
		font-size: 0.6875rem;
		color: var(--color-text-muted);
		margin-top: var(--space-xs);
	}

	.rule-box {
		padding: var(--space-sm);
		background: rgba(0, 0, 0, 0.2);
		border-radius: var(--radius-sm);
		margin-bottom: var(--space-sm);
	}

	.rule-label {
		font-size: 0.6875rem;
		text-transform: uppercase;
		color: var(--color-text-subtle);
	}

	.rule-box p {
		font-size: 0.875rem;
		font-style: italic;
		margin-top: var(--space-xs);
	}

	.rule-verdict {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-size: 0.875rem;
	}

	.clash-vs {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--color-danger);
	}

	.private-context-note {
		display: flex;
		align-items: flex-start;
		gap: var(--space-md);
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		border-left: 3px solid var(--color-success);
	}

	/* Resolution Options */
	.resolution-section {
		margin-bottom: var(--space-xl);
	}

	.options-grid {
		display: grid;
		gap: var(--space-md);
	}

	.option-card {
		text-align: left;
		cursor: pointer;
		border: 2px solid transparent;
		transition: all var(--transition-fast);
		position: relative;
	}

	.option-card:hover {
		border-color: var(--color-primary);
	}

	.option-card.selected {
		border-color: var(--color-primary);
		background: var(--color-primary-muted);
	}

	.option-card.recommended {
		border-color: var(--color-success);
	}

	.recommended-badge {
		position: absolute;
		top: var(--space-sm);
		right: var(--space-sm);
		font-size: 0.6875rem;
		padding: 2px 8px;
		background: var(--color-success);
		color: white;
		border-radius: var(--radius-sm);
	}

	.option-card h3 {
		margin-bottom: var(--space-xs);
	}

	.option-desc {
		color: var(--color-text-muted);
		font-size: 0.875rem;
		margin-bottom: var(--space-md);
	}

	.option-impacts {
		margin-bottom: var(--space-md);
	}

	.impact-row {
		display: flex;
		justify-content: space-between;
		font-size: 0.8125rem;
		padding: var(--space-xs) 0;
		border-bottom: 1px solid rgba(255, 255, 255, 0.05);
	}

	.impact-label {
		color: var(--color-text-subtle);
	}

	.privacy-preview {
		background: var(--color-bg-elevated);
		border-radius: var(--radius-sm);
		padding: var(--space-sm);
	}

	.privacy-row {
		display: flex;
		align-items: flex-start;
		gap: var(--space-sm);
		font-size: 0.75rem;
		padding: var(--space-xs) 0;
	}

	.privacy-visible {
		color: var(--color-text-muted);
	}

	.privacy-hidden {
		color: var(--color-success);
	}

	.confirm-section {
		text-align: center;
		margin-top: var(--space-xl);
	}

	/* Resolution Complete */
	.resolution-complete {
		text-align: center;
	}

	.complete-icon {
		font-size: 4rem;
		color: var(--color-success);
		margin-bottom: var(--space-md);
	}

	.resolution-summary {
		margin-bottom: var(--space-xl);
	}

	.what-happened {
		text-align: left;
		margin-bottom: var(--space-xl);
	}

	.what-happened h3 {
		margin-bottom: var(--space-lg);
	}

	.outcome-grid {
		display: grid;
		gap: var(--space-md);
	}

	.outcome-item {
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
	}

	.outcome-item h4 {
		margin-bottom: var(--space-sm);
	}

	.email-preview {
		background: var(--color-bg);
		padding: var(--space-sm);
		border-radius: var(--radius-sm);
		font-size: 0.875rem;
	}

	.email-line {
		margin-bottom: var(--space-sm);
	}

	.email-body {
		color: var(--color-text-muted);
		font-style: italic;
	}

	.calendar-preview {
		display: flex;
		flex-direction: column;
		gap: var(--space-sm);
	}

	.calendar-entry {
		display: flex;
		align-items: center;
		gap: var(--space-md);
		padding: var(--space-sm);
		background: var(--color-bg);
		border-radius: var(--radius-sm);
	}

	.cal-day {
		font-weight: 500;
		min-width: 80px;
	}

	.cal-event {
		font-size: 0.875rem;
		padding: 2px 8px;
		border-radius: var(--radius-sm);
	}

	.cal-personal {
		background: var(--color-warning-muted);
		color: var(--color-warning);
	}

	.cal-work {
		background: var(--color-primary-muted);
		color: var(--color-primary);
	}

	.audit-record {
		font-family: var(--font-mono);
		font-size: 0.75rem;
		background: var(--color-bg);
		padding: var(--space-sm);
		border-radius: var(--radius-sm);
	}

	.audit-record p {
		margin-bottom: var(--space-xs);
	}

	.key-insight {
		text-align: left;
		background: var(--color-success-muted);
		border: 1px solid var(--color-success);
		margin-bottom: var(--space-xl);
	}

	.key-insight h3 {
		margin-bottom: var(--space-sm);
	}

	.nav-buttons {
		display: flex;
		justify-content: center;
		gap: var(--space-md);
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

	@media (max-width: 640px) {
		.clash-grid {
			grid-template-columns: 1fr;
		}

		.clash-vs {
			text-align: center;
		}

		.nav-buttons {
			flex-direction: column;
		}
	}
</style>
