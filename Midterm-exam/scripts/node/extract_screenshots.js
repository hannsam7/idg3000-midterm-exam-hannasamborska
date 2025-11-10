import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const lighthouseDir = path.resolve(__dirname, '..', 'evidence', 'lighthouse');
const outDir = path.resolve(__dirname, '..', 'evidence', 'screenshots');
fs.mkdirSync(outDir, { recursive: true });

const files = fs.readdirSync(lighthouseDir).filter(f => f.endsWith('.json'));
for (const fname of files) {
  const fpath = path.join(lighthouseDir, fname);
  try {
    const data = JSON.parse(fs.readFileSync(fpath, 'utf-8'));
    const dataURI = data?.audits?.['final-screenshot']?.details?.data;
    if (!dataURI || !dataURI.startsWith('data:image/')) {
      console.warn(`No final screenshot in ${fname}`);
      continue;
    }
    const [meta, b64] = dataURI.split(',');
    const ext = meta.includes('image/webp') ? 'webp' : meta.split('/')[1].split(';')[0] || 'png';
    const outName = path.basename(fname, '.json') + `_final.${ext}`;
    fs.writeFileSync(path.join(outDir, outName), Buffer.from(b64, 'base64'));
    console.log(`Saved ${outName}`);
  } catch (e) {
    console.error(`Failed ${fname}:`, e.message);
  }
}