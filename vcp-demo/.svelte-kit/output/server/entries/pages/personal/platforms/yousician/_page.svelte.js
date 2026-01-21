import { b as attr_class, d as store_get, h as head, e as ensure_array_like, u as unsubscribe_stores } from "../../../../../chunks/index2.js";
import { v as vcpContext } from "../../../../../chunks/context2.js";
import { e as encodeContextToCSM1, f as formatTokenForDisplay, g as getTransmissionSummary } from "../../../../../chunks/token.js";
/* empty css                                                                 */
import { $ as escape_html } from "../../../../../chunks/context.js";
/* empty css                                                             */
function TokenInspector($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let {
      context
    } = $$props;
    let expanded = false;
    const token = encodeContextToCSM1(context);
    formatTokenForDisplay(token);
    getTransmissionSummary(context);
    $$renderer2.push(`<div${attr_class("token-inspector svelte-uurhug", void 0, { "expanded": expanded })}><button class="token-toggle svelte-uurhug"><span class="toggle-icon svelte-uurhug">${escape_html("▶")}</span> <span class="toggle-text svelte-uurhug">Inspect VCP Token</span> <span class="vcp-badge-mini svelte-uurhug">CSM-1</span></button> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
const yousician_lessons = [
  {
    id: "YS-L1-001",
    title: "Note Recognition Game",
    module: "Level 1",
    duration_minutes: 10,
    difficulty: "beginner",
    requires_amp: true,
    quiet_friendly: false,
    skills: [
      "note_recognition",
      "fret_navigation"
    ],
    alternative_quiet: "Use headphone amp or Tone Trainer mode",
    description: "Fun game to learn where notes are on the fretboard!"
  },
  {
    id: "YS-L1-002",
    title: "Chord Hero: G C D",
    module: "Level 1",
    duration_minutes: 15,
    difficulty: "beginner",
    requires_amp: true,
    quiet_friendly: false,
    skills: [
      "G_major",
      "C_major",
      "D_major",
      "timing"
    ],
    alternative_quiet: "Available in Tone Trainer mode",
    description: "Rock out to backing tracks while practicing basic chords!"
  },
  {
    id: "YS-L1-003",
    title: "Rhythm Challenge",
    module: "Level 1",
    duration_minutes: 12,
    difficulty: "beginner",
    requires_amp: true,
    quiet_friendly: false,
    skills: [
      "strumming_basics",
      "rhythm",
      "timing"
    ],
    alternative_quiet: "Can use acoustic muting technique",
    description: "Test your rhythm skills against the beat!"
  },
  {
    id: "YS-L2-001",
    title: "Fingerpicking Fundamentals",
    module: "Level 2",
    duration_minutes: 20,
    difficulty: "beginner",
    requires_amp: false,
    quiet_friendly: true,
    skills: [
      "fingerpicking",
      "finger_independence"
    ],
    description: "Perfect for quiet practice - no pick needed!"
  }
];
const lessonsData = {
  yousician_lessons
};
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    const ctx = store_get($$store_subs ??= {}, "$vcpContext", vcpContext);
    const lessons = () => {
      if (ctx?.constraints?.noise_restricted) {
        return lessonsData.yousician_lessons.filter((l) => l.quiet_friendly || l.alternative_quiet);
      }
      return lessonsData.yousician_lessons;
    };
    const syncedSkills = () => {
      return ctx?.current_skills?.skills_acquired?.slice(0, 4) || [];
    };
    head("9y8cwh", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Yousician - VCP Demo</title>`);
      });
    });
    $$renderer2.push(`<div class="platform-frame platform-frame-yousician"><div class="platform-header platform-header-yousician"><div class="platform-brand svelte-9y8cwh"><span class="platform-logo svelte-9y8cwh">🎮</span> <span class="platform-name svelte-9y8cwh">Yousician</span></div> <div class="vcp-badge">VCP Connected + Synced</div></div> <div class="platform-content">`);
    if (ctx) {
      $$renderer2.push("<!--[-->");
      {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="sync-banner svelte-9y8cwh"><div class="sync-content svelte-9y8cwh"><span class="sync-icon svelte-9y8cwh">🔄</span> <div><strong>Skills Synced from JustinGuitar!</strong> <p class="text-sm">We found ${escape_html(syncedSkills().length)} skills you've already learned. You can skip the basics!</p></div></div> <button class="btn btn-ghost btn-sm">Dismiss</button></div>`);
      }
      $$renderer2.push(`<!--]--> <div class="welcome-banner svelte-9y8cwh"><h1 class="svelte-9y8cwh">Ready to play, ${escape_html(ctx.public_profile.display_name)}?</h1> <p class="text-muted">Level: ${escape_html(ctx.public_profile.experience)} • Pace: ${escape_html(ctx.public_profile.pace)}</p></div> <section class="synced-skills card svelte-9y8cwh"><h3>🎯 Your Skills (Via VCP)</h3> <div class="skills-grid svelte-9y8cwh"><!--[-->`);
      const each_array = ensure_array_like(syncedSkills());
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let skill = each_array[$$index];
        $$renderer2.push(`<div class="skill-item svelte-9y8cwh"><span class="skill-check svelte-9y8cwh">✓</span> <span>${escape_html(skill.replace(/_/g, " "))}</span></div>`);
      }
      $$renderer2.push(`<!--]--></div> <p class="text-sm text-muted" style="margin-top: 1rem;">These skills were imported from your VCP profile - no need to prove them again!</p></section> <section class="challenges-section svelte-9y8cwh"><h2>🏆 Today's Challenges</h2> <div class="challenge-cards svelte-9y8cwh"><div class="challenge-card svelte-9y8cwh"><div class="challenge-icon svelte-9y8cwh">🎸</div> <h3>Chord Hero: G C D</h3> <p class="text-sm text-muted">Rock out with chords you know!</p> <div class="challenge-reward svelte-9y8cwh"><span>🌟 +50 XP</span></div> <button class="btn btn-primary">Play Now</button></div> <div class="challenge-card svelte-9y8cwh"><div class="challenge-icon svelte-9y8cwh">🎵</div> <h3>Rhythm Challenge</h3> <p class="text-sm text-muted">Test your timing skills</p> <div class="challenge-reward svelte-9y8cwh"><span>🌟 +30 XP</span></div> <button class="btn btn-secondary">Play Now</button></div> `);
      if (ctx.constraints?.noise_restricted) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="challenge-card quiet-mode svelte-9y8cwh"><div class="challenge-icon svelte-9y8cwh">🎧</div> <h3>Tone Trainer Mode</h3> <p class="text-sm text-muted">Practice with headphones - perfect for your quiet setting!</p> <div class="challenge-reward svelte-9y8cwh"><span class="badge badge-success">🔇 Quiet Friendly</span></div> <button class="btn btn-primary">Start Training</button></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div></section> <section class="lessons-section svelte-9y8cwh"><h2>📚 Lessons for You</h2> <div class="lessons-grid svelte-9y8cwh"><!--[-->`);
      const each_array_1 = ensure_array_like(lessons());
      for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
        let lesson = each_array_1[$$index_1];
        $$renderer2.push(`<div class="lesson-card svelte-9y8cwh"><div class="lesson-header svelte-9y8cwh"><h3>${escape_html(lesson.title)}</h3> <span class="badge badge-primary">${escape_html(lesson.module)}</span></div> <p class="text-sm text-muted">${escape_html(lesson.description)}</p> <div class="lesson-meta svelte-9y8cwh"><span>⏱️ ${escape_html(lesson.duration_minutes)} min</span> `);
        if (lesson.quiet_friendly) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<span class="badge badge-success text-xs">🔇 Quiet OK</span>`);
        } else {
          $$renderer2.push("<!--[!-->");
          if (lesson.alternative_quiet) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<span class="badge badge-warning text-xs">🎧 ${escape_html(lesson.alternative_quiet)}</span>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]-->`);
        }
        $$renderer2.push(`<!--]--></div></div>`);
      }
      $$renderer2.push(`<!--]--></div></section> <section class="shared-info card svelte-9y8cwh"><h3>What Yousician Received</h3> <div class="shared-comparison svelte-9y8cwh"><div class="shared-column svelte-9y8cwh"><h4 class="text-success svelte-9y8cwh">Shared:</h4> <div class="field-list"><span class="field-tag field-tag-shared">skill_level</span> <span class="field-tag field-tag-shared">skills_acquired</span> <span class="field-tag field-tag-shared">pace</span> <span class="field-tag field-tag-shared">noise_mode</span> <span class="field-tag field-tag-shared">display_name</span></div></div> <div class="shared-column svelte-9y8cwh"><h4 class="text-danger svelte-9y8cwh">Not Shared:</h4> <div class="field-list"><span class="field-tag field-tag-withheld">work_type</span> <span class="field-tag field-tag-withheld">schedule</span> <span class="field-tag field-tag-withheld">housing</span> <span class="field-tag field-tag-withheld">neighbor_situation</span></div></div></div> <div class="privacy-note" style="margin-top: 1rem;"><span class="privacy-note-icon">🔄</span> <span>Same VCP profile, different platform. Your skills transferred, your privacy remained.</span></div></section> <section class="token-section svelte-9y8cwh">`);
      TokenInspector($$renderer2, { context: ctx });
      $$renderer2.push(`<!----></section>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div></div> <div class="container-narrow" style="margin-top: 2rem;"><div class="nav-links svelte-9y8cwh"><a href="/personal/platforms/justinguitar" class="btn btn-ghost">← JustinGuitar</a> <a href="/personal/community" class="btn btn-primary">View Community →</a></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};
