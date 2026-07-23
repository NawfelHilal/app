# SonarQube Community Build

## 1. Objectif du document

FleetPro utilise SonarQube Community Build afin de centraliser l’analyse qualité du backend Django, du service GPS NestJS et de l’application mobile Expo.

SonarQube complète les contrôles CI existants en fournissant :

- une mesure de maintenabilité ;
- une détection de bugs ;
- une analyse des vulnérabilités et hotspots ;
- une mesure de dette technique ;
- un Quality Gate bloquant.

## 2. Périmètre analysé

| Bloc | Sources | Rapport de couverture |
| --- | --- | --- |
| Backend Django | `backend/apps`, `backend/core`, `backend/tests` | `backend/coverage.xml` |
| GPS NestJS | `gps-service/src` | `gps-service/src/coverage/lcov.info` |
| Mobile Expo | `mobile/src` | `mobile/coverage/lcov.info` |

La configuration principale est définie dans :

```txt
sonar-project.properties
```

## 3. Préparation TypeScript

Le job SonarQube exécute `npm ci` dans `gps-service` et `mobile` avant le scan. Cette étape permet à SonarQube de résoudre correctement les dépendances TypeScript et les fichiers étendus par les `tsconfig`, notamment les configurations Expo.

## 4. Configuration GitHub Actions

Variables à créer dans `Settings > Secrets and variables > Actions`.

Secret :

- `SONAR_TOKEN` : token d’analyse généré depuis SonarQube.

Variable :

- `SONAR_HOST_URL` : URL publique de l’instance SonarQube.

Exemple :

```txt
SONAR_HOST_URL=http://51.158.102.141:9000
```

## 5. Quality Gate

Le projet active l’attente du Quality Gate :

```properties
sonar.qualitygate.wait=true
```

Si le Quality Gate échoue, le job `sonarqube` échoue également. Ce comportement garantit qu’une régression qualité ne peut pas être intégrée sans correction ou justification.

## 6. Coût et hébergement

SonarQube Community Build est gratuit et auto-hébergeable. Le coût opérationnel correspond uniquement à l’infrastructure utilisée pour l’exécuter.

Pour FleetPro, l’hébergement peut être réalisé :

- sur l’instance Scaleway existante si les ressources sont suffisantes ;
- sur une instance dédiée si l’analyse ralentit les services applicatifs ;
- localement pour un usage ponctuel hors CI.

## 7. Complémentarité avec la CI

SonarQube ne remplace pas les contrôles spécialisés. La CI conserve :

- `ruff` et `bandit` pour Python ;
- `pip-audit` pour les dépendances backend ;
- `eslint` pour TypeScript ;
- `npm audit` pour GPS et mobile ;
- les tests automatisés avec couverture.

Cette combinaison assure une analyse rapide en CI et une vision consolidée dans SonarQube.
