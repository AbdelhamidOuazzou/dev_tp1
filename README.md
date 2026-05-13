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

---
**Séance 5 - Réponses du TP**

Q1 : Le script s’exécute-t-il ? Pourquoi ? Que fait React avec les strings dans le JSX ?
=> Non, le script ne s'exécute pas. React échappe automatiquement les strings dans le JSX pour prévenir les attaques XSS. Le HTML est affiché comme du texte brut et n'est pas interprété.

Q2 : Que se passe-t-il cette fois ? Supprimez ce code immédiatement après le test.
=> Le script s'exécute et une popup d'alerte apparaît (si le code malveillant l'inclut). Utiliser `dangerouslySetInnerHTML` désactive la protection de React et interprète le HTML, ce qui expose à des failles XSS.

Q3 : Ouvrez Network (F12). Faites un GET /projects. Voyez-vous le header Authorization: Bearer ... ?
=> Oui, grâce à l'intercepteur Axios qu'on a configuré, l'en-tête "Authorization: Bearer <token>" est automatiquement injecté dans toutes les requêtes sortantes.

Q4 : Pourquoi stocker le token en mémoire (state React) et PAS dans localStorage ?
=> Le `localStorage` est accessible par n'importe quel script JavaScript de la page, ce qui est dangereux en cas de faille XSS. Le state de React est isolé en mémoire dans l'application, limitant ce risque.

Q5 : Comparez authSlice.ts avec votre ancien authReducer.ts. Qu’est-ce qui a changé ?
=> Avec Redux Toolkit (`authSlice.ts`), la librairie utilise Immer en coulisse. Cela permet d'écrire du code de manière mutable (`state.loading = true`) alors que l'état reste immuable. De plus, il n'y a plus besoin d'écrire de `switch/case` ni de définir manuellement les types d'actions.

Q6 : Combien de composants se re-rendent quand on toggle la sidebar ? Lesquels ne DEVRAIENT PAS ?
=> Sans optimisation, plusieurs composants se re-rendent inutilement, notamment `MainContent` qui n'a pourtant rien à voir avec l'état de la Sidebar.

Q7 : Pourquoi MainContent ne se re-rend plus ? Que compare React.memo ?
=> Il ne se re-rend plus car `React.memo` fait une comparaison superficielle (shallow compare) des props. Puisque la référence du tableau `columns` n'a pas changé, React ignore ce rendu.

Q8 : Quelle différence entre useMemo et useCallback ? Quand utiliser chacun ?
=> `useMemo` mémorise le résultat d'un calcul coûteux et s'utilise pour retourner une valeur. `useCallback` mémorise la référence d'une fonction pour éviter qu'elle ne soit recréée à chaque rendu. On utilise `useCallback` quand on passe une fonction en prop à un composant enfant (optimisé avec React.memo) pour éviter de casser sa mémoïsation.

Q10 : Pour chaque action, notez : quels composants se re-rendent ? Combien de temps prend le render ? Y a-t-il des re-renders inutiles après vos optimisations React.memo ?
=> Grâce à `React.memo` et `useCallback`, lors du toggle de la sidebar, seul le `Dashboard` et la `Sidebar` se re-rendent. `MainContent` est préservé, ce qui élimine les re-renders inutiles et réduit le temps de traitement vu dans le Profiler.
