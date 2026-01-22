<script lang="ts">
	import DocsLayout from '$lib/components/docs/DocsLayout.svelte';
</script>

<svelte:head>
	<title>Privacy Architecture - VCP Documentation</title>
	<meta name="description" content="Deep dive into VCP's privacy filtering, consent mechanisms, and cryptographic audit trails." />
</svelte:head>

<DocsLayout
	title="Privacy Architecture"
	description="Deep dive into privacy filtering, consent, and audit trails."
>
	{#snippet children()}
		<h2>The Privacy Problem</h2>
		<p>
			Modern AI systems face a fundamental tension: they need context to be helpful, but
			collecting that context creates surveillance risks. Traditional approaches force users
			to choose between privacy and personalization.
		</p>
		<p>
			VCP resolves this with a key insight: <strong>AI can be influenced by information without
			that information being transmitted</strong>. Private context shapes behavior locally,
			then only the resulting recommendations—not the reasons—are shared.
		</p>

		<h2>Three Privacy Tiers</h2>

		<table>
			<thead>
				<tr>
					<th>Tier</th>
					<th>Visibility</th>
					<th>Examples</th>
					<th>How It Works</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td><strong>Public</strong></td>
					<td>All stakeholders</td>
					<td>Goal, experience level, learning style</td>
					<td>Transmitted in clear in VCP token</td>
				</tr>
				<tr>
					<td><strong>Consent</strong></td>
					<td>Approved parties only</td>
					<td>Detailed preferences, schedule</td>
					<td>Encrypted, decrypted only for authorized recipients</td>
				</tr>
				<tr>
					<td><strong>Private</strong></td>
					<td>Never transmitted</td>
					<td>Health conditions, financial stress, personal circumstances</td>
					<td>Processed locally, influences output, never leaves device</td>
				</tr>
			</tbody>
		</table>

		<h2>Private Context Flow</h2>
		<p>Here's how private context influences AI behavior without exposure:</p>

		<pre><code>{`┌─────────────────────────────────────────────────────────────┐
│                      USER'S DEVICE                          │
│  ┌─────────────────┐    ┌─────────────────────────────────┐│
│  │ Private Context │    │      VCP Processing Engine      ││
│  │                 │───▶│                                 ││
│  │ • unemployed    │    │ 1. Read private context         ││
│  │ • health issues │    │ 2. Apply constitution rules     ││
│  │ • budget stress │    │ 3. Weight recommendations       ││
│  └─────────────────┘    │ 4. Generate filtered output     ││
│                         └──────────────┬──────────────────┘│
│                                        │                    │
│                    ┌───────────────────▼───────────────────┐│
│                    │         Filtered Output               ││
│                    │ • Prioritize free resources           ││
│                    │ • Suggest flexible scheduling         ││
│                    │ • Avoid high-energy activities        ││
│                    └───────────────────┬───────────────────┘│
└────────────────────────────────────────┼────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICE                        │
│                                                             │
│  Receives: "User prefers free resources, flexible times"   │
│  Does NOT receive: Why (unemployment, health, stress)       │
│                                                             │
└─────────────────────────────────────────────────────────────┘`}</code></pre>

		<h2>Consent Management</h2>
		<p>
			Consent-tier data requires explicit user approval before sharing. VCP provides granular
			control:
		</p>

		<h3>Consent Scopes</h3>
		<pre><code>{`{
  "consent_grants": [
    {
      "recipient": "learning-platform.com",
      "scope": ["detailed_progress", "struggle_areas"],
      "granted_at": "2026-01-15T10:00:00Z",
      "expires_at": "2026-04-15T10:00:00Z",
      "revocable": true
    },
    {
      "recipient": "coach@example.com",
      "scope": ["session_recordings"],
      "granted_at": "2026-01-20T14:30:00Z",
      "requires_notification": true
    }
  ]
}`}</code></pre>

		<h3>Consent Lifecycle</h3>
		<ol>
			<li><strong>Request</strong> — Service requests access to specific data scopes</li>
			<li><strong>Review</strong> — User sees exactly what's requested and why</li>
			<li><strong>Grant/Deny</strong> — User makes informed decision</li>
			<li><strong>Audit</strong> — All access is logged with timestamps</li>
			<li><strong>Revoke</strong> — User can withdraw consent at any time</li>
		</ol>

		<h2>Cryptographic Audit Trail</h2>
		<p>
			Every data sharing event is recorded in a tamper-evident audit log:
		</p>

		<pre><code>{`{
  "audit_entry": {
    "id": "aud_2026011510300001",
    "timestamp": "2026-01-15T10:30:00.123Z",
    "event_type": "context_shared",

    "recipient": {
      "platform_id": "learning-platform.com",
      "verified": true,
      "trust_level": "standard"
    },

    "data_shared": [
      "goal",
      "experience",
      "learning_style"
    ],

    "data_withheld": [
      "private_context",
      "health_considerations"
    ],

    "influence_report": {
      "private_fields_count": 3,
      "private_fields_influenced_output": true,
      "private_fields_exposed": 0
    },

    "cryptographic_proof": {
      "hash": "sha256:a3f2b8c9d4e5...",
      "signature": "ed25519:x9y8z7...",
      "previous_hash": "sha256:b4g3h9c0d5f6..."
    }
  }
}`}</code></pre>

		<h3>Audit Verification</h3>
		<p>Users and auditors can verify the integrity of the audit trail:</p>
		<ul>
			<li><strong>Hash chain</strong> — Each entry links to the previous, detecting tampering</li>
			<li><strong>Signatures</strong> — Entries are signed by the VCP processor</li>
			<li><strong>Timestamps</strong> — Cryptographic timestamps prevent backdating</li>
			<li><strong>Zero-knowledge proofs</strong> — Prove properties without revealing data</li>
		</ul>

		<h2>Privacy-Preserving Analytics</h2>
		<p>
			Platforms may need aggregate insights without accessing individual data. VCP supports
			several privacy-preserving techniques:
		</p>

		<table>
			<thead>
				<tr>
					<th>Technique</th>
					<th>Use Case</th>
					<th>Privacy Guarantee</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Differential Privacy</td>
					<td>Aggregate statistics</td>
					<td>Individual contributions are indistinguishable</td>
				</tr>
				<tr>
					<td>Secure Aggregation</td>
					<td>Multi-party computation</td>
					<td>No party sees individual inputs</td>
				</tr>
				<tr>
					<td>Homomorphic Encryption</td>
					<td>Computation on encrypted data</td>
					<td>Data never decrypted during processing</td>
				</tr>
				<tr>
					<td>K-Anonymity</td>
					<td>Cohort analysis</td>
					<td>Individuals hidden in groups of K</td>
				</tr>
			</tbody>
		</table>

		<h2>Data Minimization</h2>
		<p>
			VCP enforces data minimization principles at every layer:
		</p>
		<ul>
			<li><strong>Collection minimization</strong> — Only gather what's needed</li>
			<li><strong>Retention limits</strong> — Auto-expire data after purpose fulfilled</li>
			<li><strong>Purpose binding</strong> — Data can only be used for stated purpose</li>
			<li><strong>Aggregation preference</strong> — Use aggregated data when individual isn't needed</li>
		</ul>

		<h2>Regulatory Compliance</h2>
		<p>
			VCP's privacy architecture supports compliance with major regulations:
		</p>
		<ul>
			<li><strong>GDPR</strong> — Right to access, rectification, erasure, portability</li>
			<li><strong>CCPA</strong> — Right to know, delete, opt-out of sale</li>
			<li><strong>COPPA</strong> — Parental consent for children's data</li>
			<li><strong>HIPAA</strong> — Health information protection (when applicable)</li>
		</ul>

		<h2>Implementation Example</h2>
		<pre><code>{`import { VCPPrivacyFilter } from 'vcp';

// Create a privacy filter with user's consent configuration
const filter = new VCPPrivacyFilter({
  publicFields: ['goal', 'experience', 'learning_style'],
  consentRequired: ['detailed_progress'],
  privateFields: ['health_condition', 'financial_stress'],
  activeConsents: user.consentGrants
});

// Filter context before sharing
const shareableContext = filter.apply(userContext, {
  recipient: 'learning-platform.com',
  purpose: 'personalized_recommendations'
});

// Result includes only authorized fields
// Private fields influenced the output but are not included
// Audit entry is automatically created`}</code></pre>

		<h2>Next Steps</h2>
		<ul>
			<li><a href="/docs/constitutional-ai">Constitutional AI</a> — How rules govern AI behavior</li>
			<li><a href="/docs/interiora">Interiora Specification</a> — Self-modeling for AI states</li>
			<li><a href="/docs/api-reference">API Reference</a> — Privacy filter functions</li>
		</ul>
	{/snippet}
</DocsLayout>
