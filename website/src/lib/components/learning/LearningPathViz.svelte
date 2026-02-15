<script lang="ts">
	/**
	 * LearningPathViz - Visual learning path progression
	 */
	import type { LearningPath, LearningTopic, MasteryLevel } from '$lib/vcp/learning';
	import type { ExperienceLevel } from '$lib/vcp/types';

	interface Props {
		path: LearningPath;
		mastery: Record<string, MasteryLevel>;
		onTopicSelect?: (topicId: string) => void;
	}

	let { path, mastery, onTopicSelect }: Props = $props();

	const levelColors: Record<ExperienceLevel, string> = {
		beginner: '#3498db',
		intermediate: '#f39c12',
		advanced: '#2ecc71',
		expert: '#9b59b6'
	};

	function getMasteryForTopic(topicId: string): MasteryLevel | undefined {
		return mastery[topicId];
	}

	function getTopicStatus(
		topic: LearningTopic,
		index: number
	): 'locked' | 'available' | 'in_progress' | 'completed' {
		const topicMastery = getMasteryForTopic(topic.topic_id);
		if (topicMastery && topicMastery.confidence >= topic.mastery_threshold) {
			return 'completed';
		}
		if (index === path.current_position) {
			return 'in_progress';
		}
		if (index < path.current_position) {
			return 'completed';
		}
		// Check prerequisites
		const prereqsMet = topic.prerequisites.every((prereq) => {
			const prereqMastery = getMasteryForTopic(prereq);
			return prereqMastery && prereqMastery.confidence >= 0.7;
		});
		return prereqsMet ? 'available' : 'locked';
	}

	function getDifficultyStars(difficulty: number): string {
		return '★'.repeat(difficulty) + '☆'.repeat(5 - difficulty);
	}

	function getProgressPercent(): number {
		return (path.completed_hours / path.estimated_total_hours) * 100;
	}
</script>

