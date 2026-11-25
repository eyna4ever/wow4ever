#!/usr/bin/env python3
"""Build RECETTES_PNJ.csv — research only, 2026-11-12. No invented facts."""
import csv, pathlib
HERE = pathlib.Path(__file__).resolve().parent
ACC = '2026-11-12'
# Official URLs
CAMP_FR = 'https://news.blizzard.com/fr-fr/article/24301516/retrouvez-vous-autour-dun-feu-de-camp-dans-world-of-warcraft-forever'
CAMP_EN = 'https://news.blizzard.com/en-us/article/24301516/gather-around-the-campfire-in-world-of-warcraft-forever'
DIVE_FR = 'https://news.blizzard.com/fr-fr/article/24303313/recapitulatif-de-la-presentation-au-cur-de-world-of-warcraft-forever'
DIVE_EN = 'https://news.blizzard.com/en-us/article/24303313/world-of-warcraft-forever-deep-dive-panel-recap'
HF = 'https://news.blizzard.com/en-us/article/24315281/wow-forever-hotfixes-november-11-2026'
LEG = 'https://news.blizzard.com/en-us/article/24307383/get-to-know-the-world-of-warcraft-forever-legacy-system'
cols = ['metier','recette_fr_officiel','recette_en','type_obtention','pnj_vendeur','source_butin','zone','sous_zone_repere','faction','prix','prerequis','statut','source_url','date_consultation','notes']
rows = []
def R(**k):
    r = {c:'' for c in cols}
    r.update(k)
    r.setdefault('date_consultation', ACC)
    rows.append(r)

# ----- OFFICIEL : 11 exemples de l’article campement -----
# Obtention générale niv. 20 : quêtes de zones de départ OU achat chez un maître de métier (PNJ et zone non nommés).
# Feu de camp basique : niveau 1, pas la même phrase d’obtention.
camp = [
('Cuisine','Feu de camp basique','Basic Campfire','1','objet qui permet de cuisiner et d’ajouter jusqu’à 3 fonctionnalités'),
('Secourisme','Trousse de premiers soins','First Aid Kit','20',''),
('Pêche','Bocal à poisson','Fishing Bowl','20','nom EN officiel : Fishing Bowl ; FR : Bocal à poisson'),
('Alchimie','Puits de mana','Mana Well','20',''),
('Forge','Meule à aiguiser','Sharpening Wheel','20',''),
('Enchantement','Luth enchanté','Enchanted Lute','20',''),
('Ingénierie','Robot vendeur de composants','Reagent Bot','20',''),
('Herboristerie','Bougie d’encens','Incense Candle','20',''),
('Travail du cuir','Tente du camp','Camp Tent','20',''),
('Dépeçage','Chaise du camp','Camp Chair','20',''),
('Couture','Bannière de faction','Faction Banner','20',''),
]
for met,fr,en,sk,note in camp:
    if sk=='1':
        obt,pr,n = 'non publié (détail)','Cuisine compétence 1', (note or '')+'. L’article le décrit comme l’objet de cuisine au niveau 1 ; il ne dit pas chez quel PNJ on l’apprend.'
    else:
        obt,pr,n = 'formateur / quête (zones de départ)','compétence 20', 'Obtention officielle : « quêtes dans les zones de départ ou achat auprès d’un maître ou d’une maîtresse de métier ». Ni le PNJ, ni la zone, ni le prix, ni le nom de la quête ne sont publiés. '+(note or '')
    R(metier=met, recette_fr_officiel=fr, recette_en=en, type_obtention=obt, pnj_vendeur='non publié', source_butin='',
      zone='non publié', sous_zone_repere='non publié', faction='', prix='non publié', prerequis=pr,
      statut='officiel confirmé', source_url=CAMP_FR+' | '+CAMP_EN, notes=n.strip())

