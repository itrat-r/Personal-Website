-- =====================================================================
-- 02_data_quality.sql
-- Q: Is the data trustworthy? What did cleaning remove?
-- =====================================================================

-- 1. Missingness in clinical fields
SELECT 'age_at_diagnosis' AS field,
       SUM(age_at_diagnosis IS NULL) AS n_missing,
       ROUND(100.0 * SUM(age_at_diagnosis IS NULL) / COUNT(*), 1) AS pct_missing
FROM patients
UNION ALL
SELECT 'smoking_status', SUM(smoking_status IS NULL),
       ROUND(100.0 * SUM(smoking_status IS NULL) / COUNT(*), 1)
FROM patients
UNION ALL
SELECT 'expression.tpm', SUM(tpm IS NULL), ROUND(100.0 * SUM(tpm IS NULL) / COUNT(*), 1)
FROM expression;

-- 2. Referential integrity: variants pointing at unknown samples/genes (expect 0)
SELECT
    (SELECT COUNT(*) FROM variants v LEFT JOIN samples s USING (sample_id)
      WHERE s.sample_id IS NULL) AS orphan_sample_variants,
    (SELECT COUNT(*) FROM variants v LEFT JOIN genes g USING (gene_symbol)
      WHERE g.gene_symbol IS NULL) AS orphan_gene_variants;

-- 3. Duplicate calls (same sample + locus + allele reported more than once)
SELECT COUNT(*)            AS duplicated_loci,
       SUM(n_copies) - COUNT(*) AS redundant_rows
FROM (
    SELECT COUNT(*) AS n_copies
    FROM variants
    GROUP BY sample_id, chromosome, position, ref_allele, alt_allele
    HAVING COUNT(*) > 1
);

-- 4. Variant QC funnel: how many raw calls survive each filter
WITH flags AS (
    SELECT filter = 'PASS'                              AS f_pass,
           filter = 'PASS' AND read_depth >= 20         AS f_depth,
           filter = 'PASS' AND read_depth >= 20 AND vaf >= 0.05 AS f_vaf
    FROM variants
)
SELECT 'raw calls'           AS step, COUNT(*)     AS n_variants FROM flags
UNION ALL SELECT 'FILTER = PASS',      SUM(f_pass)  FROM flags
UNION ALL SELECT '+ depth >= 20',      SUM(f_depth) FROM flags
UNION ALL SELECT '+ VAF >= 5%',        SUM(f_vaf)   FROM flags
UNION ALL SELECT '+ de-duplicated',    COUNT(*)     FROM v_variants_clean;

-- 5. Do low-quality calls look like artefacts? Compare depth/VAF distributions
SELECT CASE WHEN filter = 'PASS' AND read_depth >= 20 AND vaf >= 0.05
            THEN 'kept' ELSE 'removed' END AS qc_outcome,
       COUNT(*)                  AS n,
       ROUND(AVG(read_depth), 0) AS mean_depth,
       ROUND(AVG(vaf), 3)        AS mean_vaf
FROM variants
GROUP BY qc_outcome;
