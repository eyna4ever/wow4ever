#!/usr/bin/env python3
"""Apply v40 cross-link insertions onto published entries. Writes revision JSON payloads."""
from __future__ import annotations

import json
import re
import copy
from collections import defaultdict
from pathlib import Path

ROOT = Path('/workspace/wowkipedia-v21-elite')
ENTRIES = ROOT / 'bestiaire/test-tree-v38/pipeline/runtime/entries.json'
BATCH = ROOT / 'completion/import-batches/v40-cross-links.json'
OUT = ROOT / 'bestiaire/v38-t359u/v40-revisions'
CELL_MAX = 400
TEXT_MAX = 2400

HIST_FR = (
    "14 novembre 2026 : liens internes vers les fiches déjà publiées (bestiaires, "
    "listes de recettes, donjons) — lot v40, t361u. Aucun fait nouveau."
)
HIST_EN = (
    "14 November 2026: internal links to already published sheets (bestiaries, "
    "recipe lists, dungeons) — v40 batch, t361u. No new facts."
)

stats = defaultdict(int)
misses = []
notes = []


def load():
    records = json.loads(ENTRIES.read_text())
    by_id = {e['id']: e for e in records}
    batch = json.loads(BATCH.read_text())
    return records, by_id, batch


def already_linked(text: str, needle: str) -> bool:
    return f'[{needle}](' in text


def boundary_pat(needle: str) -> re.Pattern:
    # Do not match Cookie inside Cookie's / Cookie’s.
    return re.compile(
        r'(?<![A-Za-z0-9\[])'
        + re.escape(needle)
        + r"(?![A-Za-z0-9'’\]])"
    )


def inside_existing_link(text: str, start: int, end: int) -> bool:
    # Skip if this span sits inside [label](/path/)
    left = text.rfind('[', 0, start)
    mid = text.find('](/', start if False else 0)
    # simpler: check any markdown link range overlapping
    for m in re.finditer(r'\[[^\]]{1,200}\]\(/?(?:fr|en)/[^)]+\)', text):
        if m.start() <= start and end <= m.end():
            return True
    return False


def wrap(text: str, needle: str, href: str, max_len: int) -> tuple[str, str]:
    if not text or not needle or not href:
        return text, 'empty'
    if already_linked(text, needle):
        return text, 'already'
    if needle not in text:
        return text, 'missing'
    repl = f'[{needle}]({href})'
    pat = boundary_pat(needle)
    out = []
    last = 0
    changed = 0
    for m in pat.finditer(text):
        if inside_existing_link(text, m.start(), m.end()):
            continue
        out.append(text[last:m.start()])
        out.append(repl)
        last = m.end()
        changed += 1
    if not changed:
        return text, 'no-boundary'
    out.append(text[last:])
    new = ''.join(out)
    if max_len and len(new) > max_len:
        return text, f'too-long:{len(new)}'
    return new, 'ok'


FALLBACKS = []


def fallbacks(needle: str, lang: str) -> list[str]:
    alts = []
    if lang == 'fr' and needle.endswith(' cru'):
        alts.append(needle[: -len(' cru')])
    if lang == 'en' and needle.startswith('Raw '):
        alts.append(needle[4:])
    # "Cookie (The Deadmines)" → parts handled separately
    m = re.match(r'^(.+?) \((.+)\)$', needle)
    if m:
        alts.append(m.group(1))
        alts.append(m.group(2))
    return alts


def walk_bilingual(obj, pred, path='root'):
    """Yield (holder, key, lang) for every bilingual fr/en string pair? We mutate cells in place via a visitor on any dict with fr+en strings, or individual strings at known places."""
    if isinstance(obj, dict):
        if 'fr' in obj and 'en' in obj and isinstance(obj.get('fr'), str) and isinstance(obj.get('en'), str):
            pred(obj, path)
        for k, v in obj.items():
            if k in ('fr', 'en') and isinstance(v, str):
                continue
            walk_bilingual(v, pred, f'{path}.{k}')
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk_bilingual(v, pred, f'{path}[{i}]')


def extract_where_name(where: str) -> str | None:
    m = re.search(r'«\s*([^»]+?)\s*»', where or '')
    return m.group(1).strip() if m else None


