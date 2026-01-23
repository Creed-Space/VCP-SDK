/**
 * Docs Search Index
 * Client-side full-text search for documentation
 */

export interface SearchResult {
	title: string;
	path: string;
	excerpt: string;
	section?: string;
	score: number;
}

export interface SearchDocument {
	title: string;
	path: string;
	content: string;
	section?: string;
	keywords?: string[];
}

// Pre-indexed documentation content
const docsIndex: SearchDocument[] = [
	{
		title: 'Getting Started',
		path: '/docs/getting-started',
		section: 'Guides',
		content:
			'Quick start guide for VCP. Learn how to integrate the Value Context Protocol into your application. Installation, configuration, and first steps.',
		keywords: ['setup', 'install', 'configure', 'quick start', 'tutorial', 'beginner']
	},
	{
		title: 'CSM-1 Specification',
		path: '/docs/csm1-specification',
		section: 'Reference',
		content:
			'Complete CSM-1 token format specification. Encoding rules, emoji mappings, constraint flags, persona identifiers, and transmission protocols.',
		keywords: ['token', 'format', 'encoding', 'specification', 'protocol', 'csm1', 'csm-1']
	},
	{
		title: 'API Reference',
		path: '/docs/api-reference',
		section: 'Reference',
		content:
			'Full API documentation for VCP. Context encoding, privacy filtering, platform manifests, consent management, and integration endpoints.',
		keywords: ['api', 'reference', 'endpoints', 'methods', 'functions']
	},
	{
		title: 'Core Concepts',
		path: '/docs/concepts',
		section: 'Guides',
		content:
			'Understand VCP fundamentals. Context portability, privacy preservation, constraint abstraction, consent-based sharing, and stakeholder visibility.',
		keywords: ['concepts', 'fundamentals', 'basics', 'overview', 'introduction']
	},
	{
		title: 'Privacy Architecture',
		path: '/docs/privacy-architecture',
		section: 'Architecture',
		content:
			'Deep dive into VCP privacy model. Private context never transmitted, boolean constraint flags, consent layers, and data minimization strategies.',
		keywords: ['privacy', 'security', 'architecture', 'constraints', 'consent', 'gdpr']
	},
	{
		title: 'Constitutional AI',
		path: '/docs/constitutional-ai',
		section: 'Architecture',
		content:
			'Constitutional AI integration with VCP. Personas, adherence levels, scopes, and behavioral boundaries for AI systems.',
		keywords: ['constitutional', 'ai', 'persona', 'godparent', 'sentinel', 'ambassador', 'anchor', 'nanny']
	},
	{
		title: 'Multi-Agent Systems',
		path: '/docs/multi-agent',
		section: 'Architecture',
		content:
			'VCP for multi-agent coordination. Negotiation protocols, policy design, resource allocation, and collective decision-making.',
		keywords: ['multi-agent', 'coordination', 'negotiation', 'agents', 'collective']
	},
	{
		title: 'Interiora Self-Modeling',
		path: '/docs/interiora',
		section: 'Features',
		content:
			'Interiora framework for AI self-modeling. Internal state tracking, VCP token encoding, welfare indicators, and introspective capabilities.',
		keywords: ['interiora', 'self-modeling', 'introspection', 'welfare', 'internal state']
	},
	{
		title: 'Playground',
		path: '/playground',
		section: 'Tools',
		content:
			'Interactive VCP token builder. Create and inspect CSM-1 tokens, adjust settings in real-time, and visualize privacy controls.',
		keywords: ['playground', 'interactive', 'builder', 'demo', 'try']
	},
	{
		title: 'About VCP',
		path: '/about',
		section: 'Overview',
		content:
			'What is the Value Context Protocol? Share what matters. Keep what\'s personal. A standard for privacy-preserving context sharing.',
		keywords: ['about', 'overview', 'what is', 'introduction']
	}
];

/**
 * Simple text similarity scoring
 */
function calculateScore(query: string, document: SearchDocument): number {
	const queryTerms = query.toLowerCase().split(/\s+/).filter(Boolean);
	if (queryTerms.length === 0) return 0;

	let score = 0;
	const titleLower = document.title.toLowerCase();
	const contentLower = document.content.toLowerCase();
	const keywordsLower = (document.keywords || []).map((k) => k.toLowerCase());

	for (const term of queryTerms) {
		// Title match (highest weight)
		if (titleLower.includes(term)) {
			score += 10;
			if (titleLower.startsWith(term)) score += 5;
		}

		// Keyword match (high weight)
		if (keywordsLower.some((k) => k.includes(term) || term.includes(k))) {
			score += 8;
		}

		// Content match
		const contentMatches = (contentLower.match(new RegExp(term, 'g')) || []).length;
		score += Math.min(contentMatches * 2, 10);

		// Section match
		if (document.section?.toLowerCase().includes(term)) {
			score += 3;
		}
	}

	// Boost for matching all terms
	const allTermsMatch = queryTerms.every(
		(term) =>
			titleLower.includes(term) ||
			contentLower.includes(term) ||
			keywordsLower.some((k) => k.includes(term))
	);
	if (allTermsMatch) score *= 1.5;

	return score;
}

/**
 * Generate excerpt with highlighted terms
 */
function generateExcerpt(query: string, content: string, maxLength = 150): string {
	const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
	const contentLower = content.toLowerCase();

	// Find best starting position (near first term match)
	let startPos = 0;
	for (const term of terms) {
		const idx = contentLower.indexOf(term);
		if (idx !== -1) {
			startPos = Math.max(0, idx - 30);
			break;
		}
	}

	let excerpt = content.substring(startPos, startPos + maxLength);

	// Clean up excerpt boundaries
	if (startPos > 0) excerpt = '...' + excerpt.trimStart();
	if (startPos + maxLength < content.length) excerpt = excerpt.trimEnd() + '...';

	return excerpt;
}

/**
 * Search the documentation index
 */
export function searchDocs(query: string, limit = 10): SearchResult[] {
	if (!query || query.trim().length < 2) return [];

	const results: SearchResult[] = [];

	for (const doc of docsIndex) {
		const score = calculateScore(query, doc);
		if (score > 0) {
			results.push({
				title: doc.title,
				path: doc.path,
				section: doc.section,
				excerpt: generateExcerpt(query, doc.content),
				score
			});
		}
	}

	// Sort by score descending
	results.sort((a, b) => b.score - a.score);

	return results.slice(0, limit);
}

/**
 * Get all searchable sections
 */
export function getSearchSections(): string[] {
	const sections = new Set<string>();
	for (const doc of docsIndex) {
		if (doc.section) sections.add(doc.section);
	}
	return Array.from(sections).sort();
}
