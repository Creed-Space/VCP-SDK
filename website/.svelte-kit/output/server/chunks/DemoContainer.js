import { a3 as escape_html, a1 as attr_class } from "./index2.js";
/* empty css                                             */
function DemoContainer($$renderer, $$props) {
  let {
    title,
    description,
    showTokenInspector = true,
    showAuditTrail = false,
    context = null,
    onReset,
    children,
    controls
  } = $$props;
  let tokenInspectorOpen = false;
  let auditTrailOpen = false;
  $$renderer.push(`<div class="demo-container svelte-1pzj3u"><header class="demo-header svelte-1pzj3u"><div class="demo-header-content"><h1 class="svelte-1pzj3u">${escape_html(title)}</h1> <p class="demo-description svelte-1pzj3u">${escape_html(description)}</p></div> <div class="demo-controls svelte-1pzj3u">`);
  if (showTokenInspector && context) {
    $$renderer.push("<!--[-->");
    $$renderer.push(`<button${attr_class("control-btn svelte-1pzj3u", void 0, { "active": tokenInspectorOpen })}><span class="control-icon svelte-1pzj3u"><i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i></span> <span>Token</span></button>`);
  } else {
    $$renderer.push("<!--[!-->");
  }
  $$renderer.push(`<!--]--> `);
  if (showAuditTrail) {
    $$renderer.push("<!--[-->");
    $$renderer.push(`<button${attr_class("control-btn svelte-1pzj3u", void 0, { "active": auditTrailOpen })}><span class="control-icon svelte-1pzj3u"><i class="fa-solid fa-clipboard" aria-hidden="true"></i></span> <span>Audit</span></button>`);
  } else {
    $$renderer.push("<!--[!-->");
  }
  $$renderer.push(`<!--]--> `);
  if (onReset) {
    $$renderer.push("<!--[-->");
    $$renderer.push(`<button class="control-btn control-btn-reset svelte-1pzj3u"><span class="control-icon svelte-1pzj3u">↺</span> <span>Reset</span></button>`);
  } else {
    $$renderer.push("<!--[!-->");
  }
  $$renderer.push(`<!--]--> `);
  if (controls) {
    $$renderer.push("<!--[-->");
    controls($$renderer);
    $$renderer.push(`<!---->`);
  } else {
    $$renderer.push("<!--[!-->");
  }
  $$renderer.push(`<!--]--></div></header> <div${attr_class("demo-layout svelte-1pzj3u", void 0, { "with-sidebar": auditTrailOpen })}><main class="demo-main svelte-1pzj3u">`);
  children($$renderer);
  $$renderer.push(`<!----></main> `);
  {
    $$renderer.push("<!--[!-->");
  }
  $$renderer.push(`<!--]--> `);
  {
    $$renderer.push("<!--[!-->");
  }
  $$renderer.push(`<!--]--></div></div>`);
}
export {
  DemoContainer as D
};
