<script lang="ts">
	/**
	 * AuditPanel Component
	 * Shows what was shared, withheld, and how it influenced outcomes
	 */

	interface AuditEntry {
		field: string;
		category: 'shared' | 'withheld' | 'influenced';
		value?: string | number | boolean;
		reason?: string;
		stakeholder?: string;
		timestamp?: string;
	}

	interface Props {
		entries: AuditEntry[];
		title?: string;
		showTimestamps?: boolean;
		groupByCategory?: boolean;
		compact?: boolean;
	}

	let {
		entries,
		title = 'Audit Trail',
		showTimestamps = false,
		groupByCategory = true,
		compact = false
	}: Props = $props();

	const groupedEntries = $derived.by(() => {
		if (!groupByCategory) return { all: entries };

		return {
			shared: entries.filter((e) => e.category === 'shared'),
			influenced: entries.filter((e) => e.category === 'influenced'),
			withheld: entries.filter((e) => e.category === 'withheld')
		};
	});

	const categories = [
		{ key: 'shared', label: 'Shared', icon: 'fa-circle-check', color: 'success' },
		{ key: 'influenced', label: 'Influenced', icon: 'fa-bolt', color: 'warning' },
		{ key: 'withheld', label: 'Withheld', icon: 'fa-lock', color: 'danger' }
	] as const;

	function formatValue(value: string | number | boolean | undefined): string {
		if (value === undefined) return '—';
		if (typeof value === 'boolean') return value ? 'Yes' : 'No';
		return String(value);
	}
</script>

