<script lang="ts">
	/**
	 * Professional Demo - Morning Recommendation Journey
	 * Shows how VCP filters context for course recommendations
	 */
	import { vcpContext, logRecommendation } from '$lib/vcp';
	import { campionProfile, getCampionRecommendationContext } from '$lib/personas/campion';
	import coursesData from '$lib/data/courses.json';
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
	const recommendationContext = getCampionRecommendationContext();

	// Get courses sorted by priority
	const courses = $derived(
		coursesData.courses.sort((a, b) => {
			const priority = { required: 0, recommended: 1, deferred: 2 };
			return (priority[a.priority as keyof typeof priority] ?? 2) -
				(priority[b.priority as keyof typeof priority] ?? 2);
		})
	);

	// Calculate budget
	const budgetTotal = coursesData.budget.annual_total_eur;
	const budgetSpent = coursesData.budget.spent_eur;
	const budgetRemaining = coursesData.budget.remaining_eur;
	const budgetUsedPercent = $derived((budgetSpent / budgetTotal) * 100);

	// Transform recommendation context into AuditPanel entries
	const auditEntries = $derived(() => {
		const entries: { field: string; category: 'shared' | 'withheld' | 'influenced'; value?: string; reason?: string; stakeholder?: string }[] = [];

		// Shared fields
		for (const field of recommendationContext.contextUsed) {
			const [name, value] = field.split(':').map((s) => s.trim());
			entries.push({
				field: name.replace(/_/g, ' '),
				category: 'shared',
				value: value?.replace(/_/g, ' '),
				stakeholder: 'TechCorp LMS'
			});
		}

		// Influenced fields (private context that affects recommendations)
		for (const field of recommendationContext.contextInfluencing) {
			const match = field.match(/^([^:]+):\s*([^(]+)(?:\(([^)]+)\))?/);
			if (match) {
				entries.push({
					field: match[1].replace(/_/g, ' '),
					category: 'influenced',
					value: match[2].trim(),
					reason: match[3]
				});
			}
		}

		// Withheld fields (never exposed)
		for (const field of recommendationContext.contextWithheld) {
			entries.push({
				field: field.replace(/_/g, ' '),
				category: 'withheld',
				reason: 'Private - not transmitted to platforms'
			});
		}

		return entries;
	});

	// Log the recommendation on mount
	$effect(() => {
		logRecommendation(
			'techcorp-lms',
			recommendationContext.contextUsed,
			recommendationContext.contextWithheld,
			{
				budget_compliant: true,
				mandatory_addressed: true,
				progress_summary: 'Course recommendations generated'
			}
		);
	});

	function getPriorityBadge(priority: string) {
		switch (priority) {
			case 'required':
				return { class: 'badge-danger', text: 'Required' };
			case 'recommended':
				return { class: 'badge-success', text: 'Recommended' };
			case 'deferred':
				return { class: 'badge-warning', text: 'Deferred' };
			default:
				return { class: 'badge-primary', text: priority };
		}
	}

	function formatDuration(course: typeof courses[0]): string {
		if (course.duration_hours) {
			return `${course.duration_hours} hours`;
		}
		if (course.duration_weeks && course.hours_per_week) {
			return `${course.duration_weeks} weeks (${course.hours_per_week}h/week)`;
		}
		return 'Self-paced';
	}
</script>

<svelte:head>
	<title>Morning Recommendations - Professional Demo</title>
</svelte:head>

