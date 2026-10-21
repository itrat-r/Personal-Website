-- =====================================================================
-- 05_hotspots.sql
-- Q: Which exact mutations recur across patients (actionable hotspots)?
-- =====================================================================

-- 1. Recurrent protein changes seen in >= 5 distinct samples,
--    with the cancer types they occur in
SELECT v.gene_symbol,
       v.protein_change,
       v.chromosome || ':' || v.position || ' ' || v.ref_allele || '>' || v.alt_allele AS locus,
       COUNT(DISTINCT v.sample_id)          AS n_samples,
       GROUP_CONCAT(DISTINCT s.cancer_type) AS cancer_types
FROM v_variants_clean v
JOIN samples s USING (sample_id)
WHERE v.is_nonsynonymous = 1
GROUP BY v.gene_symbol, v.protein_change, locus
HAVING COUNT(DISTINCT v.sample_id) >= 5
ORDER BY n_samples DESC;

-- 2. How concentrated are each oncogene's mutations at its top hotspot?
--    (high % = classic activating oncogene; genes whose most frequent
--    change occurs < 3 times have no hotspot and are left out)
WITH counts AS (
    SELECT gene_symbol, protein_change, COUNT(*) AS n
    FROM v_variants_clean
    WHERE is_nonsynonymous = 1
    GROUP BY gene_symbol, protein_change
),
ranked AS (
    SELECT *,
           SUM(n)       OVER (PARTITION BY gene_symbol)                  AS gene_total,
           ROW_NUMBER() OVER (PARTITION BY gene_symbol ORDER BY n DESC)  AS rn
    FROM counts
)
SELECT r.gene_symbol, g.gene_role, r.protein_change AS top_hotspot,
       r.n AS hotspot_n, r.gene_total,
       ROUND(100.0 * r.n / r.gene_total, 1) AS pct_at_top_hotspot
FROM ranked r
JOIN genes g USING (gene_symbol)
WHERE r.rn = 1 AND r.gene_total >= 10 AND r.n >= 3
ORDER BY pct_at_top_hotspot DESC;

-- 3. KRAS allele spectrum by cancer type (G12C is targetable by sotorasib)
SELECT s.cancer_type,
       v.protein_change,
       COUNT(*) AS n,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY s.cancer_type), 1)
           AS pct_of_kras_in_type
FROM v_variants_clean v
JOIN samples s USING (sample_id)
WHERE v.gene_symbol = 'KRAS' AND v.protein_change IN
      ('p.G12D', 'p.G12V', 'p.G12C', 'p.G13D', 'p.Q61H')
GROUP BY s.cancer_type, v.protein_change
ORDER BY s.cancer_type, n DESC;
