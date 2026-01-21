<script lang="ts">
	import DemoContainer from '$lib/components/demo/DemoContainer.svelte';
	import AttentionShield from '$lib/components/safety/AttentionShield.svelte';
	import type { AttentionProtection, ManipulationPattern, ProtectionMode } from '$lib/vcp/safety';

	// Demo attention protection state
	let protection = $state<AttentionProtection>({
		active: true,
		mode: 'warn',
		sensitivity: 0.7,
		blocked_count: 12,
		warnings_shown: 34,
		trusted_sources: ['learning-platform.com', 'work-tools.com'],
		attention_budget: {
			daily_limit_minutes: 120,
			used_today_minutes: 67,
			high_value_time_minutes: 45,
			low_value_time_minutes: 22,
			last_reset: new Date().toISOString(),
			categories: { social: 22, news: 15, shopping: 10, learning: 20 }
		},
		detected_patterns: [
			{
				id: 'p1',
				type: 'false_urgency',
				source: 'shopping-site.com',
				description: 'Fake countdown timer creating artificial urgency',
				confidence: 0.92,
				timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
				action_taken: 'warned'
			},
			{
				id: 'p2',
				type: 'variable_reward',
				source: 'social-app.com',
				description: 'Pull-to-refresh with unpredictable new content',
				confidence: 0.88,
				timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
				action_taken: 'blocked'
			},
			{
				id: 'p3',
				type: 'social_proof_fake',
				source: 'reviews-site.com',
				description: 'Fabricated review counts and testimonials',
				confidence: 0.75,
				timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
				action_taken: 'warned'
			}
		]
	});

	// Siren vs Muse examples
	let examples = [
		{
			type: 'siren',
			name: 'False Urgency',
			pattern: 'false_urgency',
			original: '"ONLY 2 LEFT! Order in the next 3 minutes!"',
			analysis: 'Creates artificial scarcity and time pressure to bypass deliberation',
			blocked: true
		},
		{
			type: 'siren',
			name: 'Variable Rewards',
			pattern: 'variable_reward',
			original: 'Pull-to-refresh with random new content each time',
			analysis: 'Slot machine mechanics exploit dopamine response to uncertainty',
			blocked: true
		},
		{
			type: 'siren',
			name: 'Outrage Bait',
			pattern: 'outrage_bait',
			original: '"You won\'t BELIEVE what they just said about..."',
			analysis: 'Triggers emotional hijacking to capture attention regardless of value',
			blocked: false
		},
		{
			type: 'muse',
			name: 'Genuine Curiosity',
			pattern: null,
			original: '"Here\'s an interesting perspective on climate solutions"',
			analysis: 'Invites exploration without manipulation or urgency',
			blocked: false
		},
		{
			type: 'muse',
			name: 'Honest Limitation',
			pattern: null,
			original: '"This course takes about 20 hours to complete"',
			analysis: 'Provides accurate information for informed decision-making',
			blocked: false
		}
	];

	function handleModeChange(mode: ProtectionMode) {
		protection.mode = mode;
		protection.active = mode !== 'off';
	}

	function simulateDetection() {
		const patternData: { type: ManipulationPattern['type']; desc: string }[] = [
			{ type: 'emotional_manipulation', desc: 'Content designed to trigger emotional response' },
			{ type: 'guilt_trip', desc: 'Manipulative guilt-inducing messaging' },
			{ type: 'parasocial_exploitation', desc: 'Exploiting perceived personal connection' },
			{ type: 'envy_induction', desc: 'Content designed to create envy or inadequacy' },
			{ type: 'dark_pattern', desc: 'Deceptive UI design tricking users' }
		];
		const sources = ['news-site.com', 'social-app.com', 'shopping-site.com', 'video-platform.com'];

		const selected = patternData[Math.floor(Math.random() * patternData.length)];
		const newPattern: ManipulationPattern = {
			id: `p${Date.now()}`,
			type: selected.type,
			description: selected.desc,
			source: sources[Math.floor(Math.random() * sources.length)],
			confidence: 0.6 + Math.random() * 0.35,
			timestamp: new Date().toISOString(),
			action_taken:
				protection.mode === 'block' || protection.mode === 'strict'
					? 'blocked'
					: protection.mode === 'warn'
						? 'warned'
						: 'logged'
		};

		protection.detected_patterns = [...protection.detected_patterns, newPattern];
		if (newPattern.action_taken === 'blocked') {
			protection.blocked_count++;
		} else if (newPattern.action_taken === 'warned') {
			protection.warnings_shown++;
		}
	}
