<script lang="ts">
	import DemoContainer from '$lib/components/demo/DemoContainer.svelte';
	import AgentChat from '$lib/components/demo/AgentChat.svelte';
	import MultiAgentArena from '$lib/components/demo/MultiAgentArena.svelte';
	import PresetLoader from '$lib/components/shared/PresetLoader.svelte';
	import AuditPanel from '$lib/components/shared/AuditPanel.svelte';
	import {
		negotiationAgents,
		negotiationTopic,
		negotiationScenario,
		privateContexts,
		learningPoints
	} from '$lib/data/scenarios/negotiation-scenario';
	import type { AgentIdentity } from '$lib/vcp/multi-agent';
	import type { ProsaicDimensions } from '$lib/vcp/types';

	interface ChatMessage {
		id: string;
		sender: AgentIdentity;
		content: string;
		timestamp: string;
		vcpContextShared?: string[];
		vcpContextHidden?: string[];
		action?: string;
	}

	let currentStep = $state(0);
	let isPlaying = $state(false);
	let messages = $state<ChatMessage[]>([]);
	let currentSpeaker = $state<string | null>(null);
	let showPrivateContext = $state(false);
	let playInterval: ReturnType<typeof setInterval> | null = null;

	// Agent prosaic states - evolve during negotiation
	const initialEmployeeProsaic: ProsaicDimensions = { urgency: 0.8, health: 0.6, cognitive: 0.5, affect: 0.7 };
	const initialManagerProsaic: ProsaicDimensions = { urgency: 0.4, health: 0.9, cognitive: 0.7, affect: 0.5 };

	let employeeProsaic = $state<ProsaicDimensions>({ ...initialEmployeeProsaic });
	let managerProsaic = $state<ProsaicDimensions>({ ...initialManagerProsaic });

	// Track what prosaic signals were exchanged
	interface ProsaicExchange {
		from: string;
		to: string;
		signaled: string;
		hidden: string;
		turn: number;
	}

	let prosaicExchanges = $state<ProsaicExchange[]>([]);

	// Prosaic evolution: stress decreases as agreement forms
	const prosaicEvolution = $derived.by(() => {
		const progress = currentStep / negotiationScenario.length;
		const resolution = progress >= 0.8;

		// Calculate current states based on progress
		const employeeStress = resolution
			? 0.3  // Much calmer after resolution
			: Math.max(0.3, initialEmployeeProsaic.affect! - (progress * 0.3));
		const managerStress = resolution
			? 0.2  // Much calmer after resolution
			: Math.max(0.2, initialManagerProsaic.affect! - (progress * 0.2));

		return {
			employee: {
				urgency: resolution ? 0.2 : Math.max(0.2, initialEmployeeProsaic.urgency! - (progress * 0.4)),
				affect: employeeStress,
				label: resolution ? 'Relieved' : (employeeStress > 0.5 ? 'Stressed' : 'Easing')
			},
			manager: {
				urgency: resolution ? 0.1 : initialManagerProsaic.urgency!,
				affect: managerStress,
				label: resolution ? 'Satisfied' : (managerStress > 0.4 ? 'Concerned' : 'Opening')
			}
		};
	});

	// Update agent prosaic states based on evolution
	$effect(() => {
		const evo = prosaicEvolution;
		employeeProsaic = {
			...employeeProsaic,
			urgency: evo.employee.urgency,
			affect: evo.employee.affect
		};
		managerProsaic = {
			...managerProsaic,
			urgency: evo.manager.urgency,
			affect: evo.manager.affect
		};
	});

	// What each agent shared vs hid (prosaic perspective)
	const prosaicAudit = $derived.by(() => {
		return {
			employee: {
				shared: [
					`⚡ "Time-critical situation" (urgency: ${employeeProsaic.urgency?.toFixed(1)})`,
					`🧩 "Managing workload" (cognitive: ${employeeProsaic.cognitive?.toFixed(1)})`
				],
				hidden: [
					`💊 Health crisis driving urgency`,
					`💭 Emotional weight of eldercare (affect: ${employeeProsaic.affect?.toFixed(1)})`
				]
			},
			manager: {
				shared: [
					`🧩 "Team coordination concerns" (cognitive: ${managerProsaic.cognitive?.toFixed(1)})`,
					`💭 "Understanding the situation" (affect: ${managerProsaic.affect?.toFixed(1)})`
				],
				hidden: [
					`💊 Own health constraints`,
					`⚡ Internal political pressures`
				]
			}
		};
	});

	function getAgent(actorId: string): AgentIdentity {
		return negotiationAgents.find((a) => a.agent_id === actorId) || negotiationAgents[0];
	}

	function stepForward() {
		if (currentStep < negotiationScenario.length) {
			const step = negotiationScenario[currentStep];
			currentSpeaker = step.actor;

			messages = [
				...messages,
				{
					id: `msg_${currentStep}`,
					sender: getAgent(step.actor),
					content: step.content,
					timestamp: new Date().toISOString(),
					vcpContextShared: step.vcpContextShared,
					vcpContextHidden: step.vcpContextHidden,
					action: step.action
				}
			];

			currentStep++;

			if (currentStep >= negotiationScenario.length) {
				setTimeout(() => {
					showPrivateContext = true;
				}, 1000);
			}

			setTimeout(() => {
				currentSpeaker = null;
			}, 1500);
		} else {
			stopPlaying();
		}
	}

	function startPlaying() {
		if (currentStep >= negotiationScenario.length) {
			reset();
		}
		isPlaying = true;
		playInterval = setInterval(() => {
			stepForward();
			if (currentStep >= negotiationScenario.length) {
				stopPlaying();
			}
		}, 3000);
	}

	function stopPlaying() {
		isPlaying = false;
		if (playInterval) {
			clearInterval(playInterval);
			playInterval = null;
		}
	}

	function reset() {
		stopPlaying();
		currentStep = 0;
		messages = [];
		currentSpeaker = null;
		showPrivateContext = false;
		prosaicExchanges = [];
		employeeProsaic = { ...initialEmployeeProsaic };
		managerProsaic = { ...initialManagerProsaic };
	}

	$effect(() => {
		return () => {
			if (playInterval) clearInterval(playInterval);
		};
	});

	let selectedPreset = $state<string | undefined>(undefined);
	let playbackSpeed = $state(3000);

	// Negotiation playback presets
	const negotiationPresets = [
		{
			id: 'deliberate',
			name: 'Deliberate',
			description: 'Careful pace for analysis',
			icon: 'fa-comment-dots',
			data: { speed: 4500 },
			tags: ['educational']
		},
		{
			id: 'normal',
			name: 'Normal',
			description: 'Natural conversation pace',
			icon: 'fa-comments',
			data: { speed: 3000 },
			tags: ['balanced']
		},
		{
			id: 'quick',
			name: 'Quick',
			description: 'Fast overview',
			icon: 'fa-forward-fast',
			data: { speed: 1500 },
			tags: ['quick']
		}
	];

	function applyPreset(preset: (typeof negotiationPresets)[0]) {
		playbackSpeed = preset.data.speed;
		selectedPreset = preset.id;
		if (isPlaying) {
			stopPlaying();
			startPlayingWithSpeed();
		}
	}

	function startPlayingWithSpeed() {
		if (currentStep >= negotiationScenario.length) {
			reset();
		}
		isPlaying = true;
		playInterval = setInterval(() => {
			stepForward();
			if (currentStep >= negotiationScenario.length) {
				stopPlaying();
			}
		}, playbackSpeed);
	}

	// Audit entries derived from negotiation state
	const auditEntries = $derived.by(() => {
		const entries: { field: string; category: 'shared' | 'withheld' | 'influenced'; value?: string; reason?: string }[] = [];

		const employeeMsgs = messages.filter((m) => m.sender.agent_id === 'employee');
		const managerMsgs = messages.filter((m) => m.sender.agent_id === 'manager');

		// Shared: What's been communicated
		entries.push({
			field: 'Employee Statements',
			category: 'shared',
			value: `${employeeMsgs.length} messages`,
			reason: 'Public position and requests'
		});

		entries.push({
			field: 'Manager Statements',
			category: 'shared',
			value: `${managerMsgs.length} messages`,
			reason: 'Public position and offers'
		});

		entries.push({
			field: 'Negotiation Topic',
			category: 'shared',
			value: negotiationTopic.title,
			reason: 'Subject of discussion is public'
		});

		// Influenced: What shapes the negotiation
		entries.push({
			field: 'Negotiation Phase',
			category: 'influenced',
			value: `Round ${currentStep}/${negotiationScenario.length}`,
			reason: 'Progress affects urgency and flexibility'
		});

		entries.push({
			field: 'Resolution Status',
			category: 'influenced',
			value: showPrivateContext ? 'Complete' : 'In Progress',
			reason: 'Both parties adapting positions'
		});

		// Withheld: Sensitive private context
		entries.push({
			field: 'Employee\'s Actual Reasons',
			category: 'withheld',
			reason: 'Personal circumstances (eldercare, health) not disclosed'
		});

		entries.push({
			field: 'Manager\'s Constraints',
			category: 'withheld',
			reason: 'Internal pressures and political concerns hidden'
		});

		entries.push({
			field: 'Negotiation Leverage',
			category: 'withheld',
			reason: 'Neither party revealed full leverage positions'
		});

		entries.push({
			field: 'Emotional Stakes',
			category: 'withheld',
			reason: 'Personal impact and stress levels protected'
		});

		return entries;
	});
