import { describe, expect, it } from 'vitest';
import {
	createFullHello,
	negotiate,
	VCPCapability,
	VCPExtension,
	type VCPHello,
	type VCPServerCapabilities,
} from '../src/extensions/negotiation.js';

const CORE = {
	encryption: true,
	injection_scanning: true,
	revocation: true,
	audit_chain: true,
	context_opacity: true,
} as const;

function server(
	overrides: Partial<VCPServerCapabilities> = {},
): VCPServerCapabilities {
	return {
		supported_versions: ['1.0', '2.0', '3.0', '3.1'],
		extensions: {
			'VCP-X-Personal': { decay: true },
			'VCP-X-Consensus': { voting_method: 'schulze' },
		},
		core_features: CORE,
		...overrides,
	};
}

function hello(overrides: Partial<VCPHello> = {}): VCPHello {
	return {
		type: 'vcp-hello',
		version: '3.1',
		min_version: '1.0',
		extensions: [],
		...overrides,
	};
}

describe('VCP capability negotiation', () => {
	it('selects the highest inclusive version and partitions extensions in client order', () => {
		const result = negotiate(
			hello({
				extensions: [
					'VCP-X-Relational',
					'VCP-X-Personal',
					'VCP-X-Consensus',
				],
			}),
			server({ server_id: 'server/4.2', session_id: 'ses_1' }),
		);

		expect(result).toEqual({
			type: 'vcp-ack',
			version: '3.1',
			supported: ['VCP-X-Personal', 'VCP-X-Consensus'],
			unsupported: ['VCP-X-Relational'],
			capabilities: {
				'VCP-X-Personal': { decay: true },
				'VCP-X-Consensus': { voting_method: 'schulze' },
			},
			core_features: CORE,
			server_id: 'server/4.2',
			session_id: 'ses_1',
		});
	});

	it('marks every valid request unsupported when downgraded below 3.1', () => {
		const result = negotiate(
			hello({ min_version: '3.0', extensions: ['VCP-X-Personal', 'VCP-X-Torch'] }),
			server({ supported_versions: ['1.0', '3.0'] }),
		);
		expect(result).toMatchObject({
			type: 'vcp-ack',
			version: '3.0',
			supported: [],
			unsupported: ['VCP-X-Personal', 'VCP-X-Torch'],
			capabilities: {},
		});
	});

	it('overrides dependency flags only when an active extension dependency is absent', () => {
		const withoutDependencies = negotiate(
			hello({ extensions: ['VCP-X-Torch', 'VCP-X-Intent'] }),
			server({
				extensions: {
					'VCP-X-Torch': { lineage: true, degraded: false },
					'VCP-X-Intent': { user_correction: true, personal_signals: true },
				},
			}),
		);
		expect(withoutDependencies).toMatchObject({
			capabilities: {
				'VCP-X-Torch': { lineage: true, degraded: true },
				'VCP-X-Intent': { user_correction: true, personal_signals: false },
			},
		});

		const withDependencies = negotiate(
			hello({
				extensions: [
					'VCP-X-Torch',
					'VCP-X-Relational',
					'VCP-X-Intent',
					'VCP-X-Personal',
				],
			}),
			server({
				extensions: {
					'VCP-X-Torch': { degraded: false },
					'VCP-X-Relational': {},
					'VCP-X-Intent': { personal_signals: true },
					'VCP-X-Personal': {},
				},
			}),
		);
		expect(withDependencies).toMatchObject({
			capabilities: {
				'VCP-X-Torch': { degraded: false },
				'VCP-X-Intent': { personal_signals: true },
			},
		});
	});

	it('returns the canonical error for no overlap and sorts unique valid server versions', () => {
		const result = negotiate(
			hello({ version: '1.0', min_version: '1.0' }),
			server({ supported_versions: ['3.1', '2.0', '3.1'] }),
		);
		expect(result).toEqual({
			type: 'vcp-error',
			code: 'VERSION_UNSUPPORTED',
			message: 'No mutually supported VCP version',
			supported_versions: ['2.0', '3.1'],
			retry_after: null,
		});
	});

	it.each([
		['patch version', { version: '3.1.0' }],
		['leading-zero version', { version: '03.1' }],
		['reversed range', { version: '2.0', min_version: '3.0' }],
	])('fails closed on %s', (_name, overrides) => {
		expect(negotiate(hello(overrides), server())).toMatchObject({
			type: 'vcp-error',
			code: 'VERSION_UNSUPPORTED',
		});
	});

	it('ignores bounded malformed extension identifiers', () => {
		const result = negotiate(
			hello({
				extensions: [
					'personal_state',
					'VCP-X-',
					'VCP-X-Personal',
					'VCP-X-Unknown',
				],
			}),
			server(),
		);
		expect(result).toMatchObject({
			supported: ['VCP-X-Personal'],
			unsupported: ['VCP-X-Unknown'],
		});
	});

	it('uses Unicode code points for schema character bounds', () => {
		const boundedInvalidIdentifier = '🯿'.repeat(128);
		expect(
			negotiate(
				hello({
					extensions: [boundedInvalidIdentifier],
					client_id: '🯿'.repeat(256),
					identity: '🯿'.repeat(2048),
				}),
				server({ server_id: '🯿'.repeat(256), session_id: '🯿'.repeat(128) }),
			),
		).toMatchObject({ supported: [], unsupported: [] });
		expect(() =>
			negotiate(hello({ extensions: ['🯿'.repeat(129)] }), server()),
		).toThrow('hello.extensions entries must contain 1 to 128 characters');
		expect(() =>
			negotiate(hello({ client_id: '🯿'.repeat(257) }), server()),
		).toThrow('hello.client_id must be a non-empty string of at most 256 characters');
	});

	it('rejects duplicate extension strings before negotiation', () => {
		expect(() =>
			negotiate(
				hello({ extensions: ['VCP-X-Personal', 'VCP-X-Personal'] }),
				server(),
			),
		).toThrow('duplicate hello extension: VCP-X-Personal');
	});

	it('does not activate server-only extensions when the request is empty', () => {
		const result = negotiate(hello({ extensions: undefined }), server());
		expect(result).toMatchObject({ supported: [], unsupported: [], capabilities: {} });
	});

	it('snapshots capability and core-feature objects in its result', () => {
		const capability = { decay: true, nested: { level: 2 } };
		const core = { ...CORE };
		const result = negotiate(
			hello({ extensions: ['VCP-X-Personal'] }),
			server({ extensions: { 'VCP-X-Personal': capability }, core_features: core }),
		);
		capability.decay = false;
		capability.nested.level = 9;
		core.encryption = false;
		expect(result).toMatchObject({
			capabilities: { 'VCP-X-Personal': { decay: true, nested: { level: 2 } } },
			core_features: { encryption: true },
		});
	});

	it('rejects capability values that JSON would silently drop or coerce', () => {
		for (const capability of [
			{ future: undefined },
			{ score: Number.NaN },
			{ callback: () => true },
		]) {
			expect(() =>
				negotiate(
					hello({ extensions: ['VCP-X-Personal'] }),
					server({ extensions: { 'VCP-X-Personal': capability } }),
				),
			).toThrow('server.extensions.VCP-X-Personal must be a JSON-serializable object');
		}
	});

	it('rejects malformed server state and resource-exhaustion arrays', () => {
		expect(() => negotiate(hello({ extensions: null as never }), server())).toThrow(
			'hello.extensions must be an array',
		);
		for (const [field, invalidServer] of [
			['hello.client_id', hello({ client_id: '' })],
			['server.server_id', hello()],
			['server.session_id', hello()],
		] as const) {
			const overrides = field === 'server.server_id'
				? { server_id: '' }
				: field === 'server.session_id'
					? { session_id: '' }
					: {};
			expect(() => negotiate(invalidServer, server(overrides))).toThrow(
				`${field} must be a non-empty string`,
			);
		}
		expect(() =>
			negotiate(
				hello({ extensions: Array.from({ length: 257 }, () => 'VCP-X-A') }),
				server(),
			),
		).toThrow('hello.extensions exceeds 256 entries');
		expect(() =>
			negotiate(
				hello(),
				server({ supported_versions: Array.from({ length: 65 }, () => '3.1') }),
			),
		).toThrow('server.supported_versions exceeds 64 entries');
		expect(() =>
			negotiate(hello(), server({ core_features: { ...CORE, encryption: 1 } as never })),
		).toThrow('server.core_features.encryption must be a boolean');
		expect(() =>
			negotiate(
				hello(),
				server({ extensions: { 'VCP-X-Personal': [] as never } }),
			),
		).toThrow('server.extensions.VCP-X-Personal must be an object');
		expect(() =>
			negotiate(hello(), server({ extensions: { personal_state: {} } })),
		).toThrow('server.extensions has invalid identifier: personal_state');
		expect(() =>
			negotiate(hello({ extensions: [42 as unknown as string] }), server()),
		).toThrow('hello.extensions entries must be strings');
		expect(() =>
			negotiate(hello({ extensions: [''] }), server()),
		).toThrow('hello.extensions entries must contain 1 to 128 characters');
		expect(() =>
			negotiate(hello(), server({ supported_versions: ['3.1.0'] })),
		).toThrow('server.supported_versions entries must be major.minor');
		const oversizedRegistry = Object.fromEntries(
			Array.from({ length: 257 }, (_, index) => [`VCP-X-E${index}`, {}]),
		);
		expect(() =>
			negotiate(hello(), server({ extensions: oversizedRegistry })),
		).toThrow('server.extensions exceeds 256 entries');
	});

	it('accepts exactly 64 KiB of UTF-8 handshake input and rejects one byte more', () => {
		const encoder = new TextEncoder();
		const atLimit = { ...hello(), future_padding: '' } as VCPHello & {
			future_padding: string;
		};
		const fixedBytes = encoder.encode(JSON.stringify(atLimit)).byteLength;
		atLimit.future_padding = 'a'.repeat(64 * 1024 - fixedBytes);
		expect(encoder.encode(JSON.stringify(atLimit))).toHaveLength(64 * 1024);
		expect(negotiate(atLimit, server())).toMatchObject({ type: 'vcp-ack' });

		const overLimit = { ...atLimit, future_padding: `${atLimit.future_padding}a` };
		expect(() => negotiate(overLimit, server())).toThrow('handshake exceeds 64 KiB');
	});

	it('rejects a non-hello message rather than negotiating under an invalid assumption', () => {
		expect(() => negotiate({ ...hello(), type: 'VCP-Hello' } as never, server())).toThrow(
			"hello.type must be 'vcp-hello'",
		);
	});
});

describe('createFullHello', () => {
	it('creates the canonical 3.1 wire shape with every defined extension', () => {
		expect(createFullHello('client/4.2', null)).toEqual({
			type: 'vcp-hello',
			version: '3.1',
			min_version: '1.0',
			extensions: Object.values(VCPExtension),
			identity: null,
			client_id: 'client/4.2',
		});
		expect(VCPCapability).toBe(VCPExtension);
		expect(Object.values(VCPExtension)).toEqual([
			'VCP-X-Personal',
			'VCP-X-Relational',
			'VCP-X-Consensus',
			'VCP-X-Torch',
			'VCP-X-Intent',
		]);
	});

	it('omits optional identity and client identifier instead of serializing undefined', () => {
		const value = createFullHello();
		expect(value).not.toHaveProperty('identity');
		expect(value).not.toHaveProperty('client_id');
	});
});
