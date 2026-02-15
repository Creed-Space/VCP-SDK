<script lang="ts">
	/**
	 * VCP Playground - Interactive token builder and inspector
	 */
	import { encodeContextToCSM1, getEmojiLegend, getTransmissionSummary } from '$lib/vcp/token';
	import type { VCPContext, ConstraintFlags, PortablePreferences, ProsaicDimensions } from '$lib/vcp/types';
	import { Breadcrumb } from '$lib/components/shared';

	const breadcrumbItems = [
		{ label: 'Playground', icon: 'fa-sliders' }
	];

	// Default context for playground
	let context = $state<VCPContext>({
		vcp_version: '1.0.0',
		profile_id: 'playground-user',
		constitution: {
			id: 'personal.growth.creative',
			version: '1.0.0',
			persona: 'muse',
			adherence: 3,
			scopes: ['creativity', 'health', 'privacy']
		},
		public_profile: {
			display_name: 'Playground User',
			goal: 'learn_guitar',
			experience: 'beginner',
			learning_style: 'hands_on',
			pace: 'steady',
			motivation: 'stress_relief'
		},
		portable_preferences: {
			noise_mode: 'quiet_preferred',
			session_length: '30_minutes',
			budget_range: 'low',
			feedback_style: 'encouraging'
		},
		constraints: {
			time_limited: true,
			budget_limited: true,
			noise_restricted: true,
			energy_variable: false,
			schedule_irregular: false
		},
		private_context: {
			_note: 'Private context - never transmitted',
			work_type: 'office_worker',
			housing: 'apartment'
		},
		prosaic: {
			urgency: 0.3,
			health: 0.1,
			cognitive: 0.2,
			affect: 0.2
		}
	});

	const token = $derived(encodeContextToCSM1(context));
	const summary = $derived(getTransmissionSummary(context));
	const legend = getEmojiLegend();

	// Personas for quick selection
	const personas = [
		{ id: 'muse', name: 'Muse', iconClass: 'fa-palette' },
		{ id: 'ambassador', name: 'Ambassador', iconClass: 'fa-handshake' },
		{ id: 'godparent', name: 'Godparent', iconClass: 'fa-shield' },
		{ id: 'sentinel', name: 'Sentinel', iconClass: 'fa-eye' },
		{ id: 'anchor', name: 'Anchor', iconClass: 'fa-anchor' },
		{ id: 'nanny', name: 'Nanny', iconClass: 'fa-child' }
	];

	function updateConstraint(key: keyof ConstraintFlags, value: boolean) {
		context.constraints = { ...context.constraints, [key]: value };
	}

	function updatePreference(key: keyof PortablePreferences, value: string) {
		context.portable_preferences = { ...context.portable_preferences, [key]: value };
	}

	function updateProsaic(key: keyof ProsaicDimensions, value: number) {
		context.prosaic = { ...context.prosaic, [key]: value };
	}

	// Copy feedback state
	let copyFeedback = $state('');
	let copyTimeout: ReturnType<typeof setTimeout>;

	function copyToken() {
		navigator.clipboard.writeText(token);
		copyFeedback = 'Copied!';
		clearTimeout(copyTimeout);
		copyTimeout = setTimeout(() => {
			copyFeedback = '';
		}, 2000);
	}

	function sharePlayground() {
		// Encode current context as URL parameter
		const encoded = btoa(JSON.stringify({
			p: context.public_profile,
			c: context.constraints,
			pp: context.portable_preferences,
			const: context.constitution
		}));
		const url = `${window.location.origin}/playground?ctx=${encoded}`;
		navigator.clipboard.writeText(url);
		copyFeedback = 'Link copied!';
		clearTimeout(copyTimeout);
		copyTimeout = setTimeout(() => {
			copyFeedback = '';
		}, 2000);
	}

	function resetContext() {
		context = {
			...context,
			public_profile: {
				display_name: '',
				goal: '',
				experience: 'beginner',
				learning_style: 'hands_on',
				pace: 'steady',
				motivation: undefined
			},
			constraints: {
				time_limited: false,
				budget_limited: false,
				noise_restricted: false,
				energy_variable: false,
				schedule_irregular: false
			},
			portable_preferences: {
				noise_mode: 'normal',
				session_length: '30_minutes',
				budget_range: 'medium',
				feedback_style: 'encouraging'
			},
			prosaic: {
				urgency: 0.0,
				health: 0.0,
				cognitive: 0.0,
				affect: 0.0
			}
		};
	}

	function loadExample(type: 'campion' | 'gentian') {
		if (type === 'campion') {
			context = {
				...context,
				public_profile: {
					display_name: 'Campion',
					goal: 'tech_lead_promotion',
					experience: 'advanced',
					learning_style: 'reading',
					pace: 'intensive',
					motivation: 'career'
				},
				constraints: {
					time_limited: true,
					budget_limited: false,
					noise_restricted: false,
					energy_variable: true,
					schedule_irregular: true
				},
				constitution: {
					id: 'work.professional.leader',
					version: '1.0.0',
					persona: 'ambassador',
					adherence: 4,
					scopes: ['work', 'education']
				},
				prosaic: {
					urgency: 0.7,
					health: 0.2,
					cognitive: 0.5,
					affect: 0.4
				}
			};
		} else {
			context = {
				...context,
				public_profile: {
					display_name: 'Gentian',
					goal: 'learn_guitar',
					experience: 'beginner',
					learning_style: 'hands_on',
					pace: 'steady',
					motivation: 'stress_relief'
				},
				constraints: {
					time_limited: true,
					budget_limited: true,
					noise_restricted: true,
					energy_variable: true,
					schedule_irregular: true
				},
				portable_preferences: {
					noise_mode: 'quiet_preferred',
					session_length: '30_minutes',
					budget_range: 'low',
					feedback_style: 'encouraging'
				},
				constitution: {
					id: 'personal.growth.creative',
					version: '1.0.0',
					persona: 'muse',
					adherence: 3,
					scopes: ['creativity', 'health', 'privacy']
				},
				prosaic: {
					urgency: 0.2,
					health: 0.3,
					cognitive: 0.3,
					affect: 0.2
				}
			};
		}
	}
