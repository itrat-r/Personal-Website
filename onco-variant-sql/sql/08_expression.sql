-- =====================================================================
-- 08_expression.sql
-- Q: How does gene expression link to tumour type and genotype?
-- =====================================================================

-- 1. Mean log2(TPM + 1) of marker genes per cancer type (wide pivot)
SELECT s.cancer_type,
       ROUND(AVG(CASE WHEN e.gene_symbol = 'ESR1'  THEN LOG2(e.tpm + 1) END), 2) AS ESR1,
       ROUND(AVG(CASE WHEN e.gene_symbol = 'ERBB2' THEN LOG2(e.tpm + 1) END), 2) AS ERBB2,
       ROUND(AVG(CASE WHEN e.gene_symbol = 'EGFR'  THEN LOG2(e.tpm + 1) END), 2) AS EGFR,
       ROUND(AVG(CASE WHEN e.gene_symbol = 'MKI67' THEN LOG2(e.tpm + 1) END), 2) AS MKI67,
       ROUND(AVG(CASE WHEN e.gene_symbol = 'CD8A'  THEN LOG2(e.tpm + 1) END), 2) AS CD8A
FROM expression e
JOIN samples s USING (sample_id)
WHERE e.tpm IS NOT NULL
GROUP BY s.cancer_type;

-- 2. Breast cancer molecular subgroups from expression
--    ER+ : ESR1 TPM >= 20, HER2-high: ERBB2 TPM >= 200
WITH brca AS (
    SELECT e.sample_id,
           MAX(CASE WHEN e.gene_symbol = 'ESR1'  THEN e.tpm END) AS esr1,
           MAX(CASE WHEN e.gene_symbol = 'ERBB2' THEN e.tpm END) AS erbb2
    FROM expression e
    JOIN samples s USING (sample_id)
    WHERE s.cancer_type = 'BRCA'
    GROUP BY e.sample_id
)
SELECT CASE WHEN erbb2 >= 200 THEN 'HER2-high'
            WHEN esr1  >= 20  THEN 'ER+ / HER2-low'
            ELSE 'ER- / HER2-low (triple-negative-like)' END AS subgroup,
       COUNT(*) AS n,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM brca
WHERE esr1 IS NOT NULL AND erbb2 IS NOT NULL
GROUP BY subgroup
ORDER BY n DESC;

-- 3. Mini differential-expression screen: for each gene, log2 fold change
--    between TP53-mutant and wild-type tumours, plus a Welch t-statistic.
WITH expr AS (
    SELECT e.gene_symbol, LOG2(e.tpm + 1) AS x, tp53.is_mutated AS grp
    FROM expression e
    JOIN v_sample_gene_status tp53
      ON tp53.sample_id = e.sample_id AND tp53.gene_symbol = 'TP53'
    WHERE e.tpm IS NOT NULL
),
stats AS (
    SELECT gene_symbol, grp,
           COUNT(*) AS n, AVG(x) AS mean_x,
           (SUM(x * x) - SUM(x) * SUM(x) / COUNT(*)) / (COUNT(*) - 1) AS var_x
    FROM expr
    GROUP BY gene_symbol, grp
)
SELECT m.gene_symbol,
       m.n AS n_mut, w.n AS n_wt,
       ROUND(m.mean_x - w.mean_x, 2) AS log2_fold_change,
       ROUND((m.mean_x - w.mean_x) / SQRT(m.var_x / m.n + w.var_x / w.n), 2) AS welch_t
FROM stats m
JOIN stats w ON w.gene_symbol = m.gene_symbol AND w.grp = 0
WHERE m.grp = 1
ORDER BY ABS(welch_t) DESC;

-- 4. Immune infiltration (CD8A) vs mutational burden: neoantigen hypothesis
WITH cd8 AS (
    SELECT sample_id, LOG2(tpm + 1) AS log_cd8
    FROM expression
    WHERE gene_symbol = 'CD8A' AND tpm IS NOT NULL
)
SELECT CASE WHEN t.tmb_per_mb >= 10 THEN 'TMB-high (>=10)' ELSE 'TMB-low (<10)' END AS tmb_group,
       COUNT(*) AS n,
       ROUND(AVG(c.log_cd8), 2) AS mean_log2_cd8a
FROM v_tmb t
JOIN cd8 c USING (sample_id)
GROUP BY tmb_group;
