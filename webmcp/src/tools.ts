/**
 * @creed-space/vcp-sdk — Tool Factory
 *
 * Creates VCP tool definitions from a config object.
 * Framework-agnostic — no SvelteKit or framework-specific imports.
 */

import type {
	VCPWebMCPConfig,
	PersonaInfo,
	TransmissionSummary,
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

const MAX_CHAT_REQUEST_BYTES = 1024 * 1024;
const MAX_CHAT_RESPONSE_BYTES = 1024 * 1024;
const MAX_TOOL_TEXT_BYTES = 1024 * 1024;
const MAX_SSE_EVENT_BYTES = 64 * 1024;
const MAX_STREAM_CHUNKS = 4096;
const MAX_SSE_EVENTS = 2048;
const MAX_SSE_LINES = 8192;
const DEFAULT_CHAT_TIMEOUT_MS = 30_000;
const MAX_CHAT_TIMEOUT_MS = 300_000;

function byteLength(value: string): number {
	return new TextEncoder().encode(value).byteLength;
}

function errorMessage(error: unknown): string {
	try {
		if (error instanceof Error && typeof error.message === 'string') return error.message;
		return String(error);
	} catch {
		return 'unknown error';
	}
}

async function cancelReader(reader: ReadableStreamDefaultReader<Uint8Array>): Promise<void> {
	try {
		await reader.cancel();
	} catch {
		// Preserve the primary parse, size, or transport error.
	}
}

async function readBoundedText(response: Response, limit: number): Promise<string> {
	const declaredLength = response.headers.get('content-length');
	if (declaredLength !== null) {
		const parsedLength = Number(declaredLength);
		if (Number.isFinite(parsedLength) && parsedLength > limit) {
			await response.body?.cancel();
			throw new Error('Chat response exceeds 1 MiB limit');
		}
	}

	if (!response.body) return '';
	const reader = response.body.getReader();
	const decoder = new TextDecoder('utf-8', { fatal: true });
	let receivedBytes = 0;
	let text = '';
	let complete = false;
	try {
		for (;;) {
			const { done, value } = await reader.read();
			if (done) break;
			receivedBytes += value.byteLength;
			if (receivedBytes > limit) {
				throw new Error('Chat response exceeds 1 MiB limit');
			}
			text += decoder.decode(value, { stream: true });
		}
		const result = text + decoder.decode();
		complete = true;
		return result;
	} finally {
		if (!complete) await cancelReader(reader);
		reader.releaseLock();
	}
}

/** Consume an SSE stream and return the complete text. */
async function consumeSSEStream(response: Response): Promise<string> {
	const body = response.body;
	if (!body) throw new Error('No response body');

	const reader = body.getReader();
	const decoder = new TextDecoder('utf-8', { fatal: true });
	let buffered = '';
	let bufferedBytes = 0;
	let receivedBytes = 0;
	let receivedChunks = 0;
	let receivedEvents = 0;
	let receivedLines = 0;
	let eventData: string[] = [];
	let eventDataBytes = 0;
	let skipLeadingLineFeed = false;
	let text = '';

	const dispatchEvent = (): boolean => {
		if (eventData.length === 0) return false;
		receivedEvents += 1;
		if (receivedEvents > MAX_SSE_EVENTS) {
			throw new Error('Chat response exceeds 2048 SSE events');
		}
		const data = eventData.join('\n');
		eventData = [];
		eventDataBytes = 0;
		if (data === '[DONE]') return true;

		let parsed: unknown;
		try {
			parsed = JSON.parse(data);
		} catch {
			throw new Error('Malformed JSON in chat event stream');
		}
		if (!isRecord(parsed)) throw new Error('Malformed chat event payload');
		if (parsed.error !== undefined && parsed.error !== null) {
			if (typeof parsed.error !== 'string') throw new Error('Malformed chat event error');
			if (parsed.error) throw new Error(parsed.error);
		}
		const delta = parsed.delta;
		if (delta !== undefined && !isRecord(delta)) {
			throw new Error('Malformed chat delta payload');
		}
		const deltaText = isRecord(delta) ? delta.text : undefined;
		if (deltaText !== undefined && typeof deltaText !== 'string') {
			throw new Error('Malformed chat delta text');
		}
		text += deltaText ?? '';
		return false;
	};

	const consumeLine = (line: string): boolean => {
		if (line.endsWith('\r')) line = line.slice(0, -1);
		if (line === '') return dispatchEvent();
		if (!line.startsWith('data:')) return false;
		const data = line.slice(5).replace(/^ /, '');
		eventDataBytes += byteLength(data) + (eventData.length === 0 ? 0 : 1);
		if (eventDataBytes > MAX_SSE_EVENT_BYTES) {
			throw new Error('Chat event exceeds 64 KiB limit');
		}
		eventData.push(data);
		return false;
	};

	const consumeDecoded = async (decoded: string): Promise<boolean> => {
		let index = 0;
		if (skipLeadingLineFeed) {
			if (decoded.startsWith('\n')) index = 1;
			skipLeadingLineFeed = false;
		}
		let start = index;
		for (; index < decoded.length; index++) {
			const terminator = decoded[index];
			if (terminator !== '\r' && terminator !== '\n') continue;
			const part = decoded.slice(start, index);
			receivedLines += 1;
			if (receivedLines > MAX_SSE_LINES) {
				throw new Error('Chat response exceeds 8192 lines');
			}
			const lineBytes = bufferedBytes + byteLength(part);
			if (lineBytes > MAX_SSE_EVENT_BYTES) {
				throw new Error('Chat event exceeds 64 KiB limit');
			}
			const line = buffered + part;
			buffered = '';
			bufferedBytes = 0;
			if (consumeLine(line)) {
				await cancelReader(reader);
				return true;
			}
			if (terminator === '\r') {
				if (decoded[index + 1] === '\n') index += 1;
				else if (index + 1 === decoded.length) skipLeadingLineFeed = true;
			}
			start = index + 1;
		}

		const remainder = decoded.slice(start);
		buffered += remainder;
		bufferedBytes += byteLength(remainder);
		if (bufferedBytes > MAX_SSE_EVENT_BYTES) {
			throw new Error('Chat event exceeds 64 KiB limit');
		}
		return false;
	};

	let complete = false;
	try {
		for (;;) {
			const { done, value } = await reader.read();
			if (done) break;
			receivedChunks += 1;
			if (receivedChunks > MAX_STREAM_CHUNKS) {
				throw new Error('Chat response exceeds 4096 chunks');
			}
			receivedBytes += value.byteLength;
			if (receivedBytes > MAX_CHAT_RESPONSE_BYTES) {
				throw new Error('Chat response exceeds 1 MiB limit');
			}
			if (await consumeDecoded(decoder.decode(value, { stream: true }))) {
				complete = true;
				return text;
			}
		}
		if (await consumeDecoded(decoder.decode())) {
			complete = true;
			return text;
		}
		if (buffered) {
			receivedLines += 1;
			if (receivedLines > MAX_SSE_LINES) {
				throw new Error('Chat response exceeds 8192 lines');
			}
			if (consumeLine(buffered)) {
				complete = true;
				return text;
			}
		}
		throw new Error('Chat event stream ended before [DONE]');
	} finally {
		if (!complete) await cancelReader(reader);
		reader.releaseLock();
	}
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

const MAX_PERSONAS = 100;
const PERSONA_ID_PATTERN = /^[a-z0-9_-]{1,64}$/;

function snapshotPersonas(value: unknown): PersonaInfo[] {
	const source = value === undefined ? DEFAULT_PERSONAS : value;
	if (!Array.isArray(source)) throw new TypeError('personas must be an array');
	if (source.length > MAX_PERSONAS) throw new RangeError('personas exceeds 100 entries');
	const seen = new Set<string>();
	return source.map((candidate, index) => {
		if (!isRecord(candidate)) throw new TypeError(`personas[${index}] must be an object`);
		const fields = {
			id: 64,
			name: 128,
			description: 2048,
			use: 2048,
		} as const;
		for (const [name, maximum] of Object.entries(fields)) {
			const field = candidate[name];
			if (typeof field !== 'string' || field.length === 0 || field.length > maximum) {
				throw new TypeError(
					`personas[${index}].${name} must contain 1 to ${maximum} characters`,
				);
			}
		}
		const id = candidate.id as string;
		if (!PERSONA_ID_PATTERN.test(id)) {
			throw new TypeError(`personas[${index}].id has an invalid format`);
		}
		if (seen.has(id)) throw new TypeError(`duplicate persona id: ${id}`);
		seen.add(id);
		return {
			id,
			name: candidate.name as string,
			description: candidate.description as string,
			use: candidate.use as string,
		};
	});
}

function markdownTableCell(value: string): string {
	return value.replace(/\r?\n/g, ' ').replace(/\|/g, '\\|');
}

function snapshotTransmissionSummary(value: unknown): TransmissionSummary {
	if (!isRecord(value)) throw new TypeError('transmission summary must be an object');
	const result: TransmissionSummary = {
		transmitted: [],
		withheld: [],
		influencing: [],
	};
	for (const name of ['transmitted', 'withheld', 'influencing'] as const) {
		const entries = value[name];
		if (!Array.isArray(entries)) {
			throw new TypeError(`transmission summary ${name} must be an array`);
		}
		if (entries.length > 1000) {
			throw new RangeError(`transmission summary ${name} exceeds 1000 entries`);
		}
		result[name] = entries.map((entry, index) => {
			if (typeof entry !== 'string' || entry.length > 4096) {
				throw new TypeError(
					`transmission summary ${name}[${index}] must be a string of at most 4096 characters`,
				);
			}
			return entry;
		});
	}
	return result;
}

// ---------------------------------------------------------------------------
// Tool factories
// ---------------------------------------------------------------------------

function wrapExecute(
	name: string,
	fn: (args: Record<string, unknown>) => Promise<WebMCPToolResult>,
	onToolCall?: (toolName: string) => void
): (args: Record<string, unknown>) => Promise<WebMCPToolResult> {
	return async (args) => {
		try {
			onToolCall?.(name);
		} catch {
			// Observability callbacks cannot block the tool they observe.
		}
		try {
			if (typeof window !== 'undefined' && typeof window.dispatchEvent === 'function') {
				window.dispatchEvent(
					new CustomEvent('webmcp:tool-call', {
						detail: { tool: name, timestamp: Date.now() }
					})
				);
			}
		} catch {
			// Browser observability is best-effort, including partial DOM shims.
		}
		return fn(isRecord(args) ? args : {});
	};
}

function createChatTool(config: VCPWebMCPConfig): WebMCPToolDefinition {
	const endpoint = config.chatEndpoint ?? '/api/chat';
	if (typeof endpoint !== 'string' || endpoint.length === 0 || endpoint.length > 2048) {
		throw new TypeError('chatEndpoint must contain 1 to 2048 characters');
	}
	const timeoutMs = config.chatTimeoutMs ?? DEFAULT_CHAT_TIMEOUT_MS;
	if (!Number.isInteger(timeoutMs) || timeoutMs < 1 || timeoutMs > MAX_CHAT_TIMEOUT_MS) {
		throw new TypeError('chatTimeoutMs must be an integer from 1 to 300000');
	}
	const personas = snapshotPersonas(config.personas);
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
				if (args.vcp_context !== undefined && !isRecord(args.vcp_context)) {
					return errorResult('vcp_context must be an object');
				}
				if (
					args.constitution_id !== undefined &&
					(typeof args.constitution_id !== 'string' ||
						args.constitution_id.length === 0 ||
						args.constitution_id.length > 2048)
				) {
					return errorResult('constitution_id must contain 1 to 2048 characters');
				}

				if (args.persona !== undefined) {
					if (typeof args.persona !== 'string' || !personaIds.includes(args.persona)) {
						return errorResult('persona must be one of the configured persona IDs');
					}
				}

				const body = {
					query,
					vcp_context: isRecord(args.vcp_context) ? args.vcp_context : undefined,
					constitution_id:
						typeof args.constitution_id === 'string' ? args.constitution_id : 'general',
					persona: typeof args.persona === 'string' ? args.persona : undefined
				};

				try {
					const requestBody = JSON.stringify(body);
					if (byteLength(requestBody) > MAX_CHAT_REQUEST_BYTES) {
						return errorResult('Chat request exceeds 1 MiB limit');
					}
					const controller = new AbortController();
					const timeout = setTimeout(() => controller.abort(), timeoutMs);
					try {
						const response = await fetch(endpoint, {
							method: 'POST',
							headers: { 'Content-Type': 'application/json' },
							body: requestBody,
							signal: controller.signal,
						});
						if (!response.ok) throw new Error(`HTTP ${response.status}`);

						const contentType = (response.headers.get('content-type') ?? '').toLowerCase();
						if (contentType.includes('application/json') || contentType.includes('+json')) {
							const raw = await readBoundedText(response, MAX_CHAT_RESPONSE_BYTES);
							let json: unknown;
							try {
								json = JSON.parse(raw);
							} catch {
								throw new Error('Malformed JSON chat response');
							}
							if (!isRecord(json)) throw new Error('Malformed JSON chat response');
							if (json.fallback === true) {
								return textResult(
									typeof json.message === 'string'
										? json.message
										: `Chat unavailable: ${typeof json.reason === 'string' ? json.reason : 'unknown'}`
								);
							}
							if (typeof json.message !== 'string') {
								throw new Error('JSON chat response has no message');
							}
							return textResult(json.message);
						}
						const text = await consumeSSEStream(response);
						return textResult(text || 'No response received.');
					} finally {
						clearTimeout(timeout);
					}
				} catch (err) {
					const msg = errorMessage(err);
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
					let serialized: string;
					try {
						serialized = JSON.stringify(args.vcp_context);
					} catch {
						return errorResult('vcp_context must be JSON-serializable');
					}
					if (byteLength(serialized) > MAX_TOOL_TEXT_BYTES) {
						return errorResult('vcp_context exceeds 1 MiB limit');
					}
					const token = encoder(args.vcp_context);
					if (typeof token !== 'string') throw new Error('encoder returned a non-string token');
					if (byteLength(token) > MAX_TOOL_TEXT_BYTES) {
						return errorResult('encoded token exceeds 1 MiB limit');
					}
					return textResult(token);
				} catch (err) {
					const msg = errorMessage(err);
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
				if (byteLength(token) > MAX_TOOL_TEXT_BYTES) {
					return errorResult('token exceeds 1 MiB limit');
				}

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
					if (byteLength(output) > MAX_TOOL_TEXT_BYTES) {
						return errorResult('parsed token output exceeds 1 MiB limit');
					}
					return textResult(output);
				} catch (err) {
					const msg = errorMessage(err);
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
					const summary = snapshotTransmissionSummary(getSummary(args.vcp_context));
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
					const output = lines.join('\n');
					if (byteLength(output) > MAX_TOOL_TEXT_BYTES) {
						return errorResult('transmission summary exceeds 1 MiB limit');
					}
					return textResult(output);
				} catch (err) {
					const msg = errorMessage(err);
					return errorResult(`Summary generation failed: ${msg}`);
				}
			},
			config.onToolCall
		)
	};
}

