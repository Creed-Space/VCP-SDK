#!/usr/bin/env node

import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const root = resolve(import.meta.dirname, '..');
const temp = mkdtempSync(join(tmpdir(), 'vcp-webmcp-pack-'));
try {
  execFileSync('npm', ['run', 'prepack'], {
    cwd: root,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe']
  });
  const packed = JSON.parse(
    execFileSync('npm', ['pack', '--ignore-scripts', '--json', '--pack-destination', temp], {
      cwd: root,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe']
    })
  )[0];
  assert.equal(packed.name, '@creedspace/vcp-sdk');
  assert.ok(packed.integrity.startsWith('sha512-'));
  const tarball = join(temp, packed.filename);
  execFileSync('tar', ['-xzf', tarball, '-C', temp]);
  const packageJson = JSON.parse(readFileSync(join(temp, 'package', 'package.json'), 'utf8'));
  assert.deepEqual(packageJson.files, ['dist', 'README.md', 'LICENSE']);
  const module = await import(pathToFileURL(join(temp, 'package', 'dist', 'index.js')));
  assert.equal(typeof module.registerVCPTools, 'function');

  const signals = [];
  globalThis.document = {
    modelContext: {
      async registerTool(_tool, options) {
        signals.push(options.signal);
      }
    }
  };
  const registration = await module.registerVCPTools();
  assert.equal(registration.api, 'document');
  assert.ok(registration.registered.length > 0);
  assert.equal(registration.failed.length, 0);
  assert.ok(signals.every((signal) => !signal.aborted));
  registration.cleanup();
  assert.ok(signals.every((signal) => signal.aborted));
  registration.cleanup();
  console.log(
    `Packed WebMCP artifact passed: ${packed.filename}, ${registration.registered.length} tools.`
  );
} finally {
  delete globalThis.document;
  rmSync(temp, { recursive: true, force: true });
}
