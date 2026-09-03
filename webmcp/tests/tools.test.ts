import { afterEach, describe, it, expect, vi } from 'vitest';
import { createVCPTools } from '../src/tools.js';

afterEach(() => {
	vi.unstubAllGlobals();
});

function streamResponse(chunks: Uint8Array[], init?: ResponseInit): Response {
	return new Response(
		new ReadableStream<Uint8Array>({
			start(controller) {
				for (const chunk of chunks) controller.enqueue(chunk);
				controller.close();
			}
		}),
		init
	);
}

function chatTool(config: Parameters<typeof createVCPTools>[0] = {}) {
	return createVCPTools(config).find((tool) => tool.name === 'vcp_chat')!;
}

// ---------------------------------------------------------------------------
// createVCPTools — tool selection
// ---------------------------------------------------------------------------

describe('createVCPTools — tool selection', () => {
	it('returns chat and personas with empty config', () => {
		const tools = createVCPTools();
		const names = tools.map(t => t.name);
		expect(names).toContain('vcp_chat');
		expect(names).toContain('vcp_list_personas');
		expect(names).not.toContain('vcp_build_token');
		expect(names).not.toContain('vcp_parse_token');
		expect(names).not.toContain('vcp_transmission_summary');
	});

	it('includes build_token when tokenEncoder is provided', () => {
		const tools = createVCPTools({ tokenEncoder: () => 'token' });
		const names = tools.map(t => t.name);
		expect(names).toContain('vcp_build_token');
	});

	it('includes parse_token when tokenParser is provided', () => {
		const tools = createVCPTools({ tokenParser: () => ({}) });
		const names = tools.map(t => t.name);
		expect(names).toContain('vcp_parse_token');
	});

	it('includes parse_token when wasmParser is provided', () => {
		const tools = createVCPTools({ wasmParser: () => ({}) });
		const names = tools.map(t => t.name);
		expect(names).toContain('vcp_parse_token');
	});

	it('includes transmission_summary when provided', () => {
		const tools = createVCPTools({
			transmissionSummary: () => ({ transmitted: [], withheld: [], influencing: [] }),
		});
		const names = tools.map(t => t.name);
		expect(names).toContain('vcp_transmission_summary');
	});

	it('returns all 5 tools when fully configured', () => {
		const tools = createVCPTools({
			tokenEncoder: () => 'token',
			tokenParser: () => ({}),
			transmissionSummary: () => ({ transmitted: [], withheld: [], influencing: [] }),
		});
		expect(tools).toHaveLength(5);
	});

	it('respects enableChat: false', () => {
		const tools = createVCPTools({ enableChat: false });
		const names = tools.map(t => t.name);
		expect(names).not.toContain('vcp_chat');
	});

	it('respects enablePersonas: false', () => {
		const tools = createVCPTools({ enablePersonas: false });
		const names = tools.map(t => t.name);
		expect(names).not.toContain('vcp_list_personas');
	});

	it('respects enableTokenBuilder: false even with encoder', () => {
		const tools = createVCPTools({
			tokenEncoder: () => 'token',
			enableTokenBuilder: false,
		});
		const names = tools.map(t => t.name);
		expect(names).not.toContain('vcp_build_token');
	});

	it('rejects malformed or resource-exhausting persona configuration predictably', () => {
		expect(() => createVCPTools({ personas: [] })).toThrow(
			'personas must contain at least one entry',
		);
		expect(() => createVCPTools({ personas: null as never })).toThrow(
			'personas must be an array',
		);
		expect(() =>
			createVCPTools({
				personas: Array.from({ length: 101 }, (_value, index) => ({
					id: `p${index}`,
					name: 'Persona',
					description: 'Description',
					use: 'Use',
				})),
			}),
		).toThrow('personas exceeds 100 entries');
		expect(() =>
			createVCPTools({
				personas: [
					{ id: 'same', name: 'A', description: 'A', use: 'A' },
					{ id: 'same', name: 'B', description: 'B', use: 'B' },
				],
			}),
		).toThrow('duplicate persona id: same');
		expect(() => createVCPTools({ chatTimeoutMs: 0 })).toThrow(
			'chatTimeoutMs must be an integer from 1 to 300000',
		);
		expect(() => createVCPTools({ chatTimeoutMs: 300_001 })).toThrow(
			'chatTimeoutMs must be an integer from 1 to 300000',
		);
	});
});