function createPersonasTool(config: VCPWebMCPConfig): WebMCPToolDefinition {
	const personas = snapshotPersonas(config.personas);

	return {
		name: 'vcp_list_personas',
		description:
			'List all available VCP personas with their descriptions and recommended use cases. Personas shape how the AI communicates and what it prioritizes.',
		inputSchema: {
			type: 'object',
			properties: {}
		},
		annotations: { readOnlyHint: true },
		execute: wrapExecute(
			'vcp_list_personas',
			async () => {
				const lines = [
					'## VCP Personas',
					'',
					'| ID | Name | Description | Use Cases |',
					'|---|---|---|---|',
					...personas.map(
						(p) =>
							`| ${markdownTableCell(p.id)} | ${markdownTableCell(p.name)} | ` +
							`${markdownTableCell(p.description)} | ${markdownTableCell(p.use)} |`
					)
				];
				const output = lines.join('\n');
				if (byteLength(output) > MAX_TOOL_TEXT_BYTES) {
					return errorResult('persona output exceeds 1 MiB limit');
				}
				return textResult(output);
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
	const safeConfig: VCPWebMCPConfig = isRecord(config) ? config : {};
	const tools: WebMCPToolDefinition[] = [];

	if (safeConfig.enableChat !== false) {
		tools.push(createChatTool(safeConfig));
	}

	if (safeConfig.enableTokenBuilder !== false) {
		const tool = createBuildTokenTool(safeConfig);
		if (tool) tools.push(tool);
	}

	if (safeConfig.enableTokenParser !== false) {
		const tool = createParseTokenTool(safeConfig);
		if (tool) tools.push(tool);
	}

	if (safeConfig.enableSummary !== false) {
		const tool = createSummaryTool(safeConfig);
		if (tool) tools.push(tool);
	}

	if (safeConfig.enablePersonas !== false) {
		tools.push(createPersonasTool(safeConfig));
	}

	return tools;
}
