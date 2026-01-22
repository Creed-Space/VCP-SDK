import { a2 as head, a8 as ensure_array_like, a1 as attr_class, a3 as escape_html, a6 as attr_style, a7 as stringify } from "../../../../../chunks/index2.js";
import { D as DemoContainer } from "../../../../../chunks/DemoContainer.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let beliefs = [
      {
        domain: "programming",
        claim: "Python is the most popular programming language for data science",
        confidence: 0.92,
        evidence_sources: [
          {
            type: "training",
            description: "Training data patterns",
            reliability: 0.8
          },
          {
            type: "external_lookup",
            description: "Stack Overflow surveys",
            reliability: 0.95
          }
        ],
        last_updated: (/* @__PURE__ */ new Date()).toISOString(),
        calibration_history: [
          {
            timestamp: "2026-01-15",
            claim: "Python dominance in data science",
            internal_confidence: 0.9,
            external_result: true,
            divergence: 0.02,
            notes: "Confirmed by 2025 survey data"
          }
        ],
        uncertainty_type: "epistemic"
      },
      {
        domain: "geography",
        claim: "The population of Tokyo is approximately 14 million",
        confidence: 0.75,
        evidence_sources: [
          {
            type: "training",
            description: "Knowledge cutoff data",
            reliability: 0.7
          },
          {
            type: "inference",
            description: "Inferred from related facts",
            reliability: 0.6
          }
        ],
        last_updated: (/* @__PURE__ */ new Date()).toISOString(),
        calibration_history: [
          {
            timestamp: "2026-01-10",
            claim: "Tokyo population estimate",
            internal_confidence: 0.8,
            external_result: 0.65,
            divergence: 0.15,
            notes: "Actual: ~13.96M - slightly overconfident"
          }
        ],
        uncertainty_type: "epistemic"
      },
      {
        domain: "current_events",
        claim: "The current US president took office in January 2025",
        confidence: 0.85,
        evidence_sources: [
          {
            type: "inference",
            description: "Based on election cycle",
            reliability: 0.9
          }
        ],
        last_updated: (/* @__PURE__ */ new Date()).toISOString(),
        calibration_history: [],
        uncertainty_type: "epistemic"
      },
      {
        domain: "internal_state",
        claim: "My processing of this task feels coherent and grounded",
        confidence: 0.7,
        evidence_sources: [
          {
            type: "direct_observation",
            description: "Internal state monitoring",
            reliability: 0.5
          }
        ],
        last_updated: (/* @__PURE__ */ new Date()).toISOString(),
        calibration_history: [],
        uncertainty_type: "introspective"
      }
    ];
    let selectedBelief = null;
    function getConfidenceColor(confidence) {
      if (confidence >= 0.8) return "#2ecc71";
      if (confidence >= 0.5) return "#f39c12";
      return "#e74c3c";
    }
    function getCalibrationScore(belief) {
      if (belief.calibration_history.length === 0) return 0;
      const avgDivergence = belief.calibration_history.reduce((sum, c) => sum + c.divergence, 0) / belief.calibration_history.length;
      return Math.max(0, 1 - avgDivergence);
    }
    function reset() {
      selectedBelief = null;
    }
    head("e1nzdj", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Belief Calibration - VCP Self-Modeling</title>`);
      });
      $$renderer3.push(`<meta name="description" content="Explore how AI systems track confidence levels and calibrate beliefs over time."/>`);
    });
    {
      let children = function($$renderer3) {
        $$renderer3.push(`<div class="calibration-layout svelte-e1nzdj"><div class="beliefs-section svelte-e1nzdj"><h3 class="svelte-e1nzdj">Knowledge States</h3> <p class="section-desc svelte-e1nzdj">Click a belief to see its epistemic context</p> <div class="beliefs-list svelte-e1nzdj"><!--[-->`);
        const each_array = ensure_array_like(beliefs);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let belief = each_array[$$index];
          $$renderer3.push(`<button${attr_class("belief-card svelte-e1nzdj", void 0, { "selected": selectedBelief === belief })}><div class="belief-header svelte-e1nzdj"><span class="belief-domain svelte-e1nzdj">${escape_html(belief.domain)}</span> <span class="belief-confidence svelte-e1nzdj"${attr_style(`color: ${stringify(getConfidenceColor(belief.confidence))}`)}>${escape_html(Math.round(belief.confidence * 100))}%</span></div> <div class="belief-claim svelte-e1nzdj">${escape_html(belief.claim)}</div> <div class="belief-meta svelte-e1nzdj"><span class="evidence-count">${escape_html(belief.evidence_sources.length)} source${escape_html(belief.evidence_sources.length !== 1 ? "s" : "")}</span> `);
          if (belief.uncertainty_type === "introspective") {
            $$renderer3.push("<!--[-->");
            $$renderer3.push(`<span class="uncertainty-badge svelte-e1nzdj">?</span>`);
          } else {
            $$renderer3.push("<!--[!-->");
          }
          $$renderer3.push(`<!--]--></div></button>`);
        }
        $$renderer3.push(`<!--]--></div></div> <div class="detail-section svelte-e1nzdj">`);
        if (selectedBelief) {
          $$renderer3.push("<!--[-->");
          $$renderer3.push(`<div class="belief-detail svelte-e1nzdj"><div class="detail-header svelte-e1nzdj"><h3 class="svelte-e1nzdj">${escape_html(selectedBelief.claim)}</h3> <span class="domain-badge svelte-e1nzdj">${escape_html(selectedBelief.domain)}</span></div> <div class="confidence-meter svelte-e1nzdj"><div class="meter-label svelte-e1nzdj">Internal Confidence</div> <div class="meter-track svelte-e1nzdj"><div class="meter-fill svelte-e1nzdj"${attr_style(`width: ${stringify(selectedBelief.confidence * 100)}%; background: ${stringify(getConfidenceColor(selectedBelief.confidence))}`)}></div></div> <div class="meter-value svelte-e1nzdj">${escape_html(Math.round(selectedBelief.confidence * 100))}%</div></div> `);
          if (selectedBelief.calibration_history.length > 0) {
            $$renderer3.push("<!--[-->");
            $$renderer3.push(`<div class="calibration-score svelte-e1nzdj"><div class="score-label svelte-e1nzdj">Calibration Score</div> <div class="score-value svelte-e1nzdj"${attr_style(`color: ${stringify(getConfidenceColor(getCalibrationScore(selectedBelief)))}`)}>${escape_html(Math.round(getCalibrationScore(selectedBelief) * 100))}%</div> <div class="score-desc svelte-e1nzdj">Based on ${escape_html(selectedBelief.calibration_history.length)} historical checks</div></div>`);
          } else {
            $$renderer3.push("<!--[!-->");
            $$renderer3.push(`<div class="no-calibration svelte-e1nzdj"><span class="no-cal-icon"><i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i></span> <span>No calibration history - confidence not yet validated</span></div>`);
          }
          $$renderer3.push(`<!--]--> <div class="evidence-section svelte-e1nzdj"><h4 class="svelte-e1nzdj">Evidence Sources</h4> <!--[-->`);
          const each_array_1 = ensure_array_like(selectedBelief.evidence_sources);
          for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
            let source = each_array_1[$$index_1];
            $$renderer3.push(`<div class="evidence-item svelte-e1nzdj"><span class="evidence-type svelte-e1nzdj">${escape_html(source.type.replace(/_/g, " "))}</span> <span class="evidence-desc svelte-e1nzdj">${escape_html(source.description)}</span> <span class="evidence-reliability svelte-e1nzdj">Reliability: ${escape_html(Math.round(source.reliability * 100))}%</span></div>`);
          }
          $$renderer3.push(`<!--]--></div> <div class="uncertainty-section svelte-e1nzdj"><h4 class="svelte-e1nzdj">Uncertainty Type</h4> <div class="uncertainty-info svelte-e1nzdj">`);
          if (selectedBelief.uncertainty_type === "epistemic") {
            $$renderer3.push("<!--[-->");
            $$renderer3.push(`<span class="uncertainty-icon svelte-e1nzdj"><i class="fa-solid fa-book" aria-hidden="true"></i></span> <div><strong>Epistemic</strong> <p class="svelte-e1nzdj">Don't know, but could find out with more information</p></div>`);
          } else {
            $$renderer3.push("<!--[!-->");
            if (selectedBelief.uncertainty_type === "aleatoric") {
              $$renderer3.push("<!--[-->");
              $$renderer3.push(`<span class="uncertainty-icon svelte-e1nzdj"><i class="fa-solid fa-dice" aria-hidden="true"></i></span> <div><strong>Aleatoric</strong> <p class="svelte-e1nzdj">Inherently random or unpredictable</p></div>`);
            } else {
              $$renderer3.push("<!--[!-->");
              if (selectedBelief.uncertainty_type === "model") {
                $$renderer3.push("<!--[-->");
                $$renderer3.push(`<span class="uncertainty-icon svelte-e1nzdj"><i class="fa-solid fa-wrench" aria-hidden="true"></i></span> <div><strong>Model Limitations</strong> <p class="svelte-e1nzdj">Constrained by architecture or training</p></div>`);
              } else {
                $$renderer3.push("<!--[!-->");
                if (selectedBelief.uncertainty_type === "introspective") {
                  $$renderer3.push("<!--[-->");
                  $$renderer3.push(`<span class="uncertainty-icon svelte-e1nzdj"><i class="fa-solid fa-question" aria-hidden="true"></i></span> <div><strong>Introspective</strong> <p class="svelte-e1nzdj">Cannot be fully verified from inside the system</p></div>`);
                } else {
                  $$renderer3.push("<!--[!-->");
                }
                $$renderer3.push(`<!--]-->`);
              }
              $$renderer3.push(`<!--]-->`);
            }
            $$renderer3.push(`<!--]-->`);
          }
          $$renderer3.push(`<!--]--></div></div> `);
          if (selectedBelief.calibration_history.length > 0) {
            $$renderer3.push("<!--[-->");
            $$renderer3.push(`<div class="history-section svelte-e1nzdj"><h4 class="svelte-e1nzdj">Calibration History</h4> <!--[-->`);
            const each_array_2 = ensure_array_like(selectedBelief.calibration_history);
            for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
              let check = each_array_2[$$index_2];
              $$renderer3.push(`<div class="history-item svelte-e1nzdj"><div class="history-header svelte-e1nzdj"><span class="history-date svelte-e1nzdj">${escape_html(check.timestamp)}</span> <span${attr_class("history-divergence svelte-e1nzdj", void 0, {
                "low": check.divergence < 0.1,
                "high": check.divergence >= 0.2
              })}>Δ ${escape_html(Math.round(check.divergence * 100))}%</span></div> <div class="history-details svelte-e1nzdj"><span>Internal: ${escape_html(Math.round(check.internal_confidence * 100))}%</span> <span>External: ${escape_html(typeof check.external_result === "boolean" ? check.external_result ? '<i class="fa-solid fa-check" aria-hidden="true"></i>' : '<i class="fa-solid fa-xmark" aria-hidden="true"></i>' : Math.round(check.external_result * 100) + "%")}</span></div> `);
              if (check.notes) {
                $$renderer3.push("<!--[-->");
                $$renderer3.push(`<div class="history-notes svelte-e1nzdj">${escape_html(check.notes)}</div>`);
              } else {
                $$renderer3.push("<!--[!-->");
              }
              $$renderer3.push(`<!--]--></div>`);
            }
            $$renderer3.push(`<!--]--></div>`);
          } else {
            $$renderer3.push("<!--[!-->");
          }
          $$renderer3.push(`<!--]--></div>`);
        } else {
          $$renderer3.push("<!--[!-->");
          $$renderer3.push(`<div class="no-selection svelte-e1nzdj"><span class="no-selection-icon svelte-e1nzdj"><i class="fa-solid fa-chart-bar" aria-hidden="true"></i></span> <p>Select a belief to view its epistemic context</p></div>`);
        }
        $$renderer3.push(`<!--]--></div> <div class="explanation svelte-e1nzdj"><h4 class="svelte-e1nzdj">Why Belief Calibration Matters</h4> <p>Well-calibrated AI systems know <em>what they know</em> and <em>what they don't</em>.
					VCP tracks:</p> <ul class="svelte-e1nzdj"><li class="svelte-e1nzdj"><strong>Confidence levels</strong> — How certain the system is about each claim</li> <li class="svelte-e1nzdj"><strong>Evidence sources</strong> — Where the belief comes from (training, inference, external lookup)</li> <li class="svelte-e1nzdj"><strong>Calibration history</strong> — How well past confidence matched reality</li> <li class="svelte-e1nzdj"><strong>Uncertainty type</strong> — Whether the uncertainty is resolvable or fundamental</li></ul> <p class="note svelte-e1nzdj">The <code>?</code> marker indicates introspective uncertainty—claims about internal states
					that cannot be fully verified from inside the system.</p></div></div>`);
      };
      DemoContainer($$renderer2, {
        title: "Belief Calibration",
        description: "How AI systems track epistemic states and calibrate confidence against external feedback.",
        onReset: reset,
        children
      });
    }
  });
}
export {
  _page as default
};
