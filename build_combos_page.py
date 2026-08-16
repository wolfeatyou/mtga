#!/usr/bin/env python3
"""Собирает hob_combos.html — связки сета с принтами карт по наведению.

    python3 build_combos_page.py [set]

Источник — <set>_combos.json (его делает связка learn/consensus + мультиагентный разбор,
см. SKILL.md § КАК СКИЛЛ УЧИТСЯ). Принты берутся из общего кэша atlas/imgs.json и
докачиваются в него же, если каких-то карт там нет.

Страница — для человека: посмотреть перед драфтом, свериться после. В живом драфте те же
связки печатает `⚑ СВЯЗКА` (draft_live.combo_banner), ему html не нужен.
"""
import base64, html, io, json, os, re, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "mtg-draft-helper/1.0"}
WIDTH, QUALITY = 400, 72
PAIR_RE = re.compile(r"^([WUBRG]{1,2}|MONO)")


def img_url(card):
    u = card.get("image_uris")
    if not u and card.get("card_faces"):
        u = card["card_faces"][0].get("image_uris")
    return (u or {}).get("normal")


def ensure_images(names, code):
    cache_path = os.path.join(HERE, "atlas", "imgs.json")
    cache = {}
    if os.path.exists(cache_path):
        cache = json.load(open(cache_path, encoding="utf-8"))
    todo = [n for n in names if n not in cache]
    if todo:
        from PIL import Image
        cards = {}
        for c in json.load(open(os.path.join(HERE, f"{code}_set.json"), encoding="utf-8")):
            cards.setdefault(c["name"], c)                      # полное имя
            cards.setdefault(c["name"].split(" //")[0], c)      # и лицевая сторона:
            # в combos имя может прийти в любом виде — «Beorn, Reluctant Host» или
            # «Beorn, Reluctant Host // Till and Tend» (агенты цитируют по-разному)
        print(f"докачиваю принты: {len(todo)}")
        for i, n in enumerate(todo, 1):
            c = cards.get(n)
            url = img_url(c) if c else None
            if not url:
                print(f"  ⚠ нет картинки: {n}")
                continue
            raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
            im = Image.open(io.BytesIO(raw)).convert("RGB")
            if im.width != WIDTH:
                im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, "WEBP", quality=QUALITY, method=6)
            cache[n] = "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()
            print(f"  [{i}/{len(todo)}] {n}")
            time.sleep(0.12)
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        json.dump(cache, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False)
    return {n: cache[n] for n in names if n in cache}



def hub_svg(hub, imgs, esc):
    """Звезда хаба: центр — опорная карта, лучи — её связки.

    Почему звезда, а не общий граф: 65 связок в одном полотне превращаются в спагетти,
    где не видно ни одного факта. Звезда отвечает на конкретный вопрос — «я взял эту карту,
    что она мне открывает» — и толщина луча сразу показывает, какая из связок ходовая.

    Луч интерактивен: наведение показывает принт карты-спутника И механизм связки (правка
    17.08.2026). Без механизма луч сообщал только «эти две карты часто вместе», то есть
    ровно ту статистику, объяснять которую и был весь смысл разбора.
    """
    import math
    links = hub["links"][:7]
    W, H, CX, CY, R = 520, 300, 150, 150, 118
    top = max(l["decks"] for l in links) or 1
    parts = [f'<svg viewBox="0 0 {W} {H}" class="star" role="img" '
             f'aria-label="связки карты {esc(hub["card"])}">']
    n = len(links)
    for i, l in enumerate(links):
        a = math.radians(-70 + (140 * i / max(n - 1, 1)))
        x, y = CX + R * math.cos(a), CY + R * math.sin(a)
        w = 1 + 5 * l["decks"] / top
        label = " + ".join(l["with"])
        # data-c — карта для превью (первый партнёр), data-w — механизм связки
        g = (f'<g class="ray" tabindex="0" role="button" '
             f'data-c="{esc(l["with"][0])}" data-w="{esc(l.get("why", ""))}" '
             f'data-pair="{esc(hub["card"] + " + " + label)}" '
             f'data-n="{l["decks"]}" data-l="{l.get("lift", "")}">')
        parts.append(g)
        # широкая прозрачная линия — чтобы попадать курсором, а не целиться в 2px
        parts.append(f'<line x1="{CX}" y1="{CY}" x2="{x:.1f}" y2="{y:.1f}" class="hit"/>')
        parts.append(f'<line x1="{CX}" y1="{CY}" x2="{x:.1f}" y2="{y:.1f}" '
                     f'stroke-width="{w:.1f}" class="edge"/>')
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" class="node"/>')
        parts.append(f'<text x="{x + 10:.1f}" y="{y + 4:.1f}" class="lbl">'
                     f'{esc(label[:32])}<tspan class="num"> {l["decks"]}</tspan></text>')
        parts.append('</g>')
    parts.append(f'<circle cx="{CX}" cy="{CY}" r="9" class="hub"/>')
    parts.append('</svg>')
    return "".join(parts)


