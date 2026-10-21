"""
Generate a synthetic (but biologically plausible) pan-cancer targeted-sequencing
cohort as CSV files. Standard library only; seeded so results are reproducible.

Biology baked in so the SQL analysis has real signals to find:
  * known driver frequencies per cancer type (TP53, PIK3CA, KRAS, BRAF, APC ...)
  * real hotspot mutations (BRAF V600E, KRAS G12D, PIK3CA H1047R ...)
  * mutual exclusivity (KRAS vs EGFR in LUAD, BRAF vs NRAS in SKCM)
  * smoking -> higher TMB and fewer EGFR mutations in lung adenocarcinoma
  * MSI-high colorectal tumours with very high TMB
  * TP53-mutant tumours have worse survival and higher MKI67 expression
  * ESR1 expression high in breast cancer

Deliberate data-quality problems are injected (duplicates, low-quality calls,
inconsistent sex coding, missing values) so the cleaning step is meaningful.

Usage: python3 scripts/generate_data.py [output_dir]
"""
import csv
import math
import os
import random
import sys

rng = random.Random(42)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT, exist_ok=True)

# symbol, chromosome, start (approx GRCh38), end, protein length (aa), role
GENES = [
    ("TP53", "17", 7661779, 7687538, 393, "TSG"),
    ("PIK3CA", "3", 179148114, 179240093, 1068, "Oncogene"),
    ("KRAS", "12", 25205246, 25250929, 189, "Oncogene"),
    ("EGFR", "7", 55019017, 55211628, 1210, "Oncogene"),
    ("BRAF", "7", 140719327, 140924929, 766, "Oncogene"),
    ("NRAS", "1", 114704469, 114716771, 189, "Oncogene"),
    ("ERBB2", "17", 39688094, 39728658, 1255, "Oncogene"),
    ("APC", "5", 112707498, 112846239, 2843, "TSG"),
    ("PTEN", "10", 87863113, 87971930, 403, "TSG"),
    ("CDH1", "16", 68737292, 68835537, 882, "TSG"),
    ("GATA3", "10", 8045378, 8075198, 443, "TSG"),
    ("STK11", "19", 1177558, 1228431, 433, "TSG"),
    ("SMAD4", "18", 51028394, 51085045, 552, "TSG"),
    ("KEAP1", "19", 10486120, 10503576, 624, "TSG"),
    ("ARID1A", "1", 26693236, 26782104, 2285, "TSG"),
    ("NF1", "17", 31094927, 31382116, 2839, "TSG"),
    ("TTN", "2", 178525989, 178830802, 34350, "Passenger"),
    ("MUC16", "19", 8848844, 8981342, 14507, "Passenger"),
    ("CSMD3", "8", 112222928, 113436939, 3707, "Passenger"),
    ("LRP1B", "2", 140231423, 142131016, 4599, "Passenger"),
    ("RYR2", "1", 237042184, 237833988, 4967, "Passenger"),
    ("ESR1", "6", 151656691, 152129619, 595, "Expression marker"),
    ("MKI67", "10", 128096659, 128126204, 3256, "Expression marker"),
    ("CD8A", "2", 86784610, 86808396, 235, "Expression marker"),
    ("GAPDH", "12", 6534512, 6538374, 335, "Housekeeping"),
]
GENE = {g[0]: g for g in GENES}
SEQUENCED = [g for g in GENES if g[5] not in ("Expression marker", "Housekeeping")]
PANEL_MB = sum(g[4] * 3 for g in SEQUENCED) / 1e6  # coding bases on the panel

# driver mutation probability per cancer type
DRIVERS = {
    "BRCA": {"TP53": .35, "PIK3CA": .33, "CDH1": .12, "GATA3": .12, "PTEN": .06,
             "ARID1A": .05, "NF1": .04, "ERBB2": .03},
    "LUAD": {"TP53": .46, "KRAS": .30, "EGFR": .14, "STK11": .17, "KEAP1": .18,
             "NF1": .10, "BRAF": .07, "ARID1A": .07},
    "COAD": {"APC": .75, "TP53": .55, "KRAS": .42, "PIK3CA": .18, "SMAD4": .13,
             "BRAF": .10, "ARID1A": .10, "NRAS": .04},
    "SKCM": {"BRAF": .50, "NRAS": .25, "NF1": .14, "TP53": .15, "PTEN": .08,
             "ARID1A": .06},
}
COHORT = {"BRCA": 220, "LUAD": 180, "COAD": 150, "SKCM": 110}
MUTUALLY_EXCLUSIVE = [("KRAS", "EGFR"), ("BRAF", "NRAS"), ("KRAS", "BRAF")]

