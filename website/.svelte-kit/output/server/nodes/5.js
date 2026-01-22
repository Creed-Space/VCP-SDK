

export const index = 5;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/coordination/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/5.V7l2ADnp.js","_app/immutable/chunks/DLAMQWiX.js","_app/immutable/chunks/CA-YEXjj.js","_app/immutable/chunks/sU9ev7NS.js","_app/immutable/chunks/B8NQnvAs.js"];
export const stylesheets = ["_app/immutable/assets/5.5VhdiClQ.css"];
export const fonts = [];
