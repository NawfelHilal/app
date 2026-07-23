# API FleetPro

## 1. Objectif du document

Ce document décrit les principales routes REST et WebSocket exposées par FleetPro. Il sert de référence technique pour l’intégration mobile, la recette fonctionnelle et la maintenance de l’API.

Base locale via Nginx :

```txt
http://localhost:8090/api/v1
```

Base production :

```txt
http://<domaine-ou-ip-scaleway>/api/v1
```

## 2. Authentification

L’API utilise une authentification JWT basée sur `djangorestframework-simplejwt`.

| Méthode | Route | Description |
| --- | --- | --- |
| `POST` | `/auth/token/` | Authentifie un utilisateur et retourne `access` et `refresh`. |
| `POST` | `/auth/token/refresh/` | Renouvelle le token d’accès. |
| `POST` | `/accounts/` | Crée un compte passager ou chauffeur. |
| `GET` | `/accounts/me/` | Retourne le profil de l’utilisateur connecté. |
| `PATCH` | `/accounts/me/` | Met à jour le profil courant. |
| `POST` | `/accounts/change-password/` | Change le mot de passe de l’utilisateur connecté. |

Les endpoints métier nécessitent un header :

```http
Authorization: Bearer <access_token>
```

## 3. Profils chauffeurs et véhicules

| Méthode | Route | Description |
| --- | --- | --- |
| `GET` | `/driver-profiles/` | Liste les profils chauffeurs visibles par l’utilisateur. |
| `POST` | `/driver-profiles/` | Crée le profil professionnel du chauffeur connecté. |
| `GET` | `/vehicles/` | Liste les véhicules du chauffeur connecté. |
| `POST` | `/vehicles/` | Ajoute un véhicule au chauffeur connecté. |

Champs professionnels chauffeur :

- `license_number`
- `professional_card_number`
- `company_name`
- `siret_number`
- `insurance_policy_number`
- `gender`
- `is_fleether_eligible`
- `is_fleet_pmr_eligible`
- `is_professional_profile_complete`

Champs PMR véhicule :

- `is_pmr_adapted`
- `pmr_certification_reference`

## 4. Courses

| Méthode | Route | Description |
| --- | --- | --- |
| `POST` | `/rides/quote/` | Calcule le prix, la commission FleetPro et le gain chauffeur. |
| `GET` | `/rides/` | Liste les courses visibles selon le rôle. |
| `POST` | `/rides/` | Crée une demande de course passager. |
| `GET` | `/rides/{id}/` | Retourne le détail d’une course. |
| `POST` | `/rides/{id}/accept/` | Accepte une course côté chauffeur. |
| `POST` | `/rides/{id}/start/` | Démarre une course acceptée. |
| `POST` | `/rides/{id}/complete/` | Termine une course en cours. |
| `POST` | `/rides/{id}/cancel/` | Annule une course ouverte. |
| `POST` | `/rides/{id}/simulate/` | Fait avancer une course en mode démonstration passager. |
| `POST` | `/rides/simulate-nearby-request/` | Crée une demande passager proche du chauffeur connecté en mode démo. |

Types de service acceptés :

- `STANDARD` : course classique ;
- `FLEETHER` : course réservée aux chauffeurs femmes éligibles ;
- `FLEET_PMR` : course réservée aux chauffeurs avec véhicule adapté PMR ;
- `FLEET_LUXE` : course premium sans restriction métier spécifique.

Le backend filtre les courses visibles côté chauffeur et refuse l’acceptation si le chauffeur n’est pas éligible au service demandé.

## 5. Paiements

| Méthode | Route | Description |
| --- | --- | --- |
| `POST` | `/payments/create-intent/` | Crée un PaymentIntent Stripe pour une course. |
| `POST` | `/payments/simulate-intent/` | Crée une autorisation de paiement simulée. |
| `POST` | `/payments/webhook/` | Reçoit les événements Stripe signés. |
| `GET` | `/payments/` | Liste les paiements accessibles à l’utilisateur. |

Le mobile ne manipule jamais la clé secrète Stripe. Le backend reste responsable de la création et de la validation des paiements.

## 6. Notifications

| Méthode | Route | Description |
| --- | --- | --- |
| `GET` | `/notifications/devices/` | Liste les terminaux enregistrés. |
| `POST` | `/notifications/devices/` | Enregistre ou met à jour un token de notification. |

Les notifications natives complètes nécessitent un development build Expo configuré avec Firebase/APNs.

## 7. Hypermedia et niveau REST

Les ressources principales retournent des liens `_links` afin d’exposer les actions disponibles selon le rôle et l’état de la ressource.

Exemple :

```json
{
  "id": 16,
  "status": "REQUESTED",
  "_links": {
    "self": {"href": "http://localhost:8090/api/v1/rides/16/", "method": "GET"},
    "collection": {"href": "http://localhost:8090/api/v1/rides/", "method": "GET"},
    "cancel": {"href": "http://localhost:8090/api/v1/rides/16/cancel/", "method": "POST"},
    "payment_intent": {"href": "http://localhost:8090/api/v1/payments/create-intent/", "method": "POST"}
  }
}
```

Cette approche positionne l’API sur un niveau REST 2 avec une évolution vers le niveau 3 du modèle de Richardson.

## 8. WebSocket GPS

Endpoint local :

```txt
http://localhost:8090/socket.io
```

Endpoint production :

```txt
http://<domaine-ou-ip-scaleway>/socket.io
```

Le client fournit le token JWT dans `auth.token`.

Événements principaux :

| Événement | Sens | Description |
| --- | --- | --- |
| `gps:ready` | Serveur → client | Confirme l’authentification Socket.io. |
| `driver:position` | Client → serveur | Publie la position du chauffeur. |
| `drivers:nearby` | Client → serveur | Recherche les chauffeurs proches. |
| `ride:join` | Client → serveur | Rejoint la salle privée d’une course. |
| `driver:position:updated` | Serveur → client | Diffuse la position chauffeur aux utilisateurs autorisés. |

## 9. Santé applicative

| Route | Description |
| --- | --- |
| `/health` | Healthcheck Nginx. |
| `/api/v1/health/` | Healthcheck backend et base de données. |
