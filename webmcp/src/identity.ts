/**
 * VCP/I identity token validation.
 *
 * VCP/I §3.4.1 separates syntax from semantics. The syntax (the §3.4 ABNF and
 * the `token.pattern` of schemas/vcp-identity-token.schema.json) accepts any
 * lowercase first segment, so a parser may relay, log or display such a
 * token. A validator also requires a listed namespace prefix, exactly three
 * segments for a Core token, and no reserved-word segment (§3.7.1).
 * Mirrors Python `Token.validate` and Rust `VcpToken::validate`.
 */

/** Syntax of a VCP/I token (schema `token.pattern`, VCP/I §3.4). */
export const IDENTITY_TOKEN_SYNTAX =
	/^[a-z][a-z0-9-]{0,31}(?:\.[a-z][a-z0-9-]{0,31}){2,9}(?:@(?:[\^~]?[0-9]{1,5}\.[0-9]{1,5}\.[0-9]{1,5}(?:-[a-zA-Z0-9.-]+)?|latest|canary))?(?::[A-Z][A-Z0-9]{0,31})?$/;

/** Maximum length of a complete token, including version and suffix. */
export const MAX_IDENTITY_TOKEN_LENGTH = 256;

/** Namespace governance tier, labeled as in the identity schema. */
export type NamespaceTier = 'core' | 'org' | 'community' | 'personal';

/** Namespace prefixes by tier (VCP/I §3.2 and §4.2). */
export const NAMESPACE_PREFIXES: Readonly<Record<NamespaceTier, readonly string[]>> = {
	core: ['family', 'work', 'secure', 'creative', 'reality'],
	org: ['company', 'school', 'ngo'],
	community: ['religion', 'culture', 'community'],
	personal: ['user'],
};

/** Words that must not be used as segments (VCP/I §3.7.1). */
export const RESERVED_WORDS: readonly string[] = [
	'system', 'admin', 'root', 'null', 'undefined',
	'true', 'false', 'none', 'void', 'default',
	'api', 'internal', 'private', 'public', 'test',
	'debug', 'staging', 'production',
	'vcp', 'uvc', 'csm', 'bundle', 'manifest', 'creed',
	'official', 'verified', 'authentic', 'real',
];

/** Machine-readable failure codes, shared with the Python and Rust SDKs. */
export type IdentityValidationError =
	| 'syntax'
	| 'unknown_namespace_prefix'
	| 'core_segment_count'
	| 'reserved_word';

export type IdentityValidationResult =
	| { readonly valid: true; readonly syntaxValid: true; readonly namespaceTier: NamespaceTier }
	| {
			readonly valid: false;
			readonly syntaxValid: boolean;
			readonly error: IdentityValidationError;
			readonly message: string;
	  };

/** Whether `token` is a syntactically valid VCP/I token (parser rule only). */
export function isIdentityTokenSyntax(token: string): boolean {
	return token.length <= MAX_IDENTITY_TOKEN_LENGTH && IDENTITY_TOKEN_SYNTAX.test(token);
}

/** Namespace tier of a first segment, or `null` for an unlisted prefix. */
export function namespaceTierOf(prefix: string): NamespaceTier | null {
	for (const tier of Object.keys(NAMESPACE_PREFIXES) as NamespaceTier[]) {
		if (NAMESPACE_PREFIXES[tier].includes(prefix)) return tier;
	}
	return null;
}

/** Validate a VCP/I token: syntax first, then the §3.4.1 semantic rules. */
export function validateIdentityToken(token: string): IdentityValidationResult {
	if (typeof token !== 'string' || !isIdentityTokenSyntax(token)) {
		return {
			valid: false,
			syntaxValid: false,
			error: 'syntax',
			message: 'Invalid VCP/I token syntax',
		};
	}
	const path = token.split(/[@:]/, 1)[0];
	const segments = path.split('.');
	const prefix = segments[0];
	const tier = namespaceTierOf(prefix);
	if (tier === null) {
		return {
			valid: false,
			syntaxValid: true,
			error: 'unknown_namespace_prefix',
			message: `Unknown namespace prefix: '${prefix}'`,
		};
	}
	if (tier === 'core' && segments.length !== 3) {
		return {
			valid: false,
			syntaxValid: true,
			error: 'core_segment_count',
			message: `Core namespace '${prefix}' requires exactly 3 segments, got ${segments.length}`,
		};
	}
	const reservedIndex = segments.findIndex((segment) => RESERVED_WORDS.includes(segment));
	if (reservedIndex !== -1) {
		return {
			valid: false,
			syntaxValid: true,
			error: 'reserved_word',
			message: `Segment ${reservedIndex + 1} is a reserved word: '${segments[reservedIndex]}'`,
		};
	}
	return { valid: true, syntaxValid: true, namespaceTier: tier };
}
