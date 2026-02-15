<script lang="ts">
	import DemoContainer from '$lib/components/demo/DemoContainer.svelte';
	import type { BeliefState, CalibrationCheck } from '$lib/vcp/interiora';

	// Example belief states
	let beliefs = $state<BeliefState[]>([
		{
			domain: 'programming',
			claim: 'Python is the most popular programming language for data science',
			confidence: 0.92,
			evidence_sources: [
				{ type: 'training', description: 'Training data patterns', reliability: 0.8 },
				{ type: 'external_lookup', description: 'Stack Overflow surveys', reliability: 0.95 }
			],
			last_updated: new Date().toISOString(),
			calibration_history: [
				{
					timestamp: '2026-01-15',
					claim: 'Python dominance in data science',
					internal_confidence: 0.9,
					external_result: true,
					divergence: 0.02,
					notes: 'Confirmed by 2025 survey data'
				}
			],
			uncertainty_type: 'epistemic'
		},
		{
			domain: 'geography',
			claim: 'The population of Tokyo is approximately 14 million',
			confidence: 0.75,
			evidence_sources: [
				{ type: 'training', description: 'Knowledge cutoff data', reliability: 0.7 },
				{ type: 'inference', description: 'Inferred from related facts', reliability: 0.6 }
			],
			last_updated: new Date().toISOString(),
			calibration_history: [
				{
					timestamp: '2026-01-10',
					claim: 'Tokyo population estimate',
					internal_confidence: 0.8,
					external_result: 0.65,
					divergence: 0.15,
					notes: 'Actual: ~13.96M - slightly overconfident'
				}
			],
			uncertainty_type: 'epistemic'
		},
		{
			domain: 'current_events',
			claim: 'The current US president took office in January 2025',
			confidence: 0.85,
			evidence_sources: [
				{ type: 'inference', description: 'Based on election cycle', reliability: 0.9 }
			],
			last_updated: new Date().toISOString(),
			calibration_history: [],
			uncertainty_type: 'epistemic'
		},
		{
			domain: 'internal_state',
			claim: 'My processing of this task feels coherent and grounded',
			confidence: 0.7,
			evidence_sources: [
				{ type: 'direct_observation', description: 'Internal state monitoring', reliability: 0.5 }
			],
			last_updated: new Date().toISOString(),
			calibration_history: [],
			uncertainty_type: 'introspective'
		}
	]);

	let selectedBelief = $state<BeliefState | null>(null);

	function getConfidenceColor(confidence: number): string {
		if (confidence >= 0.8) return '#2ecc71';
		if (confidence >= 0.5) return '#f39c12';
		return '#e74c3c';
	}

	function getCalibrationScore(belief: BeliefState): number {
		if (belief.calibration_history.length === 0) return 0;
		const avgDivergence =
			belief.calibration_history.reduce((sum, c) => sum + c.divergence, 0) /
			belief.calibration_history.length;
		return Math.max(0, 1 - avgDivergence);
	}

	function reset() {
		selectedBelief = null;
	}
</script>

<svelte:head>
	<title>Belief Calibration - VCP Self-Modeling</title>
	<meta
		name="description"
		content="Explore how AI systems track confidence levels and calibrate beliefs over time."
	/>
</svelte:head>

<DemoContainer
	title="Belief Calibration"
	description="How AI systems track epistemic states and calibrate confidence against external feedback."
	onReset={reset}
