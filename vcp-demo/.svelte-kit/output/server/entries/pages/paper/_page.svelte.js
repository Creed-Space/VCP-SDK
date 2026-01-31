import { h as head, e as ensure_array_like, b as attr_class, s as stringify } from "../../../chunks/index2.js";
import { $ as escape_html } from "../../../chunks/context.js";
function _page($$renderer) {
  const authors = [
    { name: "Nell Watson", affiliation: "Creed Space" },
    { name: "Elena Ajayi", affiliation: "Creed Space" },
    { name: "Filip Alimpic", affiliation: "Creed Space" },
    { name: "Awwab Mahdi", affiliation: "Creed Space" },
    { name: "Blake Wells", affiliation: "Creed Space" }
  ];
  const layers = [
    {
      id: "I",
      name: "Identity",
      description: "Naming conventions, namespace governance, and privacy-preserving registry for constitutional artifacts",
      icon: "fa-fingerprint"
    },
    {
      id: "T",
      name: "Transport",
      description: "Bundles, cryptographic verification, and audit logging for secure value exchange",
      icon: "fa-truck-fast"
    },
    {
      id: "S",
      name: "Semantics",
      description: "CSM1 formal grammar with 8 personas, 11 scopes, 6 adherence levels, and composition modes",
      icon: "fa-code"
    },
    {
      id: "A",
      name: "Adaptation",
      description: "Context encoding via the 9-dimension Enneagram Protocol with transition detection",
      icon: "fa-sliders"
    }
  ];
  const contributions = [
    "First formal protocol stack for inter-agent value communication",
    "CSM1 grammar enabling precise constitutional specification",
    "Latent State Bridge (LSB) for cross-architecture value exchange",
    "MillOS VCL implementation for human-AI workplace contexts",
    "195 passing tests with ≥90% semantic fidelity in round-trip translations"
  ];
  head("afq2el", $$renderer, ($$renderer2) => {
    $$renderer2.title(($$renderer3) => {
      $$renderer3.push(`<title>VCP Paper | Value Context Protocols</title>`);
    });
    $$renderer2.push(`<meta name="description" content="Value Context Protocols: Standards for Inter-Agent Value Communication - A modular four-layer stack for AI alignment and coordination."/>`);
  });
  $$renderer.push(`<div class="paper-page svelte-afq2el"><section class="hero svelte-afq2el"><div class="container"><div class="badge svelte-afq2el">Research Paper</div> <h1 class="svelte-afq2el">Value Context Protocols</h1> <p class="subtitle svelte-afq2el">Standards for Inter-Agent Value Communication</p> <div class="authors svelte-afq2el"><!--[-->`);
  const each_array = ensure_array_like(authors);
  for (let i = 0, $$length = each_array.length; i < $$length; i++) {
    let author = each_array[i];
    $$renderer.push(`<span class="author svelte-afq2el">${escape_html(author.name)}</span>`);
    if (i < authors.length - 1) {
      $$renderer.push("<!--[-->");
      $$renderer.push(`<span class="separator svelte-afq2el">,</span>`);
    } else {
      $$renderer.push("<!--[!-->");
    }
    $$renderer.push(`<!--]-->`);
  }
  $$renderer.push(`<!--]--></div> <p class="date svelte-afq2el">January 2026</p> <div class="cta-buttons svelte-afq2el"><a href="/Value Context Protocol Paper I1D1.pdf" class="btn btn-primary svelte-afq2el" target="_blank" rel="noopener noreferrer"><i class="fa-solid fa-file-pdf"></i> Download PDF</a></div></div></section> <section class="abstract svelte-afq2el"><div class="container"><h2 class="svelte-afq2el">Abstract</h2> <div class="abstract-content svelte-afq2el"><p class="svelte-afq2el">As AI systems assume increasingly autonomous roles, the absence of a shared representational
					substrate for values risks compounding cultural bias, semantic drift, and coordination failure.
					Current alignment methods optimize for compliance in limited contexts rather than mutual
					interpretability across pluralistic systems.</p> <p class="svelte-afq2el">We introduce <strong class="svelte-afq2el">Value Context Protocols (VCP)</strong>: a modular four-layer stack for
					inter-agent value communication. The protocol enables AI systems to exchange, negotiate, and
					adapt value representations while preserving semantic fidelity across architectural boundaries.</p></div></div></section> <section class="stack svelte-afq2el"><div class="container"><h2 class="svelte-afq2el">The I-T-S-A Stack</h2> <p class="section-intro svelte-afq2el">Four layers working together to enable robust value communication</p> <div class="layers-grid svelte-afq2el"><!--[-->`);
  const each_array_1 = ensure_array_like(layers);
  for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
    let layer = each_array_1[$$index_1];
    $$renderer.push(`<div class="layer-card svelte-afq2el"><div class="layer-header svelte-afq2el"><div class="layer-icon svelte-afq2el"><i${attr_class(`fa-solid ${stringify(layer.icon)}`, "svelte-afq2el")}></i></div> <div class="layer-id svelte-afq2el">VCP/${escape_html(layer.id)}</div></div> <h3 class="svelte-afq2el">${escape_html(layer.name)}</h3> <p class="svelte-afq2el">${escape_html(layer.description)}</p></div>`);
  }
  $$renderer.push(`<!--]--></div></div></section> <section class="contributions svelte-afq2el"><div class="container"><h2 class="svelte-afq2el">Key Contributions</h2> <ul class="contribution-list svelte-afq2el"><!--[-->`);
  const each_array_2 = ensure_array_like(contributions);
  for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
    let contribution = each_array_2[$$index_2];
    $$renderer.push(`<li class="svelte-afq2el"><i class="fa-solid fa-check svelte-afq2el"></i> <span>${escape_html(contribution)}</span></li>`);
  }
  $$renderer.push(`<!--]--></ul></div></section> <section class="implementations svelte-afq2el"><div class="container"><h2 class="svelte-afq2el">Reference Implementations</h2> <div class="impl-grid svelte-afq2el"><div class="impl-card svelte-afq2el"><div class="impl-icon svelte-afq2el"><i class="fa-solid fa-bridge"></i></div> <h3 class="svelte-afq2el">Latent State Bridge (LSB)</h3> <p class="svelte-afq2el">Cross-architecture value exchange between AI systems with different internal representations</p></div> <div class="impl-card svelte-afq2el"><div class="impl-icon svelte-afq2el"><i class="fa-solid fa-building"></i></div> <h3 class="svelte-afq2el">MillOS VCL</h3> <p class="svelte-afq2el">Human-AI workplace contexts with constitutional governance and preference learning</p></div></div></div></section> <section class="final-cta svelte-afq2el"><div class="container svelte-afq2el"><h2 class="svelte-afq2el">Read the Full Paper</h2> <p class="svelte-afq2el">Dive into the technical specification and implementation details</p> <div class="cta-buttons svelte-afq2el"><a href="/Value Context Protocol Paper I1D1.pdf" class="btn btn-primary btn-lg svelte-afq2el" target="_blank" rel="noopener noreferrer"><i class="fa-solid fa-file-pdf"></i> Download PDF</a> <a href="/playground" class="btn btn-secondary btn-lg svelte-afq2el"><i class="fa-solid fa-play"></i> Try the Playground</a></div></div></section></div>`);
}
export {
  _page as default
};