<div class="learning-path-viz">
	<!-- Path Header -->
	<div class="path-header">
		<div class="path-info">
			<h3>{path.name}</h3>
			<p class="path-desc">{path.description}</p>
		</div>
		<div class="path-progress">
			<div class="progress-bar">
				<div class="progress-fill" style="width: {getProgressPercent()}%"></div>
			</div>
			<div class="progress-text">
				<span>{path.completed_hours.toFixed(1)}h / {path.estimated_total_hours}h</span>
				<span class="progress-percent">{Math.round(getProgressPercent())}%</span>
			</div>
		</div>
	</div>

	<!-- Personalization Applied -->
	{#if path.personalization_applied.length > 0}
		<div class="personalization-notice">
			<span class="notice-icon"><i class="fa-solid fa-wand-magic-sparkles" aria-hidden="true"></i></span>
			<span>Personalized for you:</span>
			{#each path.personalization_applied as adaptation}
				<span class="adaptation-chip">{adaptation.replace(/_/g, ' ')}</span>
			{/each}
		</div>
	{/if}

	<!-- Topic Path -->
	<div class="topics-path" role="list" aria-label="Learning path topics">
		{#each path.topics as topic, i}
			{@const status = getTopicStatus(topic, i)}
			{@const topicMastery = getMasteryForTopic(topic.topic_id)}
			<div class="topic-node-container" role="listitem">
				{#if i > 0}
					<div class="connector" class:completed={status === 'completed'} aria-hidden="true"></div>
				{/if}
				<button
					class="topic-node"
					class:locked={status === 'locked'}
					class:available={status === 'available'}
					class:in-progress={status === 'in_progress'}
					class:completed={status === 'completed'}
					disabled={status === 'locked'}
					onclick={() => onTopicSelect?.(topic.topic_id)}
					aria-label="{topic.name} - {status === 'completed' ? 'Completed' : status === 'in_progress' ? 'In progress' : status === 'locked' ? 'Locked' : 'Available'}, {topic.estimated_hours} hours, difficulty {topic.difficulty} of 5"
				>
					<div class="node-indicator">
						{#if status === 'completed'}
							<i class="fa-solid fa-check" aria-hidden="true"></i>
						{:else if status === 'in_progress'}
							<i class="fa-solid fa-play" aria-hidden="true"></i>
						{:else if status === 'locked'}
							<i class="fa-solid fa-lock" aria-hidden="true"></i>
						{:else}
							{i + 1}
						{/if}
					</div>
					<div class="node-content">
						<span class="topic-name">{topic.name}</span>
						<div class="topic-meta">
							<span class="difficulty">{getDifficultyStars(topic.difficulty)}</span>
							<span class="duration">{topic.estimated_hours}h</span>
						</div>
						{#if topicMastery}
							<div class="mastery-bar">
								<div
									class="mastery-fill"
									style="width: {topicMastery.confidence * 100}%; background: {levelColors[
										topicMastery.level
									]}"
								></div>
							</div>
							<span class="mastery-level" style="color: {levelColors[topicMastery.level]}">
								{topicMastery.level}
							</span>
						{/if}
					</div>
				</button>

				<!-- Topic Details (expanded for current) -->
				{#if status === 'in_progress'}
					<div class="topic-details">
						<div class="detail-row">
							<span class="detail-label">Modalities:</span>
							<div class="modality-chips">
								{#each topic.modalities_available as mod}
									<span class="modality-chip">{mod}</span>
								{/each}
							</div>
						</div>
						{#if topic.analogies_available.length > 0}
							<div class="detail-row">
								<span class="detail-label">Analogies:</span>
								<div class="analogy-chips">
									{#each topic.analogies_available as analogy}
										<span class="analogy-chip">{analogy}</span>
									{/each}
								</div>
							</div>
						{/if}
						{#if topic.prerequisites.length > 0}
							<div class="detail-row">
								<span class="detail-label">Prerequisites:</span>
								<span class="prereqs">{topic.prerequisites.join(', ')}</span>
							</div>
						{/if}
					</div>
				{/if}
			</div>
		{/each}
	</div>

	<!-- Legend -->
	<div class="legend">
		<div class="legend-item">
			<span class="legend-dot completed"></span>
			<span>Completed</span>
		</div>
		<div class="legend-item">
			<span class="legend-dot in-progress"></span>
			<span>In Progress</span>
		</div>
		<div class="legend-item">
			<span class="legend-dot available"></span>
			<span>Available</span>
		</div>
		<div class="legend-item">
			<span class="legend-dot locked"></span>
			<span>Locked</span>
		</div>
	</div>
</div>

<style>
	.learning-path-viz {
		display: flex;
		flex-direction: column;
		gap: var(--space-lg);
	}

	.path-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: var(--space-lg);
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
	}

	.path-info h3 {
		margin: 0 0 var(--space-xs) 0;
	}

	.path-desc {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		margin: 0;
	}

	.path-progress {
		min-width: 200px;
	}

	.progress-bar {
		height: 8px;
		background: var(--color-bg-elevated);
		border-radius: var(--radius-full);
		overflow: hidden;
		margin-bottom: var(--space-xs);
	}

	.progress-fill {
		height: 100%;
		background: var(--color-success);
		border-radius: var(--radius-full);
		transition: width var(--transition-normal);
	}

	.progress-text {
		display: flex;
		justify-content: space-between;
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.progress-percent {
		font-weight: 600;
		color: var(--color-success);
	}

	.personalization-notice {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: var(--space-xs);
		padding: var(--space-md);
		background: var(--color-primary-muted);
		border-radius: var(--radius-md);
		font-size: 0.875rem;
	}

	.notice-icon {
		font-size: 1rem;
	}

	.adaptation-chip {
		font-size: 0.6875rem;
		padding: 2px 8px;
		background: rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-sm);
		text-transform: capitalize;
	}

	.topics-path {
		display: flex;
		flex-direction: column;
		gap: 0;
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
	}

	.topic-node-container {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
	}

	.connector {
		width: 2px;
		height: 24px;
		background: var(--color-bg-elevated);
		margin-left: 19px;
	}

	.connector.completed {
		background: var(--color-success);
	}

	.topic-node {
		display: flex;
		align-items: flex-start;
		gap: var(--space-md);
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border: 2px solid transparent;
		border-radius: var(--radius-md);
		width: 100%;
		text-align: left;
		cursor: pointer;
		transition: all var(--transition-fast);
	}

	.topic-node:hover:not(:disabled) {
		border-color: var(--color-primary);
	}

	.topic-node:focus-visible {
		outline: 2px solid var(--color-primary);
		outline-offset: 2px;
	}

	.topic-node.locked {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.topic-node.available {
		border-color: var(--color-text-subtle);
	}

	.topic-node.in-progress {
		border-color: var(--color-primary);
		background: var(--color-primary-muted);
	}

	.topic-node.completed {
		border-color: var(--color-success);
	}

	.node-indicator {
		width: 40px;
		height: 40px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-bg);
		border-radius: 50%;
		font-weight: 700;
		flex-shrink: 0;
	}

	.topic-node.completed .node-indicator {
		background: var(--color-success);
		color: white;
	}

	.topic-node.in-progress .node-indicator {
		background: var(--color-primary);
		color: white;
	}

	.node-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.topic-name {
		font-weight: 500;
	}

	.topic-meta {
		display: flex;
		gap: var(--space-md);
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.difficulty {
		color: var(--color-warning);
	}

	.mastery-bar {
		height: 4px;
		background: var(--color-bg);
		border-radius: var(--radius-full);
		overflow: hidden;
		max-width: 150px;
	}

	.mastery-fill {
		height: 100%;
		border-radius: var(--radius-full);
	}

	.mastery-level {
		font-size: 0.6875rem;
		text-transform: capitalize;
	}

	.topic-details {
		margin-left: 56px;
		margin-top: var(--space-sm);
		padding: var(--space-md);
		background: var(--color-bg);
		border-radius: var(--radius-md);
		font-size: 0.8125rem;
	}

	.detail-row {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-xs);
	}

	.detail-row:last-child {
		margin-bottom: 0;
	}

	.detail-label {
		color: var(--color-text-subtle);
		min-width: 80px;
	}

	.modality-chips,
	.analogy-chips {
		display: flex;
		gap: var(--space-xs);
		flex-wrap: wrap;
	}

	.modality-chip,
	.analogy-chip {
		font-size: 0.6875rem;
		padding: 2px 6px;
		background: var(--color-bg-elevated);
		border-radius: var(--radius-sm);
		text-transform: capitalize;
	}

	.prereqs {
		color: var(--color-text-muted);
	}

	.legend {
		display: flex;
		gap: var(--space-lg);
		justify-content: center;
		flex-wrap: wrap;
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.legend-dot {
		width: 12px;
		height: 12px;
		border-radius: 50%;
		background: var(--color-bg-elevated);
		border: 2px solid var(--color-text-subtle);
	}

	.legend-dot.completed {
		background: var(--color-success);
		border-color: var(--color-success);
	}

	.legend-dot.in-progress {
		background: var(--color-primary);
		border-color: var(--color-primary);
	}

	.legend-dot.available {
		border-color: var(--color-text-subtle);
	}

	.legend-dot.locked {
		opacity: 0.5;
	}

	@media (max-width: 768px) {
		.path-header {
			flex-direction: column;
		}

		.path-progress {
			width: 100%;
		}
	}
</style>
