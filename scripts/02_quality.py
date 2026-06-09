import pandas as pd
from utils import get_connection, logger


def check_duplicates(conn):
    rows = []
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id_employe, COUNT(*) as nb
            FROM employees
            GROUP BY id_employe
            HAVING COUNT(*) > 1;
            """
        )
        rows = cur.fetchall()
    for id_employe, nb in rows:
        log_error(conn, id_employe, "doublon_employe", f"{nb} occurrences")
    logger.info(f"Doublons employés : {len(rows)}")


def check_nulls(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id_employe FROM employees
            WHERE nom IS NULL OR prenom IS NULL OR salaire IS NULL OR departement IS NULL;
            """
        )
        rows = cur.fetchall()
    for (id_employe,) in rows:
        log_error(conn, id_employe, "valeur_nulle", "champ obligatoire manquant")
    logger.info(f"Employés avec valeurs nulles : {len(rows)}")


def check_negative_salaries(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id_employe, salaire FROM employees WHERE salaire <= 0;")
        rows = cur.fetchall()
    for id_employe, salaire in rows:
        log_error(conn, id_employe, "salaire_invalide", f"salaire={salaire}")
    logger.info(f"Salaires négatifs/nuls : {len(rows)}")


def check_dates(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id_employe, date_embauche FROM employees
            WHERE date_embauche > CURRENT_DATE OR date_embauche < '1970-01-01';
            """
        )
        rows = cur.fetchall()
    for id_employe, date in rows:
        log_error(conn, id_employe, "date_invalide", f"date_embauche={date}")
    logger.info(f"Dates d'embauche invalides : {len(rows)}")


def check_distances(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id_employe, sport, distance_km FROM activities
            WHERE distance_km < 0 OR distance_km > 500;
            """
        )
        rows = cur.fetchall()
    for id_employe, sport, dist in rows:
        log_error(conn, id_employe, "distance_invalide", f"sport={sport}, distance={dist}km")
    logger.info(f"Distances incohérentes : {len(rows)}")


def log_error(conn, id_employe, type_erreur, detail):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO quality_errors (id_employe, type_erreur, detail)
            VALUES (%s, %s, %s);
            """,
            (id_employe, type_erreur, detail),
        )
    conn.commit()


def run():
    logger.info("=== 02_quality : démarrage ===")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE quality_errors;")
        conn.commit()
        check_duplicates(conn)
        check_nulls(conn)
        check_negative_salaries(conn)
        check_dates(conn)
        check_distances(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM quality_errors;")
            total = cur.fetchone()[0]
        logger.info(f"Total erreurs qualité détectées : {total}")
    finally:
        conn.close()
    logger.info("=== 02_quality : terminé ===")


if __name__ == "__main__":
    run()
