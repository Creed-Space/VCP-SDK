import { readFile, readdir, stat } from 'node:fs/promises';
import { join } from 'node:path';

const root = new URL('..', import.meta.url);
const pkg = JSON.parse(await readFile(new URL('package.json', root), 'utf8'));
const expectedFiles = ['dist', 'README.md', 'LICENSE'];
if (JSON.stringify(pkg.files) !== JSON.stringify(expectedFiles)) {
	throw new Error(`package files must be exactly: ${expectedFiles.join(', ')}`);
}

for (const name of ['README.md', 'LICENSE', 'dist/index.js', 'dist/index.d.ts']) {
	const info = await stat(new URL(name, root));
	if (!info.isFile() || info.size === 0) throw new Error(`missing package artifact: ${name}`);
}

async function walk(directory) {
	const entries = await readdir(directory, { withFileTypes: true });
	const paths = [];
	for (const entry of entries) {
		const path = join(directory, entry.name);
		if (entry.isDirectory()) paths.push(...(await walk(path)));
		else paths.push(path);
	}
	return paths;
}

const distPath = new URL('dist', root).pathname;
const generated = await walk(distPath);
const maps = generated.filter(path => path.endsWith('.map'));
if (maps.length > 0) throw new Error(`source maps must not ship: ${maps.join(', ')}`);
console.log(`Package contents validated: ${generated.length} generated files, no source maps`);
