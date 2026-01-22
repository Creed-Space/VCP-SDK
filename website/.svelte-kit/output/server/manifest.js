export const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set([".nojekyll","CNAME","favicon.svg"]),
	mimeTypes: {".svg":"image/svg+xml"},
	_: {
		client: {start:"_app/immutable/entry/start.Y-BHlpDX.js",app:"_app/immutable/entry/app.B1mUfMQt.js",imports:["_app/immutable/entry/start.Y-BHlpDX.js","_app/immutable/chunks/DDCcBiF0.js","_app/immutable/chunks/CA-YEXjj.js","_app/immutable/chunks/Bz1WZ207.js","_app/immutable/chunks/DahdQlr5.js","_app/immutable/entry/app.B1mUfMQt.js","_app/immutable/chunks/CA-YEXjj.js","_app/immutable/chunks/CcFbpJ_b.js","_app/immutable/chunks/DLAMQWiX.js","_app/immutable/chunks/DahdQlr5.js","_app/immutable/chunks/Cjh8sQO3.js","_app/immutable/chunks/C_FJgLy-.js","_app/immutable/chunks/D8G-iT40.js","_app/immutable/chunks/Bz1WZ207.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./nodes/0.js')),
			__memo(() => import('./nodes/1.js'))
		],
		remotes: {
			
		},
		routes: [
			
		],
		prerendered_routes: new Set(["/","/about/","/adaptation/","/coordination/","/demos/","/demos/learning/adaptive-paths/","/demos/learning/cognitive-load/","/demos/multi-agent/auction/","/demos/multi-agent/negotiation/","/demos/multi-agent/policy-design/","/demos/safety/attention-protection/","/demos/safety/mental-health/","/demos/self-modeling/belief-calibration/","/demos/self-modeling/interiora/","/demos/self-modeling/reality-grounding/","/docs/","/docs/api-reference/","/docs/concepts/","/docs/csm1-specification/","/docs/getting-started/","/personal/","/personal/community/","/personal/platforms/justinguitar/","/personal/platforms/yousician/","/personal/skip/","/playground/","/professional/","/professional/audit/","/professional/morning/","/psychosecurity/","/self-modeling/","/sharing/"]),
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();
