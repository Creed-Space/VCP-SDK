import { a2 as head } from "../../../../chunks/index2.js";
import { D as DocsLayout } from "../../../../chunks/DocsLayout.js";
function _page($$renderer) {
  head("11tzv0z", $$renderer, ($$renderer2) => {
    $$renderer2.title(($$renderer3) => {
      $$renderer3.push(`<title>CSM-1 Specification - VCP Documentation</title>`);
    });
    $$renderer2.push(`<meta name="description" content="Complete specification for the Compact State Message (CSM-1) token format."/>`);
  });
  {
    let children = function($$renderer2) {
      $$renderer2.push(`<h2>Overview</h2> <p><strong>CSM-1 (Compact State Message v1)</strong> is a human-readable token format for encoding
			VCP context. It's designed to be:</p> <ul><li><strong>Compact</strong> — Minimal bytes, fits in headers and logs</li> <li><strong>Human-readable</strong> — Developers can inspect tokens visually</li> <li><strong>Privacy-preserving</strong> — Private data is represented by markers only</li> <li><strong>Versioned</strong> — Forward compatible with future extensions</li></ul> <h2>Token Format</h2> <p>A CSM-1 token consists of 7 lines:</p> <pre><code>VCP:&lt;version>:&lt;profile_id>
C:&lt;constitution_id>@&lt;version>
P:&lt;persona>:&lt;adherence>
G:&lt;goal>:&lt;experience>:&lt;learning_style>
X:&lt;constraint_flags>
F:&lt;active_flags>
S:&lt;private_markers></code></pre> <h3>Example Token</h3> <pre><code>VCP:1.0:user_001
C:learning-assistant@1.0
P:muse:3
G:learn_guitar:beginner:visual
X:&lt;i class="fa-solid fa-volume-xmark" aria-hidden="true">&lt;/i>quiet:&lt;i class="fa-solid fa-coins" aria-hidden="true">&lt;/i>low:&lt;i class="fa-solid fa-stopwatch" aria-hidden="true">&lt;/i>30minutes
F:time_limited|budget_limited
S:&lt;i class="fa-solid fa-lock" aria-hidden="true">&lt;/i>work|&lt;i class="fa-solid fa-lock" aria-hidden="true">&lt;/i>housing</code></pre> <h2>Line-by-Line Breakdown</h2> <h3>Line 1: Header</h3> <pre><code>VCP:&lt;version>:&lt;profile_id></code></pre> <table><thead><tr><th>Field</th><th>Type</th><th>Description</th></tr></thead><tbody><tr><td>version</td><td>string</td><td>VCP protocol version (e.g., "1.0")</td></tr><tr><td>profile_id</td><td>string</td><td>Unique user/profile identifier</td></tr></tbody></table> <h3>Line 2: Constitution Reference</h3> <pre><code>C:&lt;constitution_id>@&lt;version></code></pre> <table><thead><tr><th>Field</th><th>Type</th><th>Description</th></tr></thead><tbody><tr><td>constitution_id</td><td>string</td><td>Constitution identifier (e.g., "learning-assistant")</td></tr><tr><td>version</td><td>string</td><td>Constitution version</td></tr></tbody></table> <h3>Line 3: Persona</h3> <pre><code>P:&lt;persona>:&lt;adherence></code></pre> <table><thead><tr><th>Field</th><th>Type</th><th>Values</th></tr></thead><tbody><tr><td>persona</td><td>enum</td><td>muse, sentinel, godparent, ambassador, anchor, nanny</td></tr><tr><td>adherence</td><td>1-5</td><td>How strictly to follow constitution rules</td></tr></tbody></table> <h3>Line 4: Goal Context</h3> <pre><code>G:&lt;goal>:&lt;experience>:&lt;learning_style></code></pre> <table><thead><tr><th>Field</th><th>Type</th><th>Values</th></tr></thead><tbody><tr><td>goal</td><td>string</td><td>User's primary goal (e.g., "learn_guitar")</td></tr><tr><td>experience</td><td>enum</td><td>beginner, intermediate, advanced, expert</td></tr><tr><td>learning_style</td><td>enum</td><td>visual, auditory, hands_on, reading, mixed</td></tr></tbody></table> <h3>Line 5: Constraint Flags (X-line)</h3> <pre><code>X:&lt;emoji_flags></code></pre> <p>Colon-separated constraint markers using emoji shortcodes:</p> <table><thead><tr><th>Emoji</th><th>Meaning</th><th>Example</th></tr></thead><tbody><tr><td><i class="fa-solid fa-volume-xmark" aria-hidden="true"></i></td><td>Quiet mode preference</td><td><code><i class="fa-solid fa-volume-xmark" aria-hidden="true"></i>quiet</code></td></tr><tr><td><i class="fa-solid fa-bell-slash" aria-hidden="true"></i></td><td>Silent required</td><td><code><i class="fa-solid fa-bell-slash" aria-hidden="true"></i>silent</code></td></tr><tr><td><i class="fa-solid fa-coins" aria-hidden="true"></i></td><td>Budget tier</td><td><code><i class="fa-solid fa-coins" aria-hidden="true"></i>low</code></td></tr><tr><td>🆓</td><td>Free only</td><td><code>🆓</code></td></tr><tr><td><i class="fa-solid fa-gem" aria-hidden="true"></i></td><td>Premium budget</td><td><code><i class="fa-solid fa-gem" aria-hidden="true"></i>high</code></td></tr><tr><td><i class="fa-solid fa-bolt" aria-hidden="true"></i></td><td>Energy variable</td><td><code><i class="fa-solid fa-bolt" aria-hidden="true"></i>var</code></td></tr><tr><td>⏰</td><td>Time limited</td><td><code>⏰lim</code></td></tr><tr><td><i class="fa-solid fa-stopwatch" aria-hidden="true"></i></td><td>Session length</td><td><code><i class="fa-solid fa-stopwatch" aria-hidden="true"></i>30minutes</code></td></tr><tr><td><i class="fa-solid fa-calendar" aria-hidden="true"></i></td><td>Irregular schedule</td><td><code><i class="fa-solid fa-calendar" aria-hidden="true"></i>irreg</code></td></tr></tbody></table> <p>If no constraints: <code>X:none</code></p> <h3>Line 6: Active Flags (F-line)</h3> <pre><code>F:&lt;flag1>|&lt;flag2>|...</code></pre> <p>Pipe-separated list of currently active constraint flags:</p> <ul><li><code>time_limited</code></li> <li><code>budget_limited</code></li> <li><code>noise_restricted</code></li> <li><code>energy_variable</code></li> <li><code>schedule_irregular</code></li> <li><code>mobility_limited</code></li> <li><code>health_considerations</code></li></ul> <p>If none: <code>F:none</code></p> <h3>Line 7: Private Markers (S-line)</h3> <pre><code>S:<i class="fa-solid fa-lock" aria-hidden="true"></i>&lt;category1>|<i class="fa-solid fa-lock" aria-hidden="true"></i>&lt;category2>|...</code></pre> <p>Shows <em>categories</em> of private data that influenced the context, but <strong>never the values</strong>:</p> <ul><li><code><i class="fa-solid fa-lock" aria-hidden="true"></i>work</code> — Work-related private context exists</li> <li><code><i class="fa-solid fa-lock" aria-hidden="true"></i>housing</code> — Housing-related private context exists</li> <li><code><i class="fa-solid fa-lock" aria-hidden="true"></i>health</code> — Health-related private context exists</li> <li><code><i class="fa-solid fa-lock" aria-hidden="true"></i>financial</code> — Financial private context exists</li></ul> <p>If no private context: <code>S:none</code></p> <h2>Encoding Rules</h2> <h3>String Encoding</h3> <ul><li>All strings are UTF-8</li> <li>Spaces in values are replaced with underscores</li> <li>Colons (<code>:</code>) in values must be escaped as <code>\\:</code></li> <li>Pipes (<code>|</code>) in values must be escaped as <code>\\|</code></li></ul> <h3>Optional Fields</h3> <ul><li>Missing goal: <code>G:unset:beginner:mixed</code></li> <li>Missing persona: <code>P:muse:3</code> (default)</li> <li>Empty constraints: <code>X:none</code></li></ul> <h2>Parsing</h2> <p>To parse a CSM-1 token:</p> <pre><code>function parseCSM1(token: string) {
  const lines = token.split('\\n');
  const result = {};

  for (const line of lines) {
    const [key, ...values] = line.split(':');
    result[key] = values.join(':');
  }

  return result;
}

// Returns:
// {
//   VCP: "1.0:user_001",
//   C: "learning-assistant@1.0",
//   P: "muse:3",
//   G: "learn_guitar:beginner:visual",
//   X: "&lt;i class="fa-solid fa-volume-xmark" aria-hidden="true">&lt;/i>quiet:&lt;i class="fa-solid fa-coins" aria-hidden="true">&lt;/i>low:&lt;i class="fa-solid fa-stopwatch" aria-hidden="true">&lt;/i>30minutes",
//   F: "time_limited|budget_limited",
//   S: "&lt;i class="fa-solid fa-lock" aria-hidden="true">&lt;/i>work|&lt;i class="fa-solid fa-lock" aria-hidden="true">&lt;/i>housing"
// }</code></pre> <h2>Display Formatting</h2> <p>For visual display, tokens can be boxed:</p> <pre><code>┌────────────────────────────────────────┐
│ VCP:1.0:user_001                       │
│ C:learning-assistant@1.0               │
│ P:muse:3                               │
│ G:learn_guitar:beginner:visual         │
│ X:&lt;i class="fa-solid fa-volume-xmark" aria-hidden="true">&lt;/i>quiet:&lt;i class="fa-solid fa-coins" aria-hidden="true">&lt;/i>low:&lt;i class="fa-solid fa-stopwatch" aria-hidden="true">&lt;/i>30minutes            │
│ F:time_limited|budget_limited          │
│ S:&lt;i class="fa-solid fa-lock" aria-hidden="true">&lt;/i>work|&lt;i class="fa-solid fa-lock" aria-hidden="true">&lt;/i>housing                     │
└────────────────────────────────────────┘</code></pre> <h2>Security Considerations</h2> <h3>What CSM-1 Guarantees</h3> <ul><li>Private context values are <strong>never</strong> included in tokens</li> <li>Only category names appear in the S-line, not values</li> <li>Tokens can be logged and inspected without privacy leakage</li></ul> <h3>What CSM-1 Does NOT Do</h3> <ul><li>Encryption — Tokens are readable by anyone who receives them</li> <li>Authentication — Tokens don't prove who created them</li> <li>Integrity — Tokens can be modified in transit (use signing separately)</li></ul> <h2>Extensions</h2> <p>CSM-1 is designed for forward compatibility. Future versions may add:</p> <ul><li>Additional lines for new context types</li> <li>New emoji shortcodes for constraints</li> <li>Compression for high-volume scenarios</li></ul> <p>Parsers should ignore unrecognized lines gracefully.</p> <h2>Next Steps</h2> <ul><li><a href="/docs/api-reference">API Reference</a> — Encoding/decoding functions</li> <li><a href="/playground">Playground</a> — Build tokens interactively</li></ul>`);
    };
    DocsLayout($$renderer, {
      title: "CSM-1 Specification",
      description: "Complete specification for the Compact State Message format.",
      children
    });
  }
}
export {
  _page as default
};
