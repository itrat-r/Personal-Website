"""Visualise the OncoVariant SQL results with matplotlib.

Every chart is drawn straight from onco.db: the heavy lifting stays in SQL
(same queries / views as sql/02-08), Python only does the plotting.

Usage:  python scripts/plots.py [output_dir]      (default: figures/)
Needs:  pip install pandas matplotlib
"""
import sqlite3
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "figures"
OUT.mkdir(parents=True, exist_ok=True)

con = sqlite3.connect(ROOT / "onco.db")


def q(sql):
    return pd.read_sql_query(sql, con)


# Shared look: matches the portfolio site colours
BRAND, ACCENT, GOOD, PURPLE = "#1f4e8c", "#ff6b4a", "#1aa37a", "#8a5cc2"
INK, MUTED, GRID = "#17202e", "#5b6678", "#e6e0d6"
PAL_TYPE = {"BRCA": BRAND, "LUAD": ACCENT, "COAD": GOOD, "SKCM": PURPLE}

plt.rcParams.update({
    "font.family": ["Helvetica Neue", "Arial", "DejaVu Sans"],
    "font.size": 11,
    "text.color": INK,
    "axes.labelcolor": MUTED,
    "axes.edgecolor": GRID,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "axes.axisbelow": True,
    "xtick.color": MUTED,
    "ytick.color": INK,
    "legend.frameon": False,
    "figure.facecolor": "white",
})


def titles(ax, title, subtitle, pad=10):
    """Left-aligned bold title + muted subtitle, stacked above the axes."""
    ax.annotate(subtitle, xy=(0, 1), xycoords="axes fraction", xytext=(0, pad),
                textcoords="offset points", va="bottom", color=MUTED, fontsize=11)
    ax.annotate(title, xy=(0, 1), xycoords="axes fraction", xytext=(0, pad + 20),
                textcoords="offset points", va="bottom", fontweight="bold", fontsize=14)


def save(fig, name):
    path = OUT / f"{name}.png"
    fig.savefig(path, dpi=200, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print("wrote", path)


# ---------------------------------------------------------------------
# 1. QC funnel (02_data_quality.sql #4)
# ---------------------------------------------------------------------
funnel = q("""
  WITH flags AS (
    SELECT filter = 'PASS'                                      AS f_pass,
           filter = 'PASS' AND read_depth >= 20                 AS f_depth,
           filter = 'PASS' AND read_depth >= 20 AND vaf >= 0.05 AS f_vaf
    FROM variants
  )
  SELECT 'Raw calls' AS step, COUNT(*) AS n FROM flags
  UNION ALL SELECT 'FILTER = PASS', SUM(f_pass)  FROM flags
  UNION ALL SELECT 'Depth ≥ 20',    SUM(f_depth) FROM flags
  UNION ALL SELECT 'VAF ≥ 5%',      SUM(f_vaf)   FROM flags
  UNION ALL SELECT 'De-duplicated', COUNT(*)     FROM v_variants_clean""")

fig, ax = plt.subplots(figsize=(8, 4))
y = np.arange(len(funnel))[::-1]
ax.barh(y, funnel.n, color=BRAND, height=0.65)
for yi, n in zip(y, funnel.n):
    ax.text(n + 30, yi, f"{n:,}", va="center", color=INK)
ax.set_yticks(y, funnel.step)
ax.set_xlim(0, funnel.n.max() * 1.12)
ax.set_xlabel("Variants")
ax.grid(axis="y", visible=False)
titles(ax, "Variant QC funnel", "2,590 raw calls → 2,161 analysis-ready variants")
save(fig, "01_qc_funnel")

# ---------------------------------------------------------------------
# 2. Driver landscape heatmap (04_mutation_landscape.sql #1)
# ---------------------------------------------------------------------
drivers = q("""
  WITH freq AS (
    SELECT sg.cancer_type, sg.gene_symbol,
           ROUND(100.0 * AVG(sg.is_mutated), 1) AS pct_mutated
    FROM v_sample_gene_status sg
    JOIN genes g USING (gene_symbol)
    WHERE g.gene_role IN ('Oncogene', 'TSG')
    GROUP BY sg.cancer_type, sg.gene_symbol
  ),
  top AS (
    SELECT gene_symbol FROM (
      SELECT gene_symbol,
             DENSE_RANK() OVER (PARTITION BY cancer_type ORDER BY pct_mutated DESC) AS rnk
      FROM freq)
    WHERE rnk <= 5
  )
  SELECT * FROM freq WHERE gene_symbol IN (SELECT gene_symbol FROM top)""")
mat = drivers.pivot(index="gene_symbol", columns="cancer_type", values="pct_mutated")
mat = mat[list(PAL_TYPE)].fillna(0)
mat = mat.loc[mat.max(axis=1).sort_values(ascending=False).index]

fig, ax = plt.subplots(figsize=(7, 7))
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("brand", ["#eef3fa", BRAND])
im = ax.imshow(mat.values, cmap=cmap, aspect="auto", vmin=0, vmax=mat.values.max())
for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):
        v = mat.values[i, j]
        if v >= 1:
            ax.text(j, i, f"{v:.0f}", ha="center", va="center",
                    color="white" if v > 45 else INK, fontsize=10)
