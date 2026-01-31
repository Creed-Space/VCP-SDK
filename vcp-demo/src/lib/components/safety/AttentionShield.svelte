<script lang="ts">
	/**
	 * AttentionShield - Manipulation pattern detection visualization
	 */
	import type { AttentionProtection, ManipulationPattern, ProtectionMode } from '$lib/vcp/safety';

	interface Props {
		protection: AttentionProtection;
		onModeChange?: (mode: ProtectionMode) => void;
	}

	let { protection, onModeChange }: Props = $props();

	const modes: { value: ProtectionMode; label: string; icon: string; desc: string }[] = [
		{ value: 'off', label: 'Off', icon: 'fa-circle', desc: 'No protection' },
		{ value: 'monitor', label: 'Monitor', icon: 'fa-eye', desc: 'Track only' },
		{ value: 'warn', label: 'Warn', icon: 'fa-triangle-exclamation', desc: 'Show warnings' },
		{ value: 'block', label: 'Block', icon: 'fa-shield-halved', desc: 'Block detected' },
		{ value: 'strict', label: 'Strict', icon: 'fa-lock', desc: 'Aggressive blocking' }
	];

	const patternIcons: Record<string, string> = {
		false_urgency: 'fa-clock',
		artificial_scarcity: 'fa-box',
		social_proof_fake: 'fa-users',
		dark_pattern: 'fa-moon',
		emotional_manipulation: 'fa-heart-crack',
		attention_hijack: 'fa-fish',
		variable_reward: 'fa-dice',
		fear_appeal: 'fa-face-frown-open',
		guilt_trip: 'fa-face-sad-tear',
		parasocial_exploitation: 'fa-mobile-screen',
		outrage_bait: 'fa-face-angry',
		envy_induction: 'fa-eye'
	};

	function getBudgetPercent(): number {
		if (!protection.attention_budget) return 0;
		return (protection.attention_budget.used_today_minutes / protection.attention_budget.daily_limit_minutes) * 100;
	}

	function formatMinutes(minutes: number): string {
		if (minutes < 60) return `${Math.round(minutes)}m`;
		const hours = Math.floor(minutes / 60);
		const mins = Math.round(minutes % 60);
		return `${hours}h ${mins}m`;
	}
</script>

