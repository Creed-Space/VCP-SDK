/** Parse JSON while rejecting duplicate object keys and hostile resource use. */

const DEFAULT_MAX_BYTES = 16 * 1024 * 1024;
const DEFAULT_MAX_DEPTH = 512;
const JSON_NUMBER = /-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/y;

export function parseStrictJson(
  text,
  { label = 'JSON input', maxBytes = DEFAULT_MAX_BYTES, maxDepth = DEFAULT_MAX_DEPTH } = {},
) {
  if (typeof text !== 'string') throw new TypeError(`${label} must be text`);
  if (Buffer.byteLength(text, 'utf8') > maxBytes) {
    throw new RangeError(`${label} exceeds ${maxBytes} UTF-8 bytes`);
  }

  let index = 0;
  const fail = (message) => {
    throw new SyntaxError(`${label}: ${message} at offset ${index}`);
  };
  const whitespace = () => {
    while (index < text.length && /[\t\n\r ]/.test(text[index])) index += 1;
  };
  const string = () => {
    if (text[index] !== '"') fail('expected string');
    const start = index;
    index += 1;
    while (index < text.length) {
      const character = text[index];
      if (character === '"') {
        index += 1;
        return JSON.parse(text.slice(start, index));
      }
      if (character === '\\') {
        index += 1;
        if (index >= text.length) fail('unterminated escape');
        if (text[index] === 'u') {
          const digits = text.slice(index + 1, index + 5);
          if (!/^[0-9a-fA-F]{4}$/.test(digits)) fail('invalid Unicode escape');
          index += 5;
          continue;
        }
        if (!/["\\/bfnrt]/.test(text[index])) fail('invalid escape');
        index += 1;
        continue;
      }
      if (character.charCodeAt(0) < 0x20) fail('unescaped control character');
      index += 1;
    }
    fail('unterminated string');
  };

  const value = (depth) => {
    if (depth > maxDepth) throw new RangeError(`${label} exceeds nesting depth ${maxDepth}`);
    whitespace();
    const character = text[index];
    if (character === '{') {
      index += 1;
      whitespace();
      const keys = new Set();
      if (text[index] === '}') {
        index += 1;
        return;
      }
      for (;;) {
        whitespace();
        const key = string();
        if (keys.has(key)) fail(`duplicate object key ${JSON.stringify(key)}`);
        keys.add(key);
        whitespace();
        if (text[index] !== ':') fail("expected ':'");
        index += 1;
        value(depth + 1);
        whitespace();
        if (text[index] === '}') {
          index += 1;
          return;
        }
        if (text[index] !== ',') fail("expected ',' or '}'");
        index += 1;
      }
    }
    if (character === '[') {
      index += 1;
      whitespace();
      if (text[index] === ']') {
        index += 1;
        return;
      }
      for (;;) {
        value(depth + 1);
        whitespace();
        if (text[index] === ']') {
          index += 1;
          return;
        }
        if (text[index] !== ',') fail("expected ',' or ']'");
        index += 1;
      }
    }
    if (character === '"') {
      string();
      return;
    }
    for (const literal of ['true', 'false', 'null']) {
      if (text.startsWith(literal, index)) {
        index += literal.length;
        return;
      }
    }
    JSON_NUMBER.lastIndex = index;
    const number = JSON_NUMBER.exec(text);
    if (number) {
      if (!Number.isFinite(Number(number[0]))) {
        throw new RangeError(`${label} contains a non-finite number at offset ${index}`);
      }
      index += number[0].length;
      return;
    }
    fail('expected JSON value');
  };

  whitespace();
  value(0);
  whitespace();
  if (index !== text.length) fail('unexpected trailing content');
  return JSON.parse(text);
}
