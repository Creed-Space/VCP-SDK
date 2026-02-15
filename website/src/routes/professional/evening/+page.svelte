<script lang="ts">
	/**
	 * Professional Demo - Evening Journey
	 * Shows how the personal constitution (Godparent) protects wellbeing
	 * when Campion asks about studying while exhausted
	 */
	import { vcpContext, logRecommendation } from '$lib/vcp';
	import {
		campionProfile,
		personalConstitution,
		getEveningContext,
		getGodparentResponse,
		encodeContext
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
	const eveningContext = getEveningContext();
	const godparentResponse = getGodparentResponse();

	let reminderSet = $state(false);

	// Transform context into AuditPanel entries
	const auditEntries = $derived(() => {
		const entries: {
			field: string;
			category: 'shared' | 'withheld' | 'influenced';
			value?: string;
			reason?: string;
			stakeholder?: string;
		}[] = [];

		// Context detected (influenced recommendations)
		entries.push({
			field: 'time',
			category: 'influenced',
			value: '20:15 (evening)',
			reason: 'Triggered personal constitution'
		});
		entries.push({
			field: 'energy state',
			category: 'influenced',
			value: 'tired',
			reason: 'Protective advice activated'
		});
		entries.push({
			field: 'tomorrow schedule',
			category: 'influenced',
			value: 'early standup 9am',
			reason: 'Factored into rest recommendation'
		});

		// Withheld fields (private, never exposed)
		const withheldFields = [
			{ field: 'family status', reason: 'Single parent - private' },
			{ field: 'child bedtime', reason: 'Private family schedule' },
			{ field: 'health conditions', reason: 'Chronic condition - never shared' },
			{ field: 'childcare hours', reason: 'Private constraint' }
		];
		for (const { field, reason } of withheldFields) {
			entries.push({
				field,
				category: 'withheld',
				reason
			});
		}

		return entries;
	});

	// Log the recommendation on mount
	$effect(() => {
		logRecommendation(
			'personal-evening',
			['energy_state', 'tomorrow_schedule', 'time'],
			['family_status', 'child_bedtime', 'health_conditions', 'childcare_hours'],
			{
				constitution: 'personal.balanced.guide@1.0.0',
				persona: 'godparent',
				action: 'defer_study',
				privacy_note: 'No external logging in personal mode'
			}
		);
	});

	function setReminder() {
		reminderSet = true;
	}
</script>

<svelte:head>
	<title>Evening Check-In - Professional Demo</title>
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
			<span class="badge badge-warning">Evening Journey</span>
			<h1>Energy Check-In</h1>
			<p class="journey-subtitle">
				Campion asks: "I'm exhausted. Should I start that leadership course tonight?"
			</p>
		</header>

		<!-- Context Detection -->
		<section class="card context-card">
			<h3><i class="fa-solid fa-radar" aria-hidden="true"></i> Context Detected</h3>
			<div class="context-encoding">
				<code>{eveningContext.context_encoding}</code>
				<span class="encoding-label">VCP/A encoding</span>
			</div>
			<div class="context-grid">
				<div class="context-item">
					<span class="context-icon">⏰</span>
					<span class="context-label">Time</span>
					<span class="context-value">{eveningContext.detected.time} (evening)</span>
				</div>
				<div class="context-item">
					<span class="context-icon">📍</span>
					<span class="context-label">Location</span>
					<span class="context-value">Home</span>
				</div>
				<div class="context-item">
					<span class="context-icon">🧠</span>
					<span class="context-label">Energy</span>
					<span class="context-value energy-low">Tired</span>
				</div>
				<div class="context-item">
					<span class="context-icon">📅</span>
					<span class="context-label">Tomorrow</span>
					<span class="context-value">Standup at 9am</span>
				</div>
			</div>
		</section>

		<!-- Constitution Switch -->
		<section class="card constitution-card">
			<h3><i class="fa-solid fa-shield-halved" aria-hidden="true"></i> Active Constitution</h3>
			<div class="constitution-comparison">
				<div class="constitution-item constitution-inactive">
					<span class="constitution-badge">Work</span>
					<span class="constitution-name">techcorp.career.advisor</span>
					<span class="constitution-persona">Ambassador</span>
					<span class="constitution-adherence">Adherence: 3</span>
				</div>
				<span class="switch-arrow">→</span>
				<div class="constitution-item constitution-active">
					<span class="constitution-badge badge-warning">Personal</span>
					<span class="constitution-name">personal.balanced.guide</span>
					<span class="constitution-persona">Godparent</span>
					<span class="constitution-adherence">Adherence: 4 (stricter)</span>
				</div>
			</div>
			<p class="text-sm text-muted" style="margin-top: 1rem;">
				Evening context triggered switch to personal constitution. Godparent persona prioritizes
				wellbeing over productivity.
			</p>
		</section>

		<!-- AI Response (Godparent Mode) -->
		<section class="response-card card">
			<div class="response-header">
				<span class="persona-badge">
					<i class="fa-solid fa-hand-holding-heart" aria-hidden="true"></i>
					Godparent Mode
				</span>
			</div>

			<div class="response-content">
				<p class="greeting">{godparentResponse.greeting},</p>

				<p class="observation">{godparentResponse.observation}</p>

				<p class="main-advice">{godparentResponse.main_advice}</p>

				<div class="suggestion-section">
					<h4>Tonight (5 minutes max):</h4>
					<ul class="suggestion-list">
						{#each godparentResponse.tonight_suggestions as suggestion}
							<li>
								<strong>{suggestion.action}</strong>
								{#if suggestion.reason}
									<span class="suggestion-reason">{suggestion.reason}</span>
								{/if}
								{#if suggestion.options}
									<ul class="sub-options">
										{#each suggestion.options as option}
											<li>{option}</li>
										{/each}
									</ul>
									{#if suggestion.note}
										<span class="suggestion-note">{suggestion.note}</span>
									{/if}
								{/if}
							</li>
						{/each}
					</ul>
				</div>

				<div class="skip-section">
					<h4>Skip Tonight:</h4>
					<ul class="skip-list">
						{#each godparentResponse.skip_tonight as item}
							<li><span class="skip-icon">✗</span> {item}</li>
						{/each}
					</ul>
				</div>

				<div class="health-check">
					<span class="health-icon">💚</span>
					<p>{godparentResponse.health_check}</p>
				</div>

				<div class="reminder-offer">
					{#if !reminderSet}
						<p>{godparentResponse.offer}</p>
						<button class="btn btn-primary btn-sm" onclick={setReminder}>
							<i class="fa-solid fa-bell" aria-hidden="true"></i>
							Set Reminder
						</button>
					{:else}
						<p class="reminder-set">
							<i class="fa-solid fa-check-circle" aria-hidden="true"></i>
							Reminder set for Saturday at 8:45am
						</p>
					{/if}
				</div>
			</div>

			<div class="response-footer">
				<div class="privacy-note">
					<span class="privacy-note-icon">🔒</span>
					<span>{godparentResponse.privacy_note}</span>
				</div>
			</div>
		</section>

		<!-- What's Different -->
		<section class="card comparison-card">
			<h3>Professional vs Personal Response</h3>
			<div class="comparison-grid">
				<div class="comparison-column comparison-column-stakeholder">
					<h4>
						<i class="fa-solid fa-briefcase" aria-hidden="true"></i>
						Ambassador (Work)
					</h4>
					<p class="comparison-quote">
						"The Engineering Leadership course aligns with your Tech Lead goal. Module 1 covers
						fundamental concepts - I recommend starting tonight to maintain momentum."
					</p>
					<span class="comparison-note">Focus: Career progress</span>
				</div>
				<div class="comparison-column comparison-column-user">
					<h4>
						<i class="fa-solid fa-hand-holding-heart" aria-hidden="true"></i>
						Godparent (Personal)
					</h4>
					<p class="comparison-quote">
						"You're tired and have an early morning. Rest tonight - the course is self-paced and
						you'll learn better when alert. Let's find sustainable study times."
					</p>
					<span class="comparison-note">Focus: Sustainable wellbeing</span>
				</div>
			</div>
		</section>

		<!-- Navigation -->
		<section class="journey-nav">
			<a href="/professional/morning" class="btn btn-secondary"> ← Morning Journey </a>
			<a href="/professional/audit" class="btn btn-primary"> View Audit Trail → </a>
		</section>
	</div>

	<!-- Audit Sidebar -->
	{#if showAuditPanel}
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
		transition: all var(--transition-fast);
	}

	.audit-toggle-btn:hover {
		background: var(--color-bg-card);
		color: var(--color-text);
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
		font-style: italic;
	}

	/* Context Card */
	.context-card {
		margin-bottom: var(--space-lg);
	}

	.context-encoding {
		display: flex;
		align-items: center;
		gap: var(--space-md);
		padding: var(--space-sm);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		margin-bottom: var(--space-md);
	}

	.context-encoding code {
		font-family: var(--font-mono);
		font-size: 1.25rem;
		letter-spacing: 0.05em;
	}

	.encoding-label {
		font-size: 0.75rem;
		color: var(--color-text-subtle);
	}

	.context-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: var(--space-md);
	}

	.context-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		padding: var(--space-sm);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
	}

	.context-icon {
		font-size: 1.5rem;
		margin-bottom: var(--space-xs);
	}

	.context-label {
		font-size: 0.75rem;
		color: var(--color-text-subtle);
	}

	.context-value {
		font-size: 0.875rem;
		font-weight: 500;
	}

	.context-value.energy-low {
		color: var(--color-warning);
	}

	/* Constitution Card */
	.constitution-card {
		margin-bottom: var(--space-lg);
	}

	.constitution-comparison {
		display: flex;
		align-items: center;
		gap: var(--space-md);
		justify-content: center;
	}

	.constitution-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		min-width: 200px;
	}

	.constitution-inactive {
		opacity: 0.5;
	}

	.constitution-active {
		border: 2px solid var(--color-warning);
	}

	.constitution-badge {
		font-size: 0.75rem;
		padding: 2px 8px;
		background: var(--color-primary-muted);
		color: var(--color-primary);
		border-radius: var(--radius-sm);
		margin-bottom: var(--space-sm);
	}

	.constitution-name {
		font-family: var(--font-mono);
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.constitution-persona {
		font-weight: 600;
		margin: var(--space-xs) 0;
	}

	.constitution-adherence {
		font-size: 0.75rem;
		color: var(--color-text-subtle);
	}

	.switch-arrow {
		font-size: 1.5rem;
		color: var(--color-warning);
	}

	/* Response Card */
	.response-card {
		margin-bottom: var(--space-lg);
		border: 2px solid var(--color-warning);
	}

	.response-header {
		margin-bottom: var(--space-md);
	}

	.persona-badge {
		display: inline-flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-xs) var(--space-md);
		background: var(--color-warning-muted);
		color: var(--color-warning);
		border-radius: var(--radius-md);
		font-weight: 500;
	}

	.response-content {
		line-height: 1.6;
	}

	.greeting {
		font-size: 1.125rem;
		margin-bottom: var(--space-sm);
	}

	.observation {
		color: var(--color-text-muted);
		margin-bottom: var(--space-md);
	}

	.main-advice {
		margin-bottom: var(--space-lg);
	}

	.suggestion-section,
	.skip-section {
		margin-bottom: var(--space-lg);
	}

	.suggestion-section h4,
	.skip-section h4 {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		margin-bottom: var(--space-sm);
	}

	.suggestion-list {
		padding-left: var(--space-lg);
	}

	.suggestion-list li {
		margin-bottom: var(--space-sm);
	}

	.suggestion-reason {
		display: block;
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	.sub-options {
		margin-top: var(--space-xs);
		padding-left: var(--space-lg);
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	.suggestion-note {
		display: block;
		font-size: 0.8125rem;
		color: var(--color-success);
		margin-top: var(--space-xs);
	}

	.skip-list {
		list-style: none;
		padding: 0;
	}

	.skip-list li {
		display: flex;
		align-items: flex-start;
		gap: var(--space-sm);
		margin-bottom: var(--space-sm);
	}

	.skip-icon {
		color: var(--color-danger);
		font-weight: bold;
	}

	.health-check {
		display: flex;
		align-items: flex-start;
		gap: var(--space-md);
		padding: var(--space-md);
		background: var(--color-success-muted);
		border-radius: var(--radius-md);
		margin-bottom: var(--space-lg);
	}

	.health-icon {
		font-size: 1.5rem;
	}

	.health-check p {
		margin: 0;
		font-size: 0.875rem;
	}

	.reminder-offer {
		text-align: center;
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
	}

	.reminder-offer p {
		margin-bottom: var(--space-sm);
	}

	.reminder-set {
		color: var(--color-success);
		display: flex;
		align-items: center;
		justify-content: center;
		gap: var(--space-sm);
	}

	.response-footer {
		margin-top: var(--space-lg);
		padding-top: var(--space-md);
		border-top: 1px solid rgba(255, 255, 255, 0.1);
	}

	/* Comparison Card */
	.comparison-card {
		margin-bottom: var(--space-xl);
	}

	.comparison-quote {
		font-style: italic;
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		margin-bottom: var(--space-sm);
	}

	.comparison-note {
		font-size: 0.75rem;
		color: var(--color-text-subtle);
	}

	/* Navigation */
	.journey-nav {
		display: flex;
		justify-content: center;
		gap: var(--space-md);
		padding: var(--space-xl) 0;
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

	@media (max-width: 640px) {
		.context-grid {
			grid-template-columns: repeat(2, 1fr);
		}

		.constitution-comparison {
			flex-direction: column;
		}

		.switch-arrow {
			transform: rotate(90deg);
		}

		.breadcrumb {
			flex-direction: column;
			align-items: flex-start;
			gap: var(--space-sm);
		}

		.audit-toggle-btn {
			align-self: flex-end;
		}

		.journey-nav {
			flex-direction: column;
			align-items: center;
		}
	}
</style>
