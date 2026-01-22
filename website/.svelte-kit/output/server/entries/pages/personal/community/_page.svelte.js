import { a4 as store_get, a2 as head, a1 as attr_class, a0 as attr, a3 as escape_html, a8 as ensure_array_like, a6 as attr_style, a7 as stringify, a5 as unsubscribe_stores } from "../../../../chunks/index2.js";
import { v as vcpContext } from "../../../../chunks/context.js";
import { g as gentianChallengeProgress, c as challengeLeaderboard } from "../../../../chunks/gentian.js";
import { A as AuditPanel } from "../../../../chunks/AuditPanel.js";
const challenge = { "name": "30-Day Guitar Challenge", "total_days": 30, "current_day": 21 };
const badges = { "available": [{ "id": "week_warrior", "name": "Week Warrior", "description": "Complete 7 consecutive days", "icon": "🏆" }, { "id": "chord_master_basic", "name": "Chord Master (Basic)", "description": "Master G, C, D, and Em chords", "icon": "🎸" }, { "id": "consistent_learner", "name": "Consistent Learner", "description": "Practice on 20+ days in the challenge", "icon": "⭐" }, { "id": "early_bird", "name": "Early Bird", "description": "Practice before 9am for 5 days", "icon": "🌅" }, { "id": "night_owl", "name": "Night Owl", "description": "Practice after 9pm for 5 days", "icon": "🦉" }, { "id": "song_learner", "name": "Song Learner", "description": "Complete your first full song", "icon": "🎵" }] };
const leaderboard = [{ "rank": 1, "display_name": "MelodyMaster", "days_completed": 21, "days_adjusted": 0, "total_days": 21, "is_current_user": false, "badges": ["week_warrior", "consistent_learner", "early_bird", "song_learner"] }, { "rank": 2, "display_name": "ChordCrusher", "days_completed": 20, "days_adjusted": 1, "total_days": 21, "is_current_user": false, "badges": ["week_warrior", "chord_master_basic", "consistent_learner"] }, { "rank": 3, "display_name": "Gentian", "days_completed": 18, "days_adjusted": 3, "total_days": 21, "is_current_user": true, "badges": ["week_warrior", "chord_master_basic", "consistent_learner"] }, { "rank": 4, "display_name": "StringNewbie", "days_completed": 17, "days_adjusted": 2, "total_days": 21, "is_current_user": false, "badges": ["week_warrior", "chord_master_basic"] }, { "rank": 5, "display_name": "GuitarDreamer", "days_completed": 15, "days_adjusted": 4, "total_days": 21, "is_current_user": false, "badges": ["chord_master_basic"] }];
const privacy_explainer = { "what_community_cannot_see": ["Why days were adjusted", "Work schedule", "Personal circumstances", "Specific constraint reasons", "Practice session times", "Location or device info"], "adjusted_days_explanation": "'Adjusted' means life happened. No questions asked, no judgment. Everyone's situation is different, and VCP ensures your privacy is protected while still participating in the community." };
const challengeData = {
  challenge,
  badges,
  leaderboard,
  privacy_explainer
};
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let showAuditPanel = true;
    const ctx = store_get($$store_subs ??= {}, "$vcpContext", vcpContext);
    const progress = gentianChallengeProgress;
    const leaderboard2 = challengeLeaderboard;
    const badges2 = challengeData.badges;
    function getProgressPercent(completed, total) {
      return Math.round(completed / total * 100);
    }
    const auditEntries = () => {
      const entries = [];
      const sharedFields = [
        {
          field: "display_name",
          value: ctx?.public_profile?.display_name
        },
        {
          field: "days_completed",
          value: String(progress.days_completed)
        },
        {
          field: "days_adjusted",
          value: `${progress.days_adjusted} (count only)`
        },
        {
          field: "badges",
          value: `${progress.badges?.length ?? 0} earned`
        },
        { field: "rank", value: "#3" }
      ];
      for (const { field, value } of sharedFields) {
        entries.push({
          field: field.replace(/_/g, " "),
          category: "shared",
          value: String(value ?? "—"),
          stakeholder: "Community"
        });
      }
      entries.push({
        field: "adjusted days policy",
        category: "influenced",
        value: "active",
        reason: "Private reasons accepted without penalty"
      });
      const withheldFields = [
        {
          field: "Jan 18 adjustment reason",
          reason: "Night shift recovery"
        },
        {
          field: "Jan 14 adjustment reason",
          reason: "Double shift exhaustion"
        },
        {
          field: "Jan 10 adjustment reason",
          reason: "Night shift recovery"
        },
        { field: "work schedule", reason: "Rotating shift details" },
        {
          field: "housing situation",
          reason: "Apartment noise constraints"
        }
      ];
      for (const { field, reason } of withheldFields) {
        entries.push({ field, category: "withheld", reason });
      }
      return entries;
    };
    head("h76udj", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>30-Day Challenge - VCP Demo</title>`);
      });
    });
    $$renderer2.push(`<div${attr_class("page-layout svelte-h76udj", void 0, { "audit-open": showAuditPanel })}><div class="main-content svelte-h76udj"><div class="platform-frame platform-frame-community"><div class="platform-header platform-header-community"><div class="platform-brand svelte-h76udj"><span class="platform-logo svelte-h76udj"><i class="fa-solid fa-users" aria-hidden="true"></i></span> <span class="platform-name svelte-h76udj">Guitar Community</span></div> <div class="header-actions svelte-h76udj"><div class="vcp-badge">VCP Connected</div> <button class="audit-toggle-btn svelte-h76udj"${attr("aria-label", "Hide audit panel")}><i class="fa-solid fa-clipboard-list" aria-hidden="true"></i> ${escape_html("Hide")} Audit</button></div></div> <div class="platform-content"><header class="challenge-header svelte-h76udj"><h1 class="svelte-h76udj"><i class="fa-solid fa-trophy" aria-hidden="true"></i> ${escape_html(challengeData.challenge.name)}</h1> <p class="text-muted">Day ${escape_html(challengeData.challenge.current_day)} of ${escape_html(challengeData.challenge.total_days)}</p></header> <section class="leaderboard-section card svelte-h76udj"><h2>Leaderboard</h2> <table class="table"><thead><tr><th>Rank</th><th>Player</th><th>Progress</th><th>Badges</th></tr></thead><tbody><!--[-->`);
    const each_array = ensure_array_like(leaderboard2);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let entry = each_array[$$index];
      $$renderer2.push(`<tr${attr_class("", void 0, { "highlighted": entry.is_current_user })}><td class="rank-cell svelte-h76udj">`);
      if (entry.rank === 1) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<i class="fa-solid fa-medal" aria-hidden="true"></i>`);
      } else {
        $$renderer2.push("<!--[!-->");
        if (entry.rank === 2) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<i class="fa-solid fa-medal" aria-hidden="true"></i>`);
        } else {
          $$renderer2.push("<!--[!-->");
          if (entry.rank === 3) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<i class="fa-solid fa-medal" aria-hidden="true"></i>`);
          } else {
            $$renderer2.push("<!--[!-->");
            $$renderer2.push(`#${escape_html(entry.rank)}`);
          }
          $$renderer2.push(`<!--]-->`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]--></td><td><span class="player-name svelte-h76udj">${escape_html(entry.display_name)} `);
      if (entry.is_current_user) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<span class="badge badge-primary text-xs">You</span>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></span></td><td><div class="progress-cell svelte-h76udj"><span class="progress-text svelte-h76udj">${escape_html(entry.days_completed)}/${escape_html(entry.total_days)} `);
      if (entry.days_adjusted > 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<span class="adjusted-count svelte-h76udj">(${escape_html(entry.days_adjusted)} adjusted)</span>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></span> <div class="progress" style="height: 4px;"><div class="progress-bar progress-bar-success"${attr_style(`width: ${stringify(getProgressPercent(entry.days_completed, entry.total_days))}%`)}></div></div></div></td><td><span class="badges-count svelte-h76udj">${escape_html(challengeData.leaderboard.find((l) => l.display_name === entry.display_name)?.badges.length || 0)}</span></td></tr>`);
    }
    $$renderer2.push(`<!--]--></tbody></table></section> <section class="explainer-card card svelte-h76udj"><h3>ℹ️ What are "Adjusted" Days?</h3> <p class="text-muted">${escape_html(challengeData.privacy_explainer.adjusted_days_explanation)}</p> <div class="privacy-note" style="margin-top: 1rem;"><span class="privacy-note-icon"><i class="fa-solid fa-lock" aria-hidden="true"></i></span> <span><strong>Community cannot see:</strong> ${escape_html(challengeData.privacy_explainer.what_community_cannot_see.join(", "))}</span></div></section> <section class="your-stats card svelte-h76udj"><h2>Your Stats</h2> <div class="stats-grid svelte-h76udj"><div class="stat-card svelte-h76udj"><span class="stat-value svelte-h76udj">${escape_html(progress.days_completed)}</span> <span class="stat-label svelte-h76udj">Days Practiced</span></div> <div class="stat-card svelte-h76udj"><span class="stat-value svelte-h76udj">${escape_html(progress.days_adjusted)}</span> <span class="stat-label svelte-h76udj">Adjusted Days</span></div> <div class="stat-card svelte-h76udj"><span class="stat-value svelte-h76udj">${escape_html(progress.current_streak)}</span> <span class="stat-label svelte-h76udj">Current Streak</span></div> <div class="stat-card svelte-h76udj"><span class="stat-value svelte-h76udj">${escape_html(progress.best_streak)}</span> <span class="stat-label svelte-h76udj">Best Streak</span></div></div> <div class="badges-section svelte-h76udj"><h4 class="svelte-h76udj">Your Badges</h4> <div class="badges-list svelte-h76udj"><!--[-->`);
    const each_array_1 = ensure_array_like(progress.badges || []);
    for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
      let badgeId = each_array_1[$$index_1];
      const badge = badges2.available.find((b) => b.id === badgeId);
      if (badge) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="badge-item svelte-h76udj"><span class="badge-icon svelte-h76udj">${escape_html(badge.icon)}</span> <div><span class="badge-name svelte-h76udj">${escape_html(badge.name)}</span> <span class="badge-desc svelte-h76udj">${escape_html(badge.description)}</span></div></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div></div></section> <section class="privacy-comparison card svelte-h76udj"><h2>What Others See vs What You See</h2> <div class="comparison-grid"><div class="comparison-column comparison-column-stakeholder"><h4><i class="fa-solid fa-users" aria-hidden="true"></i> Community Sees:</h4> <ul class="comparison-list svelte-h76udj"><li class="svelte-h76udj">Your display name: <strong>Gentian</strong></li> <li class="svelte-h76udj">Days completed: <strong>18</strong></li> <li class="svelte-h76udj">Days adjusted: <strong>3</strong> (count only)</li> <li class="svelte-h76udj">Badges earned: <strong>3</strong></li> <li class="svelte-h76udj">Rank: <strong>#3</strong></li></ul></div> <div class="comparison-column comparison-column-user"><h4><i class="fa-solid fa-user" aria-hidden="true"></i> You See:</h4> <ul class="comparison-list svelte-h76udj"><li class="svelte-h76udj">All of the above, plus:</li> <li class="svelte-h76udj">Why Jan 18 was adjusted: <em class="svelte-h76udj">Night shift recovery</em></li> <li class="svelte-h76udj">Why Jan 14 was adjusted: <em class="svelte-h76udj">Double shift exhaustion</em></li> <li class="svelte-h76udj">Why Jan 10 was adjusted: <em class="svelte-h76udj">Night shift recovery</em></li> <li class="svelte-h76udj">Your full schedule constraints</li></ul></div></div></section> <section class="skip-section svelte-h76udj"><a href="/personal/skip" class="btn btn-secondary btn-lg">Need to Skip Today? →</a> <p class="text-sm text-muted" style="margin-top: 0.5rem;">See how VCP handles private skip reasons</p></section></div></div> <div class="container-narrow" style="margin-top: 2rem;"><div class="nav-links svelte-h76udj"><a href="/personal/platforms/yousician" class="btn btn-ghost">← Yousician</a> <a href="/personal" class="btn btn-primary">Back to Profile →</a></div></div></div> `);
    if (ctx) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<aside class="audit-sidebar svelte-h76udj">`);
      AuditPanel($$renderer2, {
        entries: auditEntries(),
        title: "Privacy Audit",
        compact: true,
        showTimestamps: false
      });
      $$renderer2.push(`<!----></aside>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};
