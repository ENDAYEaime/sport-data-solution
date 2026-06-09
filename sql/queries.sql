-- Employés éligibles à la prime
SELECT
    e.id_employe,
    e.nom,
    e.prenom,
    e.departement,
    b.nb_sessions,
    b.total_km,
    b.montant_prime,
    b.jours_bienetre
FROM employees e
JOIN benefits b ON e.id_employe = b.id_employe
WHERE b.eligible_prime = TRUE
ORDER BY b.montant_prime DESC;

-- Coût total des primes par département
SELECT
    e.departement,
    COUNT(b.id_employe) AS nb_eligibles,
    SUM(b.montant_prime) AS cout_total
FROM employees e
JOIN benefits b ON e.id_employe = b.id_employe
WHERE b.eligible_prime = TRUE
GROUP BY e.departement
ORDER BY cout_total DESC;

-- Statistiques par sport
SELECT
    sport,
    COUNT(DISTINCT id_employe) AS nb_participants,
    ROUND(AVG(distance_km), 1) AS distance_moy_km,
    ROUND(AVG(duree_min), 0) AS duree_moy_min,
    SUM(distance_km) AS total_km
FROM activities
GROUP BY sport
ORDER BY nb_participants DESC;

-- Résumé par employé (sessions, km, prime)
SELECT
    e.id_employe,
    e.nom,
    e.prenom,
    e.salaire,
    b.nb_sessions,
    b.total_km,
    b.eligible_prime,
    b.montant_prime,
    b.jours_bienetre
FROM employees e
LEFT JOIN benefits b ON e.id_employe = b.id_employe
ORDER BY e.departement, e.nom;

-- Erreurs qualité en attente
SELECT type_erreur, COUNT(*) AS nb, MAX(detecte_le) AS derniere_detection
FROM quality_errors
GROUP BY type_erreur
ORDER BY nb DESC;
