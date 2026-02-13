/**
 * @vcp/webmcp — Tool Factory
 *
 * Creates VCP tool definitions from a config object.
 * Framework-agnostic — no SvelteKit or framework-specific imports.
 */

import type {
	VCPWebMCPConfig,
	PersonaInfo,
	WebMCPToolDefinition,
	WebMCPToolResult
} from './types.js';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function textResult(text: string): WebMCPToolResult {
	return { content: [{ type: 'text', text }] };
}

function errorResult(message: string): WebMCPToolResult {
	return textResult(`Error: ${message}`);
}

function isRecord(v: unknown): v is Record<string, unknown> {
	return typeof v === 'object' && v !== null && !Array.isArray(v);
}

/** Consume an SSE stream and return the complete text. */
async function consumeSSEStream(response: Response): Promise<string> {
	const body = response.body;
	if (!body) throw new Error('No response body');

	const reader = body.getReader();
	const decoder = new TextDecoder();
	let text = '';

	for (;;) {
		const { done, value } = await reader.read();
		if (done) break;

		const chunk = decoder.decode(value, { stream: true });
		for (const line of chunk.split('\n')) {
			if (!line.startsWith('data: ')) continue;
			const data = line.slice(6);
			if (data === '[DONE]') continue;
			try {
				const parsed = JSON.parse(data) as { delta?: { text?: string }; error?: string };
				if (parsed.error) throw new Error(parsed.error);
				text += parsed.delta?.text ?? '';
			} catch {
				// non-JSON SSE line — skip
			}
		}
	}

	return text;
}

// ---------------------------------------------------------------------------
// Default personas
// ---------------------------------------------------------------------------

const DEFAULT_PERSONAS: PersonaInfo[] = [
	{
		id: 'muse',
		name: 'Muse',
		description: 'Creative and inspiring. Adapts to energy and constraints.',
		use: 'Learning, exploration, creative work'
	},
	{
		id: 'ambassador',
		name: 'Ambassador',
		description: 'Diplomatic and professional. Balanced communication.',
		use: 'General purpose, formal contexts'
	},
	{
		id: 'godparent',
		name: 'Godparent',
		description: 'Protective and nurturing. Prioritizes wellbeing.',
		use: 'Health, children, vulnerable contexts'
	},
	{
		id: 'sentinel',
		name: 'Sentinel',
		description: 'Watchful and risk-aware. Flags concerns proactively.',
		use: 'Security, privacy, boundary enforcement'
	},
	{
		id: 'anchor',
		name: 'Anchor',
		description: 'Grounding and present-focused. Reduces overwhelm.',
		use: 'Stress, overwhelm, stability needs'
	},
	{
		id: 'nanny',
		name: 'Nanny',
		description: 'Gentle and patient. Handles immediate practical needs.',
		use: 'Daily routines, immediate care, patience-heavy tasks'
	},
	{
		id: 'steward',
		name: 'Steward',
		description: 'Responsible and sustainable. Balances obligation with capacity.',
		use: 'Decisions, obligations, long-term planning'
	}
];

// ---------------------------------------------------------------------------
// Tool factories
// ---------------------------------------------------------------------------

function wrapExecute(
	name: string,
	fn: (args: Record<string, unknown>) => Promise<WebMCPToolResult>,
	onToolCall?: (toolName: string) => void
): (args: Record<string, unknown>) => Promise<WebMCPToolResult> {
	return async (args) => {
		onToolCall?.(name);
		if (typeof window !== 'undefined') {
			window.dispatchEvent(
				new CustomEvent('webmcp:tool-call', {
					detail: { tool: name, timestamp: Date.now() }
				})
			);
		}
		return fn(args);
	};
}

