<script lang="ts">
	/**
	 * MultiAgentArena - Visualization of multiple agents with shared context
	 */
	import type { AgentIdentity, SharedContextSpace } from '$lib/vcp/multi-agent';
	import AgentAvatar from './AgentAvatar.svelte';

	interface Props {
		agents: AgentIdentity[];
		sharedContext?: SharedContextSpace | null;
		currentSpeaker?: string | null;
		layout?: 'circle' | 'row' | 'grid';
		showSharedFields?: boolean;
	}

	let {
		agents = [],
		sharedContext = null,
		currentSpeaker = null,
		layout = 'circle',
		showSharedFields = true
	}: Props = $props();

	function getAgentState(agentId: string): 'idle' | 'thinking' | 'speaking' | 'listening' {
		if (currentSpeaker === agentId) return 'speaking';
		if (currentSpeaker) return 'listening';
		return 'idle';
	}

	// Calculate positions for circle layout
	function getCirclePosition(index: number, total: number): { x: number; y: number } {
		const angle = (index / total) * 2 * Math.PI - Math.PI / 2;
		const radius = 120;
		return {
			x: Math.cos(angle) * radius + 150,
			y: Math.sin(angle) * radius + 150
		};
	}
</script>

<div class="arena arena-{layout}">
	{#if layout === 'circle'}
		<div class="arena-circle">
			<!-- Connection lines -->
			<svg class="connection-lines" viewBox="0 0 300 300">
				{#each agents as agent, i}
					{#each agents.slice(i + 1) as otherAgent, j}
						{@const pos1 = getCirclePosition(i, agents.length)}
						{@const pos2 = getCirclePosition(i + j + 1, agents.length)}
						<line
							x1={pos1.x}
							y1={pos1.y}
							x2={pos2.x}
							y2={pos2.y}
							stroke="rgba(255,255,255,0.1)"
							stroke-width="1"
						/>
					{/each}
				{/each}
			</svg>

			<!-- Shared context center -->
			{#if showSharedFields && sharedContext}
				<div class="shared-center">
					<span class="shared-icon">🔗</span>
					<span class="shared-label">Shared</span>
					<span class="shared-count">{sharedContext.shared_fields.length} fields</span>
				</div>
			{/if}

			<!-- Agents -->
			{#each agents as agent, i}
				{@const pos = getCirclePosition(i, agents.length)}
				<div
					class="agent-node"
					style="left: {pos.x}px; top: {pos.y}px; transform: translate(-50%, -50%)"
				>
					<AgentAvatar {agent} state={getAgentState(agent.agent_id)} size="lg" />
				</div>
			{/each}
		</div>
	{:else if layout === 'row'}
		<div class="arena-row">
			{#each agents as agent}
				<div class="agent-card">
					<AgentAvatar {agent} state={getAgentState(agent.agent_id)} size="lg" />
					<div class="agent-info">
						<span class="agent-role">{agent.role}</span>
						{#if sharedContext?.private_per_agent[agent.agent_id]}
							<span class="private-badge">
								🔒 {sharedContext.private_per_agent[agent.agent_id].length} private
							</span>
						{/if}
					</div>
				</div>
			{/each}
		</div>
	{:else}
		<div class="arena-grid">
			{#each agents as agent}
				<div class="agent-card">
					<AgentAvatar {agent} state={getAgentState(agent.agent_id)} size="md" />
					<div class="agent-info">
						<span class="agent-role">{agent.role}</span>
					</div>
				</div>
			{/each}
		</div>
	{/if}

	<!-- Shared Fields Panel -->
	{#if showSharedFields && sharedContext && layout !== 'circle'}
		<div class="shared-panel">
			<h4>
				<span class="panel-icon">🔗</span>
				Shared Context Space
			</h4>
			<div class="shared-fields">
				{#each sharedContext.shared_fields as field}
					<span class="field-chip shared">{field}</span>
				{/each}
			</div>
			{#if sharedContext.consensus_required.length > 0}
				<div class="consensus-fields">
					<span class="consensus-label">Requires consensus:</span>
					{#each sharedContext.consensus_required as field}
						<span class="field-chip consensus">{field}</span>
					{/each}
				</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	.arena {
		position: relative;
		width: 100%;
	}

	/* Circle Layout */
	.arena-circle {
		position: relative;
		width: 300px;
		height: 300px;
		margin: 0 auto;
	}

	.connection-lines {
		position: absolute;
		inset: 0;
		pointer-events: none;
	}

	.shared-center {
		position: absolute;
		left: 50%;
		top: 50%;
		transform: translate(-50%, -50%);
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: var(--space-md);
		background: var(--color-bg-card);
		border-radius: 50%;
		width: 80px;
		height: 80px;
		justify-content: center;
		border: 2px dashed rgba(255, 255, 255, 0.2);
	}

	.shared-icon {
		font-size: 1.25rem;
	}

	.shared-label {
		font-size: 0.625rem;
		color: var(--color-text-muted);
		text-transform: uppercase;
	}

	.shared-count {
		font-size: 0.6875rem;
		color: var(--color-primary);
	}

	.agent-node {
		position: absolute;
	}

	/* Row Layout */
	.arena-row {
		display: flex;
		justify-content: center;
		gap: var(--space-xl);
		padding: var(--space-lg);
		flex-wrap: wrap;
	}

	.agent-card {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
		min-width: 120px;
	}

	.agent-info {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-xs);
	}

	.agent-role {
		font-size: 0.75rem;
		color: var(--color-text-muted);
		text-transform: capitalize;
	}

	.private-badge {
		font-size: 0.6875rem;
		padding: 2px 6px;
		background: var(--color-warning-muted);
		color: var(--color-warning);
		border-radius: var(--radius-sm);
	}

	/* Grid Layout */
	.arena-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
		gap: var(--space-md);
		padding: var(--space-md);
	}

	.arena-grid .agent-card {
		min-width: unset;
		padding: var(--space-md);
	}

	/* Shared Panel */
	.shared-panel {
		margin-top: var(--space-lg);
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.shared-panel h4 {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-size: 0.875rem;
		margin-bottom: var(--space-sm);
	}

	.panel-icon {
		font-size: 1rem;
	}

	.shared-fields,
	.consensus-fields {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-xs);
	}

	.consensus-fields {
		margin-top: var(--space-sm);
	}

	.consensus-label {
		font-size: 0.75rem;
		color: var(--color-text-muted);
		width: 100%;
		margin-bottom: var(--space-xs);
	}

	.field-chip {
		font-size: 0.75rem;
		padding: 2px 8px;
		border-radius: var(--radius-sm);
	}

	.field-chip.shared {
		background: var(--color-success-muted);
		color: var(--color-success);
	}

	.field-chip.consensus {
		background: var(--color-warning-muted);
		color: var(--color-warning);
	}
</style>
