import fs from "node:fs/promises";
import path from "node:path";

const root = path.resolve(process.cwd(), "..", "..");
const urls = JSON.parse(await fs.readFile(path.join(root, "scripts", "municipalities.json"), "utf-8"));

const hostingDir = path.join(root, "evidence", "hosting");
await fs.mkdir(hostingDir, { recursive: true });

for (const url of urls) {
  const domain = new URL(url).hostname;

  // greencheck
  try {
    const apiUrl = `https://api.thegreenwebfoundation.org/greencheck/${domain}`;
    const res = await fetch(apiUrl);
    const payload = res.ok ? await res.json() : { error: true, status: res.status };
    const wrapped = { url, domain, checkedAt: new Date().toISOString(), ...payload };
    await fs.writeFile(path.join(hostingDir, `${domain}_greencheck.json`), JSON.stringify(wrapped, null, 2));
    console.log(`✓ greencheck ${domain}`);
  } catch (e) {
    await fs.writeFile(path.join(hostingDir, `${domain}_greencheck.json`), JSON.stringify({ url, domain, error: e.message }, null, 2));
    console.log(`✗ greencheck ${domain}: ${e.message}`);
  }

  // carbon.txt
  try {
    const ct = await fetch(`https://${domain}/carbon.txt`);
    if (ct.ok) {
      const txt = await ct.text();
      await fs.writeFile(path.join(hostingDir, `${domain}_carbon.txt`), txt, "utf-8");
      console.log(`✓ carbon.txt ${domain}`);
    } else {
      // no file do nothing
      console.log(`- no carbon.txt ${domain}`);
    }
  } catch (e) {
    console.log(`- carbon.txt check failed ${domain}: ${e.message}`);
  }
}