#!/usr/bin/env python3
"""Собирает hob_atlas.html из частей в atlas/ и вшивает принты карт.

    python3 build_atlas.py            # собрать (картинки берутся из кэша)
    python3 build_atlas.py --refetch  # перекачать принты со Scryfall заново
    python3 build_atlas.py --report   # только посчитать вес, ничего не писать

Части: atlas/head.html (title+CSS) · atlas/decks.json (данные пяти листов) ·
atlas/body.html (разметка+скрипт) · atlas/imgs.json (кэш принтов, data-URI).

Почему принты ВШИВАЮТСЯ, а не грузятся по ссылке — те же три причины, что и в
build_hob_images.py: страница нужна офлайн и мгновенно во время драфта; Scryfall просит
не хотлинкать массово; и CSP артефакта режет любой внешний хост, так что ссылка на
cards.scryfall.io в опубликованной версии просто не загрузится.
"""
import base64, io, json, os, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "atlas")
OUT = os.path.join(HERE, "hob_atlas.html")
CACHE = os.path.join(SRC, "imgs.json")
UA = {"User-Agent": "mtg-draft-helper/1.0"}
WIDTH, QUALITY = 400, 72      # превью показывается ~300px — 400 хватает на retina


def img_url(card):
    u = card.get("image_uris")
    if not u and card.get("card_faces"):
        u = card["card_faces"][0].get("image_uris")
    return (u or {}).get("normal")


def fetch_images(names, refetch=False):
    from PIL import Image
    cache = {}
    if os.path.exists(CACHE) and not refetch:
        cache = json.load(open(CACHE, encoding="utf-8"))
    cards = {c["name"]: c for c in json.load(open(os.path.join(HERE, "hob_set.json"), encoding="utf-8"))}
    byfront = {}
    for n, c in cards.items():
        byfront.setdefault(n.split(" //")[0], c)

    todo = [n for n in names if n not in cache]
    if todo:
        print(f"качаю принты: {len(todo)} (в кэше уже {len(cache)})")
    for i, n in enumerate(todo, 1):
        c = cards.get(n) or byfront.get(n)
        url = img_url(c) if c else None
        if not url:
            print(f"  ⚠ без картинки: {n}")
            continue
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        if im.width != WIDTH:
            im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "WEBP", quality=QUALITY, method=6)
        data = buf.getvalue()
        cache[n] = "data:image/webp;base64," + base64.b64encode(data).decode()
        print(f"  [{i:3}/{len(todo)}] {len(data)/1024:5.1f}KB  {n}")
        time.sleep(0.12)                      # вежливость к Scryfall
    if todo:
        json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
    return {n: cache[n] for n in names if n in cache}


def main():
    decks = json.load(open(os.path.join(SRC, "decks.json"), encoding="utf-8"))
    names = sorted({s["name"] for d in decks.values() for s in d["spells"]})
    print(f"уникальных карт в пяти листах: {len(names)}")

    imgs = fetch_images(names, refetch="--refetch" in sys.argv)
    weight = sum(len(v) for v in imgs.values())
    print(f"принтов вшито: {len(imgs)} · вес в base64 {weight/1024/1024:.2f} MB")
    missing = [n for n in names if n not in imgs]
    if missing:
        print("БЕЗ ПРИНТА:", ", ".join(missing))

    if "--report" in sys.argv:
        print("--report: файл не изменён")
        return

    parts = [
        open(os.path.join(SRC, "head.html"), encoding="utf-8").read(),
        "<script>const DECKS = " + json.dumps(decks, ensure_ascii=False) + ";",
        "const IMGS = " + json.dumps(imgs, ensure_ascii=False) + ";</script>",
        open(os.path.join(SRC, "body.html"), encoding="utf-8").read(),
    ]
    html = "\n".join(parts)
    open(OUT, "w", encoding="utf-8").write(html)
    print(f"\n→ {OUT}  ({len(html)/1024/1024:.2f} MB)")
    if len(html) > 15 * 1024 * 1024:
        print("⚠ близко к лимиту артефакта 16 MB — снизь WIDTH/QUALITY")


if __name__ == "__main__":
    main()