# Règle générale 140+
R(metier='Tous (artisanat / campement avancé)', recette_fr_officiel='(règle générale, pas une recette)', recette_en='(general rule)',
  type_obtention='butin monstre / donjon et raid', pnj_vendeur='', source_butin='non publié (article : « butin dans les donjons et les raids » ; Deep Dive : « Blueprint recipes that drop from specific dungeon bosses », boss non nommés)',
  zone='non publié', sous_zone_repere='non publié', faction='', prix='', prerequis='compétence 140 ou plus (règle de l’article du 21/10 ; des exceptions officielles existent ensuite, voir ci-dessous)',
  statut='officiel confirmé', source_url=CAMP_FR+' | '+DIVE_EN,
  notes='Aucun taux de drop publié. Aucun boss, coffre ou donjon nommé pour un plan précis. Tableau de l’article : aperçu d’un exemple par métier, pas la liste complète. Deep Dive : chaque métier a trois objets, appris à des niveaux différents.')

# Objets avancés nommés, sans obtention détaillée
R(metier='Cuisine', recette_fr_officiel='feux de camp améliorés (5 ou 10 objets)', recette_en='upgraded Campfires (5 or 10 objects)',
  type_obtention='non publié', pnj_vendeur='non publié', source_butin='', zone='non publié', sous_zone_repere='', faction='', prix='non publié',
  prerequis='non publié dans l’article campement (un kit est précisé plus tard : voir Journeyman Campfire Kit)',
  statut='officiel confirmé (existence) ; obtention non publiée', source_url=CAMP_FR+' | '+DIVE_EN,
  notes='L’article et le Deep Dive confirment que les cuisiniers peuvent apprendre des feux améliorés (5 ou 10 objets). Pas de PNJ, zone, boss ni prix.')

R(metier='Alchimie', recette_fr_officiel='laboratoire d’alchimie', recette_en='Alchemy Lab / Alchemy Laboratory',
  type_obtention='non publié', pnj_vendeur='non publié', source_butin='', zone='non publié', sous_zone_repere='', faction='', prix='non publié',
  prerequis='non publié', statut='officiel confirmé (existence) ; obtention non publiée',
  source_url=DIVE_FR+' | '+CAMP_FR, notes='Deep Dive : « Alchemists can learn to place an Alchemy Lab ». Pas de source d’obtention nommée.')

R(metier='Travail du cuir', recette_fr_officiel='râtelier de tannage (aussi « chevalet de tannage » dans le Deep Dive FR)', recette_en='Tanning Rack',
  type_obtention='non publié (après le correctif)', pnj_vendeur='non publié', source_butin='',
  zone='non publié', sous_zone_repere='', faction='', prix='non publié',
  prerequis='compétence 125 (était 140) — correctif officiel du 6/11/2026',
  statut='officiel confirmé (existence + prérequis) ; obtention non publiée',
  source_url=HF+' | '+CAMP_FR+' | '+DIVE_FR,
  notes='Correctif 6/11 : exigence baissée à 125 pour ne plus bloquer des patrons de travail du cuir qui demandent 125 ; les gains de compétence du râtelier sont baissés de 15. L’article du 21/10 rangeait les objets « 140 ou plus » dans le butin de donjon/raid ; le correctif ne redisit pas la source d’obtention. Taux de drop : non publié.')

R(metier='Cuisine', recette_fr_officiel='(FR officiel non publié dans les sources consultées ; page FR des correctifs : 404 le 12/11)', recette_en='Journeyman Campfire Kit',
  type_obtention='non publié', pnj_vendeur='non publié', source_butin='', zone='non publié', sous_zone_repere='', faction='', prix='non publié',
  prerequis='Cuisine 90 pour le placer, égal à l’exigence de la recette (était Cuisine 140) — correctif officiel du 10/11/2026',
  statut='officiel confirmé (nom EN + prérequis) ; obtention non publiée',
  source_url=HF,
  notes='Exception officielle à la règle générale « 140 ou plus ». Blizzard ne dit pas où on apprend le plan. Aucun taux de drop.')

R(metier='Enchantement', recette_fr_officiel='(FR officiel non publié)', recette_en='Arcane Salvager',
  type_obtention='non publié', pnj_vendeur='non publié', source_butin='', zone='non publié', sous_zone_repere='', faction='', prix='non publié',
  prerequis='fabrication : Runed Golden Rod (était Runed Truesilver Rod) — correctif officiel du 10/11/2026',
  statut='officiel confirmé (existence + outil) ; obtention non publiée',
  source_url=HF,
  notes='Le correctif nomme l’objet et corrige l’outil et un bonus de désenchantement. Il ne dit pas où s’obtient le plan.')

