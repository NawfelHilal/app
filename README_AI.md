# FleetPro — Instructions pour l’éditeur de code IA

## 1. Contexte du projet

FleetPro est une plateforme VTC éthique cloud-native.

L’objectif est de créer une application VTC complète avec :
- une commission fixe à 15 %
- une application mobile passager/chauffeur
- un backend métier robuste
- un service GPS temps réel
- un système de paiement Stripe en mode test
- des notifications push
- une architecture propre, maintenable et justifiable dans un dossier de fin d’étude Master

Le projet doit être développé avec une forte attention à :
- la qualité du code
- l’architecture logicielle
- les design patterns
- la sécurité
- les tests
- la maintenabilité
- la documentation
- la conformité avec une grille d’évaluation Bloc 2

---

## 2. Stack technique imposée

### Backend Core

- Python 3.12
- Django 5.x
- Django REST Framework
- djangorestframework-simplejwt
- PostgreSQL 16
- Stripe API en mode test
- Firebase FCM pour les notifications

### Backend Satellite GPS

- Node.js 24 LTS
- NestJS 11
- WebSocket / Socket.io
- Redis 7 pour stockage GPS temps réel
- TTL Redis pour expiration automatique des positions

### Mobile

- React Native
- Expo SDK 52+
- TypeScript
- React Navigation
- Zustand pour le state management
- Axios pour les appels API REST
- Socket.io-client pour le temps réel
- react-native-maps
- Stripe React Native SDK

### Infrastructure

- Docker Compose pour le développement local
- Nginx comme API Gateway / reverse proxy
- Kubernetes pour la production future
- GitHub Actions pour CI/CD

---

## 3. Architecture à respecter

Le projet doit suivre une architecture hybride :

```txt
Mobile Expo
   |
   | HTTPS / WSS
   v
Nginx API Gateway
   |
   | REST
   v
Core Django REST Framework
   |
   | SQL
   v
PostgreSQL

En parallèle :

Mobile Expo
   |
   | WebSocket
   v
Satellite NestJS GPS
   |
   | Redis GEO + TTL
   v
Redis GPS