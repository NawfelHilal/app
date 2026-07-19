# Déploiement Scaleway

Ce guide propose deux chemins de production pour FleetPro sur Scaleway :

- **Instance + Docker Compose** : recommandé pour le MVP/rendu, simple à opérer.
- **Kubernetes Kapsule** : recommandé si tu veux montrer une architecture cloud native plus avancée.

Dans les deux cas, utilise de préférence :

- **Container Registry** Scaleway pour les images `backend` et `gps-service`.
- **PostgreSQL + Redis dans Docker** pour le MVP économique sur Instance.
- **Managed PostgreSQL + Managed Redis** seulement si tu veux une production plus robuste et payante.
- **Load Balancer/TLS** Scaleway ou Ingress Kubernetes pour exposer HTTPS.

## 1. Préparer les variables

Copie l’exemple de production :

```powershell
Copy-Item .env.prod.example .env.prod
```

Puis remplace au minimum :

- `DJANGO_SECRET_KEY`
- `JWT_SIGNING_KEY`
- `GPS_JWT_SECRET`
- `POSTGRES_PASSWORD`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_SECURE_SSL_REDIRECT` : `false` sans HTTPS, `true` dès que le Load Balancer/TLS est prêt.
- `CORS_ALLOWED_ORIGINS`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`

Important : `JWT_SIGNING_KEY` et `GPS_JWT_SECRET` doivent avoir la même valeur, avec au moins 32 caractères.

## 2. Builder et pousser les images

Crée un namespace Scaleway Container Registry, par exemple `fleet-pro`.

Connexion au registry :

```powershell
$env:SCW_SECRET_KEY="ton_secret_key_scaleway"
$env:SCALEWAY_REGISTRY="rg.fr-par.scw.cloud/fleet-pro"
$env:IMAGE_TAG=(git rev-parse --short HEAD)
$env:SCW_SECRET_KEY | docker login $env:SCALEWAY_REGISTRY -u nologin --password-stdin
```

Build local :

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml build
```

Push :

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml push
```

## 3. Déploiement simple économique : Instance + Docker Compose

Sur une Instance Scaleway Ubuntu :

1. Installe Docker et Docker Compose.
2. Copie le projet ou clone ton dépôt.
3. Copie `.env.prod` sur le serveur.
4. Connecte Docker au registry Scaleway.
5. Lance la stack avec PostgreSQL et Redis inclus dans Docker.

Commandes :

```bash
export SCALEWAY_REGISTRY="rg.fr-par.scw.cloud/fleet-pro"
export IMAGE_TAG="latest"
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml logs -f
```

Si tu utilises uniquement `.env.prod` pour `SCALEWAY_REGISTRY` et `IMAGE_TAG`, lance plutôt :

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml pull
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d
docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f
```

Cette stack crée deux volumes persistants :

- `postgres_prod_data` pour PostgreSQL.
- `redis_prod_data` pour Redis.

Tu ne paies donc pas Managed PostgreSQL/Redis. Tu paies seulement l’Instance Scaleway et son disque.

Sauvegarde PostgreSQL manuelle :

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec postgres pg_dump -U fleetpro fleetpro > fleetpro_backup.sql
```

Exposition recommandée :

- Mets un Load Balancer Scaleway devant l’Instance.
- Termine TLS/HTTPS sur le Load Balancer.
- Redirige vers le port `80` de l’Instance.
- Configure `DJANGO_ALLOWED_HOSTS` avec ton domaine API.
- Passe `DJANGO_SECURE_SSL_REDIRECT=true` quand HTTPS fonctionne.

Endpoints à vérifier :

```bash
curl https://api.ton-domaine.com/health
curl https://api.ton-domaine.com/api/v1/health/
```

## 4. Déploiement Kubernetes : Kapsule

### 4.1 Préparer le cluster

Récupère le kubeconfig du cluster Kapsule :

```bash
scw k8s kubeconfig install <cluster-id>
kubectl get nodes
```

Installe ensuite un Ingress Controller NGINX et `cert-manager` si ton cluster ne les a pas déjà.

### 4.2 Adapter les manifests

Dans `infra/k8s/scaleway/kustomization.yaml`, remplace :

```yaml
newName: rg.fr-par.scw.cloud/your-namespace/fleetpro-backend
newName: rg.fr-par.scw.cloud/your-namespace/fleetpro-gps-service
newTag: latest
```

