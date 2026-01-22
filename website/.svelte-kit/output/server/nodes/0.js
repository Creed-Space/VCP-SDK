import * as universal from '../entries/pages/_layout.ts.js';

export const index = 0;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/_layout.svelte.js')).default;
export { universal };
export const universal_id = "src/routes/+layout.ts";
export const imports = ["_app/immutable/nodes/0.J0kyLxQC.js","_app/immutable/chunks/DLAMQWiX.js","_app/immutable/chunks/CA-YEXjj.js","_app/immutable/chunks/CcFbpJ_b.js","_app/immutable/chunks/CevX9nUO.js","_app/immutable/chunks/Cjh8sQO3.js","_app/immutable/chunks/BSTOKesL.js","_app/immutable/chunks/C5dXRjDF.js","_app/immutable/chunks/BRzKQYUk.js"];
export const stylesheets = ["_app/immutable/assets/0.Bp4ND8dq.css"];
export const fonts = [];
