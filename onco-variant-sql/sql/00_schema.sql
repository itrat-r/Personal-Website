-- =====================================================================
-- 00_schema.sql
-- Star-like schema for a targeted-sequencing cancer cohort.
--
--   patients 1──* samples 1──* variants *──1 genes
--                         1──* expression *──1 genes
-- =====================================================================
PRAGMA foreign_keys = ON;

DROP VIEW  IF EXISTS v_variants_clean;
DROP VIEW  IF EXISTS v_sample_gene_status;
DROP TABLE IF EXISTS expression;
DROP TABLE IF EXISTS variants;
DROP TABLE IF EXISTS samples;
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS genes;

CREATE TABLE genes (
    gene_symbol     TEXT PRIMARY KEY,
    chromosome      TEXT    NOT NULL,
    start_pos       INTEGER NOT NULL,
    end_pos         INTEGER NOT NULL CHECK (end_pos > start_pos),
    protein_length  INTEGER NOT NULL,
    gene_role       TEXT    NOT NULL
);

CREATE TABLE patients (
    patient_id               TEXT PRIMARY KEY,
    sex                      TEXT CHECK (sex IN ('Female', 'Male')),
    age_at_diagnosis         INTEGER CHECK (age_at_diagnosis BETWEEN 0 AND 120),
    smoking_status           TEXT CHECK (smoking_status IN ('Never', 'Former', 'Current')),
    stage                    TEXT CHECK (stage IN ('I', 'II', 'III', 'IV')),
    vital_status             TEXT CHECK (vital_status IN ('Alive', 'Deceased')),
    overall_survival_months  REAL CHECK (overall_survival_months >= 0)
);

CREATE TABLE samples (
    sample_id     TEXT PRIMARY KEY,
    patient_id    TEXT NOT NULL REFERENCES patients(patient_id),
    cancer_type   TEXT NOT NULL,
    sample_type   TEXT NOT NULL,
    tumor_purity  REAL CHECK (tumor_purity BETWEEN 0 AND 1),
    msi_status    TEXT CHECK (msi_status IN ('MSI-H', 'MSS')),
    platform      TEXT
);

-- Raw calls exactly as the variant caller emitted them (duplicates and
-- low-quality calls included). Analyses use v_variants_clean instead.
CREATE TABLE variants (
    variant_id      INTEGER PRIMARY KEY,
    sample_id       TEXT    NOT NULL REFERENCES samples(sample_id),
    gene_symbol     TEXT    NOT NULL REFERENCES genes(gene_symbol),
    chromosome      TEXT    NOT NULL,
    position        INTEGER NOT NULL,
    ref_allele      TEXT    NOT NULL,
    alt_allele      TEXT    NOT NULL,
    variant_class   TEXT    NOT NULL,
    protein_change  TEXT,
    read_depth      INTEGER,
    vaf             REAL CHECK (vaf BETWEEN 0 AND 1),
    filter          TEXT
);

CREATE TABLE expression (
    sample_id    TEXT NOT NULL REFERENCES samples(sample_id),
    gene_symbol  TEXT NOT NULL REFERENCES genes(gene_symbol),
    tpm          REAL CHECK (tpm >= 0),
    PRIMARY KEY (sample_id, gene_symbol)
);

CREATE INDEX idx_samples_patient   ON samples(patient_id);
CREATE INDEX idx_samples_cancer    ON samples(cancer_type);
CREATE INDEX idx_variants_sample   ON variants(sample_id);
CREATE INDEX idx_variants_gene     ON variants(gene_symbol);
CREATE INDEX idx_variants_locus    ON variants(chromosome, position, ref_allele, alt_allele);
CREATE INDEX idx_expression_gene   ON expression(gene_symbol);

-- ---------------------------------------------------------------------
-- Clean variant view: PASS filter, minimum depth/VAF, one row per
-- (sample, locus, allele) - i.e. duplicates from pipeline re-runs removed.
-- ---------------------------------------------------------------------
CREATE VIEW v_variants_clean AS
WITH ranked AS (
    SELECT v.*,
           ROW_NUMBER() OVER (
               PARTITION BY sample_id, chromosome, position, ref_allele, alt_allele
               ORDER BY read_depth DESC, variant_id
           ) AS rn
    FROM variants v
    WHERE filter = 'PASS'
      AND read_depth >= 20
      AND vaf >= 0.05
)
SELECT variant_id, sample_id, gene_symbol, chromosome, position, ref_allele,
       alt_allele, variant_class, protein_change, read_depth, vaf,
       CASE WHEN variant_class IN ('Silent') THEN 0 ELSE 1 END AS is_nonsynonymous,
       CASE WHEN variant_class IN ('Nonsense_Mutation', 'Frame_Shift_Del',
                                   'Frame_Shift_Ins', 'Splice_Site') THEN 1 ELSE 0 END AS is_truncating
FROM ranked
WHERE rn = 1;

-- One row per sample x sequenced gene: 1 if the gene carries any
-- non-synonymous clean variant. The backbone for frequency/co-occurrence work.
CREATE VIEW v_sample_gene_status AS
SELECT s.sample_id,
       s.cancer_type,
       g.gene_symbol,
       MAX(CASE WHEN v.is_nonsynonymous = 1 THEN 1 ELSE 0 END) AS is_mutated
FROM samples s
CROSS JOIN genes g
LEFT JOIN v_variants_clean v
       ON v.sample_id = s.sample_id AND v.gene_symbol = g.gene_symbol
WHERE g.gene_role IN ('Oncogene', 'TSG', 'Passenger')
GROUP BY s.sample_id, s.cancer_type, g.gene_symbol;
