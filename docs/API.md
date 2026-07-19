# API FleetPro

Base locale via Nginx: `http://localhost:8090/api/v1`

## Authentification

- `POST /auth/token/`: obtient `access` et `refresh`.
- `POST /auth/token/refresh/`: renouvelle un token.
- `POST /accounts/`: cree un passager ou un chauffeur.
- `GET /accounts/me/`: retourne le profil connecte.
- `PATCH /accounts/me/`: modifie le nom et le telephone du profil.
- `POST /accounts/change-password/`: change le mot de passe courant.
- `GET|POST /driver-profiles/`: consulte ou cree le profil chauffeur.
- `GET|POST /vehicles/`: gere les vehicules du chauffeur.

## Courses

- `POST /rides/quote/`: calcule prix, commission FleetPro et gain chauffeur.
- `GET /rides/`: liste les courses visibles selon le role.
- `POST /rides/`: cree une course passager.
- `POST /rides/{id}/accept/`: accepte une course cote chauffeur.
- `POST /rides/{id}/start/`: demarre une course acceptee.
- `POST /rides/{id}/complete/`: cloture une course en cours.
- `POST /rides/{id}/cancel/`: annule une course ouverte.

## Paiements

- `POST /payments/create-intent/`: cree un PaymentIntent Stripe test pour une course.
- `POST /payments/webhook/`: recoit les evenements Stripe signes.
- `POST /payments/simulate-intent/`: cree une autorisation de paiement simulee pour la demo sans appeler Stripe.
- `GET /payments/`: liste les paiements du passager.

## Notifications

- `POST /notifications/devices/`: enregistre un token Firebase Cloud Messaging.
- `GET /notifications/devices/`: liste les devices de l'utilisateur.

## GPS Socket.io

Endpoint local: `http://localhost:8090/socket.io`

Le client fournit le JWT dans `auth.token`.

- `driver:position`: publie une position chauffeur.
- `drivers:nearby`: retourne les chauffeurs proches via Redis GEO.
- `gps:ready`: evenement serveur apres authentification.
- `ride:join`: rejoint la salle privee d'une course apres verification par le core.
- `driver:position:updated`: diffuse la position uniquement dans la salle de la course.
