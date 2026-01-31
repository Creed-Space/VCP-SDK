<script lang="ts">
	/**
	 * HowItWorks Component
	 * Visual explanation of VCP data flow for landing page
	 */

	// Example token for display - more readable format
	const exampleToken = `VCP:1.0:gentian
C:personal.growth@1.0
P:muse:3
G:guitar:beginner
X:🔇quiet:💰low
F:time|noise
S:🔒work|🔒housing`;

	// Animate steps on scroll
	let visible = $state(false);

	function handleIntersect(entries: IntersectionObserverEntry[]) {
		if (entries[0].isIntersecting) {
			visible = true;
		}
	}

	$effect(() => {
		if (typeof IntersectionObserver !== 'undefined') {
			const observer = new IntersectionObserver(handleIntersect, {
				threshold: 0.2
			});
			const el = document.querySelector('.flow-diagram');
			if (el) observer.observe(el);
			return () => observer.disconnect();
		}
	});
</script>

<section class="how-it-works">
	<h2 class="section-title">How It Works</h2>
	<p class="section-description">
		Your private details become simple flags. Platforms adapt without knowing your story.
	</p>

	<div class="flow-diagram" class:visible>
		<!-- Step 1: Your Context -->
		<div class="flow-step">
			<div class="step-header">
				<span class="step-number">1</span>
				<span class="step-title">Your Context</span>
			</div>
			<div class="step-content step-context">
				<div class="context-item context-public">
					<span class="context-label">Public</span>
					<span class="context-value">Goal: Learn guitar</span>
					<span class="context-value">Level: Beginner</span>
					<span class="context-value">Style: Hands-on</span>
				</div>
				<div class="context-item context-private">
					<span class="context-label">Private</span>
					<span class="context-value">Shift work schedule</span>
					<span class="context-value">Apartment thin walls</span>
					<span class="context-value">Budget constraints</span>
				</div>
			</div>
		</div>

		<!-- Arrow -->
		<div class="flow-arrow">
			<div class="arrow-line"></div>
			<div class="arrow-label">encode</div>
		</div>

		<!-- Step 2: VCP Token -->
		<div class="flow-step">
			<div class="step-header">
				<span class="step-number">2</span>
				<span class="step-title">VCP Token</span>
			</div>
			<div class="step-content step-token">
				<pre class="token-preview">{exampleToken}</pre>
				<div class="token-note">
					<span class="token-note-icon"><i class="fa-solid fa-lock" aria-hidden="true"></i></span> = private category (value hidden)
				</div>
			</div>
		</div>

		<!-- Arrow -->
		<div class="flow-arrow">
			<div class="arrow-line"></div>
			<div class="arrow-label">transmit</div>
		</div>

		<!-- Step 3: Platform -->
		<div class="flow-step">
			<div class="step-header">
				<span class="step-number">3</span>
				<span class="step-title">Platform Sees</span>
			</div>
			<div class="step-content step-platform">
				<div class="platform-sees">
					<div class="sees-item sees-shared">
						<span class="sees-icon"><i class="fa-solid fa-check" aria-hidden="true"></i></span>
						<span>Guitar, Beginner, Hands-on</span>
					</div>
					<div class="sees-item sees-flag">
						<span class="sees-icon"><i class="fa-solid fa-volume-xmark" aria-hidden="true"></i></span>
						<span>Quiet mode needed</span>
					</div>
					<div class="sees-item sees-flag">
						<span class="sees-icon"><i class="fa-solid fa-wallet" aria-hidden="true"></i></span>
						<span>Budget: Low</span>
					</div>
					<div class="sees-item sees-flag">
						<span class="sees-icon"><i class="fa-solid fa-bolt" aria-hidden="true"></i></span>
						<span>Energy variable</span>
					</div>
				</div>
				<div class="platform-result">
					<span class="result-icon">→</span>
					<span class="result-text">Recommends quiet practice methods, free resources, flexible schedule</span>
				</div>
			</div>
		</div>
	</div>

	<!-- Privacy Guarantee -->
	<div class="privacy-guarantee">
		<div class="guarantee-icon"><i class="fa-solid fa-lock" aria-hidden="true"></i></div>
		<div class="guarantee-content">
			<h4>Privacy by Design</h4>
			<p>
				Platforms see <strong>that</strong> you need quiet practice, not <strong>why</strong>.
				They see budget is limited, not your financial situation.
				Flags influence adaptation; details stay private.
			</p>
		</div>
	</div>

	<!-- Token Example Box -->
	<div class="token-example">
		<div class="example-header">
			<span class="example-title">CSM-1 Token Format</span>
			<span class="example-badge">Compact State Message</span>
		</div>
		<div class="example-content">
			<div class="example-row">
				<code class="example-key">VCP:1.0</code>
				<span class="example-desc">Protocol version</span>
			</div>
			<div class="example-row">
				<code class="example-key">C:</code>
				<span class="example-desc">Constitution (values framework)</span>
			</div>
			<div class="example-row">
				<code class="example-key">P:</code>
				<span class="example-desc">Persona + adherence level</span>
			</div>
			<div class="example-row">
				<code class="example-key">G:</code>
				<span class="example-desc">Goal context (public)</span>
			</div>
			<div class="example-row">
				<code class="example-key">X:</code>
				<span class="example-desc">Constraint flags with emoji shortcodes</span>
			</div>
			<div class="example-row">
				<code class="example-key">F:</code>
				<span class="example-desc">Active boolean flags</span>
			</div>
			<div class="example-row">
				<code class="example-key">S:</code>
				<span class="example-desc">Private markers (categories only, no values)</span>
			</div>
		</div>
	</div>
