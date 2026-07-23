# Architecture FleetPro

## 1. Objectif du document

Ce document décrit l’architecture technique de FleetPro, les responsabilités de chaque composant et les choix structurants réalisés pour garantir la maintenabilité, la sécurité et l’évolutivité du projet.

FleetPro suit une architecture modulaire composée :

- d’un backend métier Django REST Framework ;
- d’un service temps réel GPS NestJS ;
- d’une application mobile Expo React Native ;
- d’une passerelle Nginx ;
- d’un stockage relationnel PostgreSQL ;
- d’un stockage éphémère Redis pour les positions GPS.

## 2. Vue d’ensemble

```txt
Application mobile Expo
  | HTTP / WebSocket
  v
Nginx API Gateway
  | REST                       | Socket.io
  v                            v
Backend Django REST            Service GPS NestJS
  | SQL                        | Redis GEO + TTL
  v                            v
PostgreSQL                     Redis
```

L’architecture sépare les responsabilités transactionnelles des responsabilités temps réel :

- le backend Django conserve les données durables : utilisateurs, chauffeurs, véhicules, courses, paiements et notifications ;
- le service GPS NestJS gère uniquement les positions chauffeurs et la diffusion temps réel ;
- Redis stocke les positions GPS avec une durée de vie limitée afin d’éviter de proposer des chauffeurs inactifs ;
- Nginx centralise l’exposition HTTP et WebSocket.

## 3. Composants applicatifs

| Composant | Technologie | Responsabilité |
| --- | --- | --- |
| `mobile/` | Expo, React Native, TypeScript | Interfaces passager et chauffeur, appels REST, connexion Socket.io, paiement mobile |
| `backend/` | Django, DRF, SimpleJWT | Authentification, comptes, courses, paiements, notifications, règles métier |
| `gps-service/` | NestJS, Socket.io | Publication GPS, recherche de chauffeurs proches, diffusion temps réel |
| `postgres` | PostgreSQL | Stockage persistant des données métier |
| `redis` | Redis | Stockage éphémère des positions chauffeurs |
| `nginx` | Nginx | Reverse proxy REST et WebSocket |

## 4. Domaines backend

Le backend Django est découpé par domaines fonctionnels :

- `accounts` : utilisateurs, rôles, profil courant, changement de mot de passe ;
- `rides` : devis, demande de course, cycle de vie, éligibilité FleetHer/Fleet PMR/FleetLuxe ;
- `payments` : PaymentIntent Stripe, paiement simulé, webhook et état de paiement ;
- `notifications` : enregistrement des terminaux et abstraction d’envoi push.

Cette séparation facilite les tests, limite le couplage et permet d’isoler les règles métier importantes dans des services dédiés.

## 5. Flux principaux

### Demande de course

1. Le passager choisit une destination et un type de service depuis l’application mobile.
2. Le mobile demande un devis au backend ou crée directement une course.
3. Le backend calcule le prix, la commission FleetPro et le gain chauffeur.
4. La course passe à l’état `REQUESTED`.
5. Les chauffeurs proches et éligibles peuvent voir la demande.

### Matching chauffeur

1. Le chauffeur passe en ligne depuis l’application mobile.
2. Le mobile publie la position via Socket.io.
3. Le service GPS stocke la position dans Redis avec TTL.
4. Le backend interroge le matching pour filtrer les courses proches.
5. Le backend applique ensuite les règles d’éligibilité métier.

### Suivi temps réel

1. Une course acceptée crée un lien entre passager et chauffeur.
2. Les deux clients rejoignent la salle Socket.io de la course.
3. Les positions du chauffeur sont diffusées uniquement aux utilisateurs autorisés.

## 6. Choix structurants

- Commission fixe : la commission FleetPro est calculée côté backend à `15 %`.
- JWT partagé : Django émet les tokens JWT, le service GPS les vérifie avec le même secret.
- Paiement sécurisé : le mobile ne manipule jamais la clé secrète Stripe.
- Paiement simulé : un mode de démonstration permet de tester le flux complet sans dépendre de Stripe.
- Éligibilité serveur : FleetHer et Fleet PMR sont contrôlés côté backend, pas uniquement dans l’interface.
- GPS éphémère : les positions sont stockées dans Redis avec expiration automatique.
- Reverse proxy unique : Nginx simplifie l’exposition de l’API REST et du WebSocket.

## 7. Sécurité

Les principaux mécanismes de sécurité sont :

- authentification JWT avec refresh token ;
- permissions DRF selon les rôles passager/chauffeur/staff ;
- vérification d’accès aux rooms WebSocket ;
- secrets externalisés dans des variables d’environnement ;
- calculs tarifaires réalisés côté serveur ;
- validation des webhooks Stripe ;
- audits de dépendances dans la CI.

## 8. Exploitabilité

FleetPro peut être exécuté :

- localement avec `docker-compose.yml` ;
- en production MVP avec `docker-compose.prod.yml` sur une instance Scaleway ;
- en cible cloud-native avec Kubernetes Kapsule.

La CI GitHub Actions vérifie les tests, la couverture, le typage, le linting, les audits sécurité et l’analyse SonarQube.