def find_rows(article, name: str) -> list[list]:
    rows = []
    if not article or not name:
        return rows
    for s in article.get('sections') or []:
        for b in s.get('blocks') or []:
            if b.get('type') != 'table':
                continue
            for row in b.get('rows') or []:
                blob = ' '.join((c.get('fr') or '') + ' ' + (c.get('en') or '') for c in row)
                if name in blob:
                    rows.append(row)
    return rows


def apply_link_to_bilingual(obj, link, max_len, scope_label):
    """Try wrap fr/en on one bilingual dict."""
    applied = 0
    for lang, key in (('fr', 'on_text_fr'), ('en', 'on_text_en')):
        needle = (link.get(key) or '').strip()
        href = link.get('to_fr') if lang == 'fr' else link.get('to_en')
        if not needle or not href:
            continue
        candidates = [needle] + fallbacks(needle, lang)
        status = 'missing'
        new = obj[lang]
        used = needle
        for cand in candidates:
            new, status = wrap(obj[lang], cand, href, max_len)
            if status == 'ok':
                obj[lang] = new
                applied += 1
                used = cand
                break
            if status == 'already':
                used = cand
                break
        if status not in ('ok', 'already', 'missing'):
            misses.append({'scope': scope_label, 'needle': used, 'lang': lang, 'status': status, 'href': href})
        elif status == 'missing' and needle:
            # recorded later if nothing on the page hits
            pass
        stats[f'wrap-{status}'] += 1
    return applied


def apply_links_on_article(entry, links, where):
    art = entry.get('article') or {}
    name = extract_where_name(where)
    rows = find_rows(art, name) if name else []
    applied = 0
    # Prefer row scope when we found the named row
    targets = []
    if rows:
        for row in rows:
            for cell in row:
                if isinstance(cell, dict) and 'fr' in cell:
                    targets.append((cell, CELL_MAX, f"{entry['id']}:{where}:row"))
    # Always also allow other bilingual fields if row scope missed a link
    def collect(obj, path):
        # skip if already in row targets
        if rows and any(obj is cell for row in rows for cell in row):
            return
        # determine max
        mx = CELL_MAX if 'rows' in path or 'head' in path or 'caption' in path else TEXT_MAX
        # don't wrap title/slug
        if '.slug' in path or path.endswith('.title') or '.title.' in path and 'article.title' in path:
            return
        targets_extra.append((obj, mx, f"{entry['id']}:{path}"))
    targets_extra = []
    walk_bilingual(art, collect, 'article')
    # First pass: row cells
    pending = list(links)
    def run_on(target_list, only_pending=True):
        nonlocal applied
        still = []
        for link in pending if only_pending else links:
            hit = 0
            for obj, mx, lab in target_list:
                before_fr, before_en = obj.get('fr'), obj.get('en')
                apply_link_to_bilingual(obj, link, mx, lab)
                if obj.get('fr') != before_fr or obj.get('en') != before_en:
                    hit += 1
                    applied += 1
            if not hit:
                still.append(link)
        return still
    if rows:
        pending = run_on(targets)
    if pending:
        pending = run_on(targets_extra, only_pending=True)
    if pending:
        # last attempt: split "X (Y)" already in fallbacks; record misses
        for link in pending:
            # skip generic invented labels
            for lang, key in (('fr', 'on_text_fr'), ('en', 'on_text_en')):
                needle = (link.get(key) or '').strip()
                if not needle:
                    continue
                if needle.lower() in ('plans par zone', 'blueprints by zone'):
                    stats['skipped-invented-label'] += 1
                    continue
                misses.append({
                    'id': entry['id'], 'where': where, 'needle': needle, 'lang': lang,
                    'to': link.get('to_id'), 'status': 'missing-on-page',
                })
                stats['missing-on-page'] += 1
    return applied


def copy_client_sources(from_entry, to_entry):
    have = {(s.get('key') or s.get('url')) for s in to_entry.get('sources') or []}
    added = 0
    for s in from_entry.get('sources') or []:
        key = s.get('key') or ''
        if not key.startswith('client-'):
            continue
        if key in have:
            continue
        to_entry.setdefault('sources', []).append(copy.deepcopy(s))
        have.add(key)
        added += 1
    if len(to_entry['sources']) > 20:
        raise SystemExit(f"too many sources on {to_entry['id']}: {len(to_entry['sources'])}")
    return added