R(metier='Pêche', recette_fr_officiel='(FR officiel non publié)', recette_en='Fishing Rack',
  type_obtention='non publié', pnj_vendeur='non publié', source_butin='', zone='non publié', sous_zone_repere='', faction='', prix='non publié',
  prerequis='non publié', statut='officiel confirmé (existence) ; obtention non publiée',
  source_url=HF,
  notes='Correctif 10/11 : certains Fishing Racks ne donnaient pas de leurres. Confirme l’existence de l’objet. Pas d’obtention.')

R(metier='Alchimie', recette_fr_officiel='(FR officiel non publié)', recette_en='Recipe: Elixir of Holy Power (anciennement Recipe: Elixir of Greater Firepower)',
  type_obtention='non publié', pnj_vendeur='non publié', source_butin='', zone='non publié', sous_zone_repere='', faction='', prix='non publié',
  prerequis='non publié', statut='officiel confirmé (nom EN corrigé) ; obtention non publiée',
  source_url=HF,
  notes='Correctif 10/11 : correction de nom, aura « Holy Power ». Pas de vendeur, monstre ni zone.')

# Sacs (recettes implicitement existantes, matériaux corrigés)
for fr,en,mats in [
    ('Sac en tisse-mage rouge','Red Mageweave Bag','5 bolts of mageweave (était 4), 14 emplacements'),
    ('Fourre-tout vert en soie','Green Silk Pack','5 bolts of silk (était 4), 12 emplacements'),
    ('Fourre-tout noir en soie','Black Silk Pack','6 bolts of silk (était 5), 12 emplacements'),
    ('Sac vert en laine','Green Woolen Bag','5 bolts of wool (était 4), 10 emplacements'),
    ('Sac rouge en laine','Red Woolen Bag','5 bolts of wool (était 4), 10 emplacements'),
]:
    R(metier='Couture', recette_fr_officiel='(FR : noms classiques non repris ici comme traduction officielle Forever ; EN officiel du correctif)', recette_en=en,
      type_obtention='non publié', pnj_vendeur='non publié', source_butin='', zone='non publié', sous_zone_repere='', faction='', prix='non publié',
      prerequis=mats, statut='officiel confirmé (existence et matériaux, 11/11) ; obtention non publiée',
      source_url=HF, notes='Le correctif ajuste matériaux et taille. Il ne dit pas où apprendre la recette. Noms FR non vérifiés dans une source officielle Forever consultée.')

# Contexte officiel, pas une recette
R(metier='(contexte)', recette_fr_officiel='plus de 600 nouvelles recettes, tous métiers et niveaux', recette_en='over 600 new recipes across professions and level ranges',
  type_obtention='non détaillé', pnj_vendeur='', source_butin='plans avancés : certains boss de donjon (non nommés)', zone='', sous_zone_repere='', faction='', prix='',
  prerequis='', statut='officiel confirmé (volume annoncé, pas la liste)', source_url=DIVE_EN+' | '+DIVE_FR,
  notes='Annonce de volume uniquement. Aucune liste individuelle.')

R(metier='(contexte)', recette_fr_officiel='Administration commerciale d’Azeroth / Transports logistiques Durotar', recette_en='Azeroth Commerce Authority / Durotar Supply and Logistics',
  type_obtention='réputation (activités de métier, sans liste de recettes)', pnj_vendeur='non publié', source_butin='', zone='non publié', sous_zone_repere='',
  faction='Alliance / Horde (deux factions officielles nouvelles)', prix='non publié', prerequis='non publié',
  statut='officiel confirmé (rôle) ; recettes non publiées', source_url=LEG,
  notes='Article héritage : « These two new Alliance and Horde factions are a major source of new tradeskill activities. » Aucune recette, aucun intendant, aucun palier.')

R(metier='(contexte)', recette_fr_officiel='marchands de fournitures de métier sur l’île de Zéphras', recette_en='trade supply vendors on Zephras Isle',
  type_obtention='vendeur (fournitures, pas des recettes nommées)', pnj_vendeur='non publié (pluriel, non nommé)', source_butin='',
  zone='Île de Zéphras (Zephras Isle)', sous_zone_repere='non publié', faction='', prix='non publié',
  prerequis='', statut='officiel confirmé (existence des marchands et des sacs d’apprenti)', source_url=HF,
  notes='Correctif 5/11 : ces marchands ne vendaient pas les sacs de métier d’apprenti. Confirme des vendeurs de fournitures sur Zéphras, pas une liste de recettes.')

