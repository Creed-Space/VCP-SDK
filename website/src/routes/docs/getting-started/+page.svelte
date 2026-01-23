<script lang="ts">
	import DocsLayout from '$lib/components/docs/DocsLayout.svelte';
</script>

<svelte:head>
	<title>Getting Started - VCP Documentation</title>
	<meta name="description" content="Quick start guide for implementing VCP in your application." />
</svelte:head>

<DocsLayout
	title="Getting Started"
	description="Get up and running with VCP in 5 minutes."
	editPath="/src/routes/docs/getting-started/+page.svelte"
>
	{#snippet children()}
		<h2>What is VCP?</h2>
		<p>
			The <strong>Value Context Protocol (VCP)</strong> is a standard for encoding user preferences,
			constraints, and context in a privacy-preserving format that AI systems can use to personalize
			responses without exposing sensitive information.
		</p>

		<blockquote>
			"Share what matters. Keep what's personal."
		</blockquote>

		<h2>Quick Start</h2>

		<h3>1. Define a VCP Context</h3>
		<p>A VCP context contains your preferences, constraints, and privacy settings:</p>

		<pre><code>{`import type { VCPContext } from 'vcp';

const context: VCPContext = {
  vcp_version: "1.0",
  profile_id: "user_001",

  // Reference a constitution (behavioral guidelines)
  constitution: {
    id: "learning-assistant",
    version: "1.0",
    persona: "godparent",
    adherence: 3
  },

  // Public preferences - shared with all stakeholders
  public_profile: {
    goal: "learn_guitar",
    experience: "beginner",
    learning_style: "visual"
  },

  // Portable preferences - follow you across platforms
  portable_preferences: {
    noise_mode: "quiet_preferred",
    session_length: "30_minutes",
    budget_range: "low"
  },

  // Private context - influences AI but NEVER exposed
  private_context: {
    _note: "Values here shape recommendations but are never transmitted",
    work_situation: "unemployed",
    housing_situation: "living_with_parents"
  }
};`}</code></pre>

		<h3>2. Encode to CSM-1 Token</h3>
		<p>The <strong>CSM-1 (Compact State Message)</strong> format is a human-readable token that encodes your context:</p>

		<pre><code>{`import { encodeContextToCSM1 } from 'vcp';

const token = encodeContextToCSM1(context);

// Output:
// VCP:1.0:user_001
// C:learning-assistant@1.0
// P:godparent:3
// G:learn_guitar:beginner:visual
// X:<i class="fa-solid fa-volume-xmark" aria-hidden="true"></i>quiet:<i class="fa-solid fa-coins" aria-hidden="true"></i>low:<i class="fa-solid fa-stopwatch" aria-hidden="true"></i>30minutes
// F:none
// S:<i class="fa-solid fa-lock" aria-hidden="true"></i>work|<i class="fa-solid fa-lock" aria-hidden="true"></i>housing`}</code></pre>

		<h3>3. Share with Stakeholders</h3>
		<p>The token tells AI systems what they need to know, while keeping private details hidden:</p>

		<table>
			<thead>
				<tr>
					<th>Line</th>
					<th>Meaning</th>
					<th>AI Sees</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td><code>G:learn_guitar:beginner:visual</code></td>
					<td>Goal + skill level + style</td>
					<td><i class="fa-solid fa-check" aria-hidden="true"></i> Full detail</td>
				</tr>
				<tr>
					<td><code>X:<i class="fa-solid fa-volume-xmark" aria-hidden="true"></i>quiet:<i class="fa-solid fa-coins" aria-hidden="true"></i>low</code></td>
					<td>Noise + budget constraints</td>
					<td><i class="fa-solid fa-check" aria-hidden="true"></i> Flags only</td>
				</tr>
				<tr>
					<td><code>S:<i class="fa-solid fa-lock" aria-hidden="true"></i>work|<i class="fa-solid fa-lock" aria-hidden="true"></i>housing</code></td>
					<td>Private context exists</td>
					<td><i class="fa-solid fa-xmark" aria-hidden="true"></i> Categories only</td>
				</tr>
			</tbody>
		</table>

		<p>
			The AI knows <em>that</em> work and housing context influenced the recommendations, but not
			<em>what</em> that context is. This enables personalization without surveillance.
		</p>

		<h2>Key Concepts</h2>

		<h3>Privacy Levels</h3>
		<ul>
			<li><strong>Public</strong> — Always shared (goals, experience level)</li>
			<li><strong>Consent</strong> — Shared when you approve (specific preferences)</li>
			<li><strong>Private</strong> — Never transmitted, only influences locally (sensitive reasons)</li>
		</ul>

		<h3>Constitutions</h3>
		<p>
			Constitutions define AI behavioral guidelines. They specify what an AI should prioritize,
			avoid, and how it should interact. VCP contexts reference constitutions to ensure consistent
			behavior.
		</p>

		<h3>Personas</h3>
		<p>Different interaction styles built into constitutions:</p>
		<ul>
			<li><strong>Godparent</strong> — Nurturing, supportive, patient</li>
			<li><strong>Sentinel</strong> — Cautious, protective, conservative</li>
			<li><strong>Ambassador</strong> — Professional, diplomatic, balanced</li>
			<li><strong>Anchor</strong> — Stable, grounding, realistic</li>
			<li><strong>Nanny</strong> — Structured, directive, safe</li>
		</ul>

		<h2>Next Steps</h2>
		<ul>
			<li><a href="/docs/concepts">Core Concepts</a> — Deep dive into VCP architecture</li>
			<li><a href="/docs/csm1-specification">CSM-1 Specification</a> — Full token format reference</li>
			<li><a href="/playground">Playground</a> — Build tokens interactively</li>
		</ul>
	{/snippet}
</DocsLayout>
