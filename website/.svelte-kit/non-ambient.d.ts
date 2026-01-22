
// this file is generated — do not edit it


declare module "svelte/elements" {
	export interface HTMLAttributes<T> {
		'data-sveltekit-keepfocus'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-noscroll'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-preload-code'?:
			| true
			| ''
			| 'eager'
			| 'viewport'
			| 'hover'
			| 'tap'
			| 'off'
			| undefined
			| null;
		'data-sveltekit-preload-data'?: true | '' | 'hover' | 'tap' | 'off' | undefined | null;
		'data-sveltekit-reload'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-replacestate'?: true | '' | 'off' | undefined | null;
	}
}

export {};


declare module "$app/types" {
	export interface AppTypes {
		RouteId(): "/" | "/about" | "/adaptation" | "/coordination" | "/demos" | "/demos/learning" | "/demos/learning/adaptive-paths" | "/demos/learning/cognitive-load" | "/demos/multi-agent" | "/demos/multi-agent/auction" | "/demos/multi-agent/negotiation" | "/demos/multi-agent/policy-design" | "/demos/safety" | "/demos/safety/attention-protection" | "/demos/safety/mental-health" | "/demos/self-modeling" | "/demos/self-modeling/belief-calibration" | "/demos/self-modeling/interiora" | "/demos/self-modeling/reality-grounding" | "/docs" | "/docs/api-reference" | "/docs/concepts" | "/docs/csm1-specification" | "/docs/getting-started" | "/personal" | "/personal/community" | "/personal/platforms" | "/personal/platforms/justinguitar" | "/personal/platforms/yousician" | "/personal/skip" | "/playground" | "/professional" | "/professional/audit" | "/professional/morning" | "/psychosecurity" | "/self-modeling" | "/sharing";
		RouteParams(): {
			
		};
		LayoutParams(): {
			"/": Record<string, never>;
			"/about": Record<string, never>;
			"/adaptation": Record<string, never>;
			"/coordination": Record<string, never>;
			"/demos": Record<string, never>;
			"/demos/learning": Record<string, never>;
			"/demos/learning/adaptive-paths": Record<string, never>;
			"/demos/learning/cognitive-load": Record<string, never>;
			"/demos/multi-agent": Record<string, never>;
			"/demos/multi-agent/auction": Record<string, never>;
			"/demos/multi-agent/negotiation": Record<string, never>;
			"/demos/multi-agent/policy-design": Record<string, never>;
			"/demos/safety": Record<string, never>;
			"/demos/safety/attention-protection": Record<string, never>;
			"/demos/safety/mental-health": Record<string, never>;
			"/demos/self-modeling": Record<string, never>;
			"/demos/self-modeling/belief-calibration": Record<string, never>;
			"/demos/self-modeling/interiora": Record<string, never>;
			"/demos/self-modeling/reality-grounding": Record<string, never>;
			"/docs": Record<string, never>;
			"/docs/api-reference": Record<string, never>;
			"/docs/concepts": Record<string, never>;
			"/docs/csm1-specification": Record<string, never>;
			"/docs/getting-started": Record<string, never>;
			"/personal": Record<string, never>;
			"/personal/community": Record<string, never>;
			"/personal/platforms": Record<string, never>;
			"/personal/platforms/justinguitar": Record<string, never>;
			"/personal/platforms/yousician": Record<string, never>;
			"/personal/skip": Record<string, never>;
			"/playground": Record<string, never>;
			"/professional": Record<string, never>;
			"/professional/audit": Record<string, never>;
			"/professional/morning": Record<string, never>;
			"/psychosecurity": Record<string, never>;
			"/self-modeling": Record<string, never>;
			"/sharing": Record<string, never>
		};
		Pathname(): "/" | "/about" | "/about/" | "/adaptation" | "/adaptation/" | "/coordination" | "/coordination/" | "/demos" | "/demos/" | "/demos/learning" | "/demos/learning/" | "/demos/learning/adaptive-paths" | "/demos/learning/adaptive-paths/" | "/demos/learning/cognitive-load" | "/demos/learning/cognitive-load/" | "/demos/multi-agent" | "/demos/multi-agent/" | "/demos/multi-agent/auction" | "/demos/multi-agent/auction/" | "/demos/multi-agent/negotiation" | "/demos/multi-agent/negotiation/" | "/demos/multi-agent/policy-design" | "/demos/multi-agent/policy-design/" | "/demos/safety" | "/demos/safety/" | "/demos/safety/attention-protection" | "/demos/safety/attention-protection/" | "/demos/safety/mental-health" | "/demos/safety/mental-health/" | "/demos/self-modeling" | "/demos/self-modeling/" | "/demos/self-modeling/belief-calibration" | "/demos/self-modeling/belief-calibration/" | "/demos/self-modeling/interiora" | "/demos/self-modeling/interiora/" | "/demos/self-modeling/reality-grounding" | "/demos/self-modeling/reality-grounding/" | "/docs" | "/docs/" | "/docs/api-reference" | "/docs/api-reference/" | "/docs/concepts" | "/docs/concepts/" | "/docs/csm1-specification" | "/docs/csm1-specification/" | "/docs/getting-started" | "/docs/getting-started/" | "/personal" | "/personal/" | "/personal/community" | "/personal/community/" | "/personal/platforms" | "/personal/platforms/" | "/personal/platforms/justinguitar" | "/personal/platforms/justinguitar/" | "/personal/platforms/yousician" | "/personal/platforms/yousician/" | "/personal/skip" | "/personal/skip/" | "/playground" | "/playground/" | "/professional" | "/professional/" | "/professional/audit" | "/professional/audit/" | "/professional/morning" | "/professional/morning/" | "/psychosecurity" | "/psychosecurity/" | "/self-modeling" | "/self-modeling/" | "/sharing" | "/sharing/";
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): "/.nojekyll" | "/CNAME" | "/favicon.svg" | string & {};
	}
}