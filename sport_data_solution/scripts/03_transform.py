import os
import pandas as pd
from utils import get_connection, logger

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

PRIME_RATE = 0.05
WELLBEING_DAYS = 5


def compute_benefits(conn):
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE benefits_summary;")

        cur.execute(
            """
            INSERT INTO benefits_summary (
                id_employe,
                nom,
                prenom,
                departement,
                salaire,
                sport,
                eligible_prime,
                montant_prime,
                eligible_bien_etre,
                jours_bien_etre,
                statut_final
            )
            SELECT
                e.id_employe,
                e.nom,
                e.prenom,
                e.departement,
                e.salaire,
                s.sport,

                CASE
                    WHEN s.sport IS NOT NULL
                     AND TRIM(s.sport) <> ''
                     AND LOWER(TRIM(s.sport)) NOT IN ('non', 'aucun', 'none', 'nan')
                    THEN TRUE
                    ELSE FALSE
                END AS eligible_prime,

                CASE
                    WHEN s.sport IS NOT NULL
                     AND TRIM(s.sport) <> ''
                     AND LOWER(TRIM(s.sport)) NOT IN ('non', 'aucun', 'none', 'nan')
                    THEN ROUND((e.salaire * %s)::numeric, 2)
                    ELSE 0
                END AS montant_prime,

                CASE
                    WHEN s.sport IS NOT NULL
                     AND TRIM(s.sport) <> ''
                     AND LOWER(TRIM(s.sport)) NOT IN ('non', 'aucun', 'none', 'nan')
                    THEN TRUE
                    ELSE FALSE
                END AS eligible_bien_etre,

                CASE
                    WHEN s.sport IS NOT NULL
                     AND TRIM(s.sport) <> ''
                     AND LOWER(TRIM(s.sport)) NOT IN ('non', 'aucun', 'none', 'nan')
                    THEN %s
                    ELSE 0
                END AS jours_bien_etre,

                CASE
                    WHEN s.sport IS NOT NULL
                     AND TRIM(s.sport) <> ''
                     AND LOWER(TRIM(s.sport)) NOT IN ('non', 'aucun', 'none', 'nan')
                    THEN 'Prime + jours bien-être'
                    ELSE 'Aucun avantage'
                END AS statut_final

            FROM employees e
            LEFT JOIN sports s
                ON e.id_employe = s.id_employe;
            """,
            (PRIME_RATE, WELLBEING_DAYS),
        )

    conn.commit()
    logger.info("Table benefits_summary calculée.")


def export_csv(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM benefits_summary
            ORDER BY departement, nom, prenom;
            """
        )
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]

    df = pd.DataFrame(rows, columns=cols)

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    out_path = os.path.join(PROCESSED_DIR, "benefits_summary.csv")
    df.to_csv(out_path, index=False, encoding="utf-8-sig")

    logger.info(f"Export CSV créé : {out_path}")


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