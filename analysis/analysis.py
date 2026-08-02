"""
Medical cost segmentation analysis.

Reads data/insurance.csv, writes:
  - data/summary.json   (all figures used by the dashboard)
  - assets/images/*.png (figures used in the README and PDF reports)

Every number published in this project is produced by this script.
Run from the repository root:  python analysis/analysis.py
"""

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OBESITY_CUTOFF = 30.0

INK = "#131C22"
MUTED = "#6B7C88"
LOW = "#2E6E5B"
HIGH = "#A63A4A"
MID = "#8494A0"
GRID = "#D5DDE3"


def load():
    raw = pd.read_csv(os.path.join(ROOT, "data", "insurance.csv"))
    df = raw.drop_duplicates().reset_index(drop=True)
    df["obese"] = df["bmi"] >= OBESITY_CUTOFF
    df["segment"] = np.where(df["smoker"] == "yes", "Smoker", "Non-smoker") + np.where(
        df["obese"], ", BMI 30+", ", BMI <30"
    )
    return raw, df


def segments(df):
    total = df["charges"].sum()
    g = df.groupby("segment")["charges"].agg(["count", "mean", "median", "sum"])
    g["pct_members"] = g["count"] / len(df) * 100
    g["pct_spend"] = g["sum"] / total * 100
    return g.sort_values("sum", ascending=False)


def bmi_bands(df):
    bands = pd.cut(
        df["bmi"],
        bins=[0, 25, 30, 35, 40, 100],
        labels=["<25", "25-30", "30-35", "35-40", "40+"],
        right=False,
    )
    return df.assign(band=bands).pivot_table(
        index="band", columns="smoker", values="charges",
        aggfunc=["count", "mean"], observed=True,
    )


def age_bands(df):
    bands = pd.cut(
        df["age"], bins=[17, 29, 39, 49, 64],
        labels=["18-29", "30-39", "40-49", "50-64"],
    )
    return df.assign(band=bands).pivot_table(
        index="band", columns="smoker", values="charges",
        aggfunc=["count", "mean"], observed=True,
    )


def bmi_slopes(df):
    """Test whether BMI acts as a gradient or a step at the obesity cutoff."""
    out = {}
    for label, sub in [("smoker", df[df.smoker == "yes"]), ("non_smoker", df[df.smoker == "no"])]:
        lo, hi = sub[~sub.obese], sub[sub.obese]
        out[label] = {
            "slope_below": float(np.polyfit(lo.bmi, lo.charges, 1)[0]),
            "slope_above": float(np.polyfit(hi.bmi, hi.charges, 1)[0]),
            "step_at_cutoff": float(hi.charges.mean() - lo.charges.mean()),
            "n_below": int(len(lo)),
            "n_above": int(len(hi)),
        }
    return out


def levers(df):
    """
    Association-based ceilings, NOT causal effects.

    Each lever moves a segment onto the observed mean of the segment it would
    belong to if the risk factor were removed. This is an upper bound that
    assumes complete conversion and no residual risk. It is presented alongside
    realistic uptake rates for exactly that reason.
    """
    sm, ns = df[df.smoker == "yes"], df[df.smoker == "no"]
    ns_obese_mean = ns[ns.obese].charges.mean()
    ns_lean_mean = ns[~ns.obese].charges.mean()
    sm_lean_mean = sm[~sm.obese].charges.mean()
    total = df.charges.sum()

    spec = [
        ("Smoking cessation - obese smokers", sm[sm.obese], ns_obese_mean, "High", "Medium"),
        ("Smoking cessation - non-obese smokers", sm[~sm.obese], ns_lean_mean, "High", "Medium"),
        ("Weight programme - obese smokers", sm[sm.obese], sm_lean_mean, "Low", "High"),
        ("Weight programme - obese non-smokers", ns[ns.obese], ns_lean_mean, "Medium", "High"),
    ]
    rows = []
    for name, pop, target, conf, effort in spec:
        ceiling = pop.charges.sum() - len(pop) * target
        rows.append({
            "lever": name,
            "n": int(len(pop)),
            "current_spend": float(pop.charges.sum()),
            "ceiling_saving": float(ceiling),
            "ceiling_pct_of_book": float(ceiling / total * 100),
            "per_head": float(ceiling / len(pop)),
            "at_5pct": float(ceiling * 0.05),
            "at_10pct": float(ceiling * 0.10),
            "at_20pct": float(ceiling * 0.20),
            "confidence": conf,
            "effort": effort,
        })
    return rows


