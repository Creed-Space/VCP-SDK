#!/usr/bin/env node

import { readFile } from 'node:fs/promises';

import { negotiate } from '../dist/extensions/negotiation.js';

const [path] = process.argv.slice(2);
if (!path) throw new Error('usage: run-negotiation.mjs <fixture-case.json>');

const value = JSON.parse(await readFile(path, 'utf8'));
if (typeof value !== 'object' || value === null || Array.isArray(value)) {
  throw new TypeError('fixture case must be an object');
}
const result = negotiate(value.client_hello, value.server_capabilities);
process.stdout.write(`${JSON.stringify(result)}\n`);
