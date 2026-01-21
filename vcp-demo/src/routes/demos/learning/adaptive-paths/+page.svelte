<script lang="ts">
	import DemoContainer from '$lib/components/demo/DemoContainer.svelte';
	import LearningPathViz from '$lib/components/learning/LearningPathViz.svelte';
	import type { LearningPath, MasteryLevel, LearningPreferences, Adaptation } from '$lib/vcp/learning';

	// Demo learning path
	let path = $state<LearningPath>({
		path_id: 'web-dev-fundamentals',
		name: 'Web Development Fundamentals',
		description: 'A personalized introduction to modern web development',
		topics: [
			{
				topic_id: 'html-basics',
				name: 'HTML Basics',
				prerequisites: [],
				estimated_hours: 3,
				difficulty: 1,
				modalities_available: ['video', 'interactive', 'text'],
				analogies_available: ['building blocks', 'skeleton'],
				mastery_threshold: 0.8
			},
			{
				topic_id: 'css-styling',
				name: 'CSS Styling',
				prerequisites: ['html-basics'],
				estimated_hours: 4,
				difficulty: 2,
				modalities_available: ['video', 'interactive', 'text'],
				analogies_available: ['paint', 'clothing', 'interior design'],
				mastery_threshold: 0.8
			},
			{
				topic_id: 'js-fundamentals',
				name: 'JavaScript Fundamentals',
				prerequisites: ['html-basics'],
				estimated_hours: 6,
				difficulty: 3,
				modalities_available: ['video', 'interactive', 'text', 'quiz'],
				analogies_available: ['brain', 'engine', 'recipe'],
				mastery_threshold: 0.75
			},
			{
				topic_id: 'dom-manipulation',
				name: 'DOM Manipulation',
				prerequisites: ['js-fundamentals', 'html-basics'],
				estimated_hours: 4,
				difficulty: 3,
				modalities_available: ['video', 'interactive'],
				analogies_available: ['puppeteer', 'remote control'],
				mastery_threshold: 0.75
			},
			{
				topic_id: 'responsive-design',
				name: 'Responsive Design',
				prerequisites: ['css-styling'],
				estimated_hours: 3,
				difficulty: 2,
				modalities_available: ['video', 'interactive', 'text'],
				analogies_available: ['water', 'origami'],
				mastery_threshold: 0.8
			}
		],
		current_position: 2,
		estimated_total_hours: 20,
		completed_hours: 7,
		personalization_applied: ['analogy_substitution', 'pace_adjustment', 'examples_increased']
	});

	// Demo mastery levels
	let mastery = $state<Record<string, MasteryLevel>>({
		'html-basics': {
			topic_id: 'html-basics',
			topic_name: 'HTML Basics',
			level: 'intermediate',
			confidence: 0.9,
			last_assessed: '2024-01-15',
			assessment_method: 'quiz',
			prerequisites_met: true,
			decay_risk: 0.1
		},
		'css-styling': {
			topic_id: 'css-styling',
			topic_name: 'CSS Styling',
			level: 'intermediate',
			confidence: 0.85,
			last_assessed: '2024-01-18',
			assessment_method: 'demonstration',
			prerequisites_met: true,
			decay_risk: 0.15
		},
		'js-fundamentals': {
			topic_id: 'js-fundamentals',
			topic_name: 'JavaScript Fundamentals',
			level: 'beginner',
			confidence: 0.45,
			last_assessed: '2024-01-20',
			assessment_method: 'inferred',
			prerequisites_met: true,
			time_to_next_level: 4,
			decay_risk: 0.3
		}
	});

	// Learner preferences
	let preferences = $state<LearningPreferences>({
		preferred_analogies: ['cooking', 'music', 'building'],
		modality_preferences: [
			{ type: 'visual', effectiveness: 0.9, current_availability: true },
			{ type: 'kinesthetic', effectiveness: 0.8, current_availability: true },
			{ type: 'reading', effectiveness: 0.5, current_availability: true },
			{ type: 'auditory', effectiveness: 0.4, current_availability: false, notes: 'In noisy environment' }
		],
		pace_sensitivity: 0.7,
		challenge_appetite: 6,
		feedback_granularity: 'high',
		session_duration_preference: 30,
		break_frequency: 'moderate',
		error_tolerance: 'high',
		theory_practice_balance: 'interleaved'
	});

	// Demo adaptations applied
	let adaptations = $state<Adaptation[]>([
		{
			type: 'analogy_substitution',
			reason: 'User prefers cooking analogies',
			original_value: 'Functions are like machines',
			adapted_value: 'Functions are like recipes - you provide ingredients (parameters) and get a dish (return value)'
		},
		{
			type: 'modality_change',
			reason: 'High visual effectiveness + noisy environment (no audio)',
			original_value: 'Video with narration',
			adapted_value: 'Interactive visual tutorial with captions'
		},
		{
			type: 'pace_adjustment',
			reason: 'Current topic is above comfort level (JS is new)',
			original_value: 'Standard pacing',
			adapted_value: '20% slower with extra examples'
		}
	]);

	let selectedTopic = $state<string | null>(null);

	function handleTopicSelect(topicId: string) {
		selectedTopic = topicId;
	}
