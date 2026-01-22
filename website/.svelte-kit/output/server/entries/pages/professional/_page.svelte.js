import { a4 as store_get, a2 as head, a3 as escape_html, a5 as unsubscribe_stores } from "../../../chunks/index2.js";
import { v as vcpContext } from "../../../chunks/context.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    const ctx = store_get($$store_subs ??= {}, "$vcpContext", vcpContext);
    head("1nf9pxw", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Professional Demo - VCP</title>`);
      });
      $$renderer3.push(`<meta name="description" content="See how VCP enables enterprise L&amp;D while keeping private life circumstances from being exposed to HR. Privacy-preserving career recommendations."/> <meta property="og:title" content="Professional Development Demo - VCP"/> <meta property="og:description" content="Follow Campion through a morning of course recommendations. See how VCP protects personal context from HR."/>`);
    });
    $$renderer2.push(`<div class="container-narrow"><div class="breadcrumb svelte-1nf9pxw"><a href="/" class="svelte-1nf9pxw">← Back to demos</a></div> <header class="demo-header svelte-1nf9pxw"><div class="demo-badge svelte-1nf9pxw"><span class="badge badge-success">Professional Development Demo</span></div> <h1>Meet Campion</h1> <p class="demo-intro svelte-1nf9pxw">Senior Software Engineer at TechCorp, working toward becoming a Tech Lead.
			Has private circumstances that affect scheduling but shouldn't be visible to HR.</p></header> `);
    if (ctx) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<section class="profile-card card svelte-1nf9pxw"><div class="profile-header svelte-1nf9pxw"><div class="profile-avatar svelte-1nf9pxw"><i class="fa-solid fa-user" aria-hidden="true"></i></div> <div class="profile-info svelte-1nf9pxw"><h2 class="svelte-1nf9pxw">${escape_html(ctx.public_profile.display_name)}</h2> <p class="text-muted">${escape_html(ctx.public_profile.role?.replace(/_/g, " "))}</p> <p class="text-subtle text-sm">Team: ${escape_html(ctx.public_profile.team?.replace(/_/g, " "))}</p></div> <div class="vcp-badge">VCP Connected</div></div> <div class="profile-details svelte-1nf9pxw"><div class="detail-group svelte-1nf9pxw"><h4 class="svelte-1nf9pxw">Career Goal</h4> <p class="svelte-1nf9pxw">${escape_html(ctx.public_profile.career_goal?.replace(/_/g, " "))} in ${escape_html(ctx.public_profile.career_timeline?.replace(/_/g, " "))}</p></div> <div class="detail-group svelte-1nf9pxw"><h4 class="svelte-1nf9pxw">Learning Style</h4> <p class="svelte-1nf9pxw">${escape_html(ctx.public_profile.learning_style?.replace(/_/g, " "))}</p></div> <div class="detail-group svelte-1nf9pxw"><h4 class="svelte-1nf9pxw">Training Budget</h4> <p class="svelte-1nf9pxw">€${escape_html(ctx.shared_with_manager?.budget_remaining_eur)} remaining</p></div></div> <div class="constitution-info svelte-1nf9pxw"><span class="text-subtle text-sm">Active Constitution:</span> <span class="badge badge-primary">${escape_html(ctx.constitution.id)}@${escape_html(ctx.constitution.version)}</span></div></section> <section class="constraints-preview card svelte-1nf9pxw"><h3>Private Context (What VCP Knows)</h3> <p class="text-muted text-sm" style="margin-bottom: 1rem;">These constraints influence recommendations but are NEVER exposed to platforms or HR.</p> <div class="constraint-flags svelte-1nf9pxw">`);
      if (ctx.constraints?.time_limited) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="constraint-flag svelte-1nf9pxw"><span class="flag-indicator flag-active svelte-1nf9pxw"></span> <span>Time Limited</span> <span class="flag-private svelte-1nf9pxw">(reason private)</span></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> `);
      if (ctx.constraints?.health_considerations) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="constraint-flag svelte-1nf9pxw"><span class="flag-indicator flag-active svelte-1nf9pxw"></span> <span>Health Considerations</span> <span class="flag-private svelte-1nf9pxw">(reason private)</span></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> `);
      if (ctx.constraints?.schedule_irregular) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="constraint-flag svelte-1nf9pxw"><span class="flag-indicator flag-active svelte-1nf9pxw"></span> <span>Schedule Irregular</span> <span class="flag-private svelte-1nf9pxw">(reason private)</span></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> `);
      if (ctx.constraints?.energy_variable) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="constraint-flag svelte-1nf9pxw"><span class="flag-indicator flag-active svelte-1nf9pxw"></span> <span>Energy Variable</span> <span class="flag-private svelte-1nf9pxw">(reason private)</span></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div> <div class="privacy-note" style="margin-top: 1rem;"><span class="privacy-note-icon"><i class="fa-solid fa-lock" aria-hidden="true"></i></span> <span>HR and platforms see boolean flags only. They know constraints exist but not WHY.
					The reasons (family situation, health details) stay with Campion.</span></div></section> <section class="journey-start svelte-1nf9pxw"><a href="/professional/morning" class="btn btn-primary btn-lg">Start Morning Journey →</a> <p class="text-muted text-sm" style="margin-top: 0.5rem;">See how VCP handles course recommendations</p></section>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div class="loading svelte-1nf9pxw">Loading profile...</div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};
