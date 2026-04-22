import { describe, it, expect, vi } from 'vitest';
import { createVCPTools } from '../src/tools.js';

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

	it('vcp_list_personas returns formatted persona list', async () => {
		const tools = createVCPTools();
		const personasTool = tools.find(t => t.name === 'vcp_list_personas')!;
		const result = await personasTool.execute({});
		const text = result.content[0].text;
		expect(text).toContain('VCP Personas');
		expect(text).toContain('muse');
		expect(text).toContain('steward');
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
});

// ---------------------------------------------------------------------------
// Default personas
// ---------------------------------------------------------------------------

describe('createVCPTools — default personas', () => {
	it('includes 7 default personas', () => {
		const tools = createVCPTools();
		const chatTool = tools.find(t => t.name === 'vcp_chat')!;
		const personaEnum = chatTool.inputSchema.properties.persona?.enum;
		expect(personaEnum).toHaveLength(7);
		expect(personaEnum).toContain('muse');
		expect(personaEnum).toContain('ambassador');
		expect(personaEnum).toContain('godparent');
		expect(personaEnum).toContain('sentinel');
		expect(personaEnum).toContain('anchor');
		expect(personaEnum).toContain('nanny');
		expect(personaEnum).toContain('steward');
	});

	it('allows custom personas to override defaults', () => {
		const tools = createVCPTools({
			personas: [{ id: 'custom', name: 'Custom', description: 'Test', use: 'Testing' }],
		});
		const chatTool = tools.find(t => t.name === 'vcp_chat')!;
		const personaEnum = chatTool.inputSchema.properties.persona?.enum;
		expect(personaEnum).toEqual(['custom']);
	});
});
