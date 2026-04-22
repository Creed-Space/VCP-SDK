import { describe, it, expect } from 'vitest';
import {
	negotiate,
	createFullHello,
	VCPCapability,
	type VCPHello,
} from '../src/extensions/negotiation.js';

// ---------------------------------------------------------------------------
// negotiate
// ---------------------------------------------------------------------------

describe('negotiate', () => {
	it('grants all capabilities when server supports everything', () => {
		const hello: VCPHello = {
			version: '3.1.0',
			requestedCapabilities: ['categorical_context', 'personal_context'],
		};
		const ack = negotiate(hello, ['categorical_context', 'personal_context', 'signal_decay']);
		expect(ack.success).toBe(true);
		expect(ack.grantedCapabilities).toEqual(['categorical_context', 'personal_context']);
		expect(ack.deniedCapabilities).toEqual([]);
		expect(ack.reason).toBeUndefined();
	});

	it('partially grants when server supports some capabilities', () => {
		const hello: VCPHello = {
			version: '3.1.0',
			requestedCapabilities: ['categorical_context', 'torch_handoff', 'consensus_voting'],
		};
		const ack = negotiate(hello, ['categorical_context']);
		expect(ack.success).toBe(false);
		expect(ack.grantedCapabilities).toEqual(['categorical_context']);
		expect(ack.deniedCapabilities).toEqual(['torch_handoff', 'consensus_voting']);
		expect(ack.reason).toContain('torch_handoff');
		expect(ack.reason).toContain('consensus_voting');
	});

	it('denies all when server supports nothing requested', () => {
		const hello: VCPHello = {
			version: '3.1.0',
			requestedCapabilities: ['consensus_voting'],
		};
		const ack = negotiate(hello, ['categorical_context']);
		expect(ack.success).toBe(false);
		expect(ack.grantedCapabilities).toEqual([]);
		expect(ack.deniedCapabilities).toEqual(['consensus_voting']);
	});

	it('succeeds with empty request', () => {
		const hello: VCPHello = {
			version: '3.1.0',
			requestedCapabilities: [],
		};
		const ack = negotiate(hello, ['categorical_context']);
		expect(ack.success).toBe(true);
		expect(ack.grantedCapabilities).toEqual([]);
		expect(ack.deniedCapabilities).toEqual([]);
	});

	it('preserves the version from hello', () => {
		const hello: VCPHello = {
			version: '3.1.0',
			requestedCapabilities: [],
		};
		const ack = negotiate(hello, []);
		expect(ack.version).toBe('3.1.0');
	});
});

// ---------------------------------------------------------------------------
// createFullHello
// ---------------------------------------------------------------------------

describe('createFullHello', () => {
	it('requests all known VCP capabilities', () => {
		const hello = createFullHello();
		const allCaps = Object.values(VCPCapability);
		expect(hello.requestedCapabilities).toEqual(allCaps);
		expect(hello.version).toBe('3.1.0');
	});

	it('includes clientId and constitutionRef when provided', () => {
		const hello = createFullHello('my-client', 'safety.core@1.0');
		expect(hello.clientId).toBe('my-client');
		expect(hello.constitutionRef).toBe('safety.core@1.0');
	});

	it('omits clientId and constitutionRef when not provided', () => {
		const hello = createFullHello();
		expect(hello.clientId).toBeUndefined();
		expect(hello.constitutionRef).toBeUndefined();
	});
});

// ---------------------------------------------------------------------------
// VCPCapability enum
// ---------------------------------------------------------------------------

describe('VCPCapability', () => {
	it('has 10 known capabilities', () => {
		expect(Object.keys(VCPCapability)).toHaveLength(10);
	});

	it('includes all expected capability strings', () => {
		const values = Object.values(VCPCapability);
		expect(values).toContain('categorical_context');
		expect(values).toContain('personal_context');
		expect(values).toContain('signal_decay');
		expect(values).toContain('relational_context');
		expect(values).toContain('torch_handoff');
		expect(values).toContain('ai_self_model');
		expect(values).toContain('consensus_voting');
		expect(values).toContain('generation_prefs');
		expect(values).toContain('attestation');
		expect(values).toContain('inter_agent');
	});
});
