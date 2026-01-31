<script lang="ts">
	import { page } from '$app/stores';
</script>

<svelte:head>
	<title>Page Not Found - VCP Demo</title>
</svelte:head>

<div class="error-page container">
	<div class="error-content">
		<div class="error-code">{$page.status}</div>
		<h1>
			{#if $page.status === 404}
				Page Not Found
			{:else}
				Something Went Wrong
			{/if}
		</h1>
		<p class="error-message">
			{#if $page.status === 404}
				The page you're looking for doesn't exist or has been moved.
			{:else}
				{$page.error?.message || 'An unexpected error occurred.'}
			{/if}
		</p>
		<div class="error-actions">
			<a href="/" class="btn btn-primary">
				<i class="fa-solid fa-home" aria-hidden="true"></i>
				Back to Home
			</a>
			<a href="/demos" class="btn btn-secondary">
				<i class="fa-solid fa-play" aria-hidden="true"></i>
				View Demos
			</a>
		</div>
	</div>
</div>

<style>
	.error-page {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 60vh;
		padding: var(--space-2xl);
	}

	.error-content {
		text-align: center;
		max-width: 500px;
	}

	.error-code {
		font-size: 6rem;
		font-weight: 700;
		line-height: 1;
		background: linear-gradient(135deg, var(--color-primary), var(--color-danger));
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
		margin-bottom: var(--space-md);
	}

	h1 {
		font-size: 1.5rem;
		margin-bottom: var(--space-md);
	}

	.error-message {
		color: var(--color-text-muted);
		margin-bottom: var(--space-xl);
	}

	.error-actions {
		display: flex;
		gap: var(--space-md);
		justify-content: center;
		flex-wrap: wrap;
	}

	@media (max-width: 480px) {
		.error-code {
			font-size: 4rem;
		}

		.error-actions {
			flex-direction: column;
		}

		.error-actions .btn {
			width: 100%;
		}
	}
</style>
