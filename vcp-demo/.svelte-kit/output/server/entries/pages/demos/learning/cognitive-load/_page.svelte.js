import { b as attr_class, a as attr, c as attr_style, s as stringify, e as ensure_array_like, h as head } from "../../../../../chunks/index2.js";
import { D as DemoContainer } from "../../../../../chunks/DemoContainer.js";
import { $ as escape_html } from "../../../../../chunks/context.js";
function CognitiveLoadMeter($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { state, showBreakdown = true, compact = false } = $$props;
    function getLoadColor(load) {
      if (load <= 0.4) return "#2ecc71";
      if (load <= 0.7) return "#f39c12";
      return "#e74c3c";
    }
    function getLoadLabel(load) {
      if (load <= 0.3) return "Light";
      if (load <= 0.5) return "Moderate";
      if (load <= 0.7) return "Heavy";
      return "Overloaded";
    }
    function formatDuration(minutes) {
      if (minutes < 60) return `${Math.round(minutes)}m`;
      const hours = Math.floor(minutes / 60);
      const mins = Math.round(minutes % 60);
      return `${hours}h ${mins}m`;
    }
    $$renderer2.push(`<div${attr_class("cognitive-load-meter svelte-k9qrky", void 0, { "compact": compact })} role="region" aria-label="Cognitive load status"><div class="main-gauge svelte-k9qrky"><div class="gauge-track svelte-k9qrky" role="progressbar"${attr("aria-valuenow", Math.round(state.current_load * 100))} aria-valuemin="0" aria-valuemax="100"${attr("aria-label", `Current cognitive load: ${stringify(Math.round(state.current_load * 100))}% - ${stringify(getLoadLabel(state.current_load))}`)}><div class="gauge-fill svelte-k9qrky"${attr_style(`width: ${stringify(state.current_load * 100)}%; background: ${stringify(getLoadColor(state.current_load))}`)}></div></div> <div class="gauge-labels svelte-k9qrky"><span class="gauge-label svelte-k9qrky">${escape_html(getLoadLabel(state.current_load))}</span> <span class="gauge-value svelte-k9qrky"${attr_style(`color: ${stringify(getLoadColor(state.current_load))}`)} aria-hidden="true">${escape_html(Math.round(state.current_load * 100))}%</span></div></div> `);
    if (showBreakdown && !compact) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="breakdown svelte-k9qrky"><div class="breakdown-item svelte-k9qrky"><span class="breakdown-label svelte-k9qrky">Intrinsic</span> <div class="breakdown-bar svelte-k9qrky"><div class="breakdown-fill intrinsic svelte-k9qrky"${attr_style(`width: ${stringify(state.intrinsic_load * 100)}%`)}></div></div> <span class="breakdown-value svelte-k9qrky">${escape_html(Math.round(state.intrinsic_load * 100))}%</span></div> <div class="breakdown-item svelte-k9qrky"><span class="breakdown-label svelte-k9qrky">Extraneous</span> <div class="breakdown-bar svelte-k9qrky"><div class="breakdown-fill extraneous svelte-k9qrky"${attr_style(`width: ${stringify(state.extraneous_load * 100)}%`)}></div></div> <span class="breakdown-value svelte-k9qrky">${escape_html(Math.round(state.extraneous_load * 100))}%</span></div> <div class="breakdown-item svelte-k9qrky"><span class="breakdown-label svelte-k9qrky">Germane</span> <div class="breakdown-bar svelte-k9qrky"><div class="breakdown-fill germane svelte-k9qrky"${attr_style(`width: ${stringify(state.germane_load * 100)}%`)}></div></div> <span class="breakdown-value svelte-k9qrky">${escape_html(Math.round(state.germane_load * 100))}%</span></div></div> <div class="session-info svelte-k9qrky"><div class="info-item svelte-k9qrky"><span class="info-icon"><i class="fa-solid fa-stopwatch" aria-hidden="true"></i></span> <span>Session: ${escape_html(formatDuration(state.session_duration_minutes))}</span></div> <div class="info-item svelte-k9qrky"><span class="info-icon"><i class="fa-solid fa-battery-half" aria-hidden="true"></i></span> <span>Capacity: ${escape_html(Math.round(state.capacity_remaining * 100))}%</span></div> `);
      if (state.fatigue_factor > 0.3) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="info-item fatigue svelte-k9qrky"><span class="info-icon"><i class="fa-solid fa-bed" aria-hidden="true"></i></span> <span>Fatigue: ${escape_html(Math.round(state.fatigue_factor * 100))}%</span></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div> `);
      if (state.overload_indicators.length > 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="overload-warning svelte-k9qrky"><span class="warning-icon svelte-k9qrky"><i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i></span> <span class="svelte-k9qrky">Overload signals detected:</span> <div class="indicator-chips svelte-k9qrky"><!--[-->`);
        const each_array = ensure_array_like(state.overload_indicators);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let indicator = each_array[$$index];
          $$renderer2.push(`<span class="indicator-chip svelte-k9qrky">${escape_html(indicator.type.replace(/_/g, " "))}</span>`);
        }
        $$renderer2.push(`<!--]--></div></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]-->`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let loadState = {
      current_load: 0.65,
      intrinsic_load: 0.35,
      extraneous_load: 0.15,
      germane_load: 0.15,
      fatigue_factor: 0.25,
      last_break: new Date(Date.now() - 45 * 60 * 1e3).toISOString(),
      session_duration_minutes: 47,
      capacity_remaining: 0.55,
      overload_indicators: []
    };
    let adaptations = (() => {
      const result = [
        {
          trigger: "Load > 70%",
          action: "Simplify language and reduce example complexity",
          active: loadState.current_load > 0.7
        },
        {
          trigger: "Extraneous > 20%",
          action: "Remove decorative elements, focus on core content",
          active: loadState.extraneous_load > 0.2
        },
        {
          trigger: "Session > 45 min",
          action: "Suggest a 5-minute break",
          active: loadState.session_duration_minutes > 45
        },
        {
          trigger: "Fatigue > 30%",
          action: "Switch to more interactive format",
          active: loadState.fatigue_factor > 0.3
        },
        {
          trigger: "Capacity < 40%",
          action: "Recommend stopping for today",
          active: loadState.capacity_remaining < 0.4
        }
      ];
      return result;
    })();
    let timeline = [
      { time: 0, load: 0.2, event: "Session start" },
      { time: 10, load: 0.35, event: "New concept introduced" },
      { time: 20, load: 0.5, event: "Practice exercise" },
      {
        time: 30,
        load: 0.45,
        event: "Mastery achieved, consolidation"
      },
      { time: 40, load: 0.6, event: "Advanced topic" },
      { time: 47, load: 0.65, event: "Current" }
    ];
    head("15t7dss", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Cognitive Load Awareness - VCP Learning</title>`);
      });
      $$renderer3.push(`<meta name="description" content="See how VCP enables load-aware teaching that adapts to cognitive capacity."/>`);
    });
    {
      let children = function($$renderer3) {
        $$renderer3.push(`<div class="load-layout svelte-15t7dss"><div class="meter-section svelte-15t7dss">`);
        CognitiveLoadMeter($$renderer3, { state: loadState, showBreakdown: true });
        $$renderer3.push(`<!----> <div class="controls-card svelte-15t7dss"><h3 class="svelte-15t7dss">Simulate Load Changes</h3> <div class="control-grid svelte-15t7dss"><div class="control-row svelte-15t7dss"><span class="control-label svelte-15t7dss">Intrinsic (Material Complexity)</span> <div class="control-buttons svelte-15t7dss"><button class="svelte-15t7dss">−</button> <span class="control-value svelte-15t7dss">${escape_html(Math.round(loadState.intrinsic_load * 100))}%</span> <button class="svelte-15t7dss">+</button></div></div> <div class="control-row svelte-15t7dss"><span class="control-label svelte-15t7dss">Extraneous (Poor Presentation)</span> <div class="control-buttons svelte-15t7dss"><button class="svelte-15t7dss">−</button> <span class="control-value svelte-15t7dss">${escape_html(Math.round(loadState.extraneous_load * 100))}%</span> <button class="svelte-15t7dss">+</button></div></div> <div class="control-row svelte-15t7dss"><span class="control-label svelte-15t7dss">Germane (Active Learning)</span> <div class="control-buttons svelte-15t7dss"><button class="svelte-15t7dss">−</button> <span class="control-value svelte-15t7dss">${escape_html(Math.round(loadState.germane_load * 100))}%</span> <button class="svelte-15t7dss">+</button></div></div></div> <div class="scenario-buttons svelte-15t7dss"><button class="scenario-btn danger svelte-15t7dss">Simulate Overload</button> <button class="scenario-btn success svelte-15t7dss">Reset to Optimal</button></div></div></div> <div class="theory-section svelte-15t7dss"><div class="adaptations-card svelte-15t7dss"><h3 class="svelte-15t7dss">Active Adaptations</h3> <div class="adaptations-list svelte-15t7dss"><!--[-->`);
        const each_array = ensure_array_like(adaptations);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let adaptation = each_array[$$index];
          $$renderer3.push(`<div${attr_class("adaptation-item svelte-15t7dss", void 0, { "active": adaptation.active })}><div class="adaptation-trigger svelte-15t7dss"><span class="trigger-condition svelte-15t7dss">${escape_html(adaptation.trigger)}</span> <span class="trigger-status svelte-15t7dss">${escape_html(adaptation.active ? "ACTIVE" : "standby")}</span></div> <div class="adaptation-action svelte-15t7dss">${escape_html(adaptation.action)}</div></div>`);
        }
        $$renderer3.push(`<!--]--></div></div> <div class="timeline-card svelte-15t7dss"><h3 class="svelte-15t7dss">Session Timeline</h3> <div class="timeline svelte-15t7dss"><!--[-->`);
        const each_array_1 = ensure_array_like(timeline);
        for (let i = 0, $$length = each_array_1.length; i < $$length; i++) {
          let point = each_array_1[i];
          $$renderer3.push(`<div${attr_class("timeline-point svelte-15t7dss", void 0, { "current": i === timeline.length - 1 })}><div class="point-marker svelte-15t7dss"><div class="point-load svelte-15t7dss"${attr_style(`height: ${stringify(point.load * 100)}%; background: ${stringify(point.load > 0.7 ? "#e74c3c" : point.load > 0.5 ? "#f39c12" : "#2ecc71")}`)}></div></div> <div class="point-info svelte-15t7dss"><span class="point-time svelte-15t7dss">${escape_html(point.time)}m</span> <span class="point-event svelte-15t7dss">${escape_html(point.event)}</span></div></div>`);
        }
        $$renderer3.push(`<!--]--></div></div> <div class="theory-card svelte-15t7dss"><h3 class="svelte-15t7dss">Cognitive Load Theory</h3> <div class="load-types svelte-15t7dss"><div class="load-type intrinsic svelte-15t7dss"><div class="type-header svelte-15t7dss"><span class="type-dot svelte-15t7dss"></span> <strong>Intrinsic Load</strong></div> <p class="svelte-15t7dss">Inherent complexity of the material. Can't be eliminated, but can be managed
								through scaffolding and sequencing.</p></div> <div class="load-type extraneous svelte-15t7dss"><div class="type-header svelte-15t7dss"><span class="type-dot svelte-15t7dss"></span> <strong>Extraneous Load</strong></div> <p class="svelte-15t7dss">Load from poor instructional design. Should be minimized. VCP helps by
								matching presentation to learner preferences.</p></div> <div class="load-type germane svelte-15t7dss"><div class="type-header svelte-15t7dss"><span class="type-dot svelte-15t7dss"></span> <strong>Germane Load</strong></div> <p class="svelte-15t7dss">Load from active learning and schema construction. This is beneficial!
								VCP optimizes for maximizing germane load within capacity.</p></div></div> <div class="key-insight svelte-15t7dss"><strong>VCP Advantage:</strong> By knowing your cognitive state, learning style,
						and current context, AI tutors can dynamically adjust material complexity,
						presentation format, and pacing to keep you in the optimal learning zone.</div></div></div></div>`);
      };
      DemoContainer($$renderer2, {
        title: "Cognitive Load Awareness",
        description: "AI that monitors and adapts to your cognitive capacity in real-time.",
        children
      });
    }
  });
}
export {
  _page as default
};
