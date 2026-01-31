import{f,a as m}from"../chunks/B-m6eJpc.js";import"../chunks/8Y3p7pre.js";import{e as k,s as e,f as I,c as t,$ as V,r as n,n as T}from"../chunks/BXTPVpRI.js";import{h as N}from"../chunks/knxwa2pA.js";import{D as q}from"../chunks/DC993n7D.js";var D=f('<meta name="description" content="Understand the fundamental concepts of VCP: context, constitutions, privacy filtering."/>'),H=f(`<h2>The Problem VCP Solves</h2> <p>Modern AI systems need user context to provide personalized experiences. But traditional
			approaches create a dilemma:</p> <ul><li><strong>Share everything</strong> — Get personalization, lose privacy</li> <li><strong>Share nothing</strong> — Keep privacy, get generic responses</li></ul> <p>VCP introduces a third option: <strong>share influence without sharing information</strong>.
			The AI knows your context <em>shaped</em> the response, but not <em>what</em> that context was.</p> <h2>VCP Context Structure</h2> <p>Every VCP context has these layers:</p> <h3>1. Profile Identity</h3> <pre><code></code></pre> <h3>2. Constitution Reference</h3> <p>Points to a constitution that defines AI behavioral guidelines:</p> <pre><code></code></pre> <h3>3. Public Profile</h3> <p>Information always shared with stakeholders:</p> <pre><code></code></pre> <h3>4. Portable Preferences</h3> <p>Settings that follow you across platforms:</p> <pre><code></code></pre> <h3>5. Constraint Flags</h3> <p>Boolean flags indicating active constraints:</p> <pre><code></code></pre> <h3>6. Private Context</h3> <p>Sensitive information that influences AI but is <strong>never transmitted</strong>:</p> <pre><code></code></pre> <h2>Privacy Filtering</h2> <p>VCP implements three privacy levels:</p> <table><thead><tr><th>Level</th><th>Description</th><th>Example</th></tr></thead><tbody><tr><td><strong>Public</strong></td><td>Always shared with all stakeholders</td><td>Goal, experience level, learning style</td></tr><tr><td><strong>Consent</strong></td><td>Shared only with explicit permission</td><td>Specific preferences, availability</td></tr><tr><td><strong>Private</strong></td><td>Never transmitted, influences locally</td><td>Health, financial, personal circumstances</td></tr></tbody></table> <h3>How Private Context Works</h3> <p>When the AI generates recommendations, private context shapes the output without being exposed:</p> <ol><li>User's private context indicates financial stress</li> <li>AI prioritizes free resources over paid courses</li> <li>Stakeholder sees: "Recommended free courses based on user preferences"</li> <li>Stakeholder does <em>not</em> see: "User has financial stress"</li></ol> <h2>Constitutions</h2> <p>Constitutions are structured documents that define AI behavioral guidelines. They contain:</p> <h3>Rules</h3> <p>Weighted instructions with triggers and exceptions:</p> <pre><code></code></pre> <h3>Sharing Policies</h3> <p>Define what each stakeholder type can see:</p> <pre><code></code></pre> <h2>Personas</h2> <p>Personas define interaction styles. The same constitution can use different personas for
			different contexts:</p> <table><thead><tr><th>Persona</th><th>Style</th><th>Best For</th></tr></thead><tbody><tr><td>🎨 <strong>Muse</strong></td><td>Creative, exploratory, encouraging</td><td>Creative work, learning, exploration</td></tr><tr><td>🛡️ <strong>Sentinel</strong></td><td>Cautious, protective, conservative</td><td>Security, safety-critical decisions</td></tr><tr><td>👪 <strong>Godparent</strong></td><td>Nurturing, supportive, patient</td><td>Education, skill building, recovery</td></tr><tr><td>🤝 <strong>Ambassador</strong></td><td>Professional, diplomatic, balanced</td><td>Business, negotiations, formal contexts</td></tr><tr><td>⚓ <strong>Anchor</strong></td><td>Stable, grounding, realistic</td><td>Crisis support, reality checking</td></tr><tr><td>👶 <strong>Nanny</strong></td><td>Structured, directive, safe</td><td>Children, vulnerable users, strict guidance</td></tr></tbody></table> <h2>Audit Trails</h2> <p>VCP maintains cryptographically verifiable audit trails of all data sharing:</p> <pre><code></code></pre> <h2>Next Steps</h2> <ul><li><a href="/docs/csm1-specification">CSM-1 Specification</a> — The token format in detail</li> <li><a href="/docs/api-reference">API Reference</a> — All VCP library functions</li> <li><a href="/demos">Interactive Demos</a> — See VCP in action</li></ul>`,1);function W(v){N("mhazmq",h=>{var r=D();k(()=>{V.title="Core Concepts - VCP Documentation"}),m(h,r)}),q(v,{title:"Core Concepts",description:"Understanding VCP's architecture and design principles.",children:r=>{var u=H(),i=e(I(u),14),_=t(i);_.textContent=`{
  vcp_version: "1.0",
  profile_id: "user_001",  // Unique identifier
  created: "2026-01-15",
  updated: "2026-01-21"
}`,n(i);var o=e(i,6),y=t(o);y.textContent=`{
  constitution: {
    id: "learning-assistant",  // Which constitution
    version: "1.0",            // Specific version
    persona: "muse",           // Interaction style
    adherence: 3,              // How strictly to follow (1-5)
    scopes: ["education", "creativity"]  // Applicable domains
  }
}`,n(o);var s=e(o,6),x=t(s);x.textContent=`{
  public_profile: {
    display_name: "Alex",
    goal: "learn_guitar",
    experience: "beginner",
    learning_style: "visual",
    pace: "relaxed",
    motivation: "stress_relief"
  }
}`,n(s);var a=e(s,6),b=t(a);b.textContent=`{
  portable_preferences: {
    noise_mode: "quiet_preferred",  // Audio environment
    session_length: "30_minutes",   // Preferred duration
    budget_range: "low",            // Spending tier
    pressure_tolerance: "medium",   // Challenge appetite
    feedback_style: "encouraging"   // How to receive feedback
  }
}`,n(a);var d=e(a,6),C=t(d);C.textContent=`{
  constraints: {
    time_limited: true,          // Has time pressure
    budget_limited: true,        // Has budget constraints
    noise_restricted: true,      // Needs quiet environment
    energy_variable: false,      // Energy levels stable
    health_considerations: false // No health factors
  }
}`,n(d);var l=e(d,6),P=t(l);P.textContent=`{
  private_context: {
    _note: "These values shape recommendations but are never shared",
    work_situation: "unemployed",
    housing_situation: "living_with_parents",
    health_condition: "chronic_fatigue",
    financial_stress: "high"
  }
}`,n(l);var c=e(l,22),w=t(c);w.textContent=`{
  rules: [
    {
      id: "respect_budget",
      weight: 0.9,
      rule: "Never recommend items exceeding user's budget tier",
      triggers: ["budget_limited"],
      exceptions: ["user explicitly requests premium options"]
    },
    {
      id: "encourage_progress",
      weight: 0.7,
      rule: "Celebrate small wins and incremental progress",
      triggers: ["motivation === 'stress_relief'"]
    }
  ]
}`,n(c);var p=e(c,6),S=t(p);S.textContent=`{
  sharing_policy: {
    "platform": {
      allowed: ["goal", "experience", "learning_style"],
      forbidden: ["private_context"],
      requires_consent: ["health_considerations"]
    },
    "coach": {
      allowed: ["progress", "struggle_areas"],
      aggregation_only: ["session_data"]
    }
  }
}`,n(p);var g=e(p,12),A=t(g);A.textContent=`{
  audit_entry: {
    id: "aud_001",
    timestamp: "2026-01-21T10:30:00Z",
    event_type: "context_shared",
    platform_id: "justinguitar",
    data_shared: ["goal", "experience", "learning_style"],
    data_withheld: ["private_context"],
    private_fields_influenced: 2,  // Private data shaped output
    private_fields_exposed: 0      // Always 0 in valid VCP
  }
}`,n(g),T(4),m(r,u)},$$slots:{default:!0}})}export{W as component};