</script>

<svelte:head>
	<title>Playground - VCP</title>
	<meta name="description" content="Interactive VCP token builder and inspector." />
</svelte:head>

<div class="container">
	<Breadcrumb items={breadcrumbItems} />

	<section class="page-hero">
		<h1>VCP Playground</h1>
		<p class="page-hero-subtitle">
			Build context tokens interactively. Toggle constraints, change preferences, and watch the token update in real-time.
		</p>
		<p class="page-hero-explainer">
			See exactly what gets transmitted to platforms — and what stays private.
			<a href="/docs/csm1-specification">Learn about the token format</a>
		</p>
	</section>

	<!-- Quick Load Examples -->
	<section class="example-loaders">
		<span class="example-label">Quick load:</span>
		<button class="btn btn-ghost btn-sm" onclick={() => loadExample('campion')}>
			<i class="fa-solid fa-briefcase" aria-hidden="true"></i> Campion (Professional)
		</button>
		<button class="btn btn-ghost btn-sm" onclick={() => loadExample('gentian')}>
			<i class="fa-solid fa-guitar" aria-hidden="true"></i> Gentian (Personal)
		</button>
	</section>

	<div class="playground-grid">
		<!-- Controls Panel -->
		<div class="panel controls-panel">
			<div class="panel-header">
				<h2>Context Builder</h2>
				<button class="btn btn-ghost btn-sm" onclick={resetContext}>Reset</button>
			</div>

			<!-- Profile Section -->
			<section class="control-section">
				<h3>Profile</h3>
				<div class="control-group">
					<label class="label" for="display-name">Display Name</label>
					<input
						id="display-name"
						type="text"
						class="input"
						bind:value={context.public_profile.display_name}
					/>
				</div>
				<div class="control-group">
					<label class="label" for="goal">Goal</label>
					<input
						id="goal"
						type="text"
						class="input"
						bind:value={context.public_profile.goal}
					/>
				</div>
				<div class="control-row">
					<div class="control-group">
						<label class="label" for="experience">Experience</label>
						<select id="experience" class="input select" bind:value={context.public_profile.experience}>
							<option value="beginner">Beginner</option>
							<option value="intermediate">Intermediate</option>
							<option value="advanced">Advanced</option>
							<option value="expert">Expert</option>
						</select>
					</div>
					<div class="control-group">
						<label class="label" for="style">Learning Style</label>
						<select id="style" class="input select" bind:value={context.public_profile.learning_style}>
							<option value="visual">Visual</option>
							<option value="auditory">Auditory</option>
							<option value="hands_on">Hands-on</option>
							<option value="reading">Reading</option>
							<option value="mixed">Mixed</option>
						</select>
					</div>
				</div>
			</section>

			<!-- Constitution Section -->
			<section class="control-section">
				<h3>Constitution</h3>
				<fieldset class="control-group">
					<legend class="label">Persona</legend>
					<div class="persona-grid">
						{#each personas as persona}
							<button
								class="persona-btn"
								class:active={context.constitution.persona === persona.id}
								onclick={() => (context.constitution.persona = persona.id as any)}
							>
								<span class="persona-icon"><i class="fa-solid {persona.iconClass}" aria-hidden="true"></i></span>
								<span class="persona-name">{persona.name}</span>
							</button>
						{/each}
					</div>
				</fieldset>
				<div class="control-group">
					<label class="label" for="adherence">Adherence Level: {context.constitution.adherence}</label>
					<input
						id="adherence"
						type="range"
						min="1"
						max="5"
						bind:value={context.constitution.adherence}
						class="slider"
					/>
				</div>
			</section>

			<!-- Constraints Section -->
			<section class="control-section">
				<h3>Constraint Flags</h3>
				<div class="checkbox-grid">
					<label class="checkbox-label">
						<input
							type="checkbox"
							checked={context.constraints?.time_limited}
							onchange={(e) => updateConstraint('time_limited', e.currentTarget.checked)}
						/>
						<span><i class="fa-solid fa-clock" aria-hidden="true"></i> Time Limited</span>
					</label>
					<label class="checkbox-label">
						<input
							type="checkbox"
							checked={context.constraints?.budget_limited}
							onchange={(e) => updateConstraint('budget_limited', e.currentTarget.checked)}
						/>
						<span><i class="fa-solid fa-wallet" aria-hidden="true"></i> Budget Limited</span>
					</label>
					<label class="checkbox-label">
						<input
							type="checkbox"
							checked={context.constraints?.noise_restricted}
							onchange={(e) => updateConstraint('noise_restricted', e.currentTarget.checked)}
						/>
						<span><i class="fa-solid fa-volume-xmark" aria-hidden="true"></i> Noise Restricted</span>
					</label>
					<label class="checkbox-label">
						<input
							type="checkbox"
							checked={context.constraints?.energy_variable}
							onchange={(e) => updateConstraint('energy_variable', e.currentTarget.checked)}
						/>
						<span><i class="fa-solid fa-bolt" aria-hidden="true"></i> Energy Variable</span>
					</label>
					<label class="checkbox-label">
						<input
							type="checkbox"
							checked={context.constraints?.schedule_irregular}
							onchange={(e) => updateConstraint('schedule_irregular', e.currentTarget.checked)}
						/>
						<span><i class="fa-solid fa-calendar" aria-hidden="true"></i> Schedule Irregular</span>
					</label>
				</div>
			</section>

			<!-- Preferences Section -->
			<section class="control-section">
				<h3>Preferences</h3>
				<div class="control-row">
					<div class="control-group">
						<label class="label" for="noise-mode">Noise Mode</label>
						<select
							id="noise-mode"
							class="input select"
							value={context.portable_preferences?.noise_mode}
							onchange={(e) => updatePreference('noise_mode', e.currentTarget.value as any)}
						>
							<option value="normal">Normal</option>
							<option value="quiet_preferred">Quiet Preferred</option>
							<option value="silent_required">Silent Required</option>
						</select>
					</div>
					<div class="control-group">
						<label class="label" for="budget">Budget Range</label>
						<select
							id="budget"
							class="input select"
							value={context.portable_preferences?.budget_range}
							onchange={(e) => updatePreference('budget_range', e.currentTarget.value as any)}
						>
							<option value="unlimited">Unlimited</option>
							<option value="high">High</option>
							<option value="medium">Medium</option>
							<option value="low">Low</option>
							<option value="free_only">Free Only</option>
						</select>
					</div>
				</div>
			</section>

			<!-- Prosaic Dimensions Section -->
			<section class="control-section prosaic-section">
				<h3>Personal State <span class="badge badge-new">New</span></h3>
				<p class="prosaic-intro">How are you right now? These shape <em>how</em> the AI communicates.</p>

				<div class="prosaic-sliders">
					<div class="prosaic-slider-group">
						<div class="prosaic-slider-header">
							<span class="prosaic-emoji">⚡</span>
							<label class="label" for="urgency">Urgency</label>
							<span class="prosaic-value">{(context.prosaic?.urgency ?? 0).toFixed(1)}</span>
						</div>
						<input
							id="urgency"
							type="range"
							min="0"
							max="1"
							step="0.1"
							value={context.prosaic?.urgency ?? 0}
							oninput={(e) => updateProsaic('urgency', parseFloat(e.currentTarget.value))}
							class="slider prosaic-range"
						/>
						<div class="prosaic-hint">
							{context.prosaic?.urgency && context.prosaic.urgency >= 0.7 ? '"I\'m in a hurry"' : context.prosaic?.urgency && context.prosaic.urgency >= 0.4 ? 'Some time pressure' : 'No rush'}
						</div>
					</div>

					<div class="prosaic-slider-group">
						<div class="prosaic-slider-header">
							<span class="prosaic-emoji">💊</span>
							<label class="label" for="health">Health</label>
							<span class="prosaic-value">{(context.prosaic?.health ?? 0).toFixed(1)}</span>
						</div>
						<input
							id="health"
							type="range"
							min="0"
							max="1"
							step="0.1"
							value={context.prosaic?.health ?? 0}
							oninput={(e) => updateProsaic('health', parseFloat(e.currentTarget.value))}
							class="slider prosaic-range"
						/>
						<div class="prosaic-hint">
							{context.prosaic?.health && context.prosaic.health >= 0.7 ? '"Not feeling well"' : context.prosaic?.health && context.prosaic.health >= 0.4 ? 'Some fatigue/discomfort' : 'Feeling fine'}
						</div>
					</div>

					<div class="prosaic-slider-group">
						<div class="prosaic-slider-header">
							<span class="prosaic-emoji">🧩</span>
							<label class="label" for="cognitive">Cognitive Load</label>
							<span class="prosaic-value">{(context.prosaic?.cognitive ?? 0).toFixed(1)}</span>
						</div>
						<input
							id="cognitive"
							type="range"
							min="0"
							max="1"
							step="0.1"
							value={context.prosaic?.cognitive ?? 0}
							oninput={(e) => updateProsaic('cognitive', parseFloat(e.currentTarget.value))}
							class="slider prosaic-range"
						/>
						<div class="prosaic-hint">
							{context.prosaic?.cognitive && context.prosaic.cognitive >= 0.7 ? '"Too many options"' : context.prosaic?.cognitive && context.prosaic.cognitive >= 0.4 ? 'Some mental load' : 'Clear headed'}
						</div>
					</div>

					<div class="prosaic-slider-group">
						<div class="prosaic-slider-header">
							<span class="prosaic-emoji">💭</span>
							<label class="label" for="affect">Emotional State</label>
							<span class="prosaic-value">{(context.prosaic?.affect ?? 0).toFixed(1)}</span>
						</div>
						<input
							id="affect"
							type="range"
							min="0"
							max="1"
							step="0.1"
							value={context.prosaic?.affect ?? 0}
							oninput={(e) => updateProsaic('affect', parseFloat(e.currentTarget.value))}
							class="slider prosaic-range"
						/>
						<div class="prosaic-hint">
							{context.prosaic?.affect && context.prosaic.affect >= 0.7 ? 'High emotional intensity' : context.prosaic?.affect && context.prosaic.affect >= 0.4 ? 'Some stress/emotion' : 'Calm, neutral'}
						</div>
					</div>
				</div>

				<div class="prosaic-presets">
					<span class="preset-label">Quick states:</span>
					<button class="btn btn-ghost btn-xs" onclick={() => { context.prosaic = { urgency: 0.9, health: 0.0, cognitive: 0.3, affect: 0.2 }; }}>
						In a hurry
					</button>
					<button class="btn btn-ghost btn-xs" onclick={() => { context.prosaic = { urgency: 0.2, health: 0.7, cognitive: 0.4, affect: 0.3 }; }}>
						Not well
					</button>
					<button class="btn btn-ghost btn-xs" onclick={() => { context.prosaic = { urgency: 0.3, health: 0.2, cognitive: 0.8, affect: 0.5 }; }}>
						Overwhelmed
					</button>
					<button class="btn btn-ghost btn-xs" onclick={() => { context.prosaic = { urgency: 0.1, health: 0.3, cognitive: 0.4, affect: 0.8, sub_signals: { emotional_state: 'grieving' } }; }}>
						Grieving
					</button>
				</div>
			</section>
		</div>

		<!-- Token Panel -->
		<div class="panel token-panel">
			<div class="panel-header">
				<h2>Generated Token</h2>
				<div class="panel-actions">
					{#if copyFeedback}
						<span class="copy-feedback">{copyFeedback}</span>
					{/if}
					<button class="btn btn-ghost btn-sm" onclick={sharePlayground} title="Copy shareable link">
						<i class="fa-solid fa-share-nodes" aria-hidden="true"></i>
					</button>
					<button class="btn btn-primary btn-sm" onclick={copyToken}>
						<i class="fa-solid fa-copy" aria-hidden="true"></i> Copy Token
					</button>
				</div>
			</div>

			<div class="token-display">
				<pre>{token}</pre>
			</div>

			<!-- Legend -->
			<div class="legend-section">
				<h3>Emoji Key</h3>
				<div class="legend-grid">
					{#each legend as item}
						<div class="legend-item">
							<span class="legend-emoji">{item.emoji}</span>
							<span class="legend-meaning">{item.meaning}</span>
						</div>
					{/each}
				</div>
			</div>

			<!-- Transmission Summary -->
			<div class="summary-section">
				<h3>Transmission Summary</h3>
				<div class="summary-grid">
					<div class="summary-group">
						<h4 class="summary-label summary-transmitted">
							Transmitted ({summary.transmitted.length})
						</h4>
						<div class="field-list">
							{#each summary.transmitted as field}
								<span class="field-tag field-tag-shared">{field}</span>
							{/each}
						</div>
					</div>
					<div class="summary-group">
						<h4 class="summary-label summary-influencing">
							Influencing ({summary.influencing.length})
						</h4>
						<div class="field-list">
							{#each summary.influencing as field}
								<span class="field-tag field-tag-influence">{field}</span>
							{/each}
						</div>
					</div>
					<div class="summary-group">
						<h4 class="summary-label summary-withheld">
							Withheld ({summary.withheld.length})
						</h4>
						<div class="field-list">
							{#each summary.withheld as field}
								<span class="field-tag field-tag-withheld">{field}</span>
							{/each}
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	.playground-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--space-lg);
		margin-bottom: var(--space-2xl);
	}

	.panel {
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
		overflow: hidden;
	}

	.panel-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: var(--space-md) var(--space-lg);
		background: rgba(255, 255, 255, 0.03);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.panel-header h2 {
		font-size: 1rem;
		margin: 0;
	}

	.controls-panel {
		max-height: 80vh;
		overflow-y: auto;
	}

	.control-section {
		padding: var(--space-lg);
		border-bottom: 1px solid rgba(255, 255, 255, 0.05);
	}

	.control-section:last-child {
		border-bottom: none;
	}

	.control-section h3 {
		font-size: 0.8125rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-muted);
		margin-bottom: var(--space-md);
	}

	.control-group {
		margin-bottom: var(--space-md);
	}

	.control-group:last-child {
		margin-bottom: 0;
	}

	.control-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--space-md);
	}

	fieldset.control-group {
		border: none;
		padding: 0;
		margin: 0 0 var(--space-md) 0;
	}

	fieldset.control-group legend {
		padding: 0;
		margin-bottom: var(--space-xs);
	}

	.persona-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: var(--space-xs);
	}

	.persona-btn {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-xs);
		padding: var(--space-sm);
		background: var(--color-bg-elevated);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-md);
		cursor: pointer;
		transition: all var(--transition-fast);
	}

	.persona-btn:hover {
		border-color: rgba(255, 255, 255, 0.2);
	}

	.persona-btn.active {
		border-color: var(--color-primary);
		background: var(--color-primary-muted);
	}

	.persona-icon {
		font-size: 1.25rem;
	}

	.persona-name {
		font-size: 0.6875rem;
		color: var(--color-text-muted);
	}

	.slider {
		width: 100%;
		accent-color: var(--color-primary);
	}

	.checkbox-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--space-sm);
	}

	.checkbox-label {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-size: 0.8125rem;
		cursor: pointer;
	}

	.token-panel {
		position: sticky;
		top: 80px;
		max-height: 80vh;
		overflow-y: auto;
	}

	.token-display {
		padding: var(--space-lg);
		border-bottom: 1px solid rgba(255, 255, 255, 0.05);
	}

	.token-display pre {
		background: var(--color-bg);
		padding: var(--space-md);
		border-radius: var(--radius-md);
		font-family: var(--font-mono);
		font-size: 0.8125rem;
		line-height: 1.6;
		overflow-x: auto;
		margin: 0;
	}

	.legend-section,
	.summary-section {
		padding: var(--space-lg);
		border-bottom: 1px solid rgba(255, 255, 255, 0.05);
	}

	.legend-section h3,
	.summary-section h3 {
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-muted);
		margin-bottom: var(--space-md);
	}

	.legend-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: var(--space-sm);
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-size: 0.75rem;
	}

	.legend-emoji {
		font-size: 1rem;
	}

	.legend-meaning {
		color: var(--color-text-muted);
	}

	.summary-grid {
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
	}

	.summary-label {
		font-size: 0.75rem;
		font-weight: 500;
		margin-bottom: var(--space-xs);
	}

	.summary-transmitted {
		color: var(--color-success);
	}

	.summary-influencing {
		color: var(--color-warning);
	}

	.summary-withheld {
		color: var(--color-danger);
	}

	.field-tag-influence {
		background: var(--color-warning-muted);
		color: var(--color-warning);
	}

	/* Example loaders */
	.example-loaders {
		display: flex;
		align-items: center;
		gap: var(--space-md);
		margin-bottom: var(--space-lg);
		padding: var(--space-md);
		background: var(--color-bg-card);
		border-radius: var(--radius-md);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.example-label {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	/* Panel actions */
	.panel-actions {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
	}

	.copy-feedback {
		font-size: var(--text-xs);
		color: var(--color-success);
		padding: var(--space-xs) var(--space-sm);
		background: var(--color-success-muted);
		border-radius: var(--radius-sm);
		animation: fadeIn 0.2s ease;
	}

	@keyframes fadeIn {
		from { opacity: 0; transform: translateY(-4px); }
		to { opacity: 1; transform: translateY(0); }
	}

	@media (max-width: 900px) {
		.playground-grid {
			grid-template-columns: 1fr;
		}

		.token-panel {
			position: static;
			order: -1; /* Show token first on mobile */
		}

		.controls-panel {
			order: 1;
		}
	}

	/* Prosaic section styles */
	.prosaic-section h3 {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
	}

	.badge-new {
		background: linear-gradient(135deg, var(--color-primary), #8b5cf6);
		color: white;
		font-size: 0.625rem;
		padding: 2px 6px;
		border-radius: var(--radius-sm);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		font-weight: 600;
	}

	.prosaic-intro {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		margin-bottom: var(--space-md);
	}

	.prosaic-sliders {
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
	}

	.prosaic-slider-group {
		background: rgba(255, 255, 255, 0.02);
		padding: var(--space-sm) var(--space-md);
		border-radius: var(--radius-md);
		border: 1px solid rgba(255, 255, 255, 0.05);
	}

	.prosaic-slider-header {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-xs);
	}

	.prosaic-emoji {
		font-size: 1.125rem;
	}

	.prosaic-slider-header .label {
		flex: 1;
		margin: 0;
	}

	.prosaic-value {
		font-family: var(--font-mono);
		font-size: var(--text-sm);
		color: var(--color-primary);
		min-width: 2rem;
		text-align: right;
	}

	.prosaic-range {
		width: 100%;
		margin: var(--space-xs) 0;
	}

	.prosaic-hint {
		font-size: 0.6875rem;
		color: var(--color-text-muted);
		font-style: italic;
		min-height: 1rem;
	}

	.prosaic-presets {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: var(--space-xs);
		margin-top: var(--space-md);
		padding-top: var(--space-md);
		border-top: 1px solid rgba(255, 255, 255, 0.05);
	}

	.preset-label {
		font-size: var(--text-xs);
		color: var(--color-text-muted);
	}

	.btn-xs {
		padding: var(--space-xs) var(--space-sm);
		font-size: 0.6875rem;
	}

	@media (max-width: 640px) {
		.control-row {
			grid-template-columns: 1fr;
		}

		.persona-grid {
			grid-template-columns: repeat(2, 1fr);
		}

		.checkbox-grid {
			grid-template-columns: 1fr;
		}

		.example-loaders {
			flex-direction: column;
			align-items: stretch;
		}

		.panel-actions {
			flex-wrap: wrap;
		}

		.prosaic-presets {
			flex-direction: column;
			align-items: flex-start;
		}
	}
</style>
