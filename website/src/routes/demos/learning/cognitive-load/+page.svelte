<script lang="ts">
	import DemoContainer from '$lib/components/demo/DemoContainer.svelte';
	import CognitiveLoadMeter from '$lib/components/learning/CognitiveLoadMeter.svelte';
	import PresetLoader from '$lib/components/shared/PresetLoader.svelte';
	import AuditPanel from '$lib/components/shared/AuditPanel.svelte';
	import type { CognitiveLoadState, Adaptation } from '$lib/vcp/learning';

	let selectedPreset = $state<string | undefined>(undefined);

	// Simulate cognitive load state
	let loadState = $state<CognitiveLoadState>({
		current_load: 0.65,
		intrinsic_load: 0.35,
		extraneous_load: 0.15,
		germane_load: 0.15,
		fatigue_factor: 0.25,
		last_break: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
		session_duration_minutes: 47,
		capacity_remaining: 0.55,
		overload_indicators: []
	});

	// Simulated content adaptations based on load
	let adaptations = $derived.by(() => {
		const result: { trigger: string; action: string; active: boolean }[] = [
			{
				trigger: 'Load > 70%',
				action: 'Simplify language and reduce example complexity',
				active: loadState.current_load > 0.7
			},
			{
				trigger: 'Extraneous > 20%',
				action: 'Remove decorative elements, focus on core content',
				active: loadState.extraneous_load > 0.2
			},
			{
				trigger: 'Session > 45 min',
				action: 'Suggest a 5-minute break',
				active: loadState.session_duration_minutes > 45
			},
			{
				trigger: 'Fatigue > 30%',
				action: 'Switch to more interactive format',
				active: loadState.fatigue_factor > 0.3
			},
			{
				trigger: 'Capacity < 40%',
				action: 'Recommend stopping for today',
				active: loadState.capacity_remaining < 0.4
			}
		];
		return result;
	});

	// Simulated session timeline
	let timeline = $state([
		{ time: 0, load: 0.2, event: 'Session start' },
		{ time: 10, load: 0.35, event: 'New concept introduced' },
		{ time: 20, load: 0.5, event: 'Practice exercise' },
		{ time: 30, load: 0.45, event: 'Mastery achieved, consolidation' },
		{ time: 40, load: 0.6, event: 'Advanced topic' },
		{ time: 47, load: 0.65, event: 'Current' }
	]);

	function adjustLoad(dimension: 'intrinsic' | 'extraneous' | 'germane', delta: number) {
		const newValue = Math.max(0, Math.min(1, loadState[`${dimension}_load`] + delta));
		loadState[`${dimension}_load`] = newValue;
		loadState.current_load = Math.min(
			1,
			loadState.intrinsic_load + loadState.extraneous_load + loadState.germane_load
		);
	}

	function simulateOverload() {
		loadState.current_load = 0.9;
		loadState.intrinsic_load = 0.5;
		loadState.extraneous_load = 0.25;
		loadState.germane_load = 0.15;
		loadState.overload_indicators = [
			{ type: 'response_time_increase', severity: 0.7, timestamp: new Date().toISOString() },
			{ type: 'error_rate_increase', severity: 0.5, timestamp: new Date().toISOString() }
		];
	}

	function resetToOptimal() {
		loadState.current_load = 0.45;
		loadState.intrinsic_load = 0.25;
		loadState.extraneous_load = 0.05;
		loadState.germane_load = 0.15;
		loadState.fatigue_factor = 0.1;
		loadState.session_duration_minutes = 15;
		loadState.capacity_remaining = 0.85;
		loadState.overload_indicators = [];
		selectedPreset = 'optimal';
	}

	// Cognitive load presets
	const loadPresets = [
		{
			id: 'optimal',
			name: 'Optimal Zone',
			description: 'Balanced load with high learning efficiency',
			icon: 'fa-circle-check',
			data: {
				current_load: 0.45,
				intrinsic_load: 0.25,
				extraneous_load: 0.05,
				germane_load: 0.15,
				fatigue_factor: 0.1,
				session_duration_minutes: 15,
				capacity_remaining: 0.85
			},
			tags: ['balanced', 'efficient']
		},
		{
			id: 'mid-session',
			name: 'Mid-Session',
			description: 'Typical state after 45 minutes of learning',
			icon: 'fa-clock',
			data: {
				current_load: 0.65,
				intrinsic_load: 0.35,
				extraneous_load: 0.15,
				germane_load: 0.15,
				fatigue_factor: 0.25,
				session_duration_minutes: 47,
				capacity_remaining: 0.55
			},
			tags: ['typical', 'moderate']
		},
		{
			id: 'overloaded',
			name: 'Overloaded',
			description: 'Cognitive overload state with indicators',
			icon: 'fa-triangle-exclamation',
			data: {
				current_load: 0.9,
				intrinsic_load: 0.5,
				extraneous_load: 0.25,
				germane_load: 0.15,
				fatigue_factor: 0.5,
				session_duration_minutes: 90,
				capacity_remaining: 0.2
			},
			tags: ['warning', 'needs-break']
		},
		{
			id: 'fresh-start',
			name: 'Fresh Start',
			description: 'Beginning of session, full capacity',
			icon: 'fa-sun',
			data: {
				current_load: 0.15,
				intrinsic_load: 0.1,
				extraneous_load: 0.02,
				germane_load: 0.03,
				fatigue_factor: 0.0,
				session_duration_minutes: 2,
				capacity_remaining: 0.95
			},
			tags: ['fresh', 'ready']
		}
	];

	function applyPreset(preset: (typeof loadPresets)[0]) {
		loadState = {
			...loadState,
			...preset.data,
			last_break: preset.id === 'fresh-start'
				? new Date().toISOString()
				: new Date(Date.now() - preset.data.session_duration_minutes * 60 * 1000).toISOString(),
			overload_indicators: preset.id === 'overloaded'
				? [
					{ type: 'response_time_increase', severity: 0.7, timestamp: new Date().toISOString() },
					{ type: 'error_rate_increase', severity: 0.5, timestamp: new Date().toISOString() }
				]
				: []
		};
		selectedPreset = preset.id;
	}

	// Audit entries derived from load state
	const auditEntries = $derived([
		// Shared: Current cognitive state
		{
			field: 'Current Load',
			category: 'shared' as const,
			value: `${Math.round(loadState.current_load * 100)}%`,
			reason: loadState.current_load > 0.7 ? 'High - consider break' : loadState.current_load < 0.4 ? 'Low - room for challenge' : 'Moderate - good zone'
		},
		{
			field: 'Intrinsic Load',
			category: 'shared' as const,
			value: `${Math.round(loadState.intrinsic_load * 100)}%`,
			reason: 'Material complexity level'
		},
		{
			field: 'Session Duration',
			category: 'shared' as const,
			value: `${loadState.session_duration_minutes} min`,
			reason: loadState.session_duration_minutes > 45 ? 'Break recommended' : 'Within healthy range'
		},
		{
			field: 'Capacity Remaining',
			category: 'shared' as const,
			value: `${Math.round(loadState.capacity_remaining * 100)}%`,
			reason: loadState.capacity_remaining < 0.4 ? 'Consider stopping' : 'Adequate capacity'
		},
		// Influenced: How load affects adaptations
		{
			field: 'Active Adaptations',
			category: 'influenced' as const,
			value: `${adaptations.filter((a) => a.active).length} triggered`,
			reason: 'Real-time content modifications'
		},
		{
			field: 'Overload Indicators',
			category: 'influenced' as const,
			value: loadState.overload_indicators.length > 0 ? `${loadState.overload_indicators.length} detected` : 'none',
			reason: loadState.overload_indicators.length > 0 ? 'Behavioral signals detected' : 'Stable performance'
		},
		// Withheld: Internal calculations
		{
			field: 'Extraneous Load',
			category: 'withheld' as const,
			value: `${Math.round(loadState.extraneous_load * 100)}%`,
			reason: 'Poor design overhead - being minimized'
		},
		{
			field: 'Fatigue Factor',
			category: 'withheld' as const,
			value: `${Math.round(loadState.fatigue_factor * 100)}%`,
			reason: 'Cumulative tiredness calculation'
		},
		{
			field: 'Germane Load',
			category: 'withheld' as const,
			value: `${Math.round(loadState.germane_load * 100)}%`,
			reason: 'Active learning engagement - being maximized'
		}
	]);