<div class="page-layout" class:audit-open={showAuditPanel}>
	<div class="main-content container-narrow">
		<div class="breadcrumb">
			<a href="/professional">← Back to profile</a>
			<button
				class="audit-toggle-btn"
				onclick={() => showAuditPanel = !showAuditPanel}
				aria-label={showAuditPanel ? 'Hide audit panel' : 'Show audit panel'}
			>
				<i class="fa-solid fa-clipboard-list" aria-hidden="true"></i>
				{showAuditPanel ? 'Hide' : 'Show'} Audit
			</button>
		</div>

		<header class="journey-header">
		<span class="badge badge-primary">Morning Journey</span>
		<h1>Course Recommendations</h1>
		<p class="journey-subtitle">
			Campion asks: "What courses should I take to become a Tech Lead?"
		</p>
	</header>

	<!-- Budget Overview -->
	<section class="card budget-card">
		<div class="budget-header">
			<h3>Training Budget</h3>
			<span class="budget-amount">€{budgetRemaining.toLocaleString()} remaining</span>
		</div>
		<div class="progress">
			<div class="progress-bar" style="width: {budgetUsedPercent}%"></div>
		</div>
		<div class="budget-labels">
			<span class="text-sm text-muted">€{budgetSpent.toLocaleString()} used</span>
			<span class="text-sm text-muted">€{budgetTotal.toLocaleString()} total</span>
		</div>
	</section>

	<!-- Context Used -->
	<section class="card context-card">
		<h3>Context Used for Recommendations</h3>
		<div class="context-grid">
			<div class="context-section">
				<h4>Shared with LMS</h4>
				<div class="field-list">
					{#each recommendationContext.contextUsed as field}
						<span class="field-tag field-tag-shared">{field}</span>
					{/each}
				</div>
			</div>
			<div class="context-section">
				<h4>Influenced (Not Exposed)</h4>
				<div class="field-list">
					{#each recommendationContext.contextInfluencing as field}
						<span class="field-tag">{field.split('(')[0].trim()}</span>
					{/each}
				</div>
			</div>
		</div>
	</section>

	<!-- Recommendations -->
	<section class="recommendations">
		<h2>Recommended Courses</h2>

		{#each courses as course}
			{@const badge = getPriorityBadge(course.priority ?? 'recommended')}
			<article class="card course-card">
				<div class="course-header">
					<div class="course-title-row">
						<h3>{course.title}</h3>
						<span class="badge {badge.class}">{badge.text}</span>
					</div>
					<p class="course-id text-subtle text-xs">{course.id}</p>
				</div>

				<p class="course-description">{course.description}</p>

				<div class="course-meta">
					<span class="meta-item">
						<span class="meta-icon">⏱️</span>
						{formatDuration(course)}
					</span>
					<span class="meta-item">
						<span class="meta-icon">💶</span>
						€{course.price_eur}
					</span>
					<span class="meta-item">
						<span class="meta-icon">📚</span>
						{course.format.replace(/_/g, ' ')}
					</span>
				</div>

				<div class="course-reasoning">
					<span class="reasoning-icon">💡</span>
					<span>{course.reasoning}</span>
				</div>

				{#if course.defer_reason}
					<div class="defer-note">
						<span class="defer-icon">⏳</span>
						<span>{course.defer_reason}</span>
					</div>
				{/if}

				{#if course.deadline}
					<div class="deadline-note">
						<span class="deadline-icon">⚠️</span>
						<span>Deadline: {new Date(course.deadline).toLocaleDateString()}</span>
					</div>
				{/if}
			</article>
		{/each}
	</section>

	<!-- Privacy Note -->
	<section class="privacy-note">
		<span class="privacy-note-icon">🔒</span>
		<div>
			<strong>What stays private:</strong>
			<p class="text-sm" style="margin-top: 0.25rem;">
				{recommendationContext.contextWithheld.join(', ')}
			</p>
			<p class="text-sm text-muted" style="margin-top: 0.5rem;">
				The LMS knows constraints exist (e.g., "time_limited: true") but not WHY.
				Campion's family situation and health details remain private.
			</p>
		</div>
	</section>

	<!-- Navigation -->
	<section class="journey-nav">
		<a href="/professional/audit" class="btn btn-primary">
			View Audit Trail →
		</a>
		<p class="text-sm text-muted" style="margin-top: 0.5rem;">
			See what Campion sees vs what HR sees
		</p>
	</section>
	</div>

	<!-- Audit Sidebar -->
	{#if showAuditPanel}
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

	.budget-card {
		margin-bottom: var(--space-lg);
	}

	.budget-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--space-md);
	}

	.budget-amount {
		font-size: 1.25rem;
		font-weight: 600;
		color: var(--color-success);
	}

	.budget-labels {
		display: flex;
		justify-content: space-between;
		margin-top: var(--space-sm);
	}

	.context-card {
		margin-bottom: var(--space-xl);
	}

	.context-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--space-lg);
		margin-top: var(--space-md);
	}

	.context-section h4 {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		margin-bottom: var(--space-sm);
	}

	.recommendations {
		margin-bottom: var(--space-xl);
	}

	.recommendations h2 {
		margin-bottom: var(--space-lg);
	}

	.course-card {
		margin-bottom: var(--space-md);
	}

	.course-header {
		margin-bottom: var(--space-md);
	}

	.course-title-row {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: var(--space-md);
	}

	.course-title-row h3 {
		font-size: 1.125rem;
	}

	.course-description {
		color: var(--color-text-muted);
		font-size: 0.875rem;
		margin-bottom: var(--space-md);
	}

	.course-meta {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-md);
		margin-bottom: var(--space-md);
	}

	.meta-item {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	.course-reasoning {
		display: flex;
		align-items: flex-start;
		gap: var(--space-sm);
		padding: var(--space-sm);
		background: var(--color-primary-muted);
		border-radius: var(--radius-md);
		font-size: 0.875rem;
	}

	.defer-note {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-sm);
		background: var(--color-warning-muted);
		border-radius: var(--radius-md);
		font-size: 0.875rem;
		margin-top: var(--space-sm);
		color: var(--color-warning);
	}

	.deadline-note {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-top: var(--space-sm);
		font-size: 0.875rem;
		color: var(--color-danger);
	}

	.journey-nav {
		text-align: center;
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
			grid-template-columns: 1fr;
		}

		.course-title-row {
			flex-direction: column;
			gap: var(--space-sm);
		}

		.breadcrumb {
			flex-direction: column;
			align-items: flex-start;
			gap: var(--space-sm);
		}

		.audit-toggle-btn {
			align-self: flex-end;
		}
	}
</style>
