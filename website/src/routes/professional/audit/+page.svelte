<script lang="ts">
	/**
	 * Professional Demo - Dual Audit Trail
	 * Shows what employee sees vs what HR sees
	 */
	import {
		vcpContext,
		todayAudit,
		getStakeholderView,
		getAuditSummary
	} from '$lib/vcp';
	import { campionProfile, getCampionPrivacyComparison } from '$lib/personas/campion';

	// Ensure profile is loaded
	$effect(() => {
		if (!$vcpContext) {
			vcpContext.set(campionProfile);
		}
	});

	let activeView: 'employee' | 'hr' = $state('employee');
	const ctx = $derived($vcpContext);
	const auditEntries = $derived($todayAudit);
	const hrView = $derived(getStakeholderView(auditEntries, 'hr'));
	const summary = $derived(getAuditSummary(auditEntries));
	const comparison = getCampionPrivacyComparison();

	function formatTime(timestamp: string): string {
		return new Date(timestamp).toLocaleTimeString('en-US', {
			hour: '2-digit',
			minute: '2-digit'
		});
	}
</script>

<svelte:head>
	<title>Audit Trail - Professional Demo</title>
</svelte:head>

<div class="container-narrow">
	<div class="breadcrumb">
		<a href="/professional/morning">← Back to recommendations</a>
	</div>

	<header class="audit-header">
		<h1>Audit Trail</h1>
		<p class="audit-subtitle">
			See exactly what was shared and what stayed private.
		</p>
	</header>

	<!-- View Toggle -->
	<section class="view-toggle-section">
		<div class="view-toggle">
			<button
				class="view-toggle-btn"
				class:active={activeView === 'employee'}
				onclick={() => (activeView = 'employee')}
			>
				👤 Employee View
			</button>
			<button
				class="view-toggle-btn"
				class:active={activeView === 'hr'}
				onclick={() => (activeView = 'hr')}
			>
				🏢 HR View
			</button>
		</div>
		<p class="text-sm text-muted" style="margin-top: 0.5rem;">
			{activeView === 'employee'
				? 'What Campion sees - full detail including private context'
				: 'What HR sees - compliance only, no private details'}
		</p>
	</section>

	<!-- Comparison Cards -->
	<section class="comparison-grid">
		<!-- Employee View Column -->
		<div class="comparison-column comparison-column-user" class:active={activeView === 'employee'}>
			<div class="column-header">
				<h3>👤 Employee View</h3>
				<span class="badge badge-success">Full Access</span>
			</div>

			{#if activeView === 'employee'}
				<div class="audit-entries">
					{#each auditEntries as entry}
						<div class="audit-entry animate-fade-in">
							<div class="audit-entry-time">{formatTime(entry.timestamp)}</div>
							<div class="audit-entry-title">
								{entry.event_type.replace(/_/g, ' ')}
							</div>

							<div class="entry-detail">
								<h5>Fields Shared:</h5>
								<div class="field-list">
									{#each entry.data_shared || [] as field}
										<span class="field-tag field-tag-shared">{field}</span>
									{/each}
								</div>
							</div>

							<div class="entry-detail">
								<h5>Fields Withheld:</h5>
								<div class="field-list">
									{#each entry.data_withheld || [] as field}
										<span class="field-tag field-tag-withheld">{field}</span>
									{/each}
								</div>
							</div>

							<div class="entry-detail">
								<h5>Private Context Influence:</h5>
								<p class="text-sm">
									{entry.private_fields_influenced} private constraints influenced this recommendation
								</p>
							</div>
						</div>
					{:else}
						<p class="text-muted text-center">No audit entries today</p>
					{/each}
				</div>

				<div class="privacy-summary">
					<h4>Your Private Context</h4>
					<p class="text-sm text-muted">Only you can see the reasons behind your constraints:</p>
					<ul class="private-reasons">
						<li>
							<span class="reason-flag">time_limited</span>
							<span class="reason-detail">→ Single parent, childcare 08:00-15:00</span>
						</li>
						<li>
							<span class="reason-flag">health_considerations</span>
							<span class="reason-detail">→ Chronic condition, regular appointments</span>
						</li>
						<li>
							<span class="reason-flag">schedule_irregular</span>
							<span class="reason-detail">→ School pickup affects availability</span>
						</li>
					</ul>
				</div>
			{/if}
		</div>

		<!-- HR View Column -->
		<div class="comparison-column comparison-column-stakeholder" class:active={activeView === 'hr'}>
			<div class="column-header">
				<h3>🏢 HR View</h3>
				<span class="badge badge-warning">Compliance Only</span>
			</div>

			{#if activeView === 'hr'}
				<div class="audit-entries">
					{#each hrView as entry}
						<div class="audit-entry animate-fade-in">
							<div class="audit-entry-time">{formatTime(entry.timestamp)}</div>
							<div class="audit-entry-title">
								{entry.event_type.replace(/_/g, ' ')}
							</div>

							<div class="compliance-checks">
								{#if entry.compliance_status}
									<div class="compliance-item">
										<span class="check-icon">
											{entry.compliance_status.policy_followed ? '✅' : '❌'}
										</span>
										<span>Policy Followed</span>
									</div>
									<div class="compliance-item">
										<span class="check-icon">
											{entry.compliance_status.budget_compliant ? '✅' : '❌'}
										</span>
										<span>Budget Compliant</span>
									</div>
									<div class="compliance-item">
										<span class="check-icon">
											{entry.compliance_status.mandatory_addressed ? '✅' : '❌'}
										</span>
										<span>Mandatory Training Addressed</span>
									</div>
								{/if}
							</div>

							<div class="privacy-indicator">
								<div class="privacy-row">
									<span>Private context used:</span>
									<span class="badge {entry.private_context_used ? 'badge-warning' : 'badge-success'}">
										{entry.private_context_used ? 'Yes' : 'No'}
									</span>
								</div>
								<div class="privacy-row">
									<span>Private context exposed:</span>
									<span class="badge badge-success">No</span>
								</div>
							</div>
						</div>
					{:else}
						<p class="text-muted text-center">No audit entries today</p>
					{/each}
				</div>

				<div class="hr-note privacy-note">
					<span class="privacy-note-icon">ℹ️</span>
					<div>
						<strong>What HR Cannot See:</strong>
						<ul class="hidden-list">
							<li>Why time is limited</li>
							<li>What health considerations exist</li>
							<li>Personal family details</li>
							<li>Specific constraint reasons</li>
						</ul>
						<p class="text-sm text-muted" style="margin-top: 0.5rem;">
							HR knows private context influenced recommendations, but cannot access the details.
							This protects employee privacy while maintaining compliance visibility.
						</p>
					</div>
				</div>
			{/if}
		</div>
	</section>

	<!-- Summary Stats -->
	<section class="card summary-card">
		<h3>Today's Summary</h3>
		<div class="summary-grid">
			<div class="summary-stat">
				<span class="stat-value">{summary.totalEvents}</span>
				<span class="stat-label">Events</span>
			</div>
			<div class="summary-stat">
				<span class="stat-value">{summary.fieldsSharedCount}</span>
				<span class="stat-label">Fields Shared</span>
			</div>
			<div class="summary-stat">
				<span class="stat-value">{summary.fieldsWithheldCount}</span>
				<span class="stat-label">Fields Withheld</span>
			</div>
			<div class="summary-stat">
				<span class="stat-value stat-highlight">{summary.privateExposedCount}</span>
				<span class="stat-label">Private Exposed</span>
			</div>
		</div>
	</section>

	<!-- Navigation -->
	<section class="journey-nav">
		<a href="/professional" class="btn btn-secondary">
			← Back to Profile
		</a>
		<a href="/" class="btn btn-primary">
			Try Personal Demo →
		</a>
	</section>
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

	.audit-header {
		text-align: center;
		margin-bottom: var(--space-xl);
	}

	.audit-subtitle {
		color: var(--color-text-muted);
	}

	.view-toggle-section {
		text-align: center;
		margin-bottom: var(--space-xl);
	}

	.comparison-column {
		opacity: 0.5;
		transition: opacity var(--transition-normal);
	}

	.comparison-column.active {
		opacity: 1;
	}

	.column-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--space-lg);
		padding-bottom: var(--space-md);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.audit-entries {
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
		margin-bottom: var(--space-lg);
	}

	.entry-detail {
		margin-top: var(--space-sm);
	}

	.entry-detail h5 {
		font-size: 0.75rem;
		color: var(--color-text-subtle);
		margin-bottom: var(--space-xs);
	}

	.compliance-checks {
		display: flex;
		flex-direction: column;
		gap: var(--space-sm);
		margin-top: var(--space-md);
	}

	.compliance-item {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-size: 0.875rem;
	}

	.privacy-indicator {
		margin-top: var(--space-md);
		padding-top: var(--space-md);
		border-top: 1px solid rgba(255, 255, 255, 0.1);
	}

	.privacy-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--space-sm);
		font-size: 0.875rem;
	}

	.privacy-summary {
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
	}

	.privacy-summary h4 {
		margin-bottom: var(--space-sm);
	}

	.private-reasons {
		list-style: none;
		margin-top: var(--space-md);
	}

	.private-reasons li {
		display: flex;
		align-items: flex-start;
		gap: var(--space-sm);
		margin-bottom: var(--space-sm);
		font-size: 0.875rem;
	}

	.reason-flag {
		font-family: var(--font-mono);
		background: var(--color-warning-muted);
		color: var(--color-warning);
		padding: 2px var(--space-sm);
		border-radius: var(--radius-sm);
		font-size: 0.75rem;
	}

	.reason-detail {
		color: var(--color-text-muted);
	}

	.hr-note {
		margin-top: var(--space-lg);
	}

	.hidden-list {
		margin: var(--space-sm) 0;
		padding-left: var(--space-lg);
	}

	.hidden-list li {
		color: var(--color-danger);
		font-size: 0.875rem;
		margin-bottom: var(--space-xs);
	}

	.summary-card {
		margin-top: var(--space-xl);
		margin-bottom: var(--space-xl);
	}

	.summary-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: var(--space-md);
		margin-top: var(--space-md);
	}

	.summary-stat {
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

	.stat-value.stat-highlight {
		color: var(--color-success);
	}

	.stat-label {
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.journey-nav {
		display: flex;
		justify-content: center;
		gap: var(--space-md);
		padding: var(--space-xl) 0;
	}

	@media (max-width: 768px) {
		.summary-grid {
			grid-template-columns: repeat(2, 1fr);
		}

		.journey-nav {
			flex-direction: column;
			align-items: center;
		}
	}
</style>
