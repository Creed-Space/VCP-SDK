<script lang="ts">
	import DemoContainer from '$lib/components/demo/DemoContainer.svelte';
	import AgentChat from '$lib/components/demo/AgentChat.svelte';
	import MultiAgentArena from '$lib/components/demo/MultiAgentArena.svelte';
	import PresetLoader from '$lib/components/shared/PresetLoader.svelte';
	import AuditPanel from '$lib/components/shared/AuditPanel.svelte';
	import {
		policyAgents,
		policyOptions,
		policyScenario,
		learningPoints,
		finalVotes
	} from '$lib/data/scenarios/policy-scenario';
	import type { AgentIdentity } from '$lib/vcp/multi-agent';

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
	let showVotes = $state(false);
	let playInterval: ReturnType<typeof setInterval> | null = null;

	function getAgent(actorId: string): AgentIdentity {
		return policyAgents.find((a) => a.agent_id === actorId) || policyAgents[0];
	}

	function stepForward() {
		if (currentStep < policyScenario.length) {
			const step = policyScenario[currentStep];
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

			if (currentStep >= policyScenario.length) {
				setTimeout(() => {
					showVotes = true;
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
		if (currentStep >= policyScenario.length) {
			reset();
		}
		isPlaying = true;
		playInterval = setInterval(() => {
			stepForward();
			if (currentStep >= policyScenario.length) {
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
		showVotes = false;
	}

	$effect(() => {
		return () => {
			if (playInterval) clearInterval(playInterval);
		};
	});

	let selectedPreset = $state<string | undefined>(undefined);
	let playbackSpeed = $state(3000);

	// Policy design playback presets
	const policyPresets = [
		{
			id: 'careful',
			name: 'Careful',
			description: 'Thoughtful deliberation pace',
			icon: 'fa-scale-balanced',
			data: { speed: 4500 },
			tags: ['educational']
		},
		{
			id: 'normal',
			name: 'Normal',
			description: 'Standard deliberation pace',
			icon: 'fa-play',
			data: { speed: 3000 },
			tags: ['balanced']
		},
		{
			id: 'fast',
			name: 'Fast',
			description: 'Quick policy overview',
			icon: 'fa-forward',
			data: { speed: 1500 },
			tags: ['quick']
		}
	];

	function applyPreset(preset: (typeof policyPresets)[0]) {
		playbackSpeed = preset.data.speed;
		selectedPreset = preset.id;
		if (isPlaying) {
			stopPlaying();
			startPlayingWithSpeed();
		}
	}

	function startPlayingWithSpeed() {
		if (currentStep >= policyScenario.length) {
			reset();
		}
		isPlaying = true;
		playInterval = setInterval(() => {
			stepForward();
			if (currentStep >= policyScenario.length) {
				stopPlaying();
			}
		}, playbackSpeed);
	}

	// Audit entries derived from policy state
	const auditEntries = $derived.by(() => {
		const entries: { field: string; category: 'shared' | 'withheld' | 'influenced'; value?: string; reason?: string }[] = [];

		// Count contributions by stakeholder
		const contributionCounts = policyAgents.reduce(
			(acc, agent) => {
				acc[agent.agent_id] = messages.filter((m) => m.sender.agent_id === agent.agent_id).length;
				return acc;
			},
			{} as Record<string, number>
		);

		// Shared: Public deliberation elements
		entries.push({
			field: 'Policy Options',
			category: 'shared',
			value: `${policyOptions.length} proposals`,
			reason: 'All options publicly presented'
		});

		entries.push({
			field: 'Stakeholder Input',
			category: 'shared',
			value: `${messages.length} statements`,
			reason: 'Public positions and arguments'
		});

		entries.push({
			field: 'Value Alignments',
			category: 'shared',
			reason: 'Which values each proposal serves'
		});

		// Influenced: What shapes decisions
		entries.push({
			field: 'Deliberation Phase',
			category: 'influenced',
			value: `Step ${currentStep}/${policyScenario.length}`,
			reason: 'Progress affects consensus building'
		});

		entries.push({
			field: 'Participation Balance',
			category: 'influenced',
			value: Object.values(contributionCounts).join('/') + ' msgs',
			reason: 'Equal voice opportunity monitored'
		});

		entries.push({
			field: 'Consensus Status',
			category: 'influenced',
			value: showVotes ? 'Achieved' : 'Building',
			reason: 'Positions converging through dialogue'
		});

		// Withheld: Private rationales
		entries.push({
			field: 'Personal Circumstances',
			category: 'withheld',
			reason: 'Individual life situations protected'
		});

		entries.push({
			field: 'Private Rationales',
			category: 'withheld',
			reason: 'Personal reasons for votes never disclosed'
		});

		entries.push({
			field: 'Political Considerations',
			category: 'withheld',
			reason: 'Career/reputation concerns hidden'
		});

		entries.push({
			field: 'Emotional Stakes',
			category: 'withheld',
			reason: 'Personal investment in outcomes protected'
		});

		return entries;
	});
</script>

<svelte:head>
	<title>Policy Design Demo - VCP Multi-Agent</title>
	<meta
		name="description"
		content="See how VCP enables preference aggregation while protecting private rationales."
	/>
</svelte:head>

<DemoContainer
	title="Community Park Renovation"
	description="Four stakeholders deliberate on how to spend $150k. VCP shares values while protecting personal circumstances."
	onReset={reset}
>
	{#snippet controls()}
		<button
			class="control-btn"
			onclick={() => (isPlaying ? stopPlaying() : startPlayingWithSpeed())}
			disabled={currentStep >= policyScenario.length && !isPlaying}
		>
			<span class="control-icon">{isPlaying ? '⏸' : '▶'}</span>
			<span>{isPlaying ? 'Pause' : 'Play'}</span>
		</button>
		<button
			class="control-btn"
			onclick={stepForward}
			disabled={isPlaying || currentStep >= policyScenario.length}
		>
			<span class="control-icon">⏭</span>
			<span>Step</span>
		</button>
	{/snippet}

	{#snippet children()}
		<div class="policy-layout">
			<!-- Controls Row -->
			<div class="controls-row">
				<PresetLoader
					presets={policyPresets}
					selected={selectedPreset}
					onselect={(p) => applyPreset(p as (typeof policyPresets)[0])}
					title="Deliberation Pace"
				/>
				<AuditPanel entries={auditEntries} title="VCP Context Audit" compact={true} />
			</div>

			<!-- Options Overview -->
			<div class="options-grid">
				{#each policyOptions as option}
					<div class="option-card">
						<h4>{option.name}</h4>
						<p class="option-desc">{option.description}</p>
						<div class="option-proposer">
							Proposed by {policyAgents.find((a) => a.agent_id === option.proposer)?.display_name}
						</div>
						<div class="option-values">
							{#each option.vcp_aligned_with as value}
								<span class="value-chip">{value.replace(/_/g, ' ')}</span>
							{/each}
						</div>
					</div>
				{/each}
			</div>

			<!-- Arena -->
			<div class="arena-section">
				<MultiAgentArena
					agents={policyAgents}
					{currentSpeaker}
					layout="row"
					showSharedFields={false}
				/>
			</div>

			<!-- Chat -->
			<div class="chat-section">
				<AgentChat {messages} agents={policyAgents} {currentSpeaker} showContextIndicators={true} />
			</div>

			<!-- Votes (shown after deliberation) -->
			{#if showVotes}
				<div class="votes-section">
					<h3>🗳️ Final Vote: Integrated Park Design</h3>
					<p class="vote-subtitle">Unanimous approval achieved through deliberation</p>
					<div class="votes-grid">
						{#each finalVotes as vote}
							{@const agent = policyAgents.find((a) => a.agent_id === vote.voter)}
							<div class="vote-card">
								<div class="vote-header">
									<span class="vote-avatar">{agent?.avatar}</span>
									<span class="vote-name" style="color: {agent?.color}">{agent?.display_name}</span>
									<span class="vote-icon">✓</span>
								</div>
								<div class="vote-public">
									<span class="vote-label">Public Rationale</span>
									<p>{vote.public_rationale}</p>
								</div>
								<div class="vote-private">
									<span class="vote-label">🔒 Private (never shared)</span>
									<p>{vote.private_rationale}</p>
								</div>
							</div>
						{/each}
					</div>
				</div>
			{/if}

			<!-- Progress -->
			<div class="progress-section">
				<div class="progress-bar">
					<div
						class="progress-fill"
						style="width: {(currentStep / policyScenario.length) * 100}%"
					></div>
				</div>
				<span class="progress-text">Step {currentStep} of {policyScenario.length}</span>
			</div>

			<!-- Learning Points -->
			{#if showVotes}
				<div class="learning-section">
					<h3>🎓 What VCP Protected</h3>
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
	.policy-layout {
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

	.options-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
		gap: var(--space-md);
	}

	.option-card {
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.option-card h4 {
		font-size: 1rem;
		margin-bottom: var(--space-xs);
	}

	.option-desc {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		margin-bottom: var(--space-sm);
		line-height: 1.4;
	}

	.option-proposer {
		font-size: 0.75rem;
		color: var(--color-text-subtle);
		margin-bottom: var(--space-sm);
	}

	.option-values {
		display: flex;
		flex-wrap: wrap;
		gap: 4px;
	}

	.value-chip {
		font-size: 0.625rem;
		padding: 2px 6px;
		background: var(--color-primary-muted);
		color: var(--color-primary);
		border-radius: var(--radius-sm);
		text-transform: capitalize;
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

	.votes-section {
		padding: var(--space-xl);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		border: 1px solid var(--color-primary);
	}

	.votes-section h3 {
		margin-bottom: var(--space-xs);
	}

	.vote-subtitle {
		color: var(--color-text-muted);
		margin-bottom: var(--space-lg);
	}

	.votes-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: var(--space-md);
	}

	.vote-card {
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
	}

	.vote-header {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-md);
	}

	.vote-avatar {
		font-size: 1.5rem;
	}

	.vote-name {
		font-weight: 600;
		flex: 1;
	}

	.vote-icon {
		color: var(--color-success);
		font-size: 1.25rem;
	}

	.vote-public,
	.vote-private {
		margin-bottom: var(--space-sm);
	}

	.vote-label {
		display: block;
		font-size: 0.6875rem;
		text-transform: uppercase;
		color: var(--color-text-subtle);
		margin-bottom: 4px;
	}

	.vote-public p,
	.vote-private p {
		font-size: 0.875rem;
		margin: 0;
	}

	.vote-private {
		padding: var(--space-sm);
		background: var(--color-warning-muted);
		border-radius: var(--radius-sm);
		border-left: 3px solid var(--color-warning);
	}

	.vote-private p {
		color: var(--color-text-muted);
		font-style: italic;
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
</style>
