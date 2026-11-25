#!/usr/bin/env python3
"""Assemble the v41 collections dataset (mounts, pets, toys, legacy) from WoW Forever client files
(official Blizzard CDN, product wowf, build 1.60.1.70862) + official Blizzard articles + Forever quest data."""
import json, glob, re, collections
from load import T
OUT = '../out/collections.json'
BUILD = '1.60.1.70862'

it = T('Item'); sp = T('ItemSparse'); spf = T('ItemSparse', 'frFR')
ie = T('ItemEffect'); ix = T('ItemXItemEffect')
spell = T('Spell'); spellf = T('Spell', 'frFR'); sname = T('SpellName'); snamef = T('SpellName', 'frFR')
se = T('SpellEffect'); sla = T('SkillLineAbility'); sk = T('SkillLine'); skf = T('SkillLine', 'frFR')
fac = T('Faction'); facf = T('Faction', 'frFR')
mount = T('Mount'); mountf = T('Mount', 'frFR')
pets = T('BattlePetSpecies'); petsf = T('BattlePetSpecies', 'frFR')
cre = T('Creature'); cref = T('Creature', 'frFR')
toys = T('Toy')

item_spells = collections.defaultdict(list)
for r in ix.values():
    e = ie.get(r['ItemEffectID'])
    if e and e['SpellID'] > 0: item_spells[r['ItemID']].append(e['SpellID'])
m_by_spell = {m['SourceSpellID']: m for m in mount.values()}
p_by_spell = {p['SummonSpellID']: p for p in pets.values()}

# crafted-by
craft = collections.defaultdict(list)
spell_skill = {r['Spell']: r for r in sla.values()}
for e in se.values():
    if e['Effect'] == 24 and e['EffectItemType']:
        craft[e['EffectItemType']].append(e['SpellID'])

# quests
QE, QF = {}, {}
for f in glob.glob('../cache/quests/en-*.json'):
    QE.update({int(k): v for k, v in json.load(open(f)).items()})
for f in glob.glob('../cache/quests/fr-*.json'):
    QF.update({int(k): v for k, v in json.load(open(f)).items()})
qrew = collections.defaultdict(list)
for qid, q in QE.items():
    for b in q.get('belohnung', []):
        for x in b.get('items', []):
            qrew[x['id']].append((qid, b.get('art')))

STAND = {0: ('Détesté', 'Hated'), 1: ('Hostile', 'Hostile'), 2: ('Inamical', 'Unfriendly'), 3: ('Neutre', 'Neutral'),
         4: ('Amical', 'Friendly'), 5: ('Honoré', 'Honored'), 6: ('Révéré', 'Revered'), 7: ('Exalté', 'Exalted')}
TEST = re.compile(r'(?i)\b(test|deprecated|deptecated|summoning|old|unused|qa|ph|zzold|monster -|dnd)\b|\[|^\s*$')

def faction(item):
    ar = item.get('AllowableRace') or [-1, -1]
    lo = ar[0] & 0xFF if isinstance(ar, list) else -1
    if ar[0] == -1 or lo == 0xFF or lo == 0: return 'both'
    a = lo & 0x4D; h = lo & 0xB2
    if a and not h: return 'alliance'
    if h and not a: return 'horde'
    return 'both'

def money(c):
    if not c: return None
    g, s, cu = c // 10000, (c // 100) % 100, c % 100
    return {'g': g, 's': s, 'c': cu}

def official():
    return {
        277718: dict(kind='heritage', fr='Récompense d’héritage du lancement : points d’héritage cumulés sur le compte (palier non publié)',
                     en='Launch Legacy reward: Legacy points earned across the account (threshold not published)', src='bz-legacy'),
        276236: dict(kind='heritage', fr='Récompense d’héritage du lancement (nommée « Réplique de carabine à air comprimé de Forgefer » par Blizzard) : points d’héritage cumulés sur le compte (palier non publié)',
                     en='Launch Legacy reward (named “Replica Ironforge Air Rifle” by Blizzard): Legacy points earned across the account (threshold not published)', src='bz-legacy'),
        277717: dict(kind='heritage', fr='Récompense d’héritage du lancement : points d’héritage cumulés sur le compte (palier non publié)',
                     en='Launch Legacy reward: Legacy points earned across the account (threshold not published)', src='bz-legacy'),
        277714: dict(kind='heritage', fr='Récompense d’héritage du lancement : points d’héritage cumulés sur le compte (palier non publié)',
                     en='Launch Legacy reward: Legacy points earned across the account (threshold not published)', src='bz-legacy'),
        280544: dict(kind='pack', fr='Pack héroïque des Éolides (aussi dans le pack épique des Éolides et la Warcraft Forever Collection) ; la compétence de monte s’achète en jeu',
                     en='Skyborne Heroic Pack (also in the Skyborne Epic Pack and the Warcraft Forever Collection); riding skill is bought in-game', src='bz-pack'),
        280740: dict(kind='pack', fr='Pack héroïque des Éolides (aussi dans le pack épique des Éolides et la Warcraft Forever Collection)',
                     en='Skyborne Heroic Pack (also in the Skyborne Epic Pack and the Warcraft Forever Collection)', src='bz-pack'),
    }
