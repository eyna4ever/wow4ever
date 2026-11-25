import {P, I, L, C, TB, S, D, Q} from '../helpers.mjs';

export default [
{
  id: 'article-forever-rulesets', code: 'AR03', category: 'guides', subcategory: 'rulesets',
  title: C('Choisir son ensemble de règles : Normal, JcJ, Jeu de rôle, JdR-JcJ et Extrême', 'Choosing a ruleset: Normal, PvP, Roleplaying, Roleplay-PvP and Hardcore'),
  description: C('Sans royaumes, World of Warcraft: Forever fait choisir un ensemble de règles. Ce guide compare les cinq options annoncées et explique ce qui est partagé et ce qui reste séparé.', 'World of Warcraft: Forever replaces realms with rulesets. This guide compares the five announced options and what is shared or kept apart.'),
  slug: C('ensembles-de-regles', 'rulesets'), illustration: 'guides',
  relations: ['forever-guide-choose-ruleset', 'article-forever-prepare-launch', 'article-forever-pvp'],
  lead: I('World of Warcraft: Forever n’a plus d’écran de choix de royaume. Le joueur choisit d’abord un ensemble de règles, qui fonctionne comme un vaste écosystème de joueurs. Cinq ensembles sont annoncés : Normal, JcJ, Jeu de rôle, JdR-JcJ au lancement et Extrême plus tard.',
    'World of Warcraft: Forever drops the realm-selection screen: you first pick a ruleset, which works like a broad player ecosystem. Five are announced: Normal, PvP, Roleplaying, Roleplay-PvP at launch, and Hardcore later.',
    'bz-rulesets', 'bz-deepdive'),
  keyPoints: [
    I('Normal, JcJ et Jeu de rôle sont disponibles au lancement. Le JdR-JcJ (Roleplay-PvP) a été ajouté le 22 octobre pour le lancement.', 'Normal, PvP and Roleplaying are available at launch; Roleplay-PvP was added on October 22 for launch.', 'bz-rulesets-en', 'bz-rulesets-fr'),
    I('Le mode Extrême arrivera après le lancement, sans date annoncée.', 'Hardcore arrives after launch, with no announced date.', 'bz-rulesets'),
    I('Pas de groupe entre ensembles différents ni entre factions. Les champs de bataille peuvent mélanger les ensembles, sauf l’Extrême.', 'No grouping across rulesets or factions; battlegrounds may mix rulesets, except Hardcore.', 'bz-rulesets'),
    I('Les collections et les points d’héritage sont partagés sur le compte, avec un traitement à part pour l’Extrême.', 'Collections and Legacy Points are account-wide, with Hardcore handled differently.', 'bz-rulesets', 'bz-deepdive')
  ],
  sections: [
    S('comparatif', 'Les ensembles en un coup d’œil', 'Rulesets at a glance',
      TB(C('Ensembles de règles annoncés', 'Announced rulesets'), [C('Ensemble', 'Ruleset'), C('Pour qui', 'For whom'), C('Disponibilité', 'Availability')], [
        [C('Normal'), C('L’expérience de base : exploration, quêtes, coopération ; le JcJ seulement si l’on s’y engage (consentement mutuel).', 'The baseline: exploration, questing, cooperation; PvP only when you engage in it (mutual consent).'), C('Lancement', 'Launch')],
        [C('JcJ', 'PvP'), C('Chaque passage en territoire disputé est plus dangereux, avec des conflits en monde ouvert.', 'Every trip into contested territory carries more danger and open-world conflict.'), C('Lancement', 'Launch')],
        [C('Jeu de rôle', 'Roleplaying'), C('Pour s’immerger dans l’univers d’Azeroth avec des joueurs aux mêmes envies.', 'Leaning into Azeroth’s fantasy with like-minded adventurers.'), C('Lancement', 'Launch')],
        [C('JdR-JcJ (Roleplay-PvP)', 'Roleplay-PvP'), C('Ensemble annoncé le 22 octobre dans la version anglaise de l’article. Blizzard ne le décrit pas davantage.', 'Ruleset announced on October 22 in the English article; Blizzard gives no further description.'), C('Lancement (4 novembre), réservation de noms prévue dès le 27 octobre', 'Launch (November 4), planned for Early Name Reservation from October 27')],
        [C('Extrême', 'Hardcore'), C('Le défi ultime : la mort a des conséquences durables.', 'The ultimate challenge: death carries lasting consequences.'), C('Après le lancement', 'After launch')]
      ], 'bz-rulesets-en', 'bz-rulesets-fr', 'bz-deepdive')
    ),
    S('jouer-ensemble', 'Jouer ensemble', 'Playing together',
      P('On peut grouper, faire des donjons et des raids avec les joueurs du même ensemble. Il n’y a pas de groupe entre ensembles. Les champs de bataille peuvent réunir des joueurs de plusieurs ensembles, sauf l’Extrême, qui reste à part.', 'You can group, run dungeons and raid with players on the same ruleset. Cross-ruleset grouping is not supported; battlegrounds may include players from other rulesets, except Hardcore, which stays separate.', 'bz-rulesets'),
      P('Les factions restent séparées : la Horde et l’Alliance ne peuvent pas grouper ensemble.', 'Factions stay separate: Horde and Alliance cannot group together.', 'bz-rulesets', 'bz-deepdive'),
      P('Les ensembles ne forment pas un royaume géant unique. Chacun fonctionne comme un grand écosystème, pensé pour qu’on recroise des noms familiers en jouant.', 'This is not one giant realm: each ruleset is its own large ecosystem, designed so you keep crossing paths with familiar names.', 'bz-deepdive')
    ),
    S('changer', 'Changer d’ensemble', 'Moving between rulesets',
      P('On ne passe pas librement d’un ensemble à l’autre : pour jouer ailleurs, il faut créer un nouveau personnage. En Extrême, un personnage mort pourra être transféré vers un autre ensemble, JcJ compris.', 'You cannot freely hop between rulesets; to play elsewhere you create a new character. In Hardcore, a character that dies can transfer to another ruleset, including PvP.', 'bz-rulesets'),
      P('Les collections et les points d’héritage sont partagés sur tout le compte. Exception : ce qui est gagné en Extrême peut servir ailleurs, mais la progression des autres ensembles ne remonte pas vers l’Extrême.', 'Collections and Legacy Points are account-wide. The exception: Hardcore progress can carry elsewhere, but progress from other rulesets does not flow back into Hardcore.', 'bz-rulesets', 'bz-deepdive')
    ),
    S('ensemble-jcj', 'Particularités de l’ensemble JcJ', 'PvP ruleset specifics',
      P('Sur l’ensemble JcJ, un compte ne peut créer des personnages que d’une seule faction. Les ensembles Normal, Jeu de rôle et Extrême autorisent les deux factions.', 'On the PvP ruleset an account can only create characters of one faction; Normal, Roleplaying and Hardcore allow both.', 'bz-rulesets'),
      P('Pour équilibrer les populations de la Horde et de l’Alliance, Blizzard prévoit des outils inspirés de la Saison de la découverte. La création de personnages dans une faction pouvait alors être limitée temporairement.', 'To keep Horde and Alliance populations closer, Blizzard plans tools similar to Season of Discovery, where new character creation could be temporarily limited for a faction.', 'bz-rulesets')
    ),
    S('langue', 'Préférence de langue', 'Language preference',
      P('Une préférence de langue aide à croiser des joueurs qui parlent la même langue. Elle se règle via Échap > Options > Système > Langues et fonctionnalités sociales > « Langue en ligne préférée ». Le réglage vaut pour tout le compte et ne peut changer qu’une fois toutes les 24 heures.', 'A language preference helps you meet players who share it: Escape > Options > System > Languages and Social > “Preferred Online Language”. It is account-wide with a 24-hour cooldown between changes.', 'bz-rulesets')
    )
  ],
  confirmed: [
    I('Normal, JcJ et Jeu de rôle au lancement ; Extrême après le lancement.', 'Normal, PvP and Roleplaying at launch; Hardcore after launch.', 'bz-rulesets'),
    I('JdR-JcJ disponible au lancement du 4 novembre.', 'Roleplay-PvP available at the November 4 launch.', 'bz-rulesets-en'),
    I('Une seule faction par compte sur l’ensemble JcJ.', 'One faction per account on the PvP ruleset.', 'bz-rulesets')
  ],
  pending: [
    Q('Blizzard a « prévu » le JdR-JcJ pour la réservation de noms du 27 octobre (« We also plan… »). Ce n’est pas encore confirmé.', 'Roleplay-PvP for the October 27 name reservation is “planned” (“We also plan…”), not confirmed.'),
    Q('La règle d’une seule faction par compte s’appliquera-t-elle au JdR-JcJ ? La source ne le dit pas.', 'Whether the one-faction-per-account rule applies to Roleplay-PvP is not stated.'),
    Q('Aucune date n’est donnée pour le mode Extrême.', 'No date is given for Hardcore.')
  ],
  notes: [
    I('La version française de l’article (21 septembre) ne mentionne pas encore le JdR-JcJ ; seule la version anglaise mise à jour le 22 octobre l’annonce. Aucun nom français officiel n’a été trouvé : « JdR-JcJ » est la formulation de ce wiki.', 'The French version of the article (September 21) does not yet mention Roleplay-PvP; only the English version updated October 22 does. No official French name was found: “JdR-JcJ” is this wiki’s wording.', 'bz-rulesets-fr', 'bz-rulesets-en')
  ],
  dates: [
    D('2026-09-21', 'Publication de l’article sur les ensembles de règles.', 'Rulesets article published.', 'bz-rulesets'),
    D('2026-10-22', 'Mise à jour (anglais) : ajout du JdR-JcJ pour le lancement.', 'Update (English): Roleplay-PvP added for launch.', 'bz-rulesets-en'),
    D('2026-10-27', 'Ouverture de la création de personnages et réservation de noms.', 'Character creation and name reservation open.', 'forum-kaivax1023', 'bz-claim')
  ]
},
{
  id: 'article-forever-prepare-launch', code: 'AR04', category: 'guides', subcategory: 'names',
  title: C('Préparer le lancement : noms en deux parties et réservation anticipée', 'Getting ready for launch: two-part names and Early Name Reservation'),
  description: C('Comment fonctionnent les noms en deux parties, qui peut réserver un nom du 27 octobre au 3 novembre, les horaires par région et les règles à connaître.', 'How two-part names work, who can reserve from October 27 to November 3, regional start times and the rules to know.'),
  slug: C('preparer-lancement-noms', 'prepare-launch-names'), illustration: 'guides',
  relations: ['article-forever-rulesets', 'article-forever-calendar', 'forever-news-launch'],
  lead: I('Dans World of Warcraft: Forever, chaque personnage porte un nom en deux parties, unique dans sa région. Les acheteurs d’offres éligibles peuvent réserver jusqu’à trois personnages entre le 27 octobre et le 3 novembre 2026, avant le lancement du 4 novembre.',
    'In World of Warcraft: Forever each character has a two-part name that is unique within its region. Eligible purchasers can reserve up to three characters between October 27 and November 3, 2026, ahead of the November 4 launch.',
    'bz-names', 'bz-claim'),
  keyPoints: [
    I('Un prénom et un « nom de famille » : c’est la combinaison complète qui doit être unique dans la région.', 'A first name and a “last name”: the complete combination must be unique within the region.', 'bz-names'),
    I('Réservation anticipée : du 27 octobre au 3 novembre, jusqu’à trois personnages au total, tous ensembles confondus.', 'Early Name Reservation: October 27 to November 3, up to three characters total across all rulesets.', 'bz-claim'),
    I('Il faut avoir acheté le pack héroïque des Éolides, le pack épique des Éolides ou la collection Warcraft Forever.', 'Requires the Skyborne Heroic Pack, Skyborne Epic Pack or Warcraft Forever Collection.', 'bz-claim', 'bz-stress'),
    I('Premier arrivé, premier servi : aucun nom n’est garanti.', 'First come, first served: no name is guaranteed.', 'bz-claim', 'bz-names')
  ],
  sections: [
    S('noms-deux-parties', 'Des noms en deux parties', 'Two-part names',
      P('Chaque personnage a un prénom et un nom secondaire. Deux personnages peuvent avoir le même prénom si leurs noms complets diffèrent. L’unicité s’apprécie à l’échelle de la région, pas d’un royaume.', 'Each character has a first name and a secondary name. Two characters can share a first name as long as their full names differ; uniqueness applies across the region, not a realm.', 'bz-names'),
      P('Le nom secondaire peut évoquer une famille, un lieu ou une réputation. Blizzard donne l’exemple d’Asha, Thalen et Mira Clairvallon (Brightvale en anglais). Une guilde peut aussi adopter un thème commun.', 'The secondary name can suggest a family, a place or a reputation; Blizzard’s example is Asha, Thalen and Mira Brightvale (Clairvallon in French). A guild can also adopt a shared theme.', 'bz-names'),
      P('Pour masquer son nom secondaire en jeu : Échap > Options > Barres d’info, puis cocher « Mon nom secondaire ». Il reste visible dans la discussion.', 'To hide your secondary name in the world: Escape > Options > Nameplates, then tick “My Secondary Name”; it still appears in chat.', 'bz-names')
    ),
    S('regles', 'Règles de nommage', 'Naming rules',
      L(
        I('Les noms doivent respecter le code de conduite en jeu.', 'Names must follow the in-game code of conduct.', 'bz-names'),
        I('Certains mots, orthographes ou répétitions de caractères peuvent être refusés, comme les noms qui se font passer pour Blizzard.', 'Some words, spellings or repeated characters may be restricted, including names impersonating Blizzard.', 'bz-names'),
        I('Les deux parties sont évaluées ensemble : couper un mot interdit en deux ne suffit pas forcément.', 'Both parts are evaluated together: splitting a restricted word across them will not necessarily work.', 'bz-names')
      )
    ),
    S('reservation', 'La réservation anticipée', 'Early Name Reservation',
      TB(C('Horaires d’ouverture', 'Start times'), [C('Région'), C('Ouverture', 'Start')], [
        [C('Europe'), C('27 octobre, 18 h (heure de Paris)', 'October 27, 18:00 CET')],
        [C('Amérique du Nord', 'North America'), C('27 octobre, 13 h (PDT)', 'October 27, 1:00 p.m. PDT')],
        [C('Corée', 'Korea'), C('28 octobre, 7 h (KST)', 'October 28, 07:00 KST')],
        [C('Taïwan', 'Taiwan'), C('28 octobre, 7 h (CST)', 'October 28, 07:00 CST')]
      ], 'bz-claim'),
      P('Pendant la réservation, on peut créer jusqu’à trois personnages au total, tous ensembles confondus. Exemple : avec deux personnages en JcJ, il n’en reste qu’un pour Normal ou Jeu de rôle. Cette limite ne vaut que pour la réservation anticipée.', 'During the reservation you can create up to three characters total across all rulesets: two on PvP leaves one for Normal or Roleplaying. The limit only applies to Early Name Reservation.', 'bz-claim'),
      P('L’avantage est réservé au compte WoW pour lequel le World of Warcraft: Forever Digital Upgrade ou l’édition collector a été acheté.', 'The benefit only applies to the specific WoW account for which the World of Warcraft: Forever Digital Upgrade or Collector’s Edition was purchased.', 'bz-claim'),
      P('Le forum officiel annonce que la création de personnages sera ouverte à tous le 27 octobre. Chacun peut donc choisir son ensemble et son nom avant le lancement.', 'The official forum says character creation will open to everyone on October 27, so everyone can pick a ruleset and a name before launch.', 'forum-kaivax1023')
    ),
    S('etapes', 'Se préparer, étape par étape', 'Getting ready, step by step',
      L(
        I('Mettre à jour ses pilotes graphiques.', 'Update graphics drivers.', 'bz-claim'),
        I('Installer ou mettre à jour l’application Battle.net.', 'Install or update the Battle.net desktop app.', 'bz-claim'),
        I('Choisir World of Warcraft, puis la version « World of Warcraft: Forever » au-dessus du bouton Jouer, et installer.', 'Select World of Warcraft, then the “World of Warcraft: Forever” game version above the Play button, and install.', 'bz-claim'),
        I('Cliquer sur Jouer, choisir son ensemble de règles et créer jusqu’à trois personnages.', 'Click Play, choose a ruleset and create up to three characters.', 'bz-claim')
      )
    )
  ],
  confirmed: [
    I('Réservation du 27 octobre au 3 novembre 2026 pour les offres éligibles.', 'Reservation from October 27 to November 3, 2026 for eligible upgrades.', 'bz-claim', 'bz-names'),
    I('Noms uniques par région, en deux parties.', 'Two-part names, unique per region.', 'bz-names', 'bz-deepdive')
  ],
  pending: [
    Q('La disponibilité du JdR-JcJ pendant la réservation est seulement « prévue ».', 'Roleplay-PvP availability during the reservation is only “planned”.'),
    Q('Les sources ne disent pas combien de personnages on pourra créer par ensemble après le lancement.', 'The sources do not say how many characters per ruleset are allowed after launch.')
  ],
  notes: [
    I('L’heure européenne est indiquée en « CET » dans la version anglaise : le 27 octobre, la France sera passée à l’heure d’hiver, donc 18 h à Paris.', 'The English text lists Europe in “CET”: on October 27 France is on winter time, so 18:00 in Paris.', 'bz-claim-en')
  ],
  dates: [
    D('2026-09-21', 'Présentation des noms en deux parties.', 'Two-part names explained.', 'bz-names'),
    D('2026-10-20', 'Annonce des horaires de réservation.', 'Reservation times announced.', 'bz-claim'),
    D('2026-10-27', 'Début de la réservation (Europe : 18 h).', 'Reservation begins (Europe: 18:00 CET).', 'bz-claim'),
    D('2026-11-03', 'Fin de la réservation.', 'Reservation ends.', 'bz-claim'),
    D('2026-11-04', 'Lancement.', 'Launch.', 'bz-roundup')
  ]
}
];
