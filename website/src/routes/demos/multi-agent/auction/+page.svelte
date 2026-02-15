<script lang="ts">
	import DemoContainer from '$lib/components/demo/DemoContainer.svelte';
	import AgentChat from '$lib/components/demo/AgentChat.svelte';
	import MultiAgentArena from '$lib/components/demo/MultiAgentArena.svelte';
	import PresetLoader from '$lib/components/shared/PresetLoader.svelte';
	import AuditPanel from '$lib/components/shared/AuditPanel.svelte';
	import {
		auctionAgents,
		auctionItem,
		auctionScenario,
		learningPoints,
		createInitialAuctionState
	} from '$lib/data/scenarios/auction-scenario';
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
	let playInterval: ReturnType<typeof setInterval> | null = null;

	function getAgent(actorId: string): AgentIdentity {
		return auctionAgents.find((a) => a.agent_id === actorId) || auctionAgents[0];
	}

	function stepForward() {
		if (currentStep < auctionScenario.length) {
			const step = auctionScenario[currentStep];
			currentSpeaker = step.actor;

			messages = [
				...messages,
				{
					id: `msg_${currentStep}`,
					sender: getAgent(step.actor),
					content: step.message,
					timestamp: new Date().toISOString(),
					vcpContextShared: step.vcpContextShared,
					vcpContextHidden: step.vcpContextHidden,
					action: step.action
				}
			];

			currentStep++;

			// Clear speaker after a moment
			setTimeout(() => {
				currentSpeaker = null;
			}, 1500);
		} else {
			stopPlaying();
		}
	}

	function startPlaying() {
		if (currentStep >= auctionScenario.length) {
			reset();
		}
		isPlaying = true;
		playInterval = setInterval(() => {
			stepForward();
			if (currentStep >= auctionScenario.length) {
				stopPlaying();
			}
		}, 2500);
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
	}

	$effect(() => {
		return () => {
			if (playInterval) clearInterval(playInterval);
		};
	});

	let selectedPreset = $state<string | undefined>(undefined);

	// Playback speed presets
	const auctionPresets = [
		{
			id: 'slow',
			name: 'Slow',
			description: 'Careful analysis of each bid',
			icon: 'fa-clock',
			data: { speed: 4000 },
			tags: ['educational']
		},
		{
			id: 'normal',
			name: 'Normal',
			description: 'Standard auction pace',
			icon: 'fa-play',
			data: { speed: 2500 },
			tags: ['balanced']
		},
		{
			id: 'fast',
			name: 'Fast',
			description: 'Quick overview of auction',
			icon: 'fa-forward-fast',
			data: { speed: 1200 },
			tags: ['quick']
		}
	];

	let playbackSpeed = $state(2500);

	function applyPreset(preset: (typeof auctionPresets)[0]) {
		playbackSpeed = preset.data.speed;
		selectedPreset = preset.id;
		// If playing, restart with new speed
		if (isPlaying) {
			stopPlaying();
			startPlaying();
		}
	}

	// Override startPlaying to use playbackSpeed
	function startPlayingWithSpeed() {
		if (currentStep >= auctionScenario.length) {
			reset();
		}
		isPlaying = true;
		playInterval = setInterval(() => {
			stepForward();
			if (currentStep >= auctionScenario.length) {
				stopPlaying();
			}
		}, playbackSpeed);
	}

	// Audit entries derived from current state
	const auditEntries = $derived.by(() => {
		const entries: { field: string; category: 'shared' | 'withheld' | 'influenced'; value?: string; reason?: string }[] = [];

		// Count what's been shared vs hidden
		const sharedCount = messages.filter((m) => m.vcpContextShared && m.vcpContextShared.length > 0).length;
		const hiddenCount = messages.filter((m) => m.vcpContextHidden && m.vcpContextHidden.length > 0).length;
		const bidCount = messages.filter((m) => m.action === 'bid').length;

		// Shared fields
		entries.push({
			field: 'Public Bids',
			category: 'shared',
			value: `${bidCount} bids made`,
			reason: 'All bids are publicly announced'
		});

		entries.push({
			field: 'Agent Identities',
			category: 'shared',
			value: `${auctionAgents.length} participants`,
			reason: 'Names and roles are public'
		});

		// Influenced fields
		entries.push({
			field: 'Bidding Strategy',
			category: 'influenced',
			value: `Round ${currentStep}/${auctionScenario.length}`,
			reason: 'Strategy adapts to competitive pressure'
		});

		if (sharedCount > 0) {
			entries.push({
				field: 'Context Signals',
				category: 'influenced',
				value: `${sharedCount} shared`,
				reason: 'Selective signals influence perception'
			});
		}

		// Withheld fields
		entries.push({
			field: 'Maximum Valuations',
			category: 'withheld',
			reason: 'Private ceiling never revealed'
		});

		entries.push({
			field: 'Bidding Algorithms',
			category: 'withheld',
			reason: 'Strategic logic stays hidden'
		});

		if (hiddenCount > 0) {
			entries.push({
				field: 'Hidden Context',
				category: 'withheld',
				value: `${hiddenCount} protected`,
				reason: 'Sensitive preferences concealed'
			});
		}

		entries.push({
			field: 'Emotional Attachment',
			category: 'withheld',
			reason: 'Personal motivations not exposed'
		});

		return entries;
	});
