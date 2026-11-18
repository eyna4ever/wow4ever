"""Render one zone page (FR or EN) with the interactive map and ONE merged quest table.

The page's existing quest list (section#quetes-liste, our beta quest index) is replaced by a single table that
merges it with the community data: every quest appears once, existing row anchors (id="r-...") are kept,
differences between the two lists are shown in the cell. Nothing else in the page changes, except the table of
contents entry, one new entry in the Sources list and the two asset links. Test tree only.
"""
import html, json, re

E = html.escape

TXT = {
    "fr": {
        "pill": "À confirmer", "map_h": "Carte interactive", "q_h": "Quêtes (à confirmer)",
        "map_p": ("Positions des PNJ et objets liés aux quêtes de la zone, d’après une base de données communautaire Forever "
                  "(à confirmer en jeu). Coordonnées en % de la carte de zone (x, y), calculées avec le cadre de carte des fichiers du jeu (client 1.60.1.70862)."),
        "show": "Afficher", "giver": "Donneurs de quêtes", "ender": "Fins de quêtes", "target": "Cibles", "dropper": "Objets de quête",
        "frame": "Carte de la zone avec repères",
        "credit": "Carte : images du jeu World of Warcraft: Forever © Blizzard Entertainment, tirées des fichiers du client 1.60.1.70862 : carte de base et calques des zones explorées, assemblés à leur place officielle comme en jeu (carte entièrement explorée), sans autre retouche (seuls le format et la compression ont changé).",
        "list": "Liste des repères", "c_npc": "PNJ ou objet (nom anglais)", "c_role": "Rôle", "c_pos": "Position (x, y)", "c_pts": "Points connus",
        "roles": {"giver": "donne une quête", "ender": "reçoit une quête", "target": "cible de quête", "dropper": "porte un objet de quête", "holder": "contient un objet de quête"},
        "q_p": ("{n} quêtes rattachées à {zone} : {both} dans les deux listes, {ours} seulement dans l’index de quêtes bêta, "
                "{ps} seulement dans la base de données communautaire Forever (client 1.60.1.70532). {k} écarts de nom, de niveau ou de faction "
                "sont signalés dans le tableau. Noms de quêtes et de PNJ en anglais (pas de traduction française dans ces sources) ; "
                "noms d’objets en français tirés des fichiers du jeu."),
        "cols": ["Quête (nom anglais)", "Niveau", "Niveau requis", "Faction", "Donneur", "Rendre à", "Prérequis", "Suite", "Récompenses"],
        "side": {"both": "les deux", "alliance": "Alliance", "horde": "Horde", None: "non indiqué"},
        "none": "non indiqué", "choice": "au choix", "any": "l’une des deux", "alt_name": "autre nom", "index": "index",
        "src": "Base de données communautaire Forever (version {v}), voir « Sources et licences »", "src2": "licences GPL-3.0 et CC BY 4.0 · consultée au commit {c}",
        "noq": "Aucune quête n’est rattachée à cette zone dans les sources consultées pour l’instant.",
        "nopins": "Aucun repère connu pour cette zone pour l’instant.",
        "toc_map": "Carte interactive", "nomap": "La carte de cette zone n’est pas disponible dans les fichiers du jeu.",
    },
    "en": {
        "pill": "Unconfirmed — to be confirmed", "map_h": "Interactive map", "q_h": "Quests (to be confirmed)",
        "map_p": ("Positions of the NPCs and objects tied to this zone's quests, from a community Forever database (to be confirmed in game). "
                  "Coordinates in % of the zone map (x, y), computed with the map frame from the game files (client 1.60.1.70862)."),
        "show": "Show", "giver": "Quest givers", "ender": "Quest turn-ins", "target": "Targets", "dropper": "Quest items",
        "frame": "Zone map with markers",
        "credit": "Map: World of Warcraft: Forever in-game images © Blizzard Entertainment, from the client 1.60.1.70862 files: base map and explored-area layers, assembled at their official positions as in game (fully explored map), with no other retouching (only format and compression changed).",
        "list": "List of markers", "c_npc": "NPC or object", "c_role": "Role", "c_pos": "Position (x, y)", "c_pts": "Known points",
        "roles": {"giver": "gives a quest", "ender": "takes a quest", "target": "quest target", "dropper": "carries a quest item", "holder": "holds a quest item"},
        "q_p": ("{n} quests tied to {zone}: {both} in both lists, {ours} only in the beta quest index, {ps} only in the community Forever "
                "database (client 1.60.1.70532). {k} differences in name, level or faction are shown in the table. Item names from the game files."),
        "cols": ["Quest", "Level", "Required level", "Faction", "Giver", "Turn in to", "Prerequisites", "Next", "Rewards"],
        "side": {"both": "both", "alliance": "Alliance", "horde": "Horde", None: "not given"},
        "none": "not given", "choice": "choice", "any": "either", "alt_name": "other name", "index": "index",
        "src": "Community Forever database (version {v}), see “Sources and licences”", "src2": "GPL-3.0 and CC BY 4.0 licences · read at commit {c}",
        "noq": "No quest is tied to this zone in the sources consulted so far.",
        "nopins": "No known marker for this zone yet.",
        "toc_map": "Interactive map", "nomap": "This zone's map is not available in the game files.",
    },
}
OURS_SIDE = {"A": "alliance", "H": "horde", "B": "both", "AH": "both"}