<div class="attention-shield">
	<!-- Protection Status -->
	<div class="status-header" class:active={protection.active}>
		<div class="status-icon">
			<i class="fa-solid {protection.active ? 'fa-shield-halved' : 'fa-circle'}" aria-hidden="true"></i>
		</div>
		<div class="status-info">
			<h3>Attention Shield</h3>
			<span class="status-label">{protection.active ? 'Active' : 'Inactive'}</span>
		</div>
		<div class="status-stats">
			<span class="stat">
				<span class="stat-value">{protection.blocked_count}</span>
				<span class="stat-label">Blocked</span>
			</span>
			<span class="stat">
				<span class="stat-value">{protection.warnings_shown}</span>
				<span class="stat-label">Warnings</span>
			</span>
		</div>
	</div>

	<!-- Mode Selector -->
	<div class="mode-section">
		<h4>Protection Mode</h4>
		<div class="mode-buttons" role="radiogroup" aria-label="Protection mode selection">
			{#each modes as mode}
				<button
					class="mode-btn"
					class:active={protection.mode === mode.value}
					onclick={() => onModeChange?.(mode.value)}
					aria-label="{mode.label}: {mode.desc}"
					role="radio"
					aria-checked={protection.mode === mode.value}
				>
					<span class="mode-icon" aria-hidden="true"><i class="fa-solid {mode.icon}"></i></span>
					<span class="mode-label">{mode.label}</span>
				</button>
			{/each}
		</div>
	</div>

	<!-- Sensitivity Slider -->
	<div class="sensitivity-section">
		<div class="sensitivity-header">
			<h4>Detection Sensitivity</h4>
			<span class="sensitivity-value">{Math.round(protection.sensitivity * 100)}%</span>
		</div>
		<div class="sensitivity-bar">
			<div
				class="sensitivity-fill"
				style="width: {protection.sensitivity * 100}%"
			></div>
		</div>
		<div class="sensitivity-labels">
			<span>Relaxed</span>
			<span>Aggressive</span>
		</div>
	</div>

	<!-- Attention Budget -->
	{#if protection.attention_budget}
		<div class="budget-section">
			<h4>Daily Attention Budget</h4>
			<div class="budget-bar">
				<div
					class="budget-fill"
					class:warning={getBudgetPercent() > 70}
					class:danger={getBudgetPercent() > 90}
					style="width: {Math.min(getBudgetPercent(), 100)}%"
				></div>
			</div>
			<div class="budget-info">
				<span>
					{formatMinutes(protection.attention_budget.used_today_minutes)} /
					{formatMinutes(protection.attention_budget.daily_limit_minutes)}
				</span>
				<div class="budget-breakdown">
					<span class="high-value">
						<i class="fa-solid fa-check" aria-hidden="true"></i> {formatMinutes(protection.attention_budget.high_value_time_minutes)} high-value
					</span>
					<span class="low-value">
						<i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i> {formatMinutes(protection.attention_budget.low_value_time_minutes)} low-value
					</span>
				</div>
			</div>
		</div>
	{/if}

	<!-- Detected Patterns -->
	<div class="patterns-section">
		<h4>Detected Patterns</h4>
		{#if protection.detected_patterns.length > 0}
			<div class="patterns-list">
				{#each protection.detected_patterns.slice(-5) as pattern}
					<div class="pattern-item" class:blocked={pattern.action_taken === 'blocked'}>
						<span class="pattern-icon"><i class="fa-solid {patternIcons[pattern.type] || 'fa-triangle-exclamation'}" aria-hidden="true"></i></span>
						<div class="pattern-info">
							<span class="pattern-type">{pattern.type.replace(/_/g, ' ')}</span>
							<span class="pattern-source">{pattern.source}</span>
						</div>
						<div class="pattern-meta">
							<span class="pattern-confidence">{Math.round(pattern.confidence * 100)}%</span>
							<span class="pattern-action" class:blocked={pattern.action_taken === 'blocked'}>
								{pattern.action_taken}
							</span>
						</div>
					</div>
				{/each}
			</div>
		{:else}
			<div class="no-patterns">
				<span class="no-patterns-icon"><i class="fa-solid fa-check-circle" aria-hidden="true"></i></span>
				<span>No manipulation patterns detected</span>
			</div>
		{/if}
	</div>

	<!-- Pattern Legend -->
	<div class="legend-section">
		<h4>Pattern Types</h4>
		<div class="legend-grid">
			{#each Object.entries(patternIcons) as [type, icon]}
				<div class="legend-item">
					<span class="legend-icon"><i class="fa-solid {icon}" aria-hidden="true"></i></span>
					<span class="legend-label">{type.replace(/_/g, ' ')}</span>
				</div>
			{/each}
		</div>
	</div>
</div>

<style>
	.attention-shield {
		display: flex;
		flex-direction: column;
		gap: var(--space-lg);
	}

	.status-header {
		display: flex;
		align-items: center;
		gap: var(--space-md);
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		border-left: 4px solid var(--color-text-subtle);
	}

	.status-header.active {
		border-color: var(--color-success);
	}

	.status-icon {
		font-size: 2rem;
	}

	.status-info h3 {
		margin: 0 0 4px 0;
	}

	.status-label {
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	.status-stats {
		display: flex;
		gap: var(--space-lg);
		margin-left: auto;
	}

	.stat {
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.stat-value {
		font-family: var(--font-mono);
		font-size: 1.5rem;
		font-weight: 700;
	}

	.stat-label {
		font-size: 0.6875rem;
		color: var(--color-text-subtle);
		text-transform: uppercase;
	}

	.mode-section,
	.sensitivity-section,
	.budget-section,
	.patterns-section,
	.legend-section {
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
	}

	h4 {
		font-size: 0.9375rem;
		margin-bottom: var(--space-md);
	}

	.mode-buttons {
		display: flex;
		gap: var(--space-xs);
	}

	.mode-btn {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-xs);
		padding: var(--space-md);
		min-height: 70px;
		min-width: 60px;
		background: var(--color-bg-card);
		border: 2px solid rgba(255, 255, 255, 0.3);
		border-radius: var(--radius-md);
		cursor: pointer;
		transition: all var(--transition-fast);
		color: #e0e0e0;
	}

	.mode-btn:hover {
		border-color: var(--color-primary);
		background: rgba(99, 102, 241, 0.15);
		color: #ffffff;
		transform: translateY(-2px);
	}

	.mode-btn:focus-visible {
		outline: 2px solid var(--color-primary);
		outline-offset: 2px;
	}

	.mode-btn.active {
		background: var(--color-primary);
		border-color: var(--color-primary);
		color: white;
		box-shadow: 0 0 16px rgba(99, 102, 241, 0.6);
		transform: translateY(-2px);
	}

	.mode-btn.active .mode-icon {
		color: white;
	}

	.mode-btn.active .mode-label {
		color: white;
		font-weight: 700;
	}

	.mode-icon {
		font-size: 1.75rem;
	}

	.mode-label {
		font-size: 0.875rem;
		font-weight: 600;
	}

	.sensitivity-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.sensitivity-value {
		font-family: var(--font-mono);
		font-weight: 600;
	}

	.sensitivity-bar {
		height: 8px;
		background: var(--color-bg-elevated);
		border-radius: var(--radius-full);
		overflow: hidden;
		margin-bottom: var(--space-xs);
	}

	.sensitivity-fill {
		height: 100%;
		background: linear-gradient(90deg, #2ecc71, #f39c12, #e74c3c);
		border-radius: var(--radius-full);
	}

	.sensitivity-labels {
		display: flex;
		justify-content: space-between;
		font-size: 0.6875rem;
		color: var(--color-text-subtle);
	}

	.budget-bar {
		height: 12px;
		background: var(--color-bg-elevated);
		border-radius: var(--radius-full);
		overflow: hidden;
		margin-bottom: var(--space-sm);
	}

	.budget-fill {
		height: 100%;
		background: var(--color-success);
		border-radius: var(--radius-full);
		transition: width var(--transition-normal);
	}

	.budget-fill.warning {
		background: var(--color-warning);
	}

	.budget-fill.danger {
		background: var(--color-danger);
	}

	.budget-info {
		font-size: 0.875rem;
	}

	.budget-breakdown {
		display: flex;
		gap: var(--space-md);
		margin-top: var(--space-xs);
		font-size: 0.75rem;
	}

	.high-value {
		color: var(--color-success);
	}

	.low-value {
		color: var(--color-warning);
	}

	.patterns-list {
		display: flex;
		flex-direction: column;
		gap: var(--space-sm);
	}

	.pattern-item {
		display: flex;
		align-items: center;
		gap: var(--space-md);
		padding: var(--space-sm) var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
	}

	.pattern-item.blocked {
		border-left: 3px solid var(--color-danger);
	}

	.pattern-icon {
		font-size: 1.25rem;
	}

	.pattern-info {
		flex: 1;
		display: flex;
		flex-direction: column;
	}

	.pattern-type {
		font-size: 0.875rem;
		text-transform: capitalize;
	}

	.pattern-source {
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.pattern-meta {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: 2px;
	}

	.pattern-confidence {
		font-family: var(--font-mono);
		font-size: 0.75rem;
	}

	.pattern-action {
		font-size: 0.6875rem;
		padding: 2px 6px;
		background: var(--color-bg);
		border-radius: var(--radius-sm);
		text-transform: capitalize;
	}

	.pattern-action.blocked {
		background: var(--color-danger-muted);
		color: var(--color-danger);
	}

	.no-patterns {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-lg);
		background: var(--color-success-muted);
		border-radius: var(--radius-md);
		color: var(--color-success);
	}

	.no-patterns-icon {
		font-size: 1.25rem;
	}

	.legend-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
		gap: var(--space-xs);
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-size: 0.75rem;
		padding: var(--space-xs);
	}

	.legend-icon {
		font-size: 1rem;
	}

	.legend-label {
		text-transform: capitalize;
		color: var(--color-text-muted);
	}
</style>