</script>

<svelte:head>
	<title>Auction Demo - VCP Multi-Agent</title>
	<meta
		name="description"
		content="See how VCP protects private valuations during a multi-agent auction."
	/>
</svelte:head>

<DemoContainer
	title="Art Auction"
	description="Three collectors bid on artwork. VCP protects their private valuations while enabling fair competition."
	onReset={reset}
>
	{#snippet controls()}
		<button
			class="control-btn"
			onclick={() => (isPlaying ? stopPlaying() : startPlayingWithSpeed())}
			disabled={currentStep >= auctionScenario.length && !isPlaying}
		>
			<span class="control-icon">{isPlaying ? '⏸' : '▶'}</span>
			<span>{isPlaying ? 'Pause' : 'Play'}</span>
		</button>
		<button
			class="control-btn"
			onclick={stepForward}
			disabled={isPlaying || currentStep >= auctionScenario.length}
		>
			<span class="control-icon">⏭</span>
			<span>Step</span>
		</button>
	{/snippet}

	{#snippet children()}
		<div class="auction-layout">
			<!-- Controls Row -->
			<div class="controls-row">
				<PresetLoader
					presets={auctionPresets}
					selected={selectedPreset}
					onselect={(p) => applyPreset(p as (typeof auctionPresets)[0])}
					title="Playback Speed"
				/>
				<AuditPanel entries={auditEntries} title="VCP Context Audit" compact={true} />
			</div>

			<!-- Item Card -->
			<div class="item-card">
				<div class="item-image">🖼️</div>
				<div class="item-details">
					<h3>{auctionItem.name}</h3>
					<p class="item-description">{auctionItem.description}</p>
					<div class="item-meta">
						<span class="meta-item">
							<span class="meta-label">Artist</span>
							<span class="meta-value">{auctionItem.attributes.artist}</span>
						</span>
						<span class="meta-item">
							<span class="meta-label">Year</span>
							<span class="meta-value">{auctionItem.attributes.year}</span>
						</span>
					</div>
					{#if currentStep > 0}
						<div class="current-bid">
							<span class="bid-label">Current Bid</span>
							<span class="bid-amount">
								${messages
									.filter((m) => m.action === 'bid')
									.slice(-1)[0]
									?.content.match(/\$[\d,]+/)?.[0]
									?.replace('$', '') || '5,000'}
							</span>
						</div>
					{/if}
				</div>
			</div>

			<!-- Arena -->
			<div class="arena-section">
				<MultiAgentArena
					agents={auctionAgents}
					{currentSpeaker}
					layout="row"
					showSharedFields={false}
				/>
			</div>

			<!-- Chat -->
			<div class="chat-section">
				<AgentChat {messages} agents={auctionAgents} {currentSpeaker} showContextIndicators={true} />
			</div>

			<!-- Progress -->
			<div class="progress-section">
				<div class="progress-bar">
					<div
						class="progress-fill"
						style="width: {(currentStep / auctionScenario.length) * 100}%"
					></div>
				</div>
				<span class="progress-text">Round {currentStep} of {auctionScenario.length}</span>
			</div>

			<!-- Learning Points (shown after completion) -->
			{#if currentStep >= auctionScenario.length}
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
	.auction-layout {
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

	.item-card {
		display: flex;
		gap: var(--space-xl);
		padding: var(--space-xl);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.item-image {
		font-size: 5rem;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		padding: var(--space-xl);
	}

	.item-details {
		flex: 1;
	}

	.item-details h3 {
		font-size: 1.5rem;
		margin-bottom: var(--space-sm);
	}

	.item-description {
		color: var(--color-text-muted);
		margin-bottom: var(--space-md);
	}

	.item-meta {
		display: flex;
		gap: var(--space-lg);
		margin-bottom: var(--space-md);
	}

	.meta-item {
		display: flex;
		flex-direction: column;
	}

	.meta-label {
		font-size: 0.75rem;
		color: var(--color-text-subtle);
		text-transform: uppercase;
	}

	.meta-value {
		font-weight: 500;
	}

	.current-bid {
		display: flex;
		flex-direction: column;
		padding: var(--space-md);
		background: var(--color-primary-muted);
		border-radius: var(--radius-md);
		width: fit-content;
	}

	.bid-label {
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.bid-amount {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--color-primary);
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

	:global(.control-btn) {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		padding: var(--space-sm) var(--space-md);
		background: var(--color-bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-md);
		color: var(--color-text-muted);
		font-size: 0.8125rem;
		cursor: pointer;
		transition: all var(--transition-fast);
	}

	:global(.control-btn:hover:not(:disabled)) {
		border-color: var(--color-primary);
		color: var(--color-text);
	}

	:global(.control-btn:disabled) {
		opacity: 0.5;
		cursor: not-allowed;
	}

	:global(.control-icon) {
		font-size: 1rem;
	}

	@media (max-width: 768px) {
		.item-card {
			flex-direction: column;
		}

		.item-image {
			font-size: 3rem;
			padding: var(--space-lg);
		}
	}
</style>
