# Qualité de code FleetPro

## 1. Objectif du document

Ce document décrit la stratégie de qualité logicielle appliquée à FleetPro. Elle couvre l’analyse statique, les tests automatisés, la couverture, les audits de sécurité et l’analyse SonarQube.

L’objectif est de garantir que chaque évolution du projet reste maintenable, testée et vérifiable dans le cadre du Bloc 2.

## 2. Outils retenus

| Périmètre | Outil | Objectif |
| --- | --- | --- |
| Backend Django | `ruff` | Analyse statique Python et cohérence du style |
| Backend Django | `bandit` | Détection de risques de sécurité Python |
| Backend Django | `pip-audit` | Audit des vulnérabilités connues dans les dépendances |
| Backend Django | `coverage` | Mesure de couverture des tests |
| GPS NestJS | `eslint` | Analyse statique TypeScript |
| GPS NestJS | `jest` | Tests unitaires et couverture |
| Mobile Expo | `eslint` | Analyse statique TypeScript/TSX |
| Mobile Expo | `jest-expo` | Tests unitaires mobile et couverture |
| Projet complet | SonarQube Community Build | Centralisation qualité, dette technique, bugs et Quality Gate |

## 3. Commandes locales

### Backend

```powershell
cd backend
..\.venv\Scripts\python.exe -m ruff check .
..\.venv\Scripts\python.exe -m bandit -r apps -x "*/migrations/*" --severity-level medium
..\.venv\Scripts\python.exe -m pip_audit -r requirements.txt --strict
..\.venv\Scripts\python.exe -m coverage run manage.py test tests
..\.venv\Scripts\python.exe -m coverage report --fail-under=90
```

### GPS service

```powershell
cd gps-service
npm ci
npm run lint
npm run typecheck
npm run test:coverage
npm run security:audit
```

### Mobile

```powershell
cd mobile
npm ci
npm run lint
npm run typecheck
npm run test:coverage
npm run security:audit
```

## 4. Contrôles en CI

Le workflow `.github/workflows/ci.yml` bloque l’intégration si :

- le lint backend échoue ;
- l’audit Bandit détecte un risque de niveau significatif ;
- `pip-audit` détecte une vulnérabilité connue dans les dépendances backend ;
- `npm audit` détecte une vulnérabilité runtime de niveau `high` ou `critical` ;
- les tests backend, GPS ou mobile échouent ;
- la couverture backend descend sous le seuil défini ;
- les seuils Jest GPS ou mobile ne sont pas respectés ;
- le Quality Gate SonarQube échoue.

## 5. Justification Bloc 2

Cette stratégie répond aux exigences de maintenabilité et d’industrialisation :

- les erreurs sont détectées avant déploiement ;
- les vulnérabilités connues sont auditées automatiquement ;
- la qualité est mesurée de manière répétable ;
- les métriques sont centralisées dans SonarQube ;
- le dépôt contient les commandes permettant de reproduire les contrôles localement.