<div class="audit-panel" class:compact>
	{#if title}
		<div class="audit-header">
			<h3><i class="fa-solid fa-clipboard-list" aria-hidden="true"></i> {title}</h3>
			<div class="audit-summary">
				<span class="summary-item success">{groupedEntries.shared?.length ?? 0} shared</span>
				<span class="summary-item warning">{groupedEntries.influenced?.length ?? 0} influenced</span>
				<span class="summary-item danger">{groupedEntries.withheld?.length ?? 0} withheld</span>
			</div>
		</div>
	{/if}

	{#if groupByCategory}
		<div class="audit-categories">
			{#each categories as cat}
				{@const catEntries = groupedEntries[cat.key] ?? []}
				{#if catEntries.length > 0}
					<div class="audit-category category-{cat.color}">
						<div class="category-header">
							<span class="category-icon"><i class="fa-solid {cat.icon}" aria-hidden="true"></i></span>
							<span class="category-label">{cat.label}</span>
							<span class="category-count">{catEntries.length}</span>
						</div>
						<div class="category-entries">
							{#each catEntries as entry}
								<div class="audit-entry">
									<div class="entry-field">{entry.field}</div>
									{#if entry.value !== undefined}
										<div class="entry-value">{formatValue(entry.value)}</div>
									{/if}
									{#if entry.reason}
										<div class="entry-reason">{entry.reason}</div>
									{/if}
									{#if entry.stakeholder}
										<div class="entry-stakeholder">
											<i class="fa-solid fa-user" aria-hidden="true"></i>
											{entry.stakeholder}
										</div>
									{/if}
									{#if showTimestamps && entry.timestamp}
										<div class="entry-timestamp">{entry.timestamp}</div>
									{/if}
								</div>
							{/each}
						</div>
					</div>
				{/if}
			{/each}
		</div>
	{:else}
		<div class="audit-list">
			{#each entries as entry}
				<div class="audit-entry audit-entry-{entry.category}">
					<span class="entry-indicator"></span>
					<div class="entry-content">
						<div class="entry-field">{entry.field}</div>
						{#if entry.value !== undefined}
							<div class="entry-value">{formatValue(entry.value)}</div>
						{/if}
						{#if entry.reason}
							<div class="entry-reason">{entry.reason}</div>
						{/if}
					</div>
					{#if showTimestamps && entry.timestamp}
						<div class="entry-timestamp">{entry.timestamp}</div>
					{/if}
				</div>
			{/each}
		</div>
	{/if}

	<div class="audit-footer">
		<span class="footer-note">
			<i class="fa-solid fa-shield-halved" aria-hidden="true"></i>
			Private context influenced behavior without being exposed
		</span>
	</div>
</div>

<style>
	.audit-panel {
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.audit-panel.compact {
		padding: var(--space-md);
		gap: var(--space-sm);
	}

	.audit-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		flex-wrap: wrap;
		gap: var(--space-sm);
	}

	.audit-header h3 {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-size: 1rem;
		margin: 0;
	}

	.audit-summary {
		display: flex;
		gap: var(--space-sm);
	}

	.summary-item {
		font-size: 0.6875rem;
		padding: 2px 8px;
		border-radius: var(--radius-sm);
	}

	.summary-item.success {
		background: var(--color-success-muted);
		color: var(--color-success);
	}

	.summary-item.warning {
		background: var(--color-warning-muted);
		color: var(--color-warning);
	}

	.summary-item.danger {
		background: var(--color-danger-muted);
		color: var(--color-danger);
	}

	.audit-categories {
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
	}

	.audit-category {
		background: var(--color-bg);
		border-radius: var(--radius-md);
		overflow: hidden;
	}

	.category-header {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-sm) var(--space-md);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.category-success .category-header {
		background: var(--color-success-muted);
	}

	.category-warning .category-header {
		background: var(--color-warning-muted);
	}

	.category-danger .category-header {
		background: var(--color-danger-muted);
	}

	.category-icon {
		font-size: 0.75rem;
	}

	.category-success .category-icon {
		color: var(--color-success);
	}

	.category-warning .category-icon {
		color: var(--color-warning);
	}

	.category-danger .category-icon {
		color: var(--color-danger);
	}

	.category-label {
		font-size: 0.75rem;
		font-weight: 600;
		flex: 1;
	}

	.category-count {
		font-size: 0.6875rem;
		padding: 1px 6px;
		background: rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-sm);
	}

	.category-entries {
		padding: var(--space-sm);
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
	}

	.audit-entry {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: var(--space-xs) var(--space-sm);
		padding: var(--space-xs) var(--space-sm);
		background: rgba(255, 255, 255, 0.03);
		border-radius: var(--radius-sm);
		font-size: 0.8125rem;
	}

	.entry-field {
		font-weight: 500;
		color: var(--color-text);
	}

	.entry-value {
		font-family: var(--font-mono);
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.entry-reason {
		width: 100%;
		font-size: 0.75rem;
		color: var(--color-text-subtle);
		font-style: italic;
	}

	.entry-stakeholder {
		font-size: 0.6875rem;
		color: var(--color-text-subtle);
		display: flex;
		align-items: center;
		gap: 4px;
	}

	.entry-timestamp {
		font-size: 0.6875rem;
		color: var(--color-text-subtle);
		margin-left: auto;
	}

	.audit-list {
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
	}

	.audit-list .audit-entry {
		border-left: 3px solid transparent;
	}

	.audit-entry-shared {
		border-color: var(--color-success);
	}

	.audit-entry-influenced {
		border-color: var(--color-warning);
	}

	.audit-entry-withheld {
		border-color: var(--color-danger);
	}

	.entry-indicator {
		display: none;
	}

	.entry-content {
		flex: 1;
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: var(--space-xs) var(--space-sm);
	}

	.audit-footer {
		padding-top: var(--space-sm);
		border-top: 1px solid rgba(255, 255, 255, 0.05);
	}

	.footer-note {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		font-size: 0.6875rem;
		color: var(--color-text-subtle);
		font-style: italic;
	}

	.compact .audit-entry {
		padding: var(--space-xs);
	}

	.compact .entry-field {
		font-size: 0.75rem;
	}

	@media (max-width: 640px) {
		.audit-header {
			flex-direction: column;
			align-items: flex-start;
		}
	}
</style>
