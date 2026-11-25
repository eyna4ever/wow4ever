# Wowkipedia completion — Phase 1 inventory
Date: 2026-11-13 (Europe/Paris). No publication, no deploy, v38 tree not touched.

Source of already-extracted data (on disk, used for v34–v37):
- NPC list JSON (3,284 rows, EN+FR): `../bestiaire/sources/npc-liste-*.json`, Forever-labelled, item DB cites client 1.60.1.70862 (7 Nov 2026).
- 2,153 profession recipes + collections (pets/mounts/toys): `../recettes-metiers/brouillons/`.
- 55 drop-recipe item pages and 121 monster–recipe pairs: `../recettes-pnj/`.
- 37 fish: `../bestiaire/import-batches/poissons-v37.entries.json`.
- Official Blizzard sheets already on the live wiki (v37).

Targeted public hub/sample checks on 13 Nov 2026 (not a crawl; evidence in `sources/`): map hub + Zephras map, quests hub + index/zonen + one shard (0.json), sets hub, dungeons hub + Hall of Thanes, NPC hub, trainers hub. Wowhead and warcraft.wiki.gg were not used.

Third-party database: Forever-labelled, “read from game files”, mixed with a player addon. No reuse licence. Mathieu has already allowed Forever client-extracted data; addon-only facts stay communautaire / « à confirmer ». Headline totals from that site are not publication targets (especially quest and faction totals).

## 1. Bestiary — type, elite/rare, FR names, loot

| Need | On disk now | At the Forever-labelled source (sampled, not imported) | Missing |
|---|---|---|---|
| Names EN | 3,284 | Same list | — |
| Names FR | 0 distinct: the FR JSON repeats the English names. A few rows are German leftovers (e.g. loot-flagged “Alter Schattenhornhirsch”). | FR NPC hub uses the same JSON. | Almost all French NPC names |
| Zone | 76 canon zones + 202 unlocated; 2 raw labels for Zephras (“Zephras Isle” 72, “Insel Zephras” 9) | Same | 202 unlocated |
| Role tags | quest giver 1,989; objective 1,179; boss 91; vendor 30; loot-flagged 9; trainer tag: 0 | Individual pages and the trainers page have more roles than the list | Most vendors and all trainers untagged in the list (Elwynn: 0 vendors tagged) |
| Level | 206 / 3,284 (mostly bosses 87/91 and vendors 30/30) | Trainers and some dungeon pages give levels | Vast majority of open-world NPCs |
| Creature type (beast, humanoid…) | Not in the list (empty field) | Not seen in the list format | Entirely missing from the extract we have |
| Elite / rare | No elite or rare tag. Official Blizzard text mentions rare-creature loot without a list. | Rares sitemap path `/en/seltene/` is 404 | No list |
| Loot | 9 “loot flagged” only, no item names in the list. Recipe drops: 121 pairs already documented (v34). | Individual NPC pages claimed to have loot; dungeon pages have named drops (see §6). Hall of Thanes: “no values for the boss loot yet”; boss assignment “from the fan addon”. | Full creature loot tables, drop rates, pick-pocket, skinning |

Live wiki: 10 bestiary index pages + official notes, Onyxia, foxes. No per-creature sheets.

## 2. Fish — zones and required skill

On disk: 37 fish/related catches (4 new-Forever, 24 cooking, etc.). **Zones: 0. Required skill: 0. Vendors: 0.**
The Forever fishing guide’s “Zones (Classic)” table was correctly rejected (it warns locations may differ). No Forever catch-by-zone table (including Zephras / Shen’dralas) was found in item pages, profession guides, or the Zephras map (only camping fishing *quests*, not fishing spots). No fishing JSON endpoint found.
**Cannot be completed from existing data.** Needs a new Forever source or in-game verification. Keep cells “non indiqué”.

## 3. Quests — by zone (NPC, rewards, chains)

Live wiki: 12 thematic sheets (legacy, Valthalak, attunements, Gelkis/Magram, expanded rewards, official “1,000+ new quests” announcement). No per-zone quest lists.

On disk: only a handful of cooking/camping quests consulted for v34.

