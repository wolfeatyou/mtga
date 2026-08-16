#!/usr/bin/env bun
/**
 * Локальный просмотрщик артефактов скилла.
 *
 *     bun ~/.claude/skills/mtg-draft-helper/serve.ts [порт]     # по умолчанию 8787
 *
 * Зачем: Chrome не открывает file://, а всё, что делает скилл, лежит локально — HTML-читшиты
 * сетов, replay-отчёты партий, атлас архетипов, листы колод, файлы знаний.
 *
 * Слушает ТОЛЬКО 127.0.0.1. Отдаёт исключительно файлы внутри директории скилла:
 * путь резолвится и проверяется на выход за корень, так что ../ наружу не уводит.
 *
 * Кодировка: Bun.file() сам ставит charset=utf-8 для текстовых типов, но .md/.txt он
 * отдаёт как application/octet-stream (браузер их СКАЧИВАЕТ), поэтому тип задаётся явно.
 * Кэш выключен целиком: файлы правятся во время работы, и подсунуть старую версию —
 * ровно тот отказ, из-за которого кракозябры пережили починку заголовков (16.08.2026).
 */
import { file } from "bun";
import { readdir, stat } from "node:fs/promises";
import { join, resolve, extname, basename } from "node:path";

const HERE = import.meta.dir;
const PORT = Number(Bun.argv[2] ?? 8787);

const TYPES: Record<string, string> = {
  ".html": "text/html", ".css": "text/css", ".js": "text/javascript",
  ".json": "application/json", ".svg": "image/svg+xml",
  ".md": "text/plain", ".txt": "text/plain", ".log": "text/plain", ".py": "text/plain",
  ".png": "image/png", ".jpg": "image/jpeg", ".gif": "image/gif",
};
const typeOf = (p: string) => {
  const t = TYPES[extname(p).toLowerCase()] ?? "text/plain";
  return t.startsWith("text/") || t === "application/json" || t === "text/javascript"
    ? `${t}; charset=utf-8` : t;
};

const GROUPS: [string, (f: string) => boolean][] = [
  ["Страницы и читшиты", f => f.endsWith(".html")],
  ["Листы колод",        f => f.endsWith(".txt") && (f.includes("deck") || f.includes("my_deck"))],
  ["Знания о сете",      f => f.endsWith(".md")],
];

const esc = (s: string) => s.replace(/[&<>"]/g, c =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]!));

async function index() {
  const names = (await readdir(HERE)).filter(f => !f.startsWith("."));
  const sizes = new Map<string, number>();
  for (const f of names) {
    const s = await stat(join(HERE, f)).catch(() => null);
    if (s?.isFile()) sizes.set(f, s.size);
  }
  const sections = GROUPS.map(([title, pred]) => {
    const picked = [...sizes.keys()].filter(pred).sort();
    if (!picked.length) return "";
    const items = picked.map(f =>
      `<li><a href="/${encodeURIComponent(f)}">${esc(f)}</a>` +
      `<span>${Math.max(1, Math.round(sizes.get(f)! / 1024))} КБ</span></li>`).join("");
    return `<section><h2>${esc(title)}</h2><ul>${items}</ul></section>`;
  }).join("");

  return new Response(`<!doctype html><meta charset="utf-8">
<title>MTG draft helper — локально</title>
<style>
 :root{color-scheme:light dark}
 body{font:15px/1.5 -apple-system,system-ui,sans-serif;max-width:820px;margin:40px auto;padding:0 20px}
 h1{font-size:22px;margin:0 0 4px} p.sub{color:#888;margin:0 0 28px;font-size:13px}
 h2{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:#888;margin:26px 0 8px;font-weight:600}
 ul{list-style:none;margin:0;padding:0}
 li{display:flex;justify-content:space-between;gap:16px;padding:7px 0;border-bottom:1px solid rgba(128,128,128,.22)}
 li span{color:#888;font-size:12px;font-variant-numeric:tabular-nums}
 a{text-decoration:none} a:hover{text-decoration:underline}
</style>
<h1>MTG draft helper</h1>
<p class="sub">${esc(HERE)} · порт ${PORT} · только 127.0.0.1 · bun ${Bun.version}</p>
${sections}`, { headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" } });
}

const server = Bun.serve({
  hostname: "127.0.0.1",
  port: PORT,
  async fetch(req) {
    const path = decodeURIComponent(new URL(req.url).pathname);
    if (path === "/" || path === "/index.html") return index();

    // никаких выходов за корень: резолвим и сверяем префикс
    const target = resolve(HERE, "." + path);
    if (target !== HERE && !target.startsWith(HERE + "/"))
      return new Response("нельзя выходить за корень", { status: 403 });

    const f = file(target);
    if (!(await f.exists()))
      return new Response(`нет файла: ${esc(basename(target))}`, {
        status: 404, headers: { "Content-Type": "text/plain; charset=utf-8" } });

    return new Response(f, { headers: {
      "Content-Type": typeOf(target),
      "Cache-Control": "no-store",     // файлы правятся на ходу — старую версию не отдаём
    }});
  },
});

console.log(`→ http://localhost:${server.port}/   (Ctrl+C чтобы остановить)`);
console.log(`   корень: ${HERE}`);