ax.set_xticks(range(mat.shape[1]), mat.columns)
ax.set_yticks(range(mat.shape[0]), mat.index)
ax.xaxis.tick_top()
ax.tick_params(length=0)
ax.set_xticks(np.arange(-.5, mat.shape[1]), minor=True)
ax.set_yticks(np.arange(-.5, mat.shape[0]), minor=True)
ax.grid(which="minor", color="white", linewidth=2)
ax.grid(which="major", visible=False)
for s in ax.spines.values():
    s.set_visible(False)
cb = fig.colorbar(im, ax=ax, shrink=0.6, pad=0.03)
cb.set_label("% tumours mutated")
cb.outline.set_visible(False)
titles(ax, "Each cancer type has its own driver genes",
       "% of tumours with a non-synonymous mutation (top-5 genes per type)", pad=30)
save(fig, "02_driver_heatmap")

# ---------------------------------------------------------------------
# 3. Recurrent hotspots (05_hotspots.sql #1)
# ---------------------------------------------------------------------
hot = q("""
  SELECT v.gene_symbol || ' ' || REPLACE(v.protein_change, 'p.', '') AS mutation,
         g.gene_role,
         COUNT(DISTINCT v.sample_id) AS n_samples
  FROM v_variants_clean v
  JOIN genes g USING (gene_symbol)
  WHERE v.is_nonsynonymous = 1
  GROUP BY v.gene_symbol, v.protein_change, v.chromosome, v.position, v.ref_allele, v.alt_allele
  HAVING COUNT(DISTINCT v.sample_id) >= 8
  ORDER BY n_samples DESC""")

fig, ax = plt.subplots(figsize=(8, 6))
y = np.arange(len(hot))[::-1]
colors = hot.gene_role.map({"Oncogene": ACCENT, "TSG": BRAND})
ax.barh(y, hot.n_samples, color=colors, height=0.7)
for yi, n in zip(y, hot.n_samples):
    ax.text(n + 0.8, yi, str(n), va="center", color=INK, fontsize=10)
ax.set_yticks(y, hot.mutation)
ax.set_xlim(0, hot.n_samples.max() * 1.1)
ax.set_xlabel("Tumours carrying the mutation")
ax.grid(axis="y", visible=False)
ax.legend(handles=[matplotlib.patches.Patch(color=ACCENT, label="Oncogene"),
                   matplotlib.patches.Patch(color=BRAND, label="Tumour suppressor")],
          loc="lower right")
titles(ax, "BRAF V600E is the most recurrent mutation", "Protein changes seen in ≥ 8 tumours")
save(fig, "03_hotspots")

