import { a as attr, b as attr_class } from "../../chunks/index2.js";
function _layout($$renderer, $$props) {
  let { children } = $$props;
  let mobileMenuOpen = false;
  $$renderer.push(`<div class="app svelte-12qhfyh"><a href="#main-content" class="skip-link">Skip to main content</a> <header class="app-header svelte-12qhfyh"><nav class="container flex items-center justify-between"><a href="/" class="logo svelte-12qhfyh" aria-label="VCP Demo Home"><span class="logo-icon svelte-12qhfyh" aria-hidden="true"><i class="fa-solid fa-shield-halved"></i></span> <span class="logo-text svelte-12qhfyh">VCP</span> <span class="logo-badge svelte-12qhfyh">Demo</span></a> <div class="nav-links desktop-nav svelte-12qhfyh" role="navigation" aria-label="Main navigation"><a href="/about" class="nav-link svelte-12qhfyh">About</a> <a href="/demos" class="nav-link svelte-12qhfyh">Demos</a> <a href="/docs" class="nav-link svelte-12qhfyh">Docs</a> <a href="/playground" class="nav-link svelte-12qhfyh">Playground</a> <span class="nav-divider svelte-12qhfyh" aria-hidden="true"></span> <a href="https://creed.space" target="_blank" rel="noopener noreferrer" class="nav-link nav-link-brand svelte-12qhfyh" aria-label="Learn more about Creed Space (opens in new tab)"><span class="brand-icon svelte-12qhfyh" aria-hidden="true">◈</span> Creed Space</a></div> <button class="mobile-menu-btn svelte-12qhfyh"${attr("aria-expanded", mobileMenuOpen)} aria-controls="mobile-nav"${attr("aria-label", "Open menu")}><span${attr_class("hamburger svelte-12qhfyh", void 0, { "open": mobileMenuOpen })}><span class="svelte-12qhfyh"></span> <span class="svelte-12qhfyh"></span> <span class="svelte-12qhfyh"></span></span></button></nav> `);
  {
    $$renderer.push("<!--[!-->");
  }
  $$renderer.push(`<!--]--></header> <main id="main-content" tabindex="-1" class="svelte-12qhfyh">`);
  {
    $$renderer.push("<!--[!-->");
    children($$renderer);
    $$renderer.push(`<!---->`);
  }
  $$renderer.push(`<!--]--></main> <footer class="app-footer svelte-12qhfyh"><div class="container"><div class="footer-content svelte-12qhfyh"><div class="footer-brand svelte-12qhfyh"><span class="footer-logo svelte-12qhfyh" aria-hidden="true"><i class="fa-solid fa-shield-halved"></i></span> <div><p class="footer-title svelte-12qhfyh">Value Context Protocol</p> <p class="footer-tagline svelte-12qhfyh">Your context stays yours. Private reasons stay private.</p></div></div> <div class="footer-links svelte-12qhfyh"><div class="footer-section svelte-12qhfyh"><h4 class="svelte-12qhfyh">Demos</h4> <a href="/sharing" class="svelte-12qhfyh">Sharing</a> <a href="/coordination" class="svelte-12qhfyh">Coordination</a> <a href="/self-modeling" class="svelte-12qhfyh">Self-Modeling</a> <a href="/adaptation" class="svelte-12qhfyh">Adaptation</a> <a href="/psychosecurity" class="svelte-12qhfyh">Psychosecurity</a></div> <div class="footer-section svelte-12qhfyh"><h4 class="svelte-12qhfyh">Learn More</h4> <a href="https://creed.space" target="_blank" rel="noopener noreferrer" class="svelte-12qhfyh">Creed Space</a> <a href="https://github.com/creed-space" target="_blank" rel="noopener noreferrer" class="svelte-12qhfyh">GitHub</a></div></div></div> <div class="footer-bottom svelte-12qhfyh"><p>Built with <span aria-label="love">♡</span> by <a href="https://creed.space" target="_blank" rel="noopener noreferrer" class="svelte-12qhfyh">Creed Space</a></p> <p class="footer-version svelte-12qhfyh">VCP Demo v0.1</p></div></div></footer></div>`);
}
export {
  _layout as default
};
