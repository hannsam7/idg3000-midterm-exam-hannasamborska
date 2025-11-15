import fs from "node:fs/promises";
import path from "node:path";
import puppeteer from "puppeteer";

const repoRoot = path.resolve(process.cwd(), "..", ".."); // -> Midterm-exam
const evidenceDir = path.join(repoRoot, "evidence");
const hostingDir = path.join(evidenceDir, "hosting");
const shotsDir = path.join(hostingDir, "screenshots");
await fs.mkdir(shotsDir, { recursive: true });

// Load domains and corresponding greencheck JSON
const urls = JSON.parse(await fs.readFile(path.join(repoRoot, "scripts", "municipalities.json"), "utf-8"));
const items = [];
for (const url of urls) {
  const domain = new URL(url).hostname;
  const gcPath = path.join(hostingDir, `${domain}_greencheck.json`);
  let provider = null;
  try {
    const gc = JSON.parse(await fs.readFile(gcPath, "utf-8"));
    provider = gc.hostedby || gc.hostedby_name || null;
  } catch {}
  items.push({ domain, provider });
}

const browser = await puppeteer.launch({ headless: "new", args: ["--no-sandbox"] });
const page = await browser.newPage();
await page.setViewport({ width: 1366, height: 900 });

for (const { domain, provider } of items) {
  // 1) Screenshot the Green Web Check web page
  const gwcUrl = `https://www.thegreenwebfoundation.org/green-web-check/?url=${encodeURIComponent(domain)}`;
  try {
    await page.goto(gwcUrl, { waitUntil: "networkidle2", timeout: 60000 });
    // Try to close cookie banners if present (best-effort)
    try {
      await page.click('button[aria-label="Accept"], button:has-text("Accept"), button:has-text("I agree")', { timeout: 3000 });
    } catch {}
    await page.waitForTimeout(1500);
    await page.screenshot({
      path: path.join(shotsDir, `${domain}_greencheck.png`),
      fullPage: true
    });
    console.log(`✓ screenshot: ${domain}_greencheck.png`);
  } catch (e) {
    console.warn(`! greencheck screenshot failed for ${domain}: ${e.message}`);
  }

  // 2) Screenshot the Directory search for provider (if known)
  if (provider) {
    const dirUrl = `https://directory.thegreenwebfoundation.org/search?q=${encodeURIComponent(provider)}`;
    try {
      await page.goto(dirUrl, { waitUntil: "networkidle2", timeout: 60000 });
      await page.waitForTimeout(1500);
      await page.screenshot({
        path: path.join(shotsDir, `${domain}_provider_search.png`),
        fullPage: true
      });
      console.log(`✓ screenshot: ${domain}_provider_search.png`);
    } catch (e) {
      console.warn(`! directory screenshot failed for ${domain} (${provider}): ${e.message}`);
    }
  } else {
    console.log(`- no provider name in greencheck JSON for ${domain}; skipped directory screenshot`);
  }
}

await browser.close();
console.log(`Screenshots in ${shotsDir}`);