OFF = official()

# Règle permanente de Mathieu : feu de camp / sac de couchage / Clé de pierre / Communauté restent non publiés.
# 289439 « Bourse de poussière pourpre » (jouet lié au feu de camp de la célébration de lancement) est donc écarté.
HELD_BACK = {289439}
UNPUB = re.compile(r'(?i)campfire|sleeping bag|stone key|feu de camp|sac de couchage|clé de pierre')

def base(iid, kind):
    if iid in HELD_BACK: return None
    s = sp.get(iid); f = spf.get(iid, {})
    if not s or not s.get('Display_lang'): return None
    name_en = s['Display_lang']; name_fr = f.get('Display_lang') or name_en
    if TEST.search(name_en): return None
    if UNPUB.search(name_en + ' ' + (s.get('Description_lang') or '')): return None
    sids = item_spells.get(iid, [])
    spl = [x for x in sids if x not in (483, 55884)] or sids
    sd_en = sd_fr = ''
    for x in spl:
        if spell.get(x, {}).get('Description_lang'):
            sd_en = spell[x]['Description_lang']; sd_fr = spellf.get(x, {}).get('Description_lang', '') or sd_en; break
    r = dict(id=iid, kind=kind, name_en=name_en, name_fr=name_fr,
             desc_en=s.get('Description_lang', ''), desc_fr=f.get('Description_lang', ''),
             use_en=sd_en, use_fr=sd_fr,
             quality=s['OverallQualityID'], level=s['RequiredLevel'], ilvl=s['ItemLevel'],
             buy=money(s['BuyPrice']), faction=faction(s), bonding=s['Bonding'],
             icon=it.get(iid, {}).get('IconFileDataID'), spells=spl)
    if s['RequiredSkill']:
        r['skill'] = dict(en=sk.get(s['RequiredSkill'], {}).get('DisplayName_lang'), fr=skf.get(s['RequiredSkill'], {}).get('DisplayName_lang'), rank=s['RequiredSkillRank'])
    if s['MinFactionID']:
        st = STAND.get(s['MinReputation'], ('?', '?'))
        r['rep'] = dict(en=fac.get(s['MinFactionID'], {}).get('Name_lang'), fr=facf.get(s['MinFactionID'], {}).get('Name_lang'), st_fr=st[0], st_en=st[1])
    if s['RequiredPVPRank']: r['pvprank'] = s['RequiredPVPRank']
    # obtention
    how = []
    if iid in OFF: how.append(dict(OFF[iid], type=OFF[iid]['kind']))
    for spid in craft.get(iid, []):
        a = spell_skill.get(spid)
        if a and a['SkillLine'] in sk:
            how.append(dict(type='craft', prof_en=sk[a['SkillLine']]['DisplayName_lang'], prof_fr=skf[a['SkillLine']]['DisplayName_lang'],
                            rank=a['MinSkillLineRank'], spell_en=sname.get(spid, {}).get('Name_lang'), spell_fr=snamef.get(spid, {}).get('Name_lang')))
    for qid, art in qrew.get(iid, []):
        q = QE[qid]; qf = QF.get(qid, {})
        st = q.get('start') or {}; stf = qf.get('start') or {}
        how.append(dict(type='quest', qid=qid, q_en=q.get('n'), q_fr=qf.get('n') if qf.get('n') and 'tqn' not in qf else None,
                        choice=(art == 'wahl'), lv=q.get('lv'), minlv=q.get('min'), fac=q.get('f'), zone_en=q.get('zone'), zone_fr=qf.get('zone'),
                        npc_en=st.get('npc'), npc_fr=stf.get('npc'), loc_en=st.get('ort'), loc_fr=stf.get('ort'), build=q.get('tqb')))
    r['how'] = how
    return r

data = {'build': BUILD, 'mounts': [], 'pets': [], 'toys': []}
seen = set()
def is_mount(iid, row):
    return (row['ClassID'] == 15 and row['SubclassID'] == 5) or (row['ClassID'] in (0, 15) and any(x in m_by_spell for x in item_spells.get(iid, [])))
def is_pet(iid, row):
    return (row['ClassID'] == 15 and row['SubclassID'] == 2) or (row['ClassID'] in (0, 15) and any(x in p_by_spell for x in item_spells.get(iid, [])))