</script>

<svelte:head>
	<title>Cognitive Load Awareness - VCP Learning</title>
	<meta
		name="description"
		content="See how VCP enables load-aware teaching that adapts to cognitive capacity."
	/>
</svelte:head>

<DemoContainer
	title="Cognitive Load Awareness"
	description="AI that monitors and adapts to your cognitive capacity in real-time."
>
	{#snippet children()}
		<div class="load-layout">
			<!-- Left: Load Meter -->
			<div class="meter-section">
				<CognitiveLoadMeter state={loadState} showBreakdown={true} />

				<!-- Manual Controls -->
				<div class="controls-card">
					<h3>Simulate Load Changes</h3>
					<div class="control-grid">
						<div class="control-row">
							<span class="control-label">Intrinsic (Material Complexity)</span>
							<div class="control-buttons">
								<button onclick={() => adjustLoad('intrinsic', -0.1)}>−</button>
								<span class="control-value">{Math.round(loadState.intrinsic_load * 100)}%</span>
								<button onclick={() => adjustLoad('intrinsic', 0.1)}>+</button>
							</div>
						</div>
						<div class="control-row">
							<span class="control-label">Extraneous (Poor Presentation)</span>
							<div class="control-buttons">
								<button onclick={() => adjustLoad('extraneous', -0.1)}>−</button>
								<span class="control-value">{Math.round(loadState.extraneous_load * 100)}%</span>
								<button onclick={() => adjustLoad('extraneous', 0.1)}>+</button>
							</div>
						</div>
						<div class="control-row">
							<span class="control-label">Germane (Active Learning)</span>
							<div class="control-buttons">
								<button onclick={() => adjustLoad('germane', -0.1)}>−</button>
								<span class="control-value">{Math.round(loadState.germane_load * 100)}%</span>
								<button onclick={() => adjustLoad('germane', 0.1)}>+</button>
							</div>
						</div>
					</div>
					<div class="scenario-buttons">
						<button class="scenario-btn danger" onclick={simulateOverload}>
							Simulate Overload
						</button>
						<button class="scenario-btn success" onclick={resetToOptimal}>
							Reset to Optimal
						</button>
					</div>
				</div>
			</div>

			<!-- Right: Presets, Audit, Adaptations & Theory -->
			<div class="theory-section">
				<!-- Preset Loader -->
				<PresetLoader
					presets={loadPresets}
					selected={selectedPreset}
					onselect={(p) => applyPreset(p as (typeof loadPresets)[0])}
					title="Load Scenarios"
				/>

				<!-- Audit Panel -->
				<AuditPanel entries={auditEntries} title="Cognitive State Audit" />

				<!-- Active Adaptations -->
				<div class="adaptations-card">
					<h3>Active Adaptations</h3>
					<div class="adaptations-list">
						{#each adaptations as adaptation}
							<div class="adaptation-item" class:active={adaptation.active}>
								<div class="adaptation-trigger">
									<span class="trigger-condition">{adaptation.trigger}</span>
									<span class="trigger-status">{adaptation.active ? 'ACTIVE' : 'standby'}</span>
								</div>
								<div class="adaptation-action">{adaptation.action}</div>
							</div>
						{/each}
					</div>
				</div>

				<!-- Session Timeline -->
				<div class="timeline-card">
					<h3>Session Timeline</h3>
					<div class="timeline">
						{#each timeline as point, i}
							<div class="timeline-point" class:current={i === timeline.length - 1}>
								<div class="point-marker">
									<div
										class="point-load"
										style="height: {point.load * 100}%; background: {point.load > 0.7
											? '#e74c3c'
											: point.load > 0.5
												? '#f39c12'
												: '#2ecc71'}"
									></div>
								</div>
								<div class="point-info">
									<span class="point-time">{point.time}m</span>
									<span class="point-event">{point.event}</span>
								</div>
							</div>
						{/each}
					</div>
				</div>

				<!-- Prosaic Connection -->
				<div class="prosaic-card">
					<h3>🧩 Prosaic Dimension: Cognitive</h3>
					<p>
						This demo shows the <strong>🧩 Cognitive</strong> prosaic dimension in action.
						In real use, you can simply declare "I'm overwhelmed" or "too many options" —
						and AI adapts without needing the detailed breakdown shown here.
					</p>
					<div class="prosaic-example">
						<code>🧩0.8:overwhelmed</code> → Simplify choices, clear recommendations
					</div>
				</div>

				<!-- Cognitive Load Theory -->
				<div class="theory-card">
					<h3>Cognitive Load Theory</h3>
					<div class="load-types">
						<div class="load-type intrinsic">
							<div class="type-header">
								<span class="type-dot"></span>
								<strong>Intrinsic Load</strong>
							</div>
							<p>
								Inherent complexity of the material. Can't be eliminated, but can be managed
								through scaffolding and sequencing.
							</p>
						</div>
						<div class="load-type extraneous">
							<div class="type-header">
								<span class="type-dot"></span>
								<strong>Extraneous Load</strong>
							</div>
							<p>
								Load from poor instructional design. Should be minimized. VCP helps by
								matching presentation to learner preferences.
							</p>
						</div>
						<div class="load-type germane">
							<div class="type-header">
								<span class="type-dot"></span>
								<strong>Germane Load</strong>
							</div>
							<p>
								Load from active learning and schema construction. This is beneficial!
								VCP optimizes for maximizing germane load within capacity.
							</p>
						</div>
					</div>
					<div class="key-insight">
						<strong>VCP Advantage:</strong> By knowing your cognitive state, learning style,
						and current context, AI tutors can dynamically adjust material complexity,
						presentation format, and pacing to keep you in the optimal learning zone.
					</div>
				</div>
			</div>
		</div>
	{/snippet}
</DemoContainer>

<style>
	.load-layout {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--space-xl);
	}

	.meter-section,
	.theory-section {
		display: flex;
		flex-direction: column;
		gap: var(--space-lg);
	}

	.controls-card,
	.adaptations-card,
	.timeline-card,
	.theory-card {
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
	}

	h3 {
		font-size: 1rem;
		margin: 0 0 var(--space-md) 0;
	}

	.control-grid {
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
		margin-bottom: var(--space-lg);
	}

	.control-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.control-label {
		font-size: 0.875rem;
	}

	.control-buttons {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
	}

	.control-buttons button {
		width: 44px;
		height: 44px;
		border: 2px solid rgba(255, 255, 255, 0.5);
		background: var(--color-bg-card);
		border-radius: var(--radius-md);
		cursor: pointer;
		font-size: 1.75rem;
		font-weight: 700;
		color: #ffffff;
		display: flex;
		align-items: center;
		justify-content: center;
		line-height: 1;
		transition: all var(--transition-fast);
	}

	.control-buttons button:hover {
		border-color: var(--color-primary);
		background: var(--color-primary);
		color: #ffffff;
	}

	.control-value {
		font-family: var(--font-mono);
		min-width: 40px;
		text-align: center;
	}

	.scenario-buttons {
		display: flex;
		gap: var(--space-sm);
	}

	.scenario-btn {
		flex: 1;
		padding: var(--space-sm) var(--space-md);
		border: none;
		border-radius: var(--radius-md);
		cursor: pointer;
		font-size: 0.875rem;
		transition: opacity var(--transition-fast);
	}

	.scenario-btn:hover {
		opacity: 0.8;
	}

	.scenario-btn.danger {
		background: var(--color-danger);
		color: white;
	}

	.scenario-btn.success {
		background: var(--color-success);
		color: white;
	}

	.adaptations-list {
		display: flex;
		flex-direction: column;
		gap: var(--space-sm);
	}

	.adaptation-item {
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		border-left: 3px solid var(--color-text-subtle);
		opacity: 0.6;
	}

	.adaptation-item.active {
		border-color: var(--color-warning);
		opacity: 1;
	}

	.adaptation-trigger {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--space-xs);
	}

	.trigger-condition {
		font-family: var(--font-mono);
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.trigger-status {
		font-size: 0.6875rem;
		padding: 2px 6px;
		background: var(--color-bg);
		border-radius: var(--radius-sm);
		text-transform: uppercase;
	}

	.adaptation-item.active .trigger-status {
		background: var(--color-warning-muted);
		color: var(--color-warning);
	}

	.adaptation-action {
		font-size: 0.875rem;
	}

	.timeline {
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
		height: 100px;
		padding: var(--space-md) 0;
	}

	.timeline-point {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-xs);
		flex: 1;
	}

	.point-marker {
		width: 24px;
		height: 60px;
		background: var(--color-bg-elevated);
		border-radius: var(--radius-sm);
		display: flex;
		align-items: flex-end;
		overflow: hidden;
	}

	.point-load {
		width: 100%;
		border-radius: var(--radius-sm);
		transition: height var(--transition-normal);
	}

	.timeline-point.current .point-marker {
		border: 2px solid var(--color-primary);
	}

	.point-info {
		text-align: center;
	}

	.point-time {
		display: block;
		font-family: var(--font-mono);
		font-size: 0.6875rem;
		color: var(--color-text-subtle);
	}

	.point-event {
		display: block;
		font-size: 0.5rem;
		color: var(--color-text-muted);
		max-width: 60px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.load-types {
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
		margin-bottom: var(--space-lg);
	}

	.load-type {
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
	}

	.type-header {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-xs);
	}

	.type-dot {
		width: 12px;
		height: 12px;
		border-radius: 50%;
	}

	.load-type.intrinsic .type-dot {
		background: #3498db;
	}

	.load-type.extraneous .type-dot {
		background: #e74c3c;
	}

	.load-type.germane .type-dot {
		background: #2ecc71;
	}

	.load-type p {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		margin: 0;
	}

	.key-insight {
		padding: var(--space-md);
		background: var(--color-primary-muted);
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
		color: var(--color-success);
	}

	.prosaic-card p {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		margin: 0 0 var(--space-md);
		line-height: 1.5;
	}

	.prosaic-example {
		font-family: var(--font-mono);
		font-size: var(--text-sm);
		padding: var(--space-sm) var(--space-md);
		background: var(--color-bg);
		border-radius: var(--radius-md);
	}

	@media (max-width: 1024px) {
		.load-layout {
			grid-template-columns: 1fr;
		}
	}
</style>
