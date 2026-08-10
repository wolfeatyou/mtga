#!/usr/bin/env python3
"""Blocking watcher for Quick Draft (bot draft) — wrapper around quickdraft.py.

quickdraft.py is snapshot-only. This blocks until a NEW (PackNumber, PickNumber)
appears in Player.log, then prints the full analyzed pack by shelling out to
quickdraft.py. Mirrors `draft_live.py <set> watch` so the live-draft loop works
for Quick Draft too (one foreground call per pick, no polling by the model).

Usage:  python3 quickdraft_watch.py [msh] [fresh]
Env:    MTGA_LOG     override log path
        MTGA_SETTLE  seconds of quiet required after newest pack (default 1.0)
        MTGA_TIMEOUT max seconds to block (default 570)
"""
import json, os, re, subprocess, sys, time

SKILL = os.path.dirname(os.path.abspath(__file__))
args = [a.lower() for a in sys.argv[1:]]
FRESH = "fresh" in args
SET = next((a for a in args if a != "fresh"), "msh")
LOG = os.environ.get("MTGA_LOG") or os.path.expanduser(
    "~/Library/Logs/Wizards Of The Coast/MTGA/Player.log")
SETTLE = float(os.environ.get("MTGA_SETTLE", "1.0"))
TIMEOUT = float(os.environ.get("MTGA_TIMEOUT", "570"))
STATE = os.path.join(SKILL, f".qd_last_{SET}.json")

RE_PAYLOAD = re.compile(r'"Payload":"(\{.*?DraftPack.*?\})"')


def read_status():
    """Return (pn, pk, npack) of the newest BotDraftDraftStatus, or None."""
    try:
        raw = open(LOG, "r", errors="ignore").read()
    except OSError:
        return None
    hits = RE_PAYLOAD.findall(raw)
    if not hits:
        return None
    last = hits[-1]
    try:
        st = json.loads(last.encode().decode("unicode_escape"))
    except Exception:
        try:
            st = json.loads(last.replace('\\"', '"').replace('\\\\', '\\'))
        except Exception:
            return None
    return (st.get("PackNumber", 0) + 1,
            st.get("PickNumber", 0) + 1,
            len(st.get("DraftPack", [])))


def load_last():
    if FRESH or not os.path.exists(STATE):
        return None
    try:
        d = json.load(open(STATE))
        return (d["pn"], d["pk"], d["n"])
    except Exception:
        return None


def save_last(cur):
    json.dump({"pn": cur[0], "pk": cur[1], "n": cur[2]}, open(STATE, "w"))


def main():
    if FRESH and os.path.exists(STATE):
        os.remove(STATE)
    seen = load_last()
    deadline = time.time() + TIMEOUT

    while time.time() < deadline:
        cur = read_status()
        if cur is not None and cur != seen:
            # debounce: wait for SETTLE seconds of quiet, take the LATEST pack
            stable_since = time.time()
            while time.time() - stable_since < SETTLE:
                time.sleep(0.25)
                nxt = read_status()
                if nxt != cur:
                    cur = nxt
                    stable_since = time.time()
            if cur is None:
                continue
            if cur[2] == 0:
                print("DRAFT COMPLETE — пак пуст, переходим к сборке колоды.")
                save_last(cur)
                return 0
            save_last(cur)
            out = subprocess.run(
                [sys.executable, os.path.join(SKILL, "quickdraft.py"), SET],
                capture_output=True, text=True)
            sys.stdout.write(out.stdout)
            if out.stderr.strip():
                sys.stderr.write(out.stderr)
            return 0
        time.sleep(0.4)

    print(f"TIMEOUT — новых паков не было {int(TIMEOUT)}с.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
