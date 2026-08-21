import assert from 'node:assert/strict';
import test from 'node:test';

import { parseStrictJson } from './strict_json.mjs';

test('accepts repeated key names in distinct objects', () => {
  assert.deepEqual(parseStrictJson('{"left":{"id":1},"right":{"id":2}}'), {
    left: { id: 1 },
    right: { id: 2 },
  });
});

test('rejects duplicate keys at any object depth', () => {
  assert.throws(() => parseStrictJson('{"id":1,"id":2}'), /duplicate object key "id"/);
  assert.throws(
    () => parseStrictJson('{"items":[{"safe":true,"safe":false}]}'),
    /duplicate object key "safe"/,
  );
});

test('detects escaped and literal spellings of the same key', () => {
  assert.throws(() => parseStrictJson('{"\\u0069d":1,"id":2}'), /duplicate object key "id"/);
});

test('bounds input bytes and nesting before parser exhaustion', () => {
  assert.throws(
    () => parseStrictJson('{"value":"éé"}', { maxBytes: 10 }),
    /exceeds 10 UTF-8 bytes/,
  );
  const nested = '['.repeat(514) + '0' + ']'.repeat(514);
  assert.throws(() => parseStrictJson(nested), /exceeds nesting depth 512/);
});

test('rejects a syntactically valid exponent that overflows the runtime number type', () => {
  assert.throws(() => parseStrictJson('{"maximum":1e999}'), /contains a non-finite number/);
});

test('handles a large flat numeric array without rescanning the remaining input', () => {
  const values = Array.from({ length: 100_000 }, (_, index) => index % 10);
  assert.deepEqual(parseStrictJson(JSON.stringify(values)), values);
});