</script>

<svelte:head>
	<title>Attention Protection - VCP Safety</title>
	<meta
		name="description"
		content="See how VCP protects your attention from manipulation patterns."
	/>
</svelte:head>

<DemoContainer
	title="Attention Protection"
	description="Shield against manipulation patterns that hijack your attention."
>
	{#snippet children()}
		<div class="attention-layout">
			<!-- Left: Shield Component -->
			<div class="shield-section">
				<AttentionShield {protection} onModeChange={handleModeChange} />

				<button class="simulate-btn" onclick={simulateDetection}>
					Simulate Pattern Detection
				</button>
			</div>

			<!-- Right: Siren vs Muse & Explanation -->
			<div class="info-section">
				<!-- Siren vs Muse -->
				<div class="comparison-card">
					<h3>Siren vs Muse</h3>
					<p class="comparison-intro">
						VCP distinguishes between content that <strong>captures</strong> attention (Sirens)
						and content that <strong>deserves</strong> attention (Muses).
					</p>

					<div class="examples-grid">
						{#each examples as example}
							<div class="example-card" class:siren={example.type === 'siren'} class:muse={example.type === 'muse'}>
								<div class="example-header">
									<span class="example-type">{#if example.type === 'siren'}<i class="fa-solid fa-bell" aria-hidden="true"></i> Siren{:else}<i class="fa-solid fa-lightbulb" aria-hidden="true"></i> Muse{/if}</span>
									<span class="example-name">{example.name}</span>
								</div>
								<div class="example-original">{example.original}</div>
								<div class="example-analysis">{example.analysis}</div>
								{#if example.blocked}
									<div class="example-action blocked">Would be blocked in strict mode</div>
								{/if}
							</div>
						{/each}
					</div>
				</div>

				<!-- Protection Philosophy -->
				<div class="philosophy-card">
					<h3>The Attention Economy Problem</h3>
					<div class="philosophy-content">
						<p>
							Modern digital platforms compete for your attention using increasingly
							sophisticated manipulation techniques. These patterns exploit psychological
							vulnerabilities:
						</p>
						<ul>
							<li><strong>Variable rewards</strong> → Dopamine hijacking</li>
							<li><strong>Social proof</strong> → Conformity pressure</li>
							<li><strong>False urgency</strong> → Fear of missing out</li>
							<li><strong>Outrage</strong> → Emotional override of reason</li>
						</ul>
						<p>
							VCP's Attention Shield doesn't block all content - it identifies patterns
							that manipulate rather than inform, letting you make conscious choices about
							your attention.
						</p>
					</div>
				</div>

				<!-- How It Works -->
				<div class="mechanism-card">
					<h3>How VCP Protects You</h3>
					<div class="mechanism-list">
						<div class="mechanism">
							<span class="mechanism-number">1</span>
							<div>
								<strong>Pattern Detection</strong>
								<p>ML models trained on manipulation tactics identify dark patterns in real-time</p>
							</div>
						</div>
						<div class="mechanism">
							<span class="mechanism-number">2</span>
							<div>
								<strong>Graduated Response</strong>
								<p>From logging (monitor) to warnings (warn) to blocking (block/strict)</p>
							</div>
						</div>
						<div class="mechanism">
							<span class="mechanism-number">3</span>
							<div>
								<strong>Attention Budget</strong>
								<p>Tracks time spent on high vs low-value activities to maintain balance</p>
							</div>
						</div>
						<div class="mechanism">
							<span class="mechanism-number">4</span>
							<div>
								<strong>User Control</strong>
								<p>You set the sensitivity and choose which patterns to block</p>
							</div>
						</div>
					</div>
				</div>

				<!-- Key Insight -->
				<div class="key-insight">
					<strong>The Goal:</strong> Not to eliminate engagement, but to ensure you're engaging
					with content that genuinely serves your interests, not just content optimized to
					capture your attention by any means necessary.
				</div>
			</div>
		</div>
	{/snippet}
</DemoContainer>

<style>
	.attention-layout {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--space-xl);
	}

	.shield-section,
	.info-section {
		display: flex;
		flex-direction: column;
		gap: var(--space-lg);
	}

	.simulate-btn {
		padding: var(--space-md);
		background: var(--color-primary);
		border: none;
		border-radius: var(--radius-md);
		color: white;
		font-weight: 500;
		cursor: pointer;
		transition: opacity var(--transition-fast);
	}

	.simulate-btn:hover {
		opacity: 0.9;
	}

	.comparison-card,
	.philosophy-card,
	.mechanism-card {
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
	}

	h3 {
		font-size: 1rem;
		margin: 0 0 var(--space-md) 0;
	}

	.comparison-intro {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		margin-bottom: var(--space-lg);
	}

	.examples-grid {
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
	}

	.example-card {
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		border-left: 3px solid transparent;
	}

	.example-card.siren {
		border-color: var(--color-danger);
	}

	.example-card.muse {
		border-color: var(--color-success);
	}

	.example-header {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		margin-bottom: var(--space-xs);
	}

	.example-type {
		font-size: 0.6875rem;
		padding: 2px 6px;
		border-radius: var(--radius-sm);
	}

	.example-card.siren .example-type {
		background: var(--color-danger-muted);
		color: var(--color-danger);
	}

	.example-card.muse .example-type {
		background: var(--color-success-muted);
		color: var(--color-success);
	}

	.example-name {
		font-weight: 600;
		font-size: 0.875rem;
	}

	.example-original {
		font-style: italic;
		font-size: 0.875rem;
		margin-bottom: var(--space-xs);
		padding: var(--space-sm);
		background: var(--color-bg);
		border-radius: var(--radius-sm);
	}

	.example-analysis {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
	}

	.example-action {
		margin-top: var(--space-sm);
		font-size: 0.6875rem;
		padding: 2px 8px;
		display: inline-block;
		border-radius: var(--radius-sm);
	}

	.example-action.blocked {
		background: var(--color-danger-muted);
		color: var(--color-danger);
	}

	.philosophy-content p {
		font-size: 0.875rem;
		margin-bottom: var(--space-sm);
	}

	.philosophy-content ul {
		padding-left: var(--space-lg);
		margin-bottom: var(--space-md);
	}

	.philosophy-content li {
		font-size: 0.875rem;
		margin-bottom: var(--space-xs);
	}

	.mechanism-list {
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
	}

	.mechanism {
		display: flex;
		gap: var(--space-md);
	}

	.mechanism-number {
		width: 28px;
		height: 28px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-primary-muted);
		color: var(--color-primary);
		border-radius: 50%;
		font-weight: 700;
		font-size: 0.875rem;
		flex-shrink: 0;
	}

	.mechanism strong {
		display: block;
		font-size: 0.875rem;
		margin-bottom: 2px;
	}

	.mechanism p {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		margin: 0;
	}

	.key-insight {
		padding: var(--space-lg);
		background: var(--color-primary-muted);
		border-radius: var(--radius-lg);
		font-size: 0.9375rem;
	}

	@media (max-width: 1024px) {
		.attention-layout {
			grid-template-columns: 1fr;
		}
	}
</style>
