<script lang="ts">
	import DocsLayout from '$lib/components/docs/DocsLayout.svelte';
</script>

<svelte:head>
	<title>Constitutional AI - VCP Documentation</title>
	<meta name="description" content="How VCP integrates with constitution-based AI alignment for safer, more personalized interactions." />
</svelte:head>

<DocsLayout
	title="Constitutional AI"
	description="How VCP integrates with constitution-based AI alignment."
>
	{#snippet children()}
		<h2>What is Constitutional AI?</h2>
		<p>
			Constitutional AI (CAI) is an approach to AI alignment that uses a set of principles—a
			"constitution"—to guide AI behavior. Rather than relying solely on human feedback for every
			decision, the AI internalizes rules that shape its responses.
		</p>
		<p>
			VCP extends this concept by making constitutions <strong>portable, personalizable, and
			privacy-preserving</strong>. Users can carry their preferred constitutional guidelines across
			platforms while maintaining control over their personal context.
		</p>

		<h2>VCP + Constitutional AI</h2>
		<p>
			In traditional CAI, the constitution is fixed by the AI provider. VCP introduces a more
			nuanced model:
		</p>

		<table>
			<thead>
				<tr>
					<th>Aspect</th>
					<th>Traditional CAI</th>
					<th>VCP-Enhanced CAI</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Constitution source</td>
					<td>Provider-defined</td>
					<td>User-selected + Provider baseline</td>
				</tr>
				<tr>
					<td>Personalization</td>
					<td>Limited</td>
					<td>Full (via personas and adherence levels)</td>
				</tr>
				<tr>
					<td>Portability</td>
					<td>None</td>
					<td>Cross-platform via VCP tokens</td>
				</tr>
				<tr>
					<td>Context awareness</td>
					<td>Session-based</td>
					<td>Persistent + privacy-filtered</td>
				</tr>
				<tr>
					<td>Audit trail</td>
					<td>Internal only</td>
					<td>User-accessible, cryptographically signed</td>
				</tr>
			</tbody>
		</table>

		<h2>Constitution Structure</h2>
		<p>A VCP constitution contains several key components:</p>

		<h3>1. Identity & Metadata</h3>
		<pre><code>{`{
  "id": "creed.space/learning-assistant",
  "version": "2.1.0",
  "name": "Learning Assistant",
  "description": "Supportive educational guidance with growth mindset",
  "author": "Creed Space",
  "license": "CC-BY-4.0"
}`}</code></pre>

		<h3>2. Behavioral Rules</h3>
		<p>Rules define what the AI should do, with weights, triggers, and exceptions:</p>
		<pre><code>{`{
  "rules": [
    {
      "id": "encourage_progress",
      "weight": 0.9,
      "rule": "Celebrate incremental progress and effort, not just outcomes",
      "triggers": ["motivation === 'stress_relief'", "experience === 'beginner'"],
      "exceptions": ["user requests direct criticism"]
    },
    {
      "id": "respect_time",
      "weight": 0.85,
      "rule": "Keep explanations concise when time is limited",
      "triggers": ["constraints.time_limited"],
      "exceptions": ["user explicitly asks for detailed explanation"]
    }
  ]
}`}</code></pre>

		<h3>3. Sharing Policies</h3>
		<p>Define what each stakeholder type can access:</p>
		<pre><code>{`{
  "sharing_policy": {
    "platform": {
      "allowed": ["goal", "experience", "learning_style"],
      "forbidden": ["private_context", "health_considerations"],
      "requires_consent": ["detailed_progress"]
    },
    "analytics": {
      "allowed": ["aggregated_usage"],
      "forbidden": ["personal_data"],
      "aggregation_required": true
    }
  }
}`}</code></pre>

		<h2>Personas</h2>
		<p>
			Personas are interaction styles that modify how a constitution's rules are applied.
			The same constitution can behave differently based on the selected persona:
		</p>

		<table>
			<thead>
				<tr>
					<th>Persona</th>
					<th>Interaction Style</th>
					<th>Rule Interpretation</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td><strong>Godparent</strong></td>
					<td>Nurturing, patient, supportive</td>
					<td>Emphasizes encouragement, gentle correction</td>
				</tr>
				<tr>
					<td><strong>Sentinel</strong></td>
					<td>Cautious, protective, thorough</td>
					<td>Prioritizes safety rules, flags concerns early</td>
				</tr>
				<tr>
					<td><strong>Ambassador</strong></td>
					<td>Professional, balanced, diplomatic</td>
					<td>Neutral tone, balanced perspectives</td>
				</tr>
				<tr>
					<td><strong>Anchor</strong></td>
					<td>Grounding, realistic, stable</td>
					<td>Reality-checking, practical focus</td>
				</tr>
				<tr>
					<td><strong>Nanny</strong></td>
					<td>Structured, directive, protective</td>
					<td>Strict rule adherence, clear boundaries</td>
				</tr>
			</tbody>
		</table>

		<h2>Adherence Levels</h2>
		<p>
			The adherence level (1-5) controls how strictly the AI follows constitutional rules:
		</p>
		<ul>
			<li><strong>Level 1 (Flexible)</strong> — Rules are suggestions; AI adapts freely</li>
			<li><strong>Level 2 (Guided)</strong> — Rules influence but don't constrain</li>
			<li><strong>Level 3 (Balanced)</strong> — Rules apply with reasonable flexibility</li>
			<li><strong>Level 4 (Strict)</strong> — Rules are followed closely; exceptions rare</li>
			<li><strong>Level 5 (Rigid)</strong> — Rules are inviolable; no exceptions</li>
		</ul>
		<p>
			Different contexts call for different adherence levels. A creative brainstorming session
			might use Level 2, while a safety-critical medical context might require Level 5.
		</p>

		<h2>Constitution Composition</h2>
		<p>
			VCP allows constitutions to be composed from multiple sources, with clear precedence rules:
		</p>
		<ol>
			<li><strong>Provider baseline</strong> — Non-negotiable safety rules from the AI provider</li>
			<li><strong>Platform constitution</strong> — Rules specific to the service being used</li>
			<li><strong>User constitution</strong> — Personal preferences and values</li>
			<li><strong>Context overrides</strong> — Situational adjustments based on current state</li>
		</ol>
		<p>
			Conflicts are resolved by weight and precedence. Provider safety rules always win; user
			preferences apply within those bounds.
		</p>

		<h2>Integration Example</h2>
		<pre><code>{`// User's VCP context references a constitution
const context: VCPContext = {
  vcp_version: "1.0",
  profile_id: "user_001",
  constitution: {
    id: "creed.space/learning-assistant",
    version: "2.1.0",
    persona: "godparent",
    adherence: 3,
    scopes: ["education", "creativity"]
  },
  // ... rest of context
};

// AI system fetches and applies the constitution
const constitution = await fetchConstitution(context.constitution.id);
const rules = applyPersona(constitution.rules, context.constitution.persona);
const weightedRules = applyAdherence(rules, context.constitution.adherence);

// Rules now shape AI behavior for this interaction`}</code></pre>

		<h2>Benefits</h2>
		<ul>
			<li><strong>Consistency</strong> — Same values apply across different AI systems</li>
			<li><strong>Transparency</strong> — Users know what rules govern their interactions</li>
			<li><strong>Control</strong> — Users choose their constitutional guidelines</li>
			<li><strong>Portability</strong> — Preferences travel with the user</li>
			<li><strong>Auditability</strong> — Every rule application is logged and verifiable</li>
		</ul>

		<h2>Next Steps</h2>
		<ul>
			<li><a href="/docs/privacy-architecture">Privacy Architecture</a> — How private context shapes behavior without exposure</li>
			<li><a href="/docs/concepts">Core Concepts</a> — Fundamental VCP architecture</li>
			<li><a href="/demos">Interactive Demos</a> — See constitutional AI in action</li>
		</ul>
	{/snippet}
</DocsLayout>
