import {P, I, L, C, TB, S, D, Q} from '../helpers.mjs';

export default [
{
  id: 'article-forever-calendar', code: 'AR01', category: 'news', subcategory: 'calendar',
  title: C('Calendrier de World of Warcraft: Forever, de la bêta aux premiers raids', 'World of Warcraft: Forever schedule, from beta to the first raids'),
  description: C('Toutes les dates officielles : bêta, test de charge, réservation des noms, lancement du 4 novembre (5 novembre à minuit à Paris) et raids du 9 décembre.', 'Every official date: beta, stress test, name reservation, the November 4 launch (midnight November 5 in Paris) and the December 9 raids.'),
  slug: C('calendrier-forever', 'forever-schedule'), illustration: 'news',
  relations: ['forever-news-launch', 'forever-news-access', 'article-forever-beta-recap', 'article-forever-prepare-launch', 'article-forever-raids', 'article-forever-poster'],
  lead: I('Annoncé à la BlizzCon 2026, World of Warcraft: Forever a connu une bêta du 17 septembre au 23 octobre 2026. Il sort le 4 novembre 2026 à 15 h, heure du Pacifique, soit le 5 novembre à minuit à Paris. Les trois premiers raids ouvriront le 9 décembre.',
    'Announced at BlizzCon 2026, World of Warcraft: Forever ran a beta from September 17 to October 23, 2026. It launches on November 4, 2026 at 3:00 p.m. Pacific time, which is midnight on November 5 in Paris. The first three raids open on December 9.',
    'bz-roundup', 'bz-whatsnext', 'forum-kaivax1023', 'bz-raids'),
  keyPoints: [
    I('Lancement mondial : 4 novembre 2026 à 15 h (PST), soit le 5 novembre à minuit, heure de Paris.', 'Worldwide launch: November 4, 2026 at 3:00 p.m. PST, i.e. midnight on November 5, Paris time.', 'bz-roundup', 'bz-whatsnext'),
    I('Réservation anticipée des noms du 27 octobre au 3 novembre pour les offres éligibles ; en Europe, ouverture le 27 octobre à 18 h.', 'Early Name Reservation from October 27 to November 3 for eligible upgrades; in Europe it opens on October 27 at 18:00 CET.', 'bz-claim'),
    I('Raids des profondeurs des Saisons, du sommet d’Hyjal et du repaire d’Onyxia : ouverture le 9 décembre.', 'Barrow Deeps, Hyjal Summit and Onyxia’s Lair raids: opening on December 9.', 'bz-raids'),
    I('Le mode Extrême et la refonte d’un raid emblématique sont prévus après le lancement, sans date annoncée.', 'Hardcore and a revamped iconic raid are planned after launch, with no announced date.', 'bz-whatsnext', 'bz-rulesets')
  ],
  sections: [
    S('avant-lancement', 'Avant le lancement', 'Before launch',
      P('La bêta a commencé le 17 septembre 2026. Elle était réservée aux comptes sélectionnés et aux acheteurs de certaines offres numériques.', 'The beta began on September 17, 2026. It was open to selected accounts and to purchasers of certain digital bundles.', 'bz-beta', 'bz-roundup'),
      P('Un test de charge ouvert à tous, sans abonnement ni invitation, a été déplacé du 19 au 21 octobre. En Europe, il commençait à 19 h (CEST).', 'A stress test open to everyone, with no subscription or invitation required, was moved from October 19 to October 21. In Europe it started at 19:00 CEST.', 'bz-stress'),
      P('L’annonce de la bêta citait le 21 octobre comme « dernière journée complète de test ». Le forum officiel a ensuite fixé la fermeture au vendredi 23 octobre à 10 h (PDT), soit 19 h à Paris. La fermeture a été confirmée le jour même.', 'The beta announcement named October 21 as the “last full day of testing”. The official forum then set the end for Friday, October 23 at 10:00 a.m. PDT (19:00 in Paris), and the closure was confirmed that day.', 'bz-beta', 'forum-kaivax1022', 'forum-kaivax1023')
    ),
    S('noms-et-personnages', 'Noms et création de personnages', 'Names and character creation',
      P('La réservation anticipée des noms est ouverte du 27 octobre au 3 novembre 2026, pour les acheteurs du pack héroïque des Éolides, du pack épique des Éolides ou de la collection Warcraft Forever.', 'Early Name Reservation runs from October 27 to November 3, 2026 for purchasers of the Skyborne Heroic Pack, the Skyborne Epic Pack or the Warcraft Forever Collection.', 'bz-claim', 'bz-names'),
      TB(C('Ouverture des réservations de noms', 'Name reservation start times'), [C('Région'), C('Ouverture', 'Start')], [
        [C('Europe'), C('27 octobre, 18 h (heure de Paris)', 'October 27, 18:00 CET')],
        [C('Amérique du Nord', 'North America'), C('27 octobre, 13 h (PDT)', 'October 27, 1:00 p.m. PDT')],
        [C('Corée', 'Korea'), C('28 octobre, 7 h (KST)', 'October 28, 07:00 KST')],
        [C('Taïwan', 'Taiwan'), C('28 octobre, 7 h (CST)', 'October 28, 07:00 CST')]
      ], 'bz-claim'),
      P('Selon le forum officiel, la création de personnages ouvrira à tous le mardi 27 octobre. Cela laisse le temps de choisir son ensemble de règles et son nom avant le lancement.', 'According to the official forum, character creation opens to everyone on Tuesday, October 27, leaving time to pick a ruleset and a name before launch.', 'forum-kaivax1023')
    ),
    S('apres-lancement', 'Après le lancement', 'After launch',
      P('Les raids des profondeurs des Saisons (10 joueurs), du sommet d’Hyjal (20 joueurs) et du repaire d’Onyxia (40 joueurs) ouvriront le 9 décembre aux personnages de niveau 60. Pour entrer dans le repaire d’Onyxia, il faudra d’abord obtenir l’amulette drakefeu.', 'The Barrow Deeps (10 players), Hyjal Summit (20 players) and Onyxia’s Lair (40 players) raids unlock on December 9 for level 60 characters; Onyxia’s Lair also requires earning the Drakefire Amulet.', 'bz-raids'),
      P('La feuille de route annonce ensuite d’autres raids et donjons, des mises à jour JcJ, du contenu en extérieur, des quêtes supplémentaires de 1 à 60, le mode Extrême et la refonte d’un raid emblématique.', 'The roadmap then lists more raids and dungeons, PvP updates, world content, additional quests across levels 1–60, Hardcore and a revamped iconic raid.', 'bz-whatsnext')
    )
  ],
  confirmed: [
    I('Lancement le 4 novembre 2026 à 15 h (PST), soit le 5 novembre à minuit à Paris.', 'Launch on November 4, 2026 at 3:00 p.m. PST, midnight on November 5 in Paris.', 'bz-roundup', 'bz-whatsnext'),
    I('Bêta fermée le 23 octobre 2026.', 'Beta closed on October 23, 2026.', 'forum-kaivax1023'),
    I('Raids ouverts le 9 décembre.', 'Raids open on December 9.', 'bz-raids')
  ],
  pending: [
    Q('Aucune date n’est annoncée pour le mode Extrême, la refonte d’un raid emblématique ni les mises à jour de contenu suivantes.', 'No date has been announced for Hardcore, the revamped iconic raid or later content updates.'),
    Q('Le « Server Slam » mentionné dans l’annonce de la bêta n’a pas de date dans les sources consultées. Le test de charge du 21 octobre en est peut-être la forme finale, mais aucune source ne le dit.', 'The “Server Slam” mentioned in the beta announcement has no date in the sources consulted; the October 21 stress test may be its final form, but no source says so.')
  ],
  notes: [
    I('Écart de dates pour la fin de la bêta : l’annonce du 17 septembre prévoyait une bêta « through October 21 ». Le forum officiel a fixé puis confirmé une fermeture le 23 octobre. Ce wiki retient le 23 octobre.', 'Beta end date discrepancy: the September 17 announcement said “through October 21”, while the official forum set and confirmed a closure on October 23. This wiki uses October 23.', 'bz-beta', 'forum-kaivax1022', 'forum-kaivax1023')
  ],
  dates: [
    D('2026-09-12', 'Annonce de World of Warcraft: Forever à la BlizzCon 2026 (conférence « L’avenir »).', 'World of Warcraft: Forever announced at BlizzCon 2026 (“What’s Next” panel).', 'bz-whatsnext', 'bz-roundup'),
    D('2026-09-17', 'Début de la bêta.', 'Beta begins.', 'bz-beta', 'bz-roundup'),
    D('2026-10-21', 'Test de charge ouvert à tous (19 h, heure de Paris).', 'Stress test open to all (19:00 CEST).', 'bz-stress'),
    D('2026-10-23', 'Fermeture de la bêta à 10 h (PDT), soit 19 h à Paris.', 'Beta closes at 10:00 a.m. PDT (19:00 Paris).', 'forum-kaivax1022', 'forum-kaivax1023'),
    D('2026-10-27', 'Réservation anticipée des noms (Europe : 18 h) et ouverture de la création de personnages.', 'Early Name Reservation (Europe: 18:00 CET) and character creation opens.', 'bz-claim', 'forum-kaivax1023'),
    D('2026-11-03', 'Fin de la réservation anticipée des noms.', 'Early Name Reservation ends.', 'bz-claim'),
    D('2026-11-04', 'Lancement mondial à 15 h (PST), soit le 5 novembre à minuit à Paris.', 'Worldwide launch at 3:00 p.m. PST (midnight November 5 in Paris).', 'bz-roundup', 'bz-whatsnext'),
    D('2026-12-09', 'Ouverture des raids des profondeurs des Saisons, du sommet d’Hyjal et du repaire d’Onyxia.', 'Barrow Deeps, Hyjal Summit and Onyxia’s Lair unlock.', 'bz-raids')
  ]
},
{
  id: 'article-forever-beta-recap', code: 'AR02', category: 'news', subcategory: 'beta',
  title: C('La bêta de World of Warcraft: Forever (17 septembre – 23 octobre 2026)', 'The World of Warcraft: Forever beta (September 17 – October 23, 2026)'),
  description: C('Accès, contenus testés, test de charge et fermeture : ce que Blizzard a publié sur la bêta, désormais terminée.', 'Access, tested content, stress test and closure: what Blizzard published about the beta, which has now ended.'),
  slug: C('beta-forever-bilan', 'forever-beta-recap'), illustration: 'news',
  relations: ['article-forever-calendar', 'forever-news-launch'],
  lead: I('La bêta de World of Warcraft: Forever s’est ouverte le 17 septembre 2026 et a fermé le 23 octobre 2026. Elle a duré environ cinq semaines. Ce bilan rassemble ce que Blizzard en a dit : qui pouvait y jouer, ce qui était testé et comment elle s’est terminée.',
    'The World of Warcraft: Forever beta opened on September 17, 2026 and closed on October 23, 2026, about five weeks in all. This recap gathers what Blizzard said about it: who could play, what was tested and how it ended.',
    'bz-beta', 'forum-kaivax1023'),
  keyPoints: [
    I('Accès : comptes sélectionnés parmi les volontaires inscrits, et acheteurs du pack épique des Éolides ou de la collection Warcraft Forever.', 'Access: selected opted-in accounts, plus purchasers of the Skyborne Epic Pack or Warcraft Forever Collection.', 'bz-beta', 'bz-roundup'),
    I('Au départ, niveau maximum 20 (relevé à 30 plus tard), avec les Éolides, l’île de Zéphras et deux donjons.', 'At the start: level cap 20 (raised to 30 later), with the Skyborne, Zephras Isle and two dungeons.', 'bz-beta'),
    I('Fermeture le 23 octobre à 10 h (PDT), soit 19 h à Paris, après une journée de célébration en jeu.', 'Closure on October 23 at 10:00 a.m. PDT (19:00 Paris) after a final in-game celebration day.', 'forum-kaivax1022', 'forum-kaivax1023')
  ],
  sections: [
    S('acces', 'Qui pouvait participer', 'Who could take part',
      P('Les joueurs inscrits pouvaient être sélectionnés, et les invitations partaient régulièrement. Les acheteurs d’offres numériques éligibles avaient aussi accès à la bêta. Contre le hameçonnage, Blizzard conseillait, en cas de doute sur une invitation, de se connecter à son compte Battle.net pour la vérifier.', 'Opted-in players could be selected, with invitations sent regularly; eligible digital bundle purchasers also had access. As a guard against phishing, Blizzard advised logging in to the Battle.net account to verify any invitation in doubt.', 'bz-beta'),
      P('Le pack épique des Éolides et la collection Warcraft Forever, édition limitée, incluaient l’accès à la bêta.', 'The Skyborne Epic Pack and the limited-time Warcraft Forever Collection included beta access.', 'bz-roundup', 'bz-beta')
    ),
    S('contenu-teste', 'Ce qui était testé', 'What was tested',
      P('La bêta commençait avec un niveau maximum de 20, relevé à 30 plus tard. La première semaine proposait les Éolides et l’île de Zéphras, les donjons de la salle des Thanes (13-18) et des ruines de Lordaeron (15-20), et toutes les zones jusqu’au niveau 20.', 'The beta began with a level cap of 20, later raised to 30. Week 1 offered the Skyborne and Zephras Isle, the Hall of Thanes (13–18) and Ruins of Lordaeron (15–20) dungeons, and all zone content up to level 20.', 'bz-beta'),
      P('Les présentations de classes parues pendant la bêta prévenaient que techniques et talents pouvaient encore changer.', 'The class deep dives published during the beta warned that abilities and talents could still change.', 'bz-cls-pw', 'bz-cls-hd')
    ),
    S('test-de-charge', 'Le test de charge du 21 octobre', 'The October 21 stress test',
      P('Le test de charge était ouvert à tous, sans abonnement, temps de jeu, invitation ni accès à la bêta. Prévu le 19 octobre, il a été déplacé au 21 octobre. Personnages, noms et guildes créés pendant le test devaient être supprimés avant l’ouverture des réservations de noms, le 27 octobre.', 'The stress test was open to everyone with no subscription, Game Time, invitation or beta access needed. It moved from October 19 to October 21, and characters, names and guilds created there were to be wiped before name reservations opened on October 27.', 'bz-stress')
    ),
    S('fermeture', 'La fermeture', 'The closure',
      P('Le 22 octobre, le forum officiel a annoncé la fin de la bêta pour le lendemain, vendredi 23 octobre à 10 h (PDT). Il annonçait aussi 24 heures de festivités sur l’île de Zéphras, en Dun Morogh, dans la forêt d’Elwynn, à Teldrassil, en Durotar, dans les clairières de Tirisfal et en Mulgore. Blizzard prévenait que des objets et expériences de cette célébration unique ne feraient presque certainement pas partie du jeu lancé.', 'On October 22 the official forum announced the beta would end the next day, Friday October 23 at 10:00 a.m. PDT, with 24 hours of festivities in Zephras Isle, Dun Morogh, Elwynn Forest, Teldrassil, Durotar, Tirisfal Glades and Mulgore; Blizzard warned that items and experiences from this one-time celebration would almost certainly not be part of the launched game.', 'forum-kaivax1022'),
      P('Le 23 octobre, Kaivax, Community Manager, a confirmé : « The WoW Forever Beta is now closed ». Il annonçait quelques jours de travail sur les problèmes prioritaires et sur le service avant le lancement du 4 novembre.', 'On October 23, community manager Kaivax confirmed: “The WoW Forever Beta is now closed”, announcing a few days of work on priority issues and the game service before the November 4 launch.', 'forum-kaivax1023'),
      P('L’épisode 5 du podcast officiel, consacré à la fin de la bêta, réunit l’animateur Countdown To Classic, l’invitée Meeix et quatre membres de l’équipe : Josh « Aggrend » Greenfield, Clay Stone, Ana Resendez et Michael Nuthals.', 'Episode 5 of the official podcast, an end-of-beta special, features host Countdown To Classic, guest Meeix and four team members: Josh “Aggrend” Greenfield, Clay Stone, Ana Resendez and Michael Nuthals.', 'bz-podcast5', 'bz-weekly1023')
    )
  ],
  confirmed: [
    I('Bêta ouverte le 17 septembre 2026.', 'Beta opened on September 17, 2026.', 'bz-beta'),
    I('Bêta fermée le 23 octobre 2026.', 'Beta closed on October 23, 2026.', 'forum-kaivax1023'),
    I('Lancement maintenu au 4 novembre 2026.', 'Launch still set for November 4, 2026.', 'forum-kaivax1023')
  ],
  pending: [
    Q('Le contenu du podcast « fin de bêta » n’est disponible qu’en vidéo, sans transcription officielle. Il n’est donc pas résumé ici.', 'The end-of-beta podcast is only available as video with no official transcript, so it is not summarized here.'),
    Q('Les sources consultées ne disent pas quand le niveau maximum est passé à 30, ni quelles zones et quels donjons ont été ouverts ensuite.', 'The sources consulted do not say when the level cap was raised to 30, nor which later zones and dungeons were opened.'),
    Q('Les résultats de la bêta (corrections, équilibrage) ne sont pas détaillés.', 'The outcomes of the beta (fixes, tuning) are not detailed.')
  ],
  notes: [
    I('L’annonce de la bêta parlait du 21 octobre comme dernière journée complète de test. La fermeture effective, confirmée par le forum, a eu lieu le 23 octobre.', 'The beta announcement called October 21 the last full day of testing; the actual closure, confirmed on the forum, was October 23.', 'bz-beta', 'forum-kaivax1023')
  ],
  dates: [
    D('2026-09-17', 'Ouverture de la bêta.', 'Beta opens.', 'bz-beta'),
    D('2026-10-21', 'Test de charge ouvert à tous.', 'Stress test open to all.', 'bz-stress'),
    D('2026-10-22', 'Journée de célébration de fin de bêta et podcast spécial.', 'End-of-beta celebration day and special podcast.', 'forum-kaivax1022', 'bz-podcast5'),
    D('2026-10-23', 'Fermeture de la bêta (19 h à Paris).', 'Beta closes (19:00 Paris).', 'forum-kaivax1023')
  ]
}

,
{
  id: 'article-forever-poster', code: 'AR15', category: 'news', subcategory: 'events',
  title: C('Séance de dédicaces Forever à l’Irvine Improv (2 novembre 2026)', 'Forever poster signing at the Irvine Improv (November 2, 2026)'),
  description: C('Événement officiel annoncé le 26 octobre : dédicaces le 2 novembre à Irvine ; billets gratuits via TIXR dès le 27 octobre à 12 h PDT. Page FR introuvable le 27/10.', 'Official event announced October 26: signing on November 2 in Irvine; free TIXR tickets from October 27 at 12:00 p.m. PDT. No FR page found on 10/27.'),
  slug: C('dedicaces-irvine-improv', 'irvine-improv-poster-signing'), illustration: 'news',
  relations: ['article-forever-calendar', 'forever-news-launch'],
  lead: I('Le 26 octobre 2026, Blizzard a annoncé une séance de dédicaces Forever le 2 novembre 2026 à l’Irvine Improv (Californie). Les billets gratuits ouvrent sur TIXR le mardi 27 octobre à 12 h (PDT). Aucune page française n’a été trouvée le 27 octobre (HTTP 404).',
    'On October 26, 2026 Blizzard announced a Forever poster signing on November 2, 2026 at the Irvine Improv (California). Free tickets open on TIXR on Tuesday, October 27 at 12:00 p.m. PDT. No French page was found on October 27 (HTTP 404).',
    'bz-poster'),
  keyPoints: [
    I('Date de l’événement : 2 novembre 2026, Irvine Improv.', 'Event date: November 2, 2026, Irvine Improv.', 'bz-poster'),
    I('Billets gratuits TIXR à partir du 27 octobre à 12 h PDT.', 'Free TIXR tickets from October 27 at 12:00 p.m. PDT.', 'bz-poster'),
    I('Entrée seulement avec billet / QR code au créneau réservé.', 'Entry only with a ticket / QR code for the reserved time slot.', 'bz-poster'),
    I('Lancement du jeu toujours annoncé le 4 novembre 2026.', 'Game launch still announced for November 4, 2026.', 'bz-poster', 'bz-roundup')
  ],
  sections: [
    S('event', 'Ce que dit l’annonce', 'What the announcement says',
      P('Blizzard invite à rencontrer des développeurs et d’autres joueurs avant la sortie du 4 novembre. La jauge est limitée. Il est recommandé d’arriver tôt dans la fenêtre horaire indiquée ; l’entrée se fait par scan du QR code sous la tente d’accueil.',
        'Blizzard invites players to meet developers and fellow adventurers before the November 4 release. Attendance is limited. Guests should arrive early in their window; entry is by QR-code scan at the check-in tent.',
        'bz-poster'),
      P('L’Irvine Improv est indiqué comme accessible PMR (ADA). Sans billet, l’accès ne sera pas possible.',
        'Irvine Improv is described as ADA compliant. Without a ticket, entry will not be possible.',
        'bz-poster')
    ),
    S('langue', 'Disponibilité linguistique', 'Language availability',
      P('Le 27 octobre 2026, la page anglaise répond en HTTP 200. La tentative fr-fr sur le même identifiant d’article renvoie HTTP 404. Ce wiki ne traduit donc pas au-delà d’une synthèse, et marque l’absence de source FR.',
        'On October 27, 2026 the English page returns HTTP 200. A fr-fr attempt on the same article id returns HTTP 404. This wiki therefore only offers a synthesis and flags the missing FR source.',
        'bz-poster')
    )
  ],
  confirmed: [
    I('Événement le 2 novembre 2026 à l’Irvine Improv.', 'Event on November 2, 2026 at the Irvine Improv.', 'bz-poster'),
    I('Ouverture des billets le 27 octobre à 12 h PDT.', 'Tickets open October 27 at 12:00 p.m. PDT.', 'bz-poster')
  ],
  pending: [
    Q('Horaires exacts des créneaux et liste des développeurs présents : renvoyés vers la page d’événement / TIXR, non recopiés ici.', 'Exact time slots and attending developers: deferred to the event / TIXR page, not copied here.'),
    Q('Une éventuelle page FR ultérieure n’était pas en ligne le 27/10/2026.', 'Any later FR page was not online on 2026-10-27.')
  ],
  notes: [
    I('Source EN seulement au moment de la rédaction (27/10/2026).', 'EN-only source at authoring time (2026-10-27).', 'bz-poster')
  ],
  dates: [
    D('2026-10-26', 'Publication de l’annonce.', 'Announcement published.', 'bz-poster'),
    D('2026-10-27', 'Ouverture des billets TIXR (12 h PDT).', 'TIXR tickets open (12:00 p.m. PDT).', 'bz-poster'),
    D('2026-11-02', 'Séance de dédicaces.', 'Poster signing.', 'bz-poster'),
    D('2026-11-04', 'Lancement de Forever.', 'Forever launch.', 'bz-roundup')
  ]
}

];
