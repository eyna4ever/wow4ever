"""v43d (Oui de Mathieu t423u, 25/11/2026, Europe/Paris) : textes de la MAJ du 23 novembre + encadré « problèmes en cours »,
repris du brouillon /workspace/wow4ever-chatgpt/veille/articles/2026-11-24-maj-correctifs-forever-5-et-6-novembre.md.
Seule la typographie change (’, « », “ ”) ; aucun fait ajouté."""
SRC = [
 ('https://news.blizzard.com/en-us/article/24315281', {'fr': 'WoW: Forever Hotfixes - November 23, 2026', 'en': 'WoW: Forever Hotfixes - November 23, 2026'}, '2026-11-24', '2026-11-24'),
 ('https://us.forums.blizzard.com/en/wow/t/2403040/15', {'fr': 'WoW: Forever Hotfixes - November 23, 2026 (Kaivax, forum officiel US, message 15)', 'en': 'WoW: Forever Hotfixes - November 23, 2026 (Kaivax, official US forum, post 15)'}, '2026-11-24', '2026-11-24'),
 ('https://eu.forums.blizzard.com/en/wow/t/639885/14', {'fr': 'WoW: Forever Hotfixes - November 23, 2026 (Kaivax, forum officiel EU, message 14)', 'en': 'WoW: Forever Hotfixes - November 23, 2026 (Kaivax, official EU forum, post 14)'}, '2026-11-24', '2026-11-24'),
 ('https://us.forums.blizzard.com/en/wow/t/2426335/4', {'fr': 'Lockbox exploit and economy hold heuristic (Kaivax, forum officiel US, message 4)', 'en': 'Lockbox exploit and economy hold heuristic (Kaivax, official US forum, post 4)'}, '2026-11-23', '2026-11-24'),
 ('https://eu.forums.blizzard.com/en/wow/t/645296/2', {'fr': 'Lockbox exploit and economy hold heuristic (Kaivax, forum officiel EU, message 2)', 'en': 'Lockbox exploit and economy hold heuristic (Kaivax, official EU forum, post 2)'}, '2026-11-23', '2026-11-24'),
 ('https://us.forums.blizzard.com/en/wow/t/2424420/2', {'fr': 'Epic Mount Riding Skill (Kaivax, forum officiel US, message 2)', 'en': 'Epic Mount Riding Skill (Kaivax, official US forum, post 2)'}, '2026-11-23', '2026-11-24'),
 ('https://eu.forums.blizzard.com/en/wow/t/642667/11', {'fr': 'Epic Mount Riding Skill (Kaivax, forum officiel EU, message 11)', 'en': 'Epic Mount Riding Skill (Kaivax, official EU forum, post 11)'}, '2026-11-23', '2026-11-24'),
]
CITES = {'nov23': (24, 25, 26), 'lockbox': (27, 28), 'epicmount': (29, 30)}
SEC = {
 'nov23': {
  'fr': ('23 novembre 2026',
         'Lot publié sur la page officielle, désormais titrée « WoW: Forever Hotfixes - November 23, 2026 », et relayé par Kaivax sur les forums officiels US et EU le 24 novembre à 03:06 heure de Paris. Les noms de sorts, PNJ, objets et quêtes sont repris en anglais.',
         ['Classes : Druide : l’ensemble 4 pièces Feralheart rend correctement 4 points d’énergie par seconde pendant 5 secondes. Prêtre : Mind Vision ne déclenche plus d’effets ; Ombre : Dark Inspiration accorde le bon bonus d’Esprit quand elle est activée par Mind Flay, et Chastise est utilisable en Shadowform. Démoniste Destruction : Intensity fonctionne sur Incinerate. Guerrier : Mortal Strike reste dans le grimoire mais n’est plus utilisable sans le point de talent correspondant.',
          'Donjons : Uldaman, l’Obsidian Sentinel donne son butin normalement.',
          'Objets : la Filcher’s Cowl n’a plus de niveau requis.',
          'Métiers : Cuisine, les plats à base de palourdes (Boiled Clams, Clam Chowder, Goblin Deviled Clams, Giant Clam Scorcho, Undermine Clam Chowder, Clam Linguine) donnent le bon bonus « Bien nourri » et sont classés en « Stamina Food » ; Murloc Fin Soup passe au palier de nourriture supérieur. Ingénierie : les Renewal Gift gobelin et gnome ne s’affichent plus en points d’interrogation inutilisables, et « The Mortar: Reloaded » s’apprend avec « Goblin Mortar ». Travail du cuir : Pattern: Centaur Hoofwarmers est de nouveau apprenable.',
          'Quêtes : Riverglades, Dunston Willis court de nouveau en fin d’escorte (« Dunston Checks Out ») ; Wetlands, « For Further Study » a des récompenses et « Uncovering the Past » / « Gleaning Our Future » donnent de la réputation Ironforge.',
          'Races : la Wisp Form ne peut plus s’appliquer à un joueur vivant.',
          'Sorts : quelques sorts déclenchaient trop d’effets d’arme (corrigé) ; les buffs mondiaux ne tombent plus en changeant de zone (ils tombent toujours en entrant dans un raid) ; Fengus’ Ferocity et les buffs de la Foire de Sombrelune donnaient deux fois trop de puissance (corrigé).',
          'Conséquences pour les joueurs : les buffs mondiaux restent actifs entre zones ; les guerriers sans talent ne peuvent plus utiliser Mortal Strike ; les buffs de Sombrelune et de Fengus pèsent deux fois moins ; paladins et démonistes concernés attendent le correctif de monte.']),
  'en': ('November 23, 2026',
         'Batch published on the official page, now titled “WoW: Forever Hotfixes - November 23, 2026”, and relayed by Kaivax on the official US and EU forums on November 24 at 03:06 Paris time. Spell, NPC, item and quest names are kept in English.',
         ['Classes: Druid: the 4-piece Feralheart set now correctly grants 4 Energy every second for 5 seconds. Priest: Mind Vision no longer procs effects; Shadow: Dark Inspiration grants the correct Spirit bonus when activated by Mind Flay, and Chastise is usable in Shadowform. Destruction Warlock: Intensity now works on Incinerate. Warrior: Mortal Strike stays in the spellbook but can no longer be used without the talent point.',
          'Dungeons: Uldaman, the Obsidian Sentinel drops loot as intended.',
          'Items: the Filcher’s Cowl no longer has a level requirement.',
          'Professions: Cooking, clam dishes (Boiled Clams, Clam Chowder, Goblin Deviled Clams, Giant Clam Scorcho, Undermine Clam Chowder, Clam Linguine) give the correct Well Fed bonus and are listed under “Stamina Food”; Murloc Fin Soup moves up to the next food tier. Engineering: Goblin and Gnome Engineer’s Renewal Gift no longer show as unusable question marks, and “The Mortar: Reloaded” is learned with “Goblin Mortar”. Leatherworking: Pattern: Centaur Hoofwarmers is learnable again.',
          'Quests: Riverglades, Dunston Willis runs again near the end of the escort (“Dunston Checks Out”); Wetlands, “For Further Study” now has rewards and “Uncovering the Past” / “Gleaning Our Future” reward Ironforge reputation.',
          'Races: Wisp Form can no longer be applied to living players.',
          'Spells: a few spells caused more weapon procs than intended (fixed); World Buffs no longer fall off when changing areas (they still fall off on entering raids); Fengus’ Ferocity and Darkmoon Faire buffs granted twice the intended power (fixed).',
          'What it means for players: world buffs persist across zones; untalented warriors can no longer use Mortal Strike; Darkmoon and Fengus buffs are halved; affected Paladins and Warlocks wait for the riding fix.']),
 },
}
# Le dernier item (« Conséquences ») cite aussi le message sur la monte épique.
CONSEQ_CITE = (24, 29)
BOX = {
 'fr': ('Problèmes en cours',
        ['Les coffres verrouillés (lockboxes) ont reçu un changement de comportement temporaire le 22 novembre à 9 h 55 PST (18 h 55 heure de Paris) ; Blizzard prépare un vrai correctif qui rétablira la possibilité de regarder et de piller partiellement un coffre, sans délai annoncé.',
         'La compétence de monte épique n’est pas accordée après les chaînes de quêtes de monture épique de classe ; Blizzard pense que paladins et démonistes sont touchés et annonce un correctif « dans un jour ou deux ».']),
 'en': ('Known issues in progress',
        ['Lockboxes received a temporary behaviour change on November 22 at 9:55 a.m. PST; Blizzard is working on a proper fix that restores peeking and partial looting, with no timeline yet.',
         'The epic riding skill is not granted after class epic mount quest chains; Blizzard believes Paladins and Warlocks are affected and expects a fix “in another day or two”.']),
}
BOX_CITE = ((27, 28), (29, 30))
KEY = {
 'nov23': {
  'fr': '23 novembre : les buffs mondiaux ne tombent plus en changeant de zone ; ceux de la Foire de Sombrelune et Fengus’ Ferocity sont divisés par deux ; Mortal Strike n’est plus utilisable sans le talent ; correctifs d’Uldaman, de nourritures, d’ingénierie et de quêtes.',
  'en': 'November 23: world buffs no longer fall off when changing areas; Darkmoon Faire and Fengus’ Ferocity buffs are halved; Mortal Strike can no longer be used without the talent; fixes for Uldaman, foods, engineering and quests.',
 },
 'issues': {
  'fr': 'Problèmes en cours : changement temporaire des coffres verrouillés le 22 novembre, un vrai correctif est en préparation ; la compétence de monte épique n’est pas accordée après les chaînes paladin et démoniste, correctif annoncé « dans un jour ou deux ».',
  'en': 'Known issues in progress: a temporary lockbox behaviour change on November 22, with a proper fix in the works; the epic riding skill is not granted after Paladin and Warlock mount quest chains, with a fix expected “in another day or two”.',
 },
}
ANAL = {
 'fr': ' Garder les buffs mondiaux entre zones tout en divisant par deux ceux de Sombrelune et de Fengus rééquilibre leur poids plutôt que de les supprimer ; on peut y voir une volonté de garder ces bonus attractifs sans qu’ils deviennent obligatoires.',
 'en': ' Keeping world buffs across zones while halving the Darkmoon and Fengus buffs rebalances their weight rather than removing them; it can be read as a wish to keep these bonuses attractive without making them mandatory.',
}
TL = {
 'fr': [('2026-11-22', '22 novembre 2026', 'Changement temporaire du comportement des coffres verrouillés (lockboxes) à 18 h 55 heure de Paris ; Kaivax l’explique le 23 novembre.', 'lockbox'),
        ('2026-11-23', '23 novembre 2026', 'Lot du 23 novembre (Feralheart, prêtre Ombre, Intensity, Mortal Strike, Uldaman, cuisine, ingénierie, quêtes Wetlands, buffs mondiaux, Sombrelune, Fengus), publié le 24 novembre à 03:06 heure de Paris.', 'nov23'),
        ('2026-11-23', '23 novembre 2026', 'Kaivax annonce un bug de compétence de monte épique après les chaînes paladin et démoniste, avec un correctif « dans un jour ou deux ».', 'epicmount')],
 'en': [('2026-11-22', '22 November 2026', 'Temporary lockbox behaviour change at 18:55 Paris time; Kaivax explains it on November 23.', 'lockbox'),
        ('2026-11-23', '23 November 2026', 'November 23 batch (Feralheart, Shadow Priest, Intensity, Mortal Strike, Uldaman, cooking, engineering, Wetlands quests, world buffs, Darkmoon, Fengus), published on November 24 at 03:06 Paris time.', 'nov23'),
        ('2026-11-23', '23 November 2026', 'Kaivax reports an epic riding skill bug after Paladin and Warlock quest chains, with a fix “in another day or two”.', 'epicmount')],
}
INTRO = {
 'fr': [('désormais titrée « WoW: Forever Hotfixes - November 20, 2026 ». Elle couvre les lots des 5, 6, 8, 9, 10, 11, 13, 16, 17, 19 et 20 novembre.',
         'désormais titrée « WoW: Forever Hotfixes - November 23, 2026 ». Elle couvre les lots des 5, 6, 8, 9, 10, 11, 13, 16, 17, 19, 20 et 23 novembre.')],
 'en': [('now titled “WoW: Forever Hotfixes - November 20, 2026”. It covers the November 5, 6, 8, 9, 10, 11, 13, 16, 17, 19 and 20 batches.',
         'now titled “WoW: Forever Hotfixes - November 23, 2026”. It covers the November 5, 6, 8, 9, 10, 11, 13, 16, 17, 19, 20 and 23 batches.')],
}
META = {
 'fr': 'Page cumulative officielle, désormais titrée « WoW: Forever Hotfixes - November 23, 2026 ». Lots des 5, 6, 8, 9, 10, 11, 13, 16, 17, 19, 20 et 23 novembre. Les changements de l’hôtel des ventes du 10 novembre ont été temporairement retirés et reportés à la maintenance du 17 novembre (Kaivax, 12 novembre 00:48 UTC) ; leur application n’est pas confirmée officiellement.',
 'en': 'Official cumulative page, now titled “WoW: Forever Hotfixes - November 23, 2026”. Batches of November 5, 6, 8, 9, 10, 11, 13, 16, 17, 19, 20 and 23. Auction House changes from November 10 were temporarily removed and postponed to November 17 maintenance (Kaivax, November 12 00:48 UTC); their application is not officially confirmed.',
}
META_OLD = {
 'fr': 'Page cumulative officielle mise à jour le 12 novembre (00:46 UTC), titrée « November 11, 2026 ». Lots des 5, 6, 8, 9, 10 et 11 novembre. Les changements de l’hôtel des ventes du 10 novembre ont été temporairement retirés et reportés à la maintenance du 17 novembre (Kaivax, 12 novembre 00:48 UTC). Page française 24315281 : 404.',
 'en': 'Official cumulative page updated on November 12 (00:46 UTC), titled “November 11, 2026”. Batches of November 5, 6, 8, 9, 10 and 11. Auction House changes from November 10 were temporarily removed and postponed to November 17 maintenance (Kaivax, November 12 00:48 UTC). French page 24315281: 404.',
}
SEARCH = {
 'fr': ' 23 novembre feralheart dark inspiration chastise intensity mortal strike uldaman filcher cowl lockboxes monte épique fengus sombrelune buffs mondiaux wisp form centaur hoofwarmers',
 'en': ' november 23 feralheart dark inspiration chastise intensity mortal strike uldaman filcher cowl lockboxes epic riding fengus darkmoon world buffs wisp form centaur hoofwarmers',
}