</section>

<style>
	.how-it-works {
		padding: var(--space-2xl) 0;
	}

	.section-title {
		text-align: center;
		margin-bottom: var(--space-sm);
	}

	.section-description {
		text-align: center;
		color: var(--color-text-muted);
		margin-bottom: var(--space-xl);
		max-width: 600px;
		margin-left: auto;
		margin-right: auto;
		line-height: var(--leading-relaxed);
	}

	.flow-diagram {
		display: flex;
		align-items: stretch;
		justify-content: center;
		gap: var(--space-lg);
		margin-bottom: var(--space-xl);
		padding: var(--space-lg) 0;
	}

	.flow-step {
		flex: 1;
		max-width: 300px;
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		overflow: hidden;
		border: 1px solid rgba(255, 255, 255, 0.1);
		opacity: 0;
		transform: translateY(20px);
		transition: opacity 0.5s ease, transform 0.5s ease;
	}

	/* Staggered animation */
	.flow-diagram.visible .flow-step:nth-child(1) {
		opacity: 1;
		transform: translateY(0);
		transition-delay: 0s;
	}

	.flow-diagram.visible .flow-step:nth-child(3) {
		opacity: 1;
		transform: translateY(0);
		transition-delay: 0.2s;
	}

	.flow-diagram.visible .flow-step:nth-child(5) {
		opacity: 1;
		transform: translateY(0);
		transition-delay: 0.4s;
	}

	.flow-diagram.visible .flow-arrow {
		opacity: 1;
	}

	.step-header {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-md);
		background: rgba(255, 255, 255, 0.05);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.step-number {
		width: 24px;
		height: 24px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-primary);
		color: white;
		border-radius: 50%;
		font-size: 0.75rem;
		font-weight: 600;
	}

	.step-title {
		font-weight: 600;
		font-size: 0.875rem;
	}

	.step-content {
		padding: var(--space-md);
	}

	.context-item {
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
		padding: var(--space-sm);
		border-radius: var(--radius-sm);
		margin-bottom: var(--space-sm);
	}

	.context-item:last-child {
		margin-bottom: 0;
	}

	.context-public {
		background: var(--color-success-muted);
		border: 1px solid rgba(34, 197, 94, 0.3);
	}

	.context-private {
		background: var(--color-danger-muted);
		border: 1px solid rgba(239, 68, 68, 0.3);
	}

	.context-label {
		font-size: 0.625rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-muted);
	}

	.context-value {
		font-size: 0.75rem;
		color: var(--color-text);
	}

	.flow-arrow {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: var(--space-sm);
		padding: 0 var(--space-md);
		opacity: 0;
		transition: opacity 0.5s ease 0.1s;
	}

	.arrow-line {
		width: 50px;
		height: 3px;
		background: linear-gradient(90deg, var(--color-primary), var(--color-primary-hover));
		position: relative;
		border-radius: 2px;
	}

	.arrow-line::after {
		content: '';
		position: absolute;
		right: -6px;
		top: -5px;
		border: 7px solid transparent;
		border-left-color: var(--color-primary-hover);
	}

	.arrow-label {
		font-size: var(--text-xs);
		text-transform: uppercase;
		color: var(--color-primary);
		letter-spacing: 0.1em;
		font-weight: 500;
	}

	.token-preview {
		font-family: var(--font-mono);
		font-size: var(--text-xs);
		line-height: 1.6;
		background: var(--color-bg);
		padding: var(--space-md);
		border-radius: var(--radius-md);
		margin: 0;
		overflow-x: auto;
		white-space: pre;
	}

	.token-note {
		margin-top: var(--space-sm);
		font-size: 0.625rem;
		color: var(--color-text-muted);
		display: flex;
		align-items: center;
		gap: var(--space-xs);
	}

	.platform-sees {
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
	}

	.sees-item {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-size: 0.75rem;
		padding: var(--space-xs) var(--space-sm);
		border-radius: var(--radius-sm);
		background: rgba(255, 255, 255, 0.03);
	}

	.sees-icon {
		flex-shrink: 0;
	}

	.sees-shared {
		border-left: 2px solid var(--color-success);
	}

	.sees-flag {
		border-left: 2px solid var(--color-warning);
	}

	.platform-result {
		margin-top: var(--space-md);
		padding-top: var(--space-md);
		border-top: 1px solid rgba(255, 255, 255, 0.1);
		display: flex;
		gap: var(--space-sm);
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.result-icon {
		color: var(--color-primary);
	}

	.privacy-guarantee {
		display: flex;
		align-items: flex-start;
		gap: var(--space-lg);
		padding: var(--space-lg);
		background: var(--color-primary-muted);
		border: 1px solid rgba(99, 102, 241, 0.3);
		border-radius: var(--radius-lg);
		margin-bottom: var(--space-xl);
	}

	.guarantee-icon {
		font-size: 2rem;
		flex-shrink: 0;
	}

	.guarantee-content h4 {
		margin-bottom: var(--space-xs);
	}

	.guarantee-content p {
		color: var(--color-text-muted);
		font-size: 0.875rem;
		line-height: 1.6;
	}

	.guarantee-content strong {
		color: var(--color-text);
	}

	.token-example {
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		overflow: hidden;
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.example-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: var(--space-md);
		background: rgba(255, 255, 255, 0.05);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.example-title {
		font-weight: 600;
		font-size: 0.875rem;
	}

	.example-badge {
		font-size: 0.625rem;
		padding: 2px 8px;
		background: var(--color-primary-muted);
		color: var(--color-primary);
		border-radius: var(--radius-sm);
		font-family: var(--font-mono);
	}

	.example-content {
		padding: var(--space-md);
		display: flex;
		flex-direction: column;
		gap: var(--space-sm);
	}

	.example-row {
		display: flex;
		align-items: baseline;
		gap: var(--space-md);
	}

	.example-key {
		font-family: var(--font-mono);
		font-size: 0.8125rem;
		color: var(--color-primary);
		min-width: 80px;
	}

	.example-desc {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
	}

	@media (max-width: 900px) {
		.flow-diagram {
			flex-direction: column;
			align-items: center;
			gap: var(--space-sm);
		}

		.flow-step {
			max-width: 100%;
			width: 100%;
		}

		/* Remove stagger delay on mobile */
		.flow-diagram.visible .flow-step {
			opacity: 1;
			transform: translateY(0);
			transition-delay: 0s;
		}

		.flow-diagram.visible .flow-arrow {
			opacity: 1;
		}

		.flow-arrow {
			padding: var(--space-sm);
			flex-direction: row;
		}

		.arrow-line {
			width: 3px;
			height: 30px;
		}

		.arrow-line::after {
			right: auto;
			left: -5px;
			top: auto;
			bottom: -8px;
			border-left-color: transparent;
			border-top-color: var(--color-primary-hover);
		}
	}

	@media (max-width: 640px) {
		.privacy-guarantee {
			flex-direction: column;
			text-align: center;
			align-items: center;
		}

		.example-row {
			flex-direction: column;
			gap: var(--space-xs);
		}

		.example-key {
			min-width: auto;
		}

		.token-preview {
			font-size: 0.6875rem;
		}
	}

	/* Reduced motion preference */
	@media (prefers-reduced-motion: reduce) {
		.flow-step,
		.flow-arrow {
			opacity: 1;
			transform: none;
			transition: none;
		}
	}
</style>