def short_pair(p):
    m = PAIR_RE.match(p or "")
    return m.group(1) if m else (p or "?")[:4]


def main():
    code = (sys.argv[1] if len(sys.argv) > 1 else "hob").lower()
    data = json.load(open(os.path.join(HERE, f"{code}_combos.json"), encoding="utf-8"))
    combos = sorted(data["combos"], key=lambda c: -c["decks"])
    names = sorted({n for c in combos for n in c["cards"]})
    imgs = ensure_images(names, code)

    # Сортировка — по ЧАСТОТЕ, а не по цветам (правка 17.08.2026 по просьбе пользователя).
    # Группировка по парам прятала главное: самые ходовые связки формата разбросаны по
    # разным группам, и «57 колод» стояло рядом с «6 колод» просто потому, что цвета те же.
    # Пара осталась меткой на карточке и фильтром — как способ сузить, а не как порядок.
    combos.sort(key=lambda c: (-c["decks"], -c.get("lift", 0)))
    groups = {}
    for c in combos:
        groups.setdefault(short_pair(c.get("pair")), []).append(c)
    order = sorted(groups, key=lambda k: (-len(groups[k]), k))

    def card_btn(n):
        has = n in imgs
        return (f'<button class="cn{"" if has else " noimg"}" data-c="{html.escape(n)}"'
                f' type="button">{html.escape(n)}</button>')

    hubs = data.get("hubs", [])[:6]
    hub_html = ""
    if hubs:
        cards_html = []
        for h in hubs:
            cards_html.append(f'''<article class="hubcard">
  <div class="hubhd">
    <div>{card_btn(h["card"])}
      <div class="hubsub">{h["deg"]} связок · {h["wdeg"]} колод суммарно · в {h["share"]}% листов</div>
    </div>
    <div class="idx" title="во сколько раз связей больше, чем ожидается от частоты карты">
      <b>&times;{h["ratio"]}</b><span>хаб-индекс</span></div>
  </div>
  {hub_svg(h, imgs, html.escape)}
</article>''')
        hub_html = ('<h2 class="sec">Опорные карты</h2>'
                    '<p class="lede">Карты, вокруг которых связки собираются пучком. Взяв такую, '
                    'открываешь сразу несколько будущих связок — ценность, которой нет ни в GIH, '
                    'ни в частоте. <b>Хаб-индекс</b> отделяет узловую карту от просто популярной: '
                    'у <i>Eagle\'s Rescue</i> всего 7% листов, но индекс 8.6 — она почти всегда '
                    'в связке; у <i>Goblin Plate Mail</i> 34% листов и индекс 1.8 — она частая, '
                    'но не узловая. Толщина луча — сколько колод содержат эту связку; наведите на луч, чтобы увидеть принт карты и <b>механизм связки</b>.</p>'
                    '<div class="hubgrid">' + "".join(cards_html) + '</div>'
                    '<h2 class="sec">Все связки по частоте</h2>')
    top = max(x["decks"] for x in combos)
    rows = ['<div class="grid" id="grid">']
    for i, c in enumerate(combos, 1):
        p = c.get("p")
        pstr = ("p&lt;1e-10" if p and p < 1e-10 else f"p={p:.2g}") if p else ""
        g = short_pair(c.get("pair"))
        rows.append(f'''<article class="combo" data-pair="{html.escape(g)}">
  <div class="hd"><span class="rank">{i}</span><span class="tag">{html.escape(g)}</span>
    <span class="freq"><b>{c["decks"]}</b> колод</span></div>
  <div class="cards">{" <span class='plus'>+</span> ".join(card_btn(n) for n in c["cards"])}</div>
  <p class="why">{html.escape(c.get("why", ""))}</p>
  <div class="meta">
    <span class="bar" title="доля от самой частой связки"><i style="--v:{round(c["decks"] / top * 100)}%"></i></span>
    <b>&times;{c["lift"]}</b><span class="u">чаще случайного</span>
    <span class="p">{pstr}</span>
  </div>
</article>''')
    rows.append('</div>')

    n_decks = data.get("_n_decks", "?")
    page = f'''<meta charset="utf-8">
<title>Hobbit Combo Index</title>
<style>
:root{{
  --ground:#E9EDEA; --surface:#FBFCFB; --surface-2:#F2F5F2; --line:#CBD4CE; --line-soft:#DEE5E0;
  --ink:#141A17; --ink-2:#3A4642; --muted:#5C6864; --brass:#8F6522; --brass-soft:#F0E4CE;
  --serif:"Iowan Old Style","Hoefler Text","Palatino Linotype",Palatino,Georgia,serif;
  --sans:"Avenir Next",Avenir,"Segoe UI",system-ui,-apple-system,sans-serif;
  --mono:"SF Mono",SFMono-Regular,Menlo,"Cascadia Mono",ui-monospace,monospace;
}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{
  --ground:#0D1311; --surface:#141C19; --surface-2:#1A2320; --line:#2C3833; --line-soft:#222D29;
  --ink:#E4EBE6; --ink-2:#B9C6BF; --muted:#8B9C94; --brass:#C79A4C; --brass-soft:#33291A;
}}}}
:root[data-theme="dark"]{{
  --ground:#0D1311; --surface:#141C19; --surface-2:#1A2320; --line:#2C3833; --line-soft:#222D29;
  --ink:#E4EBE6; --ink-2:#B9C6BF; --muted:#8B9C94; --brass:#C79A4C; --brass-soft:#33291A;
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--ink);font-family:var(--sans);
  font-size:15px;line-height:1.5;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1180px;margin:0 auto;padding:0 22px}}
header{{background:var(--surface);border-bottom:1px solid var(--line)}}
header .wrap{{padding:30px 22px 24px;display:flex;gap:28px 44px;flex-wrap:wrap;
  align-items:flex-end;justify-content:space-between}}
h1{{font-family:var(--serif);font-size:clamp(26px,3.6vw,36px);margin:0;letter-spacing:-.015em}}
.sub{{color:var(--muted);font-size:14px;margin:8px 0 0;max-width:62ch}}
.stamp{{display:flex;gap:24px;font-family:var(--mono);font-size:11px;color:var(--muted)}}
.stamp b{{display:block;font-family:var(--sans);font-size:19px;color:var(--ink);font-weight:600;
  font-variant-numeric:tabular-nums}}
.stamp span{{display:block;text-transform:uppercase;letter-spacing:.08em;margin-top:2px}}
nav{{position:sticky;top:0;z-index:20;background:var(--ground);border-bottom:1px solid var(--line)}}
nav .wrap{{display:flex;gap:2px;overflow-x:auto;padding:0 22px}}
nav .wrap{{gap:6px;padding-top:9px;padding-bottom:9px}}
.flt{{font:inherit;font-size:12.5px;padding:5px 11px;border-radius:3px;cursor:pointer;
  background:var(--surface);border:1px solid var(--line);color:var(--ink-2);white-space:nowrap}}
.flt:hover{{color:var(--ink);border-color:var(--muted)}}
.flt.on{{background:var(--brass-soft);border-color:var(--brass);color:var(--ink)}}
.flt i{{font-style:normal;font-family:var(--mono);font-size:10.5px;opacity:.7;margin-left:3px}}
main{{padding:34px 0 60px}}
h3{{font-family:var(--serif);font-size:20px;margin:34px 0 12px;display:flex;align-items:baseline;gap:10px}}
h3:first-child{{margin-top:0}}
.cnt{{font-family:var(--mono);font-size:11px;color:var(--muted);font-weight:400}}
h2.sec{{font-family:var(--serif);font-size:22px;margin:8px 0 6px;letter-spacing:-.01em}}
h2.sec+.lede{{margin:0 0 18px}}
.lede{{color:var(--ink-2);font-size:13.5px;max-width:82ch}}
.lede i{{color:var(--ink)}}
.hubgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(430px,1fr));gap:12px;margin-bottom:38px}}
.hubcard{{background:var(--surface);border:1px solid var(--line);border-radius:4px;padding:13px 15px 6px}}
.hubhd{{display:flex;justify-content:space-between;align-items:flex-start;gap:14px}}
.hubhd button.cn{{font-family:var(--serif);font-size:17px}}
.hubsub{{font-family:var(--mono);font-size:10.5px;color:var(--muted);margin-top:3px}}
.idx{{text-align:right;font-family:var(--mono);font-size:9.5px;color:var(--muted);
  text-transform:uppercase;letter-spacing:.07em}}
.idx b{{display:block;font-family:var(--sans);font-size:19px;color:var(--brass);
  letter-spacing:normal;font-variant-numeric:tabular-nums}}
.star{{width:100%;height:auto;margin-top:2px;overflow:visible}}
.star .edge{{stroke:var(--brass);opacity:.42;stroke-linecap:round;pointer-events:none}}
.star .hit{{stroke:transparent;stroke-width:16;cursor:help}}
.star .ray{{outline:none}}
.star .ray:hover .edge,.star .ray:focus-visible .edge{{opacity:1;stroke-width:5}}
.star .ray:hover .lbl,.star .ray:focus-visible .lbl{{fill:var(--brass);font-weight:600}}
.star .ray:hover .node,.star .ray:focus-visible .node{{opacity:1;r:5.5}}
.star .node{{fill:var(--brass);opacity:.75}}
.star .hub{{fill:var(--brass)}}
.star .lbl{{font-family:var(--sans);font-size:11px;fill:var(--ink-2)}}
.star .num{{font-family:var(--mono);font-size:10px;fill:var(--muted)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:12px}}
.combo{{background:var(--surface);border:1px solid var(--line);border-radius:4px;padding:12px 16px 13px;
  display:flex;flex-direction:column;gap:8px}}
.combo.hidden{{display:none}}
.hd{{display:flex;align-items:center;gap:8px;font-family:var(--mono);font-size:11px;color:var(--muted)}}
.rank{{font-variant-numeric:tabular-nums;opacity:.55;min-width:1.6em}}
.tag{{padding:1px 6px;border:1px solid var(--line);border-radius:2px;letter-spacing:.03em}}
.freq{{margin-left:auto}}
.freq b{{font-family:var(--sans);font-size:14px;color:var(--ink);font-weight:600;
  font-variant-numeric:tabular-nums}}
.cards{{display:flex;flex-wrap:wrap;align-items:baseline;gap:5px;font-family:var(--serif);font-size:15.5px}}
.plus{{color:var(--brass);font-family:var(--sans);font-size:13px}}
button.cn{{font:inherit;color:var(--ink);background:none;border:0;padding:0;cursor:help;
  border-bottom:1px dotted var(--line);text-align:left}}
button.cn:hover,button.cn:focus-visible{{color:var(--brass);border-bottom-color:var(--brass)}}
button.cn.noimg{{cursor:default;border-bottom-color:transparent}}
.why{{margin:0;font-size:13.5px;color:var(--ink-2)}}
.meta{{display:flex;align-items:center;gap:7px;flex-wrap:wrap;font-family:var(--mono);
  font-size:11px;color:var(--muted);border-top:1px solid var(--line-soft);padding-top:9px}}
.meta b{{font-size:13px;color:var(--ink);font-variant-numeric:tabular-nums}}
.meta .u{{margin-right:8px}}
.meta .p{{margin-left:auto;opacity:.75}}
.bar{{width:52px;height:4px;background:var(--line);border-radius:2px;overflow:hidden;display:block}}
.bar i{{display:block;height:100%;width:var(--v);background:var(--brass)}}
.note{{border-left:2px solid var(--brass);background:var(--surface);padding:15px 19px;margin:0 0 26px;
  font-size:13.5px;color:var(--ink-2);max-width:80ch;border-radius:0 3px 3px 0}}
.note b{{color:var(--ink)}}
#peek{{position:fixed;z-index:80;pointer-events:none;margin:0;opacity:0;visibility:hidden;
  transform:translateY(4px);transition:opacity .11s ease,transform .11s ease}}
#peek.on{{opacity:1;visibility:visible;transform:none}}
#peek img{{display:block;width:300px;border-radius:14px;
  box-shadow:0 4px 10px rgba(0,0,0,.28),0 22px 48px -14px rgba(0,0,0,.55)}}
#peek figcaption{{width:300px;margin-top:8px;background:var(--surface);border:1px solid var(--line);
  border-radius:5px;padding:9px 11px;font-size:12.5px;line-height:1.45;color:var(--ink-2);
  box-shadow:0 10px 28px -14px rgba(0,0,0,.5)}}
#peek figcaption b{{display:block;font-family:var(--serif);font-size:13.5px;color:var(--ink);
  margin-bottom:3px}}
#peek figcaption .st{{display:block;font-family:var(--mono);font-size:10.5px;color:var(--muted);
  margin-top:5px}}
#peek.txt img{{border-bottom-left-radius:6px;border-bottom-right-radius:6px}}
footer{{border-top:1px solid var(--line);background:var(--surface)}}
footer .wrap{{padding:22px;color:var(--muted);font-size:12.5px}}
:focus-visible{{outline:2px solid var(--brass);outline-offset:3px;border-radius:3px}}
@media (prefers-reduced-motion:reduce){{*{{transition:none!important}}}}
</style>
<header><div class="wrap">
  <div>
    <h1>Hobbit Combo Index</h1>
    <p class="sub">Связки, пережившие три фильтра: механизм подтверждён текстом карт,
      карты встречаются вместе чаще случайного, эффект значим статистически.</p>
  </div>
  <div class="stamp">
    <div><b>{len(combos)}</b><span>связок</span></div>
    <div><b>{n_decks}</b><span>трофейных колод</span></div>
    <div><b>{len(order)}</b><span>групп</span></div>
  </div>
</div></header>
<nav><div class="wrap"><button class="flt on" data-f="*">все {len(combos)}</button>{"".join(f'<button class="flt" data-f="{g}">{g} <i>{len(groups[g])}</i></button>' for g in order)}</div></nav>
<main class="wrap">
<div class="note">
  <b>Как читать.</b> «Колод» — в скольких трофейных листах есть обе карты.
  «Чаще случайного» — во сколько раз это превышает ожидание, если бы карты выбирались независимо.
  <b>p</b> — вероятность увидеть такое совпадение случайно; отобраны только связки, прошедшие
  поправку на множественные сравнения (FDR 5%). <b>GIH не участвует ни на одном шаге.</b><br><br>
  <b>Троек здесь нет намеренно.</b> Их нашлось 140 с подъёмом до &times;5.3, но из ~245 000
  проверенных комбинаций ни одна не пережила поправку: на пару приходится 14–46 колод, и
  «3 из 4» статистически неотличимо от совпадения. Вернуться к тройкам, когда выборка вырастет.
</div>
{hub_html}{"".join(rows)}
</main>
<footer><div class="wrap">
  Источник: {n_decks} трофейных листов untapped.gg (7-0…7-2, gold+platinum) ·
  механизмы извлечены мультиагентным разбором оракл-текстов, независимые скептики отбраковали
  треть заявленного · <code>hob_combos.json</code> · те же связки печатает
  <code>⚑ СВЯЗКА</code> в живом драфте
</div></footer>
<script>
const IMGS = {json.dumps(imgs, ensure_ascii=False)};

/* фильтр по паре: порядок карточек НЕ меняется — он по частоте, фильтр только прячет */
document.querySelector("nav .wrap").addEventListener("click", e => {{
  const b = e.target.closest(".flt"); if(!b) return;
  document.querySelectorAll(".flt").forEach(x => x.classList.toggle("on", x === b));
  const f = b.dataset.f;
  document.querySelectorAll(".combo").forEach(c =>
    c.classList.toggle("hidden", f !== "*" && c.dataset.pair !== f));
}});
const peek = document.createElement("figure");
peek.id = "peek";
peek.innerHTML = '<img alt=""><figcaption hidden></figcaption>';
document.body.appendChild(peek);
const img = peek.querySelector("img"), cap = peek.querySelector("figcaption");
let cur = null;

/* Один узел превью на всю страницу: 68 data-URI в DOM разом — это десятки мегабайт
   декодированных пикселей. Здесь в любой момент живёт ровно одна картинка. */
function show(el){{
  const n = el.dataset.c, src = IMGS[n];
  if(!src) return;
  if(cur !== n){{ img.src = src; img.alt = n; cur = n; }}
  const why = el.dataset.w, pair = el.dataset.pair;
  if(why){{
    cap.innerHTML = "<b>" + (pair || n) + "</b>" + why +
      (el.dataset.n ? '<span class="st">' + el.dataset.n + " трофейных колод" +
        (el.dataset.l ? " · ×" + el.dataset.l + " чаще случайного" : "") + "</span>" : "");
    cap.hidden = false; peek.classList.add("txt");
  }} else {{
    cap.hidden = true; peek.classList.remove("txt");
  }}
  const r = el.getBoundingClientRect(), W = 300, G = 14;
  const H = 419 + (why ? 96 : 0);
  let x = r.right + G; if(x + W > innerWidth - 8) x = Math.max(8, r.left - W - G);
  let y = Math.min(Math.max(8, r.top + r.height/2 - H/2), innerHeight - H - 8);
  peek.style.left = x + "px"; peek.style.top = y + "px";
  peek.classList.add("on");
}}
const hide = () => peek.classList.remove("on");
const target = e => e.target.closest?.("button.cn, .ray");
for(const ev of ["mouseover","focusin"])
  document.addEventListener(ev, e => {{ const b = target(e); if(b) show(b); else if(ev==="focusin") hide(); }});
for(const ev of ["mouseout","focusout"])
  document.addEventListener(ev, e => {{ if(target(e)) hide(); }});
addEventListener("scroll", hide, {{passive:true}});
addEventListener("keydown", e => {{ if(e.key === "Escape") hide(); }});
</script>'''
    out = os.path.join(HERE, f"{code}_combos.html")
    open(out, "w", encoding="utf-8").write(page)
    print(f"→ {out}  ({len(page)/1024/1024:.2f} MB, {len(combos)} связок, {len(imgs)} принтов)")


if __name__ == "__main__":
    main()
