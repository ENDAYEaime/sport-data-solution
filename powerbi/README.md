# Power BI - Rapport Sport Data Solution

## Connexion PostgreSQL

1. Ouvrir Power BI Desktop
2. Obtenir les données > Base de données PostgreSQL
3. Serveur : `localhost:5432`
4. Base de données : valeur de `POSTGRES_DB` dans votre `.env`
5. Importer les tables : `employees`, `benefits`, `activities`, `quality_errors`

## KPIs à créer

- **Taux d'éligibilité** : % employés éligibles à la prime
- **Coût total primes** : somme des montants par département
- **Top sports** : classement par nombre de participants
- **Km parcourus** : total et moyenne par sport
- **Erreurs qualité** : répartition par type d'erreur

## Rapport

Créer le fichier `rapport_sport.pbix` dans ce dossier après connexion.
