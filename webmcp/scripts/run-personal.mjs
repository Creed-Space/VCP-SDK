#!/usr/bin/env node

import { readFile } from 'node:fs/promises';

import {
  computeDecayedIntensity,
  computeLifecycleState,
  DEFAULT_DECAY_CONFIGS,
} from '../dist/extensions/personal.js';

const [path] = process.argv.slice(2);
if (!path) throw new Error('usage: run-personal.mjs <fixture-case.json>');

const vector = JSON.parse(await readFile(path, 'utf8'));
if (typeof vector !== 'object' || vector === null || Array.isArray(vector)) {
  throw new TypeError('fixture case must be an object');
}

function toWire(config) {
  return {
    half_life_seconds: config.halfLifeSeconds,
    baseline: config.baseline,
    reset_on_engagement: config.resetOnEngagement,
    stale_threshold: config.staleThreshold,
    fresh_window_seconds: config.freshWindowSeconds,
  };
}

let result;
if (vector.mode === 'configs') {
  result = {
    decay_configs: Object.fromEntries(
      Object.entries(DEFAULT_DECAY_CONFIGS).map(([name, config]) => [name, toWire(config)]),
    ),
  };
} else {
  const wire = vector.config;
  if (typeof wire !== 'object' || wire === null) throw new TypeError('config must be an object');
  const config = {
    halfLifeSeconds: wire.half_life_seconds,
    baseline: wire.baseline,
    pinned: wire.pinned === true,
    resetOnEngagement: false,
    staleThreshold: wire.stale_threshold,
    freshWindowSeconds: wire.fresh_window_seconds,
  };
  const declaredAt = new Date(0);
  const now = new Date(Math.round(Number(vector.elapsed_seconds) * 1000));
  const declared = Number(vector.declared_intensity);
  const effective = computeDecayedIntensity(declared, declaredAt, config, now);
  result =
    vector.mode === 'lifecycle'
      ? {
          lifecycle_state: computeLifecycleState(declared, declaredAt, config, now),
          effective_intensity: effective,
        }
      : { decayed_intensity: effective };
}
process.stdout.write(`${JSON.stringify(result)}\n`);
