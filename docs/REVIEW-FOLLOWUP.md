# Suite à la revue de la livraison dc364da

Revue fournie par l’utilisateur dans `REVUE.md`, datée du 30 octobre 2026. Correctifs réalisés uniquement dans la branche locale `codex/community-redesign`. Aucun accès SSH/Hetzner, aucun changement Caddy, aucune installation distante, aucun push ni déploiement.

## Corrections réalisées

| Observation | Réponse |
| --- | --- |
| 61e visiteur anonyme bloqué et une session créée pour chaque GET | Plus aucune session SQLite ni compteur de création au GET anonyme. La sonde de 70 visiteurs réussit ; le formulaire de connexion utilise un cookie CSRF signé temporaire, et alloue une session seulement au POST valide. Les écritures d’activité des sessions existantes sont regroupées à une par minute. |
| Budgets partagés derrière Caddy | Confiance désactivée par défaut, activable pour les seules adresses exactes des proxys immédiats. Un saut X-Forwarded-For uniquement, validation de l’IP, aucun hôte/protocole/préfixe de proxy accepté. Tests : 12 clients distincts derrière un proxy autorisé se connectent ; changer l’en-tête depuis un pair non autorisé ne contourne pas les limites. Configuration cible indispensable avant le public. |
| Installateur dangereux | `install.sh` neutralisé : message et sortie 1, sans modification. Test de non-exécution de commandes destructrices et de services. |
| Mention Blizzard | Phrase exacte dans le gabarit partagé : « Site indépendant et non officiel de Blizzard Entertainment. » |
| Collision des IDs d’audit à l’effacement | Cibles typées et migration idempotente au schéma 2. Effacer `user:1` n’altère plus `post:1`, `topic:1`, `report:1` ou `category:1`. L’auteur modérateur d’une action visant l’utilisateur reste identifiable ; l’identité de l’utilisateur comme acteur est retirée par la FK. |
| Pas de sauvegarde automatique | Commande `backup-daily`, service et timer privés, rotation locale de 30 jours, répertoire 0700, snapshots 0600, intégrité vérifiée avant rotation. Les liens et fichiers étrangers ne sont pas supprimés. Chiffrement/transfert hors serveur non configurés. |
| Test impossible dans une archive sans Git | Test de préservation séparé du service des pages. Manifeste de 100 empreintes SHA-256 issu du commit initial et vérifié contre Git dans le clone complet ; utilisable aussi dans une archive sans `.git`. Ce manifeste ne remplace pas une signature d’authenticité. |
| Chemins et disponibilité du wiki | `/srv/wow4ever` indiqué comme chemin communiqué par la revue, sans prétendre l’avoir vérifié. Préproduction inchangée : tunnel et répertoires dédiés. Proposition de production future corrigée : export public propre du wiki servi par Caddy, proxy limité aux chemins dynamiques. Aucun fragment n’a été appliqué sur le serveur. |
| Durcissement systemd | Modes d’état 0700 et protections supplémentaires préparées dans les unités. À vérifier sur la distribution cible, aucune installation ici. |

Un test navigateur supplémentaire a révélé le blocage par CSP de la redirection de formulaire vers Discord. La destination OAuth fixe est désormais autorisée uniquement sur le compte et le départ de connexion. Le contrôle Chromium intercepte Discord ; aucune vraie application Discord n’est contactée. La recette réelle reste nécessaire.

## Validation

- 29 tests serveur réussis dans le clone complet ; préservation des 100 pages vérifiée avec Git.
- Même suite exécutée sur une archive extraite sans `.git` pour vérifier la portabilité du manifeste et du contrôle des fichiers publics.
- 41 contrôles navigateur, dont 14 scans axe et la redirection OAuth simulée ; les résultats finaux sont dans `docs/evidence/`.
- Audit des 14 dépendances runtime renouvelé : aucun avis connu dans ce résultat ponctuel ; `pip check` réussi.
- Bandit : sept alertes B608 sur assemblages SQL à constantes examinées, aucune alerte élevée. Les constats restent visibles, sans suppression du moteur d’analyse.

Les unités systemd et le fragment Caddy sont des fichiers préparatoires : ils n’ont pas été vérifiés sur le serveur réel. Aucun test de charge global, audit d’intrusion indépendant ou certification d’accessibilité n’est revendiqué.

## Blocages publics restant ouverts

1. **Suspension après suppression** : la suppression/recréation permet encore de contourner une suspension. Définir le périmètre, la durée et la clé indépendante d’une empreinte de bannissement, sa base et les personnes habilitées, puis implémenter et tester. Une empreinte HMAC est une donnée pseudonymisée, pas anonyme. Ce traitement supplémentaire n’est pas activé sans décision de politique.
2. **Preuves de modération** : la suppression enlève actuellement aussi les signalements visant les contributions du compte. Définir les cas de conservation, durées, accès, traitement des demandes et purge, puis implémenter les instantanés restreints nécessaires. Aucune obligation LCEN/DSA particulière n’est présumée applicable sans examen.
3. **Discord, RGPD et accessibilité** : application Discord de test et vraie recette ; identité/contact et liste vérifiée des prestataires ; bases/durées ; lecteur d’écran/zoom ; deux administrateurs et équipe de modération.
4. **Exploitation** : installation autorisée de la préproduction, vérification en lecture seule des versions/réseau cible, logs OAuth/IP, sauvegardes chiffrées et hors serveur, registre restreint des effacements à rejouer, restauration et tests de charge. Aucune prestation payante souscrite.
5. **Maquettes et choix produit** : maquettes ou validation du rendu ; forums français/bilingues ; durée de session (inchangée : 1 h inactive, 24 h absolues).

La suite reste une **préproduction privée pour comptes de test**, sans autorisation de publication. Le choix recommandé pour commencer demeure le tunnel SSH sans changement de Caddy ; le propriétaire choisit et autorise toute intervention distante séparément.
