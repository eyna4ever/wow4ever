#!/usr/bin/env python3
"""Render the Polestar sample into a COPY of the wiki tree (test only; never the live site).
usage: render_sample.py --staging S.json --tree TREE --zone-slug durotar --tiles-dir DIR"""
import argparse, json, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import polestar_import as pi

ap = argparse.ArgumentParser()
ap.add_argument("--staging", required=True); ap.add_argument("--tree", required=True)
ap.add_argument("--zone-slug", required=True); ap.add_argument("--tiles-dir", required=True)
a = ap.parse_args()
tree = Path(a.tree) / "wiki"
st = json.loads(Path(a.staging).read_text(encoding="utf-8"))
pin = pi.load_pin()
man = json.loads((Path(a.tiles_dir) / "manifest.json").read_text())
dst = tree / "assets" / "carte" / a.zone_slug
dst.mkdir(parents=True, exist_ok=True)
tiles = []
for t in sorted(man["tiles"], key=lambda t: (t["row"], t["col"])):
    shutil.copy2(Path(a.tiles_dir) / t["file"], dst / t["file"])
    tiles.append(f"../../../assets/carte/{a.zone_slug}/{t['file']}")
shutil.copy2(Path(a.tiles_dir) / "manifest.json", dst / "manifest.json")
page_dir = tree / "fr" / "zones" / a.zone_slug
page = (page_dir / "index.html").read_text(encoding="utf-8")
if 'id="carte-interactive"' in page:
    sys.exit("already rendered; start from a fresh copy")
info = pi.render(st, pin, page, page_dir, tiles)
repo_wiki = Path(__file__).resolve().parent / "frontend"
for f in ("wk-map.js", "wk-map.css"):
    shutil.copy2(repo_wiki / f, tree / f)
cdir = tree / "fr" / "sources-et-licences"
cdir.mkdir(parents=True, exist_ok=True)
(cdir / "donnees-polestar-durotar.json").write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
(cdir / "index.html").write_text(pi.credits_page(pin, st["meta"]["version"], st["meta"]["commit"], "donnees-polestar-durotar.json"), encoding="utf-8")
print(json.dumps(info))
