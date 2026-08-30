import {mkdir, readFile, writeFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../..');
const comparison = JSON.parse(await readFile(path.join(root, 'evidence/results/comparison.json'), 'utf8'));
const expected = '87c7f191a64e9beb1e55d32ddfa3b67782028aca75720203a4471ba31fad5889';
if (comparison.benchmark_fingerprint !== expected || comparison.case_count !== 18) {
  throw new Error('Frozen evidence does not match the video-approved benchmark.');
}
await mkdir(path.join(here, '../src/data'), {recursive: true});
await writeFile(path.join(here, '../src/data/evidence.json'), JSON.stringify(comparison, null, 2) + '\n');
console.log('Synced frozen evidence:', comparison.benchmark_fingerprint);
