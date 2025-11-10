import fs from "fs";
import { execSync } from "child_process";
import fetch from "node-fetch";
import path from "path";

const municipalities = JSON.parse(
  fs.readFileSync("./municipalities.json", "utf-8")
);

const lighthouseOutputDir = "../evidence/lighthouse/";
const lighthouseRunsDir = "../evidence/lighthouse/runs/";
const hostingOutputDir = "../evidence/hosting/";

if (!fs.existsSync(lighthouseOutputDir))
  fs.mkdirSync(lighthouseOutputDir, { recursive: true });
if (!fs.existsSync(lighthouseRunsDir))
  fs.mkdirSync(lighthouseRunsDir, { recursive: true });
if (!fs.existsSync(hostingOutputDir))
  fs.mkdirSync(hostingOutputDir, { recursive: true });

function median(arr) {
  const nums = arr
    .filter((v) => typeof v === "number" && !Number.isNaN(v))
    .sort((a, b) => a - b);
  if (nums.length === 0) return undefined;
  const mid = Math.floor(nums.length / 2);
  return nums.length % 2 ? nums[mid] : (nums[mid - 1] + nums[mid]) / 2;
}

function getAuditNumeric(run, id) {
  return run?.audits?.[id]?.numericValue;
}

async function auditSite(url) {
  const domain = url.replace(/^https?:\/\//, "").replace(/[\/:]/g, "_");

  // 1) Run multiple cold Lighthouse runs
  const NUM_RUNS = 3;
  const runFiles = [];
  for (let i = 1; i <= NUM_RUNS; i++) {
    const runFile = `${lighthouseRunsDir}${domain}_run${i}.json`;
    try {
      execSync(
        `npx lighthouse ${url} --output=json --output-path=${runFile} --chrome-flags="--headless" --quiet`,
        { stdio: "inherit" }
      );
      runFiles.push(runFile);
    } catch (e) {
      console.error(`Lighthouse run ${i} failed for ${url}:`, e.message);
    }
  }

  // 2) Aggregate medians per metric across runs
  const runs = runFiles
    .filter((f) => fs.existsSync(f))
    .map((f) => JSON.parse(fs.readFileSync(f, "utf-8")));

  if (runs.length === 0) {
    console.error(`No successful Lighthouse runs for ${url}`);
  } else {
    const perfScores = runs.map((r) => r?.categories?.performance?.score);
    const fcpVals = runs.map((r) =>
      getAuditNumeric(r, "first-contentful-paint")
    );
    const lcpVals = runs.map((r) =>
      getAuditNumeric(r, "largest-contentful-paint")
    );
    const speedVals = runs.map((r) => getAuditNumeric(r, "speed-index"));
    const bytesVals = runs.map((r) => getAuditNumeric(r, "total-byte-weight"));
    const reqCounts = runs.map((r) => {
      const items = r?.audits?.["network-requests"]?.details?.items;
      return Array.isArray(items) ? items.length : undefined;
    });

    const medPerf = median(perfScores);
    const medFcp = median(fcpVals);
    const medLcp = median(lcpVals);
    const medSpeed = median(speedVals);
    const medBytes = median(bytesVals);
    const medReqs = Math.round(median(reqCounts) ?? 0);

    // Choose the run whose request count is closest to the median
    const reqItemsPerRun = runs.map(
      (r) => r?.audits?.["network-requests"]?.details?.items || []
    );
    const reqLens = reqItemsPerRun.map((items) =>
      Array.isArray(items) ? items.length : 0
    );
    let idx = 0;
    if (reqLens.length) {
      const target = medReqs || Math.round(median(reqLens) || 0);
      let bestDiff = Infinity;
      for (let i = 0; i < reqLens.length; i++) {
        const d = Math.abs(reqLens[i] - target);
        if (d < bestDiff) {
          bestDiff = d;
          idx = i;
        }
      }
    }
    const chosenItems = Array.isArray(reqItemsPerRun[idx])
      ? reqItemsPerRun[idx]
      : [];

    // Build synthesized report (keep real network-requests)
    const synthesized = JSON.parse(JSON.stringify(runs[0]));
    synthesized.requestedUrl = runs[0]?.requestedUrl || url;
    synthesized.finalUrl = runs[0]?.finalUrl || url;

    if (!synthesized.categories) synthesized.categories = {};
    if (!synthesized.categories.performance)
      synthesized.categories.performance = {};
    if (typeof medPerf === "number")
      synthesized.categories.performance.score = medPerf;

    if (!synthesized.audits) synthesized.audits = {};
    if (!synthesized.audits["first-contentful-paint"])
      synthesized.audits["first-contentful-paint"] = {};
    if (!synthesized.audits["largest-contentful-paint"])
      synthesized.audits["largest-contentful-paint"] = {};
    if (!synthesized.audits["speed-index"])
      synthesized.audits["speed-index"] = {};
    if (!synthesized.audits["total-byte-weight"])
      synthesized.audits["total-byte-weight"] = {};
    if (!synthesized.audits["network-requests"])
      synthesized.audits["network-requests"] = { details: { items: [] } };
    if (!synthesized.audits["network-requests"].details)
      synthesized.audits["network-requests"].details = {};

    if (typeof medFcp === "number")
      synthesized.audits["first-contentful-paint"].numericValue = medFcp;
    if (typeof medLcp === "number")
      synthesized.audits["largest-contentful-paint"].numericValue = medLcp;
    if (typeof medSpeed === "number")
      synthesized.audits["speed-index"].numericValue = medSpeed;
    if (typeof medBytes === "number")
      synthesized.audits["total-byte-weight"].numericValue = medBytes;

    // Keep the chosen run’s real requests so exporter can sum JSBytes
    synthesized.audits["network-requests"].details.items = chosenItems;

    const lighthouseFile = `${lighthouseOutputDir}${domain}.json`;
    fs.writeFileSync(lighthouseFile, JSON.stringify(synthesized, null, 2));
    console.log(
      `Saved synthesized median report for ${url} -> ${lighthouseFile}`
    );
  }

  // 3. Check for carbon.txt
  try {
    const carbonRes = await fetch(`${url}/carbon.txt`);
    if (carbonRes.ok) {
      const carbonTxt = await carbonRes.text();
      fs.writeFileSync(`${hostingOutputDir}${domain}_carbon.txt`, carbonTxt);
      console.log(`carbon.txt found for ${url}`);
    } else {
      console.log(`No carbon.txt for ${url}`);
    }
  } catch (e) {
    console.error(`carbon.txt check failed for ${url}:`, e.message);
  }

  try {
    // derive host without protocol
    const host = url.replace(/^https?:\/\//, "").replace(/\/+$/, "");
    const apiUrl = `https://api.thegreenwebfoundation.org/greencheck/${host}`;
    const greenRes = await fetch(apiUrl);
    if (greenRes.ok) {
      const greenJson = await greenRes.json();
      fs.writeFileSync(
        `${hostingOutputDir}${host}_greenweb.json`,
        JSON.stringify(greenJson, null, 2)
      );
      console.log(`Green hosting data saved for ${url}`);
    } else {
      console.warn(`Green Web check failed (${greenRes.status}) for ${url}`);
    }
  } catch (e) {
    console.error(`Green Web check error for ${url}:`, e.message);
  }
}

(async () => {
  for (const url of municipalities) {
    await auditSite(url);
  }
})();
