-- Schéma de la base veloville (PostgreSQL 14+).
-- Conforme au dictionnaire des données et aux règles de gestion (RG1 à RG8).
-- Le script est rejouable (DROP ... CASCADE).

-- Nettoyage pour rendre le script rejouable
DROP TABLE IF EXISTS incident CASCADE;
DROP TABLE IF EXISTS trajet CASCADE;
DROP TABLE IF EXISTS station CASCADE;
DROP TABLE IF EXISTS utilisateur CASCADE;

-- ---------------------------------------------------------------
-- 1. Table station
-- ---------------------------------------------------------------
CREATE TABLE station (
    station_id VARCHAR(10) PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    commune VARCHAR(100) NOT NULL,
    capacite INT NOT NULL CHECK (capacite > 0), -- capacité > 0
    latitude DECIMAL(8, 5) NOT NULL,            -- Coordonnée WGS84 (5 décimales)
    longitude DECIMAL(8, 5) NOT NULL,           -- Coordonnée WGS84 (5 décimales)
    date_mise_en_service DATE NOT NULL          -- Date d'ouverture de station
);

-- ---------------------------------------------------------------
-- 2. Table trajet
-- ---------------------------------------------------------------
CREATE TABLE trajet (
    trajet_id VARCHAR(12) PRIMARY KEY,
    velo_id VARCHAR(8) NOT NULL,               -- Format V + 4 chiffres
    depart_horodatage TIMESTAMP NOT NULL,
    station_depart VARCHAR(10) NOT NULL REFERENCES station(station_id) ON DELETE RESTRICT, -- obligatoire
    station_arrivee VARCHAR(10) REFERENCES station(station_id) ON DELETE RESTRICT,        -- facultative (si non restitué)
    duree_secondes INT NOT NULL CHECK (duree_secondes > 0),                                 -- doit être positif 
    type_usager VARCHAR(20) NOT NULL CHECK (type_usager IN ('abonne', 'occasionnel')),
    usager_ref VARCHAR(20)                                                                 -- pseudo de l'abonné
);

-- ---------------------------------------------------------------
-- 3. Table incident
-- ---------------------------------------------------------------
CREATE TABLE incident (
    incident_id VARCHAR(12) PRIMARY KEY,
    date_signalement TIMESTAMP NOT NULL,
    cible VARCHAR(10) NOT NULL CHECK (cible IN ('velo', 'station')),                          -- soit vélo, soit station
    velo_id VARCHAR(8),                                                                       -- renseigné si cible = velo
    station_id VARCHAR(10) REFERENCES station(station_id) ON DELETE RESTRICT,                 -- renseigné si cible = station
    type_incident VARCHAR(100) NOT NULL,
    statut VARCHAR(20) NOT NULL DEFAULT 'ouvert' CHECK (statut IN ('ouvert', 'en_cours', 'resolu')), -- statuts autorisés
    date_resolution TIMESTAMP,                                                                 -- renseignée ssi l'incident résolu
    technicien VARCHAR(100),                                                                   -- nom du technicien en charge

    -- La cible détermine quelle référence est renseignée
    CONSTRAINT chk_cible_coherence CHECK (
        (cible = 'velo' AND velo_id IS NOT NULL AND station_id IS NULL) OR
        (cible = 'station' AND station_id IS NOT NULL AND velo_id IS NULL)
    ),
    -- La date de résolution est renseignée ssi l'incident est résolu et >= date signalement
    CONSTRAINT chk_date_resolution CHECK (
        (statut = 'resolu' AND date_resolution IS NOT NULL AND date_resolution >= date_signalement) OR
        (statut != 'resolu' AND date_resolution IS NULL)
    )
);

-- ---------------------------------------------------------------
-- 4. Table utilisateur (Compatible avec comptes.sql)
-- ---------------------------------------------------------------
CREATE TABLE utilisateur (
    id_utilisateur SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    mot_de_passe_hash VARCHAR(255) NOT NULL,   -- mdp haché (bcrypt)
    role VARCHAR(20) NOT NULL CHECK (role IN ('exploitant', 'direction'))
);

-- ---------------------------------------------------------------
-- 5. Index utiles aux filtres et aux indicateurs
-- ---------------------------------------------------------------
CREATE INDEX idx_trajet_depart ON trajet(depart_horodatage);
CREATE INDEX idx_trajet_station_depart ON trajet(station_depart);
CREATE INDEX idx_trajet_station_arrivee ON trajet(station_arrivee);

CREATE INDEX idx_incident_statut ON incident(statut);
CREATE INDEX idx_incident_station_id ON incident(station_id);