def add_history_item(entry, src_keys):
    art = entry.get('article')
    if not art:
        return
    item = {'fr': HIST_FR, 'en': HIST_EN, 'src': src_keys[:8]}
    sec = next((s for s in art.get('sections') or [] if s['id'] == 'historique-des-corrections'), None)
    if not sec:
        art.setdefault('sections', []).append({
            'id': 'historique-des-corrections',
            'title': {'fr': 'Historique des corrections', 'en': 'Correction history'},
            'blocks': [{'type': 'list', 'items': [item], 'src': src_keys[:8]}],
        })
        return
    for b in sec.get('blocks') or []:
        if b.get('type') == 'list':
            # avoid duplicate
            if any('lot v40' in (it.get('fr') or '') for it in b.get('items') or []):
                return
            b.setdefault('items', []).append(item)
            return
    sec.setdefault('blocks', []).append({'type': 'list', 'items': [item], 'src': src_keys[:8]})


def parse_recipe_line(text_fr, text_en):
    # "Pattern: X — Monster — /fr/path/"
    def split(s):
        parts = [p.strip() for p in (s or '').split('—')]
        return parts
    a, b = split(text_fr), split(text_en)
    return a, b


def add_loot_section(entry, insertions, blueprints_href=True):
    art = entry['article']
    if any(s['id'] == 'recettes-au-butin' for s in art.get('sections') or []):
        notes.append(f"{entry['id']}: recettes-au-butin already present")
        return 0
    rows = []
    src = ['client-datenbank'] if any((s.get('key') or '').startswith('client-datenbank') for s in entry['sources']) else ['client-npc-liste']
    # prefer keys that exist
    keys = { (s.get('key') or '').rsplit('-',1)[0] if (s.get('key') or '').endswith(('-fr','-en')) else (s.get('key') or '')
             for s in entry['sources']}
    if 'client-datenbank' not in keys and 'client-npc-liste' in keys:
        src = ['client-npc-liste']
    elif 'client-datenbank' in keys:
        src = ['client-datenbank']
    elif 'client-npc-liste' in keys:
        src = ['client-npc-liste']
    else:
        src = ['client-npc-liste']
    for ins in insertions:
        tf, te = ins.get('text_fr') or '', ins.get('text_en') or ''
        pf, pe = parse_recipe_line(tf, te)
        rec_fr = pf[0] if pf else tf
        rec_en = pe[0] if pe else te
        mon_fr = pf[1] if len(pf) > 1 else ''
        mon_en = pe[1] if len(pe) > 1 else mon_fr
        path_fr = pf[2] if len(pf) > 2 else '/fr/metiers/recettes-et-plans-avances/'
        path_en = pe[2] if len(pe) > 2 else '/en/professions/recipes-and-advanced-blueprints/'
        # wrap recipe name toward blueprints
        rec_fr_l = f'[{rec_fr}]({path_fr})' if rec_fr and path_fr.startswith('/fr/') else rec_fr
        rec_en_l = f'[{rec_en}]({path_en})' if rec_en and path_en.startswith('/en/') else rec_en
        row = [
            {'fr': rec_fr_l, 'en': rec_en_l},
            {'fr': mon_fr, 'en': mon_en},
        ]
        for c in row:
            for lang in ('fr', 'en'):
                if len(c[lang]) > CELL_MAX:
                    raise SystemExit(f'loot cell too long {entry["id"]} {c[lang][:80]}')
        rows.append(row)
    if not rows:
        return 0
    section = {
        'id': 'recettes-au-butin',
        'title': {'fr': 'Recettes au butin', 'en': 'Loot recipes'},
        'blocks': [
            {
                'type': 'p',
                'fr': (
                    "Les recettes ci-dessous figurent déjà sur la page des "
                    "[plans et recettes avancées](/fr/metiers/recettes-et-plans-avances/). "
                    "Elles sont reprises ici par monstre, sans fait nouveau. "
                    "Données du jeu, client 1.60.1.70862 — ce n’est pas une confirmation officielle."
                ),
                'en': (
                    "The recipes below already appear on the "
                    "[recipes and advanced blueprints](/en/professions/recipes-and-advanced-blueprints/) "
                    "sheet. They are repeated here by monster, with no new facts. "
                    "Game data, client 1.60.1.70862 — this is not an official confirmation."
                ),
                'src': src,
            },
            {
                'type': 'table',
                'caption': {
                    'fr': f"{len(rows)} recettes à butin déjà listées sur la page des plans avancés — données du jeu, client 1.60.1.70862.",
                    'en': f"{len(rows)} loot recipes already listed on the advanced blueprints sheet — game data, client 1.60.1.70862.",
                },
                'head': [
                    {'fr': 'Recette', 'en': 'Recipe'},
                    {'fr': 'Monstre', 'en': 'Monster'},
                ],
                'rows': rows,
                'src': src,
            },
        ],
    }
    secs = art.setdefault('sections', [])
    idx = next((i for i, s in enumerate(secs) if s['id'] == 'historique-des-corrections'), len(secs))
    secs.insert(idx, section)
    return len(rows)


