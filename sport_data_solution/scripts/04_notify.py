import os
import requests
from utils import get_connection, logger

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def build_message(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                a.sport,
                COUNT(DISTINCT a.id_employe) AS nb_participants,
                ROUND(SUM(a.distance_km)::numeric, 1) AS total_km,
                COUNT(b.id_employe) FILTER (WHERE b.eligible_prime) AS nb_eligibles
            FROM activities a
            LEFT JOIN benefits b ON a.id_employe = b.id_employe
            GROUP BY a.sport
            ORDER BY nb_participants DESC;
            """
        )
        rows = cur.fetchall()

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM benefits WHERE eligible_prime = TRUE;")
        total_eligibles = cur.fetchone()[0]
        cur.execute("SELECT COALESCE(SUM(montant_prime), 0) FROM benefits;")
        total_prime = cur.fetchone()[0]

    lines = ["*Rapport Sport Data Solution*", ""]
    for sport, nb_part, total_km, nb_elig in rows:
        lines.append(f"• *{sport}* : {nb_part} participants, {total_km} km")
    lines.append("")
    lines.append(f"Employés éligibles à la prime : *{total_eligibles}*")
    lines.append(f"Coût total primes entreprise : *{total_prime:.2f} €*")

    return "\n".join(lines)


def send_slack(message):
    if not SLACK_WEBHOOK_URL or SLACK_WEBHOOK_URL.startswith("https://hooks.slack.com/services/XXXX"):
        logger.warning("SLACK_WEBHOOK_URL non configurée — notification ignorée.")
        return
    resp = requests.post(SLACK_WEBHOOK_URL, json={"text": message}, timeout=10)
    if resp.status_code == 200:
        logger.info("Notification Slack envoyée.")
    else:
        logger.error(f"Erreur Slack : {resp.status_code} {resp.text}")


def run():
    logger.info("=== 04_notify : démarrage ===")
    conn = get_connection()
    try:
        message = build_message(conn)
        logger.info(f"Message Slack :\n{message}")
        send_slack(message)
    finally:
        conn.close()
    logger.info("=== 04_notify : terminé ===")


if __name__ == "__main__":
    run()
