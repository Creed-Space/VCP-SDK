import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const directory = path.join(root, "schemas");
const schemas = fs
  .readdirSync(directory)
  .filter((name) => name.endsWith(".schema.json"))
  .map((name) => path.join(directory, name))
  .sort();

let failed = false;
for (const file of schemas) {
  const label = path.relative(root, file);
  try {
    const schema = JSON.parse(fs.readFileSync(file, "utf8"));
    const ajv = new Ajv2020({ allErrors: true, strict: true });
    addFormats(ajv);
    ajv.compile(schema);
    console.log(`strict schema OK: ${label}`);
  } catch (error) {
    failed = true;
    console.error(`strict schema FAILED: ${label}`);
    console.error(error instanceof Error ? error.message : String(error));
  }
}

if (failed) process.exitCode = 1;
