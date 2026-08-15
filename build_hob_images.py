#!/usr/bin/env python3
"""Вшить принты карт в hob_cheatsheet.html как data-URI (превью по наведению).

Почему вшиваем, а не ссылаемся на cards.scryfall.io:
  · страница обязана открываться офлайн и мгновенно — ей пользуются во время драфта;
  · Scryfall просит не хотлинкать картинки массово, а кэшировать их у себя;
  · если страницу когда-нибудь опубликуют как артефакт, CSP там режет любой внешний хост.

Скрипт идемпотентен: берёт имена карт прямо из разметки, конвертирует `<span class="cn">`
в фокусируемые кнопки и заменяет блок между маркерами IMG:START/IMG:END. Повторный запуск
не плодит дубли и не требует ручной правки HTML.

    python3 build_hob_images.py            # скачать и вшить
    python3 build_hob_images.py --report   # только показать вес, ничего не менять
"""
import base64
import io
import json
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, "hob_cheatsheet.html")
SETJ = os.path.join(HERE, "hob_set.json")
UA = {"User-Agent": "mtg-draft-helper/1.0"}
WIDTH, QUALITY = 488, 74       # 488 = «normal» у Scryfall; хватает на retina при показе ~280px
START, END = "<!--IMG:START-->", "<!--IMG:END-->"


def img_url(card):
    u = card.get("image_uris")
    if not u and card.get("card_faces"):
        u = card["card_faces"][0].get("image_uris")
    return (u or {}).get("normal")


def main():
    from PIL import Image
    report = "--report" in sys.argv
    src = open(HTML, encoding="utf-8").read()

    cards = {c["name"]: c for c in json.load(open(SETJ, encoding="utf-8"))}
    byfront = {}
    for n, c in cards.items():
        byfront.setdefault(n.split(" //")[0], c)

    # имена берём из самой разметки — и из span, и из уже сконвертированных кнопок
    names = re.findall(r'<span class="cn">([^<]+)</span>', src)
    names += re.findall(r'<button class="cn"[^>]*data-c="([^"]+)"', src)
    names = list(dict.fromkeys(names))
    print(f"карт в разметке: {len(names)}")

    blob, total, missing = {}, 0, []
    for i, n in enumerate(names, 1):
        c = cards.get(n) or byfront.get(n)
        url = img_url(c) if c else None
        if not url:
            missing.append(n)
            continue
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        if im.width != WIDTH:
            im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "WEBP", quality=QUALITY, method=6)
        data = buf.getvalue()
        total += len(data)
        blob[n] = "data:image/webp;base64," + base64.b64encode(data).decode()
        print(f"  [{i:2}/{len(names)}] {len(data)/1024:5.1f}KB  {n}")
        time.sleep(0.12)          # вежливость к Scryfall

    if missing:
        print("БЕЗ КАРТИНКИ:", ", ".join(missing))
    enc = sum(len(v) for v in blob.values())
    print(f"\nwebp суммарно {total/1024/1024:.2f} MB → в base64 {enc/1024/1024:.2f} MB")
    if report:
        print("--report: файл не изменён")
        return

    # span -> button (идемпотентно: уже сконвертированные не трогаем)
    src = re.sub(r'<span class="cn">([^<]+)</span>',
                 lambda m: f'<button class="cn" type="button" data-c="{m.group(1)}">{m.group(1)}</button>',
                 src)

    payload = (START + '\n<script id="cardimg" type="application/json">'
               + json.dumps(blob, ensure_ascii=False) + '</script>\n' + END)
    # Блок дописывается в КОНЕЦ документа — он большой, и держать его перед контентом незачем.
    # Инициализация превью в HTML ждёт DOMContentLoaded, поэтому порядок тегов роли не играет.
    if START in src:
        src = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: payload, src, flags=re.S)
    else:
        src = src.rstrip() + "\n" + payload + "\n"

    open(HTML, "w", encoding="utf-8").write(src)
    print(f"Записано: {HTML}  ({os.path.getsize(HTML)/1024/1024:.2f} MB)")


if __name__ == "__main__":
    main()
