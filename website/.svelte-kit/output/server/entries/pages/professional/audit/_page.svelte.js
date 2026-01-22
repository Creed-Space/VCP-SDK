import { a4 as store_get, a2 as head, a1 as attr_class, a3 as escape_html, a8 as ensure_array_like, a5 as unsubscribe_stores } from "../../../../chunks/index2.js";
import { g as getStakeholderView, a as getAuditSummary, v as vcpContext, t as todayAudit } from "../../../../chunks/context.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let activeView = "employee";
    store_get($$store_subs ??= {}, "$vcpContext", vcpContext);
    const auditEntries = store_get($$store_subs ??= {}, "$todayAudit", todayAudit);
    getStakeholderView(auditEntries, "hr");
    const summary = getAuditSummary(auditEntries);
    function formatTime(timestamp) {
      return new Date(timestamp).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
    }
    head("ecrwq4", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Audit Trail - Professional Demo</title>`);
      });
    });
    $$renderer2.push(`<div class="container-narrow"><div class="breadcrumb svelte-ecrwq4"><a href="/professional/morning" class="svelte-ecrwq4">← Back to recommendations</a></div> <header class="audit-header svelte-ecrwq4"><h1>Audit Trail</h1> <p class="audit-subtitle svelte-ecrwq4">See exactly what was shared and what stayed private.</p></header> <section class="view-toggle-section svelte-ecrwq4"><div class="view-toggle"><button${attr_class("view-toggle-btn", void 0, { "active": activeView === "employee" })}><i class="fa-solid fa-user" aria-hidden="true"></i> Employee View</button> <button${attr_class("view-toggle-btn", void 0, { "active": activeView === "hr" })}><i class="fa-solid fa-building" aria-hidden="true"></i> HR View</button></div> <p class="text-sm text-muted" style="margin-top: 0.5rem;">${escape_html(
      "What Campion sees - full detail including private context"
    )}</p></section> <section class="comparison-grid"><div${attr_class("comparison-column comparison-column-user svelte-ecrwq4", void 0, { "active": activeView === "employee" })}><div class="column-header svelte-ecrwq4"><h3><i class="fa-solid fa-user" aria-hidden="true"></i> Employee View</h3> <span class="badge badge-success">Full Access</span></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="audit-entries svelte-ecrwq4">`);
      const each_array = ensure_array_like(auditEntries);
      if (each_array.length !== 0) {
        $$renderer2.push("<!--[-->");
        for (let $$index_2 = 0, $$length = each_array.length; $$index_2 < $$length; $$index_2++) {
          let entry = each_array[$$index_2];
          $$renderer2.push(`<div class="audit-entry animate-fade-in"><div class="audit-entry-time">${escape_html(formatTime(entry.timestamp))}</div> <div class="audit-entry-title">${escape_html(entry.event_type.replace(/_/g, " "))}</div> <div class="entry-detail svelte-ecrwq4"><h5 class="svelte-ecrwq4">Fields Shared:</h5> <div class="field-list"><!--[-->`);
          const each_array_1 = ensure_array_like(entry.data_shared || []);
          for (let $$index = 0, $$length2 = each_array_1.length; $$index < $$length2; $$index++) {
            let field = each_array_1[$$index];
            $$renderer2.push(`<span class="field-tag field-tag-shared">${escape_html(field)}</span>`);
          }
          $$renderer2.push(`<!--]--></div></div> <div class="entry-detail svelte-ecrwq4"><h5 class="svelte-ecrwq4">Fields Withheld:</h5> <div class="field-list"><!--[-->`);
          const each_array_2 = ensure_array_like(entry.data_withheld || []);
          for (let $$index_1 = 0, $$length2 = each_array_2.length; $$index_1 < $$length2; $$index_1++) {
            let field = each_array_2[$$index_1];
            $$renderer2.push(`<span class="field-tag field-tag-withheld">${escape_html(field)}</span>`);
          }
          $$renderer2.push(`<!--]--></div></div> <div class="entry-detail svelte-ecrwq4"><h5 class="svelte-ecrwq4">Private Context Influence:</h5> <p class="text-sm">${escape_html(entry.private_fields_influenced)} private constraints influenced this recommendation</p></div></div>`);
        }
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<p class="text-muted text-center">No audit entries today</p>`);
      }
      $$renderer2.push(`<!--]--></div> <div class="privacy-summary svelte-ecrwq4"><h4 class="svelte-ecrwq4">Your Private Context</h4> <p class="text-sm text-muted">Only you can see the reasons behind your constraints:</p> <ul class="private-reasons svelte-ecrwq4"><li class="svelte-ecrwq4"><span class="reason-flag svelte-ecrwq4">time_limited</span> <span class="reason-detail svelte-ecrwq4">→ Single parent, childcare 08:00-15:00</span></li> <li class="svelte-ecrwq4"><span class="reason-flag svelte-ecrwq4">health_considerations</span> <span class="reason-detail svelte-ecrwq4">→ Chronic condition, regular appointments</span></li> <li class="svelte-ecrwq4"><span class="reason-flag svelte-ecrwq4">schedule_irregular</span> <span class="reason-detail svelte-ecrwq4">→ School pickup affects availability</span></li></ul></div>`);
    }
    $$renderer2.push(`<!--]--></div> <div${attr_class("comparison-column comparison-column-stakeholder svelte-ecrwq4", void 0, { "active": activeView === "hr" })}><div class="column-header svelte-ecrwq4"><h3><i class="fa-solid fa-building" aria-hidden="true"></i> HR View</h3> <span class="badge badge-warning">Compliance Only</span></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div></section> <section class="card summary-card svelte-ecrwq4"><h3>Today's Summary</h3> <div class="summary-grid svelte-ecrwq4"><div class="summary-stat svelte-ecrwq4"><span class="stat-value svelte-ecrwq4">${escape_html(summary.totalEvents)}</span> <span class="stat-label svelte-ecrwq4">Events</span></div> <div class="summary-stat svelte-ecrwq4"><span class="stat-value svelte-ecrwq4">${escape_html(summary.fieldsSharedCount)}</span> <span class="stat-label svelte-ecrwq4">Fields Shared</span></div> <div class="summary-stat svelte-ecrwq4"><span class="stat-value svelte-ecrwq4">${escape_html(summary.fieldsWithheldCount)}</span> <span class="stat-label svelte-ecrwq4">Fields Withheld</span></div> <div class="summary-stat svelte-ecrwq4"><span class="stat-value stat-highlight svelte-ecrwq4">${escape_html(summary.privateExposedCount)}</span> <span class="stat-label svelte-ecrwq4">Private Exposed</span></div></div></section> <section class="journey-nav svelte-ecrwq4"><a href="/professional" class="btn btn-secondary">← Back to Profile</a> <a href="/" class="btn btn-primary">Try Personal Demo →</a></section></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};