// ---------------------------------------------------------------------------
// Tool execution
// ---------------------------------------------------------------------------

describe('createVCPTools — tool execution', () => {
	it('vcp_build_token calls the encoder', async () => {
		const encoder = vi.fn(() => 'VCP:1.0|test-token');
		const tools = createVCPTools({ tokenEncoder: encoder });
		const buildTool = tools.find(t => t.name === 'vcp_build_token')!;
		const result = await buildTool.execute({ vcp_context: { vcp_version: '1.0' } });
		expect(encoder).toHaveBeenCalledWith({ vcp_version: '1.0' });
		expect(result.content[0].text).toContain('VCP:1.0|test-token');
	});

	it('vcp_build_token returns error for non-object context', async () => {
		const tools = createVCPTools({ tokenEncoder: () => 'token' });
		const buildTool = tools.find(t => t.name === 'vcp_build_token')!;
		const result = await buildTool.execute({ vcp_context: 'not-an-object' });
		expect(result.content[0].text).toContain('Error');
	});

	it('vcp_build_token rejects circular input and a non-string encoder result', async () => {
		const circular: Record<string, unknown> = {};
		circular.self = circular;
		const circularTool = createVCPTools({ tokenEncoder: () => 'token' }).find(
			(tool) => tool.name === 'vcp_build_token',
		)!;
		expect((await circularTool.execute({ vcp_context: circular })).content[0].text).toBe(
			'Error: vcp_context must be JSON-serializable',
		);

		const badEncoder = createVCPTools({ tokenEncoder: (() => 42) as never }).find(
			(tool) => tool.name === 'vcp_build_token',
		)!;
		expect((await badEncoder.execute({ vcp_context: {} })).content[0].text).toBe(
			'Error: Token encoding failed: encoder returned a non-string token',
		);
	});

	it('sanitizes a hostile thrown encoder value', async () => {
		const hostile = new Proxy(
			{},
			{
				getPrototypeOf() {
					throw new Error('prototype trap');
				},
			},
		);
		const tool = createVCPTools({
			tokenEncoder: () => {
				throw hostile;
			},
		}).find((candidate) => candidate.name === 'vcp_build_token')!;
		expect((await tool.execute({ vcp_context: {} })).content[0].text).toBe(
			'Error: Token encoding failed: unknown error',
		);
	});

	it('vcp_parse_token uses JS parser by default', async () => {
		const parser = vi.fn(() => ({ version: '1.0' }));
		const tools = createVCPTools({ tokenParser: parser });
		const parseTool = tools.find(t => t.name === 'vcp_parse_token')!;
		const result = await parseTool.execute({ token: 'VCP:1.0|test' });
		expect(parser).toHaveBeenCalledWith('VCP:1.0|test');
		expect(result.content[0].text).toContain('"parser": "js"');
	});

	it('vcp_parse_token prefers WASM parser when both are provided', async () => {
		const jsParser = vi.fn(() => ({ source: 'js' }));
		const wasmParser = vi.fn(() => ({ source: 'wasm' }));
		const tools = createVCPTools({ tokenParser: jsParser, wasmParser });
		const parseTool = tools.find(t => t.name === 'vcp_parse_token')!;
		const result = await parseTool.execute({ token: 'test' });
		expect(wasmParser).toHaveBeenCalled();
		expect(jsParser).not.toHaveBeenCalled();
		expect(result.content[0].text).toContain('"parser": "wasm"');
	});

	it('vcp_parse_token returns error for empty token', async () => {
		const tools = createVCPTools({ tokenParser: () => ({}) });
		const parseTool = tools.find(t => t.name === 'vcp_parse_token')!;
		const result = await parseTool.execute({ token: '' });
		expect(result.content[0].text).toContain('Error');
	});

	it('vcp_parse_token rejects a cyclic parser result instead of throwing', async () => {
		const cyclic: Record<string, unknown> = {};
		cyclic.self = cyclic;
		const tools = createVCPTools({ tokenParser: () => cyclic });
		const parseTool = tools.find((tool) => tool.name === 'vcp_parse_token')!;
		const result = await parseTool.execute({ token: 'test' });
		expect(result.content[0].text).toContain('Error: Token parsing failed:');
	});

	it('vcp_list_personas returns formatted persona list', async () => {
		const tools = createVCPTools();
		const personasTool = tools.find(t => t.name === 'vcp_list_personas')!;
		const result = await personasTool.execute({});
		const text = result.content[0].text;
		expect(text).toContain('VCP Personas');
		expect(text).toContain('muse');
		expect(text).toContain('mediator');
		expect(text).toContain('sentinel');
	});

	it('vcp_transmission_summary formats categories', async () => {
		const tools = createVCPTools({
			transmissionSummary: () => ({
				transmitted: ['persona', 'constraints'],
				withheld: ['mood'],
				influencing: ['energy_level'],
			}),
		});
		const summaryTool = tools.find(t => t.name === 'vcp_transmission_summary')!;
		const result = await summaryTool.execute({ vcp_context: {} });
		const text = result.content[0].text;
		expect(text).toContain('persona');
		expect(text).toContain('mood');
		expect(text).toContain('energy_level');
		expect(text).toContain('Transmitted');
		expect(text).toContain('Withheld');
		expect(text).toContain('Influencing');
	});

	it.each([
		['non-object summary', () => null],
		['non-array category', () => ({ transmitted: 'x', withheld: [], influencing: [] })],
		[
			'oversized category',
			() => ({
				transmitted: Array.from({ length: 1001 }, () => 'x'),
				withheld: [],
				influencing: [],
			}),
		],
	])('vcp_transmission_summary rejects %s', async (_name, transmissionSummary) => {
		const summaryTool = createVCPTools({ transmissionSummary: transmissionSummary as never }).find(
			(tool) => tool.name === 'vcp_transmission_summary',
		)!;
		const result = await summaryTool.execute({ vcp_context: {} });
		expect(result.content[0].text).toContain('Error: Summary generation failed:');
	});

	it('chat rejects malformed optional arguments without calling fetch', async () => {
		const fetchMock = vi.fn();
		vi.stubGlobal('fetch', fetchMock);
		expect(
			(await chatTool().execute({ query: 'hello', vcp_context: [] })).content[0].text,
		).toBe('Error: vcp_context must be an object');
		expect(
			(await chatTool().execute({ query: 'hello', constitution_id: 42 })).content[0].text,
		).toBe('Error: constitution_id must contain 1 to 2048 characters');
		expect(fetchMock).not.toHaveBeenCalled();
	});

	it('aborts a chat request that does not settle before its deadline', async () => {
		let observedSignal: AbortSignal | undefined;
		vi.stubGlobal(
			'fetch',
			vi.fn((_input: string | URL | Request, init?: RequestInit) => {
				observedSignal = init?.signal ?? undefined;
				return new Promise<Response>((_resolve, reject) => {
					observedSignal?.addEventListener(
						'abort',
						() => reject(new DOMException('request timed out', 'AbortError')),
						{ once: true },
					);
				});
			}),
		);

		const result = await chatTool({ chatTimeoutMs: 1 }).execute({ query: 'hello' });
		expect(observedSignal?.aborted).toBe(true);
		expect(result.content[0].text).toContain('Error: Chat request failed:');
	});

	it('propagates WebMCP execution cancellation to the chat request', async () => {
		let observedSignal: AbortSignal | undefined;
		vi.stubGlobal(
			'fetch',
			vi.fn((_input: string | URL | Request, init?: RequestInit) => {
				observedSignal = init?.signal ?? undefined;
				return new Promise<Response>((_resolve, reject) => {
					observedSignal?.addEventListener(
						'abort',
						() => reject(new DOMException('execution cancelled', 'AbortError')),
						{ once: true },
					);
				});
			}),
		);

		const execution = new AbortController();
		const resultPromise = chatTool({ chatTimeoutMs: 1000 }).execute(
			{ query: 'hello' },
			{ signal: execution.signal },
		);
		expect(observedSignal?.aborted).toBe(false);
		execution.abort();

		const result = await resultPromise;
		expect(observedSignal?.aborted).toBe(true);
		expect(result.content[0].text).toContain('Error: Chat request failed:');
	});

	it('reassembles SSE lines and UTF-8 characters split across chunks', async () => {
		const encoded = new TextEncoder().encode(
			'data: {"delta":{"text":"hé"}}\n\ndata: {"delta":{"text":"llo"}}\n\ndata: [DONE]\n\n'
		);
		const splitAt = encoded.indexOf(0xc3) + 1;
		vi.stubGlobal(
			'fetch',
			vi.fn(async () =>
				streamResponse(
					[encoded.slice(0, 9), encoded.slice(9, splitAt), encoded.slice(splitAt)],
					{ headers: { 'content-type': 'text/event-stream' } }
				)
			)
		);

		const result = await chatTool().execute({ query: 'hello' });
		expect(result.content[0].text).toBe('héllo');
	});

	it.each([
		['LF', '\n', false],
		['bare CR', '\r', false],
		['CRLF split across chunks', '\r\n', true],
	])('assembles multiline SSE data with %s delimiters', async (_name, eol, splitCrLf) => {
		const encoded = new TextEncoder().encode(
			`data: {"delta":${eol}` +
				`data: {"text":"multi-line"}}${eol}${eol}` +
				`data: [DONE]${eol}${eol}`,
		);
		const chunks: Uint8Array[] = [];
		if (splitCrLf) {
			let start = 0;
			for (let index = 0; index < encoded.length; index++) {
				if (encoded[index] !== 0x0d) continue;
				chunks.push(encoded.slice(start, index + 1));
				start = index + 1;
			}
			if (start < encoded.length) chunks.push(encoded.slice(start));
		} else {
			chunks.push(encoded);
		}
		vi.stubGlobal(
			'fetch',
			vi.fn(async () =>
				streamResponse(chunks, { headers: { 'content-type': 'text/event-stream' } }),
			),
		);

		const result = await chatTool().execute({ query: 'hello' });
		expect(result.content[0].text).toBe('multi-line');
	});

	it('accepts a batch over 64 KiB when every completed SSE event is bounded', async () => {
		const eventCount = 2000;
		const batch = new TextEncoder().encode(
			Array.from(
				{ length: eventCount },
				() => 'data: {"delta":{"text":"abcdefgh"}}\n\n',
			).join('') +
				'data: [DONE]\n\n',
		);
		expect(batch.byteLength).toBeGreaterThan(64 * 1024);
		vi.stubGlobal(
			'fetch',
			vi.fn(async () =>
				streamResponse([batch], { headers: { 'content-type': 'text/event-stream' } }),
			),
		);

		const result = await chatTool().execute({ query: 'hello' });
		expect(result.content[0].text).toBe('abcdefgh'.repeat(eventCount));
	});

	it('bounds an unterminated SSE event incrementally', async () => {
		const oversized = new TextEncoder().encode(`data: ${'x'.repeat(64 * 1024)}`);
		vi.stubGlobal('fetch', vi.fn(async () => streamResponse([oversized])));

		const result = await chatTool().execute({ query: 'hello' });
		expect(result.content[0].text).toBe(
			'Error: Chat request failed: Chat event exceeds 64 KiB limit',
		);
	});

	it('bounds aggregate data across a multiline SSE event', async () => {
		const line = `data: ${'x'.repeat(40 * 1024)}\n`;
		const oversized = new TextEncoder().encode(`${line}${line}\n`);
		vi.stubGlobal('fetch', vi.fn(async () => streamResponse([oversized])));

		const result = await chatTool().execute({ query: 'hello' });
		expect(result.content[0].text).toBe(
			'Error: Chat request failed: Chat event exceeds 64 KiB limit',
		);
	});

	it('bounds zero-byte stream chunks independently of response bytes', async () => {
		const chunks = Array.from({ length: 4097 }, () => new Uint8Array());
		vi.stubGlobal('fetch', vi.fn(async () => streamResponse(chunks)));

		const result = await chatTool().execute({ query: 'hello' });
		expect(result.content[0].text).toBe(
			'Error: Chat request failed: Chat response exceeds 4096 chunks',
		);
	});

	it('bounds completed SSE events even when they arrive in one chunk', async () => {
		const batch = new TextEncoder().encode('data: {}\n\n'.repeat(2049));
		vi.stubGlobal('fetch', vi.fn(async () => streamResponse([batch])));

		const result = await chatTool().execute({ query: 'hello' });
		expect(result.content[0].text).toBe(
			'Error: Chat request failed: Chat response exceeds 2048 SSE events',
		);
	});

	it('bounds delimiter-only stream lines before they can exhaust CPU', async () => {
		const batch = new TextEncoder().encode('\n'.repeat(8193));
		vi.stubGlobal('fetch', vi.fn(async () => streamResponse([batch])));

		const result = await chatTool().execute({ query: 'hello' });
		expect(result.content[0].text).toBe(
			'Error: Chat request failed: Chat response exceeds 8192 lines',
		);
	});

	it('reports explicit errors from an SSE endpoint', async () => {
		const body = new TextEncoder().encode('data: {"error":"upstream boom"}\n\n');
		vi.stubGlobal('fetch', vi.fn(async () => streamResponse([body])));

		const result = await chatTool().execute({ query: 'hello' });
		expect(result.content[0].text).toBe('Error: Chat request failed: upstream boom');
	});

	it('rejects malformed or truncated SSE JSON instead of returning partial output', async () => {
		const body = new TextEncoder().encode(
			'data: {"delta":{"text":"partial"}}\n\ndata: {"delta":\n\n',
		);
		vi.stubGlobal('fetch', vi.fn(async () => streamResponse([body])));

		const result = await chatTool().execute({ query: 'hello' });
		expect(result.content[0].text).toBe(
			'Error: Chat request failed: Malformed JSON in chat event stream'
		);
	});

	it('rejects EOF after complete data events when the DONE sentinel is missing', async () => {
		const body = new TextEncoder().encode('data: {"delta":{"text":"partial"}}\n\n');
		vi.stubGlobal('fetch', vi.fn(async () => streamResponse([body])));

		const result = await chatTool().execute({ query: 'hello' });
		expect(result.content[0].text).toBe(
			'Error: Chat request failed: Chat event stream ended before [DONE]',
		);
	});

	it('returns a direct JSON chat response without consuming it as SSE', async () => {
		vi.stubGlobal(
			'fetch',
			vi.fn(async () =>
				new Response(JSON.stringify({ message: 'direct response' }), {
					headers: { 'content-type': 'application/json; charset=utf-8' }
				})
			)
		);

		const result = await chatTool().execute({ query: 'hello' });
		expect(result.content[0].text).toBe('direct response');
	});

	it('does not let a JSON fallback body bypass a non-success HTTP status', async () => {
		vi.stubGlobal(
			'fetch',
			vi.fn(async () =>
				new Response(JSON.stringify({ fallback: true, message: 'unsafe success' }), {
					status: 503,
					headers: { 'content-type': 'application/json' },
				}),
			),
		);
		const result = await chatTool().execute({ query: 'hello' });
		expect(result.content[0].text).toBe('Error: Chat request failed: HTTP 503');
	});

	it('rejects non-success responses before parsing a stream', async () => {
		vi.stubGlobal('fetch', vi.fn(async () => new Response('denied', { status: 503 })));

		const result = await chatTool().execute({ query: 'hello' });
		expect(result.content[0].text).toBe('Error: Chat request failed: HTTP 503');
	});

	it('bounds chat response bytes before buffering them', async () => {
		const oversized = new TextEncoder().encode('x'.repeat(1024 * 1024 + 1));
		vi.stubGlobal('fetch', vi.fn(async () => streamResponse([oversized])));

		const result = await chatTool().execute({ query: 'hello' });
		expect(result.content[0].text).toBe(
			'Error: Chat request failed: Chat response exceeds 1 MiB limit'
		);
	});

	it('cancels and releases a response stream after a decoding failure', async () => {
		const cancel = vi.fn();
		const body = new ReadableStream<Uint8Array>({
			start(controller) {
				controller.enqueue(Uint8Array.of(0xff));
			},
			cancel,
		});
		vi.stubGlobal(
			'fetch',
			vi.fn(async () => new Response(body, { headers: { 'content-type': 'text/event-stream' } })),
		);
		const result = await chatTool().execute({ query: 'hello' });
		expect(result.content[0].text).toContain('Error: Chat request failed:');
		expect(cancel).toHaveBeenCalledOnce();
	});

	it('bounds encoded request bytes before calling fetch', async () => {
		const fetchMock = vi.fn();
		vi.stubGlobal('fetch', fetchMock);

		const result = await chatTool().execute({
			query: 'hello',
			vcp_context: { value: 'x'.repeat(1024 * 1024) }
		});
		expect(result.content[0].text).toBe('Error: Chat request exceeds 1 MiB limit');
		expect(fetchMock).not.toHaveBeenCalled();
	});
});

