TP 01 - Du CSR au SSR

Q1 : Comparez la structure de votre projet React (Vite) avec Next.js. Quelles différences ?
En React, le routing est défini dans le code avec react-router-dom. En Next.js, le routing est géré automatiquement par la structure des dossiers dans le répertoire app.

Q2 : Combien de fichiers avez-vous créé pour cette route ? Comparez avec React Router.
Un seul fichier page.tsx suffit pour créer une route complète. C'est beaucoup plus simple que React Router qui impose de créer le composant, de l'importer et de déclarer la route
dans App.tsx.

Q3 : En React, on utilisait useParams(). En Next.js, comment est-il récupéré ? Quelle différence fondamentale ?
L'ID est récupéré via la prop params directement passée au composant. La différence est que cela se passe sur le serveur, alors que useParams() est un hook qui s'exécute côté
client.

Q5 : En React SPA, combien de lignes fallait-il pour charger les projets ? Combien ici ?
En SPA, il fallait au moins une dizaine de lignes avec useState, useEffect et fetch. Ici, deux lignes suffisent car on peut faire un fetch direct dans un composant asynchrone.

Q6 : Ouvrez F12 > Network. Voyez-vous la requête GET /projects ? Pourquoi ?
Non, la requête n'apparaît pas dans l'onglet Network du navigateur. C'est parce que le fetch est effectué par le serveur Next.js avant d'envoyer le HTML déjà rempli au client.

Q7 : Pourquoi faut-il 'use client' ici et pas dans la page Dashboard ?
La page Dashboard ne fait que de l'affichage pur, donc un Server Component suffit. La page Login nécessite de l'interactivité pour gérer l'état du formulaire et les événements de
soumission.

Q8 : En React, on utilisait useNavigate(). En Next.js, quel est l’équivalent ?
L'équivalent est le hook useRouter() importé de next/navigation.

Q9 : Que voyez-vous dans le code source HTML (React SPA) ? Y a-t-il les noms des projets ?
On ne voit qu'une balise div vide avec l'ID root. Les noms des projets ne sont pas présents car ils sont chargés plus tard par le JavaScript.

Q10 : Que voyez-vous cette fois (Next.js) ? Les noms des projets sont-ils dans le HTML ?
Tout le contenu est présent directement dans le code source HTML. Les noms des projets sont bien là car la page a été générée sur le serveur (SSR).

Q11 : Le Header dans layout.tsx ne se re-monte pas quand on navigue. En React Router, comment faisait-on ?
On plaçait le composant Header en dehors du switch des routes dans App.tsx.

Q12 : En Next.js, si je veux un layout spécifique au Dashboard, où est-ce que je crée le fichier ?
Il suffit de créer un fichier layout.tsx directement à l'intérieur du dossier app/dashboard/.

Q13 : Le Dashboard est un Server Component. Peut-il utiliser onClick ? Pourquoi ?
Non, car onClick nécessite du JavaScript côté client pour fonctionner. Les Server Components ne supportent pas les gestionnaires d'événements interactifs.

Q14 : Si je veux ajouter un bouton « + Nouveau projet » sur le Dashboard, dois-je transformer TOUTE la page en Client Component ?
Non, il est préférable d'isoler uniquement le bouton ou le formulaire dans un composant séparé marqué use client.

Q15 : Quel avantage de sécurité apporte le fetch côté serveur ?
L'URL de l'API et les éventuelles clés secrètes ne sont jamais exposées au navigateur de l'utilisateur. Cela empêche quiconque de voir où et comment les données sont réellement
récupérées.

  ---

TP 02 - Server Actions, API Routes & Auth

Q1 : En React SPA, que fallait-il faire après un POST pour voir le nouveau projet ? Ici ?
En SPA, il fallait manuellement mettre à jour l'état local avec setProjects. Ici, il suffit d'appeler revalidatePath pour que Next.js rafraîchisse les données automatiquement.

Q3 : Le bouton supprimer est un <form> avec un <input type="hidden">. Pourquoi pas un onClick ?
Comme le Dashboard est un Server Component, il ne supporte pas onClick. Utiliser un formulaire est la méthode native du web pour envoyer des données au serveur sans JavaScript.

Q4 : Testez /api/projects dans le navigateur. Que voyez-vous ?
On voit la liste des projets affichée au format JSON brut.

Q5 : Quelle est la différence entre une API Route et une Server Action ?
Une API Route est un endpoint HTTP classique accessible par n'importe quel client externe. Une Server Action est une fonction sécurisée appelée directement depuis un formulaire
Next.js.

Q6 : Comparez ce Login avec celui de React SPA. Combien de useState en moins ?
On en utilise beaucoup moins, voire aucun si on utilise useActionState. On n'a plus besoin de gérer manuellement l'état de chaque champ ou du chargement.

Q7 : Pouvez-vous lire le cookie 'session' avec document.cookie dans la console ?
Non, car le cookie est marqué HttpOnly. Cela le rend invisible pour le JavaScript du navigateur afin d'éviter les vols de session.

Q8 : En React SPA, ProtectedRoute affichait brièvement le Dashboard avant de rediriger. Ici ?
Ici, il n'y a aucun flash de contenu. Le middleware intercepte la requête avant même que la page ne commence à se charger.

Q9 : Le middleware.ts est à la racine, pas dans app/. Pourquoi ?
C'est une règle de Next.js pour qu'il puisse intercepter toutes les requêtes du projet, pas seulement celles d'un dossier spécifique.

Q10 : En React SPA, pour le user, comment faisait-on ?
On utilisait généralement un Context API avec un hook useAuth() et un état global.

Q11 : Server Actions vs API Routes — lequel utiliseriez-vous pour un formulaire ? Pour une app mobile ?
J'utiliserais une Server Action pour le formulaire du site web. Pour une application mobile, une API Route est indispensable car elle peut être consommée par d'autres
plateformes.

Q12 : Quel avantage de sécurité pour cookies + middleware ?
La vérification se fait côté serveur avant l'envoi du HTML, ce qui est bien plus robuste. Les cookies HttpOnly protègent aussi contre les attaques XSS.

Q13 : Si vous arrêtez json-server, les API Routes fonctionnent-elles toujours ? Pourquoi ?
Oui, car nous avons réécrit les API Routes pour qu'elles lisent et écrivent directement dans le fichier db.json avec le module fs.

Q14 : Le cookie est HttpOnly. Un script XSS injecté dans la page peut-il le voler ?
Non, le flag HttpOnly interdit l'accès au cookie via document.cookie. Le script malveillant ne pourra donc pas récupérer le jeton de session.