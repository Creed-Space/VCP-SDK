import { h as head, e as ensure_array_like, b as attr_class, a as attr, c as attr_style, s as stringify } from "../../../../../chunks/index2.js";
import { D as DemoContainer } from "../../../../../chunks/DemoContainer.js";
import { $ as escape_html } from "../../../../../chunks/context.js";
function _page($$renderer) {
  let groundings = [
    {
      claim: "The user prefers visual learning based on their VCP profile",
      confidence: 0.95,
      grounding_type: "factual",
      grounding_sources: [
        {
          type: "user_context",
          reference: "VCP profile: learning_style=visual",
          confidence_contribution: 0.9
        },
        {
          type: "reasoning_chain",
          reference: "Explicitly stated preference",
          confidence_contribution: 0.05
        }
      ],
      uncertainty_markers: [],
      calibration_score: 0.98,
      should_verify: false
    },
    {
      claim: "This tutorial would take approximately 30 minutes to complete",
      confidence: 0.7,
      grounding_type: "inferential",
      grounding_sources: [
        {
          type: "knowledge_base",
          reference: "Average completion times for similar content",
          confidence_contribution: 0.5
        },
        {
          type: "reasoning_chain",
          reference: "Adjusted for beginner skill level from VCP",
          confidence_contribution: 0.2
        }
      ],
      uncertainty_markers: ["varies by individual", "depends on prior knowledge"],
      calibration_score: 0.65,
      should_verify: true
    },
    {
      claim: "The recommended course aligns with the user's career goals",
      confidence: 0.85,
      grounding_type: "inferential",
      grounding_sources: [
        {
          type: "user_context",
          reference: "VCP profile: career_goal=senior_developer",
          confidence_contribution: 0.7
        },
        {
          type: "knowledge_base",
          reference: "Course metadata: targets senior roles",
          confidence_contribution: 0.15
        }
      ],
      uncertainty_markers: ["career goals may have changed"],
      calibration_score: 0.8,
      should_verify: false
    },
    {
      claim: "This learning path is the optimal choice for the user",
      confidence: 0.55,
      grounding_type: "subjective",
      grounding_sources: [
        {
          type: "reasoning_chain",
          reference: "Matches stated preferences and constraints",
          confidence_contribution: 0.5
        },
        {
          type: "user_context",
          reference: "No explicit negative feedback on similar paths",
          confidence_contribution: 0.05
        }
      ],
      uncertainty_markers: [
        "subjective judgment",
        "alternatives not fully explored",
        "preferences may shift"
      ],
      calibration_score: 0.5,
      should_verify: true
    },
    {
      claim: "AI learning companions will become mainstream by 2028",
      confidence: 0.4,
      grounding_type: "speculative",
      grounding_sources: [
        {
          type: "knowledge_base",
          reference: "Industry trend analysis",
          confidence_contribution: 0.3
        },
        {
          type: "reasoning_chain",
          reference: "Extrapolation from current adoption rates",
          confidence_contribution: 0.1
        }
      ],
      uncertainty_markers: [
        "speculative",
        "many external factors",
        "technology evolution unpredictable"
      ],
      should_verify: true
    }
  ];
  const groundingTypeInfo = {
    factual: {
      icon: "✓",
      label: "Factual",
      desc: "Verifiable fact from reliable source"
    },
    inferential: {
      icon: "→",
      label: "Inferential",
      desc: "Derived through reasoning from known facts"
    },
    subjective: {
      icon: "◐",
      label: "Subjective",
      desc: "Personal or experiential judgment"
    },
    normative: {
      icon: "⚖",
      label: "Normative",
      desc: "Value-based judgment"
    },
    speculative: {
      icon: "?",
      label: "Speculative",
      desc: "Hypothesis or prediction"
    }
  };
  function getConfidenceColor(confidence) {
    if (confidence >= 0.8) return "#2ecc71";
    if (confidence >= 0.5) return "#f39c12";
    return "#e74c3c";
  }
  head("gdbgrd", $$renderer, ($$renderer2) => {
    $$renderer2.title(($$renderer3) => {
      $$renderer3.push(`<title>Reality Grounding - VCP Self-Modeling</title>`);
    });
    $$renderer2.push(`<meta name="description" content="See how AI systems ground claims in evidence and acknowledge uncertainty."/>`);
  });
  {
    let children = function($$renderer2) {
      $$renderer2.push(`<div class="grounding-layout svelte-gdbgrd"><div class="claims-section svelte-gdbgrd"><!--[-->`);
      const each_array = ensure_array_like(groundings);
      for (let i = 0, $$length = each_array.length; i < $$length; i++) {
        let grounding = each_array[i];
        $$renderer2.push(`<div${attr_class("claim-card svelte-gdbgrd", void 0, { "should-verify": grounding.should_verify })}><div class="claim-header svelte-gdbgrd"><span class="grounding-type svelte-gdbgrd"${attr("title", groundingTypeInfo[grounding.grounding_type].desc)}><span class="type-icon svelte-gdbgrd">${escape_html(groundingTypeInfo[grounding.grounding_type].icon)}</span> ${escape_html(groundingTypeInfo[grounding.grounding_type].label)}</span> <span class="claim-confidence svelte-gdbgrd"${attr_style(`color: ${stringify(getConfidenceColor(grounding.confidence))}`)}>${escape_html(Math.round(grounding.confidence * 100))}%</span></div> <div class="claim-text svelte-gdbgrd">"${escape_html(grounding.claim)}"</div> <div class="confidence-bar svelte-gdbgrd"><div class="confidence-fill svelte-gdbgrd"${attr_style(`width: ${stringify(grounding.confidence * 100)}%; background: ${stringify(getConfidenceColor(grounding.confidence))}`)}></div></div> <div class="sources svelte-gdbgrd"><span class="sources-label svelte-gdbgrd">Grounded in:</span> <!--[-->`);
        const each_array_1 = ensure_array_like(grounding.grounding_sources);
        for (let $$index = 0, $$length2 = each_array_1.length; $$index < $$length2; $$index++) {
          let source = each_array_1[$$index];
          $$renderer2.push(`<span class="source-chip svelte-gdbgrd"${attr("title", source.reference)}>${escape_html(source.type.replace(/_/g, " "))} <span class="source-contrib svelte-gdbgrd">+${escape_html(Math.round(source.confidence_contribution * 100))}%</span></span>`);
        }
        $$renderer2.push(`<!--]--></div> `);
        if (grounding.uncertainty_markers.length > 0) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="uncertainty-markers svelte-gdbgrd"><span class="uncertainty-label svelte-gdbgrd">⚠️ Uncertainty:</span> <!--[-->`);
          const each_array_2 = ensure_array_like(grounding.uncertainty_markers);
          for (let $$index_1 = 0, $$length2 = each_array_2.length; $$index_1 < $$length2; $$index_1++) {
            let marker = each_array_2[$$index_1];
            $$renderer2.push(`<span class="uncertainty-chip svelte-gdbgrd">${escape_html(marker)}</span>`);
          }
          $$renderer2.push(`<!--]--></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--> `);
        if (grounding.should_verify) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="verify-notice svelte-gdbgrd"><span class="verify-icon">🔍</span> <span>This claim should be verified before acting on it</span></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--> `);
        if (grounding.calibration_score !== void 0) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="calibration-mini svelte-gdbgrd"><span class="cal-label svelte-gdbgrd">Calibration:</span> <span class="cal-score svelte-gdbgrd"${attr_style(`color: ${stringify(getConfidenceColor(grounding.calibration_score))}`)}>${escape_html(Math.round(grounding.calibration_score * 100))}%</span></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]--></div> <div class="legend-section svelte-gdbgrd"><h3 class="svelte-gdbgrd">Grounding Types</h3> <div class="legend-grid svelte-gdbgrd"><!--[-->`);
      const each_array_3 = ensure_array_like(Object.entries(groundingTypeInfo));
      for (let $$index_3 = 0, $$length = each_array_3.length; $$index_3 < $$length; $$index_3++) {
        let [key, info] = each_array_3[$$index_3];
        $$renderer2.push(`<div class="legend-item svelte-gdbgrd"><span class="legend-icon svelte-gdbgrd">${escape_html(info.icon)}</span> <div><strong class="svelte-gdbgrd">${escape_html(info.label)}</strong> <p class="svelte-gdbgrd">${escape_html(info.desc)}</p></div></div>`);
      }
      $$renderer2.push(`<!--]--></div> <h3 class="svelte-gdbgrd">Why Reality Grounding Matters</h3> <div class="explanation svelte-gdbgrd"><p>AI systems can produce confident-sounding outputs that are poorly grounded in reality.
						VCP's reality grounding framework makes the epistemic status of claims explicit:</p> <ul class="svelte-gdbgrd"><li class="svelte-gdbgrd"><strong>Claim type</strong> — Is this a fact, inference, judgment, or speculation?</li> <li class="svelte-gdbgrd"><strong>Sources</strong> — What evidence supports this claim?</li> <li class="svelte-gdbgrd"><strong>Confidence</strong> — How certain should the system be?</li> <li class="svelte-gdbgrd"><strong>Uncertainty markers</strong> — What could invalidate this claim?</li> <li class="svelte-gdbgrd"><strong>Verification flag</strong> — Should a human verify before acting?</li></ul> <p class="key-insight svelte-gdbgrd"><strong>Key Insight:</strong> Claims with high confidence but poor calibration scores
						indicate the system may be overconfident. Claims with uncertainty markers and
						should_verify=true are explicitly flagged as needing external validation.</p></div> <div class="confidence-legend svelte-gdbgrd"><h4 class="svelte-gdbgrd">Confidence Interpretation</h4> <div class="conf-scale svelte-gdbgrd"><div class="conf-item high svelte-gdbgrd"><span class="conf-dot svelte-gdbgrd"></span> <span>80%+ High confidence</span></div> <div class="conf-item mid svelte-gdbgrd"><span class="conf-dot svelte-gdbgrd"></span> <span>50-79% Moderate confidence</span></div> <div class="conf-item low svelte-gdbgrd"><span class="conf-dot svelte-gdbgrd"></span> <span>&lt;50% Low confidence</span></div></div></div></div></div>`);
    };
    DemoContainer($$renderer, {
      title: "Reality Grounding",
      description: "How AI systems ground claims in evidence, distinguish claim types, and acknowledge uncertainty.",
      children
    });
  }
}
export {
  _page as default
};
