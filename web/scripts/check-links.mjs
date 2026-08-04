// ビルド後リンク検査(HC-007): out/**/*.html の内部 href/src が実ファイルに解決するか。
// 破れていれば exit 1 で build を失敗させる(dev サーバで再現しない経路欠陥の機械検査)
import { readdirSync, readFileSync, statSync, existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const OUT = resolve(dirname(fileURLToPath(import.meta.url)), "..", "out");

function* htmlFiles(dir) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) yield* htmlFiles(p);
    else if (name.endsWith(".html")) yield p;
  }
}

const RE_ATTR = /(?:href|src)="([^"]+)"/g;
let errors = 0;
let checked = 0;

for (const file of htmlFiles(OUT)) {
  const html = readFileSync(file, "utf-8");
  for (const m of html.matchAll(RE_ATTR)) {
    const url = m[1];
    if (/^(https?:|mailto:|#|data:)/.test(url)) continue;
    const clean = url.split(/[?#]/)[0];
    if (!clean) continue;
    const base = clean.startsWith("/") ? OUT : dirname(file);
    const target = resolve(base, clean.startsWith("/") ? clean.slice(1) : clean);
    checked += 1;
    const ok =
      existsSync(target) ||
      existsSync(`${target}.html`) ||
      existsSync(join(target, "index.html"));
    if (!ok) {
      errors += 1;
      console.error(`BROKEN: ${url}  (in ${file.slice(OUT.length + 1)})`);
    }
  }
}

console.log(`check-links: ${checked} 内部リンク検査, 破れ ${errors} 件`);
process.exit(errors ? 1 : 0);