def add_boss_section(entry, names, bosses_lookup):
    art = entry['article']
    if any(s['id'] == 'pnj-donnees-du-jeu' for s in art.get('sections') or []):
        notes.append(f"{entry['id']}: pnj-donnees-du-jeu already present")
        return 0
    src = ['client-npc-liste']
    rows = []
    for fr, en in names:
        info = bosses_lookup.get(en) or bosses_lookup.get(fr) or {}
        level = info.get('level') or 'non indiqué / not given'
        # keep bilingual level as in bestiary
        lvl_fr = info.get('level_fr') or info.get('level') or 'non indiqué dans la liste'
        lvl_en = info.get('level_en') or info.get('level') or 'not given in the list'
        name_fr = fr
        name_en = en
        href_fr = '/fr/creatures/bestiaire-bosses/'
        href_en = '/en/creatures/bestiary-bosses/'
        rows.append([
            {'fr': f'[{name_fr}]({href_fr})', 'en': f'[{name_en}]({href_en})'},
            {'fr': lvl_fr, 'en': lvl_en},
            {'fr': 'données du jeu', 'en': 'game data'},
        ])
    section = {
        'id': 'pnj-donnees-du-jeu',
        'title': {'fr': 'Boss dans les données du jeu', 'en': 'Bosses in the game data'},
        'blocks': [
            {
                'type': 'p',
                'fr': (
                    "Noms extraits de la liste de PNJ du client 1.60.1.70862, déjà publiés dans le "
                    "[bestiaire des boss](/fr/creatures/bestiaire-bosses/). "
                    "Ce n’est pas une confirmation officielle du roster par Blizzard."
                ),
                'en': (
                    "Names taken from the client 1.60.1.70862 NPC list, already published in the "
                    "[bosses bestiary](/en/creatures/bestiary-bosses/). "
                    "This is not an official Blizzard confirmation of the roster."
                ),
                'src': src,
            },
            {
                'type': 'table',
                'caption': {
                    'fr': f"{len(rows)} boss étiquetés dans la liste de PNJ Forever — données du jeu, client 1.60.1.70862.",
                    'en': f"{len(rows)} bosses tagged in the Forever NPC list — game data, client 1.60.1.70862.",
                },
                'head': [
                    {'fr': 'Nom', 'en': 'Name'},
                    {'fr': 'Niveau', 'en': 'Level'},
                    {'fr': 'Statut', 'en': 'Status'},
                ],
                'rows': rows,
                'src': src,
            },
        ],
    }
    secs = art.setdefault('sections', [])
    idx = next((i for i, s in enumerate(secs) if s['id'] == 'historique-des-corrections'), len(secs))
    secs.insert(idx, section)
    rel = entry.setdefault('relations', [])
    if 'forever-bestiary-bosses' not in rel:
        rel.append('forever-bestiary-bosses')
    return len(rows)


def bosses_index(by_id):
    e = by_id['forever-bestiary-bosses']
    out = {}
    for s in e['article']['sections']:
        for b in s.get('blocks') or []:
            if b.get('type') != 'table':
                continue
            for row in b['rows']:
                en = row[0]['en']
                fr = row[0]['fr']
                rec = {
                    'level_fr': row[1]['fr'],
                    'level_en': row[1]['en'],
                    'zone_en': row[5]['en'],
                    'zone_fr': row[5]['fr'],
                }
                out[en] = rec
                out[fr] = rec
    return out