TILES_V = "43b"  # cache-busting of the map tiles (v43b: fully explored maps)


def slugify(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def _names(st, lang):
    idx = {}
    for kind, rows in (("npc", st["npcs"]), ("object", st["objects"]), ("item", st["items"])):
        for r in rows:
            if kind == "item":
                n = (r.get("name_fr") if lang == "fr" else r.get("name_en_client")) or r.get("name_en")
            else:
                n = r.get("name_en")
            idx[(kind, r["id"])] = n
    return idx


def merged_rows(st, ours_rows, lang, old_anchors=None):
    """ours_rows: [[id, title, zone, level, min_level, side, ...]] of this zone (our beta index)."""
    t = TXT[lang]
    idx = _names(st, lang)
    P = {q["id"]: q for q in st["quests"]}
    O = {r[0]: r for r in ours_rows}
    allq = {**{i: (O[i][1]) for i in O}, **{i: P[i]["title_en"] for i in P if P[i].get("title_en")}}
    rows, seen_anchor, k_conf = [], set(), 0
    stats = {"both": 0, "ours": 0, "ps": 0}
    for qid in sorted(set(P) | set(O), key=lambda i: ((P.get(i) or {}).get("level") or (O[i][3] if i in O else 0) or 0, allq.get(i) or "")):
        p, o = P.get(qid), O.get(qid)
        stats["both" if p and o else ("ps" if p else "ours")] += 1
        title = (p or {}).get("title_en") or (o[1] if o else f"#{qid}")
        olds = (old_anchors or {}).get(o[1]) if o else None
        if olds:
            anchor = olds.pop(0)          # keep the anchor the page already used for this quest
        elif o:
            anchor = "r-" + slugify(o[1])
        else:
            anchor = f"r-q{qid}"
        if anchor in seen_anchor:
            anchor = f"r-q{qid}"
        seen_anchor.add(anchor)
        conf = False

        def cell(pv, ov, fmt=lambda x: str(x)):
            nonlocal conf
            if pv is not None and ov is not None and pv != ov:
                conf = True
                return f'{E(fmt(pv))} <span class="wk-alt">({t["index"]} : {E(fmt(ov))})</span>' if lang == "fr" else f'{E(fmt(pv))} <span class="wk-alt">({t["index"]}: {E(fmt(ov))})</span>'
            v = pv if pv is not None else ov
            return E(fmt(v)) if v is not None else "—"

        name_html = E(title)
        if p and o and o[1] != p.get("title_en"):
            conf = True
            name_html += f' <span class="wk-alt">({t["alt_name"]} : {E(o[1])})</span>' if lang == "fr" else f' <span class="wk-alt">({t["alt_name"]}: {E(o[1])})</span>'
        lv = cell((p or {}).get("level"), o[3] if o else None)
        ml = cell((p or {}).get("min_level"), o[4] if o else None)
        sd = cell((p or {}).get("side"), OURS_SIDE.get(o[5], o[5]) if o else None, lambda x: t["side"].get(x, x))
        if p:
            giver = ", ".join(E(idx.get((s["kind"], s["id"])) or "—") for s in p["start"]) or t["none"]
            ender = ", ".join(E(idx.get((s["kind"], s["id"])) or "—") for s in p["end"]) or t["none"]
            pre = ", ".join(E(allq.get(x["pre"]) or f"#{x['pre']}") + (f' ({t["any"]})' if x.get("mode") == "any" else "") for x in p["prereq"]) or "—"
            nxt = ", ".join(E(allq.get(n) or f"#{n}") for n in p["next"]) or "—"
            rw = ", ".join(E(idx.get(("item", w["id"])) or f"#{w['id']}") + (f' ({t["choice"]})' if w["kind"] == "choice" else "")
                           for w in p["rewards"] if w["kind"] in ("item", "choice")) or "—"
        else:
            giver = ender = t["none"]; pre = nxt = rw = "—"
        if conf:
            k_conf += 1
        rows.append(f'<tr id="{E(anchor)}"><th scope="row">{name_html}</th><td>{lv}</td><td>{ml}</td><td>{sd}</td>'
                    f'<td>{giver}</td><td>{ender}</td><td>{pre}</td><td>{nxt}</td><td>{rw}</td></tr>')
    return rows, stats, k_conf


def quest_section(st, ours_rows, lang, zone_name, cites, old_anchors=None):
    t = TXT[lang]
    rows, s, k = merged_rows(st, ours_rows, lang, old_anchors)
    pill = f'<span class="status-pill is-draft">{E(t["pill"])}</span>'
    cite = "".join(f'<sup class="cite"><a href="#source-{n}" aria-label="Source {n}">[{n}]</a></sup>' for n in cites)
    if not rows:
        return (f'<section class="article-section" id="quetes-liste" aria-labelledby="quetes-liste-title"><h2 id="quetes-liste-title">{E(t["q_h"])}</h2>'
                f'<p>{E(t["noq"])}{cite} {pill}</p></section>'), {"rows": 0, **s, "conflicts": 0}
    p = t["q_p"].format(n=len(rows), zone=E(zone_name), both=s["both"], ours=s["ours"], ps=s["ps"], k=k)
    head = "".join(f'<th scope="col">{E(c)}</th>' for c in t["cols"])
    cap = f'{E(zone_name)} : {len(rows)} quêtes — à confirmer.' if lang == "fr" else f'{E(zone_name)}: {len(rows)} quests — to be confirmed.'
    return (f'<section class="article-section" id="quetes-liste" aria-labelledby="quetes-liste-title"><h2 id="quetes-liste-title">{E(t["q_h"])}</h2>'
            f'<p>{p}{cite} {pill}</p><div class="table-wrap" role="region" aria-label="{cap}" tabindex="0"><table class="wk-quests"><caption>{cap}{cite} {pill}</caption>'
            f'<thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div></section>'), {"rows": len(rows), **s, "conflicts": k}


def map_section(st, lang, layout, tiles_href, json_href, cite_no):
    t = TXT[lang]
    pill = f'<span class="status-pill is-draft">{E(t["pill"])}</span>'
    cite = f'<sup class="cite"><a href="#source-{cite_no}" aria-label="Source {cite_no}">[{cite_no}]</a></sup>'
    if not layout:
        return (f'<section class="article-section" id="carte-interactive" aria-labelledby="carte-interactive-title"><h2 id="carte-interactive-title">{E(t["map_h"])}</h2>'
                f'<p>{E(t["nomap"])}</p></section>')
    L = layout["layer"]
    cols = max(x["col"] for x in layout["tiles"]) + 1
    tiles = "".join(f'<img src="{E(tiles_href + x["file"] + "?v=" + TILES_V)}" alt="" width="{x["w"]}" height="{x["h"]}" loading="lazy" decoding="async">' for x in layout["tiles"])
    # Grid width relative to the visible layer: (cols * tile width) / layer width. Set by CSS classes (no inline style).
    over = cols * L["tw"] / L["w"]
    grid_cls = f'wk-g{cols}-{"std" if abs(over - 1024 / 1002) < 1e-3 else "one"}'
    aspect_cls = "wk-a-std" if (L["w"], L["h"]) == (1002, 668) else "wk-a-sq"
    legend = (f'<fieldset class="wk-map-filters"><legend>{E(t["show"])}</legend>'
              + "".join(f'<label><input type="checkbox" data-role="{r}"{" checked" if r in ("giver", "ender") else ""}> {E(t[r])}</label>' for r in ("giver", "ender", "target", "dropper"))
              + "</fieldset>")
    rows = []
    for n in st["npcs"] + st["objects"]:
        if n["points"]:
            p0 = n["points"][0]
            rows.append(f'<tr><th scope="row">{E(n.get("name_en") or "")}</th><td>{E(", ".join(t["roles"].get(r, r) for r in n["roles"]))}</td><td>{p0[0]}, {p0[1]}</td><td>{n["points_total"]}</td></tr>')
    return (f'<section class="article-section" id="carte-interactive" aria-labelledby="carte-interactive-title"><h2 id="carte-interactive-title">{E(t["map_h"])}</h2>'
            f'<p>{E(t["map_p"])}{cite} {pill}</p>' + ('' if rows else f'<p class="wk-preview-note">{E(t["nopins"])}</p>') +
            f'<div class="wk-map" data-map="{E(json_href)}" data-lang="{lang}">{legend}'
            f'<div class="wk-map-frame {aspect_cls}" role="group" aria-label="{E(t["frame"])}"><div class="wk-map-tiles {grid_cls}">{tiles}</div><div class="wk-map-pins"></div></div>'
            f'<div class="wk-map-card" aria-live="polite" hidden></div><p class="wk-map-credit">{E(t["credit"])}</p></div>'
            f'<details class="wk-map-table"><summary>{E(t["list"])} ({len(rows)})</summary><div class="table-wrap" role="region" tabindex="0" aria-label="{E(t["list"])}">'
            f'<table><thead><tr><th scope="col">{E(t["c_npc"])}</th><th scope="col">{E(t["c_role"])}</th><th scope="col">{E(t["c_pos"])}</th><th scope="col">{E(t["c_pts"])}</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div></details></section>')


def map_payload(st):
    pins = []
    for kind, rows in (("npc", st["npcs"]), ("object", st["objects"])):
        for r in rows:
            for p in r["points"]:
                pins.append({"k": kind, "id": r["id"], "n": r.get("name_en"), "r": r["roles"], "x": p[0], "y": p[1]})
    q = {}
    for x in st["quests"]:
        for s in x["start"]:
            q.setdefault(f'{s["kind"]}:{s["id"]}', {}).setdefault("g", []).append(x["title_en"])
        for s in x["end"]:
            q.setdefault(f'{s["kind"]}:{s["id"]}', {}).setdefault("e", []).append(x["title_en"])
    return {"version": st["meta"]["version"], "commit": st["meta"]["commit"], "status": "a-confirmer", "pins": pins, "quests": q}


def render_page(page, st, ours_rows, lang, zone_name, layout, tiles_href, json_href, credits_href, root="../../../"):
    t = TXT[lang]
    if 'id="carte-interactive"' in page:
        raise ValueError("already rendered")
    nums = [int(x) for x in re.findall(r'<li id="source-(\d+)"', page)]
    new_no = (max(nums) + 1) if nums else 1
    m = re.search(r'<section class="article-section" id="quetes-liste".*?</section>', page, re.S)
    old_cites = sorted(set(int(x) for x in re.findall(r'href="#source-(\d+)"', m.group(0)))) if m else []
    old_anchors = {}
    if m:
        for a_, t_ in re.findall(r'<tr id="(r-[^"]+)"><th scope="row">(.*?)</th>', m.group(0)):
            old_anchors.setdefault(html.unescape(re.sub(r"<[^>]+>", "", t_)).strip(), []).append(a_)
    qsec, qstats = quest_section(st, ours_rows, lang, zone_name, old_cites + [new_no], old_anchors)
    msec = map_section(st, lang, layout, tiles_href, json_href, new_no)
    if m:
        old_ids = set(re.findall(r'<tr id="(r-[^"]+)"', m.group(0)))
        new_ids = set(re.findall(r'<tr id="(r-[^"]+)"', qsec))
        qstats["lost_anchors"] = sorted(old_ids - new_ids)
        page = page[:m.start()] + msec + qsec + page[m.end():]
    else:
        qstats["lost_anchors"] = []
        anchor = next(a for a in ('<section class="article-section" id="historique-des-corrections"', '<section class="article-section status-grid" id="confirme"', '<section class="article-section sources-block" id="sources"') if a in page)
        page = page.replace(anchor, msec + qsec + anchor, 1)
    # Table of contents
    toc = re.search(r'<li><a href="#quetes-liste">[^<]*</a></li>', page)
    new_toc = f'<li><a href="#carte-interactive">{E(t["toc_map"])}</a></li><li><a href="#quetes-liste">{E(t["q_h"])}</a></li>'
    if toc:
        page = page[:toc.start()] + new_toc + page[toc.end():]
    else:
        page = re.sub(r'(<li><a href="#historique-des-corrections">)', new_toc + r"\1", page, count=1)
    v, c = st["meta"]["version"], st["meta"]["commit"]
    li = (f'<li id="source-{new_no}"><span class="source-number">[{new_no}]</span> <span class="source-lines"><a href="{E(credits_href)}">'
          f'{E(t["src"].format(v=v))}</a> · {E(t["src2"].format(c=c[:12]))}</span></li>')
    page = re.sub(r'(<ol class="source-list">.*?)(</ol>)', lambda mm: mm.group(1) + li + mm.group(2), page, count=1, flags=re.S)
    page = page.replace("</head>", f'<link rel="stylesheet" href="{root}wk-map.css?v=43"></head>', 1)
    page = page.replace("</body>", f'<script type="module" src="{root}wk-map.js?v=43"></script></body>', 1)
    qstats["source_no"] = new_no
    return page, qstats
