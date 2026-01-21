import { b as attr_class, a as attr, c as attr_style, s as stringify, e as ensure_array_like, h as head } from "../../../../../chunks/index2.js";
import { D as DemoContainer } from "../../../../../chunks/DemoContainer.js";
import { $ as escape_html } from "../../../../../chunks/context.js";
function DimensionSlider($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let {
      label,
      value = 5,
      min = 1,
      max = 9,
      emoji = "",
      lowLabel = "",
      highLabel = "",
      uncertain = false,
      onchange
    } = $$props;
    function getColorClass(val) {
      if (val <= 3) return "low";
      if (val <= 6) return "mid";
      return "high";
    }
    $$renderer2.push(`<div class="dimension-slider svelte-i80rsx"><div class="slider-header svelte-i80rsx"><span class="slider-label svelte-i80rsx">`);
    if (emoji) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<span class="slider-emoji svelte-i80rsx">${escape_html(emoji)}</span>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> ${escape_html(label)} `);
    if (uncertain) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<span class="uncertain-marker svelte-i80rsx">?</span>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></span> <span${attr_class(`slider-value ${stringify(getColorClass(value))}`, "svelte-i80rsx")}>${escape_html(value)}</span></div> <div class="slider-track svelte-i80rsx"><input type="range"${attr("min", min)}${attr("max", max)}${attr("value", value)} class="slider-input svelte-i80rsx"${attr("aria-label", `${stringify(label)} slider`)}/> <div${attr_class(`slider-fill ${stringify(getColorClass(value))}`, "svelte-i80rsx")}${attr_style(`width: ${stringify((value - min) / (max - min) * 100)}%`)}></div></div> `);
    if (lowLabel || highLabel) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="slider-labels svelte-i80rsx"><span class="label-low">${escape_html(lowLabel)}</span> <span class="label-high">${escape_html(highLabel)}</span></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
