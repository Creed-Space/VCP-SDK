<script lang="ts">
	/**
	 * JustinGuitar Mock Platform
	 * Shows VCP context loading and personalized content
	 */
	import { vcpContext, vcpConsents, logContextShared } from '$lib/vcp';
	import { gentianProfile } from '$lib/personas/gentian';
	import lessonsData from '$lib/data/lessons.json';
	import { TokenInspector } from '$lib/components/shared';
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
	let showConsent = $state(false);
	let consentGranted = $state(false);

	// Check if consent already exists
	$effect(() => {
		if (vcpConsents.hasConsent('justinguitar')) {
			consentGranted = true;
		} else {
			showConsent = true;
		}
	});

	function grantConsent() {
		vcpConsents.grantConsent(
			'justinguitar',
			['skill_level', 'learning_style'],
			['noise_mode', 'pace', 'session_length']
		);

		logContextShared(
			'justinguitar',
			['skill_level', 'learning_style', 'noise_mode', 'pace', 'display_name'],
			['work_type', 'schedule', 'housing', 'neighbor_situation'],
			2 // noise_restricted + schedule_irregular influenced
		);

		consentGranted = true;
		showConsent = false;
	}

	function denyConsent() {
		showConsent = false;
	}

	// Filter lessons for quiet practice if noise restricted
	const lessons = $derived(() => {
		const all = lessonsData.justinguitar_lessons;
		if (ctx?.constraints?.noise_restricted) {
			return all.filter((l) => l.quiet_friendly);
		}
		return all;
	});

	// Get recommended lesson based on skills
	const recommendedLesson = $derived(() => {
		const currentFocus = ctx?.current_skills?.current_focus;
		if (currentFocus === 'chord_transitions') {
			return lessons().find((l) => l.skills.includes('chord_transitions'));
		}
		return lessons()[0];
	});

	// Transform shared context into AuditPanel entries
	const auditEntries = $derived(() => {
		const entries: { field: string; category: 'shared' | 'withheld' | 'influenced'; value?: string; reason?: string; stakeholder?: string }[] = [];

		// Shared fields (what JustinGuitar received)
		const sharedFields = ['skill_level', 'learning_style', 'noise_mode', 'pace', 'display_name'];
		for (const field of sharedFields) {
			let value = ctx?.public_profile?.[field as keyof typeof ctx.public_profile];
			if (field === 'display_name') value = ctx?.public_profile?.display_name;
			if (field === 'noise_mode') value = ctx?.constraints?.noise_restricted ? 'quiet' : 'normal';
			entries.push({
				field: field.replace(/_/g, ' '),
				category: 'shared',
				value: String(value ?? '—').replace(/_/g, ' '),
				stakeholder: 'JustinGuitar'
			});
		}

		// Influenced fields (private context affecting recommendations)
		if (ctx?.constraints?.noise_restricted) {
			entries.push({
				field: 'noise restricted',
				category: 'influenced',
				value: 'true',
				reason: 'Filtering to quiet-friendly lessons'
			});
		}
		if (ctx?.constraints?.schedule_irregular) {
			entries.push({
				field: 'schedule irregular',
				category: 'influenced',
				value: 'true',
				reason: 'Preferring self-paced content'
			});
		}

		// Withheld fields (never exposed)
		const withheldFields = ['work_type', 'schedule', 'housing', 'neighbor_situation'];
		for (const field of withheldFields) {
			entries.push({
				field: field.replace(/_/g, ' '),
				category: 'withheld',
				reason: 'Private - not transmitted to platforms'
			});
		}

		return entries;
	});
</script>

<svelte:head>
	<title>JustinGuitar - VCP Demo</title>
</svelte:head>

