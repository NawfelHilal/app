from __future__ import annotations

import html
import zipfile
from datetime import datetime, timezone
from pathlib import Path


OUT = Path("docs/FleetPro_Dossier_Bloc2.docx")


NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def run_xml(text: str, bold: bool = False, italic: bool = False, size: int | None = None, color: str | None = None) -> str:
    props = []
    props.append('<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>')
    if bold:
        props.append("<w:b/>")
    if italic:
        props.append("<w:i/>")
    if color:
        props.append(f'<w:color w:val="{color}"/>')
    if size:
        props.append(f'<w:sz w:val="{size * 2}"/><w:szCs w:val="{size * 2}"/>')
    prop_xml = f"<w:rPr>{''.join(props)}</w:rPr>"
    return f'<w:r>{prop_xml}<w:t xml:space="preserve">{esc(text)}</w:t></w:r>'


def para(
    text: str = "",
    style: str | None = None,
    align: str | None = None,
    bold: bool = False,
    italic: bool = False,
    size: int | None = None,
    color: str | None = None,
    before: int | None = None,
    after: int | None = None,
    keep_next: bool = False,
    page_break_before: bool = False,
    num_id: int | None = None,
    ilvl: int = 0,
) -> str:
    ppr = []
    if style:
        ppr.append(f'<w:pStyle w:val="{style}"/>')
    if align:
        ppr.append(f'<w:jc w:val="{align}"/>')
    if before is not None or after is not None:
        attrs = []
        if before is not None:
            attrs.append(f'w:before="{before * 20}"')
        if after is not None:
            attrs.append(f'w:after="{after * 20}"')
        attrs.append('w:line="280"')
        attrs.append('w:lineRule="auto"')
        ppr.append(f"<w:spacing {' '.join(attrs)}/>")
    if keep_next:
        ppr.append("<w:keepNext/>")
    if page_break_before:
        ppr.append("<w:pageBreakBefore/>")
    if num_id is not None:
        ppr.append(
            f"<w:numPr><w:ilvl w:val=\"{ilvl}\"/><w:numId w:val=\"{num_id}\"/></w:numPr>"
        )
    ppr_xml = f"<w:pPr>{''.join(ppr)}</w:pPr>" if ppr else ""
    return f"<w:p>{ppr_xml}{run_xml(text, bold=bold, italic=italic, size=size, color=color)}</w:p>"


def page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def heading(level: int, text: str, page: bool = False) -> str:
    style = {1: "Heading1", 2: "Heading2", 3: "Heading3"}[level]
    return para(text, style=style, page_break_before=page, keep_next=True)


def bullet(text: str) -> str:
    return para(text, num_id=1, after=4)


def numbered(text: str) -> str:
    return para(text, num_id=2, after=4)


def cell(content: str, width: int, fill: str | None = None, bold: bool = False, center: bool = False) -> str:
    shading = f'<w:shd w:fill="{fill}"/>' if fill else ""
    align = '<w:vAlign w:val="center"/>'
    p_align = "center" if center else None
    paragraphs = []
    for line in str(content).split("\n"):
        paragraphs.append(para(line, align=p_align, bold=bold, size=10, after=0))
    return (
        "<w:tc>"
        f'<w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>{shading}{align}</w:tcPr>'
        f"{''.join(paragraphs)}"
        "</w:tc>"
    )


def table(headers: list[str], rows: list[list[str]], widths: list[int]) -> str:
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    borders = (
        '<w:tblBorders><w:top w:val="single" w:sz="4" w:color="B8C2CC"/>'
        '<w:left w:val="single" w:sz="4" w:color="B8C2CC"/>'
        '<w:bottom w:val="single" w:sz="4" w:color="B8C2CC"/>'
        '<w:right w:val="single" w:sz="4" w:color="B8C2CC"/>'
        '<w:insideH w:val="single" w:sz="4" w:color="D7DBE2"/>'
        '<w:insideV w:val="single" w:sz="4" w:color="D7DBE2"/></w:tblBorders>'
    )
    margins = (
        '<w:tblCellMar><w:top w:w="80" w:type="dxa"/><w:left w:w="120" w:type="dxa"/>'
        '<w:bottom w:w="80" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tblCellMar>'
    )
    tbl_pr = (
        '<w:tblPr><w:tblW w:w="9360" w:type="dxa"/><w:tblInd w:w="120" w:type="dxa"/>'
        '<w:tblLayout w:type="fixed"/>'
        f"{borders}{margins}</w:tblPr>"
    )
    header_xml = "<w:tr><w:trPr><w:tblHeader/></w:trPr>" + "".join(
        cell(h, widths[i], fill="F2F4F7", bold=True, center=i == 0) for i, h in enumerate(headers)
    ) + "</w:tr>"
    row_xml = []
    for row in rows:
        row_xml.append("<w:tr>" + "".join(cell(row[i], widths[i], center=(len(row[i]) <= 8)) for i in range(len(widths))) + "</w:tr>")
    return f"<w:tbl>{tbl_pr}<w:tblGrid>{grid}</w:tblGrid>{header_xml}{''.join(row_xml)}</w:tbl>"


def callout(title: str, text: str) -> str:
    return table([title], [[text]], [9360])


def section(title: str, paragraphs: list[str], page: bool = True) -> list[str]:
    xml = [heading(1, title, page=page)]
    for p in paragraphs:
        xml.append(para(p))
    return xml


def metadata_page() -> list[str]:
    return [
        para("FleetPro", align="center", bold=True, size=30, color="0B2545", before=90, after=8),
        para("Dossier Bloc 2 - Concevoir et développer des applications logicielles", align="center", size=15, color="1F4D78", after=28),
        para("Master Expert en développement logiciel", align="center", bold=True, size=12, after=42),
        table(
            ["Champ", "Valeur"],
            [
                ["Candidat", "Nawfel Hilal"],
                ["Projet", "FleetPro - plateforme VTC éthique cloud-native"],
                ["Période", "Janvier 2026 - juillet 2026"],
                ["Stack", "Django REST Framework, NestJS, Expo React Native, PostgreSQL, Redis, Docker, Kubernetes, GitHub Actions, EAS"],
                ["Objectif Bloc 2", "Démontrer la conception, le développement, le test, la sécurisation, le déploiement et la documentation d'une application logicielle complète."],
            ],
            [1900, 7460],
        ),
        para("Version du dossier : 1.0 - 20 juillet 2026", align="center", italic=True, color="555555", before=24),
    ]