def style(ax):
    ax.set_facecolor("none")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.yaxis.grid(True, color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)


def fig_segments(seg, path):
    order = ["Smoker, BMI 30+", "Non-smoker, BMI 30+", "Non-smoker, BMI <30", "Smoker, BMI <30"]
    s = seg.loc[order]
    y = np.arange(len(order))
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.barh(y + 0.19, s["pct_members"], 0.36, color=MID, label="Share of members")
    ax.barh(y - 0.19, s["pct_spend"], 0.36, color=HIGH, label="Share of spend")
    for i, (m, c) in enumerate(zip(s["pct_members"], s["pct_spend"])):
        ax.text(m + 0.7, i + 0.19, f"{m:.1f}%", va="center", fontsize=9, color=MUTED)
        ax.text(c + 0.7, i - 0.19, f"{c:.1f}%", va="center", fontsize=9, color=HIGH, weight="bold")
    ax.set_yticks(y, order, fontsize=10, color=INK)
    ax.invert_yaxis()
    ax.set_xlim(0, 48)
    ax.set_xlabel("Percent", color=MUTED, fontsize=9)
    ax.set_title(
        "Obese smokers are 11% of members and 34% of spend",
        color=INK, fontsize=13, weight="bold", loc="left", pad=14,
    )
    style(ax)
    ax.xaxis.grid(True, color=GRID, linewidth=0.7)
    ax.yaxis.grid(False)
    ax.legend(frameon=False, fontsize=9, labelcolor=MUTED, loc="lower right")
    fig.tight_layout()
    fig.savefig(path, dpi=200, transparent=True)
    plt.close(fig)


def fig_bmi(bmi, path):
    labels = list(bmi.index)
    fig, ax = plt.subplots(figsize=(9, 4.6))
    x = np.arange(len(labels))
    ax.bar(x - 0.2, bmi[("mean", "no")], 0.4, color=MID, label="Non-smoker")
    ax.bar(x + 0.2, bmi[("mean", "yes")], 0.4, color=HIGH, label="Smoker")
    ax.axvline(1.5, color=INK, linestyle="--", linewidth=1)
    ax.text(1.58, 46000, "BMI 30 cutoff", fontsize=9, color=INK)
    ax.set_xticks(x, labels, fontsize=10, color=INK)
    ax.set_ylabel("Mean annual charges (USD)", color=MUTED, fontsize=9)
    ax.set_title(
        "For smokers the cutoff is a cliff, not a slope",
        color=INK, fontsize=13, weight="bold", loc="left", pad=14,
    )
    style(ax)
    ax.legend(frameon=False, fontsize=9, labelcolor=MUTED)
    fig.tight_layout()
    fig.savefig(path, dpi=200, transparent=True)
    plt.close(fig)


def fig_age(age, path):
    labels = list(age.index)
    gap = age[("mean", "yes")] - age[("mean", "no")]
    fig, ax = plt.subplots(figsize=(9, 4.6))
    x = np.arange(len(labels))
    ax.plot(x, age[("mean", "no")], "o-", color=MID, linewidth=2, label="Non-smoker")
    ax.plot(x, age[("mean", "yes")], "s-", color=HIGH, linewidth=2, label="Smoker")
    for i, g in enumerate(gap):
        ax.annotate(
            "", xy=(i, age[("mean", "yes")].iloc[i]), xytext=(i, age[("mean", "no")].iloc[i]),
            arrowprops=dict(arrowstyle="<->", color=LOW, linewidth=1),
        )
        ax.text(i + 0.07, (age[("mean", "yes")].iloc[i] + age[("mean", "no")].iloc[i]) / 2,
                f"${g:,.0f}", fontsize=9, color=LOW, va="center")
    ax.set_xticks(x, labels, fontsize=10, color=INK)
    ax.set_ylabel("Mean annual charges (USD)", color=MUTED, fontsize=9)
    ax.set_title(
        "The smoking penalty barely widens with age",
        color=INK, fontsize=13, weight="bold", loc="left", pad=14,
    )
    style(ax)
    ax.legend(frameon=False, fontsize=9, labelcolor=MUTED, loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=200, transparent=True)
    plt.close(fig)