<!-- Consent Dialog -->
{#if showConsent}
	<div class="consent-overlay">
		<div class="consent-dialog card">
			<h2>Connect Your VCP Profile</h2>
			<p class="text-muted">
				JustinGuitar would like to personalize your experience using your VCP context.
			</p>

			<div class="consent-sections">
				<div class="consent-section">
					<h4>Required for personalization:</h4>
					<ul class="consent-list">
						<li class="consent-item consent-required">
							<span>skill_level</span>
							<span class="consent-note">To recommend appropriate lessons</span>
						</li>
						<li class="consent-item consent-required">
							<span>learning_style</span>
							<span class="consent-note">To match teaching approach</span>
						</li>
					</ul>
				</div>

				<div class="consent-section">
					<h4>Optional (improves experience):</h4>
					<ul class="consent-list">
						<li class="consent-item consent-optional">
							<span>noise_mode</span>
							<span class="consent-note">For quiet practice suggestions</span>
						</li>
						<li class="consent-item consent-optional">
							<span>pace</span>
							<span class="consent-note">To adjust lesson speed</span>
						</li>
						<li class="consent-item consent-optional">
							<span>session_length</span>
							<span class="consent-note">To fit your available time</span>
						</li>
					</ul>
				</div>
			</div>

			<div class="privacy-note">
				<span class="privacy-note-icon">🔒</span>
				<span>
					Your private context (work schedule, housing situation) is NEVER shared.
					Only the fields listed above are transmitted.
				</span>
			</div>

			<div class="consent-actions">
				<button class="btn btn-secondary" onclick={denyConsent}>Deny</button>
				<button class="btn btn-primary" onclick={grantConsent}>Allow</button>
			</div>
		</div>
	</div>
{/if}

<div class="page-layout" class:audit-open={showAuditPanel}>
	<div class="main-content">
		<div class="platform-frame platform-frame-justinguitar">
			<div class="platform-header platform-header-justinguitar">
				<div class="platform-brand">
					<span class="platform-logo">🎸</span>
					<span class="platform-name">JustinGuitar</span>
				</div>
				<div class="header-actions">
					{#if consentGranted}
						<div class="vcp-badge">VCP Connected</div>
					{/if}
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
		{#if consentGranted && ctx}
			<div class="welcome-banner">
				<h1>Welcome back, {ctx.public_profile.display_name}!</h1>
				<p class="text-muted">
					Level: {ctx.public_profile.experience} • {ctx.current_skills?.weeks_learning} weeks learning
				</p>
			</div>

			<!-- Personalized recommendation -->
			{#if recommendedLesson()}
				<section class="recommendation-section">
					<h2>Recommended for You</h2>
					<div class="lesson-card featured">
						<div class="lesson-header">
							<h3>{recommendedLesson()?.title}</h3>
							<span class="badge badge-primary">Personalized</span>
						</div>
						<p class="lesson-description">{recommendedLesson()?.description}</p>
						<div class="lesson-meta">
							<span>⏱️ {recommendedLesson()?.duration_minutes} min</span>
							<span>📚 {recommendedLesson()?.module}</span>
							{#if recommendedLesson()?.quiet_friendly}
								<span class="badge badge-success">🔇 Quiet Friendly</span>
							{/if}
						</div>
						<div class="lesson-reason">
							<span class="reason-icon">💡</span>
							<span>
								Recommended because your current focus is "{ctx.current_skills?.current_focus?.replace(/_/g, ' ')}"
							</span>
						</div>
						<button class="btn btn-primary">Start Lesson →</button>
					</div>
				</section>
			{/if}

			<!-- Quiet practice tip if noise restricted -->
			{#if ctx.constraints?.noise_restricted}
				<div class="quiet-tip card">
					<span class="tip-icon">🔇</span>
					<div>
						<strong>Quiet Practice Mode Active</strong>
						<p class="text-sm text-muted">
							Based on your preferences, we're showing lessons suitable for quiet practice.
							No amp required!
						</p>
					</div>
				</div>
			{/if}

			<!-- Lesson list -->
			<section class="lessons-section">
				<h2>Your Lessons</h2>
				<div class="lessons-list">
					{#each lessons() as lesson}
						<div class="lesson-card">
							<div class="lesson-header">
								<h3>{lesson.title}</h3>
								{#if lesson.quiet_friendly}
									<span class="badge badge-success text-xs">🔇</span>
								{/if}
							</div>
							<p class="text-sm text-muted">{lesson.description}</p>
							<div class="lesson-meta text-xs">
								<span>⏱️ {lesson.duration_minutes} min</span>
								<span>📚 {lesson.module}</span>
							</div>
						</div>
					{/each}
				</div>
			</section>

			<!-- What was shared -->
			<section class="shared-info card">
				<h3>What JustinGuitar Received</h3>
				<div class="field-list" style="margin-top: 0.5rem;">
					<span class="field-tag field-tag-shared">skill_level</span>
					<span class="field-tag field-tag-shared">learning_style</span>
					<span class="field-tag field-tag-shared">noise_mode</span>
					<span class="field-tag field-tag-shared">pace</span>
					<span class="field-tag field-tag-shared">display_name</span>
				</div>
				<p class="text-sm text-muted" style="margin-top: 1rem;">
					<strong>Not shared:</strong> work_type, schedule, housing, neighbor_situation
				</p>
			</section>

			<!-- VCP Token Inspector -->
			<section class="token-section">
				<TokenInspector context={ctx} showLegend={true} showSummary={true} />
			</section>
		{:else if !showConsent}
			<div class="no-vcp">
				<h2>VCP Not Connected</h2>
				<p class="text-muted">Connect your VCP profile for a personalized experience.</p>
				<button class="btn btn-primary" onclick={() => (showConsent = true)}>
					Connect VCP
				</button>
			</div>
		{/if}
		</div>
	</div>

	<div class="container-narrow" style="margin-top: 2rem;">
		<div class="nav-links">
			<a href="/personal" class="btn btn-ghost">← Back to Profile</a>
			<a href="/personal/platforms/yousician" class="btn btn-primary">
				Try Yousician →
			</a>
		</div>
	</div>
	</div>

	<!-- Audit Sidebar -->
	{#if showAuditPanel && consentGranted}
		<aside class="audit-sidebar">
			<AuditPanel
				entries={auditEntries()}
				title="Real-Time Audit"
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

	.consent-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.8);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
		padding: var(--space-lg);
	}

	.consent-dialog {
		max-width: 500px;
		width: 100%;
	}

	.consent-dialog h2 {
		margin-bottom: var(--space-sm);
	}

	.consent-sections {
		margin: var(--space-lg) 0;
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
		display: flex;
		justify-content: space-between;
		padding: var(--space-sm);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-sm);
		margin-bottom: var(--space-xs);
		font-size: 0.875rem;
	}

	.consent-required {
		border-left: 3px solid var(--color-primary);
	}

	.consent-optional {
		border-left: 3px solid var(--color-text-subtle);
	}

	.consent-note {
		color: var(--color-text-subtle);
		font-size: 0.75rem;
	}

	.consent-actions {
		display: flex;
		gap: var(--space-md);
		justify-content: flex-end;
		margin-top: var(--space-lg);
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
		color: var(--color-justinguitar);
	}

	.welcome-banner {
		margin-bottom: var(--space-xl);
	}

	.welcome-banner h1 {
		color: var(--color-justinguitar);
	}

	.recommendation-section {
		margin-bottom: var(--space-xl);
	}

	.lesson-card {
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		padding: var(--space-md);
		margin-bottom: var(--space-md);
	}

	.lesson-card.featured {
		border: 2px solid var(--color-justinguitar);
	}

	.lesson-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: var(--space-sm);
	}

	.lesson-description {
		color: var(--color-text-muted);
		font-size: 0.875rem;
		margin-bottom: var(--space-md);
	}

	.lesson-meta {
		display: flex;
		gap: var(--space-md);
		font-size: 0.875rem;
		color: var(--color-text-muted);
		margin-bottom: var(--space-md);
	}

	.lesson-reason {
		display: flex;
		align-items: flex-start;
		gap: var(--space-sm);
		padding: var(--space-sm);
		background: rgba(255, 107, 53, 0.1);
		border-radius: var(--radius-sm);
		font-size: 0.875rem;
		margin-bottom: var(--space-md);
	}

	.quiet-tip {
		display: flex;
		align-items: flex-start;
		gap: var(--space-md);
		background: var(--color-success-muted);
		border: 1px solid var(--color-success);
		margin-bottom: var(--space-xl);
	}

	.tip-icon {
		font-size: 1.5rem;
	}

	.lessons-section {
		margin-bottom: var(--space-xl);
	}

	.lessons-list {
		display: grid;
		gap: var(--space-md);
	}

	.shared-info {
		margin-bottom: var(--space-xl);
	}

	.no-vcp {
		text-align: center;
		padding: var(--space-2xl);
	}

	.nav-links {
		display: flex;
		justify-content: space-between;
	}

	.token-section {
		margin-bottom: var(--space-xl);
	}
</style>