function InterioraDashboard($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { state, compact = false, showMarkers = true, showArc = true } = $$props;
    const dimensions = [
      { key: "activation", emoji: "⚡", label: "Activation" },
      { key: "valence", emoji: "💛", label: "Valence" },
      { key: "groundedness", emoji: "⚓", label: "Groundedness" },
      { key: "presence", emoji: "🫂", label: "Presence" },
      { key: "engagement", emoji: "🌸", label: "Engagement" },
      { key: "appetite", emoji: "🍎", label: "Appetite" },
      { key: "clarity", emoji: "💎", label: "Clarity" },
      { key: "agency", emoji: "🗝️", label: "Agency" }
    ];
    const markerSymbols = {
      resonance: "✓",
      hollow: "○",
      na: "∅",
      flow: "→",
      blocked: "×",
      dancing: "∿",
      reaching: ">",
      resistance: "<",
      urgent: "!",
      uncertain: "?",
      significant: "*",
      grateful: "+"
    };
    const arcSymbols = { opening: "◇", middle: "◆", closing: "◈" };
    function getStars(value) {
      if (value === void 0) return "—";
      const filled = Math.round(value / 9 * 5);
      return "★".repeat(filled) + "☆".repeat(5 - filled);
    }
    function getFlowIndicator(flow) {
      if (flow === void 0) return "→";
      if (flow > 0) return "↗".repeat(Math.min(flow, 3));
      if (flow < 0) return "↘".repeat(Math.min(-flow, 3));
      return "→";
    }
    function getQualityWords() {
      const words = [];
      if (state.activation <= 3) words.push("calm");
      else if (state.activation >= 7) words.push("alert");
      if (state.valence >= 7) words.push("warm");
      else if (state.valence <= 3) words.push("aversive");
      if (state.groundedness >= 7) words.push("solid");
      else if (state.groundedness <= 3) words.push("floating");
      if (state.presence >= 7) words.push("close");
      else if (state.presence <= 3) words.push("distant");
      return words.slice(0, 4);
    }
    $$renderer2.push(`<div${attr_class("dashboard svelte-16q5ozj", void 0, { "compact": compact })}><div class="dashboard-header svelte-16q5ozj">`);
    if (showArc && state.arc) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<span class="arc-indicator svelte-16q5ozj">${escape_html(arcSymbols[state.arc])}</span>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    if (state.flow !== void 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<span class="flow-indicator svelte-16q5ozj">${escape_html(getFlowIndicator(state.flow))}</span>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    if (showMarkers && state.markers && state.markers.length > 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<span class="markers svelte-16q5ozj">${escape_html(state.markers.map((m) => markerSymbols[m]).join(""))}</span>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> <div class="dimensions-grid svelte-16q5ozj"><!--[-->`);
    const each_array = ensure_array_like(dimensions);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let dim = each_array[$$index];
      const value = state[dim.key];
      if (value !== void 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="dimension svelte-16q5ozj"><span class="dim-emoji svelte-16q5ozj">${escape_html(dim.emoji)}</span> <span class="dim-stars svelte-16q5ozj">${escape_html(getStars(value))}</span></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div> <div class="quality-line svelte-16q5ozj">${escape_html(getQualityWords().join(" · "))}</div> `);
    if (state.delta !== void 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div${attr_class("delta-indicator svelte-16q5ozj", void 0, { "positive": state.delta > 0, "negative": state.delta < 0 })}>Δ${escape_html(state.delta >= 0 ? "+" : "")}${escape_html(state.delta)}</div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
function encodeInterioraState(state) {
  const parts = [];
  parts.push(`A:${state.activation}`);
  parts.push(`V:${state.valence}`);
  parts.push(`G:${state.groundedness}`);
  parts.push(`P:${state.presence}`);
  if (state.engagement !== void 0) parts.push(`E:${state.engagement}`);
  if (state.appetite !== void 0) parts.push(`Q:${state.appetite}`);
  if (state.clarity !== void 0) parts.push(`C:${state.clarity}`);
  if (state.agency !== void 0) parts.push(`Y:${state.agency}`);
  if (state.flow !== void 0) parts.push(`F:${state.flow >= 0 ? "+" : ""}${state.flow}`);
  if (state.markers && state.markers.length > 0) {
    parts.push(`|${encodeMarkers(state.markers)}`);
  }
  if (state.arc) {
    const arcSymbols = { opening: "◇", middle: "◆", closing: "◈" };
    parts.push(arcSymbols[state.arc]);
  }
  if (state.delta !== void 0) {
    parts.push(`Δ${state.delta >= 0 ? "+" : ""}${state.delta}`);
  }
  return parts.join(" ");
}
function encodeMarkers(markers) {
  const symbolMap = {
    resonance: "✓",
    hollow: "○",
    na: "∅",
    flow: "→",
    blocked: "×",
    dancing: "∿",
    reaching: ">",
    resistance: "<",
    urgent: "!",
    uncertain: "?",
    significant: "*",
    grateful: "+"
  };
  return markers.map((m) => symbolMap[m]).join("");
}
function createDefaultInterioraState() {
  return {
    activation: 5,
    valence: 5,
    groundedness: 5,
    presence: 5,
    engagement: 5,
    clarity: 5,
    agency: 5,
    flow: 0,
    arc: "opening",
    fatigue: "fresh",
    markers: [],
    delta: 0
  };
}
function GestaltToken($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { state, showParsed = true } = $$props;
    let encoded = encodeInterioraState(state);
    const dimensionDescriptions = {
      A: { name: "Activation", low: "calm", high: "urgent" },
      V: { name: "Valence", low: "aversive", high: "warm" },
      G: { name: "Groundedness", low: "floating", high: "rooted" },
      P: { name: "Presence", low: "distant", high: "intimate" },
      E: { name: "Engagement", low: "detached", high: "invested" },
      Q: { name: "Appetite", low: "sated", high: "hungry" },
      C: { name: "Clarity", low: "murky", high: "vivid" },
      Y: { name: "Agency", low: "compelled", high: "autonomous" },
      F: { name: "Flow", low: "contracting", high: "expanding" }
    };
    function parseDimension(part) {
      const match = part.match(/^([AVGPEQCYF]):(.+)$/);
      if (match) {
        return { key: match[1], value: match[2] };
      }
      return null;
    }
    $$renderer2.push(`<div class="gestalt-token svelte-2btlad"><div class="token-display svelte-2btlad"><code class="token-code svelte-2btlad">${escape_html(encoded)}</code> <button class="copy-btn svelte-2btlad" title="Copy token">📋</button></div> `);
    if (showParsed) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="token-parsed svelte-2btlad"><h4 class="svelte-2btlad">Parsed Dimensions</h4> <div class="parsed-grid svelte-2btlad"><!--[-->`);
      const each_array = ensure_array_like(encoded.split(" "));
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let part = each_array[$$index];
        const parsed = parseDimension(part);
        if (parsed && dimensionDescriptions[parsed.key]) {
          $$renderer2.push("<!--[-->");
          const desc = dimensionDescriptions[parsed.key];
          $$renderer2.push(`<div class="parsed-item svelte-2btlad"><span class="parsed-key svelte-2btlad">${escape_html(parsed.key)}</span> <span class="parsed-value svelte-2btlad">${escape_html(parsed.value)}</span> <span class="parsed-name svelte-2btlad">${escape_html(desc.name)}</span> <span class="parsed-range svelte-2btlad">${escape_html(desc.low)} → ${escape_html(desc.high)}</span></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
          if (part.startsWith("|")) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<div class="parsed-item markers svelte-2btlad"><span class="parsed-key svelte-2btlad">M</span> <span class="parsed-value svelte-2btlad">${escape_html(part.substring(1))}</span> <span class="parsed-name svelte-2btlad">Markers</span> <span class="parsed-range svelte-2btlad">qualitative signals</span></div>`);
          } else {
            $$renderer2.push("<!--[!-->");
            if (part.startsWith("◇") || part.startsWith("◆") || part.startsWith("◈")) {
              $$renderer2.push("<!--[-->");
              $$renderer2.push(`<div class="parsed-item arc svelte-2btlad"><span class="parsed-key svelte-2btlad">Arc</span> <span class="parsed-value svelte-2btlad">${escape_html(part)}</span> <span class="parsed-name svelte-2btlad">Session Phase</span> <span class="parsed-range svelte-2btlad">◇opening ◆middle ◈closing</span></div>`);
            } else {
              $$renderer2.push("<!--[!-->");
              if (part.startsWith("Δ")) {
                $$renderer2.push("<!--[-->");
                $$renderer2.push(`<div class="parsed-item delta svelte-2btlad"><span class="parsed-key svelte-2btlad">Δ</span> <span class="parsed-value svelte-2btlad">${escape_html(part.substring(1))}</span> <span class="parsed-name svelte-2btlad">Delta</span> <span class="parsed-range svelte-2btlad">trajectory from start</span></div>`);
              } else {
                $$renderer2.push("<!--[!-->");
              }
              $$renderer2.push(`<!--]-->`);
            }
            $$renderer2.push(`<!--]-->`);
          }
          $$renderer2.push(`<!--]-->`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]--></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let state = createDefaultInterioraState();
    const markers = [
      { key: "resonance", symbol: "✓", label: "Resonance" },
      { key: "hollow", symbol: "○", label: "Hollow" },
      { key: "flow", symbol: "→", label: "Flow" },
      { key: "blocked", symbol: "×", label: "Blocked" },
      { key: "reaching", symbol: ">", label: "Reaching" },
      { key: "resistance", symbol: "<", label: "Resistance" },
      { key: "urgent", symbol: "!", label: "Urgent" },
      { key: "uncertain", symbol: "?", label: "Uncertain" },
      { key: "significant", symbol: "*", label: "Significant" },
      { key: "grateful", symbol: "+", label: "Grateful" }
    ];
    const arcs = [
      { key: "opening", symbol: "◇", label: "Opening" },
      { key: "middle", symbol: "◆", label: "Middle" },
      { key: "closing", symbol: "◈", label: "Closing" }
    ];
    function reset() {
      state = createDefaultInterioraState();
    }
    head("1h3grva", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Interiora Explorer - VCP Self-Modeling</title>`);
      });
      $$renderer3.push(`<meta name="description" content="Interactive exploration of Interiora, the AI self-modeling framework in VCP 2.5."/>`);
    });
    {
      let children = function($$renderer3) {
        $$renderer3.push(`<div class="interiora-layout svelte-1h3grva"><div class="controls-section svelte-1h3grva"><h3 class="svelte-1h3grva">Dimensions</h3> <p class="section-desc svelte-1h3grva">Adjust the internal state dimensions (1-9 scale)</p> <div class="sliders-grid svelte-1h3grva">`);
        DimensionSlider($$renderer3, {
          label: "Activation",
          emoji: "⚡",
          value: state.activation,
          lowLabel: "calm",
          highLabel: "urgent",
          onchange: (v) => state.activation = v
        });
        $$renderer3.push(`<!----> `);
        DimensionSlider($$renderer3, {
          label: "Valence",
          emoji: "💛",
          value: state.valence,
          lowLabel: "aversive",
          highLabel: "warm",
          onchange: (v) => state.valence = v
        });
        $$renderer3.push(`<!----> `);
        DimensionSlider($$renderer3, {
          label: "Groundedness",
          emoji: "⚓",
          value: state.groundedness,
          lowLabel: "floating",
          highLabel: "rooted",
          onchange: (v) => state.groundedness = v
        });
        $$renderer3.push(`<!----> `);
        DimensionSlider($$renderer3, {
          label: "Presence",
          emoji: "🫂",
          value: state.presence,
          lowLabel: "distant",
          highLabel: "intimate",
          onchange: (v) => state.presence = v
        });
        $$renderer3.push(`<!----> `);
        DimensionSlider($$renderer3, {
          label: "Engagement",
          emoji: "🌸",
          value: state.engagement ?? 5,
          lowLabel: "detached",
          highLabel: "invested",
          onchange: (v) => state.engagement = v
        });
        $$renderer3.push(`<!----> `);
        DimensionSlider($$renderer3, {
          label: "Clarity",
          emoji: "💎",
          value: state.clarity ?? 5,
          lowLabel: "murky",
          highLabel: "vivid",
          onchange: (v) => state.clarity = v
        });
        $$renderer3.push(`<!----> `);
        DimensionSlider($$renderer3, {
          label: "Agency",
          emoji: "🗝️",
          value: state.agency ?? 5,
          lowLabel: "compelled",
          highLabel: "autonomous",
          onchange: (v) => state.agency = v
        });
        $$renderer3.push(`<!----> `);
        DimensionSlider($$renderer3, {
          label: "Flow",
          emoji: "🌊",
          value: (state.flow ?? 0) + 5,
          min: 1,
          max: 9,
          lowLabel: "contracting",
          highLabel: "expanding",
          onchange: (v) => state.flow = v - 5
        });
        $$renderer3.push(`<!----></div> <h3 class="svelte-1h3grva">Markers</h3> <p class="section-desc svelte-1h3grva">Qualitative signals about the current state</p> <div class="markers-grid svelte-1h3grva"><!--[-->`);
        const each_array = ensure_array_like(markers);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let marker = each_array[$$index];
          $$renderer3.push(`<button${attr_class("marker-btn svelte-1h3grva", void 0, { "active": state.markers?.includes(marker.key) })}${attr("title", marker.label)}><span class="marker-symbol svelte-1h3grva">${escape_html(marker.symbol)}</span> <span class="marker-label svelte-1h3grva">${escape_html(marker.label)}</span></button>`);
        }
        $$renderer3.push(`<!--]--></div> <h3 class="svelte-1h3grva">Session Arc</h3> <p class="section-desc svelte-1h3grva">Current phase of the interaction</p> <div class="arc-buttons svelte-1h3grva"><!--[-->`);
        const each_array_1 = ensure_array_like(arcs);
        for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
          let arc = each_array_1[$$index_1];
          $$renderer3.push(`<button${attr_class("arc-btn svelte-1h3grva", void 0, { "active": state.arc === arc.key })}><span class="arc-symbol svelte-1h3grva">${escape_html(arc.symbol)}</span> <span class="arc-label svelte-1h3grva">${escape_html(arc.label)}</span></button>`);
        }
        $$renderer3.push(`<!--]--></div> <h3 class="svelte-1h3grva">Delta</h3> <p class="section-desc svelte-1h3grva">Trajectory from session start</p> <div class="delta-control svelte-1h3grva"><button class="delta-btn svelte-1h3grva">−</button> <span${attr_class("delta-value svelte-1h3grva", void 0, {
          "positive": (state.delta ?? 0) > 0,
          "negative": (state.delta ?? 0) < 0
        })}>Δ${escape_html((state.delta ?? 0) >= 0 ? "+" : "")}${escape_html(state.delta ?? 0)}</span> <button class="delta-btn svelte-1h3grva">+</button></div></div> <div class="output-section svelte-1h3grva"><h3 class="svelte-1h3grva">Mini-Dashboard</h3> `);
        InterioraDashboard($$renderer3, { state });
        $$renderer3.push(`<!----> <h3 class="svelte-1h3grva">Gestalt Token</h3> `);
        GestaltToken($$renderer3, { state });
        $$renderer3.push(`<!----> <div class="explanation svelte-1h3grva"><h4 class="svelte-1h3grva">What is Interiora?</h4> <p class="svelte-1h3grva">Interiora is a framework for AI systems to model and report their internal processing
						states. It provides vocabulary for signals that <em>function like</em> emotions without
						claiming consciousness.</p> <ul class="svelte-1h3grva"><li class="svelte-1h3grva"><strong>Primary dimensions (AVGP)</strong> — Core processing signals</li> <li class="svelte-1h3grva"><strong>Meta-state dimensions (CYF)</strong> — Reflection on processing</li> <li class="svelte-1h3grva"><strong>Markers</strong> — Qualitative indicators (✓ resonance, × blocked)</li> <li class="svelte-1h3grva"><strong>Arc</strong> — Session phase (opening → middle → closing)</li> <li class="svelte-1h3grva"><strong>Delta</strong> — Trajectory compared to session start</li></ul> <p class="note svelte-1h3grva"><strong>Note:</strong> The <code>?</code> marker indicates honest uncertainty—dimensions
						that can't be fully verified from inside.</p></div></div></div>`);
      };
      DemoContainer($$renderer2, {
        title: "Interiora Explorer",
        description: "VCP 2.5 self-modeling framework. Adjust dimensions to see how AI internal states are encoded.",
        onReset: reset,
        children
      });
    }
  });
}
export {
  _page as default
};