def preferred_hist_src(entry):
    keys = []
    for s in entry.get('sources') or []:
        k = s.get('key')
        if not k:
            continue
        base = re.sub(r'-(fr|en)$', '', k)
        if base not in keys:
            keys.append(base)
    return keys[:8] or ['bz-dungeons']


def main():
    records, by_id, batch = load()
    bosses = bosses_index(by_id)
    client_src_from = by_id['forever-bestiary-bosses']
    OUT.mkdir(parents=True, exist_ok=True)
    changed_ids = []

    for page in batch['pages']:
        pid = page['page_id']
        entry = copy.deepcopy(by_id[pid])
        original = json.dumps(by_id[pid], ensure_ascii=False, sort_keys=True)
        insertions = page['insertions']
        if all(i.get('status') == 'already-on-page' for i in insertions):
            notes.append(f'{pid}: all insertions already-on-page; renderer will auto-link bare paths; no revise')
            stats['skipped-already-on-page-pages'] += 1
            continue

        loot_ins = [i for i in insertions if i.get('text_fr') and 'recettes-au-butin' in (i.get('where') or '')]
        name_links = [i for i in insertions if i.get('add_links') and i.get('status') != 'already-on-page']

        # Official dungeon pages: add game-data boss roster when names are not already on the page
        if pid in {
            'forever-dungeon-city-of-dalaran',
            'forever-dungeon-hall-of-thanes',
            'forever-dungeon-excavation-site',
            'forever-dungeon-ruins-of-lordaeron',
        }:
            copy_client_sources(client_src_from, entry)
            names = []
            for ins in name_links:
                for L in ins['add_links']:
                    if L.get('to_id') == 'forever-bestiary-bosses' and L.get('on_text_en'):
                        names.append((L.get('on_text_fr') or L['on_text_en'], L['on_text_en']))
            # dedupe
            seen = set()
            uniq = []
            for n in names:
                if n[1] not in seen:
                    seen.add(n[1])
                    uniq.append(n)
            if uniq:
                add_boss_section(entry, uniq, bosses)
                stats['boss-sections'] += 1

        if loot_ins:
            if pid == 'forever-dungeon-ruins-of-lordaeron':
                copy_client_sources(client_src_from, entry)
            n = add_loot_section(entry, loot_ins)
            stats['loot-rows'] += n

        # Onyxia creature: relations
        if pid == 'forever-creature-onyxia':
            rel = entry.setdefault('relations', [])
            for ins in name_links:
                for L in ins['add_links']:
                    tid = L.get('to_id')
                    if tid and tid not in rel and tid != entry['id']:
                        rel.append(tid)
                        stats['relations-added'] += 1

        # Onyxia raid short entry: relation already present; no article text to wrap
        if pid == 'forever-raid-onyxias-lair':
            rel = entry.setdefault('relations', [])
            for ins in name_links:
                for L in ins['add_links']:
                    tid = L.get('to_id')
                    if tid and tid not in rel and tid != entry['id']:
                        rel.append(tid)
                        stats['relations-added'] += 1
            # description does not contain the word Onyxia — do not invent it
            notes.append(f'{pid}: relation to creature already present; no “Onyxia” string in the short description, left unchanged')

        # Wrap existing text
        for ins in name_links:
            apply_links_on_article(entry, ins.get('add_links') or [], ins.get('where') or '')

        add_history_item(entry, preferred_hist_src(entry))

        now = json.dumps(entry, ensure_ascii=False, sort_keys=True)
        if now == original:
            notes.append(f'{pid}: no content change after apply')
            stats['unchanged'] += 1
            continue
        # strip review for incoming revise payload
        entry['status'] = 'draft'
        entry['identityConfirmed'] = False
        entry.pop('review', None)
        outp = OUT / f'{pid}.json'
        outp.write_text(json.dumps(entry, ensure_ascii=False, indent=2) + '\n')
        changed_ids.append(pid)
        stats['revised'] += 1

    report = {
        'changed_ids': changed_ids,
        'stats': dict(stats),
        'misses': misses,
        'notes': notes,
        'n_misses': len(misses),
    }
    (OUT / '_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('changed_ids', 'stats', 'n_misses', 'notes')}, ensure_ascii=False, indent=2))
    # print miss summary
    from collections import Counter
    c = Counter((m.get('id'), m.get('needle')) for m in misses)
    print('miss samples', list(c.items())[:25], 'unique', len(c))


if __name__ == '__main__':
    main()
