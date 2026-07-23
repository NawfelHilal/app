# Accessibilité FleetPro

## 1. Objectif du document

Ce document présente la démarche d’accessibilité appliquée à l’application mobile FleetPro. Il complète le dossier Bloc 2 en reliant les exigences RGAA/WCAG aux choix d’interface, aux preuves code et à la recette manuelle.

## 2. Référentiel retenu

FleetPro s’appuie sur :

- le **RGAA** comme référentiel principal dans un contexte français ;
- les principes **WCAG** pour structurer l’analyse : perceptible, utilisable, compréhensible et robuste.

L’objectif n’est pas de déclarer une conformité RGAA complète, mais de démontrer une démarche structurée sur les parcours critiques du MVP.

## 3. Périmètre audité

Le périmètre couvre :

- connexion passager et chauffeur ;
- inscription passager ;
- inscription chauffeur avec informations professionnelles ;
- sélection FleetHer, Fleet PMR, FleetLuxe et Fleet Standard ;
- passage en ligne du chauffeur ;
- simulation d’une demande client proche ;
- suivi de course ;
- affichage de la carte et des statuts.

## 4. Mesures implémentées

| Exigence | Mesure FleetPro | Preuve code |
| --- | --- | --- |
| Identification des actions | Les boutons principaux exposent un rôle, un libellé et une indication d’usage. | `mobile/src/components/AppButton.tsx` |
| Navigation par onglets | Les onglets annoncent leur libellé et leur état sélectionné. | `mobile/src/components/BottomTabs.tsx` |
| Formulaires compréhensibles | Les champs de connexion et d’inscription disposent de libellés explicites pour lecteur d’écran. | `mobile/src/screens/LoginScreen.tsx`, `mobile/src/screens/RegisterScreen.tsx` |
| Lisibilité des champs | Les placeholders utilisent une couleur dédiée plus contrastée. | `mobile/src/theme/colors.ts` |
| États interactifs | Les boutons désactivés, choix sélectionnés et switchs exposent leur état. | `mobile/src/screens/RegisterScreen.tsx`, `mobile/src/screens/DriverShellScreen.tsx` |
| Alternatives visuelles | La carte fournit une alternative textuelle décrivant le trajet et le statut. | `mobile/src/components/MapCanvas.tsx` |
| Parcours FleetHer | Le passager peut choisir FleetHer et l’éligibilité est contrôlée côté backend. | `mobile/src/data/places.ts`, `backend/apps/rides/eligibility.py` |
| Parcours Fleet PMR | Le passager peut choisir Fleet PMR et seuls les chauffeurs avec véhicule adapté sont éligibles. | `mobile/src/data/places.ts`, `backend/apps/rides/eligibility.py` |
| Parcours FleetLuxe | Le passager peut choisir FleetLuxe comme service premium. | `mobile/src/data/places.ts`, `backend/apps/rides/eligibility.py` |
| Messages d’erreur | Les erreurs de connexion, paiement, course et simulation sont affichées via alertes natives. | `mobile/src/screens/LoginScreen.tsx`, `mobile/src/screens/ActiveRideScreen.tsx` |

## 5. Recette accessibilité

| Scénario | Critère d’acceptation | Statut |
| --- | --- | --- |
| Connexion VoiceOver/TalkBack | Les champs identifiant/mot de passe et les boutons de démo sont annoncés clairement. | PASS attendu |
| Inscription chauffeur | Les informations professionnelles, le genre et l’adaptation PMR sont navigables sans ambiguïté. | PASS attendu |
| Demande de course | Les destinations, types de service, prix et états sélectionnés sont compréhensibles. | PASS attendu |
| Simulation chauffeur | Le switch de disponibilité, le bouton de simulation et l’acceptation de course sont identifiables. | PASS attendu |
| Suivi de course | Le statut, le trajet, le paiement et les actions restent compréhensibles. | PASS attendu |
| Police système augmentée | Les écrans restent utilisables avec une taille de police agrandie. | À vérifier sur appareil |
| Contraste visuel | Les champs et composants principaux restent lisibles. | PASS attendu |

## 6. Captures recommandées pour le dossier

Les captures suivantes permettent de matérialiser la preuve d’exécution :

- lecteur d’écran sur l’écran de connexion ;
- formulaire chauffeur avec informations professionnelles ;
- véhicule PMR activé ;
- sélection FleetHer/Fleet PMR/FleetLuxe côté passager ;
- course proposée au chauffeur ;
- suivi de course avec carte et statut ;
- champ avec placeholder lisible après correction du contraste.

## 7. Limites assumées

- Un audit RGAA complet nécessite une campagne manuelle détaillée sur plusieurs appareils iOS et Android.
- Les cartes interactives restent complexes à rendre totalement accessibles ; FleetPro fournit une alternative textuelle au niveau du composant.
- Les notifications push natives doivent être testées dans un development build Expo, et non uniquement dans Expo Go.

## 8. Conclusion

FleetPro intègre l’accessibilité dans la conception des parcours principaux et dans les règles métier inclusives. La démarche est documentée, vérifiable dans le code et complétée par une recette manuelle destinée au dossier Bloc 2.
