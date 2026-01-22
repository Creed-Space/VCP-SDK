import { a1 as attr_class, a3 as escape_html, a8 as ensure_array_like, a7 as stringify } from "./index2.js";
/* empty css                                         */
function AuditPanel($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let {
      entries,
      title = "Audit Trail",
      showTimestamps = false,
      groupByCategory = true,
      compact = false
    } = $$props;
    const groupedEntries = (() => {
      if (!groupByCategory) return { all: entries };
      return {
        shared: entries.filter((e) => e.category === "shared"),
        influenced: entries.filter((e) => e.category === "influenced"),
        withheld: entries.filter((e) => e.category === "withheld")
      };
    })();
    const categories = [
      {
        key: "shared",
        label: "Shared",
        icon: "fa-circle-check",
        color: "success"
      },
      {
        key: "influenced",
        label: "Influenced",
        icon: "fa-bolt",
        color: "warning"
      },
      {
        key: "withheld",
        label: "Withheld",
        icon: "fa-lock",
        color: "danger"
      }
    ];
    function formatValue(value) {
      if (value === void 0) return "—";
      if (typeof value === "boolean") return value ? "Yes" : "No";
      return String(value);
    }
    $$renderer2.push(`<div${attr_class("audit-panel svelte-eqyfat", void 0, { "compact": compact })}>`);
    if (title) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="audit-header svelte-eqyfat"><h3 class="svelte-eqyfat"><i class="fa-solid fa-clipboard-list" aria-hidden="true"></i> ${escape_html(title)}</h3> <div class="audit-summary svelte-eqyfat"><span class="summary-item success svelte-eqyfat">${escape_html(groupedEntries.shared?.length ?? 0)} shared</span> <span class="summary-item warning svelte-eqyfat">${escape_html(groupedEntries.influenced?.length ?? 0)} influenced</span> <span class="summary-item danger svelte-eqyfat">${escape_html(groupedEntries.withheld?.length ?? 0)} withheld</span></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    if (groupByCategory) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="audit-categories svelte-eqyfat"><!--[-->`);
      const each_array = ensure_array_like(categories);
      for (let $$index_1 = 0, $$length = each_array.length; $$index_1 < $$length; $$index_1++) {
        let cat = each_array[$$index_1];
        const catEntries = groupedEntries[cat.key] ?? [];
        if (catEntries.length > 0) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div${attr_class(`audit-category category-${stringify(cat.color)}`, "svelte-eqyfat")}><div class="category-header svelte-eqyfat"><span class="category-icon svelte-eqyfat"><i${attr_class(`fa-solid ${stringify(cat.icon)}`, "svelte-eqyfat")} aria-hidden="true"></i></span> <span class="category-label svelte-eqyfat">${escape_html(cat.label)}</span> <span class="category-count svelte-eqyfat">${escape_html(catEntries.length)}</span></div> <div class="category-entries svelte-eqyfat"><!--[-->`);
          const each_array_1 = ensure_array_like(catEntries);
          for (let $$index = 0, $$length2 = each_array_1.length; $$index < $$length2; $$index++) {
            let entry = each_array_1[$$index];
            $$renderer2.push(`<div class="audit-entry svelte-eqyfat"><div class="entry-field svelte-eqyfat">${escape_html(entry.field)}</div> `);
            if (entry.value !== void 0) {
              $$renderer2.push("<!--[-->");
              $$renderer2.push(`<div class="entry-value svelte-eqyfat">${escape_html(formatValue(entry.value))}</div>`);
            } else {
              $$renderer2.push("<!--[!-->");
            }
            $$renderer2.push(`<!--]--> `);
            if (entry.reason) {
              $$renderer2.push("<!--[-->");
              $$renderer2.push(`<div class="entry-reason svelte-eqyfat">${escape_html(entry.reason)}</div>`);
            } else {
              $$renderer2.push("<!--[!-->");
            }
            $$renderer2.push(`<!--]--> `);
            if (entry.stakeholder) {
              $$renderer2.push("<!--[-->");
              $$renderer2.push(`<div class="entry-stakeholder svelte-eqyfat"><i class="fa-solid fa-user" aria-hidden="true"></i> ${escape_html(entry.stakeholder)}</div>`);
            } else {
              $$renderer2.push("<!--[!-->");
            }
            $$renderer2.push(`<!--]--> `);
            if (showTimestamps && entry.timestamp) {
              $$renderer2.push("<!--[-->");
              $$renderer2.push(`<div class="entry-timestamp svelte-eqyfat">${escape_html(entry.timestamp)}</div>`);
            } else {
              $$renderer2.push("<!--[!-->");
            }
            $$renderer2.push(`<!--]--></div>`);
          }
          $$renderer2.push(`<!--]--></div></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]--></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div class="audit-list svelte-eqyfat"><!--[-->`);
      const each_array_2 = ensure_array_like(entries);
      for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
        let entry = each_array_2[$$index_2];
        $$renderer2.push(`<div${attr_class(`audit-entry audit-entry-${stringify(entry.category)}`, "svelte-eqyfat")}><span class="entry-indicator svelte-eqyfat"></span> <div class="entry-content svelte-eqyfat"><div class="entry-field svelte-eqyfat">${escape_html(entry.field)}</div> `);
        if (entry.value !== void 0) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="entry-value svelte-eqyfat">${escape_html(formatValue(entry.value))}</div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--> `);
        if (entry.reason) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="entry-reason svelte-eqyfat">${escape_html(entry.reason)}</div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--></div> `);
        if (showTimestamps && entry.timestamp) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="entry-timestamp svelte-eqyfat">${escape_html(entry.timestamp)}</div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]--></div>`);
    }
    $$renderer2.push(`<!--]--> <div class="audit-footer svelte-eqyfat"><span class="footer-note svelte-eqyfat"><i class="fa-solid fa-shield-halved" aria-hidden="true"></i> Private context influenced behavior without being exposed</span></div></div>`);
  });
}
export {
  AuditPanel as A
};