At the source (sampled 13 Nov):
- An index JSON and 64 sharded detail files exist (same `/en/daten/` pattern as the NPC list). The index is a third-party total we will **not** use as a target or a published census.
- Index fields: id, name (EN), zone or category, level, required level, faction, chain flag. 103 “zone” labels including categories (Crafting, Camping, class names). Empty zone on 106 rows. Forever-named examples in the index: Zephras Isle 113, Shen’dralas 19, Hall of Thanes 4, Ruins of Lordaeron 12, Excavation Site 14, Dalaran 8, Riverglades **1**.
- Shard 0 (69 quests, one of 64 shards) field coverage: start NPC 67/69, start coordinates ~60/69 (format “Westfall 60, 19.4”), end NPC 65, objective 61, quest text 60, rewards/XP/rep 59, multi-step chain 38, money 12. Some texts German-only (`de` flag). `tqf` is a German-text flag, not a French translation. French quest text not seen in this shard.
- Sources are mixed: client quest data, plus addon contributions. Hall of Thanes page itself notes contradictions (addon vs quest files, EN names from addon / DE in files).

Feasible as a later extract lot, with strict client-vs-addon labelling, no headline totals, FR names often missing.

## 4. Zones — full sheet (levels, NPCs, vendors, flight points)

Live wiki: 4 Forever zone sheets (Zephras, Riverglades, Hyjal, Shen’dralas) plus an index and a named-places page that already says **no coordinates**.

On disk, cheap and fully sourced from the NPC list (see `zone-npc-counts.tsv`):
- Per-zone NPC roster and role tags for 76+ zones.
- Not in that list: zone level ranges, flight points (almost no flight-master names; no flight role), vendor inventories, trainer lists (0 trainer tags), sub-zones, gathering nodes.
- Vendor tags are far too scarce (30 total) to call a zone sheet “complete” on vendors.
- Trainers with coordinates exist on a separate trainers page (starting-zone class trainers, including Zephras: e.g. Windshaper Boro 42.7, 23.5) — not yet imported.
- Map coordinates exist at the source for 45 zones / 1,995 places (see map section); Shen’dralas, Riverglades and Hyjal are **not** among those 45 maps.

A useful first lot: zone sheets that honestly list what the NPC extract has, and leave flight points / levels / full vendors as “non indiqué” until extracted.

## 5. Items — gear and sets, stats and sources

Live wiki: 2 unique items, loot/appearances policy (official), toys (2, official), pets (73: 2 official, 71 client, method unknown for 71), mounts (99: 2 official, 97 client, method unknown for 97).

On disk: 2,153 recipes (skill complete; source known for 824, unknown for 1,329; zone known for 59). Recipe item pages: quality, item level, bind, sell price, drop NPC + dungeon for all 55 “drop” recipes. No purchase prices (sell price only). No drop rates.

At the source:
- Sets hub: **154 sets**, pieces and set bonuses “as they appear in the game data”, by level (Dungeon Set 1, PvP Champion’s/Lieutenant Commander’s, etc.). Not yet extracted. No `sets.json` at the guessed path (404).
- Item catalog is advertised in the tens of thousands; the saved items sitemap has 1,125 URLs (incomplete sitemap or a subset). No `item-liste.json` (404).
- Hall of Thanes: item **names, slots, armor types** yes; **stat values no** (“we have no values for the boss loot yet”).
- Gear tooltips/stats: not verified on a broad sample; do not assume a complete stat database.

## 6. Dungeons / raids — loot by boss

Live wiki: 9 Forever dungeons + 3 raids (official levels, access, “loot: what is confirmed” = quality/appearance policy only). Pending text still says boss lists and loot tables were not taken from client extracts (written before the policy change). Bestiary already lists some dungeon NPCs/bosses from the NPC extract (5 official dungeons still have no roster: some Forever dungeons absent).

At the source (Hall of Thanes sample, 13 Nov):
- 4 bosses named, each with 3–4 named drops (13 drops + 1 quest item), slot and armor type, boss level 16 (“fan sites”; client dungeon list “content level 13”).
- 5 dungeon quests with givers, coords, faction, rewards.
- **No drop rates. No item stats.** Boss–loot assignment “from the fan addon.” Tactics mix client spell text and unconfirmed tips.
- Hub lists 31 dungeon pages (9 new + classic-named with reworked Forever loot) plus Dec 9 raids (Barrow Deeps, Hyjal Summit, Onyxia) — raid loot likely thin until then.

Usable later if client vs addon is separated; classic-era loot tables must not be substituted.

## 7. Links between pages

Already possible from data on disk, no new extract:
- 55 drop recipes ↔ 121 monster + zone pairs (v34 blueprints) → bestiary / dungeon sheets.
- Cooking recipes ↔ 24 fish (already linked on the fish page).
- NPC list ↔ 76 zones; 91 bosses ↔ dungeon names; 30 tagged vendors.
- Quest data (once extracted) would link quest ↔ NPC ↔ coords ↔ rewards ↔ chains.

Gaps: 1,329 recipes with unknown source; most creature loot; FR names.

