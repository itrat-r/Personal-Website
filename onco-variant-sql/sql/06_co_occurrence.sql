-- =====================================================================
-- 06_co_occurrence.sql
-- Q: Which driver pairs co-occur or are mutually exclusive?
--    Mutual exclusivity often means two genes hit the same pathway
--    (e.g. KRAS / EGFR / BRAF all activate MAPK signalling).
-- =====================================================================

-- Pairwise 2x2 contingency tables via a self-join, within each cancer type.
-- log2 odds ratio uses a +0.5 Haldane correction to avoid division by zero.
--   log2OR <= -1 -> mutual exclusivity,  >= 1 -> co-occurrence
-- expected_both = co-mutations expected if the genes were independent.
-- Only pairs with a clear tendency (|log2OR| >= 1) are reported.
WITH drivers AS (
    SELECT sg.*
    FROM v_sample_gene_status sg
    JOIN genes g USING (gene_symbol)
    WHERE g.gene_role IN ('Oncogene', 'TSG')
),
pairs AS (
    SELECT a.cancer_type,
           a.gene_symbol AS gene_a,
           b.gene_symbol AS gene_b,
           SUM(a.is_mutated = 1 AND b.is_mutated = 1) AS both_mut,
           SUM(a.is_mutated = 1 AND b.is_mutated = 0) AS a_only,
           SUM(a.is_mutated = 0 AND b.is_mutated = 1) AS b_only,
           SUM(a.is_mutated = 0 AND b.is_mutated = 0) AS neither
    FROM drivers a
    JOIN drivers b
      ON a.sample_id = b.sample_id
     AND a.gene_symbol < b.gene_symbol          -- each unordered pair once
    GROUP BY a.cancer_type, a.gene_symbol, b.gene_symbol
),
scored AS (
    SELECT *,
           1.0 * (both_mut + a_only) * (both_mut + b_only)
               / (both_mut + a_only + b_only + neither) AS expected_both,
           LOG2(((both_mut + 0.5) * (neither + 0.5)) /
                ((a_only + 0.5) * (b_only + 0.5)))      AS log2_or
    FROM pairs
    WHERE a_only + both_mut >= 10 AND b_only + both_mut >= 10   -- both genes reasonably frequent
)
SELECT cancer_type, gene_a, gene_b, both_mut,
       ROUND(expected_both, 1) AS expected_both,
       a_only, b_only, neither,
       ROUND(log2_or, 2)       AS log2_odds_ratio,
       CASE WHEN log2_or <= -1 THEN 'mutually exclusive' ELSE 'co-occurring' END AS pattern
FROM scored
WHERE ABS(log2_or) >= 1
ORDER BY log2_or;
