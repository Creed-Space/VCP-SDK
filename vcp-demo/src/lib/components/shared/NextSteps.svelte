<script lang="ts">
	/**
	 * NextSteps Component
	 * Provides contextual navigation suggestions at the end of pages
	 */

	interface NextStep {
		href: string;
		icon: string;
		title: string;
		description: string;
		primary?: boolean;
	}

	interface Props {
		title?: string;
		steps: NextStep[];
	}

	let { title = 'What Next?', steps }: Props = $props();
</script>

<section class="next-steps">
	<h2>{title}</h2>
	<div class="steps-grid" class:has-primary={steps.some(s => s.primary)}>
		{#each steps as step}
			<a href={step.href} class="step-card" class:step-primary={step.primary}>
				<span class="step-icon"><i class="fa-solid {step.icon}" aria-hidden="true"></i></span>
				<div class="step-content">
					<h3>{step.title}</h3>
					<p>{step.description}</p>
				</div>
				<span class="step-arrow"><i class="fa-solid fa-arrow-right" aria-hidden="true"></i></span>
			</a>
		{/each}
	</div>
</section>

<style>
	.next-steps {
		margin-top: var(--space-2xl);
		padding-top: var(--space-xl);
		border-top: 1px solid rgba(255, 255, 255, 0.1);
	}

	.next-steps h2 {
		text-align: center;
		margin-bottom: var(--space-lg);
		font-size: var(--text-xl);
	}

	.steps-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: var(--space-md);
	}

	.steps-grid.has-primary {
		grid-template-columns: 1fr;
	}

	.step-card {
		display: flex;
		align-items: center;
		gap: var(--space-md);
		padding: var(--space-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-lg);
		border: 1px solid rgba(255, 255, 255, 0.1);
		text-decoration: none;
		color: var(--color-text);
		transition: all var(--transition-fast);
	}

	.step-card:hover {
		border-color: var(--color-primary);
		transform: translateX(4px);
		text-decoration: none;
	}

	.step-primary {
		border-color: var(--color-primary);
		background: linear-gradient(135deg, var(--color-bg-card), rgba(99, 102, 241, 0.1));
	}

	.step-icon {
		font-size: 1.5rem;
		color: var(--color-primary);
		flex-shrink: 0;
	}

	.step-content {
		flex: 1;
	}

	.step-content h3 {
		font-size: var(--text-base);
		margin-bottom: var(--space-xs);
	}

	.step-content p {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		line-height: var(--leading-normal);
	}

	.step-arrow {
		color: var(--color-text-muted);
		transition: transform var(--transition-fast);
	}

	.step-card:hover .step-arrow {
		transform: translateX(4px);
		color: var(--color-primary);
	}

	@media (max-width: 640px) {
		.step-card {
			padding: var(--space-md);
		}

		.step-icon {
			font-size: 1.25rem;
		}
	}
</style>
