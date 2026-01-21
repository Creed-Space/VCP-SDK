<script lang="ts">
	import DemoContainer from '$lib/components/demo/DemoContainer.svelte';
	import type { RealityGrounding, GroundingType } from '$lib/vcp/interiora';

	// Example grounding scenarios
	let groundings = $state<RealityGrounding[]>([
		{
			claim: 'The user prefers visual learning based on their VCP profile',
			confidence: 0.95,
			grounding_type: 'factual',
			grounding_sources: [
				{ type: 'user_context', reference: 'VCP profile: learning_style=visual', confidence_contribution: 0.9 },
				{ type: 'reasoning_chain', reference: 'Explicitly stated preference', confidence_contribution: 0.05 }
			],
			uncertainty_markers: [],
			calibration_score: 0.98,
			should_verify: false
		},
		{
			claim: 'This tutorial would take approximately 30 minutes to complete',
			confidence: 0.7,
			grounding_type: 'inferential',
			grounding_sources: [
				{ type: 'knowledge_base', reference: 'Average completion times for similar content', confidence_contribution: 0.5 },
				{ type: 'reasoning_chain', reference: 'Adjusted for beginner skill level from VCP', confidence_contribution: 0.2 }
			],
			uncertainty_markers: ['varies by individual', 'depends on prior knowledge'],
			calibration_score: 0.65,
			should_verify: true
		},
		{
			claim: 'The recommended course aligns with the user\'s career goals',
			confidence: 0.85,
			grounding_type: 'inferential',
			grounding_sources: [
				{ type: 'user_context', reference: 'VCP profile: career_goal=senior_developer', confidence_contribution: 0.7 },
				{ type: 'knowledge_base', reference: 'Course metadata: targets senior roles', confidence_contribution: 0.15 }
			],
			uncertainty_markers: ['career goals may have changed'],
			calibration_score: 0.8,
			should_verify: false
		},
		{
			claim: 'This learning path is the optimal choice for the user',
			confidence: 0.55,
			grounding_type: 'subjective',
			grounding_sources: [
				{ type: 'reasoning_chain', reference: 'Matches stated preferences and constraints', confidence_contribution: 0.5 },
				{ type: 'user_context', reference: 'No explicit negative feedback on similar paths', confidence_contribution: 0.05 }
			],
			uncertainty_markers: ['subjective judgment', 'alternatives not fully explored', 'preferences may shift'],
			calibration_score: 0.5,
			should_verify: true
		},
		{
			claim: 'AI learning companions will become mainstream by 2028',
			confidence: 0.4,
			grounding_type: 'speculative',
			grounding_sources: [
				{ type: 'knowledge_base', reference: 'Industry trend analysis', confidence_contribution: 0.3 },
				{ type: 'reasoning_chain', reference: 'Extrapolation from current adoption rates', confidence_contribution: 0.1 }
			],
			uncertainty_markers: ['speculative', 'many external factors', 'technology evolution unpredictable'],
			should_verify: true
		}
	]);

	const groundingTypeInfo: Record<GroundingType, { icon: string; label: string; desc: string }> = {
		factual: { icon: '✓', label: 'Factual', desc: 'Verifiable fact from reliable source' },
		inferential: { icon: '→', label: 'Inferential', desc: 'Derived through reasoning from known facts' },
		subjective: { icon: '◐', label: 'Subjective', desc: 'Personal or experiential judgment' },
		normative: { icon: '⚖', label: 'Normative', desc: 'Value-based judgment' },
		speculative: { icon: '?', label: 'Speculative', desc: 'Hypothesis or prediction' }
	};

	function getConfidenceColor(confidence: number): string {
		if (confidence >= 0.8) return '#2ecc71';
		if (confidence >= 0.5) return '#f39c12';
		return '#e74c3c';
	}
</script>

<svelte:head>
	<title>Reality Grounding - VCP Self-Modeling</title>
	<meta
		name="description"
		content="See how AI systems ground claims in evidence and acknowledge uncertainty."
	/>
</svelte:head>

<DemoContainer
	title="Reality Grounding"
	description="How AI systems ground claims in evidence, distinguish claim types, and acknowledge uncertainty."