def build_content() -> list[str]:
    parts: list[str] = []
    parts.extend(metadata_page())
    parts.append(page_break())

    parts.append(heading(1, "Sommaire", page=False))
    for item in [
        "1. Introduction et contexte du projet",
        "2. Environnements de développement, test et déploiement",
        "3. Protocole d'intégration continue",
        "4. Critères qualité et performance",
        "5. Architecture logicielle structurée",
        "6. Prototype fonctionnel",
        "7. Frameworks, paradigmes et design patterns",
        "8. Harnais de tests unitaires",
        "9. Sécurité et accessibilité",
        "10. Historique des versions et déploiement progressif",
        "11. Cahier de recettes",
        "12. Plan de correction des bugs",
        "13. Documentation d'exploitation",
        "14. Conclusion et annexes",
    ]:
        parts.append(para(item, style="BodyText", after=5))
    parts.append(callout("Note de lecture", "Le dossier est structuré pour répondre directement aux compétences de la grille Bloc 2. Les chemins de fichiers cités correspondent au dépôt FleetPro et peuvent être utilisés comme preuves pendant la soutenance."))

    parts.extend(section("1. Introduction et contexte du projet", [
        "FleetPro est une plateforme VTC éthique cloud-native. Le projet répond à un problème métier simple : proposer une alternative aux plateformes existantes avec une commission fixe à 15 %, un parcours passager/chauffeur lisible et une architecture technique démontrable dans un contexte de fin d'étude.",
        "Le Bloc 1 a posé les objectifs SMART : MVP livrable en quatre mois, service GPS temps réel, disponibilité cible de 99,9 %, capacité théorique orientée WebSocket, réduction des trajets vides et base d'une expérience différenciante autour de la sécurité et de l'accessibilité.",
        "Le Bloc 2 se concentre sur la réalisation technique : choix d'architecture, implémentation, tests, sécurité, CI/CD, déploiement, recette et documentation d'exploitation."
    ]))
    parts.append(heading(2, "1.1 Périmètre fonctionnel retenu"))
    for item in [
        "Application mobile Expo compatible Expo Go pour démontrer les parcours passager et chauffeur.",
        "API métier Django REST Framework pour les comptes, courses, paiements et notifications.",
        "Service GPS NestJS Socket.io séparé pour la publication et la recherche de positions chauffeurs.",
        "Déploiement Docker Compose sur Scaleway avec une trajectoire Kubernetes Kapsule documentée.",
        "Build mobile EAS déclenchable depuis GitHub Actions."
    ]:
        parts.append(bullet(item))
    parts.append(page_break())

    parts.append(heading(1, "2. Environnements de développement, test et déploiement"))
    parts.append(para("L'environnement FleetPro a été conçu pour réduire l'écart entre développement local et production. Les mêmes composants logiques sont présents localement et sur l'instance Scaleway : reverse proxy Nginx, API Django, service GPS, PostgreSQL et Redis."))
    parts.append(table(
        ["Environnement", "Objectif", "Preuves"],
        [
            ["Développement local", "Lancer l'ensemble de la stack avec Docker Compose et tester l'app mobile via Expo Go.", "`docker-compose.yml`, `README.md`"],
            ["Tests automatisés", "Vérifier backend, GPS et TypeScript mobile à chaque push ou pull request.", "`.github/workflows/ci.yml`"],
            ["Production MVP", "Héberger l'API et le GPS sur une Instance Scaleway à coût maîtrisé.", "`docker-compose.prod.yml`, `DEPLOY_SCALEWAY.md`"],
            ["Production cible", "Montrer une trajectoire cloud native avec Kapsule, Ingress et secrets Kubernetes.", "`infra/k8s/scaleway/*`"],
            ["Mobile", "Compiler des builds Android/iOS via EAS sans construire le mobile sur le serveur.", "`.github/workflows/eas-build.yml`"],
        ],
        [1700, 3900, 3760],
    ))
    parts.append(heading(2, "2.1 Développement local reproductible"))
    parts.append(para("La commande `docker compose up --build` permet de construire et d'orchestrer les services nécessaires à la démonstration. Le choix Docker évite les différences de configuration entre machines et simplifie l'évaluation : l'examinateur peut démarrer la stack avec une seule commande après avoir renseigné les variables d'environnement."))
    parts.append(heading(2, "2.2 Production Scaleway économique"))
    parts.append(para("Pour le rendu MVP, l'option retenue est une Instance Scaleway Ubuntu avec Docker installé. PostgreSQL et Redis sont exécutés en conteneurs avec volumes persistants afin d'éviter le coût d'une base managée pendant la phase de démonstration. Le registre d'images Scaleway stocke les images `fleetpro-backend` et `fleetpro-gps-service`."))
    parts.append(page_break())
    parts.append(heading(2, "2.3 Trajectoire Kubernetes Kapsule"))
    parts.append(para("Le dossier inclut aussi une cible Kubernetes afin de montrer la capacité du projet à évoluer vers une production plus robuste. Les manifests présents dans `infra/k8s/scaleway` décrivent le namespace, les deployments, services, ingress, configmaps et secrets attendus."))
    parts.append(table(
        ["Objet Kubernetes", "Usage", "Fichier"],
        [
            ["Namespace", "Isoler les ressources FleetPro.", "`infra/k8s/scaleway/namespace.yaml`"],
            ["ConfigMap", "Centraliser les variables non sensibles.", "`infra/k8s/scaleway/configmap.yaml`"],
            ["Secrets", "Stocker clés Django, JWT, PostgreSQL, Redis et Stripe.", "`infra/k8s/scaleway/secret.example.yaml`"],
            ["Deployment core-api", "Exécuter l'API Django et ses probes.", "`infra/k8s/scaleway/core-api.yaml`"],
            ["Deployment gps-service", "Exécuter le service Socket.io.", "`infra/k8s/scaleway/gps-service.yaml`"],
            ["Ingress", "Exposer l'API et le WebSocket via un domaine.", "`infra/k8s/scaleway/ingress.yaml`"],
            ["Job migrate", "Appliquer les migrations Django séparément du démarrage web.", "`infra/k8s/scaleway/migrate/job.yaml`"],
        ],
        [2000, 4200, 3160],
    ))
    parts.append(page_break())

    parts.append(heading(1, "3. Protocole d'intégration continue"))
    parts.append(para("La CI FleetPro est découpée en trois jobs indépendants : backend, GPS et mobile. Cette séparation évite qu'une anomalie TypeScript bloque la lecture des résultats Python, et inversement. Elle permet aussi de relancer uniquement le périmètre concerné lors du diagnostic."))
    parts.append(table(
        ["Job", "Commandes principales", "Critère de succès"],
        [
            ["backend", "`pip install -r backend/requirements.txt`; `coverage run manage.py test tests`; `coverage report --fail-under=90`; `makemigrations --check --dry-run`", "Tests Django verts, couverture minimale 90 % et aucune migration oubliée."],
            ["gps", "`npm ci`; `npm run test:coverage`; `npm run typecheck`; `npm run build`", "Tests Jest, seuils de couverture, typage TypeScript et build NestJS valides."],
            ["mobile", "`npm ci`; `npm run test:coverage`; `npm run typecheck`", "Tests unitaires légers, contrôle de logique mobile et compilation TypeScript."],
            ["eas-build", "`npm ci`; `npm run typecheck`; `eas build`", "Build mobile déclenché avec `EXPO_TOKEN` et variables publiques."],
        ],
        [1500, 5200, 2660],
    ))
    parts.append(heading(2, "3.1 Déclencheurs"))
    parts.append(para("Le workflow principal s'exécute sur `push` et `pull_request`. Le workflow EAS s'exécute manuellement via `workflow_dispatch` ou automatiquement lorsqu'un tag `mobile-v*` est poussé. Cette règle permet de conserver une CI rapide au quotidien et de réserver les builds mobiles aux jalons."))
    parts.append(heading(2, "3.2 Gestion des secrets CI/CD"))
    for item in [
        "`EXPO_TOKEN` est stocké dans GitHub Secrets, jamais dans le dépôt.",
        "`EXPO_PUBLIC_API_URL` et `EXPO_PUBLIC_GPS_URL` sont des variables GitHub Actions.",
        "Les secrets Django, JWT, PostgreSQL, Stripe et Firebase restent côté serveur ou côté environnement de production.",
        "La pipeline échoue explicitement si `EXPO_TOKEN` est absent, ce qui rend le diagnostic immédiat."
    ]:
        parts.append(bullet(item))
    parts.append(page_break())
    parts.append(heading(2, "3.3 Protocole de livraison continue"))
    parts.append(para("Le déploiement continu est volontairement progressif. La CI vérifie d'abord le code. Les images Docker sont ensuite construites, taguées et poussées vers le Container Registry Scaleway. La production tire explicitement l'image souhaitée. Le mobile suit un cycle séparé avec EAS, car l'application Expo ne doit pas être construite dans le conteneur serveur."))
    parts.append(table(
        ["Étape", "Action", "Contrôle"],
        [
            ["1", "Fusionner une branche uniquement après CI verte.", "Jobs backend/GPS/mobile réussis."],
            ["2", "Construire les images de production.", "`docker compose --env-file .env.prod -f docker-compose.prod.yml build`."],
            ["3", "Pousser les images vers Scaleway Registry.", "`docker compose --env-file .env.prod -f docker-compose.prod.yml push`."],
            ["4", "Tirer les images depuis l'instance.", "`docker compose --env-file .env.prod -f docker-compose.prod.yml pull`."],
            ["5", "Redémarrer la stack.", "`docker compose --env-file .env.prod -f docker-compose.prod.yml up -d`."],
            ["6", "Vérifier santé et logs.", "`/health`, `/api/v1/health/`, `docker compose logs`."],
        ],
        [900, 4900, 3560],
    ))
    parts.append(page_break())

    parts.append(heading(1, "4. Critères qualité et performance"))
    parts.append(para("Les critères qualité ne se limitent pas au fonctionnement visible. Le projet vérifie la reproductibilité, la santé des conteneurs, la séparation des responsabilités, la sécurité des secrets, la robustesse du typage et la capacité à diagnostiquer les erreurs."))
    parts.append(table(
        ["Critère", "Mesure", "État FleetPro"],
        [
            ["Disponibilité", "Healthchecks `/health` et `/api/v1/health/`", "Validé sur instance Scaleway."],
            ["Qualité backend", "Tests Django + migration check", "Automatisé en CI."],
            ["Qualité GPS", "Jest + TypeScript + build NestJS", "Automatisé en CI."],
            ["Qualité mobile", "Typecheck TypeScript", "Automatisé en CI et avant build EAS."],
            ["Performance GPS", "Redis GEO + TTL pour positions éphémères", "Conçu pour limiter l'état mémoire et supprimer les positions obsolètes."],
            ["Observabilité minimale", "Logs Docker, statuts de conteneurs, endpoints santé", "Disponible dans Docker Compose et sur serveur."],
        ],
        [2100, 3300, 3960],
    ))
    parts.append(callout("Critère de démonstration", "Une version est considérée présentable lorsque la CI est verte, le backend répond en 200 sur `/api/v1/health/`, le proxy Nginx répond en 200 sur `/health`, et un build EAS est disponible ou déclenchable."))
    parts.append(page_break())
    parts.append(heading(2, "4.1 Critères mesurables retenus"))
    parts.append(table(
        ["Famille", "Indicateur", "Seuil cible MVP"],
        [
            ["Tests", "Suites backend et GPS", "100 % des tests automatisés au vert avant livraison."],
            ["Typage", "TypeScript GPS et mobile", "Aucune erreur bloquante sur `npm run typecheck`."],
            ["Santé", "Endpoints health", "Réponse HTTP 200 en local et sur Scaleway."],
            ["Sécurité", "Longueur des secrets JWT", "Au moins 32 caractères pour HS256."],
            ["Données", "Persistance PostgreSQL", "Volumes Docker conservés entre redémarrages."],
            ["Temps réel", "Expiration positions GPS", "TTL Redis pour éviter les chauffeurs fantômes."],
            ["Mobile", "Build EAS", "Artefact Android/iOS généré sur profil choisi."],
        ],
        [1800, 4200, 3360],
    ))
    parts.append(para("Ces seuils sont adaptés à un MVP d'évaluation. Ils ne remplacent pas un monitoring production complet mais donnent des critères objectifs pour accepter ou refuser une livraison."))
    parts.append(page_break())

    parts.append(heading(1, "5. Architecture logicielle structurée"))
    parts.append(para("FleetPro applique une architecture hybride : un coeur transactionnel Django pour les données durables, un satellite NestJS pour le temps réel, une application mobile Expo pour l'expérience utilisateur, et Nginx comme point d'entrée unique."))
    parts.append(table(
        ["Bloc", "Responsabilité", "Raison du choix"],
        [
            ["Mobile Expo", "Interfaces passager/chauffeur, appels REST, sockets GPS.", "Itération rapide, Expo Go pour la démo, TypeScript pour la robustesse."],
            ["Nginx", "Reverse proxy REST et WebSocket.", "Unifie les URLs, simplifie CORS et prépare HTTPS."],
            ["Django REST", "Comptes, rôles, courses, paiements, notifications.", "Framework robuste, ORM, migrations, permissions et API REST."],
            ["NestJS GPS", "Authentification socket, publication positions, salles de course.", "Architecture événementielle adaptée au temps réel."],
            ["PostgreSQL", "Persistance métier.", "Base relationnelle fiable pour courses et paiements."],
            ["Redis", "Positions GPS temporaires et géo-index.", "Rapide, adapté aux TTL et recherches de proximité."],
        ],
        [1700, 3900, 3760],
    ))
    parts.append(heading(2, "5.1 Flux logique"))
    for item in [
        "Le passager se connecte et reçoit un couple de tokens JWT via Django.",
        "Le mobile crée une demande de course puis déclenche un paiement réel Stripe ou simulé.",
        "Le chauffeur publie sa position sur le service GPS via Socket.io avec le JWT.",
        "Le backend conserve les courses et transitions d'état ; le GPS ne conserve que l'état éphémère.",
        "Nginx route `/api/v1/*` vers Django et `/socket.io/*` vers NestJS."
    ]:
        parts.append(numbered(item))
    parts.append(page_break())

    parts.append(heading(2, "5.2 Domaines backend"))
    parts.append(para("Le backend est découpé en applications Django alignées sur le métier. Cette découpe rend chaque domaine compréhensible, testable et maintenable."))
    parts.append(table(
        ["Application", "Rôle", "Fichiers clés"],
        [
            ["accounts", "Utilisateurs, rôles passager/chauffeur, profils et véhicules.", "`backend/apps/accounts/*`"],
            ["rides", "Devis, cycle de vie d'une course, acceptation, démarrage, clôture, annulation.", "`backend/apps/rides/models.py`, `services.py`, `views.py`"],
            ["payments", "Création des PaymentIntents, simulation, webhooks Stripe, états locaux.", "`backend/apps/payments/services.py`, `views.py`"],
            ["notifications", "Enregistrement des devices et abstraction d'envoi push.", "`backend/apps/notifications/services.py`"],
        ],
        [1800, 4800, 2760],
    ))
    parts.append(heading(2, "5.3 Séparation temps réel / transactionnel"))
    parts.append(para("La séparation entre Django et NestJS évite de mélanger les écritures critiques de courses avec un flux GPS très fréquent. Elle rend aussi le service GPS remplaçable : tant que le contrat Socket.io et la vérification JWT restent compatibles, le coeur métier n'a pas besoin d'être réécrit."))
    parts.append(page_break())
    parts.append(heading(2, "5.4 Séquence métier simplifiée"))
    parts.append(para("La séquence ci-dessous décrit le chemin nominal d'une course. Elle peut être rejouée pendant la soutenance pour expliquer comment les services coopèrent."))
    for item in [
        "Le passager demande un devis ; Django calcule le prix, la commission FleetPro et le gain chauffeur.",
        "Le passager confirme ; Django crée la course et initialise le paiement.",
        "Le mobile interroge le GPS pour trouver les chauffeurs proches.",
        "Le chauffeur connecté publie sa position ; Redis conserve la dernière position avec TTL.",
        "Le chauffeur accepte ; Django change l'état de la course et sécurise les transitions suivantes.",
        "Les deux clients rejoignent la room de course ; Socket.io diffuse uniquement aux utilisateurs autorisés.",
        "La course est terminée ou annulée ; Django persiste l'état final et le paiement suit le scénario prévu."
    ]:
        parts.append(numbered(item))
    parts.append(page_break())

    parts.append(heading(1, "6. Prototype fonctionnel"))
    parts.append(para("Le prototype couvre les parcours indispensables à une démonstration de plateforme VTC : inscription, connexion, demande de course, choix Fleet Standard/FleetHer/Fleet PMR, paiement, recherche de chauffeur, publication GPS, acceptation, suivi et annulation."))
    parts.append(table(
        ["Parcours", "Acteur", "Composants mobilisés", "Statut"],
        [
            ["Connexion", "Passager / chauffeur", "Mobile, Django JWT, store Zustand", "Fonctionnel"],
            ["Demande de course", "Passager", "Mobile, `/rides/quote/`, `/rides/`", "Fonctionnel"],
            ["Paiement simulé", "Passager", "Mobile, backend payments", "Fonctionnel pour démo"],
            ["Choix service", "Passager", "Mobile, API rides", "Standard, FleetHer ou Fleet PMR"],
            ["Recherche chauffeur", "Passager", "Mobile, GPS service, Redis", "Fonctionnel selon éligibilité chauffeur"],
            ["Acceptation", "Chauffeur", "Mobile driver, backend rides", "Fonctionnel avec compte driver"],
            ["Suivi GPS", "Passager / chauffeur", "Socket.io, Redis, rooms de course", "Prototype fonctionnel"],
        ],
        [1900, 1800, 3900, 1760],
    ))
    parts.append(heading(2, "6.1 Limites assumées du prototype"))
    for item in [
        "Le paiement réel Stripe reste en mode test ; un paiement simulé existe pour les démonstrations sans carte.",
        "Les notifications push nécessitent un development build Expo configuré avec Firebase/APNs.",
        "FleetHer et Fleet PMR sont intégrés au MVP via des règles d'éligibilité ; SmartPredict reste un axe produit futur.",
        "La disponibilité 99,9 % est un objectif cible ; le MVP Scaleway Instance n'est pas encore une architecture multi-zone."
    ]:
        parts.append(bullet(item))
    parts.append(page_break())
    parts.append(heading(2, "6.2 Script de démonstration recommandé"))
    parts.append(para("Pour une démonstration fluide, il est préférable de préparer deux sessions : un passager et un chauffeur. Si un seul téléphone est disponible, le mode de simulation permet de vérifier le flux passager sans dépendre d'un chauffeur réel."))
    parts.append(table(
        ["Temps", "Action", "Message à expliquer"],
        [
            ["00:00", "Ouvrir l'application et se connecter passager.", "JWT et rôle utilisateur."],
            ["01:00", "Demander une course avec départ et arrivée.", "Calcul métier côté backend."],
            ["02:00", "Confirmer la course et le paiement simulé.", "Paiement sécurisé côté serveur."],
            ["03:00", "Basculer sur le chauffeur et publier la position.", "Socket.io + Redis TTL."],
            ["04:00", "Accepter la course.", "Transition d'état côté Django."],
            ["05:00", "Observer le suivi ou annuler.", "Recette du cycle de vie."],
        ],
        [1100, 4300, 3960],
    ))
    parts.append(page_break())

    parts.append(heading(1, "7. Frameworks, paradigmes et design patterns"))
    parts.append(para("Le projet combine plusieurs paradigmes adaptés à chaque partie : REST transactionnel, événements WebSocket temps réel, composants React Native, services métiers et injection de dépendances côté NestJS."))
    parts.append(table(
        ["Pattern / paradigme", "Application dans FleetPro", "Bénéfice"],
        [
            ["Layered Architecture", "Vues, serializers, services et modèles séparés côté Django.", "Lisibilité et testabilité."],
            ["Service Layer", "`rides/services.py`, `payments/services.py`, `notifications/services.py`.", "Logique métier isolée des contrôleurs."],
            ["Repository / Store spécialisé", "`RedisGpsStore` encapsule Redis GEO et TTL.", "Remplacement et test plus simples."],
            ["Gateway Pattern", "`PushNotificationGateway` et gateway de paiement simulée/Stripe.", "Dépendances externes découplées."],
            ["API Gateway", "Nginx expose REST et WebSocket derrière un point d'entrée unique.", "Routage, sécurité réseau et future terminaison TLS."],
            ["HATEOAS", "Les serializers comptes, courses et paiements exposent `_links` avec les transitions possibles.", "API REST niveau 3 plus découvrable."],
            ["Observer / Pub-Sub", "Socket.io diffuse les positions aux salles de course.", "Temps réel sans polling."],
            ["State Store", "Zustand garde l'état auth/rides côté mobile.", "État prévisible et partagé entre écrans."],
        ],
        [2200, 4300, 2860],
    ))
    parts.append(para("Ces choix correspondent au besoin : garder un coeur métier fiable, isoler les flux fréquents, limiter le couplage et pouvoir justifier chaque brique pendant l'évaluation."))
    parts.append(page_break())

    parts.append(heading(1, "8. Harnais de tests unitaires"))
    parts.append(para("Les tests automatisés valident les règles métier principales et les contrats techniques critiques. Ils sont exécutés localement et dans GitHub Actions."))
    parts.append(table(
        ["Suite", "Fichiers", "Ce qui est vérifié"],
        [
            ["Comptes", "`backend/tests/test_accounts.py`", "Création, authentification, rôles et profil utilisateur."],
            ["Tarification", "`backend/tests/test_fares.py`", "Calcul du prix, commission fixe 15 % et gain chauffeur."],
            ["Matching", "`backend/tests/test_matching.py`", "Recherche et filtrage des chauffeurs proches."],
            ["Notifications", "`backend/tests/test_notifications.py`", "Abstraction gateway et comportement d'enregistrement."],
            ["GPS Auth", "`gps-service/src/socket-auth.service.spec.ts`", "Décodage JWT et rejet des tokens invalides."],
            ["Ride Access", "`gps-service/src/ride-access.service.spec.ts`", "Vérification d'accès à une course avant room Socket.io."],
        ],
        [1700, 3300, 4360],
    ))
    parts.append(heading(2, "8.1 Commandes de validation"))
    for item in [
        "`docker compose exec backend coverage run manage.py test tests`",
        "`docker compose exec backend coverage report --fail-under=90`",
        "`docker compose exec backend python manage.py makemigrations --check --dry-run`",
        "`docker compose exec gps-service npm run test:coverage`",
        "`docker compose exec gps-service npm run typecheck`",
        "`cd mobile && npm run test:coverage`",
        "`cd mobile && npm run typecheck`"
    ]:
        parts.append(bullet(item))
    parts.append(callout("Résultats de couverture ajoutés", "Backend Django : 42 tests, couverture globale 98 % et seuil CI `coverage report --fail-under=90` atteint. GPS NestJS : 20 tests, couverture globale environ 99 % statements, 87 % branches, 100 % functions. Mobile Expo : 21 tests Jest/Istanbul couvrant Axios JWT, auth, rides, helpers et données de démonstration ; couverture 99.04 % statements, 88.88 % branches, 96.29 % functions et 100 % lines, avec typecheck TypeScript complet."))
    parts.append(heading(2, "8.2 Stratégie de couverture"))
    parts.append(para("La priorité de couverture est donnée aux règles qui peuvent casser l'expérience ou la sécurité : authentification, rôles, calcul de prix, cycle de course, accès WebSocket et intégration paiement. Les tests d'interface mobile sont identifiés comme amélioration future, car le projet utilise actuellement surtout du typage TypeScript et des tests backend/GPS."))
    parts.append(page_break())
    parts.append(heading(2, "8.3 Matrice de traçabilité tests / risques"))
    parts.append(table(
        ["Risque", "Test ou contrôle", "Résultat attendu"],
        [
            ["Un passager accède à une action chauffeur.", "Tests comptes + permissions rides.", "Refus HTTP ou action indisponible."],
            ["Commission erronée.", "`test_fares.py`.", "Commission 15 % calculée côté serveur."],
            ["Socket acceptant un token invalide.", "`socket-auth.service.spec.ts`.", "Connexion rejetée."],
            ["Course suivie par un tiers.", "`ride-access.service.spec.ts`.", "Accès room refusé."],
            ["Migration oubliée.", "`makemigrations --check --dry-run`.", "Pipeline échoue avant livraison."],
            ["Erreur de typage mobile.", "`npm run typecheck`.", "Pipeline mobile échoue."],
        ],
        [2900, 3300, 3160],
    ))
    parts.append(page_break())

    parts.append(heading(1, "9. Sécurité et accessibilité"))
    parts.append(para("La sécurité FleetPro est traitée à plusieurs niveaux : authentification JWT, secrets hors dépôt, permissions par rôle, validation serveur, signature webhook Stripe, isolation réseau via Nginx et variables d'environnement de production."))
    parts.append(table(
        ["Risque OWASP", "Mesure FleetPro", "Preuve"],
        [
            ["Broken Access Control", "Permissions Django et vérification d'accès aux rooms GPS.", "`rides/permissions.py`, `ride-access.service.ts`"],
            ["Cryptographic Failures", "Secrets JWT longs, HTTPS prévu via Load Balancer/TLS, Stripe secret côté serveur.", "`.env.prod.example`, `DEPLOY_SCALEWAY.md`"],
            ["Injection", "ORM Django, serializers DRF, pas de concaténation SQL métier.", "`backend/apps/*/serializers.py`"],
            ["Insecure Design", "Séparation domaines, paiement serveur, GPS éphémère Redis TTL.", "`docs/ARCHITECTURE.md`"],
            ["Security Misconfiguration", "Allowed hosts, CORS, secure redirect configurable.", "`backend/core/settings.py`"],
            ["Identification/Auth Failures", "SimpleJWT, refresh token, endpoints protégés.", "`docs/API.md`"],
            ["Logging/Monitoring", "Logs Docker, healthchecks, GitHub Actions.", "`docker-compose.prod.yml`, workflows CI"],
        ],
        [2200, 4400, 2760],
    ))
    parts.append(heading(2, "9.1 Protection des paiements"))
    parts.append(para("Le mobile ne reçoit jamais de clé secrète Stripe. Il demande au backend de créer une intention de paiement, puis Stripe ou le simulateur gère l'autorisation. Les webhooks sont prévus côté backend afin de fiabiliser l'état local des paiements."))
    parts.append(heading(2, "9.2 Accessibilité"))
    parts.append(table(
        ["Thème", "Décision", "Amélioration prévue"],
        [
            ["Contrastes", "Palette sombre premium avec composants réutilisables.", "Audit RGAA/ WCAG sur écrans principaux."],
            ["Navigation", "Parcours par rôles et onglets simples.", "Ajouter labels d'accessibilité sur boutons et champs."],
            ["Lisibilité", "Composants `AppButton`, `FieldPill`, `SectionHeader`.", "Tester tailles de police dynamiques iOS/Android."],
            ["Erreurs", "Messages utilisateur sur login, paiement et course.", "Normaliser les messages et états vides."],
        ],
        [1900, 3900, 3560],
    ))
    parts.append(page_break())
    parts.append(heading(2, "9.3 Modèle de menace synthétique"))
    parts.append(para("Le modèle de menace se concentre sur les actifs critiques : comptes, tokens JWT, données de course, données de paiement et positions GPS."))
    parts.append(table(
        ["Actif", "Menace", "Mesure"],
        [
            ["Token JWT", "Vol ou réutilisation.", "Durée de vie limitée, refresh séparé, secret long."],
            ["Course", "Modification par utilisateur non autorisé.", "Permissions backend et vérification d'appartenance."],
            ["Position GPS", "Persistance excessive ou publication non autorisée.", "JWT socket, Redis TTL, rooms privées."],
            ["Paiement", "Exposition de secret Stripe.", "Secret uniquement backend, PaymentIntent côté serveur."],
            ["Infrastructure", "Mauvaise exposition de ports.", "Nginx comme point d'entrée, variables env contrôlées."],
            ["CI/CD", "Fuite de secrets.", "GitHub Secrets et absence de secrets dans le dépôt."],
        ],
        [1800, 3600, 3960],
    ))
    parts.append(page_break())

    parts.append(heading(1, "10. Historique des versions et déploiement progressif"))
    parts.append(para("L'historique Git montre une progression incrémentale : d'abord les rôles et JWT, puis les notes d'annulation et healthcheck, ensuite le flux de paiement et d'authentification de démonstration, la stabilisation CI/mobile, la production Scaleway et enfin le build EAS."))
    parts.append(table(
        ["Commit", "Objet", "Impact"],
        [
            ["497079b", "inscription + jwt", "Base authentification et rôles."],
            ["54b99d4", "role + note driver et cancelled", "Cycle de course enrichi."],
            ["965506e", "note annulationhealtch check", "Santé API et annulation."],
            ["04d45e5", "fix demo auth and payment flow", "Connexion et paiement démonstration stabilisés."],
            ["5d37f7e", "stabilize ci and local mobile docker", "CI et Docker mobile fiabilisés."],
            ["51e882a", "add scaleway production deployment stack", "Production Docker/Kubernetes documentée."],
            ["ab3d55e", "add eas mobile build pipeline and docs", "Build mobile EAS intégré."],
            ["0f524f6", "fix eas build token", "Secret Expo contrôlé en pipeline."],
        ],
        [1600, 3600, 4160],
    ))
    parts.append(heading(2, "10.1 Déploiement progressif"))
    for item in [
        "Étape 1 : validation locale Docker Compose.",
        "Étape 2 : push des images vers Scaleway Container Registry.",
        "Étape 3 : déploiement Instance + Docker Compose avec volumes persistants.",
        "Étape 4 : vérification `/health` et `/api/v1/health/`.",
        "Étape 5 : build mobile EAS avec variables API/GPS orientées production.",
        "Étape 6 : trajectoire Kubernetes Kapsule documentée pour montée en charge."
    ]:
        parts.append(numbered(item))
    parts.append(page_break())

    parts.append(heading(1, "11. Cahier de recettes"))
    parts.append(para("Le cahier de recettes permet à un évaluateur de rejouer les scénarios principaux sans connaître le code. Les scénarios ci-dessous couvrent les parcours fonctionnels, techniques et de sécurité."))
    parts.append(table(
        ["ID", "Scénario", "Prérequis", "Résultat attendu"],
        [
            ["RF-01", "Connexion passager", "Compte `passenger` créé par `seed_demo`.", "JWT reçu et écran passager affiché."],
            ["RF-02", "Connexion chauffeur", "Compte `driver` créé.", "JWT reçu et écran chauffeur affiché."],
            ["RF-03", "Création d'une course", "Passager connecté.", "Course créée en statut `REQUESTED`."],
            ["RF-04", "Paiement simulé", "`ENABLE_DEMO_SIMULATION=true`.", "Paiement autorisé sans Stripe réel."],
            ["RF-05", "Chauffeur en ligne", "Chauffeur connecté, GPS activé.", "Position publiée et stockée dans Redis."],
            ["RF-06", "Acceptation course", "Chauffeur proche disponible.", "Course en statut `ACCEPTED`."],
        ],
        [900, 2300, 3100, 3060],
    ))
    parts.append(page_break())
    parts.append(heading(2, "11.1 Recette complémentaire"))
    parts.append(table(
        ["ID", "Scénario", "Prérequis", "Résultat attendu"],
        [
            ["RF-07", "Suivi GPS", "Course acceptée et room rejointe.", "Le passager reçoit `driver:position:updated`."],
            ["RF-08", "Annulation course", "Course ouverte.", "Statut `CANCELED` et raison stockée."],
            ["RF-09", "Healthcheck API", "Stack déployée.", "`/api/v1/health/` retourne 200."],
            ["RF-10", "Build mobile EAS", "`EXPO_TOKEN` et variables configurés.", "Build Android/iOS généré sur Expo."],
            ["RS-01", "Token Socket.io absent", "Socket ouvert sans JWT.", "Connexion refusée."],
            ["RS-02", "Accès course interdit", "Utilisateur non membre de la course.", "Room non rejointe ou erreur autorisation."],
        ],
        [900, 2300, 3100, 3060],
    ))
    parts.append(heading(2, "11.2 Procédure de recette manuelle"))
    for item in [
        "Démarrer la stack : `docker compose --env-file .env.prod -f docker-compose.prod.yml up -d`.",
        "Créer les comptes : `docker compose exec backend python manage.py seed_demo`.",
        "Vérifier l'API : `Invoke-WebRequest http://51.158.102.141/api/v1/health/`.",
        "Lancer Expo Go : `cd mobile && npx expo start --lan --clear`.",
        "Tester passager puis chauffeur avec les comptes de démonstration."
    ]:
        parts.append(numbered(item))
    parts.append(page_break())

    parts.append(heading(1, "12. Plan de correction des bugs"))
    parts.append(para("Les incidents rencontrés pendant la mise en production ont été traités comme des fiches bugs : symptôme, cause probable, correction, validation. Cette méthode permet de démontrer la capacité à stabiliser un produit en environnement réel."))
    parts.append(table(
        ["Bug", "Cause", "Correction", "Validation"],
        [
            ["Docker Desktop WSL timeout", "Moteur WSL bloqué.", "Arrêt WSL, redémarrage Docker Desktop.", "`docker compose` relancé."],
            ["Port 8081 indisponible", "Ancien processus Expo/Node.", "Libérer le port ou changer le mapping.", "Mobile relancé."],
            ["`expo-notifications` introuvable", "Dépendance/volume `node_modules` incohérent.", "Dépendance ajoutée et volumes recréés.", "Expo démarre."],
            ["Node `--no-webstorage`", "Option incompatible avec Node CI.", "Script de test GPS corrigé.", "Job GPS vert."],
            ["JWT HMAC trop court", "Secret inférieur à 32 bytes.", "Secret long dans `.env.prod`.", "Warning supprimé."],
            ["Login driver 401", "Comptes absents ou refresh token mal géré.", "Seed demo et correction interceptor.", "Connexion driver OK."],
            ["Backend unhealthy", "Host Django refusé.", "`DJANGO_ALLOWED_HOSTS` corrigé.", "Healthcheck 200."],
            ["EAS sans build", "`EXPO_TOKEN` absent.", "Secret GitHub ajouté.", "Build EAS réussi."],
        ],
        [2100, 2500, 2600, 2160],
    ))
    parts.append(heading(2, "12.1 Priorisation"))
    for item in [
        "P1 : bloque la connexion, le paiement, la création de course ou le déploiement.",
        "P2 : dégrade une fonctionnalité principale sans bloquer toute la démonstration.",
        "P3 : amélioration UX, documentation ou dette technique non bloquante."
    ]:
        parts.append(bullet(item))
    parts.append(page_break())

    parts.append(heading(1, "13. Documentation d'exploitation"))
    parts.append(para("La documentation d'exploitation doit permettre de démarrer, déployer, vérifier, sauvegarder et mettre à jour FleetPro. Elle est répartie dans `README.md`, `DEPLOY_SCALEWAY.md`, `docs/API.md`, `docs/ARCHITECTURE.md` et `docs/TROUBLESHOOTING.md`."))
    parts.append(heading(2, "13.1 Déploiement Instance Scaleway"))
    for item in [
        "Créer ou utiliser le Container Registry `rg.fr-par.scw.cloud/fleet-pro`.",
        "Construire et pousser les images `fleetpro-backend` et `fleetpro-gps-service`.",
        "Copier `.env.prod` sur le serveur dans `/opt/fleetpro`.",
        "Exécuter `docker compose --env-file .env.prod -f docker-compose.prod.yml pull`.",
        "Exécuter `docker compose --env-file .env.prod -f docker-compose.prod.yml up -d`.",
        "Contrôler `docker compose ps`, `/health` et `/api/v1/health/`."
    ]:
        parts.append(numbered(item))
    parts.append(heading(2, "13.2 Sauvegarde et mise à jour"))
    parts.append(para("Les données PostgreSQL sont conservées dans un volume Docker. Une sauvegarde manuelle peut être générée avec `pg_dump`. Pour mettre à jour, il faut pousser une nouvelle image, modifier `IMAGE_TAG`, tirer les images puis recréer les conteneurs. En cas de régression, le rollback consiste à revenir au tag précédent et relancer `docker compose up -d`."))
    parts.append(page_break())
    parts.append(heading(2, "13.3 Manuel utilisateur passager"))
    for item in [
        "Ouvrir l'application mobile et choisir le profil passager.",
        "Se connecter avec un compte existant ou créer un compte.",
        "Renseigner un point de départ et une destination.",
        "Demander un devis et vérifier le prix affiché.",
        "Confirmer la course, puis valider le paiement test ou simulé.",
        "Attendre l'affectation d'un chauffeur, suivre sa position et annuler si nécessaire.",
        "Consulter l'état final de la course et l'historique disponible."
    ]:
        parts.append(numbered(item))
    parts.append(page_break())
    parts.append(heading(2, "13.4 Manuel utilisateur chauffeur"))
    for item in [
        "Ouvrir l'application mobile et choisir le profil chauffeur.",
        "Se connecter avec un compte chauffeur valide.",
        "Vérifier le profil chauffeur et le véhicule associé.",
        "Passer disponible et autoriser la localisation.",
        "Publier la position GPS afin d'apparaître dans la recherche de proximité.",
        "Accepter une course disponible, puis démarrer la prise en charge.",
        "Terminer la course et vérifier le changement d'état côté backend."
    ]:
        parts.append(numbered(item))
    parts.append(page_break())
    parts.append(heading(2, "13.5 Manuel de maintenance technique"))
    parts.append(table(
        ["Action", "Commande", "Moment"],
        [
            ["Voir les conteneurs", "`docker compose --env-file .env.prod -f docker-compose.prod.yml ps`", "Après chaque déploiement."],
            ["Lire les logs backend", "`docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f backend`", "En cas d'erreur API."],
            ["Lancer migrations", "`docker compose exec backend python manage.py migrate`", "Après changement de modèle."],
            ["Créer données demo", "`docker compose exec backend python manage.py seed_demo`", "Avant recette."],
            ["Sauvegarder PostgreSQL", "`pg_dump -U fleetpro fleetpro > fleetpro_backup.sql`", "Avant mise à jour majeure."],
            ["Rollback image", "Remettre l'ancien `IMAGE_TAG` puis `up -d`", "Si la recette post-déploiement échoue."],
        ],
        [2100, 5000, 2260],
    ))
    parts.append(page_break())

    parts.append(heading(1, "14. Conclusion"))
    parts.append(para("FleetPro valide le périmètre attendu du Bloc 2 : architecture structurée, prototype fonctionnel, tests automatisés, CI/CD, déploiement cloud, sécurité, recette et documentation. Le projet reste volontairement réaliste : le MVP fonctionne sur une infrastructure économique, tout en conservant une trajectoire Kubernetes et production plus robuste."))
    parts.append(para("Les prochaines améliorations à prioriser sont l'ajout de tests end-to-end mobile, la finalisation des notifications push en development build, l'audit accessibilité détaillé, la supervision applicative et l'activation HTTPS avec domaine dédié."))
    parts.append(page_break())

    parts.append(heading(1, "Annexe A - Correspondance compétences Bloc 2"))
    parts.append(table(
        ["Compétence", "Preuve principale", "Couverture"],
        [
            ["C2.1.1", "Docker, Scaleway, healthchecks, critères qualité/performance.", "Protocole de déploiement continu et critères exploitables."],
            ["C2.1.2", "GitHub Actions backend/GPS/mobile + EAS.", "Intégration continue et déclenchement de builds."],
            ["C2.2.1", "Architecture Django/NestJS/Expo.", "Conception structurée et prototype."],
            ["C2.2.2", "Tests Django, Jest GPS, typecheck mobile.", "Harnais de tests unitaires."],
            ["C2.2.3", "JWT, rôles, CORS, secrets, Stripe côté serveur.", "Sécurité et accessibilité."],
            ["C2.2.4", "Git log, Docker Registry, déploiement Scaleway, EAS.", "Version fonctionnelle et historique."],
            ["C2.3.1", "Cahier RF/RS.", "Recette fonctionnelle et technique."],
            ["C2.3.2", "Fiches bugs.", "Méthode de correction."],
            ["C2.4.1", "README, DEPLOY, API, TROUBLESHOOTING.", "Documentation technique."],
        ],
        [1300, 4500, 3560],
    ))
    parts.append(page_break())

    parts.append(heading(1, "Annexe B - Captures à ajouter avant dépôt"))
    parts.append(para("Les captures ne sont pas intégrées automatiquement car elles dépendent de ton compte GitHub, Expo et Scaleway. Elles peuvent être insérées dans Word aux emplacements indiqués ci-dessous pour renforcer le dossier final."))
    parts.append(table(
        ["Capture", "Où l'ajouter", "Objectif"],
        [
            ["GitHub Actions CI verte", "Section 3", "Prouver l'intégration continue."],
            ["EAS Build terminé", "Section 3 ou 10", "Prouver le build mobile."],
            ["Scaleway Instance + containers", "Section 2 ou 13", "Prouver l'hébergement cloud."],
            ["Endpoint `/health` en 200", "Section 4", "Prouver la santé production."],
            ["Écran mobile passager", "Section 6", "Prouver le prototype."],
            ["Écran mobile chauffeur", "Section 6", "Prouver le double rôle."],
        ],
        [2600, 2700, 4060],
    ))
    parts.append(page_break())
    parts.append(heading(1, "Annexe C - Checklist finale avant soutenance"))
    for item in [
        "Vérifier que le dépôt ne contient aucun secret réel dans `.env`, `.env.prod` ou les manifests Kubernetes.",
        "Pousser la dernière version et contrôler que la CI GitHub Actions est verte.",
        "Vérifier que l'instance Scaleway répond sur `http://51.158.102.141/health` et `/api/v1/health/`.",
        "Relancer `seed_demo` si les comptes passager/chauffeur de démonstration ne fonctionnent plus.",
        "Préparer un QR code Expo Go ou un build EAS installable selon le support choisi.",
        "Insérer les captures d'écran récentes dans l'annexe ou en illustration des sections concernées.",
        "Exporter ce DOCX en PDF après vérification manuelle sous Word ou LibreOffice."
    ]:
        parts.append(bullet(item))
    return parts


