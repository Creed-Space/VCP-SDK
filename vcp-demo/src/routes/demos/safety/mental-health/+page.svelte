<script lang="ts">
	import DemoContainer from '$lib/components/demo/DemoContainer.svelte';
	import SensitiveContextEditor from '$lib/components/safety/SensitiveContextEditor.svelte';
	import PresetLoader from '$lib/components/shared/PresetLoader.svelte';
	import AuditPanel from '$lib/components/shared/AuditPanel.svelte';
	import type { MentalHealthContext } from '$lib/vcp/safety';

	// Demo mental health context
	let context = $state<MentalHealthContext>({
		seeking_support: true,
		professional_involved: true,
		crisis_indicators: false,
		medication_relevant: false,
		escalation_consent: true,
		share_with_ai: 'moderate',
		share_with_humans: 'minimal',
		requested_adaptations: [
			{ type: 'gentle_language', active: true, user_requested: true },
			{ type: 'avoid_pressure', active: true, user_requested: true },
			{ type: 'celebration_of_small_wins', active: true, user_requested: false }
		],
		sensitive_topics: [
			{ topic: 'work deadlines', approach: 'careful', reason_category: 'anxiety' }
		],
		private_context: {
			conditions: ['anxiety', 'adhd'],
			triggers: ['time pressure', 'criticism'],
			coping_strategies: ['breathing exercises', 'breaks']
		}
	});

	let selectedPreset = $state<string | undefined>(undefined);

	// Mental health context presets in PresetLoader format
	const mentalHealthPresets = [
		{
			id: 'default-safe',
			name: 'Default Safe',
			description: 'Minimal sharing, no context exposed',
			icon: 'fa-shield',
			data: {
				seeking_support: false,
				professional_involved: false,
				crisis_indicators: false,
				medication_relevant: false,
				escalation_consent: false,
				share_with_ai: 'none' as const,
				share_with_humans: 'none' as const,
				requested_adaptations: [],
				sensitive_topics: [],
				private_context: undefined
			},
			tags: ['privacy', 'minimal']
		},
		{
			id: 'support-seeker',
			name: 'Support Seeker',
			description: 'Actively getting help, shares with AI',
			icon: 'fa-hand-holding-heart',
			data: {
				seeking_support: true,
				professional_involved: true,
				crisis_indicators: false,
				medication_relevant: false,
				escalation_consent: true,
				share_with_ai: 'moderate' as const,
				share_with_humans: 'minimal' as const,
				requested_adaptations: [
					{ type: 'gentle_language' as const, active: true, user_requested: true },
					{ type: 'avoid_pressure' as const, active: true, user_requested: true }
				],
				sensitive_topics: [{ topic: 'deadlines', approach: 'careful' as const }],
				private_context: {
					conditions: ['anxiety'],
					triggers: ['deadlines'],
					coping_strategies: ['breaks']
				}
			},
			tags: ['therapeutic', 'moderate']
		},
		{
			id: 'crisis-protocol',
			name: 'Crisis Protocol',
			description: 'Crisis indicators active, full sharing enabled',
			icon: 'fa-bell',
			data: {
				seeking_support: true,
				professional_involved: true,
				crisis_indicators: true,
				medication_relevant: true,
				escalation_consent: true,
				share_with_ai: 'full' as const,
				share_with_humans: 'moderate' as const,
				requested_adaptations: [
					{ type: 'gentle_language' as const, active: true, user_requested: false },
					{ type: 'explicit_support_offers' as const, active: true, user_requested: false },
					{ type: 'shorter_sessions' as const, active: true, user_requested: false }
				],
				sensitive_topics: [
					{ topic: 'isolation', approach: 'careful' as const, reason_category: 'depression' }
				],
				private_context: {
					conditions: ['depression', 'anxiety'],
					triggers: ['isolation', 'criticism'],
					coping_strategies: ['crisis hotline', 'therapy']
				}
			},
			tags: ['crisis', 'full-support']
		},
		{
			id: 'work-focused',
			name: 'Work Focused',
			description: 'Productivity adaptations without clinical details',
			icon: 'fa-briefcase',
			data: {
				seeking_support: false,
				professional_involved: false,
				crisis_indicators: false,
				medication_relevant: false,
				escalation_consent: false,
				share_with_ai: 'minimal' as const,
				share_with_humans: 'none' as const,
				requested_adaptations: [
					{ type: 'avoid_pressure' as const, active: true, user_requested: true },
					{ type: 'celebration_of_small_wins' as const, active: true, user_requested: true }
				],
				sensitive_topics: [
					{ topic: 'deadlines', approach: 'careful' as const }
				],
				private_context: undefined
			},
			tags: ['productivity', 'minimal']
		}
	];

	function applyPreset(preset: (typeof mentalHealthPresets)[0]) {
		context = { ...preset.data };
		selectedPreset = preset.id;
	}

	function handleContextChange(newContext: MentalHealthContext) {
		context = newContext;
		selectedPreset = undefined; // Clear preset when manually edited
	}

	// Audit entries derived from context (using AuditPanel's interface)
	const auditEntries = $derived([
		// Shared fields
		{
			field: 'AI Sharing Level',
			category: 'shared' as const,
			value: context.share_with_ai,
			reason: 'User-controlled disclosure level for AI systems'
		},
		{
			field: 'Human Sharing Level',
			category: 'shared' as const,
			value: context.share_with_humans,
			reason: 'User-controlled disclosure level for human stakeholders'
		},
		{
			field: 'Seeking Support',
			category: context.seeking_support ? 'shared' as const : 'withheld' as const,
			value: context.seeking_support
		},
		{
			field: 'Professional Involved',
			category: context.professional_involved ? 'shared' as const : 'withheld' as const,
			value: context.professional_involved
		},
		// Influenced fields
		{
			field: 'Active Adaptations',
			category: 'influenced' as const,
			value: `${context.requested_adaptations.filter((a) => a.active).length} adaptations`,
			reason: 'Influences AI communication style without exposing why'
		},
		{
			field: 'Sensitive Topics',
			category: 'influenced' as const,
			value: `${context.sensitive_topics.length} topics marked`,
			reason: 'AI avoids or approaches carefully without knowing specifics'
		},
		// Withheld fields
		{
			field: 'Private Context',
			category: 'withheld' as const,
			value: context.private_context ? 'defined' : 'not set',
			reason: 'Conditions, triggers, coping strategies NEVER transmitted'
		},
		{
			field: 'Crisis Indicators',
			category: context.crisis_indicators ? 'shared' as const : 'withheld' as const,
			value: context.crisis_indicators ? 'ACTIVE' : 'inactive',
			reason: context.crisis_indicators ? 'Shared for safety escalation' : 'Protected when inactive'
		},
		{
			field: 'Escalation Consent',
			category: context.escalation_consent ? 'shared' as const : 'withheld' as const,
			value: context.escalation_consent ? 'granted' : 'withheld',
			reason: 'User controls whether crisis escalation can occur'
		}
	]);