>
	{#snippet children()}
		<div class="grounding-layout">
			<!-- Claims List -->
			<div class="claims-section">
				{#each groundings as grounding, i}
					<div class="claim-card" class:should-verify={grounding.should_verify}>
						<div class="claim-header">
							<span
								class="grounding-type"
								title={groundingTypeInfo[grounding.grounding_type].desc}
							>
								<span class="type-icon">{groundingTypeInfo[grounding.grounding_type].icon}</span>
								{groundingTypeInfo[grounding.grounding_type].label}
							</span>
							<span
								class="claim-confidence"
								style="color: {getConfidenceColor(grounding.confidence)}"
							>
								{Math.round(grounding.confidence * 100)}%
							</span>
						</div>

						<div class="claim-text">"{grounding.claim}"</div>

						<!-- Confidence Bar -->
						<div class="confidence-bar">
							<div
								class="confidence-fill"
								style="width: {grounding.confidence * 100}%; background: {getConfidenceColor(grounding.confidence)}"
							></div>
						</div>

						<!-- Sources -->
						<div class="sources">
							<span class="sources-label">Grounded in:</span>
							{#each grounding.grounding_sources as source}
								<span class="source-chip" title={source.reference}>
									{source.type.replace(/_/g, ' ')}
									<span class="source-contrib">+{Math.round(source.confidence_contribution * 100)}%</span>
								</span>
							{/each}
						</div>

						<!-- Uncertainty Markers -->
						{#if grounding.uncertainty_markers.length > 0}
							<div class="uncertainty-markers">
								<span class="uncertainty-label">⚠️ Uncertainty:</span>
								{#each grounding.uncertainty_markers as marker}
									<span class="uncertainty-chip">{marker}</span>
								{/each}
							</div>
						{/if}

						<!-- Should Verify -->
						{#if grounding.should_verify}
							<div class="verify-notice">
								<span class="verify-icon">🔍</span>
								<span>This claim should be verified before acting on it</span>
							</div>
						{/if}

						<!-- Calibration -->
						{#if grounding.calibration_score !== undefined}
							<div class="calibration-mini">
								<span class="cal-label">Calibration:</span>
								<span
									class="cal-score"
									style="color: {getConfidenceColor(grounding.calibration_score)}"
								>
									{Math.round(grounding.calibration_score * 100)}%
								</span>
							</div>
						{/if}
					</div>
				{/each}
			</div>

			<!-- Legend & Explanation -->
			<div class="legend-section">
				<h3>Grounding Types</h3>
				<div class="legend-grid">
					{#each Object.entries(groundingTypeInfo) as [key, info]}
						<div class="legend-item">
							<span class="legend-icon">{info.icon}</span>
							<div>
								<strong>{info.label}</strong>
								<p>{info.desc}</p>
							</div>
						</div>
					{/each}
				</div>

				<h3>Why Reality Grounding Matters</h3>
				<div class="explanation">
					<p>
						AI systems can produce confident-sounding outputs that are poorly grounded in reality.
						VCP's reality grounding framework makes the epistemic status of claims explicit:
					</p>
					<ul>
						<li><strong>Claim type</strong> — Is this a fact, inference, judgment, or speculation?</li>
						<li><strong>Sources</strong> — What evidence supports this claim?</li>
						<li><strong>Confidence</strong> — How certain should the system be?</li>
						<li><strong>Uncertainty markers</strong> — What could invalidate this claim?</li>
						<li><strong>Verification flag</strong> — Should a human verify before acting?</li>
					</ul>
					<p class="key-insight">
						<strong>Key Insight:</strong> Claims with high confidence but poor calibration scores
						indicate the system may be overconfident. Claims with uncertainty markers and
						should_verify=true are explicitly flagged as needing external validation.
					</p>
				</div>

				<div class="confidence-legend">
					<h4>Confidence Interpretation</h4>
					<div class="conf-scale">
						<div class="conf-item high">
							<span class="conf-dot"></span>
							<span>80%+ High confidence</span>
						</div>
						<div class="conf-item mid">
							<span class="conf-dot"></span>
							<span>50-79% Moderate confidence</span>
						</div>
						<div class="conf-item low">
							<span class="conf-dot"></span>
							<span>&lt;50% Low confidence</span>
						</div>
					</div>
				</div>
			</div>
		</div>
	{/snippet}
</DemoContainer>

<style>
	.grounding-layout {
		display: grid;
		grid-template-columns: 1.5fr 1fr;
		gap: var(--space-xl);
	}

	.claims-section {
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
	}

	.claim-card {
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.claim-card.should-verify {
		border-color: var(--color-warning);
	}

	.claim-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--space-sm);
	}

	.grounding-type {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		font-size: 0.75rem;
		padding: 2px 8px;
		background: var(--color-bg-elevated);
		border-radius: var(--radius-sm);
		color: var(--color-text-muted);
	}

	.type-icon {
		font-size: 0.875rem;
	}

	.claim-confidence {
		font-family: var(--font-mono);
		font-weight: 700;
		font-size: 1.125rem;
	}

	.claim-text {
		font-size: 1rem;
		line-height: 1.5;
		margin-bottom: var(--space-md);
		font-style: italic;
	}

	.confidence-bar {
		height: 6px;
		background: var(--color-bg-elevated);
		border-radius: var(--radius-full);
		overflow: hidden;
		margin-bottom: var(--space-md);
	}

	.confidence-fill {
		height: 100%;
		border-radius: var(--radius-full);
		transition: width var(--transition-normal);
	}

	.sources {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: var(--space-xs);
		margin-bottom: var(--space-sm);
	}

	.sources-label {
		font-size: 0.75rem;
		color: var(--color-text-subtle);
	}

	.source-chip {
		display: flex;
		align-items: center;
		gap: 4px;
		font-size: 0.6875rem;
		padding: 2px 8px;
		background: var(--color-success-muted);
		color: var(--color-success);
		border-radius: var(--radius-sm);
		text-transform: capitalize;
	}

	.source-contrib {
		opacity: 0.7;
	}

	.uncertainty-markers {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: var(--space-xs);
		margin-bottom: var(--space-sm);
	}

	.uncertainty-label {
		font-size: 0.75rem;
		color: var(--color-warning);
	}

	.uncertainty-chip {
		font-size: 0.6875rem;
		padding: 2px 8px;
		background: var(--color-warning-muted);
		color: var(--color-warning);
		border-radius: var(--radius-sm);
	}

	.verify-notice {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-sm);
		background: var(--color-warning-muted);
		border-radius: var(--radius-sm);
		font-size: 0.8125rem;
		color: var(--color-warning);
		margin-bottom: var(--space-sm);
	}

	.calibration-mini {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-size: 0.75rem;
	}

	.cal-label {
		color: var(--color-text-subtle);
	}

	.cal-score {
		font-family: var(--font-mono);
		font-weight: 600;
	}

	.legend-section {
		display: flex;
		flex-direction: column;
		gap: var(--space-lg);
	}

	.legend-section h3 {
		font-size: 1rem;
		margin-bottom: var(--space-sm);
	}

	.legend-grid {
		display: flex;
		flex-direction: column;
		gap: var(--space-sm);
	}

	.legend-item {
		display: flex;
		gap: var(--space-md);
		padding: var(--space-sm);
		background: var(--color-bg-card);
		border-radius: var(--radius-md);
	}

	.legend-icon {
		font-size: 1.25rem;
		width: 32px;
		text-align: center;
	}

	.legend-item strong {
		font-size: 0.875rem;
	}

	.legend-item p {
		font-size: 0.75rem;
		color: var(--color-text-muted);
		margin: 0;
	}

	.explanation {
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		font-size: 0.875rem;
		line-height: 1.6;
	}

	.explanation ul {
		padding-left: var(--space-lg);
		margin: var(--space-md) 0;
	}

	.explanation li {
		margin-bottom: var(--space-xs);
	}

	.key-insight {
		padding: var(--space-md);
		background: var(--color-primary-muted);
		border-radius: var(--radius-md);
		margin: 0;
	}

	.confidence-legend {
		padding: var(--space-md);
		background: var(--color-bg-card);
		border-radius: var(--radius-md);
	}

	.confidence-legend h4 {
		font-size: 0.875rem;
		margin-bottom: var(--space-sm);
	}

	.conf-scale {
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
	}

	.conf-item {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-size: 0.8125rem;
	}

	.conf-dot {
		width: 12px;
		height: 12px;
		border-radius: 50%;
	}

	.conf-item.high .conf-dot {
		background: #2ecc71;
	}

	.conf-item.mid .conf-dot {
		background: #f39c12;
	}

	.conf-item.low .conf-dot {
		background: #e74c3c;
	}

	@media (max-width: 1024px) {
		.grounding-layout {
			grid-template-columns: 1fr;
		}
	}
</style>
