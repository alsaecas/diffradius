import { cp, mkdir, rm, access } from 'node:fs/promises';
import { constants } from 'node:fs';

const out = new URL('../dist/', import.meta.url);
const demo = new URL('../demo/', import.meta.url);
const evidence = new URL('../evidence/', import.meta.url);
await rm(out, { recursive: true, force: true });
await mkdir(out, { recursive: true });
await cp(demo, out, { recursive: true });
try {
  await access(evidence, constants.R_OK);
  await cp(evidence, new URL('./evidence/', out), { recursive: true });
} catch {
  // Evidence is intentionally absent until the live benchmark has been frozen.
}
