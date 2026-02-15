<script lang="ts">
	/**
	 * AgentAvatar - Visual representation of an AI agent
	 */
	import type { AgentIdentity } from '$lib/vcp/multi-agent';

	interface Props {
		agent: AgentIdentity;
		state?: 'idle' | 'thinking' | 'speaking' | 'listening';
		size?: 'sm' | 'md' | 'lg';
		showBadge?: boolean;
		showName?: boolean;
	}

	let {
		agent,
		state = 'idle',
		size = 'md',
		showBadge = true,
		showName = true
	}: Props = $props();

	const sizeClasses = {
		sm: 'size-sm',
		md: 'size-md',
		lg: 'size-lg'
	};

	const stateLabels = {
		idle: '',
		thinking: '...',
		speaking: '💬',
		listening: '👂'
	};

	const roleIcons: Record<string, string> = {
		negotiator: '🤝',
		mediator: '⚖️',
		voter: '🗳️',
		advocate: '📢',
		bidder: '💰',
		auctioneer: '🔨'
	};
</script>

<div class="agent-avatar {sizeClasses[size]}" class:thinking={state === 'thinking'}>
	<div class="avatar-ring" style="--agent-color: {agent.color}">
		<div class="avatar-icon">
			{agent.avatar}
		</div>
		{#if state !== 'idle'}
			<span class="state-indicator">{stateLabels[state]}</span>
		{/if}
	</div>

	{#if showBadge}
		<span class="role-badge" title={agent.role}>
			{roleIcons[agent.role] || '🤖'}
		</span>
	{/if}

	{#if showName}
		<span class="agent-name">{agent.display_name}</span>
	{/if}
</div>

<style>
	.agent-avatar {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-xs);
		position: relative;
	}

	.avatar-ring {
		border-radius: 50%;
		background: var(--color-bg-card);
		border: 3px solid var(--agent-color, var(--color-primary));
		display: flex;
		align-items: center;
		justify-content: center;
		position: relative;
		transition: all var(--transition-fast);
	}

	.thinking .avatar-ring {
		animation: pulse 1.5s ease-in-out infinite;
	}

	.avatar-icon {
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.state-indicator {
		position: absolute;
		bottom: -4px;
		right: -4px;
		font-size: 0.75em;
		animation: bounce 0.6s ease-in-out infinite;
	}

	.role-badge {
		position: absolute;
		top: -4px;
		right: -4px;
		background: var(--color-bg-elevated);
		border-radius: 50%;
		padding: 2px;
		font-size: 0.7em;
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.agent-name {
		font-size: 0.75rem;
		font-weight: 500;
		color: var(--color-text-muted);
		text-align: center;
		max-width: 100%;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	/* Sizes */
	.size-sm .avatar-ring {
		width: 40px;
		height: 40px;
	}

	.size-sm .avatar-icon {
		font-size: 1.25rem;
	}

	.size-md .avatar-ring {
		width: 56px;
		height: 56px;
	}

	.size-md .avatar-icon {
		font-size: 1.75rem;
	}

	.size-lg .avatar-ring {
		width: 80px;
		height: 80px;
	}

	.size-lg .avatar-icon {
		font-size: 2.5rem;
	}

	@keyframes pulse {
		0%,
		100% {
			box-shadow: 0 0 0 0 var(--agent-color, var(--color-primary));
		}
		50% {
			box-shadow: 0 0 0 8px transparent;
		}
	}

	@keyframes bounce {
		0%,
		100% {
			transform: translateY(0);
		}
		50% {
			transform: translateY(-3px);
		}
	}
</style>