def main():
    raw, df = load()
    seg = segments(df)
    bmi = bmi_bands(df)
    age = age_bands(df)
    total = float(df.charges.sum())

    sorted_charges = df.charges.sort_values(ascending=False)
    concentration = {
        f"top_{int(k * 100)}pct": float(sorted_charges.head(int(len(df) * k)).sum() / total * 100)
        for k in (0.05, 0.10, 0.20, 0.50)
    }

    region = df.groupby("region").agg(
        n=("charges", "size"),
        smoker_pct=("smoker", lambda s: (s == "yes").mean() * 100),
        obese_pct=("obese", lambda s: s.mean() * 100),
        mean_bmi=("bmi", "mean"),
        mean_charges=("charges", "mean"),
    )
    region["obese_smoker_pct"] = df.groupby("region").apply(
        lambda d: ((d.smoker == "yes") & d.obese).mean() * 100, include_groups=False
    )

    high_cost_ns = df[(df.smoker == "no") & (df.charges > 30000)]

    summary = {
        "meta": {
            "rows_raw": int(len(raw)),
            "rows_analysed": int(len(df)),
            "duplicates_removed": int(len(raw) - len(df)),
            "columns": list(raw.columns),
            "null_count": int(raw.isna().sum().sum()),
            "obesity_cutoff": OBESITY_CUTOFF,
            "total_spend": total,
            "mean_charges": float(df.charges.mean()),
            "median_charges": float(df.charges.median()),
            "max_charges": float(df.charges.max()),
            "charges_skew": float(df.charges.skew()),
            "smoker_pct": float((df.smoker == "yes").mean() * 100),
            "obese_pct": float(df.obese.mean() * 100),
        },
        "segments": [
            {
                "name": name, "n": int(r["count"]), "mean": float(r["mean"]),
                "median": float(r["median"]), "total": float(r["sum"]),
                "pct_members": float(r["pct_members"]), "pct_spend": float(r["pct_spend"]),
            }
            for name, r in seg.iterrows()
        ],
        "concentration": concentration,
        "bmi_bands": [
            {
                "band": str(b),
                "n_non_smoker": int(bmi.loc[b, ("count", "no")]),
                "n_smoker": int(bmi.loc[b, ("count", "yes")]),
                "mean_non_smoker": float(bmi.loc[b, ("mean", "no")]),
                "mean_smoker": float(bmi.loc[b, ("mean", "yes")]),
            }
            for b in bmi.index
        ],
        "age_bands": [
            {
                "band": str(b),
                "n_non_smoker": int(age.loc[b, ("count", "no")]),
                "n_smoker": int(age.loc[b, ("count", "yes")]),
                "mean_non_smoker": float(age.loc[b, ("mean", "no")]),
                "mean_smoker": float(age.loc[b, ("mean", "yes")]),
                "gap": float(age.loc[b, ("mean", "yes")] - age.loc[b, ("mean", "no")]),
            }
            for b in age.index
        ],
        "bmi_slopes": bmi_slopes(df),
        "regions": [
            {
                "region": r, "n": int(row["n"]), "smoker_pct": float(row["smoker_pct"]),
                "obese_pct": float(row["obese_pct"]), "mean_bmi": float(row["mean_bmi"]),
                "mean_charges": float(row["mean_charges"]),
                "obese_smoker_pct": float(row["obese_smoker_pct"]),
            }
            for r, row in region.iterrows()
        ],
        "levers": levers(df),
        "unexplained": {
            "high_cost_non_smokers": int(len(high_cost_ns)),
            "non_smoker_total": int((df.smoker == "no").sum()),
            "their_spend": float(high_cost_ns.charges.sum()),
            "pct_of_book": float(high_cost_ns.charges.sum() / total * 100),
        },
    }

    with open(os.path.join(ROOT, "data", "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    with open(os.path.join(ROOT, "data", "summary.js"), "w") as f:
        f.write("const SUMMARY = " + json.dumps(summary, indent=2) + ";\n")

    img = os.path.join(ROOT, "assets", "images")
    fig_segments(seg, os.path.join(img, "segment-population-vs-spend.png"))
    fig_bmi(bmi, os.path.join(img, "bmi-threshold.png"))
    fig_age(age, os.path.join(img, "age-gap.png"))

    print(f"Analysed {len(df)} rows ({len(raw) - len(df)} duplicate removed).")
    print(f"Total spend ${total:,.0f}. Wrote summary.json, summary.js and 3 figures.")


if __name__ == "__main__":
    main()