function createChatTool(config: VCPWebMCPConfig): WebMCPToolDefinition {
	const endpoint = config.chatEndpoint ?? '/api/chat';
	const personas = config.personas ?? DEFAULT_PERSONAS;
	const personaIds = personas.map((p) => p.id);

	return {
		name: 'vcp_chat',
		description:
			'Send a message to a VCP-aware AI assistant. Optionally include VCP context (personal state, constraints, preferences) to get a context-adapted response.',
		inputSchema: {
			type: 'object',
			properties: {
				query: { type: 'string', description: 'The user message to send' },
				vcp_context: {
					type: 'object',
					description:
						'Optional VCP context object with personal_state, constraints, public_profile, etc.'
				},
				constitution_id: {
					type: 'string',
					description:
						"Constitution ID (e.g. 'personal.growth.creative'). Defaults to 'general'."
				},
				persona: {
					type: 'string',
					enum: personaIds,
					description: 'AI persona to use. Defaults to steward.'
				}
			},
			required: ['query']
		},
		annotations: { readOnlyHint: false },
		execute: wrapExecute(
			'vcp_chat',
			async (args) => {
				const query = typeof args.query === 'string' ? args.query.trim() : '';
				if (!query) return errorResult('query is required and must be a non-empty string');
				if (query.length > 4000) return errorResult('query exceeds 4000 character limit');

				const body = {
					query,
					vcp_context: isRecord(args.vcp_context) ? args.vcp_context : undefined,
					constitution_id:
						typeof args.constitution_id === 'string' ? args.constitution_id : 'general',
					persona: typeof args.persona === 'string' ? args.persona : undefined
				};

				try {
					const response = await fetch(endpoint, {
						method: 'POST',
						headers: { 'Content-Type': 'application/json' },
						body: JSON.stringify(body)
					});

					const contentType = response.headers.get('content-type') ?? '';
					if (contentType.includes('application/json')) {
						const json = (await response.json()) as {
							fallback?: boolean;
							reason?: string;
							message?: string;
						};
						if (json.fallback) {
							return textResult(
								json.message ?? `Chat unavailable: ${json.reason ?? 'unknown'}`
							);
						}
					}

					const text = await consumeSSEStream(response);
					return textResult(text || 'No response received.');
				} catch (err) {
					const msg = err instanceof Error ? err.message : String(err);
					return errorResult(`Chat request failed: ${msg}`);
				}
			},
			config.onToolCall
		)
	};
}

function createBuildTokenTool(config: VCPWebMCPConfig): WebMCPToolDefinition | null {
	if (!config.tokenEncoder) return null;
	const encoder = config.tokenEncoder;

	return {
		name: 'vcp_build_token',
		description:
			'Build a CSM-1 token from a VCP context object. Returns a compact, emoji-annotated token string encoding personal state, constraints, and privacy markers.',
		inputSchema: {
			type: 'object',
			properties: {
				vcp_context: {
					type: 'object',
					description:
						'VCP context object. Must include at least vcp_version, profile_id, and constitution (with id and version).'
				}
			},
			required: ['vcp_context']
		},
		annotations: { readOnlyHint: true },
		execute: wrapExecute(
			'vcp_build_token',
			async (args) => {
				if (!isRecord(args.vcp_context)) return errorResult('vcp_context must be an object');
				try {
					const token = encoder(args.vcp_context);
					return textResult(token);
				} catch (err) {
					const msg = err instanceof Error ? err.message : String(err);
					return errorResult(`Token encoding failed: ${msg}`);
				}
			},
			config.onToolCall
		)
	};
}

function createParseTokenTool(config: VCPWebMCPConfig): WebMCPToolDefinition | null {
	if (!config.tokenParser && !config.wasmParser) return null;

	return {
		name: 'vcp_parse_token',
		description:
			'Parse a CSM-1 token string back into structured VCP context data. Uses the WASM parser if available, otherwise falls back to a JavaScript parser.',
		inputSchema: {
			type: 'object',
			properties: {
				token: {
					type: 'string',
					description: 'CSM-1 token string (newline-separated lines)'
				}
			},
			required: ['token']
		},
		annotations: { readOnlyHint: true },
		execute: wrapExecute(
			'vcp_parse_token',
			async (args) => {
				const token = typeof args.token === 'string' ? args.token.trim() : '';
				if (!token) return errorResult('token is required and must be a non-empty string');

				try {
					let parsed: unknown;
					let parser: string;

					if (config.wasmParser) {
						parsed = config.wasmParser(token);
						parser = 'wasm';
					} else if (config.tokenParser) {
						parsed = config.tokenParser(token);
						parser = 'js';
					} else {
						return errorResult('No token parser available');
					}

					const output = JSON.stringify({ parsed, parser }, null, 2);
					return textResult(output);
				} catch (err) {
					const msg = err instanceof Error ? err.message : String(err);
					return errorResult(`Token parsing failed: ${msg}`);
				}
			},
			config.onToolCall
		)
	};
}

