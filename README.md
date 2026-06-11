# Sport Data Solution — POC Avantages Sportifs

Pipeline de données automatisé pour calculer et attribuer des avantages salariés liés à la pratique sportive.  
Projet réalisé dans le cadre du parcours **Data Engineer — OpenClassrooms (2026)**.

---

## Contexte

L'entreprise Sport Data Solution souhaite encourager la pratique sportive de ses salariés en mettant en place deux avantages :

- une **prime sportive** pour les salariés se rendant au travail par un moyen de déplacement sportif ;
- des **journées bien-être** pour les salariés pratiquant une activité sportive régulière.

Ce POC démontre la faisabilité technique d'un pipeline de données end-to-end : ingestion des fichiers RH, simulation d'un historique d'activités sportives sur 12 mois, contrôles qualité, calcul des avantages, notification Slack et restitution dans un dashboard Power BI.

---

## Règles métier

| Avantage | Condition | Valeur |
|---|---|---|
| Prime sportive | Venir au bureau en mode de déplacement sportif (marche, running, vélo, trottinette) | 5 % du salaire brut annuel |
| Journées bien-être | Au moins 15 activités sportives déclarées sur les 12 derniers mois | 5 jours de congé supplémentaires |

La cohérence du mode de déplacement déclaré est vérifiée via l'API Google Maps :

| Mode déclaré | Distance domicile-bureau maximale |
|---|---|
| Marche / Running | 15 km |
| Vélo / Trottinette | 25 km |

---

## Architecture du pipeline

```
Données RH.xlsx          Données Sportive.xlsx
       |                         |
       +------------+------------+
                    |
              Python (pandas)
          Nettoyage + génération
         activités sur 12 mois
                    |
               PostgreSQL
           Stockage centralisé
                    |
           Contrôles qualité
         (Great Expectations)
                    |
          Calcul des avantages
          Prime 5 % + 5 jours
                    |
          +---------+---------+
          |                   |
        Slack             Power BI
    Notifications         Dashboard
```

L'ensemble du pipeline est orchestré par **Kestra**.

---

## Stack technique

| Composant | Technologie |
|---|---|
| Traitement des données | Python 3 (pandas, openpyxl, psycopg2, requests) |
| Base de données | PostgreSQL |
| Orchestration | Kestra |
| Qualité des données | Great Expectations / tests Python |
| Géolocalisation | API Google Maps |
| Notifications | Slack (webhook) |
| Visualisation | Power BI Desktop |
| Conteneurisation | Docker / docker-compose |

---

## Structure du projet

```
sport_data_solution/
├── docker-compose.yml          # services PostgreSQL + Kestra
├── requirements.txt
├── data/
│   ├── raw/                    # fichiers sources Excel
│   └── processed/              # résultats après traitement
├── scripts/
│   ├── 01_ingest.py            # ingestion et nettoyage des sources
│   ├── 02_quality.py           # contrôles qualité
│   ├── 03_transform.py         # calcul des avantages
│   ├── 04_notify.py            # notifications Slack
│   ├── main.py                 # point d'entrée du pipeline
│   └── utils.py                # fonctions utilitaires partagées
├── kestra/
│   └── flow_pipeline.yml       # orchestration Kestra
└── sql/
    ├── init_db.sql             # création des tables PostgreSQL
    └── queries.sql             # requêtes analytiques
```

---

## Installation et lancement

### Prérequis

- Docker et docker-compose
- Python 3.10+
- Une clé API Google Maps
- Un webhook Slack

### 1. Cloner le projet

```bash
git clone https://github.com/ENDAYEaime/sport-data-solution.git
cd sport-data-solution/sport_data_solution
```

### 2. Configurer les variables d'environnement

Créer un fichier `.env` à la racine de `sport_data_solution/` :

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=sport_db
POSTGRES_USER=sport_user
POSTGRES_PASSWORD=sport_password

GOOGLE_MAPS_API_KEY=votre_cle_api
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
```

### 3. Lancer les services

```bash
docker compose up -d
```

Démarre PostgreSQL (port 5432) et Kestra (interface web sur `http://localhost:8080`).

### 4. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 5. Exécuter le pipeline

**Via Kestra (recommandé)** : importer `kestra/flow_pipeline.yml` dans l'interface Kestra puis déclencher le flow.

**Manuellement** :

```bash
python scripts/main.py
```

---

## Modèle de données

Base : `sport_db` — schéma `public`

| Table | Contenu |
|---|---|
| `employees` | Données RH nettoyées (id, nom, prénom, salaire, adresse, département, mode de déplacement) |
| `sports` | Sport déclaré par salarié |
| `activities` | Activités sportives simulées sur 12 mois |
| `quality_errors` | Anomalies détectées lors des contrôles qualité |
| `benefits_summary` | Résultat final : éligibilité, montant de la prime, jours bien-être par salarié |

---

## Étapes du pipeline

| Etape | Script | Description |
|---|---|---|
| 1. Ingestion | `01_ingest.py` | Lecture et nettoyage des fichiers RH et sportifs, génération des activités |
| 2. Qualité | `02_quality.py` | Contrôles d'intégrité, cohérence temporelle, validation métier via Google Maps |
| 3. Calcul | `03_transform.py` | Attribution de la prime sportive et des journées bien-être |
| 4. Notification | `04_notify.py` | Publication automatique des activités sur Slack |

---

## Contrôles qualité

- Intégrité référentielle : chaque activité appartient à un salarié existant, pas de doublons.
- Cohérence temporelle : `date_debut < date_fin`, dates dans les 12 derniers mois.
- Valeurs : `distance >= 0`, `salaire > 0`, sport renseigné pour chaque salarié sportif.
- Cohérence métier : distance domicile-entreprise compatible avec le mode de déplacement déclaré (via API Google Maps).

Les anomalies sont tracées dans la table `quality_errors` sans bloquer l'exécution du pipeline.

---

## Auteur

Projet réalisé par **Aime ENDAYE** — parcours Data Engineer, OpenClassrooms (2026).