R(metier='(contexte)', recette_fr_officiel='Caisses égarées et Commandes de l’artisan (noms FR à confirmer)', recette_en='Waylaid Crates and Craftsman’s Writs',
  type_obtention='butin (dans les donjons) — le correctif ne dit pas que ce sont des recettes', pnj_vendeur='',
  source_butin='non détaillé (« dropping inside dungeons »)', zone='donjons (non nommés)', sous_zone_repere='', faction='', prix='',
  prerequis='', statut='officiel confirmé (ces objets tombent en donjon, 9/11) ; lien avec des recettes : non publié par Blizzard',
  source_url=HF, notes='Correctif 9/11 : un bug empêchait leur butin en donjon. Des messages de joueurs sur les forums parlent de recettes chez des vendeurs liés à ces caisses : ce n’est PAS une source officielle, non repris comme fait.')

# ----- À CONFIRMER : consultation ciblée (extrait client), PAS un import de masse -----
AC = 'à confirmer (données extraites du client)'
R(metier='Cuisine', recette_fr_officiel='(FR officiel non publié)', recette_en='Recipe: Smoked Sagefish / Smoked Sagefish',
  type_obtention='vendeur', pnj_vendeur='Zerril Softbreeze', source_butin='',
  zone='Île de Zéphras', sous_zone_repere='coordonnées 43,8 / 43,8 indiquées « per quest data » — à confirmer, non publiées par Blizzard',
  faction='', prix='prix d’ACHAT non publié (la page item indique un prix de REVENTE : 1 po 25 ? en réalité « Sell Price: 1 25 », probablement 1 a 25 c — ne pas confondre avec le prix d’achat)',
  prerequis='Cuisine (80)', statut=AC,
  source_url='https://eternadex.com/en/item/21099/ | https://eternadex.com/en/npc/zerril-softbreeze/ | https://eternadex.com/en/berufe/kochkunst/',
  notes='Deux recettes seulement sont classées « Vendor » dans le tableau d’ensemble consulté (2126 recettes). Ne pas reporter un vendeur Classic Era : ce PNJ a un identifiant élevé (251905) dans les données consultées, présenté comme PNJ Forever. Sous-zone type village non reprise (absente de la page NPC consultée).')

R(metier='Cuisine', recette_fr_officiel='(FR officiel non publié)', recette_en='Recipe: Sagefish Delight / Sagefish Delight',
  type_obtention='vendeur', pnj_vendeur='Zerril Softbreeze', source_butin='',
  zone='Île de Zéphras', sous_zone_repere='idem (page NPC)', faction='',
  prix='prix d’ACHAT non publié (Sell Price indiqué : 12 50)', prerequis='Cuisine (175)', statut=AC,
  source_url='https://eternadex.com/en/item/21219/ | https://eternadex.com/en/npc/zerril-softbreeze/',
  notes='Seconde et dernière recette « Vendor » du tableau d’ensemble consulté.')

R(metier='Cuisine', recette_fr_officiel='(FR officiel non publié)', recette_en="Blueprint: Cookie's Feast / Cookie's Feast",
  type_obtention='butin monstre', pnj_vendeur='', source_butin='Cookie',
  zone='Les Mortemines (The Deadmines)', sous_zone_repere='non précisé au-delà du donjon', faction='', prix='',
  prerequis='Cuisine (140) — exigence sur la page item consultée, pas un chiffre Blizzard pour ce plan', statut=AC,
  source_url='https://eternadex.com/en/item/273102/',
  notes='Taux de drop : non indiqué sur la page consultée, donc non repris. Donjon Classic présent dans Forever selon les correctifs officiels (plusieurs mentions des Deadmines ? — les correctifs du 11/11 ne citent pas Cookie). Fait uniquement à confirmer.')

