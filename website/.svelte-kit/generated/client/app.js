export { matchers } from './matchers.js';

export const nodes = [
	() => import('./nodes/0'),
	() => import('./nodes/1'),
	() => import('./nodes/2'),
	() => import('./nodes/3'),
	() => import('./nodes/4'),
	() => import('./nodes/5'),
	() => import('./nodes/6'),
	() => import('./nodes/7'),
	() => import('./nodes/8'),
	() => import('./nodes/9'),
	() => import('./nodes/10'),
	() => import('./nodes/11'),
	() => import('./nodes/12'),
	() => import('./nodes/13'),
	() => import('./nodes/14'),
	() => import('./nodes/15'),
	() => import('./nodes/16'),
	() => import('./nodes/17'),
	() => import('./nodes/18'),
	() => import('./nodes/19'),
	() => import('./nodes/20'),
	() => import('./nodes/21'),
	() => import('./nodes/22'),
	() => import('./nodes/23'),
	() => import('./nodes/24'),
	() => import('./nodes/25'),
	() => import('./nodes/26'),
	() => import('./nodes/27'),
	() => import('./nodes/28'),
	() => import('./nodes/29'),
	() => import('./nodes/30'),
	() => import('./nodes/31'),
	() => import('./nodes/32'),
	() => import('./nodes/33')
];

export const server_loads = [];

export const dictionary = {
		"/": [2],
		"/about": [3],
		"/adaptation": [4],
		"/coordination": [5],
		"/demos": [6],
		"/demos/learning/adaptive-paths": [7],
		"/demos/learning/cognitive-load": [8],
		"/demos/multi-agent/auction": [9],
		"/demos/multi-agent/negotiation": [10],
		"/demos/multi-agent/policy-design": [11],
		"/demos/safety/attention-protection": [12],
		"/demos/safety/mental-health": [13],
		"/demos/self-modeling/belief-calibration": [14],
		"/demos/self-modeling/interiora": [15],
		"/demos/self-modeling/reality-grounding": [16],
		"/docs": [17],
		"/docs/api-reference": [18],
		"/docs/concepts": [19],
		"/docs/csm1-specification": [20],
		"/docs/getting-started": [21],
		"/personal": [22],
		"/personal/community": [23],
		"/personal/platforms/justinguitar": [24],
		"/personal/platforms/yousician": [25],
		"/personal/skip": [26],
		"/playground": [27],
		"/professional": [28],
		"/professional/audit": [29],
		"/professional/morning": [30],
		"/psychosecurity": [31],
		"/self-modeling": [32],
		"/sharing": [33]
	};

export const hooks = {
	handleError: (({ error }) => { console.error(error) }),
	
	reroute: (() => {}),
	transport: {}
};

export const decoders = Object.fromEntries(Object.entries(hooks.transport).map(([k, v]) => [k, v.decode]));
export const encoders = Object.fromEntries(Object.entries(hooks.transport).map(([k, v]) => [k, v.encode]));

export const hash = false;

export const decode = (type, value) => decoders[type](value);

export { default as root } from '../root.js';