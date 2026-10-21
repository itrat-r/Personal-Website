-- =====================================================================
-- 03_cohort_overview.sql
-- Q: Who is in the cohort? (the "Table 1" of any clinical paper)
-- =====================================================================

-- 1. Demographics per cancer type, including a true median age
--    (SQLite has no MEDIAN(), so it is computed with window functions)
WITH ordered AS (
    SELECT s.cancer_type, p.age_at_diagnosis AS age,
           ROW_NUMBER() OVER (PARTITION BY s.cancer_type ORDER BY p.age_at_diagnosis) AS rn,
           COUNT(*)     OVER (PARTITION BY s.cancer_type)                             AS n
    FROM patients p
    JOIN samples s USING (patient_id)
    WHERE p.age_at_diagnosis IS NOT NULL
),
median_age AS (
    SELECT cancer_type, AVG(age) AS median_age
    FROM ordered
    WHERE rn IN ((n + 1) / 2, (n + 2) / 2)
    GROUP BY cancer_type
)
SELECT s.cancer_type,
       COUNT(*)                                                    AS n_patients,
       ROUND(100.0 * SUM(p.sex = 'Female') / COUNT(*), 1)          AS pct_female,
       m.median_age,
       ROUND(100.0 * SUM(p.stage IN ('III', 'IV')) / COUNT(*), 1)  AS pct_stage_III_IV,
       ROUND(100.0 * SUM(p.vital_status = 'Deceased') / COUNT(*), 1) AS pct_deceased
FROM patients p
JOIN samples s USING (patient_id)
JOIN median_age m USING (cancer_type)
GROUP BY s.cancer_type
ORDER BY n_patients DESC;

-- 2. Stage distribution as a pivot (conditional aggregation)
SELECT s.cancer_type,
       SUM(p.stage = 'I')   AS stage_I,
       SUM(p.stage = 'II')  AS stage_II,
       SUM(p.stage = 'III') AS stage_III,
       SUM(p.stage = 'IV')  AS stage_IV
FROM patients p
JOIN samples s USING (patient_id)
GROUP BY s.cancer_type;

-- 3. Smoking history in lung adenocarcinoma
SELECT COALESCE(p.smoking_status, 'Unknown') AS smoking_status,
       COUNT(*) AS n,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM patients p
JOIN samples s USING (patient_id)
WHERE s.cancer_type = 'LUAD'
GROUP BY 1
ORDER BY n DESC;