def styles_xml() -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="{NS_W}">
  <w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="280" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/><w:pPr><w:spacing w:after="120" w:line="280" w:lineRule="auto"/></w:pPr><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="BodyText"><w:name w:val="Body Text"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="100" w:line="280" w:lineRule="auto"/></w:pPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:outlineLvl w:val="0"/><w:spacing w:before="320" w:after="160"/></w:pPr><w:rPr><w:b/><w:color w:val="2E74B5"/><w:sz w:val="32"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:outlineLvl w:val="1"/><w:spacing w:before="240" w:after="120"/></w:pPr><w:rPr><w:b/><w:color w:val="2E74B5"/><w:sz w:val="26"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:outlineLvl w:val="2"/><w:spacing w:before="160" w:after="80"/></w:pPr><w:rPr><w:b/><w:color w:val="1F4D78"/><w:sz w:val="24"/></w:rPr></w:style>
</w:styles>'''


def numbering_xml() -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="{NS_W}">
  <w:abstractNum w:abstractNumId="0">
    <w:multiLevelType w:val="singleLevel"/>
    <w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/><w:lvlJc w:val="left"/><w:pPr><w:tabs><w:tab w:val="num" w:pos="720"/></w:tabs><w:ind w:left="720" w:hanging="360"/></w:pPr></w:lvl>
  </w:abstractNum>
  <w:abstractNum w:abstractNumId="1">
    <w:multiLevelType w:val="singleLevel"/>
    <w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%1."/><w:lvlJc w:val="left"/><w:pPr><w:tabs><w:tab w:val="num" w:pos="720"/></w:tabs><w:ind w:left="720" w:hanging="360"/></w:pPr></w:lvl>
  </w:abstractNum>
  <w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
  <w:num w:numId="2"><w:abstractNumId w:val="1"/></w:num>
</w:numbering>'''


