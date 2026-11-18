#!/usr/bin/env python3
"""Classic Era items (Polestar_ItemDB/Items.lua, client 1.15.9) checked against our WoW Forever client (1.60.1.70862).

Rules (Mathieu, t417u): only items whose ID exists in the Forever client are kept (an ID whose details are
encrypted in the client is counted but not used); Forever client values win.
Classic-only numbers (stat amounts, armor, weapon damage, equip bonuses: the Forever client stores only stat
types and budget shares) are kept ONLY when every field both clients store is identical, marked
"a-confirmer" with their provenance; otherwise they are dropped.

usage: classic_items.py --items-lua Items.lua --forever FOREVER_EXPORT.json --out STAGING.json
"""
import argparse, hashlib, json, re, sys
from pathlib import Path

DIRECT = ("inv", "ilvl", "req", "quality", "class", "sub", "cls", "uniq")
BASE = ("mana", "health", "agi", "str", "int", "spi", "sta")
PROV = {"source": "polestar-itemdb", "file": "addon/Polestar_ItemDB/Items.lua", "clientBuild": "1.15.9.70576",
        "licence": "GPL-3.0-only (file); game facts (c) Blizzard Entertainment"}


def decode(s):
    p = s.split(" ")
    rec = {"inv": int(p[0]), "ilvl": int(p[1]), "req": int(p[2]), "quality": int(p[3]), "class": int(p[4]), "sub": int(p[5]),
           "stats": {}, "cls": 0, "uniq": False}
    for t in p[6:]:
        m = re.match(r"([a-zA-Z]+)(-?\d+)$", t)
        if not m:
            raise ValueError(f"bad token {t!r}")
        k, v = m.group(1), int(m.group(2))
        if k in ("dmin", "dmax", "speed"):
            rec[k] = v
        elif k == "cls":
            rec["cls"] = v
        elif k == "uniq":
            rec["uniq"] = v == 1
        else:
            rec["stats"][k] = v
    return rec


def parse_items_lua(text):
    m = re.search(r'build = "([^"]+)"', text)
    build = m.group(1) if m else None
    return build, {int(a): decode(b) for a, b in re.findall(r'\[(\d+)\]="([^"]*)"', text)}


def merge(classic, forever, file_sha):
    out, rep, fields = {}, {"items_lua_total": len(classic), "present_in_forever": 0, "absent_from_forever_client": 0,
                            "present_but_not_equipment": 0, "present_details_encrypted": 0, "identical": 0, "differing": 0,
                            "classic_numbers_kept": 0, "classic_numbers_dropped": 0}, {}
    for iid, c in sorted(classic.items()):
        f = forever.get(str(iid))
        if f is None:
            rep["absent_from_forever_client"] += 1
            continue
        if f.get("encrypted"):
            # The ID is in the Forever Item table but its ItemSparse row is encrypted in the client
            # (often content not yet released): nothing from Forever to win, so it is not used.
            rep["present_details_encrypted"] += 1
            continue
        if "skipped" in f:
            rep["present_but_not_equipment"] += 1
            continue
        rep["present_in_forever"] += 1
        diff = [k for k in DIRECT if c.get(k) != f.get(k)]
        if "speed" in c and c["speed"] != f.get("speed"):
            diff.append("speed")
        if sorted(k for k in c["stats"] if k in BASE) != sorted(t for t in f.get("stat_types", []) if t in BASE):
            diff.append("stat_types")
        for k in diff:
            fields[k] = fields.get(k, 0) + 1
        rec = {"id": iid, **{k: v for k, v in f.items()}, "status_client": "client 1.60.1.70862",
               "dedupe": {"status": "doublon-conflit" if diff else "doublon-identique", "match": "client:ItemSparse:1.60.1.70862",
                          "conflicts": [{"field": k, "classic": c.get(k) if k != "stat_types" else sorted(c["stats"]), "forever": f.get(k)} for k in diff]}}
        rep["differing" if diff else "identical"] += 1
        nums = dict(c["stats"])
        for k in ("dmin", "dmax"):
            if k in c:
                nums[k] = c[k]
        if nums and not diff:
            rec["classic_1_15_9"] = {"values": nums, "status": "a-confirmer", "provenance": {**PROV, "sha256": file_sha}}
            rep["classic_numbers_kept"] += 1
        elif nums:
            rep["classic_numbers_dropped"] += 1
        out[iid] = rec
    rep["differing_fields"] = fields
    return out, rep


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--items-lua", required=True); ap.add_argument("--forever", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    raw = Path(a.items_lua).read_bytes()
    build, classic = parse_items_lua(raw.decode("utf-8"))
    if not (build or "").startswith("1.15."):
        print(f"REFUSED: unexpected Items.lua build {build!r}", file=sys.stderr)
        return 2
    fx = json.loads(Path(a.forever).read_text())
    if not fx.get("build", "").startswith("1.60.1."):
        print("REFUSED: the Forever export is not a 1.60.1 client", file=sys.stderr)
        return 2
    out, rep = merge(classic, fx["items"], hashlib.sha256(raw).hexdigest())
    Path(a.out).write_text(json.dumps({"meta": {"classic_build": build, "forever_build": fx["build"], "report": rep},
                                       "items": list(out.values())}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(json.dumps(rep))
    return 0


if __name__ == "__main__":
    sys.exit(main())