R(metier='Ingénierie', recette_fr_officiel='(FR officiel non publié)', recette_en='Blueprint: Repair Bot / Repair Bot',
  type_obtention='butin monstre', pnj_vendeur='', source_butin='Sneed',
  zone='Les Mortemines (The Deadmines)', sous_zone_repere='', faction='', prix='',
  prerequis='Ingénierie (140) selon la page item', statut=AC,
  source_url='https://eternadex.com/en/item/273092/',
  notes='Taux de drop non indiqué. Le correctif officiel du 10/11 nomme un « Repair Bot » ? Non — il nomme Reagent Bot dans l’article camp (officiel, niv. 20) distinct de Repair Bot (à confirmer, 140). Ne pas fusionner les deux.')

R(metier='Enchantement', recette_fr_officiel='(FR officiel non publié)', recette_en='Blueprint: Arcane Salvager / Arcane Salvager',
  type_obtention='butin monstre', pnj_vendeur='', source_butin="Rath'mael ; Charlga Razorflank",
  zone="Ruines de Lordaeron (Rath'mael) ; Kraal de Tranchebauge / Razorfen Kraul (Charlga Razorflank)",
  sous_zone_repere='', faction='', prix='', prerequis='Enchantement (140) selon la page item', statut=AC,
  source_url='https://eternadex.com/en/item/273103/',
  notes='Les Ruines de Lordaeron sont un donjon officiel Forever. Rath\'mael n’est pas nommé dans les sources officielles consultées (la fiche donjon officielle nomme The Baron, pas Rath\'mael). Charlga / Tranchebauge : pas trouvé dans les news officielles consultées. Taux de drop non indiqué. L’existence d’Arcane Salvager est officielle (correctif 10/11) ; la source de butin reste à confirmer.')

R(metier='Couture', recette_fr_officiel='(FR officiel non publié)', recette_en='Pattern: Filigreed Shining Gown / Filigreed Shining Gown',
  type_obtention='butin monstre', pnj_vendeur='', source_butin='Cookie ; Fel Steed / Shadow Charger',
  zone='Les Mortemines (Cookie) ; Donjon d’Ombrecroc / Shadowfang Keep (Fel Steed / Shadow Charger)',
  sous_zone_repere='', faction='', prix='', prerequis='Couture (75) selon la page item', statut=AC,
  source_url='https://eternadex.com/en/item/253912/', notes='Taux de drop non indiqué. Patron « new Forever » possible (nom inconnu de Classic).')

R(metier='Travail du cuir', recette_fr_officiel='(FR officiel non publié)', recette_en="Pattern: Brawler's Leather Hood / Brawler's Leather Hood",
  type_obtention='butin monstre', pnj_vendeur='', source_butin='Lady Sarevess',
  zone='Profondeurs de Brassenoire (Blackfathom Deeps)', sous_zone_repere='', faction='', prix='',
  prerequis='Travail du cuir (100) selon la page item', statut=AC,
  source_url='https://eternadex.com/en/item/252798/', notes='Taux de drop non indiqué. Blackfathom Deeps est mentionné dans les correctifs officiels (bug de libération). Le lien recette–boss reste à confirmer.')

R(metier='Cuisine', recette_fr_officiel='(FR officiel non publié)', recette_en='Skywall Souffle (indiqué New in Forever)',
  type_obtention='quête', pnj_vendeur='', source_butin='',
  zone='Île de Zéphras (le PNJ Zerril Softbreeze démarre « Restocking the Larders », selon la page NPC)',
  sous_zone_repere='', faction='', prix='', prerequis='selon guide cuisine consulté', statut=AC,
  source_url='https://eternadex.com/en/berufe/kochkunst/ | https://eternadex.com/en/npc/zerril-softbreeze/',
  notes='Récompense de quête « Restocking the Larders ». Quête et PNJ non trouvés dans une source officielle Blizzard.')

R(metier='Cuisine', recette_fr_officiel='(FR officiel non publié)', recette_en='Beer Basted Boar Ribs',
  type_obtention='quête', pnj_vendeur='', source_butin='',
  zone='Dun Morogh (Alliance), selon https://eternadex.com/en/quests/384/',
  sous_zone_repere='', faction='Alliance', prix='', prerequis='quête niveau 7 selon la page', statut=AC,
  source_url='https://eternadex.com/en/berufe/kochkunst/ | https://eternadex.com/en/quests/384/',
  notes='Ne pas conclure que le PNJ et le déroulement sont identiques à Classic Era : source = données Forever consultées, à confirmer.')