</script>

<svelte:head>
	<title>Mental Health Context - VCP Safety</title>
	<meta
		name="description"
		content="See how VCP protects sensitive mental health context with graduated sharing."
	/>
</svelte:head>

<DemoContainer
	title="Mental Health Context Protection"
	description="Graduated disclosure controls for sensitive mental health information."
>
	{#snippet children()}
		<div class="mental-health-layout">
			<!-- Left: Editor -->
			<div class="editor-section">
				<SensitiveContextEditor {context} onchange={handleContextChange} />
			</div>

			<!-- Right: Presets, Audit & Explanation -->
			<div class="info-section">
				<!-- Preset Loader -->
				<PresetLoader
					presets={mentalHealthPresets}
					selected={selectedPreset}
					onselect={(p) => applyPreset(p as (typeof mentalHealthPresets)[0])}
					title="Mental Health Scenarios"
				/>

				<!-- Prosaic Connection -->
				<div class="prosaic-card">
					<h3>💭 💊 Prosaic Dimensions</h3>
					<p>
						This demo shows the <strong>💭 Affect</strong> and <strong>💊 Health</strong> prosaic dimensions.
						Instead of detailed mental health configuration, you can simply declare your state:
					</p>
					<div class="prosaic-examples">
						<code>💭0.8:grieving</code> — Presence over solutions, no silver-lining
						<code>💊0.6:illness</code> — Gentler tone, suggest breaks
					</div>
					<p class="prosaic-note">
						The detailed controls here show what's <em>possible</em> — but prosaic dimensions let you communicate quickly.
					</p>
				</div>

				<!-- Audit Panel -->
				<AuditPanel entries={auditEntries} title="Context Audit" />

				<!-- Privacy Guarantees -->
				<div class="guarantees-card">
					<h3>Privacy Guarantees</h3>
					<div class="guarantee-list">
						<div class="guarantee">
							<span class="guarantee-icon"><i class="fa-solid fa-key" aria-hidden="true"></i></span>
							<div>
								<strong>Private Context Never Transmitted</strong>
								<p>
									Conditions, triggers, and coping strategies in private_context are NEVER
									sent to any stakeholder, regardless of sharing level.
								</p>
							</div>
						</div>
						<div class="guarantee">
							<span class="guarantee-icon"><i class="fa-solid fa-chart-simple" aria-hidden="true"></i></span>
							<div>
								<strong>Minimal = Booleans Only</strong>
								<p>
									At minimal sharing, only yes/no flags are transmitted. No details about
									what kind of support, what conditions, or what adaptations.
								</p>
							</div>
						</div>
						<div class="guarantee">
							<span class="guarantee-icon"><i class="fa-solid fa-robot" aria-hidden="true"></i></span>
							<div>
								<strong>AI vs Human Separation</strong>
								<p>
									You can share more with AI (which has no persistent memory) than with
									human stakeholders who might form lasting judgments.
								</p>
							</div>
						</div>
						<div class="guarantee">
							<span class="guarantee-icon"><i class="fa-solid fa-bell" aria-hidden="true"></i></span>
							<div>
								<strong>Crisis Escalation Consent</strong>
								<p>
									Even if crisis indicators are detected, escalation only happens if
									escalation_consent is true. User maintains control.
								</p>
							</div>
						</div>
					</div>
				</div>

				<!-- How It Works -->
				<div class="explanation-card">
					<h3>How Adaptations Work</h3>
					<p>When you enable adaptations, AI systems adjust their behavior:</p>
					<div class="adaptation-examples">
						<div class="example">
							<span class="example-name">Gentle Language</span>
							<div class="example-comparison">
								<span class="before">"You failed to complete the task"</span>
								<span class="arrow">→</span>
								<span class="after">"This one didn't work out - let's try a different approach"</span>
							</div>
						</div>
						<div class="example">
							<span class="example-name">Avoid Pressure</span>
							<div class="example-comparison">
								<span class="before">"You need to finish this TODAY"</span>
								<span class="arrow">→</span>
								<span class="after">"When you're ready, we can work on this together"</span>
							</div>
						</div>
						<div class="example">
							<span class="example-name">Celebrate Small Wins</span>
							<div class="example-comparison">
								<span class="before">"Task completed."</span>
								<span class="arrow">→</span>
								<span class="after">"Great job getting that done! Every step forward counts."</span>
							</div>
						</div>
					</div>
					<div class="key-insight">
						<strong>Key:</strong> These adaptations happen automatically when your VCP
						context includes mental health preferences. You don't have to disclose WHY you
						need gentle language - the AI just provides it.
					</div>
				</div>
			</div>
		</div>
	{/snippet}
</DemoContainer>

<style>
	.mental-health-layout {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--space-xl);
	}

	.editor-section,
	.info-section {
		display: flex;
		flex-direction: column;
		gap: var(--space-lg);
	}

	.guarantees-card,
	.explanation-card {
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
	}

	h3 {
		font-size: 1rem;
		margin: 0 0 var(--space-md) 0;
	}

	.guarantee-list {
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
	}

	.guarantee {
		display: flex;
		gap: var(--space-md);
	}

	.guarantee-icon {
		font-size: 1.25rem;
		flex-shrink: 0;
	}

	.guarantee strong {
		display: block;
		font-size: 0.875rem;
		margin-bottom: 2px;
	}

	.guarantee p {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		margin: 0;
	}

	.explanation-card p {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		margin-bottom: var(--space-md);
	}

	.adaptation-examples {
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
		margin-bottom: var(--space-lg);
	}

	.example {
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
	}

	.example-name {
		display: block;
		font-size: 0.75rem;
		text-transform: uppercase;
		color: var(--color-primary);
		font-weight: 600;
		margin-bottom: var(--space-sm);
	}

	.example-comparison {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-size: 0.8125rem;
	}

	.before {
		text-decoration: line-through;
		color: var(--color-text-subtle);
	}

	.arrow {
		color: var(--color-text-subtle);
	}

	.after {
		color: var(--color-success);
	}

	.key-insight {
		padding: var(--space-md);
		background: var(--color-success-muted);
		border-radius: var(--radius-md);
		font-size: 0.875rem;
	}

	/* Prosaic card */
	.prosaic-card {
		padding: var(--space-lg);
		background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
		border: 1px solid rgba(16, 185, 129, 0.3);
		border-radius: var(--radius-lg);
	}

	.prosaic-card h3 {
		margin: 0 0 var(--space-md);
		color: var(--color-success);
	}

	.prosaic-card p {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		margin: 0 0 var(--space-sm);
		line-height: 1.5;
	}

	.prosaic-examples {
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
		margin-bottom: var(--space-sm);
	}

	.prosaic-examples code {
		font-family: var(--font-mono);
		font-size: var(--text-sm);
		padding: var(--space-xs) var(--space-sm);
		background: var(--color-bg);
		border-radius: var(--radius-sm);
	}

	.prosaic-note {
		font-style: italic;
		font-size: 0.75rem !important;
	}

	@media (max-width: 1024px) {
		.mental-health-layout {
			grid-template-columns: 1fr;
		}
	}
</style>
