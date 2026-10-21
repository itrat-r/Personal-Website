-- =====================================================================
-- 01_load.sql  (run from the project root with the sqlite3 CLI)
-- Load raw CSVs into all-TEXT staging tables, then clean + cast into
-- the typed tables defined in 00_schema.sql.
-- =====================================================================
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS stg_genes;
DROP TABLE IF EXISTS stg_patients;
DROP TABLE IF EXISTS stg_samples;
DROP TABLE IF EXISTS stg_variants;
DROP TABLE IF EXISTS stg_expression;

-- .import creates each staging table from the CSV header (all TEXT columns)
.import --csv data/genes.csv      stg_genes
.import --csv data/patients.csv   stg_patients
.import --csv data/samples.csv    stg_samples
.import --csv data/variants.csv   stg_variants
.import --csv data/expression.csv stg_expression

BEGIN;

INSERT INTO genes
SELECT gene_symbol, chromosome, CAST(start_pos AS INTEGER), CAST(end_pos AS INTEGER),
       CAST(protein_length AS INTEGER), gene_role
FROM stg_genes;

-- Normalise inconsistent sex coding ('F', 'female', 'MALE' ...) and turn
-- empty strings into proper NULLs.
INSERT INTO patients
SELECT patient_id,
       CASE UPPER(SUBSTR(TRIM(sex), 1, 1)) WHEN 'F' THEN 'Female' WHEN 'M' THEN 'Male' END,
       CAST(NULLIF(age_at_diagnosis, '') AS INTEGER),
       NULLIF(smoking_status, ''),
       stage,
       vital_status,
       CAST(overall_survival_months AS REAL)
FROM stg_patients;

INSERT INTO samples
SELECT sample_id, patient_id, cancer_type, sample_type,
       CAST(tumor_purity AS REAL), NULLIF(msi_status, ''), platform
FROM stg_samples;

INSERT INTO variants
SELECT CAST(variant_id AS INTEGER), sample_id, gene_symbol, chromosome,
       CAST(position AS INTEGER), ref_allele, alt_allele, variant_class,
       NULLIF(protein_change, ''), CAST(read_depth AS INTEGER), CAST(vaf AS REAL), filter
FROM stg_variants;

INSERT INTO expression
SELECT sample_id, gene_symbol, CAST(NULLIF(tpm, '') AS REAL)
FROM stg_expression;

COMMIT;

DROP TABLE stg_genes;
DROP TABLE stg_patients;
DROP TABLE stg_samples;
DROP TABLE stg_variants;
DROP TABLE stg_expression;

ANALYZE;