R(metier='Cuisine', recette_fr_officiel='(FR officiel non publié)', recette_en='Soothing Turtle Bisque',
  type_obtention='quête', pnj_vendeur='', source_butin='',
  zone='non précisée sur les extraits consultés (PNJ : Chef Jessen Alliance ; Christoph Jeffcoat Horde)',
  sous_zone_repere='', faction='Alliance et Horde (deux quêtes, ids 555 et 7321)', prix='', prerequis='quête métier cuisine, niveau 31 selon les pages', statut=AC,
  source_url='https://eternadex.com/en/quests/555/ | https://eternadex.com/en/quests/7321/',
  notes='Consultation ciblée de deux pages de quête. À confirmer.')

# Autres quêtes cuisine vues sur UNE page (guide), zone souvent absente
for en,q in [
    ('Kaldorei Spider Kabob','Recipe of the Kaldorei'),
    ('Pincer Bites (New in Forever)','Crab Season'),
    ('Goretusk Liver Pie','Goretusk Liver Pie'),
    ('Strider Stew','Easy Strider Living'),
    ('Blood Sausage','Thelsamar Blood Sausages'),
    ('Westfall Stew','Westfall Stew'),
    ('Twice-Spiced Raptor Slice (New in Forever)','Changing Tastes'),
    ('Crocolisk Steak','Crocolisk Hunting'),
    ('Dig Rat Stew','Dig Rat Stew'),
    ('Murloc Fin Soup','Selling Fish'),
    ('Seasoned Wolf Kabob','Spiced Wolf Kebab'),
    ('Redridge Goulash','Redridge Goulash'),
    ('Big Bear Steak','The Rescue'),
    ('Gooey Spider Cake','Dusky Crab Cakes'),
    ('Crocolisk Gumbo',"Apprentice's Duties"),
    ('Hot Lion Chops','Elixir of Pain'),
    ('Curiously Tasty Omelet',"Ormer's Revenge"),
]:
    R(metier='Cuisine', recette_fr_officiel='(FR officiel non publié)', recette_en=en,
      type_obtention='quête', pnj_vendeur='non renseigné sur la page consultée', source_butin='',
      zone='non renseigné sur la page consultée (ne pas reporter Classic Era)', sous_zone_repere='', faction='', prix='',
      prerequis='voir guide cuisine consulté', statut=AC,
      source_url='https://eternadex.com/en/berufe/kochkunst/',
      notes=f"Récompense indiquée : quête « {q} ». Page unique consultée (guide 1–300). PNJ et zone non ouverts un par un — volontairement, pour rester sur une consultation ciblée.")

# Formateur cuisine (même page) — la vue d’ensemble dit « probably from the trainer (not confirmed) »
for en in ['Roasted Boar Meat','Herb Baked Egg','Charred Wolf Meat','Spiced Wolf Meat','Boiled Clams','Coyote Steak','Crab Cake','Dry Pork Ribs','Goblin Deviled Clams','Critter Cookie (New in Forever)']:
    R(metier='Cuisine', recette_fr_officiel='(FR officiel non publié)', recette_en=en,
      type_obtention='formateur (non confirmé même par la base consultée au niveau d’ensemble)', pnj_vendeur='maître de métier, non nommé', source_butin='',
      zone='non publié / « Where they are in WoW Forever isn’t confirmed yet » (page formateurs consultée)', sous_zone_repere='', faction='', prix='non publié',
      prerequis='variable', statut=AC,
      source_url='https://eternadex.com/en/berufe/kochkunst/ | https://eternadex.com/en/lehrer/',
      notes='Le guide cuisine écrit « from the trainer » ; le tableau d’ensemble classe ce type en « probably from the trainer (not confirmed) » (pas d’objet-recette trouvé). Les deux mentions sont à confirmer. Aucun nom de formateur Forever n’est donné comme confirmé sur la page formateurs.')

out = HERE/'RECETTES_PNJ.csv'
with out.open('w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
# counts
from collections import Counter
c=Counter(r['statut'].split(';')[0].strip() for r in rows)
print('rows',len(rows), dict(c))