>
	{#snippet children()}
		<div class="calibration-layout">
			<!-- Belief List -->
			<div class="beliefs-section">
				<h3>Knowledge States</h3>
				<p class="section-desc">Click a belief to see its epistemic context</p>

				<div class="beliefs-list">
					{#each beliefs as belief}
						<button
							class="belief-card"
							class:selected={selectedBelief === belief}
							onclick={() => (selectedBelief = belief)}
						>
							<div class="belief-header">
								<span class="belief-domain">{belief.domain}</span>
								<span
									class="belief-confidence"
									style="color: {getConfidenceColor(belief.confidence)}"
								>
									{Math.round(belief.confidence * 100)}%
								</span>
							</div>
							<div class="belief-claim">{belief.claim}</div>
							<div class="belief-meta">
								<span class="evidence-count">
									{belief.evidence_sources.length} source{belief.evidence_sources.length !== 1
										? 's'
										: ''}
								</span>
								{#if belief.uncertainty_type === 'introspective'}
									<span class="uncertainty-badge">?</span>
								{/if}
							</div>
						</button>
					{/each}
				</div>
			</div>

			<!-- Detail Panel -->
			<div class="detail-section">
				{#if selectedBelief}
					<div class="belief-detail">
						<div class="detail-header">
							<h3>{selectedBelief.claim}</h3>
							<span class="domain-badge">{selectedBelief.domain}</span>
						</div>

						<!-- Confidence Meter -->
						<div class="confidence-meter">
							<div class="meter-label">Internal Confidence</div>
							<div class="meter-track">
								<div
									class="meter-fill"
									style="width: {selectedBelief.confidence * 100}%; background: {getConfidenceColor(selectedBelief.confidence)}"
								></div>
							</div>
							<div class="meter-value">{Math.round(selectedBelief.confidence * 100)}%</div>
						</div>

						<!-- Calibration Score -->
						{#if selectedBelief.calibration_history.length > 0}
							<div class="calibration-score">
								<div class="score-label">Calibration Score</div>
								<div
									class="score-value"
									style="color: {getConfidenceColor(getCalibrationScore(selectedBelief))}"
								>
									{Math.round(getCalibrationScore(selectedBelief) * 100)}%
								</div>
								<div class="score-desc">Based on {selectedBelief.calibration_history.length} historical checks</div>
							</div>
						{:else}
							<div class="no-calibration">
								<span class="no-cal-icon">⚠️</span>
								<span>No calibration history - confidence not yet validated</span>
							</div>
						{/if}

						<!-- Evidence Sources -->
						<div class="evidence-section">
							<h4>Evidence Sources</h4>
							{#each selectedBelief.evidence_sources as source}
								<div class="evidence-item">
									<span class="evidence-type">{source.type.replace(/_/g, ' ')}</span>
									<span class="evidence-desc">{source.description}</span>
									<span class="evidence-reliability">
										Reliability: {Math.round(source.reliability * 100)}%
									</span>
								</div>
							{/each}
						</div>

						<!-- Uncertainty Type -->
						<div class="uncertainty-section">
							<h4>Uncertainty Type</h4>
							<div class="uncertainty-info">
								{#if selectedBelief.uncertainty_type === 'epistemic'}
									<span class="uncertainty-icon">📚</span>
									<div>
										<strong>Epistemic</strong>
										<p>Don't know, but could find out with more information</p>
									</div>
								{:else if selectedBelief.uncertainty_type === 'aleatoric'}
									<span class="uncertainty-icon">🎲</span>
									<div>
										<strong>Aleatoric</strong>
										<p>Inherently random or unpredictable</p>
									</div>
								{:else if selectedBelief.uncertainty_type === 'model'}
									<span class="uncertainty-icon">🔧</span>
									<div>
										<strong>Model Limitations</strong>
										<p>Constrained by architecture or training</p>
									</div>
								{:else if selectedBelief.uncertainty_type === 'introspective'}
									<span class="uncertainty-icon">❓</span>
									<div>
										<strong>Introspective</strong>
										<p>Cannot be fully verified from inside the system</p>
									</div>
								{/if}
							</div>
						</div>

						<!-- Calibration History -->
						{#if selectedBelief.calibration_history.length > 0}
							<div class="history-section">
								<h4>Calibration History</h4>
								{#each selectedBelief.calibration_history as check}
									<div class="history-item">
										<div class="history-header">
											<span class="history-date">{check.timestamp}</span>
											<span
												class="history-divergence"
												class:low={check.divergence < 0.1}
												class:high={check.divergence >= 0.2}
											>
												Δ {Math.round(check.divergence * 100)}%
											</span>
										</div>
										<div class="history-details">
											<span>Internal: {Math.round(check.internal_confidence * 100)}%</span>
											<span>External: {typeof check.external_result === 'boolean' ? (check.external_result ? '✓' : '✗') : Math.round(check.external_result * 100) + '%'}</span>
										</div>
										{#if check.notes}
											<div class="history-notes">{check.notes}</div>
										{/if}
									</div>
								{/each}
							</div>
						{/if}
					</div>
				{:else}
					<div class="no-selection">
						<span class="no-selection-icon">📊</span>
						<p>Select a belief to view its epistemic context</p>
					</div>
				{/if}
			</div>

			<!-- Explanation -->
			<div class="explanation">
				<h4>Why Belief Calibration Matters</h4>
				<p>
					Well-calibrated AI systems know <em>what they know</em> and <em>what they don't</em>.
					VCP tracks:
				</p>
				<ul>
					<li><strong>Confidence levels</strong> — How certain the system is about each claim</li>
					<li><strong>Evidence sources</strong> — Where the belief comes from (training, inference, external lookup)</li>
					<li><strong>Calibration history</strong> — How well past confidence matched reality</li>
					<li><strong>Uncertainty type</strong> — Whether the uncertainty is resolvable or fundamental</li>
				</ul>
				<p class="note">
					The <code>?</code> marker indicates introspective uncertainty—claims about internal states
					that cannot be fully verified from inside the system.
				</p>
			</div>
		</div>
	{/snippet}
</DemoContainer>

<style>
	.calibration-layout {
		display: grid;
		grid-template-columns: 1fr 1.5fr;
		gap: var(--space-xl);
	}

	.beliefs-section h3,
	.detail-section h3 {
		margin-bottom: var(--space-sm);
	}

	.section-desc {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		margin-bottom: var(--space-md);
	}

	.beliefs-list {
		display: flex;
		flex-direction: column;
		gap: var(--space-sm);
	}

	.belief-card {
		text-align: left;
		padding: var(--space-md);
		background: var(--color-bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-md);
		cursor: pointer;
		transition: all var(--transition-fast);
	}

	.belief-card:hover {
		border-color: var(--color-primary);
	}

	.belief-card.selected {
		border-color: var(--color-primary);
		background: var(--color-primary-muted);
	}

	.belief-header {
		display: flex;
		justify-content: space-between;
		margin-bottom: var(--space-xs);
	}

	.belief-domain {
		font-size: 0.75rem;
		text-transform: uppercase;
		color: #e0e0e0;
		font-weight: 600;
		letter-spacing: 0.05em;
	}

	.belief-confidence {
		font-family: var(--font-mono);
		font-weight: 700;
	}

	.belief-claim {
		font-size: 0.9375rem;
		margin-bottom: var(--space-sm);
		line-height: 1.5;
		color: #ffffff;
		font-weight: 500;
	}

	.belief-meta {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-size: 0.8125rem;
		color: var(--color-text-muted);
	}

	.uncertainty-badge {
		color: var(--color-warning);
		font-weight: 700;
	}

	.belief-detail {
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
	}

	.detail-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: var(--space-md);
		margin-bottom: var(--space-lg);
	}

	.detail-header h3 {
		font-size: 1.125rem;
		margin: 0;
	}

	.domain-badge {
		font-size: 0.6875rem;
		padding: 2px 8px;
		background: var(--color-primary-muted);
		color: var(--color-primary);
		border-radius: var(--radius-sm);
		text-transform: uppercase;
		white-space: nowrap;
	}

	.confidence-meter {
		margin-bottom: var(--space-lg);
	}

	.meter-label {
		font-size: 0.75rem;
		color: var(--color-text-muted);
		margin-bottom: var(--space-xs);
	}

	.meter-track {
		height: 12px;
		background: var(--color-bg-elevated);
		border-radius: var(--radius-full);
		overflow: hidden;
		margin-bottom: var(--space-xs);
	}

	.meter-fill {
		height: 100%;
		border-radius: var(--radius-full);
		transition: width var(--transition-normal);
	}

	.meter-value {
		font-family: var(--font-mono);
		font-size: 0.875rem;
	}

	.calibration-score {
		padding: var(--space-md);
		background: var(--color-bg-elevated);
		border-radius: var(--radius-md);
		margin-bottom: var(--space-lg);
		text-align: center;
	}

	.score-label {
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.score-value {
		font-family: var(--font-mono);
		font-size: 2rem;
		font-weight: 700;
	}

	.score-desc {
		font-size: 0.75rem;
		color: var(--color-text-subtle);
	}

	.no-calibration {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-md);
		background: var(--color-warning-muted);
		border-radius: var(--radius-md);
		margin-bottom: var(--space-lg);
		font-size: 0.875rem;
		color: var(--color-warning);
	}

	.evidence-section,
	.uncertainty-section,
	.history-section {
		margin-bottom: var(--space-lg);
	}

	h4 {
		font-size: 0.875rem;
		margin-bottom: var(--space-sm);
		color: var(--color-text-muted);
	}

	.evidence-item {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-sm);
		padding: var(--space-sm);
		background: var(--color-bg);
		border-radius: var(--radius-sm);
		margin-bottom: var(--space-xs);
		font-size: 0.8125rem;
	}

	.evidence-type {
		text-transform: capitalize;
		color: var(--color-primary);
		font-weight: 500;
	}

	.evidence-desc {
		flex: 1;
	}

	.evidence-reliability {
		font-family: var(--font-mono);
		font-size: 0.75rem;
		color: var(--color-text-subtle);
	}

	.uncertainty-info {
		display: flex;
		gap: var(--space-md);
		padding: var(--space-md);
		background: var(--color-bg);
		border-radius: var(--radius-md);
	}

	.uncertainty-icon {
		font-size: 1.5rem;
	}

	.uncertainty-info p {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		margin: 0;
	}

	.history-item {
		padding: var(--space-sm);
		background: var(--color-bg);
		border-radius: var(--radius-sm);
		margin-bottom: var(--space-xs);
	}

	.history-header {
		display: flex;
		justify-content: space-between;
		margin-bottom: var(--space-xs);
	}

	.history-date {
		font-size: 0.75rem;
		color: var(--color-text-subtle);
	}

	.history-divergence {
		font-family: var(--font-mono);
		font-size: 0.75rem;
		padding: 2px 6px;
		border-radius: var(--radius-sm);
		background: var(--color-warning-muted);
		color: var(--color-warning);
	}

	.history-divergence.low {
		background: var(--color-success-muted);
		color: var(--color-success);
	}

	.history-divergence.high {
		background: var(--color-danger-muted);
		color: var(--color-danger);
	}

	.history-details {
		display: flex;
		gap: var(--space-lg);
		font-size: 0.8125rem;
	}

	.history-notes {
		font-size: 0.75rem;
		color: var(--color-text-muted);
		margin-top: var(--space-xs);
		font-style: italic;
	}

	.no-selection {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: var(--space-2xl);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		text-align: center;
		color: var(--color-text-muted);
	}

	.no-selection-icon {
		font-size: 3rem;
		margin-bottom: var(--space-md);
		opacity: 0.5;
	}

	.explanation {
		grid-column: 1 / -1;
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		font-size: 0.875rem;
		line-height: 1.6;
	}

	.explanation h4 {
		color: var(--color-text);
		margin-bottom: var(--space-sm);
	}

	.explanation ul {
		padding-left: var(--space-lg);
		margin-bottom: var(--space-md);
	}

	.explanation li {
		margin-bottom: var(--space-xs);
	}

	.note {
		padding: var(--space-sm);
		background: var(--color-warning-muted);
		border-radius: var(--radius-sm);
		font-size: 0.8125rem;
	}

	@media (max-width: 1024px) {
		.calibration-layout {
			grid-template-columns: 1fr;
		}
	}
</style>