function createSummaryTool(config: VCPWebMCPConfig): WebMCPToolDefinition | null {
	if (!config.transmissionSummary) return null;
	const getSummary = config.transmissionSummary;

	return {
		name: 'vcp_transmission_summary',
		description:
			'Analyze a VCP context to show what data would be transmitted to an AI, what is withheld (private), and what influences responses without being exposed. Privacy transparency tool.',
		inputSchema: {
			type: 'object',
			properties: {
				vcp_context: {
					type: 'object',
					description: 'VCP context object to analyze for privacy and transparency.'
				}
			},
			required: ['vcp_context']
		},
		annotations: { readOnlyHint: true },
		execute: wrapExecute(
			'vcp_transmission_summary',
			async (args) => {
				if (!isRecord(args.vcp_context)) return errorResult('vcp_context must be an object');

				try {
					const summary = getSummary(args.vcp_context);
					const lines = [
						'## VCP Transmission Summary',
						'',
						'### Transmitted (shared with AI)',
						...(summary.transmitted.length > 0
							? summary.transmitted.map((f) => `- ${f}`)
							: ['- (none)']),
						'',
						'### Withheld (private, never sent)',
						...(summary.withheld.length > 0
							? summary.withheld.map((f) => `- ${f}`)
							: ['- (none)']),
						'',
						'### Influencing (shapes response without exposing raw data)',
						...(summary.influencing.length > 0
							? summary.influencing.map((f) => `- ${f}`)
							: ['- (none)'])
					];
					return textResult(lines.join('\n'));
				} catch (err) {
					const msg = err instanceof Error ? err.message : String(err);
					return errorResult(`Summary generation failed: ${msg}`);
				}
			},
			config.onToolCall
		)
	};
}

function createPersonasTool(config: VCPWebMCPConfig): WebMCPToolDefinition {
	const personas = config.personas ?? DEFAULT_PERSONAS;

	return {
		name: 'vcp_list_personas',
		description:
			'List all available VCP personas with their descriptions and recommended use cases. Personas shape how the AI communicates and what it prioritizes.',
		inputSchema: {
			type: 'object',
			properties: {}
		},
		annotations: { readOnlyHint: true, idempotentHint: true },
		execute: wrapExecute(
			'vcp_list_personas',
			async () => {
				const lines = [
					'## VCP Personas',
					'',
					'| ID | Name | Description | Use Cases |',
					'|---|---|---|---|',
					...personas.map(
						(p) => `| ${p.id} | ${p.name} | ${p.description} | ${p.use} |`
					)
				];
				return textResult(lines.join('\n'));
			},
			config.onToolCall
		)
	};
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Build an array of VCP tool definitions from config.
 * Tools whose dependencies are missing (e.g. tokenEncoder not provided) are skipped.
 */
export function createVCPTools(config: VCPWebMCPConfig = {}): WebMCPToolDefinition[] {
	const tools: WebMCPToolDefinition[] = [];

	if (config.enableChat !== false) {
		tools.push(createChatTool(config));
	}

	if (config.enableTokenBuilder !== false) {
		const tool = createBuildTokenTool(config);
		if (tool) tools.push(tool);
	}

	if (config.enableTokenParser !== false) {
		const tool = createParseTokenTool(config);
		if (tool) tools.push(tool);
	}

	if (config.enableSummary !== false) {
		const tool = createSummaryTool(config);
		if (tool) tools.push(tool);
	}

	if (config.enablePersonas !== false) {
		tools.push(createPersonasTool(config));
	}

	return tools;
}
