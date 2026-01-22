import { a1 as attr_class, a3 as escape_html, a8 as ensure_array_like, a7 as stringify, a0 as attr } from "./index2.js";
function PresetLoader($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let {
      presets,
      selected,
      title = "Presets",
      showDescriptions = true,
      layout = "cards",
      onselect
    } = $$props;
    $$renderer2.push(`<div${attr_class(`preset-loader layout-${stringify(layout)}`, "svelte-1s04knq")}>`);
    if (title) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="loader-header svelte-1s04knq"><h4 class="svelte-1s04knq"><i class="fa-solid fa-bookmark" aria-hidden="true"></i> ${escape_html(title)}</h4></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    if (layout === "cards") {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="preset-cards svelte-1s04knq"><!--[-->`);
      const each_array = ensure_array_like(presets);
      for (let $$index_1 = 0, $$length = each_array.length; $$index_1 < $$length; $$index_1++) {
        let preset = each_array[$$index_1];
        $$renderer2.push(`<button${attr_class("preset-card svelte-1s04knq", void 0, { "selected": selected === preset.id })}>`);
        if (preset.icon) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<span class="preset-icon svelte-1s04knq"><i${attr_class(`fa-solid ${stringify(preset.icon)}`, "svelte-1s04knq")} aria-hidden="true"></i></span>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--> <div class="preset-content svelte-1s04knq"><span class="preset-name svelte-1s04knq">${escape_html(preset.name)}</span> `);
        if (showDescriptions && preset.description) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<span class="preset-description svelte-1s04knq">${escape_html(preset.description)}</span>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--></div> `);
        if (preset.tags && preset.tags.length > 0) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="preset-tags svelte-1s04knq"><!--[-->`);
          const each_array_1 = ensure_array_like(preset.tags);
          for (let $$index = 0, $$length2 = each_array_1.length; $$index < $$length2; $$index++) {
            let tag = each_array_1[$$index];
            $$renderer2.push(`<span class="preset-tag svelte-1s04knq">${escape_html(tag)}</span>`);
          }
          $$renderer2.push(`<!--]--></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--></button>`);
      }
      $$renderer2.push(`<!--]--></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      if (layout === "list") {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="preset-list svelte-1s04knq"><!--[-->`);
        const each_array_2 = ensure_array_like(presets);
        for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
          let preset = each_array_2[$$index_2];
          $$renderer2.push(`<button${attr_class("preset-item svelte-1s04knq", void 0, { "selected": selected === preset.id })}>`);
          if (preset.icon) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<span class="preset-icon svelte-1s04knq"><i${attr_class(`fa-solid ${stringify(preset.icon)}`, "svelte-1s04knq")} aria-hidden="true"></i></span>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--> <span class="preset-name svelte-1s04knq">${escape_html(preset.name)}</span> `);
          if (showDescriptions && preset.description) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<span class="preset-description svelte-1s04knq">${escape_html(preset.description)}</span>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--> `);
          if (selected === preset.id) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<span class="selected-check svelte-1s04knq"><i class="fa-solid fa-check" aria-hidden="true"></i></span>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--></button>`);
        }
        $$renderer2.push(`<!--]--></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="preset-chips svelte-1s04knq"><!--[-->`);
        const each_array_3 = ensure_array_like(presets);
        for (let $$index_3 = 0, $$length = each_array_3.length; $$index_3 < $$length; $$index_3++) {
          let preset = each_array_3[$$index_3];
          $$renderer2.push(`<button${attr_class("preset-chip svelte-1s04knq", void 0, { "selected": selected === preset.id })}${attr("title", preset.description)}>`);
          if (preset.icon) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<i${attr_class(`fa-solid ${stringify(preset.icon)}`, "svelte-1s04knq")} aria-hidden="true"></i>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--> ${escape_html(preset.name)}</button>`);
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  PresetLoader as P
};