## 8. Cartographer (interactive map)

**Coordinates exist.** Not in the NPC list JSON. Found at the source:

| Source | What | Coverage |
|---|---|---|
| 45 schematic zone maps, 1,995 places | x,y in percent, type (quest giver, turn-in, vendor, trainer, quest object; gathering reserved but empty on Zephras), name, faction, linked quests | 45 classic-named zones + **Zephras Isle (72 places)**. **No Shen’dralas, no Riverglades, no Hyjal.** Zephras sample: 54 quest givers, 14 turn-ins, 3 quest+vendor, 1 object. 0 gathering, 0 flight, 0 fishing spots, 0 bosses on that map. Explicitly: “Schematic map without game map images.” |
| Quest detail shards | `start.ort` / `ende.ort` like “Dun Morogh 30.2, 45.7” | ~60/69 in shard 0 (~87% of those with a start location) |
| Trainers page | Starting-zone class trainers with coords, including Zephras | Professional trainer locations were “not confirmed” on 12 Nov; the 13 Nov page still focuses on class trainers. Weapon masters: locations “Blizzard hasn't named.” |
| One NPC page (Zerril, 12 Nov) | 43.8, 43.8 “per quest data” | Anecdote; not a full NPC-coord dump |

**Lightest CSP-safe approach** (live CSP: `script-src 'self'; img-src 'self'; connect-src 'self'; style-src 'self'` — no external tiles, no third-party tooltips):

1. Self-hosted **SVG coordinate grid** per zone (viewBox matching in-game 0–100% x,y), vanilla JS vendored in-repo (no Leaflet CDN; Leaflet is unnecessary).
2. Filterable markers (quest giver, vendor, trainer, boss, object) from JSON we host ourselves.
3. Optional **original drawn zone outlines** (our art, like the existing v25 stylized Azeroth map, which is already original generated art with no Blizzard imagery). That overview is decorative, not a calibrated projection — do not pin exact coords on it without a measured transform.
4. Prototype: **Zephras only** (Forever-only, 72 places, already viewed).

**Legally usable imagery**
- Usable: our own grids and outlines; the existing original Azeroth illustration already on the site; self-hosted SVG markers.
- Not usable without an explicit copyright decision from Mathieu: Blizzard world maps, minimaps, tiles, or item icons (even from the client). Flag this if anyone proposes client map textures.
- Do not copy the third-party schematic artwork (their work, no licence). Recreate a simpler original grid. Do not use their icons (Blizzard ©, and CSP would also block hotlinking).

Addon-contributed pins and “later gathering nodes” stay « à confirmer » / communautaire.

## Proposed lots (after v38)

Skip PvP step 05 and the Heritage checklist (await Mathieu). No fish-zone lot until a Forever source appears.

1. **v39 — Zone sheets from the NPC extract already on disk.** Highest value, fully sourced, cheap. Rosters and roles per zone, links to the bestiary, Forever zones first. Honest “non indiqué” for flight points, level ranges, untagged vendors. No new crawl.
2. **v40 — Cross-links.** Recipe → monster (121 pairs) → dungeon/bestiary; fish → cooking (already partly done). Low risk.
3. **v41 — Cartographer prototype (Zephras), then the other 44 maps if approved.** High “wiki visuel” value. Extract place JSON for Zephras only first; original SVG grid; CSP-safe. Then decide on a wider coord extract (quest starts + map places), never Blizzard tiles.
4. **v42 — Quests by zone.** Large extract (index + shards), no published census totals, client vs addon vs official clearly marked, FR often missing. Forever-new zones first (Zephras, Shen’dralas, dungeon quests).
5. **v43 — Dungeon loot by boss.** Start with the nine Forever dungeons. Names/slots from game-data pages; leave stats and rates empty if absent; label addon-only boss assignments. Then classic-named dungeons with Forever loot only. Raids after 9 Dec if still empty.
6. **v44 — Sets and gear.** 154 sets + bonuses from game data is the solid core. Broader item stats only where tooltips actually contain values (Hall of Thanes warns many have none yet). Sources where known.
7. **Visual redesign (tiles, infobox, filters, dark blue/gold).** Can run in parallel from v39 (CSS, original CC0 icons already on the site). No Blizzard art. Infobox fields stay empty rather than invented.
8. **Bestiary type / elite / rare / FR names / full loot:** not doable from the current NPC list. Revisit only if a richer Forever client table appears or Mathieu provides in-game evidence.

## Drafts

None. No test-tree under `completion/`, no imports, no package. Only this inventory, `zone-npc-counts.tsv`, and the 13 Nov sample fetches in `sources/`.
