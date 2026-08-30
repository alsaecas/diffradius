import {mkdir, readFile, access} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const publicDir = path.join(here, '../public/audio');
const data = JSON.parse(await readFile(path.join(here, '../src/data/content.json'), 'utf8'));
await mkdir(publicDir, {recursive: true});

for (let i = 0; i < data.captions.length; i++) {
  const id = String(i + 1).padStart(2, '0');
  const mp3 = path.join(publicDir, `narration-${id}.mp3`);
  try { await access(mp3); continue; } catch {}
  const aiff = path.join(publicDir, `narration-${id}.aiff`);
  const rate = i === 20 ? '180' : '155';
  const spoken = spawnSync('say', ['-v', 'Samantha', '-r', rate, '-o', aiff, data.captions[i].text], {stdio: 'inherit'});
  if (spoken.status !== 0) throw new Error(`say failed for cue ${id}`);
  const converted = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', aiff, '-codec:a', 'libmp3lame', '-q:a', '3', mp3], {stdio: 'inherit'});
  if (converted.status !== 0) throw new Error(`ffmpeg failed for cue ${id}`);
  spawnSync('rm', [aiff]);
}

const ambient = path.join(publicDir, 'ambient.mp3');
try { await access(ambient); } catch {
  const made = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'sine=frequency=82:duration=282', '-f', 'lavfi', '-i', 'sine=frequency=164:duration=282', '-filter_complex', '[0:a]volume=0.012[a0];[1:a]volume=0.004[a1];[a0][a1]amix=inputs=2,afade=t=in:st=0:d=3,afade=t=out:st=278:d=4', '-codec:a', 'libmp3lame', '-q:a', '5', ambient], {stdio: 'inherit'});
  if (made.status !== 0) throw new Error('ambient generation failed');
}
console.log('Narration and procedural ambient audio ready.');
