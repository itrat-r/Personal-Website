-- =====================================================================
-- 04_mutation_landscape.sql
-- Q: Which genes drive each cancer type, and how mutated are tumours?
-- =====================================================================

-- 1. Top 5 most frequently mutated genes per cancer type
--    (% of samples with >=1 non-synonymous mutation; passenger genes excluded)
WITH freq AS (
    SELECT sg.cancer_type, sg.gene_symbol, g.gene_role,
           SUM(sg.is_mutated)                        AS n_mutated,
           COUNT(*)                                  AS n_samples,
           ROUND(100.0 * AVG(sg.is_mutated), 1)      AS pct_mutated
    FROM v_sample_gene_status sg
    JOIN genes g USING (gene_symbol)
    WHERE g.gene_role IN ('Oncogene', 'TSG')
    GROUP BY sg.cancer_type, sg.gene_symbol
),
ranked AS (
    SELECT *, DENSE_RANK() OVER (PARTITION BY cancer_type ORDER BY pct_mutated DESC) AS rnk
    FROM freq
)
SELECT cancer_type, rnk, gene_symbol, gene_role, n_mutated, n_samples, pct_mutated
FROM ranked
WHERE rnk <= 5
ORDER BY cancer_type, rnk;

-- 2. Oncogenes vs tumour suppressors: share of truncating mutations.
--    TSGs are inactivated (truncating), oncogenes are activated (missense hotspots).
SELECT g.gene_role,
       COUNT(*)                                     AS n_mutations,
       ROUND(100.0 * AVG(v.is_truncating), 1)       AS pct_truncating
FROM v_variants_clean v
JOIN genes g USING (gene_symbol)
WHERE v.is_nonsynonymous = 1
GROUP BY g.gene_role
ORDER BY pct_truncating DESC;

-- 3. Tumour mutational burden (TMB) per sample:
--    non-synonymous mutations per megabase of sequenced coding sequence.
--    Like clinical panels (e.g. FoundationOne CDx), known cancer genes are
--    excluded: their mutations are positively selected and would inflate TMB.
DROP VIEW IF EXISTS v_tmb;
CREATE VIEW v_tmb AS
WITH panel AS (
    SELECT SUM(protein_length) * 3 / 1e6 AS tmb_region_mb
    FROM genes
    WHERE gene_role = 'Passenger'
)
SELECT s.sample_id, s.cancer_type, s.msi_status, p.smoking_status,
       COUNT(v.variant_id)                                       AS n_nonsyn,
       ROUND(COUNT(v.variant_id) / (SELECT tmb_region_mb FROM panel), 2) AS tmb_per_mb
FROM samples s
JOIN patients p USING (patient_id)
LEFT JOIN (
    SELECT cv.*
    FROM v_variants_clean cv
    JOIN genes g USING (gene_symbol)
    WHERE cv.is_nonsynonymous = 1 AND g.gene_role = 'Passenger'
) v ON v.sample_id = s.sample_id
GROUP BY s.sample_id;

-- 4. TMB distribution per cancer type (median + quartiles via NTILE / ROW_NUMBER)
WITH ordered AS (
    SELECT cancer_type, tmb_per_mb,
           ROW_NUMBER() OVER (PARTITION BY cancer_type ORDER BY tmb_per_mb) AS rn,
           COUNT(*)     OVER (PARTITION BY cancer_type)                    AS n
    FROM v_tmb
)
SELECT cancer_type,
       MAX(n)                                                       AS n_samples,
       MAX(CASE WHEN rn = CAST(0.25 * n AS INT) + 1 THEN tmb_per_mb END) AS q1_tmb,
       MAX(CASE WHEN rn = CAST(0.50 * n AS INT) + 1 THEN tmb_per_mb END) AS median_tmb,
       MAX(CASE WHEN rn = CAST(0.75 * n AS INT) + 1 THEN tmb_per_mb END) AS q3_tmb,
       MAX(tmb_per_mb)                                              AS max_tmb
FROM ordered
GROUP BY cancer_type
ORDER BY median_tmb DESC;

-- 5. TMB-high tumours (>= 10 mut/Mb, the FDA pembrolizumab threshold)
SELECT cancer_type,
       COUNT(*)                                    AS n_samples,
       SUM(tmb_per_mb >= 10)                       AS n_tmb_high,
       ROUND(100.0 * AVG(tmb_per_mb >= 10), 1)     AS pct_tmb_high
FROM v_tmb
GROUP BY cancer_type
ORDER BY pct_tmb_high DESC;

-- 6. Colorectal: microsatellite instability explains the TMB-high group
SELECT msi_status, COUNT(*) AS n,
       ROUND(AVG(tmb_per_mb), 1) AS mean_tmb,
       ROUND(100.0 * AVG(tmb_per_mb >= 10), 1) AS pct_tmb_high
FROM v_tmb
WHERE cancer_type = 'COAD'
GROUP BY msi_status;