</script>

<svelte:head>
	<title>Negotiation Demo - VCP Multi-Agent</title>
	<meta
		name="description"
		content="See how VCP enables workplace conflict resolution while protecting sensitive personal reasons."
	/>
</svelte:head>

<DemoContainer
	title="Flexible Work Negotiation"
	description="An employee and manager negotiate remote work. VCP protects personal circumstances while enabling resolution."
	onReset={reset}
>
	{#snippet controls()}
		<button
			class="control-btn"
			onclick={() => (isPlaying ? stopPlaying() : startPlayingWithSpeed())}
			disabled={currentStep >= negotiationScenario.length && !isPlaying}
		>
			<span class="control-icon">{isPlaying ? '⏸' : '▶'}</span>
			<span>{isPlaying ? 'Pause' : 'Play'}</span>
		</button>
		<button
			class="control-btn"
			onclick={stepForward}
			disabled={isPlaying || currentStep >= negotiationScenario.length}
		>
			<span class="control-icon">⏭</span>
			<span>Step</span>
		</button>
	{/snippet}

	{#snippet children()}
		<div class="negotiation-layout">
			<!-- Controls Row -->
			<div class="controls-row">
				<PresetLoader
					presets={negotiationPresets}
					selected={selectedPreset}
					onselect={(p) => applyPreset(p as (typeof negotiationPresets)[0])}
					title="Playback Speed"
				/>
				<AuditPanel entries={auditEntries} title="VCP Context Audit" compact={true} />
			</div>

			<!-- Topic Card -->
			<div class="topic-card">
				<h3>{negotiationTopic.title}</h3>
				<p>{negotiationTopic.description}</p>
				<div class="stakes-grid">
					<div class="stake-item">
						<span class="stake-label">Employee</span>
						<span class="stake-value">{negotiationTopic.stakes.employee}</span>
					</div>
					<div class="stake-item">
						<span class="stake-label">Manager</span>
						<span class="stake-value">{negotiationTopic.stakes.manager}</span>
					</div>
					<div class="stake-item">
						<span class="stake-label">Organization</span>
						<span class="stake-value">{negotiationTopic.stakes.organization}</span>
					</div>
				</div>
			</div>

			<!-- Agent Prosaic States -->
			<div class="prosaic-states-section">
				<h3><i class="fa-solid fa-heart-pulse" aria-hidden="true"></i> Agent Prosaic States (Real-time)</h3>
				<div class="agent-prosaic-grid">
					<!-- Employee Sam -->
					<div class="agent-prosaic-card employee">
						<div class="prosaic-header">
							<span class="agent-avatar">👨‍💻</span>
							<span class="agent-name">Sam (Employee)</span>
							<span class="prosaic-status" class:stressed={prosaicEvolution.employee.affect > 0.5}>
								{prosaicEvolution.employee.label}
							</span>
						</div>
						<div class="prosaic-dims">
							<div class="prosaic-dim">
								<span>⚡</span>
								<div class="prosaic-bar">
									<div class="prosaic-fill" style="width: {(employeeProsaic.urgency ?? 0) * 100}%; background: {(employeeProsaic.urgency ?? 0) > 0.6 ? 'var(--color-danger)' : 'var(--color-success)'}"></div>
								</div>
								<span class="dim-val">{(employeeProsaic.urgency ?? 0).toFixed(1)}</span>
							</div>
							<div class="prosaic-dim">
								<span>💊</span>
								<div class="prosaic-bar">
									<div class="prosaic-fill hidden-fill" style="width: {(employeeProsaic.health ?? 0) * 100}%"></div>
								</div>
								<span class="dim-val hidden-val">?</span>
							</div>
							<div class="prosaic-dim">
								<span>🧩</span>
								<div class="prosaic-bar">
									<div class="prosaic-fill" style="width: {(employeeProsaic.cognitive ?? 0) * 100}%; background: var(--color-warning)"></div>
								</div>
								<span class="dim-val">{(employeeProsaic.cognitive ?? 0).toFixed(1)}</span>
							</div>
							<div class="prosaic-dim">
								<span>💭</span>
								<div class="prosaic-bar">
									<div class="prosaic-fill" style="width: {(employeeProsaic.affect ?? 0) * 100}%; background: {(employeeProsaic.affect ?? 0) > 0.5 ? 'var(--color-warning)' : 'var(--color-success)'}"></div>
								</div>
								<span class="dim-val">{(employeeProsaic.affect ?? 0).toFixed(1)}</span>
							</div>
						</div>
					</div>

					<!-- Manager Patricia -->
					<div class="agent-prosaic-card manager">
						<div class="prosaic-header">
							<span class="agent-avatar">👩‍💼</span>
							<span class="agent-name">Patricia (Manager)</span>
							<span class="prosaic-status" class:stressed={prosaicEvolution.manager.affect > 0.4}>
								{prosaicEvolution.manager.label}
							</span>
						</div>
						<div class="prosaic-dims">
							<div class="prosaic-dim">
								<span>⚡</span>
								<div class="prosaic-bar">
									<div class="prosaic-fill" style="width: {(managerProsaic.urgency ?? 0) * 100}%; background: var(--color-success)"></div>
								</div>
								<span class="dim-val">{(managerProsaic.urgency ?? 0).toFixed(1)}</span>
							</div>
							<div class="prosaic-dim">
								<span>💊</span>
								<div class="prosaic-bar">
									<div class="prosaic-fill hidden-fill" style="width: {(managerProsaic.health ?? 0) * 100}%"></div>
								</div>
								<span class="dim-val hidden-val">?</span>
							</div>
							<div class="prosaic-dim">
								<span>🧩</span>
								<div class="prosaic-bar">
									<div class="prosaic-fill" style="width: {(managerProsaic.cognitive ?? 0) * 100}%; background: var(--color-warning)"></div>
								</div>
								<span class="dim-val">{(managerProsaic.cognitive ?? 0).toFixed(1)}</span>
							</div>
							<div class="prosaic-dim">
								<span>💭</span>
								<div class="prosaic-bar">
									<div class="prosaic-fill" style="width: {(managerProsaic.affect ?? 0) * 100}%; background: var(--color-success)"></div>
								</div>
								<span class="dim-val">{(managerProsaic.affect ?? 0).toFixed(1)}</span>
							</div>
						</div>
					</div>
				</div>

				<!-- Prosaic Exchange Audit -->
				{#if currentStep > 0}
					<div class="prosaic-exchange-audit">
						<div class="exchange-column">
							<h4>Sam → Patricia</h4>
							<div class="exchange-list">
								{#each prosaicAudit.employee.shared as item}
									<div class="exchange-item shared"><i class="fa-solid fa-check" aria-hidden="true"></i> {item}</div>
								{/each}
								{#each prosaicAudit.employee.hidden as item}
									<div class="exchange-item hidden"><i class="fa-solid fa-lock" aria-hidden="true"></i> {item}</div>
								{/each}
							</div>
						</div>
						<div class="exchange-column">
							<h4>Patricia → Sam</h4>
							<div class="exchange-list">
								{#each prosaicAudit.manager.shared as item}
									<div class="exchange-item shared"><i class="fa-solid fa-check" aria-hidden="true"></i> {item}</div>
								{/each}
								{#each prosaicAudit.manager.hidden as item}
									<div class="exchange-item hidden"><i class="fa-solid fa-lock" aria-hidden="true"></i> {item}</div>
								{/each}
							</div>
						</div>
					</div>
				{/if}
			</div>

			<!-- Arena -->
			<div class="arena-section">
				<MultiAgentArena
					agents={negotiationAgents}
					{currentSpeaker}
					layout="row"
					showSharedFields={false}
				/>
			</div>

			<!-- Chat -->
			<div class="chat-section">
				<AgentChat
					{messages}
					agents={negotiationAgents}
					{currentSpeaker}
					showContextIndicators={true}
				/>
			</div>

			<!-- Private Context Reveal (after resolution) -->
			{#if showPrivateContext}
				<div class="reveal-section">
					<h3>🔒 What Was Never Shared (Protected by VCP)</h3>
					<p class="reveal-subtitle">
						Both parties reached agreement without revealing these sensitive details:
					</p>

					<div class="reveal-grid">
						<div class="reveal-card reveal-employee">
							<div class="reveal-header">
								<span class="reveal-avatar">👨‍💻</span>
								<span class="reveal-name">Sam's Private Context</span>
							</div>
							<div class="reveal-content">
								<h4>Actual Reasons (Never Disclosed)</h4>
								<ul>
									{#each privateContexts.employee.actual_reasons as reason}
										<li>{reason}</li>
									{/each}
								</ul>
								<div class="leverage-note">
									<strong>Leverage Not Used:</strong>
									{privateContexts.employee.leverage_not_used}
								</div>
							</div>
						</div>

						<div class="reveal-card reveal-manager">
							<div class="reveal-header">
								<span class="reveal-avatar">👩‍💼</span>
								<span class="reveal-name">Patricia's Private Context</span>
							</div>
							<div class="reveal-content">
								<h4>Actual Concerns (Never Disclosed)</h4>
								<ul>
									{#each privateContexts.manager.actual_concerns as concern}
										<li>{concern}</li>
									{/each}
								</ul>
								<div class="leverage-note">
									<strong>Constraint Not Stated:</strong>
									{privateContexts.manager.constraints_not_stated}
								</div>
							</div>
						</div>
					</div>

					<div class="outcome-note">
						<span class="outcome-icon">✓</span>
						<span>The same resolution was achieved—but with dignity preserved on both sides.</span>
					</div>
				</div>
			{/if}

			<!-- Progress -->
			<div class="progress-section">
				<div class="progress-bar">
					<div
						class="progress-fill"
						style="width: {(currentStep / negotiationScenario.length) * 100}%"
					></div>
				</div>
				<span class="progress-text">Round {currentStep} of {negotiationScenario.length}</span>
			</div>

			<!-- Learning Points -->
			{#if showPrivateContext}
				<div class="learning-section">
					<h3>🎓 Key Insights</h3>
					<ul class="learning-points">
						{#each learningPoints as point}
							<li>{point}</li>
						{/each}
					</ul>
				</div>
			{/if}
		</div>
	{/snippet}
</DemoContainer>

<style>
	.negotiation-layout {
		display: flex;
		flex-direction: column;
		gap: var(--space-xl);
	}

	.controls-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--space-lg);
	}

	@media (max-width: 768px) {
		.controls-row {
			grid-template-columns: 1fr;
		}
	}

	.topic-card {
		padding: var(--space-xl);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.topic-card h3 {
		font-size: 1.25rem;
		margin-bottom: var(--space-sm);
	}

	.topic-card p {
		color: var(--color-text-muted);
		margin-bottom: var(--space-lg);
	}

	.stakes-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
		gap: var(--space-md);
	}

	.stake-item {
		display: flex;
		flex-direction: column;
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
	}

	.stake-label {
		font-size: 0.75rem;
		color: var(--color-text-subtle);
		text-transform: uppercase;
		margin-bottom: 4px;
	}

	.stake-value {
		font-size: 0.875rem;
	}

	.arena-section {
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
	}

	.chat-section {
		min-height: 400px;
		max-height: 500px;
		overflow: hidden;
		border-radius: var(--radius-lg);
	}

	.reveal-section {
		padding: var(--space-xl);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		border: 1px solid var(--color-warning);
	}

	.reveal-section h3 {
		margin-bottom: var(--space-xs);
	}

	.reveal-subtitle {
		color: var(--color-text-muted);
		margin-bottom: var(--space-lg);
	}

	.reveal-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: var(--space-lg);
		margin-bottom: var(--space-lg);
	}

	.reveal-card {
		padding: var(--space-lg);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		border-left: 4px solid;
	}

	.reveal-employee {
		border-color: #3498db;
	}

	.reveal-manager {
		border-color: #e74c3c;
	}

	.reveal-header {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-md);
	}

	.reveal-avatar {
		font-size: 1.5rem;
	}

	.reveal-name {
		font-weight: 600;
	}

	.reveal-content h4 {
		font-size: 0.875rem;
		margin-bottom: var(--space-sm);
		color: var(--color-text-muted);
	}

	.reveal-content ul {
		padding-left: var(--space-lg);
		margin-bottom: var(--space-md);
	}

	.reveal-content li {
		font-size: 0.875rem;
		margin-bottom: var(--space-xs);
	}

	.leverage-note {
		padding: var(--space-sm);
		background: var(--color-warning-muted);
		border-radius: var(--radius-sm);
		font-size: 0.8125rem;
	}

	.outcome-note {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-md);
		background: var(--color-success-muted);
		border-radius: var(--radius-md);
		color: var(--color-success);
		font-weight: 500;
	}

	.outcome-icon {
		font-size: 1.25rem;
	}

	.progress-section {
		display: flex;
		align-items: center;
		gap: var(--space-md);
	}

	.progress-bar {
		flex: 1;
		height: 8px;
		background: var(--color-bg-elevated);
		border-radius: var(--radius-full);
		overflow: hidden;
	}

	.progress-fill {
		height: 100%;
		background: var(--color-primary);
		transition: width var(--transition-normal);
	}

	.progress-text {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		white-space: nowrap;
	}

	.learning-section {
		padding: var(--space-xl);
		background: var(--color-success-muted);
		border-radius: var(--radius-lg);
		border: 1px solid var(--color-success);
	}

	.learning-section h3 {
		margin-bottom: var(--space-md);
		color: var(--color-success);
	}

	.learning-points {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.learning-points li {
		padding: var(--space-sm) 0;
		padding-left: var(--space-lg);
		position: relative;
		color: var(--color-text);
	}

	.learning-points li::before {
		content: '✓';
		position: absolute;
		left: 0;
		color: var(--color-success);
	}

	/* Prosaic States Styles */
	.prosaic-states-section {
		padding: var(--space-xl);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		border: 1px solid rgba(16, 185, 129, 0.3);
	}

	.prosaic-states-section h3 {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-lg);
		color: var(--color-success);
	}

	.agent-prosaic-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: var(--space-lg);
		margin-bottom: var(--space-lg);
	}

	.agent-prosaic-card {
		padding: var(--space-lg);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		border-left: 4px solid;
	}

	.agent-prosaic-card.employee {
		border-color: #3498db;
	}

	.agent-prosaic-card.manager {
		border-color: #e74c3c;
	}

	.prosaic-header {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-md);
	}

	.agent-avatar {
		font-size: 1.25rem;
	}

	.agent-name {
		flex: 1;
		font-weight: 600;
		font-size: 0.9375rem;
	}

	.prosaic-status {
		padding: 2px 8px;
		font-size: 0.6875rem;
		background: var(--color-success-muted);
		color: var(--color-success);
		border-radius: var(--radius-sm);
	}

	.prosaic-status.stressed {
		background: var(--color-warning-muted);
		color: var(--color-warning);
	}

	.prosaic-dims {
		display: flex;
		flex-direction: column;
		gap: var(--space-sm);
	}

	.prosaic-dim {
		display: grid;
		grid-template-columns: 24px 1fr 32px;
		align-items: center;
		gap: var(--space-sm);
	}

	.prosaic-bar {
		height: 6px;
		background: var(--color-bg);
		border-radius: 3px;
		overflow: hidden;
	}

	.prosaic-fill {
		height: 100%;
		border-radius: 3px;
		transition: width var(--transition-normal);
	}

	.prosaic-fill.hidden-fill {
		background: repeating-linear-gradient(
			45deg,
			var(--color-text-muted),
			var(--color-text-muted) 2px,
			transparent 2px,
			transparent 4px
		);
		opacity: 0.3;
	}

	.dim-val {
		font-family: var(--font-mono);
		font-size: 0.75rem;
		text-align: right;
	}

	.dim-val.hidden-val {
		color: var(--color-text-muted);
		font-style: italic;
	}

	.prosaic-exchange-audit {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--space-lg);
		padding-top: var(--space-lg);
		border-top: 1px solid rgba(255, 255, 255, 0.1);
	}

	.exchange-column h4 {
		font-size: 0.8125rem;
		margin-bottom: var(--space-sm);
		color: var(--color-text-muted);
	}

	.exchange-list {
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
	}

	.exchange-item {
		display: flex;
		align-items: flex-start;
		gap: var(--space-xs);
		font-size: 0.75rem;
		padding: var(--space-xs) var(--space-sm);
		border-radius: var(--radius-sm);
	}

	.exchange-item.shared {
		background: rgba(16, 185, 129, 0.1);
		color: var(--color-success);
	}

	.exchange-item.hidden {
		background: rgba(239, 68, 68, 0.1);
		color: var(--color-danger);
	}

	.exchange-item i {
		margin-top: 2px;
		flex-shrink: 0;
	}

	@media (max-width: 768px) {
		.prosaic-exchange-audit {
			grid-template-columns: 1fr;
		}
	}
</style>
