// 地図描画スモーク(T-044)。loop_011 の再発防止:
//   1. 地図コンテナの実高さ > 300px(高さ 0 バグの検出)
//   2. マーカー数 = sites.geojson の Feature 数
//   3. pageerror(未捕捉例外)ゼロ
// GSI タイルの取得成否には依存しない(console エラーは警告表示のみ、CI フレーク回避)。
// 前提: `npx next build` 済みの out/ が存在すること。
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const OUT = join(fileURLToPath(new URL(".", import.meta.url)), "..", "out");
const MIME = {
  ".html": "text/html", ".js": "text/javascript", ".css": "text/css",
  ".json": "application/json", ".geojson": "application/geo+json",
  ".png": "image/png", ".svg": "image/svg+xml", ".woff2": "font/woff2",
};

const server = createServer(async (req, res) => {
  let path = decodeURIComponent(new URL(req.url, "http://x").pathname);
  if (path.endsWith("/")) path += "index.html";
  try {
    const body = await readFile(join(OUT, path));
    res.writeHead(200, { "content-type": MIME[extname(path)] ?? "application/octet-stream" });
    res.end(body);
  } catch {
    res.writeHead(404).end();
  }
});
await new Promise((ok) => server.listen(0, ok));
const base = `http://localhost:${server.address().port}`;

const expected = JSON.parse(await readFile(join(OUT, "data", "sites.geojson"), "utf-8")).features.length;
const minHeight = Number(process.env.SMOKE_MIN_HEIGHT ?? 300);

const browser = await chromium.launch({ args: ["--no-sandbox"] });
const page = await (await browser.newContext({ viewport: { width: 1200, height: 800 } })).newPage();
const pageErrors = [];
const consoleErrors = [];
page.on("pageerror", (e) => pageErrors.push(e.message));
page.on("console", (m) => { if (m.type() === "error") consoleErrors.push(m.text()); });

await page.goto(base, { waitUntil: "networkidle", timeout: 60000 });
await page.waitForSelector(".marker", { timeout: 15000 }).catch(() => {});
const mapH = (await page.locator(".map").boundingBox())?.height ?? 0;
const markers = await page.locator(".marker").count();
await browser.close();
server.close();

const failures = [];
if (mapH < minHeight) failures.push(`地図コンテナ高さ ${mapH}px < ${minHeight}px(高さ 0 バグの兆候)`);
if (markers !== expected) failures.push(`マーカー ${markers} 個 ≠ Feature ${expected} 件`);
if (pageErrors.length) failures.push(`pageerror ${pageErrors.length} 件: ${pageErrors[0]}`);

if (consoleErrors.length) console.warn(`⚠ console エラー ${consoleErrors.length} 件(タイル取得等の可能性、警告のみ):`, consoleErrors[0]);
if (failures.length) {
  console.error("map-smoke 不合格:");
  for (const f of failures) console.error("  ✗ " + f);
  process.exit(1);
}
console.log(`map-smoke 合格: 高さ ${mapH}px / マーカー ${markers} = Feature ${expected} / pageerror 0`);
