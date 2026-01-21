export const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set(["favicon.svg"]),
	mimeTypes: {".svg":"image/svg+xml"},
	_: {
		client: {start:"_app/immutable/entry/start.BVe8oNSi.js",app:"_app/immutable/entry/app.26HB_VDz.js",imports:["_app/immutable/entry/start.BVe8oNSi.js","_app/immutable/chunks/ALvaYeCq.js","_app/immutable/chunks/Dk9CUYtt.js","_app/immutable/chunks/CYrRvoOV.js","_app/immutable/chunks/BKK8S_aC.js","_app/immutable/entry/app.26HB_VDz.js","_app/immutable/chunks/Dk9CUYtt.js","_app/immutable/chunks/CheaE_T0.js","_app/immutable/chunks/SS7UIiiu.js","_app/immutable/chunks/BKK8S_aC.js","_app/immutable/chunks/THaxzejt.js","_app/immutable/chunks/BHzHEumm.js","_app/immutable/chunks/DuyiI72M.js","_app/immutable/chunks/CYrRvoOV.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
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
