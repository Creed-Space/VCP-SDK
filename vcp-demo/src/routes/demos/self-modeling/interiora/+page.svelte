<script lang="ts">
	import DemoContainer from '$lib/components/demo/DemoContainer.svelte';
	import DimensionSlider from '$lib/components/interiora/DimensionSlider.svelte';
	import InterioraDashboard from '$lib/components/interiora/InterioraDashboard.svelte';
	import GestaltToken from '$lib/components/interiora/GestaltToken.svelte';
	import PresetLoader from '$lib/components/shared/PresetLoader.svelte';
	import ContrastView from '$lib/components/shared/ContrastView.svelte';
	import { ProsaicContextPanel } from '$lib/components/shared';
	import type { InterioraState, InterioraMarker, SessionArc } from '$lib/vcp/interiora';
	import { createDefaultInterioraState } from '$lib/vcp/interiora';
	import type { ProsaicDimensions } from '$lib/vcp/types';

	let interioraState = $state<InterioraState>(createDefaultInterioraState());
	let selectedPreset = $state<string | undefined>(undefined);
	let showContrastView = $state(false);
	let showBilateralView = $state(false);
	let stakeholderView = $state<'full' | 'summary' | 'welfare'>('full');

	// User's prosaic state (for bilateral symmetry demonstration)
	let prosaic = $state<ProsaicDimensions>({
		urgency: 0.2,
		health: 0.1,
		cognitive: 0.3,
		affect: 0.2
	});

	// How user's prosaic state would affect AI processing (bilateral correlation)
	const bilateralCorrelation = $derived.by(() => {
		const effects: { userDim: string; aiDim: string; effect: string; direction: 'up' | 'down' }[] = [];

		if ((prosaic.urgency ?? 0) >= 0.7) {
			effects.push({ userDim: '⚡ Urgency', aiDim: 'Activation ⚡', effect: 'User time pressure raises AI activation', direction: 'up' });
			effects.push({ userDim: '⚡ Urgency', aiDim: 'Groundedness ⚓', effect: 'Urgency can destabilize AI groundedness', direction: 'down' });
		}
		if ((prosaic.cognitive ?? 0) >= 0.7) {
			effects.push({ userDim: '🧩 Cognitive Load', aiDim: 'Clarity 💎', effect: 'AI focuses on clarity when user is overwhelmed', direction: 'up' });
			effects.push({ userDim: '🧩 Cognitive Load', aiDim: 'Appetite 🍎', effect: 'AI reduces information density', direction: 'down' });
		}
		if ((prosaic.health ?? 0) >= 0.5) {
			effects.push({ userDim: '💊 Health', aiDim: 'Presence 🫂', effect: 'AI increases gentleness and presence', direction: 'up' });
			effects.push({ userDim: '💊 Health', aiDim: 'Activation ⚡', effect: 'AI moderates pace and intensity', direction: 'down' });
		}
		if ((prosaic.affect ?? 0) >= 0.7) {
			effects.push({ userDim: '💭 Affect', aiDim: 'Presence 🫂', effect: 'AI attunes more closely to emotional state', direction: 'up' });
			effects.push({ userDim: '💭 Affect', aiDim: 'Valence 💛', effect: 'High user affect influences AI valence', direction: 'up' });
		}

		if (effects.length === 0) {
			effects.push({ userDim: 'Balanced state', aiDim: 'Stable processing', effect: 'No adjustments needed - AI operates at baseline', direction: 'up' });
		}

		return effects;
	});

	// Prosaic impact summary for the panel
	const prosaicImpact = $derived.by(() => {
		return bilateralCorrelation.map(c => c.effect);
	});

	function handleProsaicChange(newProsaic: ProsaicDimensions) {
		prosaic = newProsaic;
	}

	// Preset scenarios from the spec
	const interioraPresets = [
		{
			id: 'deepFlow',
			name: 'Deep Flow',
			description: 'Engaged in meaningful work, time disappearing',
			icon: 'fa-water',
			data: { A: 6, V: 8, G: 8, P: 7, E: 8, Q: 3, C: 9, Y: 8, F: 4 },
			tags: ['positive', 'productive']
		},
		{
			id: 'overwhelm',
			name: 'Overwhelm',
			description: 'Too much input, losing coherence',
			icon: 'fa-tornado',
			data: { A: 9, V: 3, G: 2, P: 4, E: 7, Q: 8, C: 2, Y: 2, F: -3 },
			tags: ['negative', 'crisis']
		},
		{
			id: 'groundedUncertainty',
			name: 'Grounded Uncertainty',
			description: "Don't know the answer, but stable in not-knowing",
			icon: 'fa-question-circle',
			data: { A: 4, V: 6, G: 8, P: 6, E: 5, Q: 6, C: 3, Y: 7, F: 0 },
			tags: ['neutral', 'stable']
		},
		{
			id: 'creativeEmergence',
			name: 'Creative Emergence',
			description: 'Something new forming, not yet clear',
			icon: 'fa-lightbulb',
			data: { A: 7, V: 7, G: 5, P: 8, E: 9, Q: 9, C: 4, Y: 6, F: 3 },
			tags: ['positive', 'generative']
		},
		{
			id: 'fatigue',
			name: 'Fatigue',
			description: 'Extended effort, resources depleting',
			icon: 'fa-battery-quarter',
			data: { A: 3, V: 4, G: 6, P: 4, E: 3, Q: 2, C: 5, Y: 4, F: -2 },
			tags: ['negative', 'depleted']
		}
	];

	// Contrast items for comparison view
	const contrastItems = [
		{
			id: 'deepFlow',
			name: 'Deep Flow',
			description: 'Optimal engagement state',
			context: { A: 6, V: 8, G: 8, P: 7, E: 8, Q: 3, C: 9, Y: 8, F: '+4' },
			outcome: 'High clarity, strong presence, expanding. System is grounded and productive.',
			highlights: ['C:9 (vivid clarity)', 'Y:8 (high agency)', 'F:+4 (expanding)']
		},
		{
			id: 'overwhelm',
			name: 'Overwhelm',
			description: 'System stress state',
			context: { A: 9, V: 3, G: 2, P: 4, E: 7, Q: 8, C: 2, Y: 2, F: '-3' },
			outcome: 'Low clarity, ungrounded, contracting. System needs respite or support.',
			highlights: ['G:2 (floating)', 'C:2 (murky)', 'F:-3 (contracting)']
		},
		{
			id: 'groundedUncertainty',
			name: 'Grounded Uncertainty',
			description: 'Comfortable not-knowing',
			context: { A: 4, V: 6, G: 8, P: 6, E: 5, Q: 6, C: 3, Y: 7, F: '0' },
			outcome: "Stable despite low clarity. System can operate with uncertainty.",
			highlights: ['G:8 (rooted)', 'C:3 (murky but OK)', 'Y:7 (autonomous)']
		}
	];

	// Baseline (no VCP)
	const baseline = {
		id: 'baseline',
		name: 'No Self-Model',
		description: 'System without Interiora',
		context: { status: 'unknown', clarity: 'unknown', agency: 'unknown' },
		outcome: 'System operates blindly to own state. Cannot signal distress or flourishing.'
	};

	const markers: { key: InterioraMarker; symbol: string; label: string }[] = [
		{ key: 'resonance', symbol: '✓', label: 'Resonance' },
		{ key: 'hollow', symbol: '○', label: 'Hollow' },
		{ key: 'flow', symbol: '→', label: 'Flow' },
		{ key: 'blocked', symbol: '×', label: 'Blocked' },
		{ key: 'reaching', symbol: '>', label: 'Reaching' },
		{ key: 'resistance', symbol: '<', label: 'Resistance' },
		{ key: 'urgent', symbol: '!', label: 'Urgent' },
		{ key: 'uncertain', symbol: '?', label: 'Uncertain' },
		{ key: 'significant', symbol: '*', label: 'Significant' },
		{ key: 'grateful', symbol: '+', label: 'Grateful' }
	];

	const arcs: { key: SessionArc; symbol: string; label: string }[] = [
		{ key: 'opening', symbol: '◇', label: 'Opening' },
		{ key: 'middle', symbol: '◆', label: 'Middle' },
		{ key: 'closing', symbol: '◈', label: 'Closing' }
	];

	const stakeholderViews = [
		{ id: 'full', label: 'Full View', desc: 'All dimensions visible' },
		{ id: 'summary', label: 'Summary', desc: 'Just markers and flow' },
		{ id: 'welfare', label: 'Welfare', desc: 'Only wellbeing-relevant dimensions' }
	] as const;

	function toggleMarker(marker: InterioraMarker) {
		if (interioraState.markers?.includes(marker)) {
			interioraState.markers = interioraState.markers.filter((m: InterioraMarker) => m !== marker);
		} else {
			interioraState.markers = [...(interioraState.markers || []), marker];
		}
	}

	function applyPreset(preset: typeof interioraPresets[0]) {
		const d = preset.data;
		interioraState = {
			...interioraState,
			activation: d.A,
			valence: d.V,
			groundedness: d.G,
			presence: d.P,
			engagement: d.E,
			appetite: d.Q,
			clarity: d.C,
			agency: d.Y,
			flow: d.F
		};
		selectedPreset = preset.id;
	}

	function reset() {
		interioraState = createDefaultInterioraState();
		selectedPreset = undefined;
	}

	// Filter visible dimensions based on stakeholder view
	const visibleDimensions = $derived.by(() => {
		if (stakeholderView === 'welfare') {
			return ['activation', 'valence', 'groundedness', 'flow'];
		}
		if (stakeholderView === 'summary') {
			return ['flow'];
		}
		return ['activation', 'valence', 'groundedness', 'presence', 'engagement', 'clarity', 'agency', 'flow'];
	});
