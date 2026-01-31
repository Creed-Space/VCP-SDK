<script lang="ts">
	/**
	 * SensitiveContextEditor - Mental health context configuration
	 */
	import type { MentalHealthContext, SharingLevel, AdaptationType } from '$lib/vcp/safety';

	interface Props {
		context: MentalHealthContext;
		onchange?: (context: MentalHealthContext) => void;
		readonly?: boolean;
	}

	let { context, onchange, readonly = false }: Props = $props();

	const sharingLevels: { value: SharingLevel; label: string; desc: string }[] = [
		{ value: 'none', label: 'None', desc: 'No information shared' },
		{ value: 'minimal', label: 'Minimal', desc: 'Boolean flags only' },
		{ value: 'moderate', label: 'Moderate', desc: 'Category-level info' },
		{ value: 'full', label: 'Full', desc: 'All allowed details' }
	];

	const adaptationTypes: { type: AdaptationType; label: string; desc: string }[] = [
		{ type: 'gentle_language', label: 'Gentle Language', desc: 'Softer, more supportive tone' },
		{ type: 'avoid_pressure', label: 'Avoid Pressure', desc: 'No deadlines or urgency' },
		{ type: 'frequent_check_ins', label: 'Check-ins', desc: 'Regular wellness checks' },
		{ type: 'shorter_sessions', label: 'Shorter Sessions', desc: 'Breaks more often' },
		{ type: 'explicit_support_offers', label: 'Support Offers', desc: 'Proactive help' },
		{ type: 'no_criticism', label: 'No Criticism', desc: 'Only positive feedback' },
		{ type: 'celebration_of_small_wins', label: 'Celebrate Wins', desc: 'Acknowledge progress' }
	];

	function toggleAdaptation(type: AdaptationType) {
		if (readonly) return;
		const existing = context.requested_adaptations.find(a => a.type === type);
		if (existing) {
			context.requested_adaptations = context.requested_adaptations.filter(a => a.type !== type);
		} else {
			context.requested_adaptations = [
				...context.requested_adaptations,
				{ type, active: true, user_requested: true }
			];
		}
		onchange?.(context);
	}

	function isAdaptationActive(type: AdaptationType): boolean {
		return context.requested_adaptations.some(a => a.type === type && a.active);
	}

	function updateSharingLevel(target: 'ai' | 'humans', level: SharingLevel) {
		if (readonly) return;
		if (target === 'ai') {
			context.share_with_ai = level;
		} else {
			context.share_with_humans = level;
		}
		onchange?.(context);
	}
</script>

