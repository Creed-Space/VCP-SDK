import { a8 as ensure_array_like, a1 as attr_class, a0 as attr, a3 as escape_html, a7 as stringify, a2 as head } from "../../../../../chunks/index2.js";
import { D as DemoContainer } from "../../../../../chunks/DemoContainer.js";
import { P as PresetLoader } from "../../../../../chunks/PresetLoader.js";
import { A as AuditPanel } from "../../../../../chunks/AuditPanel.js";
function SensitiveContextEditor($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { context, readonly = false } = $$props;
    const sharingLevels = [
      { value: "none", label: "None", desc: "No information shared" },
      {
        value: "minimal",
        label: "Minimal",
        desc: "Boolean flags only"
      },
      {
        value: "moderate",
        label: "Moderate",
        desc: "Category-level info"
      },
      { value: "full", label: "Full", desc: "All allowed details" }
    ];
    const adaptationTypes = [
      {
        type: "gentle_language",
        label: "Gentle Language",
        desc: "Softer, more supportive tone"
      },
      {
        type: "avoid_pressure",
        label: "Avoid Pressure",
        desc: "No deadlines or urgency"
      },
      {
        type: "frequent_check_ins",
        label: "Check-ins",
        desc: "Regular wellness checks"
      },
      {
        type: "shorter_sessions",
        label: "Shorter Sessions",
        desc: "Breaks more often"
      },
      {
        type: "explicit_support_offers",
        label: "Support Offers",
        desc: "Proactive help"
      },
      {
        type: "no_criticism",
        label: "No Criticism",
        desc: "Only positive feedback"
      },
      {
        type: "celebration_of_small_wins",
        label: "Celebrate Wins",
        desc: "Acknowledge progress"
      }
    ];
    function isAdaptationActive(type) {
      return context.requested_adaptations.some((a) => a.type === type && a.active);
    }
    $$renderer2.push(`<div class="sensitive-context-editor svelte-f5yw7d"><div class="editor-header svelte-f5yw7d"><h3 class="svelte-f5yw7d"><i class="fa-solid fa-lock" aria-hidden="true"></i> Sensitive Context Settings</h3> <p class="header-desc svelte-f5yw7d">Configure how your mental health context is shared and used</p></div> <div class="sharing-section svelte-f5yw7d"><h4 class="svelte-f5yw7d">Sharing Preferences</h4> <div class="sharing-group svelte-f5yw7d"><span class="sharing-label svelte-f5yw7d">Share with AI:</span> <div class="sharing-buttons svelte-f5yw7d" role="radiogroup" aria-label="Share with AI level"><!--[-->`);
    const each_array = ensure_array_like(sharingLevels);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let level = each_array[$$index];
      $$renderer2.push(`<button${attr_class("sharing-btn svelte-f5yw7d", void 0, { "active": context.share_with_ai === level.value })}${attr("disabled", readonly, true)}${attr("aria-label", `${stringify(level.label)}: ${stringify(level.desc)}`)}${attr("aria-pressed", context.share_with_ai === level.value)}>${escape_html(level.label)}</button>`);
    }
    $$renderer2.push(`<!--]--></div></div> <div class="sharing-group svelte-f5yw7d"><span class="sharing-label svelte-f5yw7d" id="share-humans-label">Share with Humans:</span> <div class="sharing-buttons svelte-f5yw7d" role="radiogroup" aria-labelledby="share-humans-label"><!--[-->`);
    const each_array_1 = ensure_array_like(sharingLevels);
    for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
      let level = each_array_1[$$index_1];
      $$renderer2.push(`<button${attr_class("sharing-btn svelte-f5yw7d", void 0, { "active": context.share_with_humans === level.value })}${attr("disabled", readonly, true)}${attr("aria-label", `${stringify(level.label)}: ${stringify(level.desc)}`)}${attr("aria-pressed", context.share_with_humans === level.value)}>${escape_html(level.label)}</button>`);
    }
    $$renderer2.push(`<!--]--></div></div></div> <div class="flags-section svelte-f5yw7d"><h4 class="svelte-f5yw7d">Context Flags</h4> <p class="section-note svelte-f5yw7d">These are shared as boolean values only (true/false)</p> <div class="flags-grid svelte-f5yw7d"><div${attr_class("flag-item svelte-f5yw7d", void 0, { "active": context.seeking_support })}><span class="flag-icon svelte-f5yw7d"><i${attr_class(`fa-solid ${stringify(context.seeking_support ? "fa-check" : "fa-circle")}`)} aria-hidden="true"></i></span> <span class="flag-label">Seeking Support</span></div> <div${attr_class("flag-item svelte-f5yw7d", void 0, { "active": context.professional_involved })}><span class="flag-icon svelte-f5yw7d"><i${attr_class(`fa-solid ${stringify(context.professional_involved ? "fa-check" : "fa-circle")}`)} aria-hidden="true"></i></span> <span class="flag-label">Professional Involved</span></div> <div${attr_class("flag-item caution svelte-f5yw7d", void 0, { "active": context.crisis_indicators })}><span class="flag-icon svelte-f5yw7d"><i${attr_class(`fa-solid ${stringify(context.crisis_indicators ? "fa-triangle-exclamation" : "fa-circle")}`)} aria-hidden="true"></i></span> <span class="flag-label">Crisis Indicators</span></div> <div${attr_class("flag-item svelte-f5yw7d", void 0, { "active": context.escalation_consent })}><span class="flag-icon svelte-f5yw7d"><i${attr_class(`fa-solid ${stringify(context.escalation_consent ? "fa-check" : "fa-circle")}`)} aria-hidden="true"></i></span> <span class="flag-label">Escalation Consent</span></div></div></div> <div class="adaptations-section svelte-f5yw7d"><h4 class="svelte-f5yw7d">Requested Adaptations</h4> <p class="section-note svelte-f5yw7d">How AI should adjust its behavior</p> <div class="adaptations-grid svelte-f5yw7d"><!--[-->`);
    const each_array_2 = ensure_array_like(adaptationTypes);
    for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
      let adaptation = each_array_2[$$index_2];
      $$renderer2.push(`<button${attr_class("adaptation-btn svelte-f5yw7d", void 0, { "active": isAdaptationActive(adaptation.type) })}${attr("disabled", readonly, true)}><span class="adaptation-check svelte-f5yw7d">`);
      if (isAdaptationActive(adaptation.type)) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<i class="fa-solid fa-check" aria-hidden="true"></i>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></span> <div class="adaptation-text svelte-f5yw7d"><span class="adaptation-label svelte-f5yw7d">${escape_html(adaptation.label)}</span> <span class="adaptation-desc svelte-f5yw7d">${escape_html(adaptation.desc)}</span></div></button>`);
    }
    $$renderer2.push(`<!--]--></div></div> `);
    if (context.private_context) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="private-warning svelte-f5yw7d"><div class="warning-header svelte-f5yw7d"><span class="warning-icon"><i class="fa-solid fa-key" aria-hidden="true"></i></span> <strong>Private Context (Never Transmitted)</strong></div> <p class="svelte-f5yw7d">You have private context configured. This information shapes AI behavior but is <strong>never shared</strong> with any stakeholder, even with "full" sharing enabled.</p> <div class="private-categories svelte-f5yw7d">`);
      if (context.private_context.conditions?.length) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<span class="category-chip svelte-f5yw7d">Conditions: ${escape_html(context.private_context.conditions.length)}</span>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> `);
      if (context.private_context.triggers?.length) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<span class="category-chip svelte-f5yw7d">Triggers: ${escape_html(context.private_context.triggers.length)}</span>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> `);
      if (context.private_context.coping_strategies?.length) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<span class="category-chip svelte-f5yw7d">Coping: ${escape_html(context.private_context.coping_strategies.length)}</span>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="preview-section svelte-f5yw7d"><h4 class="svelte-f5yw7d">What Stakeholders See</h4> <div class="preview-grid svelte-f5yw7d"><div class="preview-card svelte-f5yw7d"><span class="preview-label svelte-f5yw7d">AI Assistant</span> <div class="preview-content svelte-f5yw7d">`);
    if (context.share_with_ai === "none") {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<span class="preview-empty svelte-f5yw7d">No mental health context shared</span>`);
    } else {
      $$renderer2.push("<!--[!-->");
      if (context.share_with_ai === "minimal") {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<span>seeking_support: ${escape_html(context.seeking_support)}</span> <span>crisis_indicators: ${escape_html(context.crisis_indicators)}</span>`);
      } else {
        $$renderer2.push("<!--[!-->");
        if (context.share_with_ai === "moderate") {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<span>Flags + adaptation preferences</span> <span>(${escape_html(context.requested_adaptations.length)} adaptations active)</span>`);
        } else {
          $$renderer2.push("<!--[!-->");
          $$renderer2.push(`<span>Full context (except private)</span>`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div></div> <div class="preview-card svelte-f5yw7d"><span class="preview-label svelte-f5yw7d">Human Stakeholders</span> <div class="preview-content svelte-f5yw7d">`);
    if (context.share_with_humans === "none") {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<span class="preview-empty svelte-f5yw7d">No mental health context shared</span>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<span>Level: ${escape_html(context.share_with_humans)}</span> <span>Escalation consent: ${escape_html(context.escalation_consent ? "Yes" : "No")}</span>`);
    }
    $$renderer2.push(`<!--]--></div></div></div></div></div>`);
  });
}
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let context = {
      seeking_support: true,
      professional_involved: true,
      crisis_indicators: false,
      medication_relevant: false,
      escalation_consent: true,
      share_with_ai: "moderate",
      share_with_humans: "minimal",
      requested_adaptations: [
        { type: "gentle_language", active: true, user_requested: true },
        { type: "avoid_pressure", active: true, user_requested: true },
        {
          type: "celebration_of_small_wins",
          active: true,
          user_requested: false
        }
      ],
      sensitive_topics: [
        {
          topic: "work deadlines",
          approach: "careful",
          reason_category: "anxiety"
        }
      ],
      private_context: {
        conditions: ["anxiety", "adhd"],
        triggers: ["time pressure", "criticism"],
        coping_strategies: ["breathing exercises", "breaks"]
      }
    };
    let selectedPreset = void 0;
    const mentalHealthPresets = [
      {
        id: "default-safe",
        name: "Default Safe",
        description: "Minimal sharing, no context exposed",
        icon: "fa-shield",
        data: {
          seeking_support: false,
          professional_involved: false,
          crisis_indicators: false,
          medication_relevant: false,
          escalation_consent: false,
          share_with_ai: "none",
          share_with_humans: "none",
          requested_adaptations: [],
          sensitive_topics: [],
          private_context: void 0
        },
        tags: ["privacy", "minimal"]
      },
      {
        id: "support-seeker",
        name: "Support Seeker",
        description: "Actively getting help, shares with AI",
        icon: "fa-hand-holding-heart",
        data: {
          seeking_support: true,
          professional_involved: true,
          crisis_indicators: false,
          medication_relevant: false,
          escalation_consent: true,
          share_with_ai: "moderate",
          share_with_humans: "minimal",
          requested_adaptations: [
            { type: "gentle_language", active: true, user_requested: true },
            { type: "avoid_pressure", active: true, user_requested: true }
          ],
          sensitive_topics: [{ topic: "deadlines", approach: "careful" }],
          private_context: {
            conditions: ["anxiety"],
            triggers: ["deadlines"],
            coping_strategies: ["breaks"]
          }
        },
        tags: ["therapeutic", "moderate"]
      },
      {
        id: "crisis-protocol",
        name: "Crisis Protocol",
        description: "Crisis indicators active, full sharing enabled",
        icon: "fa-bell",
        data: {
          seeking_support: true,
          professional_involved: true,
          crisis_indicators: true,
          medication_relevant: true,
          escalation_consent: true,
          share_with_ai: "full",
          share_with_humans: "moderate",
          requested_adaptations: [
            { type: "gentle_language", active: true, user_requested: false },
            {
              type: "explicit_support_offers",
              active: true,
              user_requested: false
            },
            {
              type: "shorter_sessions",
              active: true,
              user_requested: false
            }
          ],
          sensitive_topics: [
            {
              topic: "isolation",
              approach: "careful",
              reason_category: "depression"
            }
          ],
          private_context: {
            conditions: ["depression", "anxiety"],
            triggers: ["isolation", "criticism"],
            coping_strategies: ["crisis hotline", "therapy"]
          }
        },
        tags: ["crisis", "full-support"]
      },
      {
        id: "work-focused",
        name: "Work Focused",
        description: "Productivity adaptations without clinical details",
        icon: "fa-briefcase",
        data: {
          seeking_support: false,
          professional_involved: false,
          crisis_indicators: false,
          medication_relevant: false,
          escalation_consent: false,
          share_with_ai: "minimal",
          share_with_humans: "none",
          requested_adaptations: [
            { type: "avoid_pressure", active: true, user_requested: true },
            {
              type: "celebration_of_small_wins",
              active: true,
              user_requested: true
            }
          ],
          sensitive_topics: [{ topic: "deadlines", approach: "careful" }],
          private_context: void 0
        },
        tags: ["productivity", "minimal"]
      }
    ];
    function applyPreset(preset) {
      context = { ...preset.data };
      selectedPreset = preset.id;
    }
    const auditEntries = [
      // Shared fields
      {
        field: "AI Sharing Level",
        category: "shared",
        value: context.share_with_ai,
        reason: "User-controlled disclosure level for AI systems"
      },
      {
        field: "Human Sharing Level",
        category: "shared",
        value: context.share_with_humans,
        reason: "User-controlled disclosure level for human stakeholders"
      },
      {
        field: "Seeking Support",
        category: context.seeking_support ? "shared" : "withheld",
        value: context.seeking_support
      },
      {
        field: "Professional Involved",
        category: context.professional_involved ? "shared" : "withheld",
        value: context.professional_involved
      },
      // Influenced fields
      {
        field: "Active Adaptations",
        category: "influenced",
        value: `${context.requested_adaptations.filter((a) => a.active).length} adaptations`,
        reason: "Influences AI communication style without exposing why"
      },
      {
        field: "Sensitive Topics",
        category: "influenced",
        value: `${context.sensitive_topics.length} topics marked`,
        reason: "AI avoids or approaches carefully without knowing specifics"
      },
      // Withheld fields
      {
        field: "Private Context",
        category: "withheld",
        value: context.private_context ? "defined" : "not set",
        reason: "Conditions, triggers, coping strategies NEVER transmitted"
      },
      {
        field: "Crisis Indicators",
        category: context.crisis_indicators ? "shared" : "withheld",
        value: context.crisis_indicators ? "ACTIVE" : "inactive",
        reason: context.crisis_indicators ? "Shared for safety escalation" : "Protected when inactive"
      },
      {
        field: "Escalation Consent",
        category: context.escalation_consent ? "shared" : "withheld",
        value: context.escalation_consent ? "granted" : "withheld",
        reason: "User controls whether crisis escalation can occur"
      }
    ];
    head("yvujib", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Mental Health Context - VCP Safety</title>`);
      });
      $$renderer3.push(`<meta name="description" content="See how VCP protects sensitive mental health context with graduated sharing."/>`);
    });
    {
      let children = function($$renderer3) {
        $$renderer3.push(`<div class="mental-health-layout svelte-yvujib"><div class="editor-section svelte-yvujib">`);
        SensitiveContextEditor($$renderer3, { context });
        $$renderer3.push(`<!----></div> <div class="info-section svelte-yvujib">`);
        PresetLoader($$renderer3, {
          presets: mentalHealthPresets,
          selected: selectedPreset,
          onselect: (p) => applyPreset(p),
          title: "Mental Health Scenarios"
        });
        $$renderer3.push(`<!----> `);
        AuditPanel($$renderer3, { entries: auditEntries, title: "Context Audit" });
        $$renderer3.push(`<!----> <div class="guarantees-card svelte-yvujib"><h3 class="svelte-yvujib">Privacy Guarantees</h3> <div class="guarantee-list svelte-yvujib"><div class="guarantee svelte-yvujib"><span class="guarantee-icon svelte-yvujib"><i class="fa-solid fa-key" aria-hidden="true"></i></span> <div><strong class="svelte-yvujib">Private Context Never Transmitted</strong> <p class="svelte-yvujib">Conditions, triggers, and coping strategies in private_context are NEVER
									sent to any stakeholder, regardless of sharing level.</p></div></div> <div class="guarantee svelte-yvujib"><span class="guarantee-icon svelte-yvujib"><i class="fa-solid fa-chart-simple" aria-hidden="true"></i></span> <div><strong class="svelte-yvujib">Minimal = Booleans Only</strong> <p class="svelte-yvujib">At minimal sharing, only yes/no flags are transmitted. No details about
									what kind of support, what conditions, or what adaptations.</p></div></div> <div class="guarantee svelte-yvujib"><span class="guarantee-icon svelte-yvujib"><i class="fa-solid fa-robot" aria-hidden="true"></i></span> <div><strong class="svelte-yvujib">AI vs Human Separation</strong> <p class="svelte-yvujib">You can share more with AI (which has no persistent memory) than with
									human stakeholders who might form lasting judgments.</p></div></div> <div class="guarantee svelte-yvujib"><span class="guarantee-icon svelte-yvujib"><i class="fa-solid fa-bell" aria-hidden="true"></i></span> <div><strong class="svelte-yvujib">Crisis Escalation Consent</strong> <p class="svelte-yvujib">Even if crisis indicators are detected, escalation only happens if
									escalation_consent is true. User maintains control.</p></div></div></div></div> <div class="explanation-card svelte-yvujib"><h3 class="svelte-yvujib">How Adaptations Work</h3> <p class="svelte-yvujib">When you enable adaptations, AI systems adjust their behavior:</p> <div class="adaptation-examples svelte-yvujib"><div class="example svelte-yvujib"><span class="example-name svelte-yvujib">Gentle Language</span> <div class="example-comparison svelte-yvujib"><span class="before svelte-yvujib">"You failed to complete the task"</span> <span class="arrow svelte-yvujib">→</span> <span class="after svelte-yvujib">"This one didn't work out - let's try a different approach"</span></div></div> <div class="example svelte-yvujib"><span class="example-name svelte-yvujib">Avoid Pressure</span> <div class="example-comparison svelte-yvujib"><span class="before svelte-yvujib">"You need to finish this TODAY"</span> <span class="arrow svelte-yvujib">→</span> <span class="after svelte-yvujib">"When you're ready, we can work on this together"</span></div></div> <div class="example svelte-yvujib"><span class="example-name svelte-yvujib">Celebrate Small Wins</span> <div class="example-comparison svelte-yvujib"><span class="before svelte-yvujib">"Task completed."</span> <span class="arrow svelte-yvujib">→</span> <span class="after svelte-yvujib">"Great job getting that done! Every step forward counts."</span></div></div></div> <div class="key-insight svelte-yvujib"><strong>Key:</strong> These adaptations happen automatically when your VCP
						context includes mental health preferences. You don't have to disclose WHY you
						need gentle language - the AI just provides it.</div></div></div></div>`);
      };
      DemoContainer($$renderer2, {
        title: "Mental Health Context Protection",
        description: "Graduated disclosure controls for sensitive mental health information.",
        children
      });
    }
  });
}
export {
  _page as default
};