def document_xml() -> str:
    body = "".join(build_content())
    sect = (
        '<w:sectPr><w:headerReference w:type="default" r:id="rId1"/>'
        '<w:footerReference w:type="default" r:id="rId2"/>'
        '<w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/>'
        '<w:cols w:space="720"/><w:docGrid w:linePitch="360"/></w:sectPr>'
    )
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{NS_W}" xmlns:r="{NS_R}">
  <w:body>{body}{sect}</w:body>
</w:document>'''


def footer_xml() -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="{NS_W}" xmlns:r="{NS_R}">
  <w:p><w:pPr><w:jc w:val="right"/></w:pPr>
    {run_xml("FleetPro - Bloc 2 | Page ", size=9, color="555555")}
    <w:r><w:rPr><w:sz w:val="18"/><w:color w:val="555555"/></w:rPr><w:fldChar w:fldCharType="begin"/></w:r>
    <w:r><w:rPr><w:sz w:val="18"/><w:color w:val="555555"/></w:rPr><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>
    <w:r><w:rPr><w:sz w:val="18"/><w:color w:val="555555"/></w:rPr><w:fldChar w:fldCharType="end"/></w:r>
  </w:p>
</w:ftr>'''


def header_xml() -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:hdr xmlns:w="{NS_W}" xmlns:r="{NS_R}">
  <w:p><w:pPr><w:jc w:val="right"/></w:pPr>{run_xml("Dossier professionnel - FleetPro", size=9, color="777777")}</w:p>