# (protein change, variant class, weight); remaining weight -> random mutation
HOTSPOTS = {
    "TP53": [("p.R175H", "Missense_Mutation", .08), ("p.R248Q", "Missense_Mutation", .06),
             ("p.R273H", "Missense_Mutation", .06), ("p.R248W", "Missense_Mutation", .04),
             ("p.R273C", "Missense_Mutation", .04), ("p.G245S", "Missense_Mutation", .03)],
    "PIK3CA": [("p.H1047R", "Missense_Mutation", .35), ("p.E545K", "Missense_Mutation", .20),
               ("p.E542K", "Missense_Mutation", .12)],
    "KRAS": [("p.G12D", "Missense_Mutation", .30), ("p.G12V", "Missense_Mutation", .22),
             ("p.G12C", "Missense_Mutation", .18), ("p.G13D", "Missense_Mutation", .12),
             ("p.Q61H", "Missense_Mutation", .06)],
    "EGFR": [("p.L858R", "Missense_Mutation", .45), ("p.E746_A750del", "In_Frame_Del", .40),
             ("p.T790M", "Missense_Mutation", .05)],
    "BRAF": [("p.V600E", "Missense_Mutation", .85)],
    "NRAS": [("p.Q61R", "Missense_Mutation", .45), ("p.Q61K", "Missense_Mutation", .35),
             ("p.G12D", "Missense_Mutation", .10)],
    "APC": [("p.R1450*", "Nonsense_Mutation", .10), ("p.E1309fs", "Frame_Shift_Del", .08)],
    "ERBB2": [("p.S310F", "Missense_Mutation", .30), ("p.L755S", "Missense_Mutation", .20)],
}
AA = "ACDEFGHIKLMNPQRSTVWY"
BASES = "ACGT"
BACKGROUND_CLASSES = [("Missense_Mutation", .60), ("Silent", .25), ("Nonsense_Mutation", .05),
                      ("Frame_Shift_Del", .04), ("Frame_Shift_Ins", .02), ("Splice_Site", .04)]


def weighted(choices):
    r, acc = rng.random(), 0.0
    for value, w in choices:
        acc += w
        if r < acc:
            return value
    return choices[-1][0]


def poisson(lam):
    # Knuth's algorithm; fine for the small lambdas used here
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= L:
            return k
        k += 1


def protein_pos(change):
    digits = "".join(ch for ch in change.split("_")[0] if ch.isdigit())
    return int(digits)


def random_change(gene, vclass):
    length = GENE[gene][4]
    pos = rng.randint(2, length - 1)
    ref = rng.choice(AA)
    if vclass == "Missense_Mutation":
        return f"p.{ref}{pos}{rng.choice(AA.replace(ref, ''))}", pos
    if vclass == "Silent":
        return f"p.{ref}{pos}=", pos
    if vclass == "Nonsense_Mutation":
        return f"p.{ref}{pos}*", pos
    if vclass.startswith("Frame_Shift"):
        return f"p.{ref}{pos}fs", pos
    if vclass == "Splice_Site":
        return f"p.X{pos}_splice", pos
    return f"p.{ref}{pos}del", pos


def driver_mutation(gene):
    for change, vclass, w in HOTSPOTS.get(gene, []):
        if rng.random() < w:
            return change, vclass
    if GENE[gene][5] == "TSG":
        vclass = weighted([("Nonsense_Mutation", .30), ("Frame_Shift_Del", .18),
                           ("Frame_Shift_Ins", .07), ("Splice_Site", .08), ("Missense_Mutation", .37)])
    else:
        vclass = "Missense_Mutation"
    return random_change(gene, vclass)[0], vclass


def genomic(gene, change):
    """Deterministic coordinate + alleles so recurrent hotspots share a position."""
    _, chrom, start, end, _, _ = GENE[gene]
    pos = start + protein_pos(change) * 3
    local = random.Random(f"{gene}{change}")
    ref = local.choice(BASES)
    alt = local.choice(BASES.replace(ref, ""))
    return chrom, min(pos, end), ref, alt


patients, samples, variants, expression = [], [], [], []
variant_id = 0