# ---------------------------------------------------------------------
# 4. Tumour mutational burden (04_mutation_landscape.sql, view v_tmb)
# ---------------------------------------------------------------------
tmb = q("""
  SELECT cancer_type,
         CASE WHEN cancer_type = 'COAD' THEN 'COAD ' || msi_status ELSE cancer_type END AS grp,
         tmb_per_mb
  FROM v_tmb""")
groups = ["BRCA", "LUAD", "COAD MSS", "COAD MSI-H", "SKCM"]
rng = np.random.default_rng(42)

fig, ax = plt.subplots(figsize=(8, 5))
ax.axhline(10, ls="--", color=MUTED, lw=1)
ax.text(-0.45, 10.8, "TMB-high (≥ 10 mut/Mb)", color=MUTED, fontsize=9.5)
data = []
for i, g in enumerate(groups):
    d = tmb[tmb.grp == g]
    data.append(d.tmb_per_mb.values)
    ax.scatter(i + rng.uniform(-.25, .25, len(d)), d.tmb_per_mb + rng.uniform(-.4, .4, len(d)),
               s=10, alpha=.45, color=PAL_TYPE[d.cancer_type.iloc[0]], lw=0)
ax.boxplot(data, positions=range(len(groups)), widths=.45, showfliers=False,
           medianprops=dict(color=INK, lw=1.5), boxprops=dict(color=INK),
           whiskerprops=dict(color=INK), capprops=dict(color=INK))
ax.set_xticks(range(len(groups)), groups)
ax.set_xlim(-.6, len(groups) - .4)
ax.set_ylabel("Mutations per Mb")
ax.grid(axis="x", visible=False)
titles(ax, "MSI-high colorectal tumours carry ~10× the mutational burden",
       "Tumour mutational burden per sample; COAD split by microsatellite status")
save(fig, "04_tmb")

# ---------------------------------------------------------------------
# 5. Mutual exclusivity (06_co_occurrence.sql)
# ---------------------------------------------------------------------
pairs = q("""
  WITH drivers AS (
    SELECT sg.* FROM v_sample_gene_status sg
    JOIN genes g USING (gene_symbol)
    WHERE g.gene_role IN ('Oncogene', 'TSG')
  ),
  pairs AS (
    SELECT a.cancer_type, a.gene_symbol AS gene_a, b.gene_symbol AS gene_b,
           SUM(a.is_mutated = 1 AND b.is_mutated = 1) AS both_mut,
           SUM(a.is_mutated = 1 AND b.is_mutated = 0) AS a_only,
           SUM(a.is_mutated = 0 AND b.is_mutated = 1) AS b_only,
           SUM(a.is_mutated = 0 AND b.is_mutated = 0) AS neither
    FROM drivers a
    JOIN drivers b ON a.sample_id = b.sample_id AND a.gene_symbol < b.gene_symbol
    GROUP BY a.cancer_type, a.gene_symbol, b.gene_symbol
  )
  SELECT gene_a || ' / ' || gene_b || '  (' || cancer_type || ')' AS label,
         LOG2(((both_mut + 0.5) * (neither + 0.5)) /
              ((a_only + 0.5) * (b_only + 0.5))) AS log2_or
  FROM pairs
  WHERE a_only + both_mut >= 10 AND b_only + both_mut >= 10""")
pairs = pairs[pairs.log2_or.abs() >= 1.3].sort_values("log2_or", ascending=False)

fig, ax = plt.subplots(figsize=(8, 5.5))
y = np.arange(len(pairs))
colors = np.where(pairs.log2_or < 0, ACCENT, GOOD)
ax.hlines(y, 0, pairs.log2_or, color=colors, lw=2)
ax.scatter(pairs.log2_or, y, color=colors, s=50, zorder=3)
ax.axvline(0, color=MUTED, lw=1)
ax.set_yticks(y, pairs.label)
ax.set_xlabel("log2 odds ratio of co-mutation")
ax.grid(axis="y", visible=False)
ax.legend(handles=[matplotlib.lines.Line2D([], [], color=ACCENT, marker="o", lw=2, label="Mutually exclusive"),
                   matplotlib.lines.Line2D([], [], color=GOOD, marker="o", lw=2, label="Co-occurring")],
          loc="lower left")