</w:hdr>'''


def content_types_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
  <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
  <Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>
  <Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>'''


def rels_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''


def document_rels_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
</Relationships>'''


def settings_xml() -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="{NS_W}"><w:zoom w:percent="100"/><w:defaultTabStop w:val="720"/><w:updateFields w:val="true"/></w:settings>'''


def core_xml() -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>FleetPro - Dossier Bloc 2</dc:title>
  <dc:subject>Concevoir et développer des applications logicielles</dc:subject>
  <dc:creator>Nawfel Hilal</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>'''


def app_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>FleetPro DOCX Builder</Application>
  <DocSecurity>0</DocSecurity>
  <ScaleCrop>false</ScaleCrop>
  <Company>FleetPro</Company>
  <LinksUpToDate>false</LinksUpToDate>
  <SharedDoc>false</SharedDoc>
  <HyperlinksChanged>false</HyperlinksChanged>
  <AppVersion>1.0</AppVersion>
</Properties>'''


def build_docx() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types_xml())
        docx.writestr("_rels/.rels", rels_xml())
        docx.writestr("docProps/core.xml", core_xml())
        docx.writestr("docProps/app.xml", app_xml())
        docx.writestr("word/document.xml", document_xml())
        docx.writestr("word/styles.xml", styles_xml())
        docx.writestr("word/numbering.xml", numbering_xml())
        docx.writestr("word/settings.xml", settings_xml())
        docx.writestr("word/header1.xml", header_xml())
        docx.writestr("word/footer1.xml", footer_xml())
        docx.writestr("word/_rels/document.xml.rels", document_rels_xml())


if __name__ == "__main__":
    build_docx()
    print(OUT)
