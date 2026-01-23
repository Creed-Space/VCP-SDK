<script lang="ts">
	/**
	 * AgentChat - Chat interface for agent interactions
	 */
	import type { AgentIdentity } from '$lib/vcp/multi-agent';
	import AgentAvatar from './AgentAvatar.svelte';

	interface ChatMessage {
		id: string;
		sender: AgentIdentity;
		content: string;
		timestamp: string;
		vcpContextShared?: string[];
		vcpContextHidden?: string[];
		action?: string;
	}

	interface Props {
		messages: ChatMessage[];
		agents: AgentIdentity[];
		currentSpeaker?: string | null;
		showContextIndicators?: boolean;
	}

	let {
		messages = [],
		agents = [],
		currentSpeaker = null,
		showContextIndicators = true
	}: Props = $props();

	function getAgentState(agentId: string): 'idle' | 'speaking' | 'listening' {
		if (currentSpeaker === agentId) return 'speaking';
		if (currentSpeaker) return 'listening';
		return 'idle';
	}

	function formatTime(timestamp: string): string {
		try {
			return new Date(timestamp).toLocaleTimeString([], {
				hour: '2-digit',
				minute: '2-digit'
			});
		} catch {
			return '';
		}
	}
</script>

<div class="agent-chat">
	<!-- Agent Roster -->
	<div class="agent-roster">
		{#each agents as agent}
			<AgentAvatar {agent} state={getAgentState(agent.agent_id)} size="sm" showName={true} />
		{/each}
	</div>

	<!-- Messages -->
	<div class="message-list">
		{#each messages as message (message.id)}
			<div
				class="message"
				style="--sender-color: {message.sender.color}"
			>
				<div class="message-avatar">
					<AgentAvatar
						agent={message.sender}
						state="idle"
						size="sm"
						showBadge={false}
						showName={false}
					/>
				</div>

				<div class="message-content">
					<div class="message-header">
						<span class="sender-name" style="color: {message.sender.color}">
							{message.sender.display_name}
						</span>
						{#if message.action}
							<span class="action-badge">{message.action}</span>
						{/if}
						<span class="timestamp">{formatTime(message.timestamp)}</span>
					</div>

					<div class="message-body">
						{message.content}
					</div>

					{#if showContextIndicators && (message.vcpContextShared?.length || message.vcpContextHidden?.length)}
						<div class="context-indicators">
							{#if message.vcpContextShared?.length}
								<span class="context-shared" title="VCP context shared">
									✓ {message.vcpContextShared.join(', ')}
								</span>
							{/if}
							{#if message.vcpContextHidden?.length}
								<span class="context-hidden" title="VCP context (private, influenced output)">
									🔒 {message.vcpContextHidden.length} private field{message.vcpContextHidden.length > 1 ? 's' : ''} influenced
								</span>
							{/if}
						</div>
					{/if}
				</div>
			</div>
		{/each}

		{#if messages.length === 0}
			<div class="empty-state">
				<span class="empty-icon">💬</span>
				<p>No messages yet. Start the simulation to see agent interactions.</p>
			</div>
		{/if}
	</div>
</div>

<style>
	.agent-chat {
		display: flex;
		flex-direction: column;
		height: 100%;
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		overflow: hidden;
	}

	.agent-roster {
		display: flex;
		gap: var(--space-lg);
		padding: var(--space-md) var(--space-lg);
		background: var(--color-bg-elevated);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
		overflow-x: auto;
	}

	.message-list {
		flex: 1;
		overflow-y: auto;
		padding: var(--space-md);
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
	}

	.message {
		display: flex;
		gap: var(--space-md);
		padding: var(--space-md);
		background: var(--color-bg);
		border-radius: var(--radius-md);
		border-left: 3px solid var(--sender-color, var(--color-primary));
	}

	.message-avatar {
		flex-shrink: 0;
	}

	.message-content {
		flex: 1;
		min-width: 0;
	}

	.message-header {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-xs);
	}

	.sender-name {
		font-weight: 600;
		font-size: 0.875rem;
	}

	.action-badge {
		font-size: 0.6875rem;
		padding: 2px 6px;
		background: var(--color-primary-muted);
		color: var(--color-primary);
		border-radius: var(--radius-sm);
		text-transform: uppercase;
	}

	.timestamp {
		font-size: 0.75rem;
		color: var(--color-text-subtle);
		margin-left: auto;
	}

	.message-body {
		font-size: 0.9375rem;
		line-height: 1.5;
		color: var(--color-text);
	}

	.context-indicators {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-sm);
		margin-top: var(--space-sm);
		font-size: 0.75rem;
	}

	.context-shared {
		color: var(--color-success);
		background: var(--color-success-muted);
		padding: 2px 6px;
		border-radius: var(--radius-sm);
	}

	.context-hidden {
		color: var(--color-warning);
		background: var(--color-warning-muted);
		padding: 2px 6px;
		border-radius: var(--radius-sm);
	}

	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: var(--space-2xl);
		text-align: center;
		color: var(--color-text-muted);
	}

	.empty-icon {
		font-size: 3rem;
		margin-bottom: var(--space-md);
		opacity: 0.5;
	}
</style>