// ---------------------------------------------------------------------------
// onToolCall callback
// ---------------------------------------------------------------------------

describe('createVCPTools — onToolCall', () => {
	it('fires callback when a tool executes', async () => {
		const callback = vi.fn();
		const tools = createVCPTools({ onToolCall: callback });
		const personasTool = tools.find(t => t.name === 'vcp_list_personas')!;
		await personasTool.execute({});
		expect(callback).toHaveBeenCalledWith('vcp_list_personas');
	});

	it('isolates callback failures from the observed tool', async () => {
		const tools = createVCPTools({
			onToolCall: () => {
				throw new Error('observer failed');
			}
		});
		const personasTool = tools.find((tool) => tool.name === 'vcp_list_personas')!;

		const result = await personasTool.execute({});
		expect(result.content[0].text).toContain('VCP Personas');
	});
});

// ---------------------------------------------------------------------------
// Default personas
// ---------------------------------------------------------------------------

describe('createVCPTools — default personas', () => {
	it('includes the 6 named CSM-1 registry personas', () => {
		const tools = createVCPTools();
		const chatTool = tools.find(t => t.name === 'vcp_chat')!;
		const personaEnum = chatTool.inputSchema.properties.persona?.enum;
		expect(personaEnum).toHaveLength(6);
		expect(personaEnum).toContain('muse');
		expect(personaEnum).toContain('ambassador');
		expect(personaEnum).toContain('godparent');
		expect(personaEnum).toContain('sentinel');
		expect(personaEnum).toContain('mediator');
		expect(personaEnum).toContain('nanny');
		expect(personaEnum).not.toContain('anchor');
		expect(personaEnum).not.toContain('steward');
	});

	it('documents and applies the ambassador default persona', async () => {
		const fetchMock = vi.fn(async () => new Response(JSON.stringify({ response: 'ok' })));
		vi.stubGlobal('fetch', fetchMock);
		try {
			const tools = createVCPTools();
			const chatTool = tools.find(t => t.name === 'vcp_chat')!;
			expect(chatTool.inputSchema.properties.persona?.description).toBe(
				'AI persona to use. Defaults to ambassador.',
			);
			await chatTool.execute({ query: 'hello' });
			const [, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
			expect(JSON.parse(init.body as string).persona).toBe('ambassador');
		} finally {
			vi.unstubAllGlobals();
		}
	});

	it('falls back to the first configured persona when ambassador is not configured', () => {
		const tools = createVCPTools({
			personas: [{ id: 'custom', name: 'Custom', description: 'Test', use: 'Testing' }],
		});
		const chatTool = tools.find(t => t.name === 'vcp_chat')!;
		expect(chatTool.inputSchema.properties.persona?.description).toBe(
			'AI persona to use. Defaults to custom.',
		);
	});

	it('allows custom personas to override defaults', () => {
		const tools = createVCPTools({
			personas: [{ id: 'custom', name: 'Custom', description: 'Test', use: 'Testing' }],
		});
		const chatTool = tools.find(t => t.name === 'vcp_chat')!;
		const personaEnum = chatTool.inputSchema.properties.persona?.enum;
		expect(personaEnum).toEqual(['custom']);
	});

	it('snapshots custom personas and escapes table-breaking text', async () => {
		const persona = {
			id: 'custom',
			name: 'Custom | Name',
			description: 'Line one\nLine two',
			use: 'Testing',
		};
		const tools = createVCPTools({ personas: [persona] });
		persona.name = 'Mutated';
		const personasTool = tools.find((tool) => tool.name === 'vcp_list_personas')!;
		const output = (await personasTool.execute({})).content[0].text;
		expect(output).toContain('Custom \\| Name');
		expect(output).toContain('Line one Line two');
		expect(output).not.toContain('Mutated');
	});

	it('escapes a backslash before a table separator without re-exposing the separator', async () => {
		const tools = createVCPTools({
			personas: [
				{
					id: 'custom',
					name: String.raw`Custom \| Name`,
					description: 'Test',
					use: 'Testing',
				},
			],
		});
		const personasTool = tools.find((tool) => tool.name === 'vcp_list_personas')!;
		const output = (await personasTool.execute({})).content[0].text;

		expect(output).toContain(String.raw`Custom \\\| Name`);
	});
});
