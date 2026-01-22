import { a2 as head, a3 as escape_html, a4 as store_get, a5 as unsubscribe_stores } from "../../chunks/index2.js";
import { p as page } from "../../chunks/stores.js";
function _error($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    head("1j96wlh", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Page Not Found - VCP Demo</title>`);
      });
    });
    $$renderer2.push(`<div class="error-page container svelte-1j96wlh"><div class="error-content svelte-1j96wlh"><div class="error-code svelte-1j96wlh">${escape_html(store_get($$store_subs ??= {}, "$page", page).status)}</div> <h1 class="svelte-1j96wlh">`);
    if (store_get($$store_subs ??= {}, "$page", page).status === 404) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`Page Not Found`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`Something Went Wrong`);
    }
    $$renderer2.push(`<!--]--></h1> <p class="error-message svelte-1j96wlh">`);
    if (store_get($$store_subs ??= {}, "$page", page).status === 404) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`The page you're looking for doesn't exist or has been moved.`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`${escape_html(store_get($$store_subs ??= {}, "$page", page).error?.message || "An unexpected error occurred.")}`);
    }
    $$renderer2.push(`<!--]--></p> <div class="error-actions svelte-1j96wlh"><a href="/" class="btn btn-primary svelte-1j96wlh"><i class="fa-solid fa-home" aria-hidden="true"></i> Back to Home</a> <a href="/demos" class="btn btn-secondary svelte-1j96wlh"><i class="fa-solid fa-play" aria-hidden="true"></i> View Demos</a></div></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _error as default
};
