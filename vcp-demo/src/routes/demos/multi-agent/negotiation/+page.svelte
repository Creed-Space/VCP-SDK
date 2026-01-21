<script lang="ts">
	import DemoContainer from '$lib/components/demo/DemoContainer.svelte';
	import AgentChat from '$lib/components/demo/AgentChat.svelte';
	import MultiAgentArena from '$lib/components/demo/MultiAgentArena.svelte';
	import {
		negotiationAgents,
		negotiationTopic,
		negotiationScenario,
		privateContexts,
		learningPoints
	} from '$lib/data/scenarios/negotiation-scenario';
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
	let showPrivateContext = $state(false);
	let playInterval: ReturnType<typeof setInterval> | null = null;

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
	}

	$effect(() => {
		return () => {
			if (playInterval) clearInterval(playInterval);
		};
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
			onclick={() => (isPlaying ? stopPlaying() : startPlaying())}
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
</style>
