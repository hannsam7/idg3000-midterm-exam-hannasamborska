const fs = require('fs');
const { execSync } = require('child_process');
const fetch = require('node-fetch');

const municipalities = require('./municipalities.json');
const lighthouseOutputDir = '../evidence/lighthouse/';
const hostingOutputDir = '../evidence/hosting/';

if (!fs.existsSync(lighthouseOutputDir)) fs.mkdirSync(lighthouseOutputDir, { recursive: true });
if (!fs.existsSync(hostingOutputDir)) fs.mkdirSync(hostingOutputDir, { recursive: true });

async function auditSite(url) {
  const domain = url.replace(/^https?:\/\//, '').replace(/[\/:]/g, '_');
  // 1. Run Lighthouse
  const lighthouseFile = `${lighthouseOutputDir}${domain}.json`;
  try {
    execSync(`npx lighthouse ${url} --output=json --output-path=${lighthouseFile} --chrome-flags="--headless"`);
    console.log(`Lighthouse done for ${url}`);
  } catch (e) {
    console.error(`Lighthouse failed for ${url}:`, e.message);
  }

  // 2. Green Web Foundation API
  try {
    const apiRes = await fetch(`https://api.thegreenwebfoundation.org/greencheck/${domain}`);
    const apiJson = await apiRes.json();
    fs.writeFileSync(`${hostingOutputDir}${domain}_greenweb.json`, JSON.stringify(apiJson, null, 2));
    console.log(`Green Web Check done for ${url}`);
  } catch (e) {
    console.error(`Green Web Check failed for ${url}:`, e.message);
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
}

(async () => {
  for (const url of municipalities) {
    await auditSite(url);
  }
})();