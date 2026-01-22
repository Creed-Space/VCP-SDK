import { a4 as store_get, a2 as head, a1 as attr_class, a0 as attr, a3 as escape_html, a5 as unsubscribe_stores } from "../../../../../chunks/index2.js";
import { v as vcpContext } from "../../../../../chunks/context.js";
/* empty css                                                                 */
/* empty css                                                             */
/* empty css                                                             */
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let showAuditPanel = true;
    store_get($$store_subs ??= {}, "$vcpContext", vcpContext);
    head("10vrk7k", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>JustinGuitar - VCP Demo</title>`);
      });
    });
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div${attr_class("page-layout svelte-10vrk7k", void 0, { "audit-open": showAuditPanel })}><div class="main-content svelte-10vrk7k"><div class="platform-frame platform-frame-justinguitar"><div class="platform-header platform-header-justinguitar"><div class="platform-brand svelte-10vrk7k"><span class="platform-logo svelte-10vrk7k"><i class="fa-solid fa-guitar" aria-hidden="true"></i></span> <span class="platform-name svelte-10vrk7k">JustinGuitar</span></div> <div class="header-actions svelte-10vrk7k">`);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <button class="audit-toggle-btn svelte-10vrk7k"${attr("aria-label", "Hide audit panel")}><i class="fa-solid fa-clipboard-list" aria-hidden="true"></i> ${escape_html("Hide")} Audit</button></div></div> <div class="platform-content">`);
    {
      $$renderer2.push("<!--[!-->");
      {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="no-vcp svelte-10vrk7k"><h2>VCP Not Connected</h2> <p class="text-muted">Connect your VCP profile for a personalized experience.</p> <button class="btn btn-primary">Connect VCP</button></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div></div> <div class="container-narrow" style="margin-top: 2rem;"><div class="nav-links svelte-10vrk7k"><a href="/personal" class="btn btn-ghost">← Back to Profile</a> <a href="/personal/platforms/yousician" class="btn btn-primary">Try Yousician →</a></div></div></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};
