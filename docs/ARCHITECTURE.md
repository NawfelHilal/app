# Architecture FleetPro

## Vue d'ensemble

FleetPro separe le metier transactionnel du temps reel:

- Le core Django porte les donnees durables: utilisateurs, chauffeurs, courses, paiements, tokens de notification.
- Le satellite GPS NestJS porte uniquement l'etat ephemere des positions chauffeurs.
- Redis expire automatiquement les positions GPS pour eviter d'afficher un chauffeur inactif.
- Nginx centralise les entrees HTTP et WebSocket.

```txt
Mobile Expo
  | HTTPS / WSS
  v
Nginx
  | REST                  | Socket.io
  v                       v
Django REST API           NestJS GPS
  | SQL                   | GEO + TTL
  v                       v
PostgreSQL                Redis
```

## Choix structurants

- Commission plateforme fixe: `15 %`, calculee cote backend dans le domaine `rides`.
- JWT partage: SimpleJWT cote Django, secret compatible cote GPS pour authentifier les sockets.
- Paiement Stripe: le backend cree les PaymentIntents, le mobile ne manipule jamais de secret.
- Paiement demo: un gateway simule l'autorisation puis la capture en fin de course pour presenter le flux complet sans dependance externe.
- Notifications: abstraction `PushNotificationGateway` pour garder Firebase remplacable et testable.
- GPS: positions TTL dans Redis et index GEO separe pour les recherches de chauffeurs proches.

## Domaines backend

- `accounts`: roles, inscription, profil courant.
- `rides`: devis, cycle de vie d'une course, commission.
- `payments`: PaymentIntent Stripe et etat local.
- `notifications`: enregistrement de devices et envoi push.

## Qualite attendue Bloc 2

- Separation des responsabilites par application Django.
- Services metier testables hors des vues.
- Variables d'environnement pour secrets et endpoints.
- CI avec tests backend, tests GPS et verification TypeScript mobile.
- Infrastructure locale reproductible via Docker Compose.
