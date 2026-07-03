const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const { batches } = require("./urls");

const MAX_PAGES = 100;
const SITE_CONCURRENCY = 3; // websites crawled in parallel
const PAGE_CONCURRENCY = 3; // pages per website in parallel

const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36";

function sanitizeFilename(url) {
  return url
    .replace(/^https?:\/\//, "")
    .replace(/[\/:?&=#]+/g, "_")
    .slice(0, 200);
}

function normalizeUrl(url) {
  try {
    //should skip .gov
    //yelp / healthgrades / zocdoc / ratemds / opencare / 1800dentist
    //dentaltown
    //directory

    const u = new URL(url);
    u.hash = "";
    ["utm_source", "utm_medium", "utm_campaign", "fbclid", "gclid"].forEach(p =>
      u.searchParams.delete(p)
    );
    if (
      u.hostname.includes("facebook") ||
      u.hostname.endsWith(".gov") ||
      u.hostname.includes("yelp") ||
      u.hostname.includes("healthgrades") ||
      u.hostname.includes("zocdoc") ||
      u.hostname.includes("ratemds") ||
      u.hostname.includes("opencare") ||
      u.hostname.includes("1800dentist") ||
      u.hostname.includes("dentaltown") ||
      u.hostname.includes("directory")
    ) {
      return null;
    }
    return u.toString().replace(/\/$/, "");
  } catch {
    return null;
  }
}

function isInternalLink(link, domain) {
  try {
    return new URL(link).hostname === domain;
  } catch {
    return false;
  }
}

function shouldSkipUrl(url) {
  const lower = url.toLowerCase();
  const parts = new URL(url).pathname.split("/").filter(Boolean);
  if (parts.includes("blog")) return true;
  if (lower.endsWith(".jpg") || lower.endsWith(".jpeg") || lower.endsWith(".pdf")) return true;
  return false;
}

// Run fn(item) for each item with at most `limit` in flight at once
async function runWithConcurrency(items, limit, fn) {
  const executing = new Set();
  for (const item of items) {
    const p = Promise.resolve()
      .then(() => fn(item))
      .finally(() => executing.delete(p));
    executing.add(p);
    if (executing.size >= limit) await Promise.race(executing);
  }
  await Promise.allSettled([...executing]);
}

async function crawlWebsite(browser, startUrl) {
  const normalizedStart = normalizeUrl(startUrl);
  if (!normalizedStart) return;

  const domain = new URL(startUrl).hostname;
  const siteFolder = path.join("scrapedDentists", domain.replace(/^www\./, ""));
  fs.mkdirSync(siteFolder, { recursive: true });

  const context = await browser.newContext({ userAgent: UA });

  const visited = new Set([normalizedStart]);
  const queue = [normalizedStart];
  const inFlight = new Set();

  console.log(`\n==============================`);
  console.log(`Starting: ${startUrl}`);
  console.log(`==============================`);

  async function processUrl(page, url) {
    const filename = sanitizeFilename(url) + ".html";
    const filePath = path.join(siteFolder, filename);

    if (fs.existsSync(filePath)) {
      console.log(`Skip (exists): ${filename}`);
      return;
    }

    await page.goto(url, { waitUntil: "load", timeout: 30000 });
    await page.waitForTimeout(1000);

    const html = await page.content();
    fs.writeFileSync(filePath, html, "utf8");
    console.log(`Saved: ${filename}`);

    const links = await page.$$eval("a", anchors =>
      anchors.map(a => a.href).filter(Boolean)
    );

    for (const link of links) {
      const norm = normalizeUrl(link);
      if (
        norm &&
        isInternalLink(norm, domain) &&
        !visited.has(norm) &&
        !shouldSkipUrl(norm) &&
        visited.size < MAX_PAGES
      ) {
        visited.add(norm);
        queue.push(norm);
      }
    }
  }

  async function worker() {
    const page = await context.newPage();
    try {
      while (visited.size <= MAX_PAGES) {
        const url = queue.shift();

        if (!url) {
          if (inFlight.size > 0) {
            await new Promise(r => setTimeout(r, 100));
            continue;
          }
          break;
        }

        inFlight.add(url);
        try {
          await processUrl(page, url);
        } catch (err) {
          console.log(`Failed: ${url}: ${err.message}`);
        } finally {
          inFlight.delete(url);
        }
      }
    } finally {
      await page.close();
    }
  }

  await Promise.all(Array.from({ length: PAGE_CONCURRENCY }, worker));
  await context.close();

  console.log(`\nFinished: ${startUrl} | Pages: ${visited.size}`);
}

async function main() {
  const batchNum = parseInt(process.env.BATCH_NUM, 10);
  if (!batchNum || !batches[batchNum] || batches[batchNum].length === 0) {
    console.log(`Batch ${batchNum} is empty or out of range — nothing to do.`);
    process.exit(0);
  }

  const urls = batches[batchNum];
  console.log(`Running batch ${batchNum} — ${urls.length} sites`);

  const browser = await chromium.launch({ headless: true });

  fs.mkdirSync("scrapedDentists", { recursive: true });
  fs.mkdirSync("failures", { recursive: true });
  const failuresPath = path.join("failures", `batch-${batchNum}.txt`);

  await runWithConcurrency(urls, SITE_CONCURRENCY, url => {
    return crawlWebsite(browser, url).catch(err => {
      console.log(`\nError with site: ${url}: ${err.message}`);
      fs.appendFileSync(failuresPath, url + "\n");
    });
  });

  await browser.close();
  console.log("\nBATCH COMPLETE");
}

main();
