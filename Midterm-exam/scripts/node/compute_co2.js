import fs from 'fs';
import path from 'path';
import { co2 } from '@tgwf/co2';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '..', '..'); // go up to Midterm-exam
const lighthouseDir = path.join(repoRoot, 'evidence', 'lighthouse');
const hostingDir = path.join(repoRoot, 'evidence', 'hosting');

if (!fs.existsSync(hostingDir)) fs.mkdirSync(hostingDir, { recursive: true });
if (!fs.existsSync(lighthouseDir)) {
  console.error('Lighthouse folder not found:', lighthouseDir);
  process.exit(1);
}

const files = fs.readdirSync(lighthouseDir).filter(f => f.endsWith('.json'));
const swd = new co2({ model: 'swd' });
const onebyte = new co2({ model: '1byte' });

let wrote = 0, skipped = 0;
for (const fname of files) {
  const fpath = path.join(lighthouseDir, fname);
  try {
    const data = JSON.parse(fs.readFileSync(fpath, 'utf-8'));
    const bytes = data?.audits?.['total-byte-weight']?.numericValue;
    if (typeof bytes !== 'number') { skipped++; continue; }
    const domain = path.basename(fname, '.json');
    const out = {
      url: data.requestedUrl || '',
      bytes,
      co2_swd_g: swd.perByte(bytes),
      co2_onebyte_g: onebyte.perByte(bytes)
    };
    fs.writeFileSync(path.join(hostingDir, `${domain}_co2.json`), JSON.stringify(out, null, 2));
    wrote++;
  } catch (e) {
    console.error('CO2 calc failed for', fname, e.message);
    skipped++;
  }
}
console.log(`CO2: wrote ${wrote}, skipped ${skipped}`);