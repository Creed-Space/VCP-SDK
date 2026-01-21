import { h as head } from "../../../../chunks/index2.js";
import { D as DocsLayout } from "../../../../chunks/DocsLayout.js";
function _page($$renderer) {
  head("d104oh", $$renderer, ($$renderer2) => {
    $$renderer2.title(($$renderer3) => {
      $$renderer3.push(`<title>API Reference - VCP Documentation</title>`);
    });
    $$renderer2.push(`<meta name="description" content="Full API documentation for all VCP library functions."/>`);
  });
  {
    let children = function($$renderer2) {
      $$renderer2.push(`<h2>Installation</h2> <pre><code>npm install @creed-space/vcp</code></pre> <h2>Core Types</h2> <h3>VCPContext</h3> <p>The main context object containing all user preferences and settings.</p> <pre><code>interface VCPContext {
  vcp_version: string;           // Protocol version
  profile_id: string;            // Unique identifier
  created?: string;              // ISO date
  updated?: string;              // ISO date

  constitution: ConstitutionReference;
  public_profile: PublicProfile;
  portable_preferences?: PortablePreferences;
  current_skills?: CurrentSkills;
  constraints?: ConstraintFlags;
  availability?: Availability;
  sharing_settings?: SharingSettings;
  private_context?: PrivateContext;
}</code></pre> <h3>ConstitutionReference</h3> <pre><code>interface ConstitutionReference {
  id: string;              // Constitution identifier
  version: string;         // Version string
  persona?: PersonaType;   // Interaction style
  adherence?: number;      // 1-5, how strictly to follow
  scopes?: ScopeType[];    // Applicable domains
}</code></pre> <h3>PublicProfile</h3> <pre><code>interface PublicProfile {
  display_name?: string;
  goal?: string;
  experience?: ExperienceLevel;  // beginner | intermediate | advanced | expert
  learning_style?: LearningStyle; // visual | auditory | hands_on | reading | mixed
  pace?: Pace;                   // intensive | steady | relaxed
  motivation?: Motivation;       // career | stress_relief | social | achievement | curiosity

  // Professional fields
  role?: string;
  team?: string;
  tenure_years?: number;
  career_goal?: string;
  career_timeline?: string;
}</code></pre> <h3>PortablePreferences</h3> <pre><code>interface PortablePreferences {
  noise_mode?: NoiseMode;           // normal | quiet_preferred | silent_required
  session_length?: SessionLength;   // 15_minutes | 30_minutes | 60_minutes | flexible
  pressure_tolerance?: PressureTolerance; // high | medium | low
  budget_range?: BudgetRange;       // unlimited | high | medium | low | free_only
  feedback_style?: FeedbackStyle;   // direct | encouraging | detailed | minimal
}</code></pre> <h3>ConstraintFlags</h3> <pre><code>interface ConstraintFlags {
  time_limited?: boolean;
  budget_limited?: boolean;
  noise_restricted?: boolean;
  energy_variable?: boolean;
  schedule_irregular?: boolean;
  mobility_limited?: boolean;
  health_considerations?: boolean;
}</code></pre> <h3>PrivateContext</h3> <pre><code>interface PrivateContext {
  _note?: string;        // Internal documentation
  [key: string]: unknown; // Any private values
}</code></pre> <h2>Encoding Functions</h2> <h3>encodeContextToCSM1</h3> <p>Encodes a VCP context into CSM-1 token format.</p> <pre><code>import { encodeContextToCSM1 } from '@creed-space/vcp';

const token = encodeContextToCSM1(context);
// Returns:
// VCP:1.0:user_001
// C:learning-assistant@1.0
// P:muse:3
// ...</code></pre> <h4>Parameters</h4> <table><thead><tr><th>Name</th><th>Type</th><th>Description</th></tr></thead><tbody><tr><td>ctx</td><td>VCPContext</td><td>The context to encode</td></tr></tbody></table> <h4>Returns</h4> <p><code>string</code> — CSM-1 formatted token</p> <h3>formatTokenForDisplay</h3> <p>Wraps a CSM-1 token in a box for visual display.</p> <pre><code>import { formatTokenForDisplay } from '@creed-space/vcp';

const boxed = formatTokenForDisplay(token);
// Returns:
// ┌────────────────────────────────────────┐
// │ VCP:1.0:user_001                       │
// │ ...                                    │
// └────────────────────────────────────────┘</code></pre> <h3>parseCSM1Token</h3> <p>Parses a CSM-1 token back into key-value components.</p> <pre><code>import { parseCSM1Token } from '@creed-space/vcp';

const parsed = parseCSM1Token(token);
// Returns:
// {
//   VCP: "1.0:user_001",
//   C: "learning-assistant@1.0",
//   P: "muse:3",
//   ...
// }</code></pre> <h2>Utility Functions</h2> <h3>getEmojiLegend</h3> <p>Returns an array of emoji shortcodes and their meanings.</p> <pre><code>import { getEmojiLegend } from '@creed-space/vcp';

const legend = getEmojiLegend();
// Returns:
// [
//   { emoji: '🔇', meaning: 'quiet mode' },
//   { emoji: '💰', meaning: 'budget tier' },
//   ...
// ]</code></pre> <h3>getTransmissionSummary</h3> <p>Analyzes a context and returns what would be transmitted vs withheld.</p> <pre><code>import { getTransmissionSummary } from '@creed-space/vcp';

const summary = getTransmissionSummary(context);
// Returns:
// {
//   transmitted: ['goal', 'experience', 'learning_style'],
//   withheld: ['work_situation', 'housing_situation'],
//   influencing: ['budget_limited', 'time_limited']
// }</code></pre> <h2>Constants</h2> <h3>CONSTRAINT_EMOJI</h3> <p>Mapping of constraint flags to emoji shortcodes.</p> <pre><code>const CONSTRAINT_EMOJI = {
  noise_restricted: '🔇',
  budget_limited: '💰',
  energy_variable: '⚡',
  time_limited: '⏰',
  schedule_irregular: '📅',
  mobility_limited: '🚶',
  health_considerations: '💊'
}</code></pre> <h3>PRIVATE_MARKER / SHARED_MARKER</h3> <pre><code>const PRIVATE_MARKER = '🔒';
const SHARED_MARKER = '✓';</code></pre> <h2>Enums</h2> <h3>PersonaType</h3> <pre><code>type PersonaType = 'muse' | 'ambassador' | 'godparent' | 'sentinel' | 'anchor' | 'nanny';</code></pre> <h3>ExperienceLevel</h3> <pre><code>type ExperienceLevel = 'beginner' | 'intermediate' | 'advanced' | 'expert';</code></pre> <h3>LearningStyle</h3> <pre><code>type LearningStyle = 'visual' | 'auditory' | 'hands_on' | 'reading' | 'mixed';</code></pre> <h3>NoiseMode</h3> <pre><code>type NoiseMode = 'normal' | 'quiet_preferred' | 'silent_required';</code></pre> <h3>SessionLength</h3> <pre><code>type SessionLength = '15_minutes' | '30_minutes' | '60_minutes' | 'flexible';</code></pre> <h3>BudgetRange</h3> <pre><code>type BudgetRange = 'unlimited' | 'high' | 'medium' | 'low' | 'free_only';</code></pre> <h3>ScopeType</h3> <pre><code>type ScopeType = 'work' | 'education' | 'creativity' | 'health' | 'privacy'
  | 'family' | 'finance' | 'social' | 'legal' | 'safety';</code></pre> <h2>Audit Types</h2> <h3>AuditEntry</h3> <pre><code>interface AuditEntry {
  id: string;
  timestamp: string;              // ISO date
  event_type: AuditEventType;
  platform_id?: string;
  data_shared?: string[];         // Fields that were shared
  data_withheld?: string[];       // Fields that were withheld
  private_fields_influenced?: number; // Count of private fields that shaped output
  private_fields_exposed?: number;    // Always 0 in valid VCP
  details?: Record&lt;string, unknown>;
}</code></pre> <h3>AuditEventType</h3> <pre><code>type AuditEventType =
  | 'context_shared'
  | 'context_withheld'
  | 'consent_granted'
  | 'consent_revoked'
  | 'progress_synced'
  | 'recommendation_generated'
  | 'skip_requested'
  | 'adjustment_recorded';</code></pre> <h2>Platform Types</h2> <h3>PlatformManifest</h3> <pre><code>interface PlatformManifest {
  platform_id: string;
  platform_name: string;
  platform_type: 'learning' | 'community' | 'commerce' | 'coaching';
  version: string;
  context_requirements: {
    required: string[];
    optional: string[];
  };
  capabilities: string[];
  branding?: {
    primary_color: string;
    logo?: string;
  };
}</code></pre> <h3>FilteredContext</h3> <p>The context as seen by a specific stakeholder after privacy filtering.</p> <pre><code>interface FilteredContext {
  public: Partial&lt;PublicProfile>;
  preferences: Partial&lt;PortablePreferences>;
  constraints: ConstraintFlags;
  skills?: Partial&lt;CurrentSkills>;
}</code></pre> <h2>Next Steps</h2> <ul><li><a href="/playground">Playground</a> — Test the API interactively</li> <li><a href="/docs/concepts">Core Concepts</a> — Understand the architecture</li> <li><a href="/demos">Demos</a> — See real-world examples</li></ul>`);
    };
    DocsLayout($$renderer, {
      title: "API Reference",
      description: "Complete reference for all VCP library types and functions.",
      children
    });
  }
}
export {
  _page as default
};
