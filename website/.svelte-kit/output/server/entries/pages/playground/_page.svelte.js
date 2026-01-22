import { a2 as head, a0 as attr, a8 as ensure_array_like, a1 as attr_class, a3 as escape_html, a7 as stringify } from "../../../chunks/index2.js";
import { e as encodeContextToCSM1, g as getTransmissionSummary, a as getEmojiLegend } from "../../../chunks/token.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let context = {
      vcp_version: "1.0.0",
      profile_id: "playground-user",
      constitution: {
        id: "personal.growth.creative",
        version: "1.0.0",
        persona: "muse",
        adherence: 3,
        scopes: ["creativity", "health", "privacy"]
      },
      public_profile: {
        display_name: "Playground User",
        goal: "learn_guitar",
        experience: "beginner",
        learning_style: "hands_on",
        pace: "steady",
        motivation: "stress_relief"
      },
      portable_preferences: {
        noise_mode: "quiet_preferred",
        session_length: "30_minutes",
        budget_range: "low",
        feedback_style: "encouraging"
      },
      constraints: {
        time_limited: true,
        budget_limited: true,
        noise_restricted: true,
        energy_variable: false,
        schedule_irregular: false
      },
      private_context: {
        _note: "Private context - never transmitted",
        work_type: "office_worker",
        housing: "apartment"
      }
    };
    const token = encodeContextToCSM1(context);
    const summary = getTransmissionSummary(context);
    const legend = getEmojiLegend();
    const personas = [
      { id: "muse", name: "Muse", iconClass: "fa-palette" },
      {
        id: "ambassador",
        name: "Ambassador",
        iconClass: "fa-handshake"
      },
      { id: "godparent", name: "Godparent", iconClass: "fa-shield" },
      { id: "sentinel", name: "Sentinel", iconClass: "fa-eye" },
      { id: "anchor", name: "Anchor", iconClass: "fa-anchor" },
      { id: "nanny", name: "Nanny", iconClass: "fa-child" }
    ];
    function updatePreference(key, value) {
      context.portable_preferences = { ...context.portable_preferences, [key]: value };
    }
    head("j6hxly", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Playground - VCP</title>`);
      });
      $$renderer3.push(`<meta name="description" content="Interactive VCP token builder and inspector."/>`);
    });
    $$renderer2.push(`<div class="container"><section class="hero svelte-j6hxly"><h1 class="svelte-j6hxly">VCP Playground</h1> <p class="hero-subtitle svelte-j6hxly">Build and inspect VCP tokens interactively. Adjust settings and see the CSM-1 encoding in real-time.</p></section> <div class="playground-grid svelte-j6hxly"><div class="panel controls-panel svelte-j6hxly"><div class="panel-header svelte-j6hxly"><h2 class="svelte-j6hxly">Context Builder</h2> <button class="btn btn-ghost btn-sm">Reset</button></div> <section class="control-section svelte-j6hxly"><h3 class="svelte-j6hxly">Profile</h3> <div class="control-group svelte-j6hxly"><label class="label" for="display-name">Display Name</label> <input id="display-name" type="text" class="input"${attr("value", context.public_profile.display_name)}/></div> <div class="control-group svelte-j6hxly"><label class="label" for="goal">Goal</label> <input id="goal" type="text" class="input"${attr("value", context.public_profile.goal)}/></div> <div class="control-row svelte-j6hxly"><div class="control-group svelte-j6hxly"><label class="label" for="experience">Experience</label> `);
    $$renderer2.select(
      {
        id: "experience",
        class: "input select",
        value: context.public_profile.experience
      },
      ($$renderer3) => {
        $$renderer3.option({ value: "beginner" }, ($$renderer4) => {
          $$renderer4.push(`Beginner`);
        });
        $$renderer3.option({ value: "intermediate" }, ($$renderer4) => {
          $$renderer4.push(`Intermediate`);
        });
        $$renderer3.option({ value: "advanced" }, ($$renderer4) => {
          $$renderer4.push(`Advanced`);
        });
        $$renderer3.option({ value: "expert" }, ($$renderer4) => {
          $$renderer4.push(`Expert`);
        });
      }
    );
    $$renderer2.push(`</div> <div class="control-group svelte-j6hxly"><label class="label" for="style">Learning Style</label> `);
    $$renderer2.select(
      {
        id: "style",
        class: "input select",
        value: context.public_profile.learning_style
      },
      ($$renderer3) => {
        $$renderer3.option({ value: "visual" }, ($$renderer4) => {
          $$renderer4.push(`Visual`);
        });
        $$renderer3.option({ value: "auditory" }, ($$renderer4) => {
          $$renderer4.push(`Auditory`);
        });
        $$renderer3.option({ value: "hands_on" }, ($$renderer4) => {
          $$renderer4.push(`Hands-on`);
        });
        $$renderer3.option({ value: "reading" }, ($$renderer4) => {
          $$renderer4.push(`Reading`);
        });
        $$renderer3.option({ value: "mixed" }, ($$renderer4) => {
          $$renderer4.push(`Mixed`);
        });
      }
    );
    $$renderer2.push(`</div></div></section> <section class="control-section svelte-j6hxly"><h3 class="svelte-j6hxly">Constitution</h3> <fieldset class="control-group svelte-j6hxly"><legend class="label svelte-j6hxly">Persona</legend> <div class="persona-grid svelte-j6hxly"><!--[-->`);
    const each_array = ensure_array_like(personas);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let persona = each_array[$$index];
      $$renderer2.push(`<button${attr_class("persona-btn svelte-j6hxly", void 0, { "active": context.constitution.persona === persona.id })}><span class="persona-icon svelte-j6hxly"><i${attr_class(`fa-solid ${stringify(persona.iconClass)}`, "svelte-j6hxly")} aria-hidden="true"></i></span> <span class="persona-name svelte-j6hxly">${escape_html(persona.name)}</span></button>`);
    }
    $$renderer2.push(`<!--]--></div></fieldset> <div class="control-group svelte-j6hxly"><label class="label" for="adherence">Adherence Level: ${escape_html(context.constitution.adherence)}</label> <input id="adherence" type="range" min="1" max="5"${attr("value", context.constitution.adherence)} class="slider svelte-j6hxly"/></div></section> <section class="control-section svelte-j6hxly"><h3 class="svelte-j6hxly">Constraint Flags</h3> <div class="checkbox-grid svelte-j6hxly"><label class="checkbox-label svelte-j6hxly"><input type="checkbox"${attr("checked", context.constraints?.time_limited, true)}/> <span><i class="fa-solid fa-clock" aria-hidden="true"></i> Time Limited</span></label> <label class="checkbox-label svelte-j6hxly"><input type="checkbox"${attr("checked", context.constraints?.budget_limited, true)}/> <span><i class="fa-solid fa-wallet" aria-hidden="true"></i> Budget Limited</span></label> <label class="checkbox-label svelte-j6hxly"><input type="checkbox"${attr("checked", context.constraints?.noise_restricted, true)}/> <span><i class="fa-solid fa-volume-xmark" aria-hidden="true"></i> Noise Restricted</span></label> <label class="checkbox-label svelte-j6hxly"><input type="checkbox"${attr("checked", context.constraints?.energy_variable, true)}/> <span><i class="fa-solid fa-bolt" aria-hidden="true"></i> Energy Variable</span></label> <label class="checkbox-label svelte-j6hxly"><input type="checkbox"${attr("checked", context.constraints?.schedule_irregular, true)}/> <span><i class="fa-solid fa-calendar" aria-hidden="true"></i> Schedule Irregular</span></label></div></section> <section class="control-section svelte-j6hxly"><h3 class="svelte-j6hxly">Preferences</h3> <div class="control-row svelte-j6hxly"><div class="control-group svelte-j6hxly"><label class="label" for="noise-mode">Noise Mode</label> `);
    $$renderer2.select(
      {
        id: "noise-mode",
        class: "input select",
        value: context.portable_preferences?.noise_mode,
        onchange: (e) => updatePreference("noise_mode", e.currentTarget.value)
      },
      ($$renderer3) => {
        $$renderer3.option({ value: "normal" }, ($$renderer4) => {
          $$renderer4.push(`Normal`);
        });
        $$renderer3.option({ value: "quiet_preferred" }, ($$renderer4) => {
          $$renderer4.push(`Quiet Preferred`);
        });
        $$renderer3.option({ value: "silent_required" }, ($$renderer4) => {
          $$renderer4.push(`Silent Required`);
        });
      }
    );
    $$renderer2.push(`</div> <div class="control-group svelte-j6hxly"><label class="label" for="budget">Budget Range</label> `);
    $$renderer2.select(
      {
        id: "budget",
        class: "input select",
        value: context.portable_preferences?.budget_range,
        onchange: (e) => updatePreference("budget_range", e.currentTarget.value)
      },
      ($$renderer3) => {
        $$renderer3.option({ value: "unlimited" }, ($$renderer4) => {
          $$renderer4.push(`Unlimited`);
        });
        $$renderer3.option({ value: "high" }, ($$renderer4) => {
          $$renderer4.push(`High`);
        });
        $$renderer3.option({ value: "medium" }, ($$renderer4) => {
          $$renderer4.push(`Medium`);
        });
        $$renderer3.option({ value: "low" }, ($$renderer4) => {
          $$renderer4.push(`Low`);
        });
        $$renderer3.option({ value: "free_only" }, ($$renderer4) => {
          $$renderer4.push(`Free Only`);
        });
      }
    );
    $$renderer2.push(`</div></div></section></div> <div class="panel token-panel svelte-j6hxly"><div class="panel-header svelte-j6hxly"><h2 class="svelte-j6hxly">CSM-1 Token</h2> <button class="btn btn-primary btn-sm">Copy</button></div> <div class="token-display svelte-j6hxly"><pre class="svelte-j6hxly">${escape_html(token)}</pre></div> <div class="legend-section svelte-j6hxly"><h3 class="svelte-j6hxly">Emoji Key</h3> <div class="legend-grid svelte-j6hxly"><!--[-->`);
    const each_array_1 = ensure_array_like(legend);
    for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
      let item = each_array_1[$$index_1];
      $$renderer2.push(`<div class="legend-item svelte-j6hxly"><span class="legend-emoji svelte-j6hxly">${escape_html(item.emoji)}</span> <span class="legend-meaning svelte-j6hxly">${escape_html(item.meaning)}</span></div>`);
    }
    $$renderer2.push(`<!--]--></div></div> <div class="summary-section svelte-j6hxly"><h3 class="svelte-j6hxly">Transmission Summary</h3> <div class="summary-grid svelte-j6hxly"><div class="summary-group"><h4 class="summary-label summary-transmitted svelte-j6hxly">Transmitted (${escape_html(summary.transmitted.length)})</h4> <div class="field-list"><!--[-->`);
    const each_array_2 = ensure_array_like(summary.transmitted);
    for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
      let field = each_array_2[$$index_2];
      $$renderer2.push(`<span class="field-tag field-tag-shared">${escape_html(field)}</span>`);
    }
    $$renderer2.push(`<!--]--></div></div> <div class="summary-group"><h4 class="summary-label summary-influencing svelte-j6hxly">Influencing (${escape_html(summary.influencing.length)})</h4> <div class="field-list"><!--[-->`);
    const each_array_3 = ensure_array_like(summary.influencing);
    for (let $$index_3 = 0, $$length = each_array_3.length; $$index_3 < $$length; $$index_3++) {
      let field = each_array_3[$$index_3];
      $$renderer2.push(`<span class="field-tag field-tag-influence svelte-j6hxly">${escape_html(field)}</span>`);
    }
    $$renderer2.push(`<!--]--></div></div> <div class="summary-group"><h4 class="summary-label summary-withheld svelte-j6hxly">Withheld (${escape_html(summary.withheld.length)})</h4> <div class="field-list"><!--[-->`);
    const each_array_4 = ensure_array_like(summary.withheld);
    for (let $$index_4 = 0, $$length = each_array_4.length; $$index_4 < $$length; $$index_4++) {
      let field = each_array_4[$$index_4];
      $$renderer2.push(`<span class="field-tag field-tag-withheld">${escape_html(field)}</span>`);
    }
    $$renderer2.push(`<!--]--></div></div></div></div></div></div></div>`);
  });
}
export {
  _page as default
};
