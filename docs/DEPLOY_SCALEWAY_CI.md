# Déploiement automatique Scaleway

## 1. Objectif du document

Ce document décrit le déploiement automatique de FleetPro sur une instance Scaleway à partir de GitHub Actions.

Le workflow concerné est :

```txt
.github/workflows/deploy-scaleway.yml
```

Il peut être déclenché automatiquement après validation de la CI ou manuellement avec `workflow_dispatch`.

## 2. Responsabilités de la pipeline

La pipeline de déploiement :

1. récupère le commit validé ;
2. se connecte au Scaleway Container Registry ;
3. construit l’image Docker du backend ;
4. construit l’image Docker du service GPS ;
5. pousse les images avec le SHA du commit et le tag `latest` ;
6. copie les fichiers de déploiement nécessaires sur l’instance ;
7. met à jour `IMAGE_TAG` dans `/opt/fleetpro/.env.prod` ;
8. exécute `docker compose pull` ;
9. redémarre la stack avec `docker compose up -d --no-build` ;
10. exécute les migrations Django ;
11. exécute le seed de démonstration si prévu par le workflow.

Le fichier `.env.prod` du serveur n’est pas écrasé par la CI afin de préserver les secrets de production.

## 3. Secrets GitHub Actions

Les secrets suivants doivent être créés dans `Settings > Secrets and variables > Actions > Secrets`.

| Secret | Description |
| --- | --- |
| `SCW_REGISTRY_TOKEN` | Clé secrète Scaleway autorisée à tirer et pousser les images |
| `SCALEWAY_SSH_HOST` | Adresse IP ou domaine de l’instance |
| `SCALEWAY_SSH_USER` | Utilisateur SSH de déploiement |
| `SCALEWAY_SSH_PRIVATE_KEY` | Clé privée SSH sans passphrase pour l’automatisation |

## 4. Prérequis serveur

L’instance Scaleway doit contenir :

```bash
/opt/fleetpro/.env.prod
```

Elle doit également disposer de :

- Docker ;
- Docker Compose ;
- un accès au Container Registry Scaleway ;
- les fichiers `docker-compose.prod.yml` et `infra/nginx/nginx.prod.conf`.

## 5. Sécurité réseau

Le groupe de sécurité Scaleway doit autoriser :

- TCP `22` pour le déploiement SSH ;
- TCP `80` pour l’API HTTP ;
- TCP `443` si HTTPS est activé.

Pour une production durcie, l’accès SSH doit être restreint par adresse IP, VPN ou runner GitHub auto-hébergé.

## 6. Vérification post-déploiement

Depuis un poste local :

```powershell
Invoke-WebRequest http://51.158.102.141/health
Invoke-WebRequest http://51.158.102.141/api/v1/health/
```

Depuis le serveur :

```bash
cd /opt/fleetpro
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
docker compose --env-file .env.prod -f docker-compose.prod.yml logs --tail=100 backend
docker compose --env-file .env.prod -f docker-compose.prod.yml logs --tail=100 gps-service
```

## 7. Rollback

Le rollback consiste à revenir à un tag d’image précédent.

```bash
cd /opt/fleetpro
sed -i 's/^IMAGE_TAG=.*/IMAGE_TAG=<ancien_sha>/' .env.prod
docker compose --env-file .env.prod -f docker-compose.prod.yml pull backend gps-service
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-build
```

Après rollback, vérifier les endpoints de santé et les logs applicatifs.

## 8. Limites connues

- Le déploiement SSH nécessite une clé privée non protégée par passphrase côté GitHub Actions.
- Les secrets de production doivent rester exclusivement sur l’instance ou dans GitHub Secrets.
- La disponibilité dépend de l’instance Scaleway et du bon état du moteur Docker.

Ces limites sont acceptables pour le MVP. Une production plus avancée peut migrer vers Kubernetes Kapsule, un Load Balancer TLS et des services managés PostgreSQL/Redis.
