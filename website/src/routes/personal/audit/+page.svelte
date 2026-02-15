<script lang="ts">
	/**
	 * Unified Audit Trail Dashboard
	 * Shows data flow across ALL platforms: JustinGuitar, Yousician, Community, Music Shop
	 */
	import { vcpContext, todayAudit } from '$lib/vcp';
	import { gentianProfile } from '$lib/personas/gentian';

	// Ensure profile is loaded
	$effect(() => {
		if (!$vcpContext) {
			vcpContext.set(gentianProfile);
		}
	});

	const ctx = $derived($vcpContext);

	// Platform data for unified view
	const platforms = [
		{
			id: 'justinguitar',
			name: 'JustinGuitar',
			icon: 'fa-guitar',
			color: 'var(--color-justinguitar)',
			type: 'Learning',
			lastAccess: '2026-01-24 14:30',
			fieldsShared: ['skill_level', 'learning_style', 'noise_mode', 'pace', 'display_name'],
			fieldsWithheld: ['work_schedule', 'housing_details', 'neighbor_situation', 'financial_details'],
			fieldsInfluenced: 2,
			actions: ['Recommended quiet-friendly lessons', 'Filtered content for beginner level']
		},
		{
			id: 'yousician',
			name: 'Yousician',
			icon: 'fa-headphones',
			color: 'var(--color-yousician)',
			type: 'Learning',
			lastAccess: '2026-01-24 15:15',
			fieldsShared: ['skill_level', 'learning_style', 'display_name', 'session_length'],
			fieldsWithheld: ['work_schedule', 'housing_details', 'neighbor_situation', 'financial_details'],
			fieldsInfluenced: 1,
			actions: ['Adapted practice length to 30 min', 'Sync progress from JustinGuitar']
		},
		{
			id: 'musicshop',
			name: 'Barcelona Guitar Shop',
			icon: 'fa-store',
			color: 'var(--color-shop)',
			type: 'Retail',
			lastAccess: '2026-01-24 11:00',
			fieldsShared: ['skill_level', 'budget_tier', 'noise_concern', 'availability_abstract'],
			fieldsWithheld: ['exact_budget', 'work_schedule', 'housing_details', 'neighbor_complaint_history'],
			fieldsInfluenced: 2,
			actions: ['Recommended soundhole cover', 'Suggested quiet practice workshop', 'Offered layaway plan']
		},
		{
			id: 'community',
			name: 'Guitar Community',
			icon: 'fa-users',
			color: 'var(--color-community)',
			type: 'Community',
			lastAccess: '2026-01-24 16:00',
			fieldsShared: ['display_name', 'days_completed', 'days_adjusted_count', 'badges', 'rank'],
			fieldsWithheld: ['adjustment_reasons', 'work_schedule', 'energy_levels', 'health_status'],
			fieldsInfluenced: 3,
			actions: ['Displayed on leaderboard', 'Recorded 3 adjusted days (reasons private)', 'Awarded "Night Owl" badge']
		}
	];

	// Privacy summary stats
	const privacySummary = $derived(() => {
		const totalShared = platforms.reduce((acc, p) => acc + p.fieldsShared.length, 0);
		const totalWithheld = platforms.reduce((acc, p) => acc + p.fieldsWithheld.length, 0);
		const totalInfluenced = platforms.reduce((acc, p) => acc + p.fieldsInfluenced, 0);
		const uniqueWithheld = new Set(platforms.flatMap(p => p.fieldsWithheld)).size;
		return {
			totalShared,
			totalWithheld,
			totalInfluenced,
			uniqueWithheld,
			exposedCount: 0 // Always 0 with VCP
		};
	});

	// All withheld fields across platforms
	const allWithheldFields = $derived(() => {
		const withheld = new Map<string, string[]>();
		for (const p of platforms) {
			for (const field of p.fieldsWithheld) {
				if (!withheld.has(field)) {
					withheld.set(field, []);
				}
				withheld.get(field)!.push(p.name);
			}
		}
		return withheld;
	});

	let activeTab: 'platforms' | 'fields' | 'timeline' = $state('platforms');
</script>

<svelte:head>
	<title>Unified Audit Trail - VCP Demo</title>
</svelte:head>

