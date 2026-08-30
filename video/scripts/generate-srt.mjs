import {mkdir, readFile, writeFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const data = JSON.parse(await readFile(path.join(here, '../src/data/content.json'), 'utf8'));
const stamp = (seconds) => {
  const ms = Math.round(seconds * 1000);
  const h = Math.floor(ms / 3600000);
  const m = Math.floor((ms % 3600000) / 60000);
  const s = Math.floor((ms % 60000) / 1000);
  const z = ms % 1000;
  return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')},${String(z).padStart(3,'0')}`;
};
const srt = data.captions.map((c, i) => `${i + 1}\n${stamp(c.start)} --> ${stamp(c.end)}\n${c.text}\n`).join('\n');
await mkdir(path.join(here, '../out'), {recursive: true});
await writeFile(path.join(here, '../out/diffradius-hackathon-final.srt'), srt);
console.log(`Generated ${data.captions.length} subtitle cues.`);
