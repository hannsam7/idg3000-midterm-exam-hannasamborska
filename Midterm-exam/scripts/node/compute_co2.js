import fs from 'fs';
import path from 'path';
import { co2 } from '@tgwf/co2'; 
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const lighthouseDir = path.resolve(__dirname, '..', 'evidence', 'lighthouse');
const hostingDir = path.resolve(__dirname, '..', 'evidence', 'hosting');
if (!fs.existsSync(hostingDir)) fs.mkdirSync(hostingDir, { recursive: true });

const files = fs.readdirSync(lighthouseDir).filter(f => f.endsWith('.json'));

const swd = new co2({ model: 'swd' });
const onebyte = new co2({ model: '1byte' });

let wrote = 0, skipped = 0;
for (const fname of files) {
  const fpath = path.join(lighthouseDir, fname);
  try {
    const data = JSON.parse(fs.readFileSync(fpath, 'utf-8'));
    const url = data.requestedUrl || '';
    const bytes = data?.audits?.['total-byte-weight']?.numericValue;

    if (typeof bytes !== 'number') {
      console.warn(`Skip (no total-byte-weight): ${fname}`);
      skipped++;
      continue;
    }

    const swd_g = swd.perByte(bytes);
    const onebyte_g = onebyte.perByte(bytes);

    const domain = path.basename(fname, '.json');
    const out = { url, bytes, co2_swd_g: swd_g, co2_onebyte_g: onebyte_g };
    const outPath = path.join(hostingDir, `${domain}_co2.json`);
    fs.writeFileSync(outPath, JSON.stringify(out, null, 2));
    wrote++;
  } catch (e) {
    console.error(`Failed for ${fname}:`, e.message);
  }
}
console.log(`CO2 files written: ${wrote}, skipped: ${skipped}, dir: ${hostingDir}`);