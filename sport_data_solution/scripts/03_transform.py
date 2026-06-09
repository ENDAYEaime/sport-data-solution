import os
import pandas as pd
from utils import get_connection, logger

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

# Règles métier
PRIME_RATE = 0.05          # 5% du salaire
MIN_SESSIONS = 3           # sessions/mois pour être éligible
WELLBEING_DAYS = 2         # jours bien-être accordés si éligible


def compute_benefits(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                e.id_employe,
                e.nom,
                e.prenom,
                e.salaire,
                COUNT(a.id) AS nb_sessions,
                SUM(a.distance_km) AS total_km
            FROM employees e
            LEFT JOIN activities a ON e.id_employe = a.id_employe
            GROUP BY e.id_employe, e.nom, e.prenom, e.salaire;
            """
        )
        rows = cur.fetchall()

    results = []
    for id_employe, nom, prenom, salaire, nb_sessions, total_km in rows:
        nb_sessions = nb_sessions or 0
        total_km = total_km or 0
        eligible = nb_sessions >= MIN_SESSIONS
        prime = round(float(salaire) * PRIME_RATE, 2) if eligible else 0.0
        jours_bienetre = WELLBEING_DAYS if eligible else 0
        results.append((id_employe, eligible, prime, jours_bienetre, int(nb_sessions), float(total_km)))

    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE benefits;")
        for row in results:
            cur.execute(
                """
                INSERT INTO benefits (id_employe, eligible_prime, montant_prime, jours_bienetre, nb_sessions, total_km)
                VALUES (%s, %s, %s, %s, %s, %s);
                """,
                row,
            )
    conn.commit()
    logger.info(f"{len(results)} avantages calculés.")
    return results


def export_csv(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                e.id_employe, e.nom, e.prenom, e.departement,
                b.eligible_prime, b.montant_prime, b.jours_bienetre,
                b.nb_sessions, b.total_km
            FROM employees e
            JOIN benefits b ON e.id_employe = b.id_employe
            ORDER BY e.departement, e.nom;
            """
        )
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]

    df = pd.DataFrame(rows, columns=cols)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    out_path = os.path.join(PROCESSED_DIR, "avantages_sport.csv")
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    logger.info(f"Export CSV : {out_path}")


def run():
    logger.info("=== 03_transform : démarrage ===")
    conn = get_connection()
    try:
        compute_benefits(conn)
        export_csv(conn)
    finally:
        conn.close()
    logger.info("=== 03_transform : terminé ===")


if __name__ == "__main__":
    run()
