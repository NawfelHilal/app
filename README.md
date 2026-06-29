# FleetPro

FleetPro est une plateforme VTC ethique cloud-native composee de trois blocs:

- `backend/`: API metier Django REST Framework avec JWT, courses, paiements Stripe et notifications.
- `gps-service/`: satellite NestJS Socket.io pour les positions GPS temps reel stockees dans Redis avec TTL.
- `mobile/`: application Expo React Native TypeScript pour les parcours passager et chauffeur.

## Demarrage local

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Services exposes:

- API Gateway Nginx: `http://localhost:8090`
- API Core: `http://localhost:8090/api/v1`
- WebSocket GPS Socket.io: `http://localhost:8090/socket.io`
- Backend direct: `http://localhost:8000`
- GPS direct: `http://localhost:3001`
- Expo mobile: `http://localhost:8081`

Pour tester sur un telephone avec Expo Go, le plus fiable est d'utiliser l'IP Wi-Fi du PC dans `.env`:

```powershell
ipconfig
```

Remplace ensuite `localhost` par ton IPv4 Wi-Fi, par exemple:

```env
EXPO_PUBLIC_API_URL=http://192.168.1.20:8090/api/v1
EXPO_PUBLIC_GPS_URL=http://192.168.1.20:8090
REACT_NATIVE_PACKAGER_HOSTNAME=192.168.1.20
```

Puis relance:

```powershell
docker compose up --build mobile
```

Alternative hors Docker:

```powershell
cd mobile
npm install
npx expo start --lan
```

## Carte mobile

Le mobile reste compatible Expo Go. La carte utilise `react-native-maps` avec un style sombre proche d'une experience VTC premium.

Mapbox reel necessite un development build, donc il n'est pas active tant que le projet doit tourner uniquement dans Expo Go.

## Commandes utiles

```powershell
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_demo
docker compose exec backend python manage.py createsuperuser
docker compose exec backend pytest
docker compose exec gps-service npm test
```

Comptes demo crees par `seed_demo`:

- Passager: `passenger` / `password123`
- Chauffeur: `driver` / `password123`

## Architecture

Voir [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
Voir aussi [docs/API.md](docs/API.md) pour les endpoints REST et Socket.io.
En cas de probleme Docker, npm ou Expo, voir [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).