<div class="container">
	<div class="breadcrumb">
		<a href="/personal">← Back to profile</a>
	</div>

	<header class="audit-header">
		<h1>Unified Audit Trail</h1>
		<p class="text-muted">
			See exactly what data went where across ALL platforms
		</p>
	</header>

	<!-- Privacy Summary -->
	<section class="summary-section">
		<div class="summary-grid">
			<div class="summary-card">
				<span class="summary-icon"><i class="fa-solid fa-share-nodes" aria-hidden="true"></i></span>
				<span class="summary-value">{privacySummary().totalShared}</span>
				<span class="summary-label">Fields Shared</span>
			</div>
			<div class="summary-card">
				<span class="summary-icon"><i class="fa-solid fa-shield-halved" aria-hidden="true"></i></span>
				<span class="summary-value">{privacySummary().uniqueWithheld}</span>
				<span class="summary-label">Fields Protected</span>
			</div>
			<div class="summary-card">
				<span class="summary-icon"><i class="fa-solid fa-wand-magic-sparkles" aria-hidden="true"></i></span>
				<span class="summary-value">{privacySummary().totalInfluenced}</span>
				<span class="summary-label">Private Influences</span>
			</div>
			<div class="summary-card summary-card-highlight">
				<span class="summary-icon"><i class="fa-solid fa-lock" aria-hidden="true"></i></span>
				<span class="summary-value">{privacySummary().exposedCount}</span>
				<span class="summary-label">Private Exposed</span>
			</div>
		</div>
	</section>

	<!-- Tab Navigation -->
	<section class="tab-nav">
		<button
			class="tab-btn"
			class:active={activeTab === 'platforms'}
			onclick={() => activeTab = 'platforms'}
		>
			<i class="fa-solid fa-server" aria-hidden="true"></i>
			By Platform
		</button>
		<button
			class="tab-btn"
			class:active={activeTab === 'fields'}
			onclick={() => activeTab = 'fields'}
		>
			<i class="fa-solid fa-table-cells" aria-hidden="true"></i>
			By Field
		</button>
		<button
			class="tab-btn"
			class:active={activeTab === 'timeline'}
			onclick={() => activeTab = 'timeline'}
		>
			<i class="fa-solid fa-clock-rotate-left" aria-hidden="true"></i>
			Timeline
		</button>
	</section>

	<!-- Platform View -->
	{#if activeTab === 'platforms'}
		<section class="platforms-view">
			{#each platforms as platform}
				<div class="platform-card card" style="--platform-color: {platform.color}">
					<div class="platform-header">
						<div class="platform-info">
							<span class="platform-icon">
								<i class="fa-solid {platform.icon}" aria-hidden="true"></i>
							</span>
							<div>
								<h3>{platform.name}</h3>
								<span class="platform-type">{platform.type}</span>
							</div>
						</div>
						<span class="platform-access">Last: {platform.lastAccess}</span>
					</div>

					<div class="platform-fields">
						<div class="field-section">
							<h4 class="field-section-title field-section-shared">
								<i class="fa-solid fa-check-circle" aria-hidden="true"></i>
								Shared ({platform.fieldsShared.length})
							</h4>
							<div class="field-list">
								{#each platform.fieldsShared as field}
									<span class="field-tag field-tag-shared">{field.replace(/_/g, ' ')}</span>
								{/each}
							</div>
						</div>

						<div class="field-section">
							<h4 class="field-section-title field-section-withheld">
								<i class="fa-solid fa-shield" aria-hidden="true"></i>
								Protected ({platform.fieldsWithheld.length})
							</h4>
							<div class="field-list">
								{#each platform.fieldsWithheld as field}
									<span class="field-tag field-tag-withheld">{field.replace(/_/g, ' ')}</span>
								{/each}
							</div>
						</div>
					</div>

					<div class="platform-actions">
						<h4>Actions Taken</h4>
						<ul class="action-list">
							{#each platform.actions as action}
								<li>{action}</li>
							{/each}
						</ul>
					</div>

					<div class="platform-influence">
						<span class="influence-badge">
							{platform.fieldsInfluenced} private field{platform.fieldsInfluenced !== 1 ? 's' : ''} influenced recommendations
						</span>
					</div>
				</div>
			{/each}
		</section>
	{/if}

	<!-- Field View -->
	{#if activeTab === 'fields'}
		<section class="fields-view">
			<div class="fields-grid">
				<!-- Shared Fields Matrix -->
				<div class="field-matrix card">
					<h3><i class="fa-solid fa-check-circle" aria-hidden="true"></i> Shared Fields</h3>
					<table class="matrix-table">
						<thead>
							<tr>
								<th>Field</th>
								{#each platforms as p}
									<th class="platform-col">
										<i class="fa-solid {p.icon}" aria-hidden="true" style="color: {p.color}"></i>
									</th>
								{/each}
							</tr>
						</thead>
						<tbody>
							{#each ['skill_level', 'learning_style', 'display_name', 'noise_mode', 'pace', 'budget_tier', 'session_length', 'days_completed', 'badges'] as field}
								<tr>
									<td>{field.replace(/_/g, ' ')}</td>
									{#each platforms as p}
										<td class="check-cell">
											{#if p.fieldsShared.includes(field) || p.fieldsShared.includes(field.replace('_tier', '_range'))}
												<span class="check-yes">✓</span>
											{:else}
												<span class="check-no">—</span>
											{/if}
										</td>
									{/each}
								</tr>
							{/each}
						</tbody>
					</table>
				</div>

				<!-- Protected Fields -->
				<div class="protected-fields card">
					<h3><i class="fa-solid fa-shield" aria-hidden="true"></i> Protected Fields</h3>
					<p class="text-sm text-muted" style="margin-bottom: 1rem;">
						These fields were requested but NEVER transmitted
					</p>
					<div class="protected-list">
						{#each allWithheldFields() as [field, platforms]}
							<div class="protected-item">
								<span class="protected-field">{field.replace(/_/g, ' ')}</span>
								<span class="protected-platforms">
									Blocked from: {platforms.join(', ')}
								</span>
							</div>
						{/each}
					</div>
				</div>
			</div>
		</section>
	{/if}

	<!-- Timeline View -->
	{#if activeTab === 'timeline'}
		<section class="timeline-view">
			<div class="timeline">
				<div class="timeline-item" style="--item-color: var(--color-shop)">
					<div class="timeline-marker"></div>
					<div class="timeline-content card">
						<div class="timeline-header">
							<span class="timeline-time">11:00</span>
							<span class="timeline-platform">Barcelona Guitar Shop</span>
						</div>
						<p>Scanned VCP QR code at kiosk</p>
						<div class="timeline-fields">
							<span class="badge badge-success">4 shared</span>
							<span class="badge badge-warning">4 protected</span>
						</div>
						<p class="text-sm text-muted">Got personalized gear recommendations based on budget tier and noise concerns</p>
					</div>
				</div>

				<div class="timeline-item" style="--item-color: var(--color-justinguitar)">
					<div class="timeline-marker"></div>
					<div class="timeline-content card">
						<div class="timeline-header">
							<span class="timeline-time">14:30</span>
							<span class="timeline-platform">JustinGuitar</span>
						</div>
						<p>Continued chord transition lesson</p>
						<div class="timeline-fields">
							<span class="badge badge-success">5 shared</span>
							<span class="badge badge-warning">4 protected</span>
						</div>
						<p class="text-sm text-muted">Quiet-friendly content filtered based on noise constraints (reason not shared)</p>
					</div>
				</div>

				<div class="timeline-item" style="--item-color: var(--color-yousician)">
					<div class="timeline-marker"></div>
					<div class="timeline-content card">
						<div class="timeline-header">
							<span class="timeline-time">15:15</span>
							<span class="timeline-platform">Yousician</span>
						</div>
						<p>Practiced with game mode</p>
						<div class="timeline-fields">
							<span class="badge badge-success">4 shared</span>
							<span class="badge badge-warning">4 protected</span>
						</div>
						<p class="text-sm text-muted">Progress synced from JustinGuitar via VCP</p>
					</div>
				</div>

				<div class="timeline-item" style="--item-color: var(--color-community)">
					<div class="timeline-marker"></div>
					<div class="timeline-content card">
						<div class="timeline-header">
							<span class="timeline-time">16:00</span>
							<span class="timeline-platform">Guitar Community</span>
						</div>
						<p>Checked leaderboard position</p>
						<div class="timeline-fields">
							<span class="badge badge-success">5 shared</span>
							<span class="badge badge-warning">4 protected</span>
						</div>
						<p class="text-sm text-muted">Rank #3 displayed. Adjusted days shown as count only (reasons private)</p>
					</div>
				</div>
			</div>
		</section>
	{/if}

	<!-- Privacy Guarantee -->
	<section class="guarantee-section card">
		<div class="guarantee-header">
			<span class="guarantee-icon"><i class="fa-solid fa-shield-check" aria-hidden="true"></i></span>
			<h3>VCP Privacy Guarantee</h3>
		</div>
		<div class="guarantee-content">
			<p>
				Across 4 platforms today, <strong>0 private fields were exposed</strong>.
				Your work schedule, housing situation, and personal circumstances remained
				completely private while still enabling personalized experiences.
			</p>
			<div class="guarantee-comparison">
				<div class="comparison-item comparison-without">
					<h4>Without VCP</h4>
					<ul>
						<li>Each platform asks for all your data</li>
						<li>No control over what's shared</li>
						<li>Community sees "skipped" not "adjusted"</li>
						<li>Shop sees your bank balance</li>
					</ul>
				</div>
				<div class="comparison-item comparison-with">
					<h4>With VCP</h4>
					<ul>
						<li>You control exactly what's shared</li>
						<li>Private context influences without exposure</li>
						<li>Community sees "adjusted" with dignity</li>
						<li>Shop sees "budget: low" only</li>
					</ul>
				</div>
			</div>
		</div>
	</section>

	<!-- Navigation -->
	<section class="nav-section">
		<a href="/personal" class="btn btn-secondary">
			← Back to Profile
		</a>
		<a href="/professional" class="btn btn-primary">
			Try Professional Demo →
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

	/* Summary Section */
	.summary-section {
		margin-bottom: var(--space-xl);
	}

	.summary-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: var(--space-md);
	}

	.summary-card {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.summary-card-highlight {
		border-color: var(--color-success);
		background: var(--color-success-muted);
	}

	.summary-icon {
		font-size: 1.5rem;
		color: var(--color-text-muted);
		margin-bottom: var(--space-sm);
	}

	.summary-card-highlight .summary-icon {
		color: var(--color-success);
	}

	.summary-value {
		font-size: 2rem;
		font-weight: 700;
	}

	.summary-card-highlight .summary-value {
		color: var(--color-success);
	}

	.summary-label {
		font-size: 0.75rem;
		color: var(--color-text-muted);
		text-transform: uppercase;
	}

	/* Tab Navigation */
	.tab-nav {
		display: flex;
		gap: var(--space-sm);
		margin-bottom: var(--space-xl);
		justify-content: center;
	}

	.tab-btn {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-sm) var(--space-lg);
		background: var(--color-bg-elevated);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-md);
		color: var(--color-text-muted);
		cursor: pointer;
		transition: all var(--transition-fast);
	}

	.tab-btn:hover {
		background: var(--color-bg-card);
		color: var(--color-text);
	}

	.tab-btn.active {
		background: var(--color-primary);
		color: white;
		border-color: var(--color-primary);
	}

	/* Platforms View */
	.platforms-view {
		display: grid;
		gap: var(--space-lg);
	}

	.platform-card {
		border-left: 4px solid var(--platform-color);
	}

	.platform-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--space-lg);
		padding-bottom: var(--space-md);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.platform-info {
		display: flex;
		align-items: center;
		gap: var(--space-md);
	}

	.platform-icon {
		width: 48px;
		height: 48px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		font-size: 1.5rem;
		color: var(--platform-color);
	}

	.platform-info h3 {
		margin-bottom: 0;
	}

	.platform-type {
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.platform-access {
		font-size: 0.75rem;
		color: var(--color-text-subtle);
	}

	.platform-fields {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--space-lg);
		margin-bottom: var(--space-lg);
	}

	.field-section-title {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-size: 0.75rem;
		text-transform: uppercase;
		margin-bottom: var(--space-sm);
	}

	.field-section-shared {
		color: var(--color-success);
	}

	.field-section-withheld {
		color: var(--color-danger);
	}

	.platform-actions h4 {
		font-size: 0.75rem;
		text-transform: uppercase;
		color: var(--color-text-muted);
		margin-bottom: var(--space-sm);
	}

	.action-list {
		margin: 0;
		padding-left: var(--space-lg);
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	.action-list li {
		margin-bottom: var(--space-xs);
	}

	.platform-influence {
		margin-top: var(--space-md);
		padding-top: var(--space-md);
		border-top: 1px solid rgba(255, 255, 255, 0.1);
	}

	.influence-badge {
		font-size: 0.75rem;
		padding: var(--space-xs) var(--space-sm);
		background: var(--color-warning-muted);
		color: var(--color-warning);
		border-radius: var(--radius-sm);
	}

	/* Fields View */
	.fields-grid {
		display: grid;
		gap: var(--space-lg);
	}

	.field-matrix h3,
	.protected-fields h3 {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-lg);
	}

	.matrix-table {
		width: 100%;
		border-collapse: collapse;
	}

	.matrix-table th,
	.matrix-table td {
		padding: var(--space-sm);
		text-align: left;
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.matrix-table th {
		font-size: 0.75rem;
		color: var(--color-text-muted);
		text-transform: uppercase;
	}

	.platform-col {
		text-align: center;
		width: 60px;
	}

	.check-cell {
		text-align: center;
	}

	.check-yes {
		color: var(--color-success);
		font-weight: bold;
	}

	.check-no {
		color: var(--color-text-subtle);
	}

	.protected-list {
		display: flex;
		flex-direction: column;
		gap: var(--space-sm);
	}

	.protected-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: var(--space-sm);
		background: var(--color-danger-muted);
		border-radius: var(--radius-sm);
	}

	.protected-field {
		font-weight: 500;
		color: var(--color-danger);
	}

	.protected-platforms {
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	/* Timeline View */
	.timeline {
		position: relative;
		padding-left: var(--space-xl);
	}

	.timeline::before {
		content: '';
		position: absolute;
		left: 8px;
		top: 0;
		bottom: 0;
		width: 2px;
		background: var(--color-bg-elevated);
	}

	.timeline-item {
		position: relative;
		margin-bottom: var(--space-lg);
	}

	.timeline-marker {
		position: absolute;
		left: calc(-1 * var(--space-xl) + 4px);
		top: var(--space-md);
		width: 12px;
		height: 12px;
		background: var(--item-color);
		border-radius: 50%;
		border: 2px solid var(--color-bg);
	}

	.timeline-content {
		margin-left: var(--space-sm);
	}

	.timeline-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--space-sm);
	}

	.timeline-time {
		font-weight: 600;
		color: var(--color-text-muted);
	}

	.timeline-platform {
		font-size: 0.75rem;
		padding: 2px 8px;
		background: var(--item-color);
		color: white;
		border-radius: var(--radius-sm);
	}

	.timeline-fields {
		display: flex;
		gap: var(--space-sm);
		margin: var(--space-sm) 0;
	}

	/* Guarantee Section */
	.guarantee-section {
		margin-top: var(--space-xl);
		margin-bottom: var(--space-xl);
		border: 2px solid var(--color-success);
	}

	.guarantee-header {
		display: flex;
		align-items: center;
		gap: var(--space-md);
		margin-bottom: var(--space-md);
	}

	.guarantee-icon {
		font-size: 2rem;
		color: var(--color-success);
	}

	.guarantee-comparison {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--space-lg);
		margin-top: var(--space-lg);
	}

	.comparison-item {
		padding: var(--space-md);
		border-radius: var(--radius-md);
	}

	.comparison-without {
		background: var(--color-danger-muted);
	}

	.comparison-with {
		background: var(--color-success-muted);
	}

	.comparison-item h4 {
		margin-bottom: var(--space-sm);
	}

	.comparison-without h4 {
		color: var(--color-danger);
	}

	.comparison-with h4 {
		color: var(--color-success);
	}

	.comparison-item ul {
		margin: 0;
		padding-left: var(--space-lg);
		font-size: 0.875rem;
	}

	.comparison-item li {
		margin-bottom: var(--space-xs);
	}

	/* Navigation */
	.nav-section {
		display: flex;
		justify-content: center;
		gap: var(--space-md);
		padding: var(--space-xl) 0;
	}

	@media (max-width: 768px) {
		.summary-grid {
			grid-template-columns: repeat(2, 1fr);
		}

		.platform-fields {
			grid-template-columns: 1fr;
		}

		.guarantee-comparison {
			grid-template-columns: 1fr;
		}

		.tab-nav {
			flex-wrap: wrap;
		}
	}
</style>
