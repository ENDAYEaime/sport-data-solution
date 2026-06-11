import os
import pandas as pd
from utils import get_connection, logger

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

RH_FILE = os.path.join(RAW_DIR, "Données+RH.xlsx")
SPORT_FILE = os.path.join(RAW_DIR, "Données+Sportive.xlsx")


RH_COL_MAP = {
    "id_salarié": "id_employe",
    "prénom": "prenom",
    "bu": "departement",
    "salaire_brut": "salaire",
    "date_d'embauche": "date_embauche",
}


SPORT_COL_MAP = {
    "id_salarié": "id_employe",
    "pratique_d'un_sport": "sport",
}


def clean_columns(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df


def load_employees(conn):
    df = pd.read_excel(RH_FILE)
    df = clean_columns(df)
    df = df.rename(columns=RH_COL_MAP)

    df = df.dropna(subset=["id_employe"])
    df["id_employe"] = df["id_employe"].astype(str).str.strip()

    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE employees RESTART IDENTITY CASCADE;")

        for _, row in df.iterrows():
            cur.execute(
                """
                INSERT INTO employees
                (id_employe, nom, prenom, departement, poste, salaire, date_embauche)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id_employe) DO UPDATE SET
                    nom = EXCLUDED.nom,
                    prenom = EXCLUDED.prenom,
                    departement = EXCLUDED.departement,
                    poste = EXCLUDED.poste,
                    salaire = EXCLUDED.salaire,
                    date_embauche = EXCLUDED.date_embauche;
                """,
                (
                    row.get("id_employe"),
                    row.get("nom"),
                    row.get("prenom"),
                    row.get("departement"),
                    row.get("poste"),
                    row.get("salaire"),
                    row.get("date_embauche"),
                ),
            )

    conn.commit()
    logger.info(f"{len(df)} employés insérés.")
    return df


def load_sports(conn):
    df = pd.read_excel(SPORT_FILE)
    df = clean_columns(df)
    df = df.rename(columns=SPORT_COL_MAP)

    df = df.dropna(subset=["id_employe"])
    df["id_employe"] = df["id_employe"].astype(str).str.strip()

    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE sports RESTART IDENTITY CASCADE;")

        for _, row in df.iterrows():
            cur.execute(
                """
                INSERT INTO sports
                (id_employe, sport)
                VALUES (%s, %s)
                ON CONFLICT (id_employe) DO UPDATE SET
                    sport = EXCLUDED.sport;
                """,
                (
                    row.get("id_employe"),
                    row.get("sport"),
                ),
            )

    conn.commit()
    logger.info(f"{len(df)} sports insérés.")
    return df


def run():
    logger.info("=== 01_ingest : démarrage ===")

    conn = get_connection()

    try:
        load_employees(conn)
        load_sports(conn)
    finally:
        conn.close()

    logger.info("=== 01_ingest : terminé ===")


if __name__ == "__main__":
    run()