titles(ax, "Genes in the same pathway are rarely mutated together",
       "Driver pairs within a cancer type, |log2 odds ratio| ≥ 1.3")
save(fig, "05_mutual_exclusivity")

# ---------------------------------------------------------------------
# 6. Kaplan-Meier survival by TP53 status (07_clinical_outcomes.sql, view v_km_tp53)
# ---------------------------------------------------------------------
km = q("SELECT grp, months, survival FROM v_km_tp53 ORDER BY grp, months")
medians = q("SELECT grp, MIN(months) AS median_os FROM v_km_tp53 WHERE survival <= 0.5 GROUP BY grp")
pal_tp53 = {"TP53 mutant": ACCENT, "TP53 wild-type": BRAND}

fig, ax = plt.subplots(figsize=(8, 5))
ax.axhline(.5, ls=":", color=MUTED, lw=1)
for grp, d in km.groupby("grp"):
    t = np.concatenate([[0], d.months])
    s = np.concatenate([[1], d.survival])
    ax.step(t, s, where="post", color=pal_tp53[grp], lw=2, label=grp)
for _, m in medians.iterrows():
    c = pal_tp53[m.grp]
    ax.vlines(m.median_os, 0, .5, color=c, ls="--", lw=1)
    ax.text(m.median_os + 1, .03, f"{m.median_os:g} mo", color=c, fontsize=10)
ax.set_ylim(0, 1.02)
ax.set_xlim(0, km.months.max())
ax.set_xticks(range(0, int(km.months.max()) + 1, 12))
ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
ax.set_xlabel("Months since diagnosis")
ax.set_ylabel("Overall survival")
ax.legend(loc="upper right")
titles(ax, "TP53-mutant patients have shorter overall survival",
       "Kaplan–Meier estimate computed in SQL; dashed lines mark median survival")
save(fig, "06_survival_tp53")

# ---------------------------------------------------------------------
# 7. Smoking and lung cancer drivers (07_clinical_outcomes.sql #1)
# ---------------------------------------------------------------------
smk = q("""
  SELECT CASE WHEN t.smoking_status = 'Never' THEN 'Never smoker' ELSE 'Ever smoker' END AS grp,
         100.0 * AVG(egfr.is_mutated) AS EGFR,
         100.0 * AVG(kras.is_mutated) AS KRAS
  FROM v_tmb t
  JOIN v_sample_gene_status egfr ON egfr.sample_id = t.sample_id AND egfr.gene_symbol = 'EGFR'
  JOIN v_sample_gene_status kras ON kras.sample_id = t.sample_id AND kras.gene_symbol = 'KRAS'
  WHERE t.cancer_type = 'LUAD' AND t.smoking_status IS NOT NULL
  GROUP BY grp""").set_index("grp").loc[["Never smoker", "Ever smoker"]]

fig, ax = plt.subplots(figsize=(6.5, 4.8))
x = np.arange(2)
for k, (grp, color) in enumerate([("Never smoker", GOOD), ("Ever smoker", MUTED)]):
    vals = smk.loc[grp, ["EGFR", "KRAS"]].values
    bars = ax.bar(x + (k - .5) * .36, vals, width=.34, color=color, label=grp)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + .8, f"{v:.0f}%", ha="center", color=INK)
ax.set_xticks(x, ["EGFR", "KRAS"])
ax.set_ylim(0, smk.values.max() * 1.25)
ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(100, decimals=0))
ax.set_ylabel("% of tumours")
ax.grid(axis="x", visible=False)
ax.legend(loc="upper center", ncol=2)
titles(ax, "Lung cancer: EGFR in never-smokers, KRAS in smokers",
       "LUAD tumours with a mutation in each gene, by smoking history")
save(fig, "07_smoking_luad")

con.close()
