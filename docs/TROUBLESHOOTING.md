# Depannage FleetPro

## Expo ne montre pas le QR code

Depuis `mobile/`, installe d'abord les dependances du projet:

```powershell
npm install
npm run start:lan
```

Evite `npx expo start` tant que `node_modules` n'est pas installe: `npx` peut tenter de telecharger une autre version d'Expo que celle du projet.

## npm affiche `ECOMPROMISED Lock compromised`

Ce blocage vient generalement d'un cache npm ou d'une installation interrompue. Nettoie l'installation locale puis reinstalle:

```powershell
cd mobile
npm cache verify
npm cache clean --force
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue
npm install --no-audit
npm run start:lan
```

## Passer ou reparer Expo SDK 54

Le mobile FleetPro cible Expo SDK 54. Nettoie l'installation locale avant de relancer Expo:

```powershell
cd mobile
Get-Process node -ErrorAction SilentlyContinue | Stop-Process
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue
npm install --no-audit
npx expo install --fix
npm run start:lan -- --clear
```

SDK 54 cible React Native `0.81` et React `19.1.0`.

Si le telephone n'est pas sur le meme Wi-Fi que le PC:

```powershell
npm run start:tunnel
```

## API inaccessible depuis le telephone

Dans `.env`, remplace `localhost` par l'IPv4 Wi-Fi du PC:

```env
EXPO_PUBLIC_API_URL=http://192.168.1.20:8090/api/v1
EXPO_PUBLIC_GPS_URL=http://192.168.1.20:8090
REACT_NATIVE_PACKAGER_HOSTNAME=192.168.1.20
```

Puis redemarre Expo.

## Carte dans Expo Go

Expo Go ne charge pas `@rnmapbox/maps`, car Mapbox ajoute du code natif. FleetPro utilise donc `react-native-maps` pour rester testable dans Expo Go.

Si tu veux Mapbox reel plus tard, il faudra passer sur un development build avec `npx expo run:android` ou EAS Build.
