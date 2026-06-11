-- Salariés éligibles à la prime
SELECT
    id_employe,
    nom,
    prenom,
    departement,
    salaire,
    sport,
    montant_prime,
    jours_bien_etre,
    statut_final
FROM benefits_summary
WHERE eligible_prime = TRUE
ORDER BY montant_prime DESC;


-- Coût total des primes par département
SELECT
    departement,
    COUNT(id_employe) AS nb_eligibles,
    SUM(montant_prime) AS cout_total
FROM benefits_summary
WHERE eligible_prime = TRUE
GROUP BY departement
ORDER BY cout_total DESC;


-- Répartition des sports
SELECT
    sport,
    COUNT(id_employe) AS nb_salaries
FROM benefits_summary
WHERE sport IS NOT NULL
  AND TRIM(sport) <> ''
GROUP BY sport
ORDER BY nb_salaries DESC;


-- Résumé complet par salarié
SELECT
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
FROM benefits_summary
ORDER BY departement, nom, prenom;


-- Erreurs qualité détectées
SELECT
    type_erreur,
    COUNT(*) AS nb,
    MAX(detecte_le) AS derniere_detection
FROM quality_errors
GROUP BY type_erreur
ORDER BY nb DESC;