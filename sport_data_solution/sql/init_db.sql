-- Schéma Sport Data Solution - POC simplifié

DROP TABLE IF EXISTS quality_errors;
DROP TABLE IF EXISTS benefits_summary;
DROP TABLE IF EXISTS sports;
DROP TABLE IF EXISTS employees;

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    id_employe VARCHAR(50) UNIQUE NOT NULL,
    nom VARCHAR(100),
    prenom VARCHAR(100),
    departement VARCHAR(100),
    poste VARCHAR(100),
    salaire NUMERIC(10, 2),
    date_embauche DATE
);

CREATE TABLE sports (
    id SERIAL PRIMARY KEY,
    id_employe VARCHAR(50) UNIQUE NOT NULL REFERENCES employees(id_employe) ON DELETE CASCADE,
    sport VARCHAR(100)
);

CREATE TABLE benefits_summary (
    id SERIAL PRIMARY KEY,
    id_employe VARCHAR(50) UNIQUE NOT NULL REFERENCES employees(id_employe) ON DELETE CASCADE,
    nom VARCHAR(100),
    prenom VARCHAR(100),
    departement VARCHAR(100),
    salaire NUMERIC(10, 2),
    sport VARCHAR(100),
    eligible_prime BOOLEAN DEFAULT FALSE,
    montant_prime NUMERIC(10, 2) DEFAULT 0,
    eligible_bien_etre BOOLEAN DEFAULT FALSE,
    jours_bien_etre INTEGER DEFAULT 0,
    statut_final VARCHAR(100),
    calcule_le TIMESTAMP DEFAULT NOW()
);

CREATE TABLE quality_errors (
    id SERIAL PRIMARY KEY,
    id_employe VARCHAR(50),
    type_erreur VARCHAR(100),
    detail TEXT,
    detecte_le TIMESTAMP DEFAULT NOW()
);