<div class="sensitive-context-editor">
	<div class="editor-header">
		<h3><i class="fa-solid fa-lock" aria-hidden="true"></i> Sensitive Context Settings</h3>
		<p class="header-desc">Configure how your mental health context is shared and used</p>
	</div>

	<!-- Sharing Controls -->
	<div class="sharing-section">
		<h4>Sharing Preferences</h4>

		<div class="sharing-group">
			<span class="sharing-label">Share with AI:</span>
			<div class="sharing-buttons" role="radiogroup" aria-label="Share with AI level">
				{#each sharingLevels as level}
					<button
						class="sharing-btn"
						class:active={context.share_with_ai === level.value}
						disabled={readonly}
						onclick={() => updateSharingLevel('ai', level.value)}
						aria-label="{level.label}: {level.desc}"
						aria-pressed={context.share_with_ai === level.value}
					>
						{level.label}
					</button>
				{/each}
			</div>
		</div>

		<div class="sharing-group">
			<span class="sharing-label" id="share-humans-label">Share with Humans:</span>
			<div class="sharing-buttons" role="radiogroup" aria-labelledby="share-humans-label">
				{#each sharingLevels as level}
					<button
						class="sharing-btn"
						class:active={context.share_with_humans === level.value}
						disabled={readonly}
						onclick={() => updateSharingLevel('humans', level.value)}
						aria-label="{level.label}: {level.desc}"
						aria-pressed={context.share_with_humans === level.value}
					>
						{level.label}
					</button>
				{/each}
			</div>
		</div>
	</div>

	<!-- Flags -->
	<div class="flags-section">
		<h4>Context Flags</h4>
		<p class="section-note">These are shared as boolean values only (true/false)</p>

		<div class="flags-grid">
			<div class="flag-item" class:active={context.seeking_support}>
				<span class="flag-icon"><i class="fa-solid {context.seeking_support ? 'fa-check' : 'fa-circle'}" aria-hidden="true"></i></span>
				<span class="flag-label">Seeking Support</span>
			</div>
			<div class="flag-item" class:active={context.professional_involved}>
				<span class="flag-icon"><i class="fa-solid {context.professional_involved ? 'fa-check' : 'fa-circle'}" aria-hidden="true"></i></span>
				<span class="flag-label">Professional Involved</span>
			</div>
			<div class="flag-item caution" class:active={context.crisis_indicators}>
				<span class="flag-icon"><i class="fa-solid {context.crisis_indicators ? 'fa-triangle-exclamation' : 'fa-circle'}" aria-hidden="true"></i></span>
				<span class="flag-label">Crisis Indicators</span>
			</div>
			<div class="flag-item" class:active={context.escalation_consent}>
				<span class="flag-icon"><i class="fa-solid {context.escalation_consent ? 'fa-check' : 'fa-circle'}" aria-hidden="true"></i></span>
				<span class="flag-label">Escalation Consent</span>
			</div>
		</div>
	</div>

	<!-- Adaptations -->
	<div class="adaptations-section">
		<h4>Requested Adaptations</h4>
		<p class="section-note">How AI should adjust its behavior</p>

		<div class="adaptations-grid">
			{#each adaptationTypes as adaptation}
				<button
					class="adaptation-btn"
					class:active={isAdaptationActive(adaptation.type)}
					disabled={readonly}
					onclick={() => toggleAdaptation(adaptation.type)}
				>
					<span class="adaptation-check">{#if isAdaptationActive(adaptation.type)}<i class="fa-solid fa-check" aria-hidden="true"></i>{/if}</span>
					<div class="adaptation-text">
						<span class="adaptation-label">{adaptation.label}</span>
						<span class="adaptation-desc">{adaptation.desc}</span>
					</div>
				</button>
			{/each}
		</div>
	</div>

	<!-- Private Context Warning -->
	{#if context.private_context}
		<div class="private-warning">
			<div class="warning-header">
				<span class="warning-icon"><i class="fa-solid fa-key" aria-hidden="true"></i></span>
				<strong>Private Context (Never Transmitted)</strong>
			</div>
			<p>
				You have private context configured. This information shapes AI behavior but is
				<strong>never shared</strong> with any stakeholder, even with "full" sharing enabled.
			</p>
			<div class="private-categories">
				{#if context.private_context.conditions?.length}
					<span class="category-chip">Conditions: {context.private_context.conditions.length}</span>
				{/if}
				{#if context.private_context.triggers?.length}
					<span class="category-chip">Triggers: {context.private_context.triggers.length}</span>
				{/if}
				{#if context.private_context.coping_strategies?.length}
					<span class="category-chip">Coping: {context.private_context.coping_strategies.length}</span>
				{/if}
			</div>
		</div>
	{/if}

	<!-- Preview -->
	<div class="preview-section">
		<h4>What Stakeholders See</h4>
		<div class="preview-grid">
			<div class="preview-card">
				<span class="preview-label">AI Assistant</span>
				<div class="preview-content">
					{#if context.share_with_ai === 'none'}
						<span class="preview-empty">No mental health context shared</span>
					{:else if context.share_with_ai === 'minimal'}
						<span>seeking_support: {context.seeking_support}</span>
						<span>crisis_indicators: {context.crisis_indicators}</span>
					{:else if context.share_with_ai === 'moderate'}
						<span>Flags + adaptation preferences</span>
						<span>({context.requested_adaptations.length} adaptations active)</span>
					{:else}
						<span>Full context (except private)</span>
					{/if}
				</div>
			</div>
			<div class="preview-card">
				<span class="preview-label">Human Stakeholders</span>
				<div class="preview-content">
					{#if context.share_with_humans === 'none'}
						<span class="preview-empty">No mental health context shared</span>
					{:else}
						<span>Level: {context.share_with_humans}</span>
						<span>Escalation consent: {context.escalation_consent ? 'Yes' : 'No'}</span>
					{/if}
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	.sensitive-context-editor {
		display: flex;
		flex-direction: column;
		gap: var(--space-lg);
	}

	.editor-header h3 {
		margin-bottom: var(--space-xs);
	}

	.header-desc {
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	h4 {
		font-size: 0.9375rem;
		margin-bottom: var(--space-sm);
	}

	.section-note {
		font-size: 0.75rem;
		color: var(--color-text-subtle);
		margin-bottom: var(--space-md);
	}

	.sharing-section {
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
	}

	.sharing-group {
		display: flex;
		align-items: center;
		gap: var(--space-md);
		margin-bottom: var(--space-md);
	}

	.sharing-group:last-child {
		margin-bottom: 0;
	}

	.sharing-label {
		font-size: 0.875rem;
		min-width: 140px;
	}

	.sharing-buttons {
		display: flex;
		gap: var(--space-xs);
	}

	.sharing-btn {
		padding: var(--space-sm) var(--space-md);
		background: var(--color-bg-elevated);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-sm);
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		cursor: pointer;
		transition: all var(--transition-fast);
	}

	.sharing-btn:hover:not(:disabled) {
		border-color: var(--color-primary);
	}

	.sharing-btn:focus-visible {
		outline: 2px solid var(--color-primary);
		outline-offset: 2px;
	}

	.sharing-btn.active {
		background: var(--color-primary-muted);
		border-color: var(--color-primary);
		color: var(--color-primary);
	}

	.sharing-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.flags-section {
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
	}

	.flags-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
		gap: var(--space-sm);
	}

	.flag-item {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-sm) var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		font-size: 0.8125rem;
	}

	.flag-item.active {
		background: var(--color-success-muted);
	}

	.flag-item.caution.active {
		background: var(--color-warning-muted);
	}

	.flag-icon {
		font-size: 1rem;
	}

	.adaptations-section {
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
	}

	.adaptations-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
		gap: var(--space-sm);
	}

	.adaptation-btn {
		display: flex;
		align-items: flex-start;
		gap: var(--space-sm);
		padding: var(--space-md);
		background: var(--color-bg-card);
		border: 2px solid rgba(255, 255, 255, 0.25);
		border-radius: var(--radius-md);
		text-align: left;
		cursor: pointer;
		transition: all var(--transition-fast);
		color: var(--color-text);
	}

	.adaptation-btn:hover:not(:disabled) {
		border-color: var(--color-primary);
		background: rgba(99, 102, 241, 0.15);
	}

	.adaptation-btn:focus-visible {
		outline: 2px solid var(--color-primary);
		outline-offset: 2px;
	}

	.adaptation-btn.active {
		background: var(--color-primary-muted);
		border-color: var(--color-primary);
	}

	.adaptation-btn:disabled {
		opacity: 0.7;
		cursor: not-allowed;
	}

	.adaptation-check {
		width: 24px;
		height: 24px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-bg);
		border: 2px solid rgba(255, 255, 255, 0.3);
		border-radius: var(--radius-sm);
		font-size: 1rem;
		color: var(--color-success);
		flex-shrink: 0;
	}

	.adaptation-btn.active .adaptation-check {
		background: var(--color-success);
		border-color: var(--color-success);
		color: white;
	}

	.adaptation-text {
		display: flex;
		flex-direction: column;
	}

	.adaptation-label {
		font-size: 1rem;
		font-weight: 600;
		color: #ffffff;
	}

	.adaptation-desc {
		font-size: 0.8125rem;
		color: #c0c0c0;
		margin-top: 4px;
	}

	.private-warning {
		padding: var(--space-lg);
		background: var(--color-warning-muted);
		border-radius: var(--radius-lg);
		border-left: 4px solid var(--color-warning);
	}

	.warning-header {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-sm);
	}

	.private-warning p {
		font-size: 0.875rem;
		margin-bottom: var(--space-md);
	}

	.private-categories {
		display: flex;
		gap: var(--space-xs);
		flex-wrap: wrap;
	}

	.category-chip {
		font-size: 0.6875rem;
		padding: 2px 8px;
		background: rgba(0, 0, 0, 0.2);
		border-radius: var(--radius-sm);
	}

	.preview-section {
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
	}

	.preview-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: var(--space-md);
	}

	.preview-card {
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
	}

	.preview-label {
		display: block;
		font-size: 0.75rem;
		color: var(--color-text-subtle);
		text-transform: uppercase;
		margin-bottom: var(--space-sm);
	}

	.preview-content {
		display: flex;
		flex-direction: column;
		gap: 4px;
		font-size: 0.8125rem;
	}

	.preview-empty {
		color: var(--color-text-muted);
		font-style: italic;
	}
</style>
