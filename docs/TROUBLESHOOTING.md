# Guide de dépannage FleetPro

## 1. Objectif du document

Ce document centralise les incidents courants rencontrés lors du développement, de la recette et de la démonstration de FleetPro. Chaque section décrit le symptôme, la cause probable et la procédure de résolution.

## 2. Docker Desktop indisponible

### Symptôme

```txt
Cannot connect to the Docker daemon
```

ou :

```txt
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified
```

### Cause probable

Docker Desktop n’est pas démarré ou le moteur WSL2 associé est bloqué.

### Résolution

1. Ouvrir Docker Desktop.
2. Attendre que le moteur soit entièrement démarré.
3. Relancer la stack :

```powershell
docker compose up --build
```

Si Docker reste bloqué, redémarrer Windows ou relancer WSL :

```powershell
wsl --shutdown
```

## 3. Port local déjà utilisé

### Symptôme

```txt
ports are not available
```

### Cause probable

Un autre processus utilise déjà le port exposé par Docker Compose, par exemple `8081` pour Expo.

### Résolution

Identifier le processus :

```powershell
netstat -ano | findstr :8081
```

Puis arrêter le processus concerné ou modifier le port dans `docker-compose.yml`.

## 4. Expo Go ne se connecte pas

### Symptôme

Expo Go affiche une erreur de connexion ou le QR code ne charge pas l’application.

### Cause probable

Le téléphone ne peut pas joindre `localhost`, car `localhost` désigne le téléphone et non le PC.

### Résolution

Utiliser l’adresse IPv4 Wi-Fi du PC dans les variables Expo :

```env
EXPO_PUBLIC_API_URL=http://192.168.1.20:8090/api/v1
EXPO_PUBLIC_GPS_URL=http://192.168.1.20:8090
REACT_NATIVE_PACKAGER_HOSTNAME=192.168.1.20
```

Puis relancer Expo :

```powershell
cd mobile
npx expo start --lan --clear
```

Si le réseau local bloque la connexion :

```powershell
npx expo start --tunnel --clear
```

## 5. Tester le mobile avec le backend Scaleway

### Contexte

Lorsque le backend, le service GPS, Redis et PostgreSQL sont déjà hébergés sur Scaleway, il n’est pas nécessaire de lancer la stack Docker locale.

### Configuration

Dans `mobile/.env` :

```env
EXPO_PUBLIC_API_URL=http://51.158.102.141/api/v1
EXPO_PUBLIC_GPS_URL=http://51.158.102.141
EXPO_PUBLIC_USE_SIMULATED_PAYMENT=true
EXPO_PUBLIC_ENABLE_DEMO_SIMULATION=true
EXPO_PUBLIC_DEMO_PASSWORD=password123
```

Remplacer l’IP par le domaine ou l’adresse actuelle de l’instance.

### Commande

```powershell
cd mobile
npx expo start --lan --clear
```

## 6. Erreur HTTP 401

### Symptôme

L’application affiche une erreur de connexion ou une réponse `401 Unauthorized`.

### Causes possibles

- identifiant ou mot de passe incorrect ;
- compte démo non créé ;
- token expiré ;
- mobile configuré sur une mauvaise URL API ;
- secret JWT incohérent entre backend et GPS.

### Résolution

Vérifier les comptes démo :

```powershell
docker compose exec backend python manage.py seed_demo
```

Vérifier l’URL API utilisée par le mobile :

```env
EXPO_PUBLIC_API_URL=http://51.158.102.141/api/v1
```

Relancer Expo avec nettoyage du cache :

```powershell
npx expo start --lan --clear
```

## 7. Simulation chauffeur impossible

### Symptôme

Le bouton de simulation chauffeur affiche une erreur.

### Cause probable

Le mode démonstration est désactivé côté backend ou côté mobile.

### Résolution

Vérifier les variables :

```env
ENABLE_DEMO_SIMULATION=true
EXPO_PUBLIC_ENABLE_DEMO_SIMULATION=true
```

Redémarrer le backend et relancer Expo après modification.

## 8. QR code web Expo sans effet

### Symptôme

La touche `w` dans Expo ne lance pas correctement l’application web.

### Cause probable

FleetPro est prioritairement une application mobile. Certaines dépendances natives comme `react-native-maps`, `expo-secure-store` ou Stripe mobile ne sont pas destinées au web sans adaptation.

### Résolution

Tester prioritairement sur smartphone avec Expo Go :

```powershell
npx expo start --lan --clear
```

Pour une expérimentation web uniquement :

```powershell
npx expo install react-dom react-native-web @expo/metro-runtime
npx expo start --web --clear
```

## 9. Carte mobile

FleetPro utilise `react-native-maps` via le composant `MapCanvas` afin de rester compatible avec Expo Go. Mapbox nécessiterait un development build Expo ou une application native générée.

## 10. Vérifications de santé Scaleway

Avant une démonstration, vérifier :

```powershell
Invoke-WebRequest http://51.158.102.141/health
Invoke-WebRequest http://51.158.102.141/api/v1/health/
```

Une réponse `200 OK` confirme que Nginx et le backend sont joignables.
