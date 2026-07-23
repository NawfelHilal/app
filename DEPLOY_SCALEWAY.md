# Déploiement Scaleway

## 1. Objectif du document

Ce document décrit la procédure de déploiement de FleetPro sur Scaleway. Il couvre deux scénarios :

- **Instance Scaleway + Docker Compose** : scénario retenu pour le MVP et la démonstration, avec un coût maîtrisé.
- **Kubernetes Kapsule** : scénario cible pour une architecture cloud-native plus industrialisée.

Le scénario Instance + Docker Compose héberge le backend, le service GPS, PostgreSQL, Redis et Nginx sur une même machine virtuelle. L’application mobile est construite séparément via Expo/EAS et consomme l’API exposée par Scaleway.

## 2. Architecture de production MVP

```txt
Mobile Expo / EAS
  | HTTP / WebSocket
  v
Instance Scaleway
  |
  | Nginx
  |-- Backend Django
  |-- GPS NestJS
  |-- PostgreSQL
  |-- Redis
```

Cette architecture permet de valider le fonctionnement bout-en-bout sans souscrire immédiatement à des services managés payants.

## 3. Prérequis

- Instance Scaleway Linux avec IP publique.
- Docker et Docker Compose installés sur l’instance.
- Container Registry Scaleway créé.
- Images `fleetpro-backend` et `fleetpro-gps-service` poussées dans le registry.
- Fichier `.env.prod` présent sur le serveur.
- Groupe de sécurité Scaleway autorisant au minimum les ports `22` et `80`.

## 4. Variables de production

Créer le fichier à partir du modèle :

```powershell
Copy-Item .env.prod.example .env.prod
```

Variables minimales à définir :

- `DJANGO_SECRET_KEY`
- `JWT_SIGNING_KEY`
- `GPS_JWT_SECRET`
- `POSTGRES_PASSWORD`
- `DJANGO_ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `SCALEWAY_REGISTRY`
- `IMAGE_TAG`

`JWT_SIGNING_KEY` et `GPS_JWT_SECRET` doivent avoir la même valeur et contenir au moins 32 caractères.

En production réelle, `ENABLE_DEMO_SIMULATION` doit être positionné à `false`. Pour une démonstration encadrée, il peut être temporairement activé.

## 5. Build et push des images

Connexion au Container Registry Scaleway :

```powershell
$env:SCW_SECRET_KEY="secret-key-scaleway"
$env:SCALEWAY_REGISTRY="rg.fr-par.scw.cloud/fleet-pro"
$env:IMAGE_TAG=(git rev-parse --short HEAD)
$env:SCW_SECRET_KEY | docker login $env:SCALEWAY_REGISTRY -u nologin --password-stdin
```

Build :

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml build
```

Push :

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml push
```

## 6. Déploiement sur l’instance

Connexion SSH :

```powershell
ssh root@51.158.102.141
```

Placement recommandé du projet :

```bash
mkdir -p /opt/fleetpro
cd /opt/fleetpro
```

Connexion Docker au registry depuis le serveur :

```bash
echo "$SCW_SECRET_KEY" | docker login rg.fr-par.scw.cloud/fleet-pro -u nologin --password-stdin
```

Récupération des images :

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml pull
```

Démarrage :

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d
```

Suivi des logs :

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f
```

## 7. Migrations et données de démonstration

Les migrations sont exécutées au démarrage du conteneur backend. Elles peuvent aussi être relancées manuellement :

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec backend python manage.py migrate
```

Pour créer ou réinitialiser les comptes de démonstration :

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec backend python manage.py seed_demo
```

Comptes démo :

- passager : `passenger`
- chauffeur : `driver`

Le mot de passe doit rester réservé à un environnement de démonstration.

## 8. Vérifications de santé

Depuis le serveur :

```bash
curl http://127.0.0.1/health
curl http://127.0.0.1/api/v1/health/
```

Depuis le poste local :

```powershell
Invoke-WebRequest http://51.158.102.141/health
Invoke-WebRequest http://51.158.102.141/api/v1/health/
```

Réponses attendues :

- `/health` : `ok`
- `/api/v1/health/` : statut applicatif `ok`

## 9. Mobile Expo / EAS

Le service `mobile` n’est pas déployé comme un conteneur serveur. Il est testé localement avec Expo Go ou construit via EAS Build.

Variables GitHub Actions pour EAS :

- `EXPO_PUBLIC_API_URL`
- `EXPO_PUBLIC_GPS_URL`
- `EXPO_PUBLIC_USE_SIMULATED_PAYMENT`
- `EXPO_PUBLIC_ENABLE_DEMO_SIMULATION`
- `EXPO_PUBLIC_DEMO_PASSWORD`

Secrets GitHub Actions :

- `EXPO_TOKEN`
- `EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY`

Exemple de configuration pour un mobile pointant vers Scaleway :

```env
EXPO_PUBLIC_API_URL=http://51.158.102.141/api/v1
EXPO_PUBLIC_GPS_URL=http://51.158.102.141
EXPO_PUBLIC_USE_SIMULATED_PAYMENT=true
EXPO_PUBLIC_ENABLE_DEMO_SIMULATION=true
```

## 10. Déploiement automatisé GitHub Actions

Le workflow `.github/workflows/deploy-scaleway.yml` peut automatiser :

1. le build des images ;
2. le push vers Scaleway Container Registry ;
3. la connexion SSH à l’instance ;
4. le `docker compose pull` ;
5. le redémarrage de la stack ;
6. l’exécution des migrations ;
7. l’exécution éventuelle du seed de démonstration.

La procédure détaillée et les secrets nécessaires sont documentés dans `docs/DEPLOY_SCALEWAY_CI.md`.

## 11. Option Kubernetes Kapsule

Kubernetes Kapsule constitue une cible d’industrialisation. Cette option permet :

- la séparation des workloads ;
- le scaling horizontal ;
- l’utilisation d’Ingress et de certificats TLS ;
- une meilleure stratégie de rolling update.

Les manifests sont placés dans `infra/k8s/scaleway`.

Déploiement :

```bash
kubectl apply -k infra/k8s/scaleway
```

Migrations :

```bash
kubectl delete job core-api-migrate -n fleetpro --ignore-not-found
kubectl apply -k infra/k8s/scaleway/migrate
kubectl wait --for=condition=complete job/core-api-migrate -n fleetpro --timeout=180s
```

Suivi :

```bash
kubectl rollout status deployment/core-api -n fleetpro
kubectl rollout status deployment/gps-service -n fleetpro
kubectl get ingress -n fleetpro
```

## 12. Sauvegarde PostgreSQL

Sauvegarde manuelle :

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec postgres pg_dump -U fleetpro fleetpro > fleetpro_backup.sql
```

La sauvegarde doit être externalisée avant toute opération risquée sur les volumes Docker.

## 13. Checklist avant démonstration

- L’instance Scaleway répond en SSH.
- Le groupe de sécurité autorise le trafic HTTP.
- Les images backend et GPS sont disponibles dans le registry.
- `.env.prod` contient des secrets longs et cohérents.
- `/health` répond en `200`.
- `/api/v1/health/` répond en `200`.
- Le mobile pointe vers l’URL Scaleway.
- Le mode démonstration est activé uniquement si nécessaire.
- Les logs backend et GPS ne montrent pas d’erreurs critiques.
