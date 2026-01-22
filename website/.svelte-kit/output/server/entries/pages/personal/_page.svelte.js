import { a4 as store_get, a2 as head, a3 as escape_html, a8 as ensure_array_like, a6 as attr_style, a5 as unsubscribe_stores, a7 as stringify } from "../../../chunks/index2.js";
import { v as vcpContext } from "../../../chunks/context.js";
import { g as gentianChallengeProgress } from "../../../chunks/gentian.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    const ctx = store_get($$store_subs ??= {}, "$vcpContext", vcpContext);
    const progress = gentianChallengeProgress;
    head("1b808f1", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Personal Demo - VCP</title>`);
      });
      $$renderer3.push(`<meta name="description" content="See how VCP enables cross-platform portability while protecting personal circumstances from community judgment. Configure once, use everywhere."/> <meta property="og:title" content="Personal Growth Demo - VCP"/> <meta property="og:description" content="Follow Gentian learning guitar across platforms. See how VCP protects work schedule and living situation from the community."/>`);
    });
    $$renderer2.push(`<div class="container-narrow"><div class="breadcrumb svelte-1b808f1"><a href="/" class="svelte-1b808f1">← Back to demos</a></div> <header class="demo-header svelte-1b808f1"><div class="demo-badge svelte-1b808f1"><span class="badge badge-primary">Personal Growth Demo</span></div> <h1>Meet Gentian</h1> <p class="demo-intro svelte-1b808f1">Factory worker learning guitar for stress relief.
			Has constraints (shift work, apartment living) that should stay private from the community.</p></header> `);
    if (ctx) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<section class="profile-card card svelte-1b808f1"><div class="profile-header svelte-1b808f1"><div class="profile-avatar svelte-1b808f1"><i class="fa-solid fa-guitar" aria-hidden="true"></i></div> <div class="profile-info svelte-1b808f1"><h2 class="svelte-1b808f1">${escape_html(ctx.public_profile.display_name)}</h2> <p class="text-muted">${escape_html(ctx.public_profile.goal?.replace(/_/g, " "))}</p> <p class="text-subtle text-sm">${escape_html(ctx.public_profile.experience)} • ${escape_html(ctx.current_skills?.weeks_learning)} weeks learning</p></div> <div class="vcp-badge">VCP Connected</div></div> <div class="profile-details svelte-1b808f1"><div class="detail-group svelte-1b808f1"><h4 class="svelte-1b808f1">Motivation</h4> <p class="svelte-1b808f1">${escape_html(ctx.public_profile.motivation?.replace(/_/g, " "))}</p></div> <div class="detail-group svelte-1b808f1"><h4 class="svelte-1b808f1">Learning Style</h4> <p class="svelte-1b808f1">${escape_html(ctx.public_profile.learning_style?.replace(/_/g, " "))}</p></div> <div class="detail-group svelte-1b808f1"><h4 class="svelte-1b808f1">Pace</h4> <p class="svelte-1b808f1">${escape_html(ctx.public_profile.pace)}</p></div></div> <div class="skills-section svelte-1b808f1"><h4 class="svelte-1b808f1">Skills Acquired</h4> <div class="skills-list svelte-1b808f1"><!--[-->`);
      const each_array = ensure_array_like(ctx.current_skills?.skills_acquired || []);
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let skill = each_array[$$index];
        $$renderer2.push(`<span class="skill-tag svelte-1b808f1">${escape_html(skill.replace(/_/g, " "))}</span>`);
      }
      $$renderer2.push(`<!--]--></div></div> <div class="constitution-info svelte-1b808f1"><span class="text-subtle text-sm">Active Constitution:</span> <span class="badge badge-primary">${escape_html(ctx.constitution.id)}@${escape_html(ctx.constitution.version)}</span></div></section> <section class="constraints-preview card svelte-1b808f1"><h3>Private Context (What VCP Knows)</h3> <p class="text-muted text-sm" style="margin-bottom: 1rem;">These constraints affect recommendations and community participation,
				but are NEVER exposed to platforms or other users.</p> <div class="constraint-flags svelte-1b808f1">`);
      if (ctx.constraints?.time_limited) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="constraint-flag svelte-1b808f1"><span class="flag-indicator flag-active svelte-1b808f1"></span> <span>Time Limited</span> <span class="flag-private svelte-1b808f1">(shift work)</span></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> `);
      if (ctx.constraints?.noise_restricted) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="constraint-flag svelte-1b808f1"><span class="flag-indicator flag-active svelte-1b808f1"></span> <span>Noise Restricted</span> <span class="flag-private svelte-1b808f1">(apartment)</span></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> `);
      if (ctx.constraints?.budget_limited) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="constraint-flag svelte-1b808f1"><span class="flag-indicator flag-active svelte-1b808f1"></span> <span>Budget Limited</span> <span class="flag-private svelte-1b808f1">(factory wages)</span></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> `);
      if (ctx.constraints?.energy_variable) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="constraint-flag svelte-1b808f1"><span class="flag-indicator flag-active svelte-1b808f1"></span> <span>Energy Variable</span> <span class="flag-private svelte-1b808f1">(rotating shifts)</span></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> `);
      if (ctx.constraints?.schedule_irregular) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="constraint-flag svelte-1b808f1"><span class="flag-indicator flag-active svelte-1b808f1"></span> <span>Schedule Irregular</span> <span class="flag-private svelte-1b808f1">(night/day rotation)</span></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div> <div class="privacy-note" style="margin-top: 1rem;"><span class="privacy-note-icon"><i class="fa-solid fa-lock" aria-hidden="true"></i></span> <span>Community members see "18/21 (3 adjusted)" - they don't know WHY days were adjusted.
					Gentian's work schedule and living situation stay private.</span></div></section> <section class="challenge-preview card svelte-1b808f1"><h3><i class="fa-solid fa-trophy" aria-hidden="true"></i> 30-Day Challenge Progress</h3> <div class="challenge-stats svelte-1b808f1"><div class="stat svelte-1b808f1"><span class="stat-value svelte-1b808f1">${escape_html(progress.days_completed)}</span> <span class="stat-label svelte-1b808f1">Days Practiced</span></div> <div class="stat svelte-1b808f1"><span class="stat-value svelte-1b808f1">${escape_html(progress.days_adjusted)}</span> <span class="stat-label svelte-1b808f1">Adjusted</span></div> <div class="stat svelte-1b808f1"><span class="stat-value svelte-1b808f1">${escape_html(progress.current_streak)}</span> <span class="stat-label svelte-1b808f1">Current Streak</span></div></div> <div class="progress" style="margin-top: 1rem;"><div class="progress-bar progress-bar-success"${attr_style(`width: ${stringify(progress.days_completed / progress.total_days * 100)}%`)}></div></div> <p class="text-sm text-muted text-center" style="margin-top: 0.5rem;">${escape_html(progress.days_completed)}/${escape_html(progress.total_days)} days • Rank #3 in community</p></section> <section class="demo-paths svelte-1b808f1"><h2 class="svelte-1b808f1">Choose Your Path</h2> <div class="grid grid-2 gap-lg"><a href="/personal/platforms/justinguitar" class="card card-hover path-card svelte-1b808f1"><div class="path-icon svelte-1b808f1"><i class="fa-solid fa-mobile" aria-hidden="true"></i></div> <h3 class="svelte-1b808f1">Portability Demo</h3> <p class="text-muted text-sm">See how the same profile works across JustinGuitar and Yousician -
						configure once, use everywhere.</p> <span class="btn btn-secondary" style="margin-top: auto;">Try Platforms →</span></a> <a href="/personal/community" class="card card-hover path-card svelte-1b808f1"><div class="path-icon svelte-1b808f1"><i class="fa-solid fa-users" aria-hidden="true"></i></div> <h3 class="svelte-1b808f1">Privacy Demo</h3> <p class="text-muted text-sm">See how community challenges work with adjusted days -
						participate without exposing personal life.</p> <span class="btn btn-secondary" style="margin-top: auto;">View Community →</span></a></div></section>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div class="loading svelte-1b808f1">Loading profile...</div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};
