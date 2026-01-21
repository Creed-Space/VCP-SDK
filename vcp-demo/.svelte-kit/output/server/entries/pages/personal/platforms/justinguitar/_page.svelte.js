import { d as store_get, h as head, u as unsubscribe_stores } from "../../../../../chunks/index2.js";
import { v as vcpContext } from "../../../../../chunks/context2.js";
/* empty css                                                                 */
/* empty css                                                             */
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    store_get($$store_subs ??= {}, "$vcpContext", vcpContext);
    head("10vrk7k", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>JustinGuitar - VCP Demo</title>`);
      });
    });
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="platform-frame platform-frame-justinguitar"><div class="platform-header platform-header-justinguitar"><div class="platform-brand svelte-10vrk7k"><span class="platform-logo svelte-10vrk7k">🎸</span> <span class="platform-name svelte-10vrk7k">JustinGuitar</span></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> <div class="platform-content">`);
    {
      $$renderer2.push("<!--[!-->");
      {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="no-vcp svelte-10vrk7k"><h2>VCP Not Connected</h2> <p class="text-muted">Connect your VCP profile for a personalized experience.</p> <button class="btn btn-primary">Connect VCP</button></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div></div> <div class="container-narrow" style="margin-top: 2rem;"><div class="nav-links svelte-10vrk7k"><a href="/personal" class="btn btn-ghost">← Back to Profile</a> <a href="/personal/platforms/yousician" class="btn btn-primary">Try Yousician →</a></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};
