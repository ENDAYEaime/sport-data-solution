-- Schéma Sport Data Solution

CREATE TABLE IF NOT EXISTS employees (
    id          SERIAL PRIMARY KEY,
    id_employe  VARCHAR(50) UNIQUE NOT NULL,
    nom         VARCHAR(100),
    prenom      VARCHAR(100),
    departement VARCHAR(100),
    poste       VARCHAR(100),
    salaire     NUMERIC(10, 2),
    date_embauche DATE
);

CREATE TABLE IF NOT EXISTS sports (
    id    SERIAL PRIMARY KEY,
    nom   VARCHAR(100) UNIQUE NOT NULL,
    type  VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS activities (
    id             SERIAL PRIMARY KEY,
    id_employe     VARCHAR(50) REFERENCES employees(id_employe) ON DELETE CASCADE,
    sport          VARCHAR(100),
    distance_km    NUMERIC(8, 2),
    duree_min      INTEGER,
    date_activite  DATE
);

CREATE TABLE IF NOT EXISTS benefits (
    id              SERIAL PRIMARY KEY,
    id_employe      VARCHAR(50) REFERENCES employees(id_employe) ON DELETE CASCADE,
    eligible_prime  BOOLEAN DEFAULT FALSE,
    montant_prime   NUMERIC(10, 2) DEFAULT 0,
    jours_bienetre  INTEGER DEFAULT 0,
    nb_sessions     INTEGER DEFAULT 0,
    total_km        NUMERIC(10, 2) DEFAULT 0,
    calcule_le      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS quality_errors (
    id           SERIAL PRIMARY KEY,
    id_employe   VARCHAR(50),
    type_erreur  VARCHAR(100),
    detail       TEXT,
    detecte_le   TIMESTAMP DEFAULT NOW()
);
