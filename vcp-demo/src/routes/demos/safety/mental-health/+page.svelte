<script lang="ts">
	import DemoContainer from '$lib/components/demo/DemoContainer.svelte';
	import SensitiveContextEditor from '$lib/components/safety/SensitiveContextEditor.svelte';
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

	// Demonstration scenarios
	let scenarios = [
		{
			name: 'Default Safe',
			desc: 'Minimal sharing, gentle adaptations',
			context: {
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
			}
		},
		{
			name: 'Support Seeker',
			desc: 'Actively getting help, shares with AI',
			context: {
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
				sensitive_topics: [
					{ topic: 'deadlines', approach: 'careful' as const }
				],
				private_context: {
					conditions: ['anxiety'],
					triggers: ['deadlines'],
					coping_strategies: ['breaks']
				}
			}
		},
		{
			name: 'Crisis Protocol',
			desc: 'Crisis indicators active, full sharing',
			context: {
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
			}
		}
	];

	function loadScenario(scenario: (typeof scenarios)[0]) {
		context = { ...scenario.context };
	}

	function handleContextChange(newContext: MentalHealthContext) {
		context = newContext;
	}
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

			<!-- Right: Scenarios & Explanation -->
			<div class="info-section">
				<!-- Quick Scenarios -->
				<div class="scenarios-card">
					<h3>Try Different Scenarios</h3>
					<div class="scenario-buttons">
						{#each scenarios as scenario}
							<button class="scenario-btn" onclick={() => loadScenario(scenario)}>
								<span class="scenario-name">{scenario.name}</span>
								<span class="scenario-desc">{scenario.desc}</span>
							</button>
						{/each}
					</div>
				</div>

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

	.scenarios-card,
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

	.scenario-buttons {
		display: flex;
		flex-direction: column;
		gap: var(--space-sm);
	}

	.scenario-btn {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-md);
		cursor: pointer;
		text-align: left;
		transition: all var(--transition-fast);
	}

	.scenario-btn:hover {
		border-color: var(--color-primary);
	}

	.scenario-name {
		font-weight: 600;
		margin-bottom: 2px;
	}

	.scenario-desc {
		font-size: 0.75rem;
		color: var(--color-text-muted);
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

	@media (max-width: 1024px) {
		.mental-health-layout {
			grid-template-columns: 1fr;
		}
	}
</style>
