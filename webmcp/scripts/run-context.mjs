#!/usr/bin/env node

import { readFile } from 'node:fs/promises';

import {
  conformanceLevel,
  contextFromJSON,
  contextToJSON,
  decodeContext,
  encodeContext,
  SITUATIONAL_SPECS,
} from '../dist/extensions/context.js';

const [path] = process.argv.slice(2);
if (!path) throw new Error('usage: run-context.mjs <fixture-case.json>');

const vector = JSON.parse(await readFile(path, 'utf8'));
if (typeof vector !== 'object' || vector === null || Array.isArray(vector)) {
  throw new TypeError('fixture case must be an object');
}

const context =
  typeof vector.wire_input === 'string'
    ? decodeContext(vector.wire_input)
    : contextFromJSON(vector.input);
const wire = encodeContext(context);
const situational = Object.keys(context.situational).filter(
  (dim) => (context.situational[dim] ?? []).length > 0,
);
const personal = Object.keys(context.personal);
const result = {
  wire,
  has_any: situational.length > 0 || personal.length > 0,
  has_situational: situational.length > 0,
  has_personal: personal.length > 0,
  has_vep_0004: situational.some((dim) => SITUATIONAL_SPECS[dim].isVep0004),
  conformance_level: conformanceLevel(context),
  roundtrip: contextToJSON(decodeContext(wire)),
};
process.stdout.write(`${JSON.stringify(result)}\n`);
