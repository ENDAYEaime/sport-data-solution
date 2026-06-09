import os
import pandas as pd
from utils import get_connection, logger

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
RH_FILE = os.path.join(RAW_DIR, "RH.xlsx")
SPORT_FILE = os.path.join(RAW_DIR, "Sport.xlsx")


def load_employees(conn):
    df = pd.read_excel(RH_FILE)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df = df.dropna(subset=["id_employe"])
    df["id_employe"] = df["id_employe"].astype(str).str.strip()

    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE employees RESTART IDENTITY CASCADE;")
        for _, row in df.iterrows():
            cur.execute(
                """
                INSERT INTO employees (id_employe, nom, prenom, departement, poste, salaire, date_embauche)
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
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df = df.dropna(subset=["id_employe"])
    df["id_employe"] = df["id_employe"].astype(str).str.strip()

    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE activities RESTART IDENTITY CASCADE;")
        for _, row in df.iterrows():
            cur.execute(
                """
                INSERT INTO activities (id_employe, sport, distance_km, duree_min, date_activite)
                VALUES (%s, %s, %s, %s, %s);
                """,
                (
                    row.get("id_employe"),
                    row.get("sport"),
                    row.get("distance_km"),
                    row.get("duree_min"),
                    row.get("date_activite"),
                ),
            )
    conn.commit()
    logger.info(f"{len(df)} activités sportives insérées.")
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
