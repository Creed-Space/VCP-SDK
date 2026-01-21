import { d as store_get, h as head, c as attr_style, e as ensure_array_like, b as attr_class, s as stringify, u as unsubscribe_stores } from "../../../../chunks/index2.js";
import { v as vcpContext } from "../../../../chunks/context2.js";
import { $ as escape_html } from "../../../../chunks/context.js";
function getCampionRecommendationContext() {
  return {
    contextUsed: [
      "career_goal: tech_lead",
      "learning_style: hands_on",
      "budget_remaining_eur: 5000",
      "workload_level: high"
    ],
    contextInfluencing: [
      "time_limited: true (prefers shorter sessions)",
      "schedule_irregular: true (needs self-paced options)",
      "health_considerations: true (flexibility needed)"
    ],
    contextWithheld: [
      "family_status",
      "dependent_ages",
      "childcare_hours",
      "health_conditions",
      "health_appointments",
      "evening_available_after"
    ]
  };
}
const courses = [
  {
    id: "SEC-101",
    title: "Cybersecurity Fundamentals",
    description: "Essential security practices for all engineering staff. Covers threat modeling, secure coding, and incident response basics.",
    duration_hours: 8,
    price_eur: 200,
    format: "self_paced",
    mandatory: true,
    deadline: "2026-03-15",
    career_paths: [
      "all"
    ],
    priority: "required",
    reasoning: "Mandatory compliance training - deadline March 15"
  },
  {
    id: "LEAD-101",
    title: "Engineering Leadership Essentials",
    description: "Core leadership skills for aspiring tech leads. Includes 1-on-1 coaching, team dynamics, and decision-making frameworks.",
    duration_weeks: 4,
    hours_per_week: 3,
    price_eur: 500,
    format: "self_paced",
    mandatory: false,
    career_paths: [
      "tech_lead",
      "engineering_manager"
    ],
    priority: "recommended",
    reasoning: "Directly aligned with your Tech Lead goal"
  },
  {
    id: "LEAD-102",
    title: "Technical Mentorship Skills",
    description: "Learn to effectively mentor junior engineers. Practical exercises and real-world scenarios.",
    duration_hours: 12,
    price_eur: 300,
    format: "video",
    mandatory: false,
    career_paths: [
      "tech_lead",
      "senior_engineer"
    ],
    priority: "recommended",
    reasoning: "Supports leadership development and team growth"
  },
  {
    id: "ARCH-201",
    title: "Advanced System Design",
    description: "Deep dive into distributed systems, scaling patterns, and architectural trade-offs. Intensive course with hands-on projects.",
    duration_weeks: 6,
    hours_per_week: 5,
    price_eur: 1e3,
    format: "interactive",
    mandatory: false,
    career_paths: [
      "tech_lead",
      "architect"
    ],
    priority: "deferred",
    defer_reason: "Your current workload is high - recommend deferring to Q2",
    reasoning: "Excellent for Tech Lead path but time-intensive"
  },
  {
    id: "COMM-101",
    title: "Technical Communication",
    description: "Improve your ability to communicate complex technical concepts to various audiences. Writing, presenting, and stakeholder management.",
    duration_hours: 6,
    price_eur: 150,
    format: "self_paced",
    mandatory: false,
    career_paths: [
      "tech_lead",
      "engineering_manager",
      "architect"
    ],
    priority: "recommended",
    reasoning: "Essential skill for leadership roles"
  }
];
const budget = {
  annual_total_eur: 6e3,
  spent_eur: 1e3,
  remaining_eur: 5e3
};
const coursesData = {
  courses,
  budget
};
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    store_get($$store_subs ??= {}, "$vcpContext", vcpContext);
    const recommendationContext = getCampionRecommendationContext();
    const courses2 = coursesData.courses.sort((a, b) => {
      const priority = { required: 0, recommended: 1, deferred: 2 };
      return (priority[a.priority] ?? 2) - (priority[b.priority] ?? 2);
    });
    const budgetTotal = coursesData.budget.annual_total_eur;
    const budgetSpent = coursesData.budget.spent_eur;
    const budgetRemaining = coursesData.budget.remaining_eur;
    const budgetUsedPercent = budgetSpent / budgetTotal * 100;
    function getPriorityBadge(priority) {
      switch (priority) {
        case "required":
          return { class: "badge-danger", text: "Required" };
        case "recommended":
          return { class: "badge-success", text: "Recommended" };
        case "deferred":
          return { class: "badge-warning", text: "Deferred" };
        default:
          return { class: "badge-primary", text: priority };
      }
    }
    function formatDuration(course) {
      if (course.duration_hours) {
        return `${course.duration_hours} hours`;
      }
      if (course.duration_weeks && course.hours_per_week) {
        return `${course.duration_weeks} weeks (${course.hours_per_week}h/week)`;
      }
      return "Self-paced";
    }
    head("1wqcjlh", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Morning Recommendations - Professional Demo</title>`);
      });
    });
    $$renderer2.push(`<div class="container-narrow"><div class="breadcrumb svelte-1wqcjlh"><a href="/professional" class="svelte-1wqcjlh">← Back to profile</a></div> <header class="journey-header svelte-1wqcjlh"><span class="badge badge-primary">Morning Journey</span> <h1 class="svelte-1wqcjlh">Course Recommendations</h1> <p class="journey-subtitle svelte-1wqcjlh">Campion asks: "What courses should I take to become a Tech Lead?"</p></header> <section class="card budget-card svelte-1wqcjlh"><div class="budget-header svelte-1wqcjlh"><h3>Training Budget</h3> <span class="budget-amount svelte-1wqcjlh">€${escape_html(budgetRemaining.toLocaleString())} remaining</span></div> <div class="progress"><div class="progress-bar"${attr_style(`width: ${stringify(budgetUsedPercent)}%`)}></div></div> <div class="budget-labels svelte-1wqcjlh"><span class="text-sm text-muted">€${escape_html(budgetSpent.toLocaleString())} used</span> <span class="text-sm text-muted">€${escape_html(budgetTotal.toLocaleString())} total</span></div></section> <section class="card context-card svelte-1wqcjlh"><h3>Context Used for Recommendations</h3> <div class="context-grid svelte-1wqcjlh"><div class="context-section svelte-1wqcjlh"><h4 class="svelte-1wqcjlh">Shared with LMS</h4> <div class="field-list"><!--[-->`);
    const each_array = ensure_array_like(recommendationContext.contextUsed);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let field = each_array[$$index];
      $$renderer2.push(`<span class="field-tag field-tag-shared">${escape_html(field)}</span>`);
    }
    $$renderer2.push(`<!--]--></div></div> <div class="context-section svelte-1wqcjlh"><h4 class="svelte-1wqcjlh">Influenced (Not Exposed)</h4> <div class="field-list"><!--[-->`);
    const each_array_1 = ensure_array_like(recommendationContext.contextInfluencing);
    for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
      let field = each_array_1[$$index_1];
      $$renderer2.push(`<span class="field-tag">${escape_html(field.split("(")[0].trim())}</span>`);
    }
    $$renderer2.push(`<!--]--></div></div></div></section> <section class="recommendations svelte-1wqcjlh"><h2 class="svelte-1wqcjlh">Recommended Courses</h2> <!--[-->`);
    const each_array_2 = ensure_array_like(courses2);
    for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
      let course = each_array_2[$$index_2];
      const badge = getPriorityBadge(course.priority ?? "recommended");
      $$renderer2.push(`<article class="card course-card svelte-1wqcjlh"><div class="course-header svelte-1wqcjlh"><div class="course-title-row svelte-1wqcjlh"><h3 class="svelte-1wqcjlh">${escape_html(course.title)}</h3> <span${attr_class(`badge ${stringify(badge.class)}`, "svelte-1wqcjlh")}>${escape_html(badge.text)}</span></div> <p class="course-id text-subtle text-xs">${escape_html(course.id)}</p></div> <p class="course-description svelte-1wqcjlh">${escape_html(course.description)}</p> <div class="course-meta svelte-1wqcjlh"><span class="meta-item svelte-1wqcjlh"><span class="meta-icon">⏱️</span> ${escape_html(formatDuration(course))}</span> <span class="meta-item svelte-1wqcjlh"><span class="meta-icon">💶</span> €${escape_html(course.price_eur)}</span> <span class="meta-item svelte-1wqcjlh"><span class="meta-icon">📚</span> ${escape_html(course.format.replace(/_/g, " "))}</span></div> <div class="course-reasoning svelte-1wqcjlh"><span class="reasoning-icon">💡</span> <span>${escape_html(course.reasoning)}</span></div> `);
      if (course.defer_reason) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="defer-note svelte-1wqcjlh"><span class="defer-icon">⏳</span> <span>${escape_html(course.defer_reason)}</span></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> `);
      if (course.deadline) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="deadline-note svelte-1wqcjlh"><span class="deadline-icon">⚠️</span> <span>Deadline: ${escape_html(new Date(course.deadline).toLocaleDateString())}</span></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></article>`);
    }
    $$renderer2.push(`<!--]--></section> <section class="privacy-note"><span class="privacy-note-icon">🔒</span> <div><strong>What stays private:</strong> <p class="text-sm" style="margin-top: 0.25rem;">${escape_html(recommendationContext.contextWithheld.join(", "))}</p> <p class="text-sm text-muted" style="margin-top: 0.5rem;">The LMS knows constraints exist (e.g., "time_limited: true") but not WHY.
				Campion's family situation and health details remain private.</p></div></section> <section class="journey-nav svelte-1wqcjlh"><a href="/professional/audit" class="btn btn-primary">View Audit Trail →</a> <p class="text-sm text-muted" style="margin-top: 0.5rem;">See what Campion sees vs what HR sees</p></section></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};
