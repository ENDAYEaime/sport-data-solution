# Sport Data Solution — POC Avantages Sportifs

Pipeline de données automatisé permettant de calculer et d'attribuer des avantages salariés liés à la pratique sportive : **prime sportive** et **journées bien-être**.

Projet réalisé dans le cadre du parcours **Data Engineer — OpenClassrooms**.

---

## Table des matières

1. [Contexte du projet](#contexte-du-projet)
2. [Règles métier](#règles-métier)
3. [Données sources](#données-sources)
4. [Architecture du pipeline](#architecture-du-pipeline)
5. [Stack technique](#stack-technique)
6. [Structure du projet](#structure-du-projet)
7. [Installation et lancement](#installation-et-lancement)
8. [Étapes du pipeline](#étapes-du-pipeline)
9. [Modèle de données (PostgreSQL)](#modèle-de-données-postgresql)
10. [Contrôles qualité](#contrôles-qualité)
11. [Notifications Slack](#notifications-slack)
12. [Dashboard Power BI](#dashboard-power-bi)
13. [Monitoring](#monitoring)
14. [Livrables](#livrables)
15. [Pistes d'amélioration](#pistes-damélioration)

---

## Contexte du projet

L'entreprise **Sport Data Solution** souhaite encourager la pratique sportive de ses salariés en mettant en place deux avantages :

- une **prime sportive** pour les salariés se rendant au travail par un moyen de déplacement « sportif » ;
- des **journées bien-être** pour les salariés pratiquant une activité sportive régulière.

L'objectif de ce **POC (Proof of Concept)** est de démontrer la **faisabilité technique** d'un pipeline de données automatisé qui :

1. ingère les données RH et les données sportives des salariés ;
2. simule un historique d'activités sportives sur 12 mois (flux « Strava-like ») ;
3. contrôle la qualité des données ;
4. calcule automatiquement les avantages (prime + jours bien-être) ;
5. publie les activités sur Slack ;
6. restitue les résultats dans un dashboard Power BI.

---

## Règles métier

| Avantage | Condition d'éligibilité | Valeur |
|---|---|---|
| **Prime sportive** | Venir au bureau en mode de déplacement sportif (marche/running, vélo/trottinette) | **5 % du salaire brut annuel** |
| **Journées bien-être** | Au moins **15 activités sportives** déclarées sur les 12 derniers mois | **5 jours** de congé supplémentaires |

### Validation des distances domicile -> entreprise

La cohérence du mode de déplacement déclaré est vérifiée via l'**API Google Maps** (calcul de la distance domicile -> bureau) :

| Mode de déplacement déclaré | Distance maximale acceptée |
|---|---|
| Marche / Running | **≤ 15 km** |
| Vélo / Trottinette / Autres | **≤ 25 km** |

Un salarié déclarant venir en courant alors qu'il habite à 40 km est donc considéré comme **non éligible** à la prime.

---

## Données sources

### 1. `Données RH.xlsx` — 161 salariés

Informations RH par salarié :

- ID salarié, nom, prénom
- Salaire brut annuel
- Date d'embauche, type de contrat
- Adresse du domicile (utilisée pour le calcul de distance)
- Business Unit / département
- **Moyen de déplacement déclaré** :
  - Véhicule : 73 salariés
  - Vélo / Trottinette / Autres : 54 salariés
  - Transports en commun : 20 salariés
  - Marche / Running : 14 salariés

### 2. `Données Sportive.xlsx` — 161 salariés

- ID salarié + **sport pratiqué**
- 66 salariés ne déclarent **aucun sport**
- Sports les plus fréquents : Running (18), Randonnée (16), Tennis (11), Natation (8), Football (6)

### 3. Activités sportives simulées (générateur Python « Strava-like »)

Le générateur **n'invente pas** de sport : il s'appuie sur le sport **déjà déclaré** par chaque salarié dans le fichier sportif, puis génère un historique réaliste de séances sur les **12 derniers mois** (plusieurs milliers de lignes au total, cible : 5 000 à 10 000 activités).

Colonnes générées :

| Colonne | Description |
|---|---|
| `id` | Identifiant unique de l'activité |
| `id_salarie` | Référence au salarié |
| `sport` | Sport déclaré par le salarié |
| `date_debut` | Date/heure de début (aléatoire dans les 12 derniers mois) |
| `date_fin` | Date/heure de fin (début + durée) |
| `distance` | Distance réaliste selon le sport |
| `temps` | Durée de la séance |
| `commentaire` | Commentaire simulé |

Paramètres de simulation par sport (exemples) :

| Sport | Distance | Durée |
|---|---|---|
| Running | 3 – 15 km | 25 – 90 min |
| Randonnée | 5 – 25 km | 60 – 240 min |
| Vélo | 10 – 60 km | — |
| Natation | 500 – 3 000 m | — |
| Tennis | (vide) | 45 – 120 min |
| Musculation | (vide) | 45 – 90 min |
| Escalade | (vide) | — |

Chaque salarié sportif se voit attribuer entre **5 et 80 séances** sur l'année, ce qui simule des profils plus ou moins assidus.

---

## Architecture du pipeline

```
        ┌────────────────────┐   ┌──────────────────────┐
        │  Données RH.xlsx   │   │ Données Sportive.xlsx │
        └─────────┬──────────┘   └──────────┬───────────┘
                  └────────────┬────────────┘
                               ▼
              ┌──────────────────────────────┐
              │ Python                       │
              │ Nettoyage + génération des   │
              │ activités sur 12 mois        │
              └──────────────┬───────────────┘
                             ▼
              ┌──────────────────────────────┐
              │ PostgreSQL                   │
              │ Stockage des tables propres  │
              └──────────────┬───────────────┘
                             ▼
              ┌──────────────────────────────┐
              │ Tests qualité                │
              │ (Great Expectations / Python)│
              └──────────────┬───────────────┘
                             ▼
              ┌──────────────────────────────┐
              │ Calcul des avantages         │
              │ Prime 5 % + 5 jours bien-être│
              └──────────────┬───────────────┘
                ┌────────────┴─────────────┐
                ▼                          ▼
        ┌──────────────┐          ┌────────────────┐
        │ Slack        │          │ Power BI       │
        │ Publications │          │ Dashboard KPI  │
        └──────────────┘          └────────────────┘
```

L'ensemble du pipeline est **orchestré par Kestra** (déclenchement, enchaînement des étapes, monitoring des exécutions).

---

## Stack technique

| Composant | Technologie | Rôle |
|---|---|---|
| Langage de traitement | **Python 3** (pandas, openpyxl, psycopg2/SQLAlchemy, requests) | Nettoyage, génération des activités, calculs |
| Base de données | **PostgreSQL** | Stockage centralisé des données |
| Orchestration | **Kestra** | Automatisation et enchaînement du pipeline |
| Qualité des données | **Great Expectations** (ou tests Python) | Contrôles de validité |
| Géolocalisation | **API Google Maps** | Distance domicile -> entreprise |
| Notifications | **Slack (webhook)** | Publication automatique des activités |
| Visualisation | **Power BI Desktop** | Dashboard des KPI |
| Conteneurisation | **Docker / docker-compose** | Déploiement de PostgreSQL et Kestra |

---

## Structure du projet

```
sport-data-solution/
│
├── README.md                      # ce fichier
├── docker-compose.yml             # services PostgreSQL + Kestra
├── .env                           # variables d'environnement (non versionné)
│
├── data/
│   ├── Données RH.xlsx            # données RH sources
│   └── Données Sportive.xlsx      # sports déclarés par salarié
│
├── scripts/
│   ├── clean_data.py              # nettoyage des fichiers sources
│   ├── generate_activities.py     # générateur d'activités « Strava-like »
│   ├── load_postgres.py           # insertion des données en base
│   ├── quality_checks.py          # contrôles qualité
│   ├── compute_benefits.py        # calcul prime + jours bien-être
│   └── send_slack.py              # envoi des notifications Slack
│
├── kestra/
│   └── flow_pipeline.yml          # flow Kestra orchestrant le pipeline
│
├── powerbi/
│   └── sport_data_solution.pbix   # dashboard Power BI
│
└── captures_ecran/                # captures pour le rapport
```

> Adapter les noms de fichiers/dossiers à votre arborescence réelle si elle diffère.

### Variables d'environnement (`.env`)

```env
POSTGRES_HOST=localhost          # ou IP de la machine (ex. 192.168.1.149)
POSTGRES_PORT=5432
POSTGRES_DB=sport_db
POSTGRES_USER=sport_user
POSTGRES_PASSWORD=sport_password

GOOGLE_MAPS_API_KEY=xxxxxxxxxxxx
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
```

> Le fichier `.env` contient des secrets : il ne doit **jamais** être versionné (à ajouter au `.gitignore`).

---

## Installation et lancement

### Prérequis

- Docker + docker-compose
- Python 3.10+
- Power BI Desktop (Windows — ici exécuté dans une VM UTM sur Mac)
- Une clé API Google Maps et un webhook Slack

### 1. Cloner le projet et configurer l'environnement

```bash
git clone <url-du-repo>
cd sport-data-solution
cp .env.example .env    # puis renseigner les secrets
```

### 2. Lancer les services

```bash
docker compose up -d
```

Services démarrés :

- **PostgreSQL** : port `5432`
- **Kestra** : interface web sur `http://localhost:8080`

### 3. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 4. Exécuter le pipeline

**Option A — via Kestra (recommandé)** : importer `kestra/flow_pipeline.yml` dans l'interface Kestra puis exécuter le flow. Toutes les étapes s'enchaînent automatiquement.

**Option B — manuellement, script par script** :

```bash
python scripts/clean_data.py
python scripts/generate_activities.py
python scripts/load_postgres.py
python scripts/quality_checks.py
python scripts/compute_benefits.py
python scripts/send_slack.py
```

### 5. Connecter Power BI

Dans Power BI Desktop : **Obtenir des données > PostgreSQL**

- Serveur : `192.168.1.149:5432` (IP de la machine hébergeant PostgreSQL)
- Base de données : `sport_db`
- Utilisateur : `sport_user` / mot de passe : `sport_password`

Charger les tables `public.*` puis ouvrir `sport_data_solution.pbix`.

---

## Étapes du pipeline

| # | Étape | Outil | Description |
|---|---|---|---|
| 1 | Import des fichiers | Python | Lecture des fichiers `Données RH.xlsx` et `Données Sportive.xlsx` |
| 2 | Nettoyage | Python (pandas) | Normalisation des colonnes, types, valeurs manquantes |
| 3 | Génération des activités | Python | Simulation « Strava-like » de 5 000 à 10 000 activités sur 12 mois |
| 4 | Insertion en base | Python + SQL | Chargement des tables dans PostgreSQL |
| 5 | Contrôles qualité | Great Expectations / Python | Validation des données (voir section dédiée) |
| 6 | Vérification des distances | API Google Maps | Distance domicile -> entreprise vs mode déclaré |
| 7 | Calcul des avantages | SQL + Python | Prime 5 % et jours bien-être |
| 8 | Notifications | Webhook Slack | Publication des activités sur le canal Slack |
| 9 | Restitution | Power BI | Dashboard connecté à PostgreSQL |

L'orchestration complète (étapes 1 à 8) est définie dans `kestra/flow_pipeline.yml`.

---

## Modèle de données (PostgreSQL)

Base : `sport_db` — schéma `public`

| Table | Contenu |
|---|---|
| `employees` | Données RH nettoyées (id, nom, prénom, salaire, adresse, département, mode de déplacement…) |
| `sports` | Sport déclaré par salarié |
| `activities` | Activités sportives générées sur 12 mois |
| `quality_errors` | Anomalies détectées par les contrôles qualité |
| `benefits_summary` | Table finale : éligibilité prime, montant de la prime, jours bien-être, statut final par salarié |

Colonnes clés de `benefits_summary` : `id_employee`, `nom`, `prenom`, `department`, `salaire`, `sport`, `eligible_prime`, `montant_prime`, `nb_activites`, `jours_bien_etre`, `statut_final`.

---

## Contrôles qualité

Contrôles appliqués avant le calcul des avantages :

- **Intégrité** : chaque activité appartient à un salarié existant ; pas de doublons d'activités.
- **Cohérence temporelle** : `date_debut < date_fin` ; dates comprises dans les 12 derniers mois.
- **Valeurs** : `distance >= 0` ; `salaire > 0` ; pas de salaire vide ; sport connu pour chaque salarié sportif.
- **Cohérence métier (Google Maps)** : distance domicile -> entreprise compatible avec le mode de déplacement déclaré (Marche/Running ≤ 15 km, Vélo/Trottinette ≤ 25 km).

Les enregistrements en anomalie sont tracés dans la table `quality_errors` (et visibles dans le dashboard), ce qui permet d'auditer le pipeline sans bloquer l'exécution.

---

## Notifications Slack

À chaque activité générée, un message est publié automatiquement sur le canal Slack via **webhook**, par exemple :

> Bravo Juliette ! Tu viens de courir 10 km en 50 min

**Vérification du bon fonctionnement** : les messages apparaissent dans le canal Slack cible, et le statut HTTP `200` retourné par le webhook est loggé dans Kestra.

---

## Dashboard Power BI

Fichier : `sport_data_solution.pbix` — connecté à PostgreSQL (`sport_db`).

### Page « Vue d'ensemble »

**KPI (cartes)** :

- Nombre d'employés (nombre distinct de `id_employee`) — 161
- Salaire moyen (moyenne de `salaire`)
- Montant total des primes (somme de `montant_prime`)
- Nombre d'employés éligibles à la prime

**Graphiques** :

- Primes par département (`departement` × somme `montant_prime`)
- Répartition des sports pratiqués (`sport` × nombre `id_employee`)
- Salaire moyen par département (`departement` × moyenne `salaire`) — permet de croiser salaires et primes pour une lecture RH

### Exports

- `sport_data_solution.pbix` — fichier source Power BI
- `sport_data_solution.pdf` — export PDF du rapport (bonus, lecture facile)

---

## Monitoring

Le monitoring du pipeline est assuré par **Kestra**, qui fournit nativement :

- statut de chaque exécution (succès / erreur) ;
- temps d'exécution de chaque étape ;
- historique complet des runs ;
- logs détaillés par tâche.

Métriques métier complémentaires suivies :

- nombre d'activités traitées par run ;
- nombre de salariés éligibles (prime / jours bien-être) ;
- coût total des primes ;
- nombre d'anomalies détectées (`quality_errors`).

---

## Livrables

- `README.md` — documentation du projet
- Diagramme d'architecture du pipeline
- `docker-compose.yml` — infrastructure (PostgreSQL + Kestra)
- Scripts Python (nettoyage, génération, chargement, qualité, calculs, Slack)
- `flow_pipeline.yml` — orchestration Kestra
- `sport_data_solution.pbix` — dashboard Power BI
- `captures_ecran/` — preuves de fonctionnement (Kestra, Slack, Power BI)

---

## Pistes d'amélioration

- Remplacer le générateur simulé par une **vraie intégration API Strava** (OAuth).
- Planifier le pipeline en exécution **quotidienne** automatique dans Kestra (trigger cron).
- Ajouter des **alertes Slack** en cas d'échec du pipeline ou d'anomalies qualité.
- Historiser les calculs d'avantages pour un suivi pluriannuel.
- Publier le dashboard sur **Power BI Service** pour un partage en ligne.
- Mettre en place un **CI/CD** (tests automatisés des scripts à chaque commit).

---

## Auteur

Projet réalisé par **Aime** — parcours Data Engineer, OpenClassrooms (2026).
