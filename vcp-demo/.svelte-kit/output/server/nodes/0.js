import * as universal from '../entries/pages/_layout.ts.js';

export const index = 0;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/_layout.svelte.js')).default;
export { universal };
export const universal_id = "src/routes/+layout.ts";
export const imports = ["_app/immutable/nodes/0.CI2HkVh-.js","_app/immutable/chunks/SS7UIiiu.js","_app/immutable/chunks/Dk9CUYtt.js","_app/immutable/chunks/CheaE_T0.js","_app/immutable/chunks/DNOi2MYz.js","_app/immutable/chunks/THaxzejt.js","_app/immutable/chunks/CYZTMHMP.js","_app/immutable/chunks/CxNXv9Qd.js","_app/immutable/chunks/DLdlFW72.js"];
export const stylesheets = ["_app/immutable/assets/0.CPpqgH5z.css"];
export const fonts = [];
