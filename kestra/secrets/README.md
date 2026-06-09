# Secrets Kestra

Configurer ces secrets dans l'interface Kestra (Settings > Secrets) :

| Clé                  | Description                        |
|----------------------|------------------------------------|
| `POSTGRES_HOST`      | Hôte PostgreSQL                    |
| `POSTGRES_PORT`      | Port PostgreSQL (5432)             |
| `POSTGRES_DB`        | Nom de la base de données          |
| `POSTGRES_USER`      | Utilisateur PostgreSQL             |
| `POSTGRES_PASSWORD`  | Mot de passe PostgreSQL            |
| `SLACK_WEBHOOK_URL`  | URL du webhook Slack               |

Ne jamais stocker de secrets en clair dans ce dossier.
