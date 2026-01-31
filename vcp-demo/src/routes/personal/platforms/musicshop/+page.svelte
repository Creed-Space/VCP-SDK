<script lang="ts">
	/**
	 * Music Shop Kiosk - Physical Retail VCP Demo
	 * Shows how VCP context works in a brick-and-mortar scenario
	 * User scans QR code, shop kiosk receives filtered context
	 */
	import { vcpContext, vcpConsents, logContextShared } from '$lib/vcp';
	import { gentianProfile } from '$lib/personas/gentian';
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
	let showQRScan = $state(true);

	// Check if consent already exists
	$effect(() => {
		if (vcpConsents.hasConsent('musicshop')) {
			consentGranted = true;
			showQRScan = false;
		} else {
			showConsent = false;
			showQRScan = true;
		}
	});

	function scanQR() {
		showQRScan = false;
		showConsent = true;
	}

	function grantConsent() {
		vcpConsents.grantConsent(
			'musicshop',
			['skill_level', 'budget_range'],
			['noise_concern', 'learning_goals']
		);

		logContextShared(
			'musicshop',
			['skill_level', 'budget_range', 'noise_concern', 'display_name', 'availability_abstract'],
			['work_schedule', 'housing_details', 'neighbor_situation', 'financial_details'],
			2 // noise_restricted + budget_limited influenced
		);

		consentGranted = true;
		showConsent = false;
	}

	function denyConsent() {
		showConsent = false;
		showQRScan = true;
	}

	// Shop recommendations based on VCP context
	const recommendations = $derived(() => {
		if (!ctx) return [];

		const recs = [];

		// Always recommend soundhole cover for noise-restricted users
		if (ctx.constraints?.noise_restricted) {
			recs.push({
				id: 'soundhole-cover',
				name: 'Soundhole Cover',
				price: 12,
				reason: 'Reduces acoustic volume 60% - perfect for apartment practice',
				category: 'essential',
				vcp_match: 'noise_restricted: true'
			});
		}

		// Budget-conscious recommendations
		if (ctx.constraints?.budget_limited) {
			recs.push({
				id: 'used-electric',
				name: 'Used Electric + Headphones Bundle',
				price: 180,
				reason: 'Silent practice option, 6-month layaway available',
				category: 'upgrade',
				vcp_match: 'budget_limited: true + noise_restricted: true',
				financing: 'In-store layaway: €30/month'
			});
		}

		// Beginner-specific items
		if (ctx.public_profile?.experience === 'beginner') {
			recs.push({
				id: 'finger-trainers',
				name: 'Finger Strength Trainers',
				price: 8,
				reason: 'Build calluses faster - great for beginners',
				category: 'accessory',
				vcp_match: 'experience: beginner'
			});
		}

		return recs;
	});

	// Workshop based on availability
	const workshop = $derived(() => {
		const availability = ctx?.availability?.best_times || [];
		if (availability.includes('saturday_afternoon')) {
			return {
				title: 'Quiet Practice Techniques',
				time: 'Saturday 2pm',
				location: 'Back room',
				price: 'Free',
				reason: 'Matches your Saturday availability + noise concerns'
			};
		}
		return null;
	});

	// Transform context into AuditPanel entries
	const auditEntries = $derived(() => {
		const entries: {
			field: string;
			category: 'shared' | 'withheld' | 'influenced';
			value?: string;
			reason?: string;
			stakeholder?: string;
		}[] = [];

		// Shared fields
		const sharedFields = [
			{ field: 'skill_level', value: 'beginner' },
			{ field: 'budget_range', value: 'low' },
			{ field: 'noise_concern', value: 'true' },
			{ field: 'display_name', value: ctx?.public_profile?.display_name }
		];
		for (const { field, value } of sharedFields) {
			entries.push({
				field: field.replace(/_/g, ' '),
				category: 'shared',
				value: String(value ?? ''),
				stakeholder: 'Music Shop Kiosk'
			});
		}

		// Influenced fields
		entries.push({
			field: 'availability abstract',
			category: 'influenced',
			value: 'Saturday afternoon',
			reason: 'Workshop timing matched to availability'
		});

		// Withheld fields
		const withheldFields = [
			{ field: 'work schedule', reason: 'Factory shift details - private' },
			{ field: 'exact budget', reason: 'Only tier shared, not amount' },
			{ field: 'housing details', reason: 'Apartment specifics - private' },
			{ field: 'neighbor situation', reason: 'Complaint history - private' }
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
</script>

<svelte:head>
	<title>Music Shop - VCP Demo</title>
</svelte:head>

<!-- QR Scan Screen -->
{#if showQRScan}
	<div class="qr-scan-overlay">
		<div class="qr-scan-dialog card">
			<div class="qr-icon">
				<i class="fa-solid fa-qrcode" aria-hidden="true"></i>
			</div>
			<h2>Barcelona Guitar Shop</h2>
			<p class="text-muted">Scan your VCP QR code at the kiosk</p>

			<div class="qr-preview">
				<div class="qr-placeholder">
					<i class="fa-solid fa-mobile-screen" aria-hidden="true"></i>
					<span>Your VCP Profile</span>
				</div>
			</div>

			<button class="btn btn-primary btn-lg" onclick={scanQR}>
				<i class="fa-solid fa-camera" aria-hidden="true"></i>
				Scan QR Code
			</button>

			<p class="text-sm text-muted" style="margin-top: 1rem;">
				Simulates scanning your phone's VCP QR code at a shop kiosk
			</p>
		</div>
	</div>
{/if}

<!-- Consent Dialog -->
{#if showConsent}
	<div class="consent-overlay">
		<div class="consent-dialog card">
			<div class="shop-logo">
				<i class="fa-solid fa-store" aria-hidden="true"></i>
			</div>
			<h2>Barcelona Guitar Shop</h2>
			<p class="text-muted">Would like to personalize your experience using VCP</p>

			<div class="consent-sections">
				<div class="consent-section">
					<h4>Required for recommendations:</h4>
					<ul class="consent-list">
						<li class="consent-item consent-required">
							<span>skill_level</span>
							<span class="consent-note">To suggest appropriate gear</span>
						</li>
						<li class="consent-item consent-required">
							<span>budget_range</span>
							<span class="consent-note">To filter by price tier</span>
						</li>
					</ul>
				</div>

				<div class="consent-section">
					<h4>Optional (improves recommendations):</h4>
					<ul class="consent-list">
						<li class="consent-item consent-optional">
							<span>noise_concern</span>
							<span class="consent-note">For quiet practice gear</span>
						</li>
						<li class="consent-item consent-optional">
							<span>availability</span>
							<span class="consent-note">For workshop timing</span>
						</li>
					</ul>
				</div>
			</div>

			<div class="privacy-note">
				<span class="privacy-note-icon">🔒</span>
				<span>
					Your private details (work schedule, housing, finances) are NEVER shared.
					Shop sees: "budget: low" not "tight budget on factory wages".
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
		<div class="platform-frame platform-frame-shop">
			<div class="platform-header platform-header-shop">
				<div class="platform-brand">
					<span class="platform-logo"><i class="fa-solid fa-store" aria-hidden="true"></i></span>
					<span class="platform-name">Barcelona Guitar Shop</span>
				</div>
				<div class="header-actions">
					{#if consentGranted}
						<div class="vcp-badge">VCP Connected</div>
					{/if}
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
				{#if consentGranted && ctx}
					<div class="kiosk-welcome">
						<h1>Welcome, {ctx.public_profile.display_name}!</h1>
						<p class="text-muted">VCP Profile Detected - Personalized Recommendations Ready</p>
					</div>

					<!-- Profile Summary -->
					<section class="profile-summary card">
						<h3><i class="fa-solid fa-user-circle" aria-hidden="true"></i> Your Profile</h3>
						<div class="profile-grid">
							<div class="profile-item">
								<span class="item-label">Experience</span>
								<span class="item-value">{ctx.public_profile.experience}</span>
							</div>
							<div class="profile-item">
								<span class="item-label">Budget Tier</span>
								<span class="item-value">{ctx.portable_preferences?.budget_range}</span>
							</div>
							<div class="profile-item">
								<span class="item-label">Goal</span>
								<span class="item-value">{ctx.public_profile.motivation?.replace(/_/g, ' ')}</span>
							</div>
							{#if ctx.constraints?.noise_restricted}
								<div class="profile-item profile-item-highlight">
									<span class="item-label">Noise Mode</span>
									<span class="item-value">Quiet Practice</span>
								</div>
							{/if}
						</div>
					</section>

					<!-- Recommendations -->
					<section class="recommendations-section">
						<h2><i class="fa-solid fa-magic-wand-sparkles" aria-hidden="true"></i> Personalized
							For You</h2>

						{#each recommendations() as rec}
							<div class="recommendation-card card" class:essential={rec.category === 'essential'}>
								<div class="rec-header">
									<div>
										<h3>{rec.name}</h3>
										{#if rec.category === 'essential'}
											<span class="badge badge-success">Essential</span>
										{:else if rec.category === 'upgrade'}
											<span class="badge badge-primary">Upgrade Option</span>
										{:else}
											<span class="badge badge-ghost">Accessory</span>
										{/if}
									</div>
									<span class="rec-price">€{rec.price}</span>
								</div>

								<p class="rec-reason">{rec.reason}</p>

								{#if rec.financing}
									<p class="rec-financing">
										<i class="fa-solid fa-calendar-check" aria-hidden="true"></i>
										{rec.financing}
									</p>
								{/if}

								<div class="rec-match">
									<span class="match-label">VCP Match:</span>
									<code>{rec.vcp_match}</code>
								</div>
							</div>
						{/each}
					</section>

					<!-- Workshop Invitation -->
					{#if workshop()}
						<section class="workshop-card card">
							<div class="workshop-header">
								<span class="workshop-icon">
									<i class="fa-solid fa-chalkboard-user" aria-hidden="true"></i>
								</span>
								<div>
									<h3>{workshop()?.title}</h3>
									<span class="badge badge-warning">Free Workshop</span>
								</div>
							</div>

							<div class="workshop-details">
								<div class="workshop-detail">
									<i class="fa-solid fa-clock" aria-hidden="true"></i>
									<span>{workshop()?.time}</span>
								</div>
								<div class="workshop-detail">
									<i class="fa-solid fa-location-dot" aria-hidden="true"></i>
									<span>{workshop()?.location}</span>
								</div>
							</div>

							<p class="workshop-reason">
								<i class="fa-solid fa-lightbulb" aria-hidden="true"></i>
								{workshop()?.reason}
							</p>

							<button class="btn btn-primary">
								<i class="fa-solid fa-calendar-plus" aria-hidden="true"></i>
								Reserve Spot
							</button>
						</section>
					{/if}

					<!-- What was shared -->
					<section class="shared-info card">
						<h3>What the Shop Received</h3>
						<div class="field-list" style="margin-top: 0.5rem;">
							<span class="field-tag field-tag-shared">skill_level: beginner</span>
							<span class="field-tag field-tag-shared">budget_tier: low</span>
							<span class="field-tag field-tag-shared">noise_concern: true</span>
							<span class="field-tag field-tag-shared">availability: sat_afternoon</span>
						</div>
						<div class="privacy-note" style="margin-top: 1rem;">
							<span class="privacy-note-icon">🔒</span>
							<span>
								<strong>Not shared:</strong> exact_budget (€20/month), work_schedule (factory shifts),
								housing_details (apartment), neighbor_situation (complaints)
							</span>
						</div>
					</section>
				{:else if !showConsent && !showQRScan}
					<div class="no-vcp">
						<h2>VCP Not Connected</h2>
						<p class="text-muted">Scan your VCP QR code for personalized recommendations.</p>
						<button class="btn btn-primary" onclick={() => (showQRScan = true)}>
							<i class="fa-solid fa-qrcode" aria-hidden="true"></i>
							Scan QR Code
						</button>
					</div>
				{/if}
			</div>
		</div>

		<div class="container-narrow" style="margin-top: 2rem;">
			<div class="nav-links">
				<a href="/personal/platforms/yousician" class="btn btn-ghost">← Yousician</a>
				<a href="/personal/community" class="btn btn-primary">Community Challenge →</a>
			</div>
		</div>
	</div>

	<!-- Audit Sidebar -->
	{#if showAuditPanel && consentGranted}
		<aside class="audit-sidebar">
			<AuditPanel
				entries={auditEntries()}
				title="Kiosk Audit"
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

	/* QR Scan Screen */
	.qr-scan-overlay,
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

	.qr-scan-dialog,
	.consent-dialog {
		max-width: 400px;
		width: 100%;
		text-align: center;
	}

	.qr-icon {
		font-size: 4rem;
		color: var(--color-primary);
		margin-bottom: var(--space-md);
	}

	.qr-preview {
		margin: var(--space-lg) 0;
	}

	.qr-placeholder {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-xl);
		background: var(--color-bg-elevated);
		border: 2px dashed rgba(255, 255, 255, 0.2);
		border-radius: var(--radius-lg);
	}

	.qr-placeholder i {
		font-size: 3rem;
		color: var(--color-text-muted);
	}

	.shop-logo {
		font-size: 3rem;
		color: var(--color-shop);
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

	/* Platform Frame */
	.platform-frame-shop {
		--platform-color: var(--color-shop, #8b5cf6);
	}

	.platform-header-shop {
		border-bottom-color: var(--color-shop, #8b5cf6);
	}

	.platform-brand {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
	}

	.platform-logo {
		font-size: 1.5rem;
		color: var(--color-shop, #8b5cf6);
	}

	.platform-name {
		font-weight: 600;
		color: var(--color-shop, #8b5cf6);
	}

	/* Kiosk Content */
	.kiosk-welcome {
		text-align: center;
		margin-bottom: var(--space-xl);
	}

	.kiosk-welcome h1 {
		color: var(--color-shop, #8b5cf6);
	}

	.profile-summary {
		margin-bottom: var(--space-lg);
	}

	.profile-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
		gap: var(--space-md);
		margin-top: var(--space-md);
	}

	.profile-item {
		padding: var(--space-sm);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		text-align: center;
	}

	.profile-item-highlight {
		border: 1px solid var(--color-success);
		background: var(--color-success-muted);
	}

	.item-label {
		display: block;
		font-size: 0.6875rem;
		text-transform: uppercase;
		color: var(--color-text-subtle);
		margin-bottom: var(--space-xs);
	}

	.item-value {
		font-weight: 500;
		text-transform: capitalize;
	}

	/* Recommendations */
	.recommendations-section {
		margin-bottom: var(--space-xl);
	}

	.recommendations-section h2 {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-lg);
	}

	.recommendation-card {
		margin-bottom: var(--space-md);
	}

	.recommendation-card.essential {
		border: 2px solid var(--color-success);
	}

	.rec-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: var(--space-sm);
	}

	.rec-header h3 {
		margin-bottom: var(--space-xs);
	}

	.rec-price {
		font-size: 1.25rem;
		font-weight: 600;
		color: var(--color-success);
	}

	.rec-reason {
		color: var(--color-text-muted);
		font-size: 0.875rem;
		margin-bottom: var(--space-sm);
	}

	.rec-financing {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-sm);
		background: var(--color-primary-muted);
		border-radius: var(--radius-sm);
		font-size: 0.875rem;
		color: var(--color-primary);
		margin-bottom: var(--space-sm);
	}

	.rec-match {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-size: 0.75rem;
	}

	.match-label {
		color: var(--color-text-subtle);
	}

	.rec-match code {
		font-family: var(--font-mono);
		color: var(--color-text-muted);
	}

	/* Workshop */
	.workshop-card {
		margin-bottom: var(--space-xl);
		border: 2px solid var(--color-warning);
		background: var(--color-warning-muted);
	}

	.workshop-header {
		display: flex;
		align-items: center;
		gap: var(--space-md);
		margin-bottom: var(--space-md);
	}

	.workshop-icon {
		font-size: 2rem;
		color: var(--color-warning);
	}

	.workshop-details {
		display: flex;
		gap: var(--space-lg);
		margin-bottom: var(--space-md);
	}

	.workshop-detail {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-size: 0.875rem;
	}

	.workshop-reason {
		display: flex;
		align-items: flex-start;
		gap: var(--space-sm);
		padding: var(--space-sm);
		background: rgba(0, 0, 0, 0.2);
		border-radius: var(--radius-sm);
		font-size: 0.875rem;
		margin-bottom: var(--space-md);
	}

	/* Shared info */
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
</style>
