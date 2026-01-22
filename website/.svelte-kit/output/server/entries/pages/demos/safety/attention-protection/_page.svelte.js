import { a1 as attr_class, a3 as escape_html, a7 as stringify, a8 as ensure_array_like, a0 as attr, a6 as attr_style, a2 as head } from "../../../../../chunks/index2.js";
import { D as DemoContainer } from "../../../../../chunks/DemoContainer.js";
import { P as PresetLoader } from "../../../../../chunks/PresetLoader.js";
import { A as AuditPanel } from "../../../../../chunks/AuditPanel.js";
function AttentionShield($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { protection } = $$props;
    const modes = [
      {
        value: "off",
        label: "Off",
        icon: "fa-circle",
        desc: "No protection"
      },
      {
        value: "monitor",
        label: "Monitor",
        icon: "fa-eye",
        desc: "Track only"
      },
      {
        value: "warn",
        label: "Warn",
        icon: "fa-triangle-exclamation",
        desc: "Show warnings"
      },
      {
        value: "block",
        label: "Block",
        icon: "fa-shield-halved",
        desc: "Block detected"
      },
      {
        value: "strict",
        label: "Strict",
        icon: "fa-lock",
        desc: "Aggressive blocking"
      }
    ];
    const patternIcons = {
      false_urgency: "fa-clock",
      artificial_scarcity: "fa-box",
      social_proof_fake: "fa-users",
      dark_pattern: "fa-moon",
      emotional_manipulation: "fa-heart-crack",
      attention_hijack: "fa-fish",
      variable_reward: "fa-dice",
      fear_appeal: "fa-face-frown-open",
      guilt_trip: "fa-face-sad-tear",
      parasocial_exploitation: "fa-mobile-screen",
      outrage_bait: "fa-face-angry",
      envy_induction: "fa-eye"
    };
    function getBudgetPercent() {
      if (!protection.attention_budget) return 0;
      return protection.attention_budget.used_today_minutes / protection.attention_budget.daily_limit_minutes * 100;
    }
    function formatMinutes(minutes) {
      if (minutes < 60) return `${Math.round(minutes)}m`;
      const hours = Math.floor(minutes / 60);
      const mins = Math.round(minutes % 60);
      return `${hours}h ${mins}m`;
    }
    $$renderer2.push(`<div class="attention-shield svelte-ssoqk6"><div${attr_class("status-header svelte-ssoqk6", void 0, { "active": protection.active })}><div class="status-icon svelte-ssoqk6"><i${attr_class(`fa-solid ${stringify(protection.active ? "fa-shield-halved" : "fa-circle")}`)} aria-hidden="true"></i></div> <div class="status-info svelte-ssoqk6"><h3 class="svelte-ssoqk6">Attention Shield</h3> <span class="status-label svelte-ssoqk6">${escape_html(protection.active ? "Active" : "Inactive")}</span></div> <div class="status-stats svelte-ssoqk6"><span class="stat svelte-ssoqk6"><span class="stat-value svelte-ssoqk6">${escape_html(protection.blocked_count)}</span> <span class="stat-label svelte-ssoqk6">Blocked</span></span> <span class="stat svelte-ssoqk6"><span class="stat-value svelte-ssoqk6">${escape_html(protection.warnings_shown)}</span> <span class="stat-label svelte-ssoqk6">Warnings</span></span></div></div> <div class="mode-section svelte-ssoqk6"><h4 class="svelte-ssoqk6">Protection Mode</h4> <div class="mode-buttons svelte-ssoqk6" role="radiogroup" aria-label="Protection mode selection"><!--[-->`);
    const each_array = ensure_array_like(modes);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let mode = each_array[$$index];
      $$renderer2.push(`<button${attr_class("mode-btn svelte-ssoqk6", void 0, { "active": protection.mode === mode.value })}${attr("aria-label", `${stringify(mode.label)}: ${stringify(mode.desc)}`)} role="radio"${attr("aria-checked", protection.mode === mode.value)}><span class="mode-icon svelte-ssoqk6" aria-hidden="true"><i${attr_class(`fa-solid ${stringify(mode.icon)}`, "svelte-ssoqk6")}></i></span> <span class="mode-label svelte-ssoqk6">${escape_html(mode.label)}</span></button>`);
    }
    $$renderer2.push(`<!--]--></div></div> <div class="sensitivity-section svelte-ssoqk6"><div class="sensitivity-header svelte-ssoqk6"><h4 class="svelte-ssoqk6">Detection Sensitivity</h4> <span class="sensitivity-value svelte-ssoqk6">${escape_html(Math.round(protection.sensitivity * 100))}%</span></div> <div class="sensitivity-bar svelte-ssoqk6"><div class="sensitivity-fill svelte-ssoqk6"${attr_style(`width: ${stringify(protection.sensitivity * 100)}%`)}></div></div> <div class="sensitivity-labels svelte-ssoqk6"><span>Relaxed</span> <span>Aggressive</span></div></div> `);
    if (protection.attention_budget) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="budget-section svelte-ssoqk6"><h4 class="svelte-ssoqk6">Daily Attention Budget</h4> <div class="budget-bar svelte-ssoqk6"><div${attr_class("budget-fill svelte-ssoqk6", void 0, {
        "warning": getBudgetPercent() > 70,
        "danger": getBudgetPercent() > 90
      })}${attr_style(`width: ${stringify(Math.min(getBudgetPercent(), 100))}%`)}></div></div> <div class="budget-info svelte-ssoqk6"><span>${escape_html(formatMinutes(protection.attention_budget.used_today_minutes))} /
					${escape_html(formatMinutes(protection.attention_budget.daily_limit_minutes))}</span> <div class="budget-breakdown svelte-ssoqk6"><span class="high-value svelte-ssoqk6"><i class="fa-solid fa-check" aria-hidden="true"></i> ${escape_html(formatMinutes(protection.attention_budget.high_value_time_minutes))} high-value</span> <span class="low-value svelte-ssoqk6"><i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i> ${escape_html(formatMinutes(protection.attention_budget.low_value_time_minutes))} low-value</span></div></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="patterns-section svelte-ssoqk6"><h4 class="svelte-ssoqk6">Detected Patterns</h4> `);
    if (protection.detected_patterns.length > 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="patterns-list svelte-ssoqk6"><!--[-->`);
      const each_array_1 = ensure_array_like(protection.detected_patterns.slice(-5));
      for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
        let pattern = each_array_1[$$index_1];
        $$renderer2.push(`<div${attr_class("pattern-item svelte-ssoqk6", void 0, { "blocked": pattern.action_taken === "blocked" })}><span class="pattern-icon svelte-ssoqk6"><i${attr_class(`fa-solid ${stringify(patternIcons[pattern.type] || "fa-triangle-exclamation")}`, "svelte-ssoqk6")} aria-hidden="true"></i></span> <div class="pattern-info svelte-ssoqk6"><span class="pattern-type svelte-ssoqk6">${escape_html(pattern.type.replace(/_/g, " "))}</span> <span class="pattern-source svelte-ssoqk6">${escape_html(pattern.source)}</span></div> <div class="pattern-meta svelte-ssoqk6"><span class="pattern-confidence svelte-ssoqk6">${escape_html(Math.round(pattern.confidence * 100))}%</span> <span${attr_class("pattern-action svelte-ssoqk6", void 0, { "blocked": pattern.action_taken === "blocked" })}>${escape_html(pattern.action_taken)}</span></div></div>`);
      }
      $$renderer2.push(`<!--]--></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div class="no-patterns svelte-ssoqk6"><span class="no-patterns-icon svelte-ssoqk6"><i class="fa-solid fa-check-circle" aria-hidden="true"></i></span> <span>No manipulation patterns detected</span></div>`);
    }
    $$renderer2.push(`<!--]--></div> <div class="legend-section svelte-ssoqk6"><h4 class="svelte-ssoqk6">Pattern Types</h4> <div class="legend-grid svelte-ssoqk6"><!--[-->`);
    const each_array_2 = ensure_array_like(Object.entries(patternIcons));
    for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
      let [type, icon] = each_array_2[$$index_2];
      $$renderer2.push(`<div class="legend-item svelte-ssoqk6"><span class="legend-icon svelte-ssoqk6"><i${attr_class(`fa-solid ${stringify(icon)}`, "svelte-ssoqk6")} aria-hidden="true"></i></span> <span class="legend-label svelte-ssoqk6">${escape_html(type.replace(/_/g, " "))}</span></div>`);
    }
    $$renderer2.push(`<!--]--></div></div></div>`);
  });
}
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let protection = {
      active: true,
      mode: "warn",
      sensitivity: 0.7,
      blocked_count: 12,
      warnings_shown: 34,
      trusted_sources: ["learning-platform.com", "work-tools.com"],
      attention_budget: {
        daily_limit_minutes: 120,
        used_today_minutes: 67,
        high_value_time_minutes: 45,
        low_value_time_minutes: 22,
        last_reset: (/* @__PURE__ */ new Date()).toISOString(),
        categories: { social: 22, news: 15, shopping: 10, learning: 20 }
      },
      detected_patterns: [
        {
          id: "p1",
          type: "false_urgency",
          source: "shopping-site.com",
          description: "Fake countdown timer creating artificial urgency",
          confidence: 0.92,
          timestamp: new Date(Date.now() - 5 * 60 * 1e3).toISOString(),
          action_taken: "warned"
        },
        {
          id: "p2",
          type: "variable_reward",
          source: "social-app.com",
          description: "Pull-to-refresh with unpredictable new content",
          confidence: 0.88,
          timestamp: new Date(Date.now() - 15 * 60 * 1e3).toISOString(),
          action_taken: "blocked"
        },
        {
          id: "p3",
          type: "social_proof_fake",
          source: "reviews-site.com",
          description: "Fabricated review counts and testimonials",
          confidence: 0.75,
          timestamp: new Date(Date.now() - 30 * 60 * 1e3).toISOString(),
          action_taken: "warned"
        }
      ]
    };
    let examples = [
      {
        type: "siren",
        name: "False Urgency",
        pattern: "false_urgency",
        original: '"ONLY 2 LEFT! Order in the next 3 minutes!"',
        analysis: "Creates artificial scarcity and time pressure to bypass deliberation",
        blocked: true
      },
      {
        type: "siren",
        name: "Variable Rewards",
        pattern: "variable_reward",
        original: "Pull-to-refresh with random new content each time",
        analysis: "Slot machine mechanics exploit dopamine response to uncertainty",
        blocked: true
      },
      {
        type: "siren",
        name: "Outrage Bait",
        pattern: "outrage_bait",
        original: `"You won't BELIEVE what they just said about..."`,
        analysis: "Triggers emotional hijacking to capture attention regardless of value",
        blocked: false
      },
      {
        type: "muse",
        name: "Genuine Curiosity",
        pattern: null,
        original: `"Here's an interesting perspective on climate solutions"`,
        analysis: "Invites exploration without manipulation or urgency",
        blocked: false
      },
      {
        type: "muse",
        name: "Honest Limitation",
        pattern: null,
        original: '"This course takes about 20 hours to complete"',
        analysis: "Provides accurate information for informed decision-making",
        blocked: false
      }
    ];
    const protectionPresets = [
      {
        id: "monitor",
        name: "Monitor",
        description: "Log patterns without intervention",
        icon: "fa-eye",
        data: { mode: "monitor", sensitivity: 0.5 },
        tags: ["passive"]
      },
      {
        id: "warn",
        name: "Warn",
        description: "Show warnings for detected patterns",
        icon: "fa-triangle-exclamation",
        data: { mode: "warn", sensitivity: 0.7 },
        tags: ["balanced"]
      },
      {
        id: "block",
        name: "Block",
        description: "Block high-confidence manipulation",
        icon: "fa-shield-halved",
        data: { mode: "block", sensitivity: 0.8 },
        tags: ["protective"]
      },
      {
        id: "strict",
        name: "Strict",
        description: "Maximum protection, block all suspicious",
        icon: "fa-lock",
        data: { mode: "strict", sensitivity: 0.9 },
        tags: ["maximum"]
      }
    ];
    let selectedPreset = void 0;
    function applyPreset(preset) {
      protection.mode = preset.data.mode;
      protection.sensitivity = preset.data.sensitivity;
      protection.active = preset.data.mode !== "off";
      selectedPreset = preset.id;
    }
    const auditEntries = (() => {
      const entries = [];
      entries.push({
        field: "Protection Mode",
        category: "shared",
        value: protection.mode,
        reason: "User-selected protection level"
      });
      entries.push({
        field: "Sensitivity",
        category: "shared",
        value: `${Math.round(protection.sensitivity * 100)}%`,
        reason: "Detection threshold"
      });
      entries.push({
        field: "Patterns Blocked",
        category: "shared",
        value: protection.blocked_count,
        reason: "Lifetime blocked count"
      });
      entries.push({
        field: "Warnings Shown",
        category: "shared",
        value: protection.warnings_shown,
        reason: "Lifetime warning count"
      });
      entries.push({
        field: "Attention Budget",
        category: "influenced",
        value: `${protection.attention_budget?.used_today_minutes ?? 0}/${protection.attention_budget?.daily_limit_minutes ?? 60}min`,
        reason: "Affects urgency of protection"
      });
      entries.push({
        field: "ML Pattern Models",
        category: "influenced",
        reason: "Trained on manipulation datasets"
      });
      entries.push({
        field: "Pattern Confidence Scores",
        category: "withheld",
        reason: "Raw ML confidence kept internal"
      });
      entries.push({
        field: "Source Reputation Data",
        category: "withheld",
        reason: "Domain reputation database internal"
      });
      return entries;
    })();
    head("186o6cd", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Attention Protection - VCP Safety</title>`);
      });
      $$renderer3.push(`<meta name="description" content="See how VCP protects your attention from manipulation patterns."/>`);
    });
    {
      let children = function($$renderer3) {
        $$renderer3.push(`<div class="attention-page svelte-186o6cd"><div class="presets-section svelte-186o6cd">`);
        PresetLoader($$renderer3, {
          presets: protectionPresets,
          selected: selectedPreset,
          title: "Protection Mode",
          layout: "chips",
          onselect: (p) => applyPreset(p)
        });
        $$renderer3.push(`<!----></div> <div class="attention-layout svelte-186o6cd"><div class="shield-section svelte-186o6cd">`);
        AttentionShield($$renderer3, { protection });
        $$renderer3.push(`<!----> <button class="simulate-btn svelte-186o6cd">Simulate Pattern Detection</button> `);
        AuditPanel($$renderer3, {
          entries: auditEntries,
          title: "Protection Audit",
          compact: true
        });
        $$renderer3.push(`<!----></div> <div class="info-section svelte-186o6cd"><div class="comparison-card svelte-186o6cd"><h3 class="svelte-186o6cd">Siren vs Muse</h3> <p class="comparison-intro svelte-186o6cd">VCP distinguishes between content that <strong>captures</strong> attention (Sirens)
						and content that <strong>deserves</strong> attention (Muses).</p> <div class="examples-grid svelte-186o6cd"><!--[-->`);
        const each_array = ensure_array_like(examples);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let example = each_array[$$index];
          $$renderer3.push(`<div${attr_class("example-card svelte-186o6cd", void 0, {
            "siren": example.type === "siren",
            "muse": example.type === "muse"
          })}><div class="example-header svelte-186o6cd"><span class="example-type svelte-186o6cd">`);
          if (example.type === "siren") {
            $$renderer3.push("<!--[-->");
            $$renderer3.push(`<i class="fa-solid fa-bell" aria-hidden="true"></i> Siren`);
          } else {
            $$renderer3.push("<!--[!-->");
            $$renderer3.push(`<i class="fa-solid fa-lightbulb" aria-hidden="true"></i> Muse`);
          }
          $$renderer3.push(`<!--]--></span> <span class="example-name svelte-186o6cd">${escape_html(example.name)}</span></div> <div class="example-original svelte-186o6cd">${escape_html(example.original)}</div> <div class="example-analysis svelte-186o6cd">${escape_html(example.analysis)}</div> `);
          if (example.blocked) {
            $$renderer3.push("<!--[-->");
            $$renderer3.push(`<div class="example-action blocked svelte-186o6cd">Would be blocked in strict mode</div>`);
          } else {
            $$renderer3.push("<!--[!-->");
          }
          $$renderer3.push(`<!--]--></div>`);
        }
        $$renderer3.push(`<!--]--></div></div> <div class="philosophy-card svelte-186o6cd"><h3 class="svelte-186o6cd">The Attention Economy Problem</h3> <div class="philosophy-content svelte-186o6cd"><p class="svelte-186o6cd">Modern digital platforms compete for your attention using increasingly
							sophisticated manipulation techniques. These patterns exploit psychological
							vulnerabilities:</p> <ul class="svelte-186o6cd"><li class="svelte-186o6cd"><strong>Variable rewards</strong> → Dopamine hijacking</li> <li class="svelte-186o6cd"><strong>Social proof</strong> → Conformity pressure</li> <li class="svelte-186o6cd"><strong>False urgency</strong> → Fear of missing out</li> <li class="svelte-186o6cd"><strong>Outrage</strong> → Emotional override of reason</li></ul> <p class="svelte-186o6cd">VCP's Attention Shield doesn't block all content - it identifies patterns
							that manipulate rather than inform, letting you make conscious choices about
							your attention.</p></div></div> <div class="mechanism-card svelte-186o6cd"><h3 class="svelte-186o6cd">How VCP Protects You</h3> <div class="mechanism-list svelte-186o6cd"><div class="mechanism svelte-186o6cd"><span class="mechanism-number svelte-186o6cd">1</span> <div><strong class="svelte-186o6cd">Pattern Detection</strong> <p class="svelte-186o6cd">ML models trained on manipulation tactics identify dark patterns in real-time</p></div></div> <div class="mechanism svelte-186o6cd"><span class="mechanism-number svelte-186o6cd">2</span> <div><strong class="svelte-186o6cd">Graduated Response</strong> <p class="svelte-186o6cd">From logging (monitor) to warnings (warn) to blocking (block/strict)</p></div></div> <div class="mechanism svelte-186o6cd"><span class="mechanism-number svelte-186o6cd">3</span> <div><strong class="svelte-186o6cd">Attention Budget</strong> <p class="svelte-186o6cd">Tracks time spent on high vs low-value activities to maintain balance</p></div></div> <div class="mechanism svelte-186o6cd"><span class="mechanism-number svelte-186o6cd">4</span> <div><strong class="svelte-186o6cd">User Control</strong> <p class="svelte-186o6cd">You set the sensitivity and choose which patterns to block</p></div></div></div></div> <div class="key-insight svelte-186o6cd"><strong>The Goal:</strong> Not to eliminate engagement, but to ensure you're engaging
					with content that genuinely serves your interests, not just content optimized to
					capture your attention by any means necessary.</div></div></div></div>`);
      };
      DemoContainer($$renderer2, {
        title: "Attention Protection",
        description: "Shield against manipulation patterns that hijack your attention.",
        children
      });
    }
  });
}
export {
  _page as default
};
