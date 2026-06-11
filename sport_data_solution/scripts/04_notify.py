import os
import requests
from utils import get_connection, logger

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def build_message(conn):

    with conn.cursor() as cur:

        cur.execute(
            """
            SELECT COUNT(*)
            FROM benefits_summary
            WHERE eligible_prime = TRUE;
            """
        )
        total_eligibles = cur.fetchone()[0]

        cur.execute(
            """
            SELECT COALESCE(SUM(montant_prime), 0)
            FROM benefits_summary;
            """
        )
        total_primes = cur.fetchone()[0]

        cur.execute(
            """
            SELECT sport, COUNT(*)
            FROM benefits_summary
            WHERE sport IS NOT NULL
            GROUP BY sport
            ORDER BY COUNT(*) DESC;
            """
        )
        sports = cur.fetchall()

    lines = [
        "🏃 Rapport Sport Data Solution",
        "",
        f"Employés éligibles à la prime : {total_eligibles}",
        f"Coût total des primes : {float(total_primes):.2f} €",
        "",
        "Sports pratiqués :"
    ]

    for sport, nb in sports:
        lines.append(f"• {sport} : {nb} salarié(s)")

    return "\n".join(lines)


def send_slack(message):

    if (
        not SLACK_WEBHOOK_URL
        or SLACK_WEBHOOK_URL.startswith(
            "https://hooks.slack.com/services/XXXX"
        )
    ):
        logger.warning(
            "SLACK_WEBHOOK_URL non configurée - notification ignorée."
        )
        return

    response = requests.post(
        SLACK_WEBHOOK_URL,
        json={"text": message},
        timeout=10
    )

    if response.status_code == 200:
        logger.info("Notification Slack envoyée.")
    else:
        logger.error(
            f"Erreur Slack : {response.status_code} {response.text}"
        )


def run():

    logger.info("=== 04_notify : démarrage ===")

    conn = get_connection()

    try:
        message = build_message(conn)

        logger.info(
            f"Message Slack généré :\n{message}"
        )

        send_slack(message)

    finally:
        conn.close()

    logger.info("=== 04_notify : terminé ===")


if __name__ == "__main__":
    run()