import { a4 as store_get, a0 as attr, a1 as attr_class, a8 as ensure_array_like, a3 as escape_html, a5 as unsubscribe_stores } from "./index2.js";
import { p as page } from "./stores.js";
function DocsLayout($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let { title, description, children } = $$props;
    const navSections = [
      {
        title: "Getting Started",
        items: [
          {
            href: "/docs/getting-started",
            label: "Quick Start",
            time: "5 min"
          },
          {
            href: "/docs/concepts",
            label: "Core Concepts",
            time: "10 min"
          }
        ]
      },
      {
        title: "Specifications",
        items: [
          {
            href: "/docs/csm1-specification",
            label: "CSM-1 Format",
            time: "15 min"
          },
          {
            href: "/docs/api-reference",
            label: "API Reference",
            time: "Ref"
          }
        ]
      },
      {
        title: "Advanced",
        items: [
          {
            href: "/docs/constitutional-ai",
            label: "Constitutional AI",
            time: "12 min"
          },
          {
            href: "/docs/privacy-architecture",
            label: "Privacy Architecture",
            time: "8 min"
          },
          {
            href: "/docs/interiora",
            label: "Interiora Spec",
            time: "20 min"
          },
          {
            href: "/docs/multi-agent",
            label: "Multi-Agent Patterns",
            time: "15 min"
          }
        ]
      }
    ];
    let currentPath = store_get($$store_subs ??= {}, "$page", page).url.pathname;
    let sidebarOpen = false;
    $$renderer2.push(`<div class="docs-layout svelte-fxrvrl"><button class="sidebar-toggle svelte-fxrvrl"${attr("aria-expanded", sidebarOpen)} aria-controls="docs-sidebar"><span class="toggle-icon svelte-fxrvrl">`);
    {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<i class="fa-solid fa-bars" aria-hidden="true"></i>`);
    }
    $$renderer2.push(`<!--]--></span> <span class="toggle-text">Menu</span></button> <aside id="docs-sidebar"${attr_class("sidebar svelte-fxrvrl", void 0, { "open": sidebarOpen })}><nav class="sidebar-nav" aria-label="Documentation navigation"><a href="/docs"${attr_class("sidebar-home svelte-fxrvrl", void 0, { "active": currentPath === "/docs" })}><span class="home-icon svelte-fxrvrl"><i class="fa-solid fa-book" aria-hidden="true"></i></span> Documentation Home</a> <!--[-->`);
    const each_array = ensure_array_like(navSections);
    for (let $$index_1 = 0, $$length = each_array.length; $$index_1 < $$length; $$index_1++) {
      let section = each_array[$$index_1];
      $$renderer2.push(`<div class="nav-section svelte-fxrvrl"><h3 class="nav-section-title svelte-fxrvrl">${escape_html(section.title)}</h3> <ul class="nav-list svelte-fxrvrl"><!--[-->`);
      const each_array_1 = ensure_array_like(section.items);
      for (let $$index = 0, $$length2 = each_array_1.length; $$index < $$length2; $$index++) {
        let item = each_array_1[$$index];
        $$renderer2.push(`<li><a${attr("href", item.href)}${attr_class("nav-link svelte-fxrvrl", void 0, { "active": currentPath === item.href })}><span class="nav-link-label">${escape_html(item.label)}</span> <span class="nav-link-time svelte-fxrvrl">${escape_html(item.time)}</span></a></li>`);
      }
      $$renderer2.push(`<!--]--></ul></div>`);
    }
    $$renderer2.push(`<!--]--></nav></aside> <main class="docs-content svelte-fxrvrl"><header class="docs-header svelte-fxrvrl"><nav class="breadcrumbs svelte-fxrvrl" aria-label="Breadcrumb"><a href="/docs" class="svelte-fxrvrl">Docs</a> <span class="breadcrumb-sep svelte-fxrvrl" aria-hidden="true">/</span> <span class="breadcrumb-current svelte-fxrvrl">${escape_html(title)}</span></nav> <h1 class="svelte-fxrvrl">${escape_html(title)}</h1> `);
    if (description) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p class="docs-description svelte-fxrvrl">${escape_html(description)}</p>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></header> <article class="docs-article svelte-fxrvrl">`);
    children($$renderer2);
    $$renderer2.push(`<!----></article> <footer class="docs-footer svelte-fxrvrl"><div class="footer-nav svelte-fxrvrl"><a href="/docs" class="footer-link svelte-fxrvrl"><span class="footer-link-direction svelte-fxrvrl">←</span> <span>Back to Docs</span></a> <a href="/playground" class="footer-link svelte-fxrvrl"><span>Try the Playground</span> <span class="footer-link-direction svelte-fxrvrl">→</span></a></div></footer></main></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]-->`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  DocsLayout as D
};
