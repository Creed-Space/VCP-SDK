<script lang="ts">
	import DocsLayout from '$lib/components/docs/DocsLayout.svelte';
</script>

<svelte:head>
	<title>Multi-Agent Patterns - VCP Documentation</title>
	<meta name="description" content="Implementing VCP in multi-agent coordination scenarios with shared context and negotiation." />
</svelte:head>

<DocsLayout
	title="Multi-Agent Patterns"
	description="Implementing VCP in multi-agent coordination scenarios."
>
	{#snippet children()}
		<h2>The Multi-Agent Challenge</h2>
		<p>
			As AI systems become more capable, they increasingly need to coordinate with each other—
			multiple agents working together on complex tasks, negotiating resources, or representing
			different stakeholders. VCP provides the coordination layer for these interactions.
		</p>
		<p>
			Key challenges VCP addresses:
		</p>
		<ul>
			<li>How do agents share context without oversharing?</li>
			<li>How do agents with different constitutions negotiate?</li>
			<li>How is trust established between agents?</li>
			<li>How do users maintain control over multi-agent systems?</li>
		</ul>

		<h2>Agent Identity</h2>
		<p>
			Each agent in a VCP system has an identity profile:
		</p>
		<pre><code>{`{
  "agent_id": "agent_learning_tutor_001",
  "agent_type": "tutor",
  "provider": "learning-platform.com",

  "constitution": {
    "id": "creed.space/educational-assistant",
    "version": "2.1.0",
    "persona": "godparent"
  },

  "capabilities": [
    "explanation",
    "assessment",
    "encouragement"
  ],

  "trust_anchors": [
    "creed.space",
    "learning-platform.com"
  ],

  "interiora_enabled": true
}`}</code></pre>

		<h2>Context Sharing Patterns</h2>

		<h3>Pattern 1: Mediated Sharing</h3>
		<p>
			A user's VCP context is shared through a mediator that enforces privacy policies:
		</p>
		<pre><code>{`┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   User      │     │  Mediator   │     │  Agent A    │
│   Context   │────▶│  (VCP Hub)  │────▶│  (Tutor)    │
└─────────────┘     │             │     └─────────────┘
                    │  Enforces   │
                    │  privacy    │     ┌─────────────┐
                    │  policies   │────▶│  Agent B    │
                    │             │     │  (Assessor) │
                    └─────────────┘     └─────────────┘`}</code></pre>
		<p>
			The mediator ensures each agent only receives the context they're authorized to see.
		</p>

		<h3>Pattern 2: Direct Negotiation</h3>
		<p>
			Agents negotiate directly, sharing only what's needed for coordination:
		</p>
		<pre><code>{`// Agent A proposes
{
  "proposal_id": "prop_001",
  "from": "agent_tutor",
  "to": "agent_scheduler",
  "action": "schedule_session",
  "constraints": {
    "duration": "30_minutes",
    "user_preference": "quiet_environment",
    "priority": "medium"
  },
  "context_shared": ["duration", "priority"],
  "context_withheld": ["user_health_state"]
}`}</code></pre>

		<h3>Pattern 3: Broadcast with Filters</h3>
		<p>
			Context is broadcast to all agents, but each applies their own privacy filter:
		</p>
		<pre><code>{`const context = user.vcpContext;

// Each agent filters according to their authorization level
const tutorView = privacyFilter.apply(context, {
  recipient: 'agent_tutor',
  level: 'educational'
});

const analyticsView = privacyFilter.apply(context, {
  recipient: 'agent_analytics',
  level: 'aggregated_only'
});`}</code></pre>

		<h2>Constitutional Negotiation</h2>
		<p>
			When agents with different constitutions interact, they need to negotiate compatible
			behavior:
		</p>

		<h3>Compatibility Check</h3>
		<pre><code>{`function checkConstitutionalCompatibility(agentA, agentB) {
  const conflictingRules = [];

  for (const ruleA of agentA.constitution.rules) {
    for (const ruleB of agentB.constitution.rules) {
      if (rulesConflict(ruleA, ruleB)) {
        conflictingRules.push({
          ruleA: ruleA.id,
          ruleB: ruleB.id,
          conflict_type: classifyConflict(ruleA, ruleB)
        });
      }
    }
  }

  return {
    compatible: conflictingRules.length === 0,
    conflicts: conflictingRules,
    resolution_required: conflictingRules.some(c => c.conflict_type === 'hard')
  };
}`}</code></pre>

		<h3>Resolution Strategies</h3>
		<table>
			<thead>
				<tr>
					<th>Strategy</th>
					<th>When to Use</th>
					<th>Example</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td><strong>Hierarchy</strong></td>
					<td>Clear authority relationship</td>
					<td>Safety rules override efficiency rules</td>
				</tr>
				<tr>
					<td><strong>Voting</strong></td>
					<td>Democratic multi-agent systems</td>
					<td>Majority of agents agree on action</td>
				</tr>
				<tr>
					<td><strong>Auction</strong></td>
					<td>Resource allocation</td>
					<td>Agents bid for priority with utility scores</td>
				</tr>
				<tr>
					<td><strong>Mediation</strong></td>
					<td>Complex disputes</td>
					<td>Neutral agent proposes compromise</td>
				</tr>
				<tr>
					<td><strong>Escalation</strong></td>
					<td>Unresolvable conflicts</td>
					<td>Human user makes final decision</td>
				</tr>
			</tbody>
		</table>

		<h2>Trust Establishment</h2>
		<p>
			VCP uses a web-of-trust model for agent authentication:
		</p>

		<h3>Trust Chain</h3>
		<pre><code>{`{
  "trust_chain": [
    {
      "subject": "agent_tutor_001",
      "issuer": "learning-platform.com",
      "level": "verified",
      "issued_at": "2026-01-01T00:00:00Z",
      "expires_at": "2027-01-01T00:00:00Z"
    },
    {
      "subject": "learning-platform.com",
      "issuer": "creed.space",
      "level": "certified_provider",
      "issued_at": "2025-06-01T00:00:00Z"
    }
  ]
}`}</code></pre>

		<h3>Trust Levels</h3>
		<ul>
			<li><strong>Unknown</strong> — No trust established, minimal context sharing</li>
			<li><strong>Verified</strong> — Identity confirmed, basic context sharing</li>
			<li><strong>Trusted</strong> — Good track record, expanded context sharing</li>
			<li><strong>Certified</strong> — Audited by trusted authority, full sharing within policy</li>
		</ul>

		<h2>Coordination Protocols</h2>

		<h3>Task Delegation</h3>
		<pre><code>{`// Primary agent delegates subtask
const delegation = {
  task_id: "task_001",
  from: "agent_coordinator",
  to: "agent_specialist",

  task: {
    type: "research",
    topic: "learning_resources",
    constraints: user.vcpContext.constraints
  },

  context_grant: {
    fields: ["goal", "experience", "learning_style"],
    duration: "task_completion",
    audit_required: true
  },

  callback: {
    type: "result",
    schema: "research_findings_v1"
  }
};`}</code></pre>

		<h3>Result Aggregation</h3>
		<p>
			When multiple agents contribute to a response, their outputs are aggregated with
			provenance tracking:
		</p>
		<pre><code>{`{
  "aggregated_response": {
    "content": "Based on your learning style...",

    "contributions": [
      {
        "agent": "agent_content",
        "portion": "content_recommendations",
        "confidence": 0.85
      },
      {
        "agent": "agent_scheduling",
        "portion": "time_suggestions",
        "confidence": 0.92
      }
    ],

    "constitution_applied": "composite",
    "privacy_audit": {
      "user_fields_accessed": ["goal", "learning_style", "time_constraints"],
      "private_fields_influenced": 2,
      "private_fields_exposed": 0
    }
  }
}`}</code></pre>

		<h2>Human-in-the-Loop</h2>
		<p>
			Multi-agent systems should maintain human oversight. VCP supports several patterns:
		</p>

		<h3>Approval Gates</h3>
		<pre><code>{`{
  "approval_required": {
    "threshold": "high_impact",
    "actions": [
      "schedule_commitment",
      "share_with_third_party",
      "modify_preferences"
    ],
    "timeout": "5_minutes",
    "default_action": "reject"
  }
}`}</code></pre>

		<h3>Transparency Dashboard</h3>
		<p>
			Users can see what agents are doing and intervene:
		</p>
		<ul>
			<li>Which agents are active</li>
			<li>What context each agent has accessed</li>
			<li>What actions each agent is considering</li>
			<li>Ability to pause, revoke access, or redirect</li>
		</ul>

		<h2>Example: Learning Ecosystem</h2>
		<pre><code>{`// User's learning session with multiple coordinating agents
const session = {
  user: userContext,

  agents: [
    {
      id: "agent_tutor",
      role: "primary_instruction",
      context_access: ["goal", "experience", "progress"]
    },
    {
      id: "agent_assessor",
      role: "evaluate_understanding",
      context_access: ["responses", "time_patterns"]
    },
    {
      id: "agent_scheduler",
      role: "optimize_timing",
      context_access: ["constraints", "energy_patterns"]
    },
    {
      id: "agent_wellbeing",
      role: "monitor_fatigue",
      context_access: ["session_duration", "engagement_signals"]
    }
  ],

  coordination: {
    protocol: "mediated",
    mediator: "vcp_hub",
    conflict_resolution: "hierarchy_then_escalate"
  }
};`}</code></pre>

		<h2>Security Considerations</h2>
		<ul>
			<li><strong>Agent impersonation</strong> — Verify agent identity before sharing context</li>
			<li><strong>Context leakage</strong> — Audit all context sharing between agents</li>
			<li><strong>Collusion</strong> — Monitor for agents combining data inappropriately</li>
			<li><strong>Cascade failures</strong> — Isolate agent failures to prevent system-wide issues</li>
		</ul>

		<h2>Next Steps</h2>
		<ul>
			<li><a href="/demos/multi-agent/negotiation">Negotiation Demo</a> — Watch agents negotiate in real-time</li>
			<li><a href="/demos/multi-agent/policy-design">Policy Design Demo</a> — Multi-stakeholder constitutional design</li>
			<li><a href="/docs/privacy-architecture">Privacy Architecture</a> — How privacy is preserved in multi-agent systems</li>
		</ul>
	{/snippet}
</DocsLayout>
