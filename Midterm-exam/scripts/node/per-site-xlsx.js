import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import XLSX from 'xlsx';
import { co2 } from '@tgwf/co2';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, '..', '..');

const runsDir = path.join(repoRoot, 'evidence', 'lighthouse', 'runs');
const spreadsheetsDir = path.join(repoRoot, 'evidence', 'spreadsheets', 'per_site');
if (!fs.existsSync(spreadsheetsDir)) fs.mkdirSync(spreadsheetsDir, { recursive: true });

const municipalitiesPath = path.join(repoRoot, 'scripts', 'municipalities.json');
const municipalities = JSON.parse(fs.readFileSync(municipalitiesPath, 'utf-8'));

const metricKeys = [
  { key: 'largest-contentful-paint', name: 'LCP' },
  { key: 'first-contentful-paint', name: 'FCP' },
  { key: 'server-response-time', name: 'TTFB' },
  { key: 'interactive', name: 'TTI' },
  { key: 'total-blocking-time', name: 'TBT' },
  { key: 'cumulative-layout-shift', name: 'CLS' },
  { key: 'speed-index', name: 'SpeedIndex' }
];

function domainKey(url) {
  return url.replace(/^https?:\/\//, '').replace(/[\/:]/g, '_').replace(/\/+$/, '');
}

function readRun(filePath) {
  if (!fs.existsSync(filePath)) return null;
  try { return JSON.parse(fs.readFileSync(filePath, 'utf-8')); } catch { return null; }
}

function getMetric(audits, key) {
  const v = audits?.[key]?.numericValue;
  return typeof v === 'number' ? v : null;
}

function getPerfScore(lhr) {
  const s = lhr?.categories?.performance?.score;
  return typeof s === 'number' ? Math.round(s * 100) : null;
}

function getRequests(lhr) {
  return lhr?.audits?.['network-requests']?.details?.items || [];
}

function sumTransferBytes(lhr) {
  return getRequests(lhr).reduce((sum, it) => sum + (it.transferSize || 0), 0);
}

function median(arr) {
  const a = arr.filter(v => typeof v === 'number' && !Number.isNaN(v)).sort((x, y) => x - y);
  if (!a.length) return null;
  const mid = Math.floor(a.length / 2);
  return a.length % 2 ? a[mid] : (a[mid - 1] + a[mid]) / 2;
}

function buildWorkbookFor(url) {
  const key = domainKey(url);
  const runPaths = [1, 2, 3].map(i => path.join(runsDir, `${key}_run${i}.json`));
  const runs = runPaths.map(readRun).filter(Boolean);
  if (!runs.length) return { url, key, written: false, reason: 'no runs found' };

  const perRunMetrics = runs.map((lhr) => {
    const audits = lhr?.audits || {};
    const m = {};
    metricKeys.forEach(({ key, name }) => { m[name] = getMetric(audits, key); });
    m.PerformanceScore_0_100 = getPerfScore(lhr);
    m.TotalBytes_B = sumTransferBytes(lhr);
    m.Requests = getRequests(lhr).length;
    return m;
  });

  const medians = {};
  Object.keys(perRunMetrics[0]).forEach((metric) => {
    medians[metric] = median(perRunMetrics.map(r => r[metric]));
  });

  const runsSheet = perRunMetrics.map((m, idx) => ({ iteration: idx + 1, ...m }));
  runsSheet.push({ iteration: 'median', ...medians });

  const oneByte = new co2({ model: '1byte' });
  const swd = new co2({ model: 'swd' });

  const perResourceAll = [];
  runs.forEach((lhr, idx) => {
    const items = getRequests(lhr);
    items.forEach((it) => {
      const transfer = it.transferSize || 0;
      perResourceAll.push({
        iteration: idx + 1,
        url: it.url,
        resourceType: it.resourceType || 'other',
        mimeType: it.mimeType || '',
        transferBytes: transfer,
        resourceBytes: it.resourceSize || null,
        CO2_g_transfer_1byte: oneByte.perByte(transfer),
        CO2_g_transfer_swd: swd.perByte(transfer)
      });
    });
  });

  const summaryByType = {};
  perResourceAll.forEach((row) => {
    const type = row.resourceType || 'other';
    if (!summaryByType[type]) summaryByType[type] = { type, requests: 0, transferBytes: 0, resourceBytes: 0 };
    summaryByType[type].requests += 1;
    summaryByType[type].transferBytes += row.transferBytes || 0;
    summaryByType[type].resourceBytes += row.resourceBytes || 0;
  });
  const summaryArr = Object.values(summaryByType);

  const co2Sheet = perRunMetrics.map((run, idx) => ({
    iteration: idx + 1,
    TotalBytes_B: run.TotalBytes_B,
    CO2_g_1byte: oneByte.perByte(run.TotalBytes_B || 0),
    CO2_g_swd: swd.perByte(run.TotalBytes_B || 0)
  }));
  co2Sheet.push({
    iteration: 'median',
    TotalBytes_B: medians.TotalBytes_B,
    CO2_g_1byte: oneByte.perByte(medians.TotalBytes_B || 0),
    CO2_g_swd: swd.perByte(medians.TotalBytes_B || 0)
  });

  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(runsSheet), 'runs');
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(perResourceAll), 'per_resource_all_runs');
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(summaryArr), 'summary_by_type');
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(co2Sheet), 'co2');

  const outPath = path.join(spreadsheetsDir, `${key}.xlsx`);
  XLSX.writeFile(wb, outPath);
  return { url, key, written: true, outPath };
}

async function main() {
  const arg = process.argv[2]; 
  const targets = arg
    ? municipalities.filter(u => domainKey(u).includes(arg) || u.includes(arg))
    : municipalities;

  let ok = 0, skip = 0;
  for (const url of targets) {
    const res = buildWorkbookFor(url);
    if (res.written) {
      ok++;
      console.log(`Workbook saved: ${res.outPath}`);
    } else {
      skip++;
      console.warn(`Skipped (${res.reason}): ${res.key}`);
    }
  }
  console.log(`Per-site XLSX: wrote ${ok}, skipped ${skip}`);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});