pid = 0
for cancer, n in COHORT.items():
    for _ in range(n):
        pid += 1
        patient_id = f"PT-{pid:04d}"
        sample_id = f"SM-{pid:04d}-T"
        sex = "Female" if cancer == "BRCA" and rng.random() < .99 else rng.choice(["Female", "Male"])
        age = max(22, min(90, int(rng.gauss({"BRCA": 58, "LUAD": 66, "COAD": 67, "SKCM": 61}[cancer], 11))))
        smoking = None
        if cancer == "LUAD":
            smoking = weighted([("Current", .30), ("Former", .50), ("Never", .20)])
        elif rng.random() < .7:
            smoking = weighted([("Current", .18), ("Former", .32), ("Never", .50)])
        stage = weighted([("I", .25), ("II", .35), ("III", .25), ("IV", .15)])
        msi = None
        if cancer == "COAD":
            msi = "MSI-H" if rng.random() < .14 else "MSS"

        # ---- mutations ----
        mutated = set()
        probs = dict(DRIVERS[cancer])
        if cancer == "LUAD" and smoking == "Never":
            probs["EGFR"], probs["KRAS"] = .45, .08
        elif cancer == "LUAD":
            probs["EGFR"] = .06
        for gene, p in probs.items():
            if rng.random() < p and not any(
                    gene in pair and (set(pair) - {gene}) & mutated for pair in MUTUALLY_EXCLUSIVE):
                mutated.add(gene)
        muts = [(g, *driver_mutation(g)) for g in sorted(mutated)]  # sorted: set order varies per run

        tmb_rate = {"BRCA": 1.5, "LUAD": 10 if smoking in ("Current", "Former") else 2,
                    "COAD": 40 if msi == "MSI-H" else 4, "SKCM": 15}[cancer]
        weights = [(g[0], g[4]) for g in SEQUENCED]
        total_w = sum(w for _, w in weights)
        for _ in range(poisson(tmb_rate * PANEL_MB)):
            gene = weighted([(g, w / total_w) for g, w in weights])
            vclass = weighted(BACKGROUND_CLASSES)
            muts.append((gene, random_change(gene, vclass)[0], vclass))

        purity = round(rng.uniform(.3, .95), 2)
        for gene, change, vclass in muts:
            chrom, pos, ref, alt = genomic(gene, change)
            depth = int(rng.gauss(250, 80))
            vaf = round(min(.98, max(.05, rng.gauss(purity / 2, .08))), 3)
            variant_id += 1
            row = [variant_id, sample_id, gene, chrom, pos, ref, alt, vclass, change,
                   max(30, depth), vaf, "PASS"]
            variants.append(row)
            if rng.random() < .02:  # pipeline re-run produced a duplicate call
                variant_id += 1
                variants.append([variant_id] + row[1:])
        for _ in range(poisson(.6)):  # sequencing artefacts
            gene = rng.choice(SEQUENCED)[0]
            vclass = weighted(BACKGROUND_CLASSES)
            change = random_change(gene, vclass)[0]
            chrom, pos, ref, alt = genomic(gene, change)
            variant_id += 1
            variants.append([variant_id, sample_id, gene, chrom, pos, ref, alt, vclass, change,
                             rng.randint(4, 18), round(rng.uniform(.01, .04), 3),
                             rng.choice(["LowQual", "LowQual", "PASS"])])

        # ---- expression (TPM) ----
        tp53_mut = "TP53" in mutated
        means = {"ESR1": 120 if cancer == "BRCA" and rng.random() < .75 else 3,
                 "ERBB2": 40 if not (cancer == "BRCA" and rng.random() < .15) else 600,
                 "EGFR": 60 if cancer == "LUAD" else 15,
                 "MKI67": 35 if tp53_mut else 15,
                 "CD8A": 25 if (cancer == "SKCM" or msi == "MSI-H") else 8,
                 "GAPDH": 1500, "TP53": 45, "KRAS": 30, "PTEN": 20 if "PTEN" not in mutated else 6,
                 "CDH1": 150 if not (cancer == "BRCA" and "CDH1" in mutated) else 10}
        for gene, mean in means.items():
            tpm = round(math.exp(rng.gauss(math.log(mean), .45)), 2)
            expression.append([sample_id, gene, "" if rng.random() < .01 else tpm])

        # ---- survival ----
        hazard = {"I": .006, "II": .010, "III": .020, "IV": .055}[stage]
        hazard *= {"BRCA": .7, "LUAD": 1.4, "COAD": 1.0, "SKCM": 1.1}[cancer]
        hazard *= 1.6 if tp53_mut else 1.0
        event_time = rng.expovariate(hazard)
        follow_up = rng.uniform(6, 120)
        dead = event_time <= follow_up
        os_months = round(event_time if dead else follow_up, 1)

        # inject messy clinical values
        sex_out = sex if rng.random() > .05 else rng.choice([sex[0], sex.lower(), sex.upper()])
        age_out = "" if rng.random() < .03 else age
        patients.append([patient_id, sex_out, age_out, smoking or "", stage,
                         "Deceased" if dead else "Alive", os_months])
        samples.append([sample_id, patient_id, cancer, "Primary Tumor", purity, msi or "",
                        rng.choice(["NovaSeq 6000", "NovaSeq X", "HiSeq 4000"])])

rng.shuffle(variants)


def write(name, header, rows):
    with open(os.path.join(OUT, name), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"wrote {len(rows):>6} rows -> {name}")


write("genes.csv", ["gene_symbol", "chromosome", "start_pos", "end_pos", "protein_length", "gene_role"],
      [list(g) for g in GENES])
write("patients.csv", ["patient_id", "sex", "age_at_diagnosis", "smoking_status", "stage",
                       "vital_status", "overall_survival_months"], patients)
write("samples.csv", ["sample_id", "patient_id", "cancer_type", "sample_type", "tumor_purity",
                      "msi_status", "platform"], samples)
write("variants.csv", ["variant_id", "sample_id", "gene_symbol", "chromosome", "position", "ref_allele",
                       "alt_allele", "variant_class", "protein_change", "read_depth", "vaf", "filter"],
      variants)
write("expression.csv", ["sample_id", "gene_symbol", "tpm"], expression)
print(f"panel size: {PANEL_MB:.4f} Mb coding sequence")
