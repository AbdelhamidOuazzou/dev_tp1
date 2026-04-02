Q1 : Pourquoi <Navigate /> (composant) et pas navigate() (hook) ici ?
=>Ce code s'exécute pendant la phase de rendu de React, navigate() est fait pour être appelé en dehors du rendu par exemple un handler ou un useEffect.


Q2 : Quelle différence entre navigate(from) et navigate(from, { replace: true }) ?
=>La différence principale réside dans la façon dont le routeur gère l'historique du navigateur ce qui impacte le comportement du bouton Retour

Q3 : Après un POST, pourquoi fait-on setProjects(prev => [...prev, data]) plutôt qu’un
re-fetch GET ?
=>Cela permet d'afficher le nouveau projet instantanément pour l'utilisateur tout en évitant une requête réseau complète qui surchargerait inutilement le serveur.

Q5 : Quelle différence entre <Link> et <NavLink> ? Pourquoi NavLink ici ?
=> <NavLink> possède une propriété isActive permettant d'appliquer un style CSS conditionnel quand l'URL correspond au lien, contrairement à <Link>. On l'utilise ici pour mettre en évidence le projet actuellement sélectionné dans la barre latérale.

Q6 : Ce composant sert pour le POST ET le PUT. Qu'est-ce qui change entre les deux usages ?
=> Ce qui change, ce sont les props passées par le composant parent : pour un POST, les champs sont initialisés vides et la soumission crée un élément ; pour un PUT, les champs sont pré-remplis avec les données existantes et la soumission les met à jour.

Q7 : Arrêtez json-server et tentez un POST. Le message s'affiche ?
=> Oui, le message s'affiche. Sans le serveur, la requête échoue (Network Error) et Axios lève immédiatement une exception qui est capturée par le bloc catch pour mettre à jour l'état d'erreur et l'afficher dans l'interface.

Q8 : Avec fetch, un 404 ne lance PAS d'erreur. Avec Axios, que se passe-t-il ?
=> Contrairement à fetch, Axios lance automatiquement une exception pour tous les statuts HTTP d'erreur (4xx et 5xx), ce qui vous fait entrer directement dans le bloc catch.



TP4
Q1 : Je n'ai écrit aucune ligne de CSS car Material UI intègre tout le style directement dans les composants via la propriété sx.

Q2 : React-Bootstrap est plus court à écrire grâce à ses classes utilitaires, mais Material UI est structurellement plus lisible grâce à ses balises explicites.

Q3 : Je préfère le système de classes de Bootstrap car il garde le code JSX plus léger visuellement, même si la propriété sx de MUI est pratique pour lier des variables JavaScript au style.

Q4 : Je choisirais Material UI car ses composants préfabriqués (tableaux, sélecteurs) sont beaucoup plus puissants et adaptés pour un tableau de bord professionnel comme TaskFlow.

Q5 : React s'exécutant sur le navigateur de l'utilisateur, une connexion directe obligerait à exposer publiquement les mots de passe de la base de données, créant une faille de sécurité majeure.

Q6 : On ne l'utiliserait pas en production car il n'offre aucune sécurité d'authentification, ne gère pas les modifications simultanées et a de mauvaises performances.

Q7 : Firebase est un "Backend as a Service" qui gère la sécurité non pas par un mot de passe global caché, mais via des règles d'accès vérifiées directement sur ses propres serveurs pour chaque requête client.

Q8 : Il faudrait développer une véritable API (avec Java, Node.js, etc.), configurer une vraie base de données (comme MySQL), et mettre en place une authentification sécurisée par token.

Q9 : Le risque principal est d'alourdir inutilement l'application et d'être forcé de réécrire son code si ces bibliothèques font des mises à jour incompatibles avec les anciennes versions.

Q10 : Je choisirais Firebase ou un Backend personnalisé (avec WebSockets) car json-server est incapable de gérer les flux de données en temps réel nécessaires pour un chat.