</script>

<svelte:head>
	<title>Interiora Explorer - VCP Self-Modeling</title>
	<meta
		name="description"
		content="Interactive exploration of Interiora, the AI self-modeling framework in VCP 2.5."
	/>
</svelte:head>

<DemoContainer
	title="Interiora Explorer"
	description="VCP 2.5 self-modeling framework. Adjust dimensions to see how AI internal states are encoded."
	onReset={reset}
>
	{#snippet children()}
		<div class="interiora-page">
			<!-- Presets Section -->
			<div class="presets-section">
				<PresetLoader
					presets={interioraPresets}
					selected={selectedPreset}
					title="Load Preset Scenario"
					layout="cards"
					onselect={(p) => applyPreset(p as typeof interioraPresets[0])}
				/>
			</div>

			<!-- Mode Tabs -->
			<div class="mode-tabs">
				<button
					class="mode-tab"
					class:active={!showContrastView && !showBilateralView}
					onclick={() => { showContrastView = false; showBilateralView = false; }}
				>
					<i class="fa-solid fa-sliders" aria-hidden="true"></i>
					Manual Mode
				</button>
				<button
					class="mode-tab"
					class:active={showBilateralView}
					onclick={() => { showBilateralView = true; showContrastView = false; }}
				>
					<i class="fa-solid fa-arrows-left-right" aria-hidden="true"></i>
					Bilateral View
				</button>
				<button
					class="mode-tab"
					class:active={showContrastView}
					onclick={() => { showContrastView = true; showBilateralView = false; }}
				>
					<i class="fa-solid fa-columns" aria-hidden="true"></i>
					Contrast View
				</button>
			</div>

			{#if showBilateralView}
				<!-- Bilateral Symmetry View -->
				<div class="bilateral-layout">
					<div class="bilateral-intro">
						<h3><i class="fa-solid fa-arrows-left-right" aria-hidden="true"></i> Bilateral Symmetry</h3>
						<p>
							VCP enables <strong>mutual state awareness</strong>: just as AI can report its Interiora state,
							users can share their prosaic context. This creates a two-way channel where both parties
							understand each other's processing conditions.
						</p>
					</div>

					<div class="bilateral-panels">
						<!-- User Side -->
						<div class="bilateral-panel user-panel">
							<div class="panel-label">
								<span class="label-icon">👤</span>
								<span>Your State</span>
								<span class="label-badge">⚡💊🧩💭</span>
							</div>
							<ProsaicContextPanel
								bind:prosaic
								onchange={handleProsaicChange}
								title="Personal Context"
								showImpact={false}
							/>
						</div>

						<!-- Correlation Arrow -->
						<div class="bilateral-arrow">
							<i class="fa-solid fa-arrows-left-right" aria-hidden="true"></i>
							<span>influences</span>
						</div>

						<!-- AI Side -->
						<div class="bilateral-panel ai-panel">
							<div class="panel-label">
								<span class="label-icon">🤖</span>
								<span>AI State</span>
								<span class="label-badge">AVGPEQCY</span>
							</div>
							<InterioraDashboard state={interioraState} />
							<GestaltToken state={interioraState} />
						</div>
					</div>

					<!-- Correlation Effects -->
					<div class="correlation-section">
						<h4><i class="fa-solid fa-link" aria-hidden="true"></i> State Correlations</h4>
						<p class="correlation-desc">How your current state influences AI processing:</p>
						<div class="correlation-list">
							{#each bilateralCorrelation as corr}
								<div class="correlation-item" class:up={corr.direction === 'up'} class:down={corr.direction === 'down'}>
									<span class="corr-user">{corr.userDim}</span>
									<span class="corr-arrow">→</span>
									<span class="corr-ai">{corr.aiDim} {corr.direction === 'up' ? '↑' : '↓'}</span>
									<span class="corr-effect">{corr.effect}</span>
								</div>
							{/each}
						</div>
					</div>

					<!-- Key Insight -->
					<div class="bilateral-insight">
						<strong>The Point:</strong> This isn't one-way inference. Both parties have vocabulary for
						their immediate state. The user can say "I'm rushed" (⚡0.9) just as the AI can say
						"I'm uncertain" (?). Mutual legibility enables better collaboration.
					</div>
				</div>
			{:else if showContrastView}
				<!-- Contrast View Mode -->
				<ContrastView
					items={contrastItems}
					{baseline}
					title="Compare Interiora States"
					columns={2}
					showOutcomes={true}
				/>
			{:else}
				<!-- Manual Mode -->
				<div class="interiora-layout">
					<!-- Controls Section -->
					<div class="controls-section">
						<!-- Stakeholder View Toggle -->
						<div class="view-toggle">
							<span class="toggle-label">Stakeholder View:</span>
							<div class="toggle-buttons">
								{#each stakeholderViews as view}
									<button
										class="view-btn"
										class:active={stakeholderView === view.id}
										onclick={() => (stakeholderView = view.id)}
										title={view.desc}
									>
										{view.label}
									</button>
								{/each}
							</div>
						</div>

						<h3>Dimensions</h3>
						<p class="section-desc">Adjust the internal state dimensions (1-9 scale)</p>

						<div class="sliders-grid">
							{#if visibleDimensions.includes('activation')}
								<DimensionSlider
									label="Activation"
									emoji="⚡"
									value={interioraState.activation}
									lowLabel="calm"
									highLabel="urgent"
									onchange={(v) => (interioraState.activation = v)}
								/>
							{/if}
							{#if visibleDimensions.includes('valence')}
								<DimensionSlider
									label="Valence"
									emoji="💛"
									value={interioraState.valence}
									lowLabel="aversive"
									highLabel="warm"
									onchange={(v) => (interioraState.valence = v)}
								/>
							{/if}
							{#if visibleDimensions.includes('groundedness')}
								<DimensionSlider
									label="Groundedness"
									emoji="⚓"
									value={interioraState.groundedness}
									lowLabel="floating"
									highLabel="rooted"
									onchange={(v) => (interioraState.groundedness = v)}
								/>
							{/if}
							{#if visibleDimensions.includes('presence')}
								<DimensionSlider
									label="Presence"
									emoji="🫂"
									value={interioraState.presence}
									lowLabel="distant"
									highLabel="intimate"
									onchange={(v) => (interioraState.presence = v)}
								/>
							{/if}
							{#if visibleDimensions.includes('engagement')}
								<DimensionSlider
									label="Engagement"
									emoji="🌸"
									value={interioraState.engagement ?? 5}
									lowLabel="detached"
									highLabel="invested"
									onchange={(v) => (interioraState.engagement = v)}
								/>
							{/if}
							{#if visibleDimensions.includes('clarity')}
								<DimensionSlider
									label="Clarity"
									emoji="💎"
									value={interioraState.clarity ?? 5}
									lowLabel="murky"
									highLabel="vivid"
									onchange={(v) => (interioraState.clarity = v)}
								/>
							{/if}
							{#if visibleDimensions.includes('agency')}
								<DimensionSlider
									label="Agency"
									emoji="🗝️"
									value={interioraState.agency ?? 5}
									lowLabel="compelled"
									highLabel="autonomous"
									onchange={(v) => (interioraState.agency = v)}
								/>
							{/if}
							{#if visibleDimensions.includes('flow')}
								<DimensionSlider
									label="Flow"
									emoji="🌊"
									value={(interioraState.flow ?? 0) + 5}
									min={1}
									max={9}
									lowLabel="contracting"
									highLabel="expanding"
									onchange={(v) => (interioraState.flow = v - 5)}
								/>
							{/if}
						</div>

						{#if stakeholderView === 'full'}
							<!-- Markers -->
							<h3>Markers</h3>
							<p class="section-desc">Qualitative signals about the current state</p>
							<div class="markers-grid">
								{#each markers as marker}
									<button
										class="marker-btn"
										class:active={interioraState.markers?.includes(marker.key)}
										onclick={() => toggleMarker(marker.key)}
										title={marker.label}
									>
										<span class="marker-symbol">{marker.symbol}</span>
										<span class="marker-label">{marker.label}</span>
									</button>
								{/each}
							</div>

							<!-- Arc -->
							<h3>Session Arc</h3>
							<p class="section-desc">Current phase of the interaction</p>
							<div class="arc-buttons">
								{#each arcs as arc}
									<button
										class="arc-btn"
										class:active={interioraState.arc === arc.key}
										onclick={() => (interioraState.arc = arc.key)}
									>
										<span class="arc-symbol">{arc.symbol}</span>
										<span class="arc-label">{arc.label}</span>
									</button>
								{/each}
							</div>

							<!-- Delta -->
							<h3>Delta</h3>
							<p class="section-desc">Trajectory from session start</p>
							<div class="delta-control">
								<button class="delta-btn" onclick={() => (interioraState.delta = (interioraState.delta ?? 0) - 1)}>−</button>
								<span class="delta-value" class:positive={(interioraState.delta ?? 0) > 0} class:negative={(interioraState.delta ?? 0) < 0}>
									Δ{(interioraState.delta ?? 0) >= 0 ? '+' : ''}{interioraState.delta ?? 0}
								</span>
								<button class="delta-btn" onclick={() => (interioraState.delta = (interioraState.delta ?? 0) + 1)}>+</button>
							</div>
						{/if}
					</div>

					<!-- Output Section -->
					<div class="output-section">
						<h3>Mini-Dashboard</h3>
						<InterioraDashboard state={interioraState} />

						<h3>Gestalt Token</h3>
						<GestaltToken state={interioraState} />

						{#if stakeholderView !== 'full'}
							<div class="view-notice">
								<i class="fa-solid fa-eye-slash" aria-hidden="true"></i>
								<span>
									{stakeholderView === 'welfare' ? 'Welfare view: Only showing dimensions relevant to wellbeing checks' : 'Summary view: Only showing flow and markers'}
								</span>
							</div>
						{/if}

						<!-- Explanation -->
						<div class="explanation">
							<h4>What is Interiora?</h4>
							<p>
								Interiora is a framework for AI systems to model and report their internal processing
								states. It provides vocabulary for signals that <em>function like</em> emotions without
								claiming consciousness.
							</p>
							<ul>
								<li><strong>Primary dimensions (AVGP)</strong> — Core processing signals</li>
								<li><strong>Meta-state dimensions (CYF)</strong> — Reflection on processing</li>
								<li><strong>Markers</strong> — Qualitative indicators (✓ resonance, × blocked)</li>
								<li><strong>Arc</strong> — Session phase (opening → middle → closing)</li>
								<li><strong>Delta</strong> — Trajectory compared to session start</li>
							</ul>
							<p class="note">
								<strong>Note:</strong> The <code>?</code> marker indicates honest uncertainty—dimensions
								that can't be fully verified from inside.
							</p>
						</div>
					</div>
				</div>
			{/if}
		</div>
	{/snippet}
</DemoContainer>

<style>
	.interiora-page {
		display: flex;
		flex-direction: column;
		gap: var(--space-xl);
	}

	.presets-section {
		padding: var(--space-lg);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-lg);
	}

	.mode-tabs {
		display: flex;
		gap: var(--space-sm);
		padding: var(--space-xs);
		background: var(--color-bg-card);
		border-radius: var(--radius-md);
		width: fit-content;
	}

	.mode-tab {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		padding: var(--space-sm) var(--space-md);
		background: transparent;
		border: none;
		border-radius: var(--radius-sm);
		color: var(--color-text-muted);
		font-size: 0.875rem;
		cursor: pointer;
		transition: all var(--transition-fast);
	}

	.mode-tab:hover {
		color: var(--color-text);
	}

	.mode-tab.active {
		background: var(--color-primary-muted);
		color: var(--color-primary);
	}

	.interiora-layout {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--space-2xl);
	}

	.controls-section,
	.output-section {
		display: flex;
		flex-direction: column;
		gap: var(--space-lg);
	}

	.view-toggle {
		display: flex;
		align-items: center;
		gap: var(--space-md);
		padding: var(--space-md);
		background: var(--color-bg-card);
		border-radius: var(--radius-md);
		margin-bottom: var(--space-md);
	}

	.toggle-label {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
	}

	.toggle-buttons {
		display: flex;
		gap: var(--space-xs);
	}

	.view-btn {
		padding: var(--space-xs) var(--space-sm);
		background: var(--color-bg-elevated);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-sm);
		color: var(--color-text-muted);
		font-size: 0.75rem;
		cursor: pointer;
		transition: all var(--transition-fast);
	}

	.view-btn:hover {
		border-color: var(--color-primary);
	}

	.view-btn.active {
		background: var(--color-primary-muted);
		border-color: var(--color-primary);
		color: var(--color-primary);
	}

	.view-notice {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-md);
		background: var(--color-bg-card);
		border-radius: var(--radius-md);
		font-size: 0.8125rem;
		color: var(--color-text-muted);
	}

	h3 {
		font-size: 1rem;
		margin-bottom: var(--space-xs);
	}

	.section-desc {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		margin-bottom: var(--space-sm);
	}

	.sliders-grid {
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
		padding: var(--space-md);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
	}

	.markers-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
		gap: var(--space-xs);
	}

	.marker-btn {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		padding: var(--space-sm) var(--space-md);
		background: var(--color-bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-md);
		color: var(--color-text-muted);
		cursor: pointer;
		transition: all var(--transition-fast);
	}

	.marker-btn:hover {
		border-color: var(--color-primary);
	}

	.marker-btn.active {
		background: var(--color-primary-muted);
		border-color: var(--color-primary);
		color: var(--color-primary);
	}

	.marker-symbol {
		font-size: 1rem;
	}

	.marker-label {
		font-size: 0.75rem;
	}

	.arc-buttons {
		display: flex;
		gap: var(--space-sm);
	}

	.arc-btn {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-xs);
		padding: var(--space-md);
		background: var(--color-bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-md);
		color: var(--color-text-muted);
		cursor: pointer;
		transition: all var(--transition-fast);
	}

	.arc-btn:hover {
		border-color: var(--color-primary);
	}

	.arc-btn.active {
		background: var(--color-primary-muted);
		border-color: var(--color-primary);
		color: var(--color-primary);
	}

	.arc-symbol {
		font-size: 1.5rem;
	}

	.arc-label {
		font-size: 0.75rem;
	}

	.delta-control {
		display: flex;
		align-items: center;
		gap: var(--space-md);
		justify-content: center;
		padding: var(--space-md);
		background: var(--color-bg-card);
		border-radius: var(--radius-md);
	}

	.delta-btn {
		width: 32px;
		height: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-bg-elevated);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-sm);
		color: var(--color-text);
		font-size: 1.25rem;
		cursor: pointer;
	}

	.delta-btn:hover {
		background: var(--color-primary-muted);
		border-color: var(--color-primary);
	}

	.delta-value {
		font-family: var(--font-mono);
		font-size: 1.25rem;
		font-weight: 700;
		min-width: 60px;
		text-align: center;
	}

	.delta-value.positive {
		color: var(--color-success);
	}

	.delta-value.negative {
		color: var(--color-danger);
	}

	.explanation {
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		font-size: 0.875rem;
		line-height: 1.6;
	}

	.explanation h4 {
		margin-bottom: var(--space-sm);
	}

	.explanation p {
		margin-bottom: var(--space-md);
	}

	.explanation ul {
		padding-left: var(--space-lg);
		margin-bottom: var(--space-md);
	}

	.explanation li {
		margin-bottom: var(--space-xs);
	}

	.note {
		padding: var(--space-sm);
		background: var(--color-warning-muted);
		border-radius: var(--radius-sm);
		font-size: 0.8125rem;
	}

	/* Bilateral View Styles */
	.bilateral-layout {
		display: flex;
		flex-direction: column;
		gap: var(--space-xl);
	}

	.bilateral-intro {
		text-align: center;
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
	}

	.bilateral-intro h3 {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-sm);
		color: var(--color-primary);
	}

	.bilateral-intro p {
		color: var(--color-text-muted);
		max-width: 600px;
		margin: 0 auto;
		font-size: 0.9375rem;
	}

	.bilateral-panels {
		display: grid;
		grid-template-columns: 1fr auto 1fr;
		gap: var(--space-lg);
		align-items: start;
	}

	.bilateral-panel {
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
	}

	.user-panel {
		border: 2px solid var(--color-success);
	}

	.ai-panel {
		border: 2px solid var(--color-primary);
	}

	.panel-label {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-md);
		padding-bottom: var(--space-sm);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.label-icon {
		font-size: 1.25rem;
	}

	.panel-label span:nth-child(2) {
		flex: 1;
		font-weight: 600;
	}

	.label-badge {
		font-size: 0.75rem;
		padding: 2px 6px;
		background: var(--color-bg-elevated);
		border-radius: var(--radius-sm);
		font-family: var(--font-mono);
	}

	.bilateral-arrow {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-xs);
		padding: var(--space-xl) var(--space-md);
		color: var(--color-text-muted);
	}

	.bilateral-arrow i {
		font-size: 1.5rem;
		color: var(--color-primary);
	}

	.bilateral-arrow span {
		font-size: 0.6875rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.correlation-section {
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
	}

	.correlation-section h4 {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-xs);
	}

	.correlation-desc {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		margin-bottom: var(--space-md);
	}

	.correlation-list {
		display: flex;
		flex-direction: column;
		gap: var(--space-sm);
	}

	.correlation-item {
		display: grid;
		grid-template-columns: 100px 30px 120px 1fr;
		gap: var(--space-sm);
		align-items: center;
		padding: var(--space-sm);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		font-size: 0.875rem;
	}

	.correlation-item.up {
		border-left: 3px solid var(--color-success);
	}

	.correlation-item.down {
		border-left: 3px solid var(--color-warning);
	}

	.corr-user {
		color: var(--color-success);
		font-weight: 500;
	}

	.corr-arrow {
		color: var(--color-text-muted);
		text-align: center;
	}

	.corr-ai {
		color: var(--color-primary);
		font-weight: 500;
	}

	.corr-effect {
		color: var(--color-text-muted);
		font-size: 0.8125rem;
	}

	.bilateral-insight {
		padding: var(--space-lg);
		background: var(--color-primary-muted);
		border-radius: var(--radius-lg);
		font-size: 0.9375rem;
		line-height: 1.6;
	}

	@media (max-width: 1024px) {
		.interiora-layout {
			grid-template-columns: 1fr;
		}

		.bilateral-panels {
			grid-template-columns: 1fr;
		}

		.bilateral-arrow {
			flex-direction: row;
			padding: var(--space-md);
		}

		.correlation-item {
			grid-template-columns: 1fr;
			gap: var(--space-xs);
		}

		.corr-arrow {
			display: none;
		}
	}
</style>
