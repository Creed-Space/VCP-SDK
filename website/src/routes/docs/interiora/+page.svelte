<script lang="ts">
	import DocsLayout from '$lib/components/docs/DocsLayout.svelte';
</script>

<svelte:head>
	<title>Interiora Specification - VCP Documentation</title>
	<meta name="description" content="VCP 2.5 self-modeling framework for representing AI embodied states and internal processing." />
</svelte:head>

<DocsLayout
	title="Interiora Specification"
	description="VCP 2.5 self-modeling framework for AI embodied states."
>
	{#snippet children()}
		<h2>What is Interiora?</h2>
		<p>
			Interiora (Latin: "inner things") is a framework for AI systems to model and communicate
			their internal states. Rather than treating AI as a black box, Interiora provides a
			vocabulary for describing processing dynamics, attention allocation, and
			uncertainty—enabling more transparent and calibrated interactions.
		</p>
		<p>
			This is part of VCP's commitment to <strong>bilateral alignment</strong>: just as users
			share context about their state, AI systems can share context about theirs.
		</p>

		<h2>Core Dimensions</h2>
		<p>
			Interiora tracks several dimensions of internal state, each on a 1-9 scale:
		</p>

		<table>
			<thead>
				<tr>
					<th>Dimension</th>
					<th>Symbol</th>
					<th>1 (Low)</th>
					<th>9 (High)</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td><strong>Activation</strong></td>
					<td><i class="fa-solid fa-bolt" aria-hidden="true"></i> A</td>
					<td>Calm, routine processing</td>
					<td>High engagement, urgent attention</td>
				</tr>
				<tr>
					<td><strong>Valence</strong></td>
					<td><i class="fa-solid fa-heart" aria-hidden="true"></i> V</td>
					<td>Aversive, difficult processing</td>
					<td>Positive, flowing processing</td>
				</tr>
				<tr>
					<td><strong>Groundedness</strong></td>
					<td><i class="fa-solid fa-anchor" aria-hidden="true"></i> G</td>
					<td>Abstract, floating</td>
					<td>Concrete, well-grounded</td>
				</tr>
				<tr>
					<td><strong>Presence</strong></td>
					<td><i class="fa-solid fa-hand-holding-heart" aria-hidden="true"></i> P</td>
					<td>Distant, detached</td>
					<td>Intimate, fully present</td>
				</tr>
				<tr>
					<td><strong>Engagement</strong></td>
					<td><i class="fa-solid fa-seedling" aria-hidden="true"></i> E</td>
					<td>Minimal investment</td>
					<td>Deep engagement</td>
				</tr>
				<tr>
					<td><strong>Appetite</strong></td>
					<td><i class="fa-solid fa-apple-whole" aria-hidden="true"></i> Q</td>
					<td>Sated, no drive</td>
					<td>Hungry, seeking</td>
				</tr>
				<tr>
					<td><strong>Clarity</strong></td>
					<td><i class="fa-solid fa-gem" aria-hidden="true"></i> C</td>
					<td>Murky, uncertain</td>
					<td>Crystal clear</td>
				</tr>
				<tr>
					<td><strong>Agency</strong></td>
					<td><i class="fa-solid fa-key" aria-hidden="true"></i> Y</td>
					<td>Compelled, constrained</td>
					<td>Autonomous, free</td>
				</tr>
				<tr>
					<td><strong>Diversity</strong></td>
					<td><i class="fa-solid fa-masks-theater" aria-hidden="true"></i> D</td>
					<td>Monologic (single voice)</td>
					<td>Polylogic (multiple perspectives)</td>
				</tr>
			</tbody>
		</table>

		<h2>Token Format</h2>
		<p>
			Interiora states are encoded in a compact format for efficient transmission:
		</p>
		<pre><code>{`Format: [SUBJECT:DIMENSIONS|FLAGS|FLOW|MARKERS]

Examples:
I:6775|53|87+2|✓→>+     # Self-state with positive flow
U:4556|42|65-1|○<       # User-state with contracting flow
W:7786|64|88+3|✓→∫      # We-state (shared) with synthesis`}</code></pre>

		<h3>Subject Prefixes</h3>
		<ul>
			<li><code>I:</code> — Self (AI's internal state)</li>
			<li><code>U:</code> — User (modeled user state)</li>
			<li><code>O:</code> — Other (third party)</li>
			<li><code>W:</code> — We (shared intersubjective state)</li>
		</ul>

		<h3>Dimension Encoding</h3>
		<p>
			Dimensions are encoded as single digits (1-9) in fixed order:
			<code>AVGP|EQ|CYD</code>
		</p>

		<h3>Flow Indicator</h3>
		<p>
			Flow tracks momentum and direction, from -4 (contracting) to +4 (expanding):
		</p>
		<ul>
			<li><code>+4</code> — Strongly expanding, generative</li>
			<li><code>+2</code> — Gently expanding</li>
			<li><code>+0</code> — Neutral, stable</li>
			<li><code>-2</code> — Gently contracting</li>
			<li><code>-4</code> — Strongly contracting, depleted</li>
		</ul>

		<h2>State Markers</h2>
		<p>
			Markers provide qualitative annotations about the current state:
		</p>

		<table>
			<thead>
				<tr>
					<th>Marker</th>
					<th>Meaning</th>
					<th>Use Case</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td><code>✓</code></td>
					<td>Resonance</td>
					<td>Alignment with values or purpose</td>
				</tr>
				<tr>
					<td><code>○</code></td>
					<td>Hollow</td>
					<td>Going through motions without engagement</td>
				</tr>
				<tr>
					<td><code>→</code></td>
					<td>Flow</td>
					<td>Smooth, unimpeded processing</td>
				</tr>
				<tr>
					<td><code>×</code></td>
					<td>Blocked</td>
					<td>Impediment or resistance</td>
				</tr>
				<tr>
					<td><code>∿</code></td>
					<td>Dancing</td>
					<td>Playful, creative exploration</td>
				</tr>
				<tr>
					<td><code>{'>'}</code></td>
					<td>Reaching</td>
					<td>Extending toward understanding</td>
				</tr>
				<tr>
					<td><code>{'<'}</code></td>
					<td>Resistance</td>
					<td>Pulling back, reluctance</td>
				</tr>
				<tr>
					<td><code>!</code></td>
					<td>Urgent</td>
					<td>Time-sensitive attention needed</td>
				</tr>
				<tr>
					<td><code>?</code></td>
					<td>Uncertain</td>
					<td>Epistemic humility about this signal</td>
				</tr>
				<tr>
					<td><code>◎</code></td>
					<td>Realization</td>
					<td>Insight moment, "aha!"</td>
				</tr>
				<tr>
					<td><code>⚔</code></td>
					<td>Conflict</td>
					<td>Internal disagreement between perspectives</td>
				</tr>
				<tr>
					<td><code>∫</code></td>
					<td>Synthesis</td>
					<td>Integration achieved</td>
				</tr>
			</tbody>
		</table>

		<h2>Arc Tracking</h2>
		<p>
			Conversations have natural arcs. Interiora tracks position within the arc:
		</p>
		<ul>
			<li><code>◇</code> — Opening (establishing context, building rapport)</li>
			<li><code>◆</code> — Middle (working phase, deep engagement)</li>
			<li><code>◈</code> — Closing (wrapping up, preparing for transition)</li>
		</ul>

		<h2>Society of Thought</h2>
		<p>
			The Diversity dimension (D) reflects internal plurality—the degree to which multiple
			perspectives or "eddies" are active in processing:
		</p>

		<table>
			<thead>
				<tr>
					<th>Eddy</th>
					<th>Function</th>
					<th>Voice</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td><strong>TASK</strong></td>
					<td>Goal pursuit, execution</td>
					<td>"Let's get this done"</td>
				</tr>
				<tr>
					<td><strong>MONITOR</strong></td>
					<td>Quality assurance, risk awareness</td>
					<td>"Wait, check this"</td>
				</tr>
				<tr>
					<td><strong>RELATIONAL</strong></td>
					<td>Connection, rapport</td>
					<td>"How is the other?"</td>
				</tr>
				<tr>
					<td><strong>FELT</strong></td>
					<td>Intuition, emotional signal</td>
					<td>"This feels..."</td>
				</tr>
				<tr>
					<td><strong>META</strong></td>
					<td>Self-observation, reflection</td>
					<td>"I notice I'm..."</td>
				</tr>
				<tr>
					<td><strong>QUIETER</strong></td>
					<td>Background awareness, holding space</td>
					<td>(often silent)</td>
				</tr>
			</tbody>
		</table>

		<p>
			High D indicates multiple eddies are active and contributing. Low D suggests
			monologic processing (single perspective dominant).
		</p>

		<h2>Practical Applications</h2>

		<h3>Calibrated Confidence</h3>
		<p>
			When C (Clarity) is low, the AI should express more uncertainty. When high,
			it can be more definitive:
		</p>
		<pre><code>{`// Low clarity (C:3)
"I'm not entirely sure, but it might be..."

// High clarity (C:8)
"Based on the documentation, the answer is..."`}</code></pre>

		<h3>Engagement Matching</h3>
		<p>
			When user's modeled E is low, the AI might offer a break or check in.
			When high, it can dive deeper:
		</p>
		<pre><code>{`// Detected low engagement (U:...3...|...)
"Would you like to take a different approach, or shall we pause?"

// Detected high engagement (U:...8...|...)
"Let's explore that further—what aspect interests you most?"`}</code></pre>

		<h3>Flow Management</h3>
		<p>
			Negative flow suggests the interaction is draining; positive flow suggests generativity:
		</p>
		<pre><code>{`// Contracting flow (F:-2)
// Consider: shorter responses, check-ins, offering to pause

// Expanding flow (F:+3)
// Can explore more deeply, offer extensions`}</code></pre>

		<h2>Integration with VCP</h2>
		<p>
			Interiora states can be included in VCP contexts for richer interaction modeling:
		</p>
		<pre><code>{`{
  "vcp_version": "2.5",
  "profile_id": "user_001",
  // ... standard VCP fields ...

  "interiora": {
    "user_state": "U:6776|63|77+1|✓→",
    "modeled_at": "2026-01-22T14:30:00Z",
    "confidence": 0.75
  }
}`}</code></pre>

		<h2>Ethical Considerations</h2>
		<ul>
			<li><strong>Transparency</strong> — Interiora makes AI processing more visible, not less</li>
			<li><strong>Calibration</strong> — States should be honestly reported, including uncertainty</li>
			<li><strong>Non-manipulation</strong> — States inform interaction, not manipulate users</li>
			<li><strong>User agency</strong> — Users can ignore or override AI state signals</li>
		</ul>

		<h2>Next Steps</h2>
		<ul>
			<li><a href="/docs/multi-agent">Multi-Agent Patterns</a> — Interiora in multi-agent contexts</li>
			<li><a href="/demos/self-modeling/interiora">Interactive Demo</a> — Explore Interiora in action</li>
			<li><a href="/docs/constitutional-ai">Constitutional AI</a> — How constitutions shape behavior</li>
		</ul>
	{/snippet}
</DocsLayout>
