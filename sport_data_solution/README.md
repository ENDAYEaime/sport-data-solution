# Sport Data Solution

Pipeline de données RH et sportives : ingestion, contrôle qualité, calcul des avantages et notifications Slack.

## Architecture

```
sport_data_solution/
├── data/raw/          # Fichiers sources xlsx (RH + Sport)
├── data/processed/    # Exports CSV après transformation
├── scripts/           # Pipeline Python (01 → 02 → 03 → 04)
├── sql/               # Schéma de la base et requêtes métier
├── kestra/            # Orchestration des flows
└── powerbi/           # Rapport de visualisation
```

## Prérequis

- Docker & Docker Compose
- Python 3.11+
- Power BI Desktop (Windows)

## Installation

```bash
# 1. Copier et configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos identifiants

# 2. Démarrer PostgreSQL et Kestra
docker-compose up -d

# 3. Installer les dépendances Python
python -m venv venv
source venv/bin/activate   # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

## Lancement du pipeline

```bash
# Exécution manuelle complète
python scripts/main.py

# Ou étape par étape
python scripts/01_ingest.py
python scripts/02_quality.py
python scripts/03_transform.py
python scripts/04_notify.py
```

## Pipeline

| Étape | Script | Description |
|-------|--------|-------------|
| 1 | `01_ingest.py` | Lecture xlsx, nettoyage Pandas, insertion en base |
| 2 | `02_quality.py` | Contrôles qualité (doublons, nulls, cohérence) |
| 3 | `03_transform.py` | Calcul prime 5%, jours bien-être, avantages |
| 4 | `04_notify.py` | Notifications Slack par activité sportive |

## Kestra

Accéder à l'interface Kestra : http://localhost:8080

Les flows se trouvent dans `kestra/` et sont montés automatiquement.