for iid, row in sorted(it.items()):
    if is_mount(iid, row):
        b = base(iid, 'mount')
        if b:
            m = next((m_by_spell[x] for x in item_spells.get(iid, []) if x in m_by_spell), None)
            if m:
                b['mount_id'] = m['ID']; b['mname_en'] = m['Name_lang']; b['mname_fr'] = mountf.get(m['ID'], {}).get('Name_lang')
                b['mdesc_en'] = m['Description_lang']; b['mdesc_fr'] = mountf.get(m['ID'], {}).get('Description_lang')
            data['mounts'].append(b); seen.add(iid)
    elif is_pet(iid, row):
        b = base(iid, 'pet')
        if b:
            p = next((p_by_spell[x] for x in item_spells.get(iid, []) if x in p_by_spell), None)
            if p:
                b['species'] = p['ID']; b['pet_icon'] = p['IconFileDataID']
                c = cre.get(p['CreatureID']); cf = cref.get(p['CreatureID'])
                if c: b['cname_en'] = c['Name_lang']; b['cname_fr'] = (cf or {}).get('Name_lang')
                b['pdesc_en'] = p['Description_lang']; b['pdesc_fr'] = petsf.get(p['ID'], {}).get('Description_lang')
            data['pets'].append(b); seen.add(iid)
for t in toys.values():
    iid = t['ItemID']
    if iid in seen: continue
    b = base(iid, 'toy')
    if b: data['toys'].append(b)
# class mounts (spells, no item) — names from Mount.db2, icon from SpellMisc, obtention from quest data ("lernt")
smisc = {r['SpellID']: r for r in T('SpellMisc').values()}
learn = collections.defaultdict(list)
for qid, q in QE.items():
    for nm in q.get('lernt', []) or []: learn[nm].append(qid)
seen_names = set()
for mid in sorted(mount):
    m = mount[mid]
    if m['SourceSpellID'] in {x for b in data['mounts'] for x in b['spells']}: continue
    if not m['Name_lang'].startswith('Summon ') or m['Flags'] not in (0, 4) or 'Qiraji' in m['Name_lang']: continue
    if m['Name_lang'] in seen_names: continue
    seen_names.add(m['Name_lang'])
    sid = m['SourceSpellID']
    how = []
    for qid in learn.get(sname.get(sid, {}).get('Name_lang', m['Name_lang']), []) or learn.get(m['Name_lang'], []):
        q = QE[qid]; qf = QF.get(qid, {}); st = q.get('start') or {}; stf = qf.get('start') or {}
        how.append(dict(type='quest', qid=qid, q_en=q.get('n'), q_fr=qf.get('n') if qf.get('n') and 'tqn' not in qf else None, choice=False,
                        lv=q.get('lv'), minlv=q.get('min'), fac=q.get('f'), zone_en=q.get('zone'), zone_fr=qf.get('zone'), npc_en=st.get('npc'), npc_fr=stf.get('npc'),
                        loc_en=st.get('ort'), loc_fr=stf.get('ort'), build=q.get('tqb'), learns=True))
    data['mounts'].append(dict(id=None, spell_mount=True, mount_id=mid, kind='mount', name_en=m['Name_lang'], name_fr=mountf.get(mid, {}).get('Name_lang') or m['Name_lang'],
        desc_en='', desc_fr='', use_en=spell.get(sid, {}).get('Description_lang', ''), use_fr=spellf.get(sid, {}).get('Description_lang', ''),
        quality=None, level=None, ilvl=None, buy=None, faction='both', bonding=None, icon=smisc.get(sid, {}).get('SpellIconFileDataID'), spells=[sid], how=how))
# official-only entries absent from the client files we can read
data['pets'].append(dict(id=None, official_only=True, kind='pet', name_en='Azurky', name_fr='Azurbie', desc_en='', desc_fr='', use_en='', use_fr='',
    quality=None, level=None, ilvl=None, buy=None, faction='both', bonding=None, icon=None, spells=[],
    how=[dict(type='subscription', fr='Abonnement : offre spéciale 6 ou 12 mois (bonus à récupérer avant le 30 avril 2027)',
              en='Subscription: 6- or 12-month special offer (bonus to redeem by 30 April 2027)', src='bz-sub-year')]))
# legacy tabard (official) for heritage page
for iid in sp:
    if sp[iid]['Display_lang'] in ('Spectral Bear Tabard',):
        b = base(iid, 'tabard'); b['how'] = [dict(type='heritage', fr=OFF[277718]['fr'], en=OFF[277718]['en'], src='bz-legacy')]; data['tabard'] = b
json.dump(data, open(OUT, 'w'), ensure_ascii=False, indent=1)
for k in ('mounts', 'pets', 'toys'):
    c = collections.Counter(h['type'] for x in data[k] for h in x['how'][:1]) ; n0 = sum(1 for x in data[k] if not x['how'])
    print(k, len(data[k]), dict(c), 'no-how', n0)
print('tabard', data.get('tabard', {}).get('id'))
