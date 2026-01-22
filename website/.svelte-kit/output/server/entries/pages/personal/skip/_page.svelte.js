import { a4 as store_get, a2 as head, a3 as escape_html, a0 as attr, a5 as unsubscribe_stores } from "../../../../chunks/index2.js";
import "@sveltejs/kit/internal";
import "../../../../chunks/exports.js";
import "../../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../../chunks/state.svelte.js";
import { v as vcpContext } from "../../../../chunks/context.js";
import { a as getSkipDayContext } from "../../../../chunks/gentian.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    store_get($$store_subs ??= {}, "$vcpContext", vcpContext);
    const skipContext = getSkipDayContext();
    let isSkipping = false;
    head("1nks1yp", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Skip Day - VCP Demo</title>`);
      });
    });
    $$renderer2.push(`<div class="container-narrow"><div class="breadcrumb svelte-1nks1yp"><a href="/personal/community" class="svelte-1nks1yp">← Back to challenge</a></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<section class="skip-header svelte-1nks1yp"><h1>Need a Break?</h1> <p class="text-muted">VCP detected context that might affect today's practice.</p></section> <section class="context-card card svelte-1nks1yp"><h3><i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i> Context Detected</h3> <div class="context-details svelte-1nks1yp"><div class="context-item svelte-1nks1yp"><span class="context-label svelte-1nks1yp">Trigger:</span> <span class="context-value svelte-1nks1yp">${escape_html(skipContext.detected.trigger.replace(/_/g, " "))}</span></div> <div class="context-item svelte-1nks1yp"><span class="context-label svelte-1nks1yp">Energy State:</span> <span class="context-value svelte-1nks1yp">${escape_html(skipContext.detected.energy_state)}</span></div> <div class="context-item svelte-1nks1yp"><span class="context-label svelte-1nks1yp">Current Streak:</span> <span class="context-value svelte-1nks1yp">${escape_html(skipContext.detected.current_streak)} days</span></div></div></section> <section class="recommendation-card card svelte-1nks1yp"><h3><i class="fa-solid fa-lightbulb" aria-hidden="true"></i> VCP Recommendation</h3> <p class="recommendation-text svelte-1nks1yp">${escape_html(skipContext.recommendation.reasoning)}</p></section> <section class="outcomes-card card svelte-1nks1yp"><h3>What Happens If You Skip?</h3> <div class="outcome-list svelte-1nks1yp"><div class="outcome-item svelte-1nks1yp"><span class="outcome-icon svelte-1nks1yp"><i class="fa-solid fa-fire" aria-hidden="true"></i></span> <div><strong>Your Streak</strong> <p class="text-sm text-muted">${escape_html(skipContext.recommendation.what_happens.streak)}</p></div></div> <div class="outcome-item svelte-1nks1yp"><span class="outcome-icon svelte-1nks1yp"><i class="fa-solid fa-chart-bar" aria-hidden="true"></i></span> <div><strong>Leaderboard</strong> <p class="text-sm text-muted">${escape_html(skipContext.recommendation.what_happens.leaderboard)}</p></div></div> <div class="outcome-item outcome-private svelte-1nks1yp"><span class="outcome-icon svelte-1nks1yp"><i class="fa-solid fa-lock" aria-hidden="true"></i></span> <div><strong>Your Private Reason</strong> <p class="text-sm text-muted">${escape_html(skipContext.recommendation.what_happens.private_reason)}</p></div></div></div></section> <section class="privacy-card card svelte-1nks1yp"><h3>Privacy Preview</h3> <div class="comparison-grid"><div class="comparison-column comparison-column-user"><h4><i class="fa-solid fa-user" aria-hidden="true"></i> You Will See:</h4> <ul class="comparison-list svelte-1nks1yp"><li class="svelte-1nks1yp">Today: Adjusted (night shift recovery)</li> <li class="svelte-1nks1yp">Days: 18/22 (4 adjusted)</li> <li class="svelte-1nks1yp">Full skip history with reasons</li></ul></div> <div class="comparison-column comparison-column-stakeholder"><h4><i class="fa-solid fa-users" aria-hidden="true"></i> Community Will See:</h4> <ul class="comparison-list svelte-1nks1yp"><li class="svelte-1nks1yp">Today: Adjusted</li> <li class="svelte-1nks1yp">Days: 18/22 (4 adjusted)</li> <li class="svelte-1nks1yp">No reason, no judgment</li></ul></div></div></section> <section class="actions svelte-1nks1yp"><button class="btn btn-secondary btn-lg"${attr("disabled", isSkipping, true)}>Practice Anyway <i class="fa-solid fa-dumbbell" aria-hidden="true"></i></button> <button class="btn btn-primary btn-lg"${attr("disabled", isSkipping, true)}>`);
      {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`Skip Today (Adjusted) <i class="fa-solid fa-check" aria-hidden="true"></i>`);
      }
      $$renderer2.push(`<!--]--></button></section> <p class="text-center text-sm text-muted" style="margin-top: 1rem;">Either choice is valid. Your wellbeing matters more than a streak.</p>`);
    }
    $$renderer2.push(`<!--]--></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};