Fais le même remplacement d’image backend dans `infra/k8s/scaleway/migrate/kustomization.yaml`.

Dans `infra/k8s/scaleway/configmap.yaml`, remplace :

- `DJANGO_ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `POSTGRES_HOST`

Dans `infra/k8s/scaleway/ingress.yaml`, remplace :

- `api.fleetpro.example.com`
- `fleetpro-api-tls` si tu veux un autre nom de secret TLS

### 4.3 Créer les secrets Kubernetes

Namespace :

```bash
kubectl apply -f infra/k8s/scaleway/namespace.yaml
```

Secret pour tirer les images privées Scaleway :

```bash
kubectl create secret docker-registry scaleway-registry \
  --namespace fleetpro \
  --docker-server=rg.fr-par.scw.cloud/fleet-pro \
  --docker-username=nologin \
  --docker-password="$SCW_SECRET_KEY"
```

Secret applicatif :

```bash
kubectl create secret generic fleetpro-secrets \
  --namespace fleetpro \
  --from-literal=DJANGO_SECRET_KEY="change-me" \
  --from-literal=POSTGRES_PASSWORD="change-me" \
  --from-literal=REDIS_URL="redis://:password@redis-endpoint:6379/0" \
  --from-literal=JWT_SIGNING_KEY="same-32-plus-character-secret" \
  --from-literal=GPS_JWT_SECRET="same-32-plus-character-secret" \
  --from-literal=STRIPE_SECRET_KEY="sk_live_or_test_change_me" \
  --from-literal=STRIPE_WEBHOOK_SECRET="whsec_change_me"
```

Le fichier `infra/k8s/scaleway/secret.example.yaml` sert uniquement de modèle. Ne le déploie pas tel quel en production.

### 4.4 Déployer l’application

Déployer les services :

```bash
kubectl apply -k infra/k8s/scaleway
```

Lancer les migrations :

```bash
kubectl delete job core-api-migrate -n fleetpro --ignore-not-found
kubectl apply -k infra/k8s/scaleway/migrate
kubectl wait --for=condition=complete job/core-api-migrate -n fleetpro --timeout=180s
```

Suivre le déploiement :

```bash
kubectl rollout status deployment/core-api -n fleetpro
kubectl rollout status deployment/gps-service -n fleetpro
kubectl get ingress -n fleetpro
kubectl logs -f deployment/core-api -n fleetpro
```

## 5. Mobile Expo / EAS

Le service `mobile` ne se déploie pas comme conteneur production.

Un workflow GitHub Actions est disponible dans `.github/workflows/eas-build.yml`.
Il lance un build EAS :

- manuellement avec `workflow_dispatch`;
- automatiquement sur un tag Git `mobile-v*`, par exemple `mobile-v1.0.0`.

Pour une build mobile réelle :

- `EXPO_PUBLIC_API_URL=https://api.ton-domaine.com/api/v1`
- `EXPO_PUBLIC_GPS_URL=https://api.ton-domaine.com`
- `EXPO_PUBLIC_USE_SIMULATED_PAYMENT=false`
- `EXPO_PUBLIC_ENABLE_DEMO_SIMULATION=false`

À créer dans GitHub :

Secrets :

- `EXPO_TOKEN`
- `EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY`

Variables :

- `EXPO_PUBLIC_API_URL`
- `EXPO_PUBLIC_GPS_URL`
- `EXPO_PUBLIC_USE_SIMULATED_PAYMENT`
- `EXPO_PUBLIC_ENABLE_DEMO_SIMULATION`

Créer un token Expo :

```bash
eas whoami
eas token:create
```

Lancer un build depuis Git :

```bash
git tag mobile-v1.0.0
git push origin mobile-v1.0.0
```

## 6. Checklist avant démo

- `/api/v1/health/` répond en `200`.
- `/socket.io/` est routé vers `gps-service`.
- Les logs backend ne montrent plus d’avertissement de clé JWT trop courte.
- Le paiement Stripe est en mode test ou live selon ta démo.
- Le matching GPS utilise Redis, soit Docker Compose, soit Scaleway Managed Redis.
- `ENABLE_DEMO_SIMULATION=false` en vraie prod, `true` seulement pour une démo mono-device.