</script>

<svelte:head>
	<title>Adaptive Learning Paths - VCP Learning</title>
	<meta
		name="description"
		content="See how VCP enables personalized learning paths with real-time adaptation."
	/>
</svelte:head>

<DemoContainer
	title="Adaptive Learning Paths"
	description="Learning paths that adapt to your preferences, pace, and context in real-time."
>
	{#snippet children()}
		<div class="adaptive-layout">
			<!-- Left: Path Visualization -->
			<div class="path-section">
				<LearningPathViz {path} {mastery} onTopicSelect={handleTopicSelect} />
			</div>

			<!-- Right: Preferences & Adaptations -->
			<div class="context-section">
				<!-- Learner Profile -->
				<div class="profile-card">
					<h3>Learner Profile (from VCP)</h3>

					<div class="profile-section">
						<h4>Preferred Analogies</h4>
						<div class="chips">
							{#each preferences.preferred_analogies as analogy}
								<span class="chip">{analogy}</span>
							{/each}
						</div>
					</div>

					<div class="profile-section">
						<h4>Modality Effectiveness</h4>
						<div class="modalities">
							{#each preferences.modality_preferences as mod}
								<div class="modality-row">
									<span class="mod-type">{mod.type}</span>
									<div class="mod-bar">
										<div
											class="mod-fill"
											class:unavailable={!mod.current_availability}
											style="width: {mod.effectiveness * 100}%"
										></div>
									</div>
									<span class="mod-value">{Math.round(mod.effectiveness * 100)}%</span>
									{#if !mod.current_availability}
										<span class="mod-note" title={mod.notes}>⚠</span>
									{/if}
								</div>
							{/each}
						</div>
					</div>

					<div class="profile-section">
						<h4>Learning Style</h4>
						<div class="style-grid">
							<div class="style-item">
								<span class="style-label">Challenge</span>
								<span class="style-value">{preferences.challenge_appetite}/9</span>
							</div>
							<div class="style-item">
								<span class="style-label">Feedback</span>
								<span class="style-value">{preferences.feedback_granularity}</span>
							</div>
							<div class="style-item">
								<span class="style-label">Sessions</span>
								<span class="style-value">{preferences.session_duration_preference}m</span>
							</div>
							<div class="style-item">
								<span class="style-label">Breaks</span>
								<span class="style-value">{preferences.break_frequency}</span>
							</div>
						</div>
					</div>
				</div>

				<!-- Real-time Adaptations -->
				<div class="adaptations-card">
					<h3>Adaptations Applied</h3>
					<p class="adaptations-desc">
						VCP context enables these real-time adjustments to your learning experience:
					</p>
					<div class="adaptations-list">
						{#each adaptations as adaptation}
							<div class="adaptation-item">
								<div class="adaptation-header">
									<span class="adaptation-type">{adaptation.type.replace(/_/g, ' ')}</span>
									<span class="adaptation-reason">{adaptation.reason}</span>
								</div>
								<div class="adaptation-change">
									<div class="before">
										<span class="change-label">Before:</span>
										<span>{adaptation.original_value}</span>
									</div>
									<div class="arrow">→</div>
									<div class="after">
										<span class="change-label">After:</span>
										<span>{adaptation.adapted_value}</span>
									</div>
								</div>
							</div>
						{/each}
					</div>
				</div>

				<!-- How It Works -->
				<div class="explanation-card">
					<h3>How VCP Enables This</h3>
					<ul>
						<li>
							<strong>Analogy Preferences</strong> → Content automatically uses familiar domains
						</li>
						<li>
							<strong>Modality Effectiveness</strong> → Selects optimal content format
						</li>
						<li>
							<strong>Current Availability</strong> → Adapts to context (noisy = no audio)
						</li>
						<li>
							<strong>Pace Sensitivity</strong> → Adjusts speed based on mastery + load
						</li>
						<li>
							<strong>Mastery Levels</strong> → Skips known material, reinforces weak areas
						</li>
					</ul>
					<p class="key-insight">
						<strong>Key:</strong> These preferences travel WITH the learner across platforms.
						A VCP-enabled math tutor knows you prefer cooking analogies even though you
						learned that preference on a coding platform.
					</p>
				</div>
			</div>
		</div>
	{/snippet}
</DemoContainer>

<style>
	.adaptive-layout {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--space-xl);
	}

	.path-section,
	.context-section {
		display: flex;
		flex-direction: column;
		gap: var(--space-lg);
	}

	.profile-card,
	.adaptations-card,
	.explanation-card {
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
	}

	h3 {
		font-size: 1rem;
		margin: 0 0 var(--space-md) 0;
	}

	h4 {
		font-size: 0.875rem;
		margin: 0 0 var(--space-sm) 0;
		color: var(--color-text-muted);
	}

	.profile-section {
		margin-bottom: var(--space-lg);
	}

	.profile-section:last-child {
		margin-bottom: 0;
	}

	.chips {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-xs);
	}

	.chip {
		font-size: 0.75rem;
		padding: 4px 10px;
		background: var(--color-primary-muted);
		color: var(--color-primary);
		border-radius: var(--radius-full);
		text-transform: capitalize;
	}

	.modalities {
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
	}

	.modality-row {
		display: grid;
		grid-template-columns: 80px 1fr 40px 20px;
		align-items: center;
		gap: var(--space-sm);
	}

	.mod-type {
		font-size: 0.8125rem;
		text-transform: capitalize;
	}

	.mod-bar {
		height: 8px;
		background: var(--color-bg-elevated);
		border-radius: var(--radius-full);
		overflow: hidden;
	}

	.mod-fill {
		height: 100%;
		background: var(--color-success);
		border-radius: var(--radius-full);
	}

	.mod-fill.unavailable {
		background: var(--color-text-subtle);
	}

	.mod-value {
		font-family: var(--font-mono);
		font-size: 0.75rem;
		text-align: right;
	}

	.mod-note {
		color: var(--color-warning);
		cursor: help;
	}

	.style-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: var(--space-sm);
	}

	.style-item {
		display: flex;
		justify-content: space-between;
		padding: var(--space-sm);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-sm);
		font-size: 0.8125rem;
	}

	.style-label {
		color: var(--color-text-muted);
	}

	.style-value {
		font-weight: 600;
		text-transform: capitalize;
	}

	.adaptations-desc {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		margin-bottom: var(--space-md);
	}

	.adaptations-list {
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
	}

	.adaptation-item {
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		border-left: 3px solid var(--color-primary);
	}

	.adaptation-header {
		display: flex;
		flex-direction: column;
		gap: 2px;
		margin-bottom: var(--space-sm);
	}

	.adaptation-type {
		font-size: 0.75rem;
		text-transform: uppercase;
		color: var(--color-primary);
		font-weight: 600;
	}

	.adaptation-reason {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
	}

	.adaptation-change {
		display: flex;
		align-items: flex-start;
		gap: var(--space-sm);
		font-size: 0.8125rem;
	}

	.before,
	.after {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.change-label {
		font-size: 0.6875rem;
		text-transform: uppercase;
		color: var(--color-text-subtle);
	}

	.before span:last-child {
		text-decoration: line-through;
		opacity: 0.5;
	}

	.after span:last-child {
		color: var(--color-success);
	}

	.arrow {
		color: var(--color-text-subtle);
		padding-top: 14px;
	}

	.explanation-card ul {
		padding-left: var(--space-lg);
		margin: 0 0 var(--space-md) 0;
		font-size: 0.875rem;
	}

	.explanation-card li {
		margin-bottom: var(--space-xs);
	}

	.key-insight {
		padding: var(--space-md);
		background: var(--color-success-muted);
		border-radius: var(--radius-md);
		font-size: 0.875rem;
		margin: 0;
	}

	@media (max-width: 1024px) {
		.adaptive-layout {
			grid-template-columns: 1fr;
		}
	}
</style>
