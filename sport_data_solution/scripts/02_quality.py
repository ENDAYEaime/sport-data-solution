from utils import get_connection, logger


def log_error(conn, id_employe, type_erreur, detail):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO quality_errors (id_employe, type_erreur, detail)
            VALUES (%s, %s, %s);
            """,
            (id_employe, type_erreur, detail),
        )


def check_duplicates(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id_employe, COUNT(*) AS nb
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
            SELECT id_employe
            FROM employees
            WHERE nom IS NULL
               OR prenom IS NULL
               OR salaire IS NULL
               OR departement IS NULL;
            """
        )
        rows = cur.fetchall()

    for (id_employe,) in rows:
        log_error(conn, id_employe, "valeur_nulle", "champ obligatoire manquant")

    logger.info(f"Employés avec valeurs nulles : {len(rows)}")


def check_negative_salaries(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id_employe, salaire
            FROM employees
            WHERE salaire <= 0;
            """
        )
        rows = cur.fetchall()

    for id_employe, salaire in rows:
        log_error(conn, id_employe, "salaire_invalide", f"salaire={salaire}")

    logger.info(f"Salaires négatifs/nuls : {len(rows)}")


def check_dates(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id_employe, date_embauche
            FROM employees
            WHERE date_embauche > CURRENT_DATE
               OR date_embauche < '1970-01-01';
            """
        )
        rows = cur.fetchall()

    for id_employe, date_embauche in rows:
        log_error(conn, id_employe, "date_invalide", f"date_embauche={date_embauche}")

    logger.info(f"Dates d'embauche invalides : {len(rows)}")


def check_sports_without_employee(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT s.id_employe
            FROM sports s
            LEFT JOIN employees e
                ON s.id_employe = e.id_employe
            WHERE e.id_employe IS NULL;
            """
        )
        rows = cur.fetchall()

    for (id_employe,) in rows:
        log_error(conn, id_employe, "sport_sans_employe", "sport associé à aucun salarié RH")

    logger.info(f"Sports sans employé correspondant : {len(rows)}")


def check_empty_sports(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id_employe
            FROM sports
            WHERE sport IS NULL
               OR TRIM(sport) = '';
            """
        )
        rows = cur.fetchall()

    for (id_employe,) in rows:
        log_error(conn, id_employe, "sport_vide", "aucun sport renseigné")

    logger.info(f"Sports vides : {len(rows)}")


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
        check_sports_without_employee(conn)
        check_empty_sports(conn)

        conn.commit()

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM quality_errors;")
            total = cur.fetchone()[0]

        logger.info(f"Total erreurs qualité détectées : {total}")

    finally:
        conn.close()

    logger.info("=== 02_quality : terminé ===")


if __name__ == "__main__":
    run()