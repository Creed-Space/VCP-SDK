import { describe, it, expect } from 'vitest';
import {
	NAMESPACE_PREFIXES,
	isIdentityTokenSyntax,
	namespaceTierOf,
	validateIdentityToken,
} from '../src/identity.js';

describe('VCP/I identity validation (VCP/I 3.4.1)', () => {
	it('lists the twelve namespace prefixes by tier', () => {
		expect(NAMESPACE_PREFIXES.core).toEqual(['family', 'work', 'secure', 'creative', 'reality']);
		expect(NAMESPACE_PREFIXES.org).toEqual(['company', 'school', 'ngo']);
		expect(NAMESPACE_PREFIXES.community).toEqual(['religion', 'culture', 'community']);
		expect(NAMESPACE_PREFIXES.personal).toEqual(['user']);
		expect(namespaceTierOf('health')).toBeNull();
	});

	it.each([
		['family.safe.guide@1.2.0', 'core'],
		['creative.growth.muse', 'core'],
		['company.acme.legal.compliance:SEC', 'org'],
		['religion.buddhist.mindfulness', 'community'],
		['user.alice.notes', 'personal'],
	])('accepts %s as %s', (token, tier) => {
		expect(validateIdentityToken(token)).toEqual({
			valid: true,
			syntaxValid: true,
			namespaceTier: tier,
		});
	});

	it.each([
		['my-org.safe-net.web-guard', 'unknown_namespace_prefix'],
		['personal.growth.creative', 'unknown_namespace_prefix'],
		['health.privacy.hipaa', 'unknown_namespace_prefix'],
		['family.safe.guide.extra', 'core_segment_count'],
		['family.safe.guide.extra@1.0.0:SEC', 'core_segment_count'],
		['user.alice.private', 'reserved_word'],
	])('parses %s but rejects it with %s', (token, error) => {
		expect(isIdentityTokenSyntax(token)).toBe(true);
		const result = validateIdentityToken(token);
		expect(result.valid).toBe(false);
		expect(result).toMatchObject({ syntaxValid: true, error });
	});

	it('reports syntax errors before semantic rules', () => {
		expect(validateIdentityToken('Family.Safe.Guide')).toMatchObject({
			valid: false,
			syntaxValid: false,
			error: 'syntax',
		});
		expect(validateIdentityToken(`company.${'a'.repeat(260)}.x`).valid).toBe(false);
	});
});
