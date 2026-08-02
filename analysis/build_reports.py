"""
Builds the three supporting PDF reports in assets/reports/ from data/summary.json.

Run after analysis.py:  python analysis/build_reports.py
"""

import json
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "reports")
IMG = os.path.join(ROOT, "assets", "images")

INK = colors.HexColor("#131C22")
MUTED = colors.HexColor("#4E606B")
FAINT = colors.HexColor("#8B9AA4")
LINE = colors.HexColor("#D3DCE2")
HIGH = colors.HexColor("#A63A4A")
FLAG_BG = colors.HexColor("#F6EFDD")
FLAG = colors.HexColor("#8A6410")
BAND = colors.HexColor("#F4F7F9")

S = getSampleStyleSheet()

TITLE = ParagraphStyle("T", parent=S["Title"], fontName="Helvetica-Bold", fontSize=22,
                       leading=26, alignment=TA_LEFT, textColor=INK, spaceAfter=6)
SUB = ParagraphStyle("Sub", parent=S["Normal"], fontName="Helvetica", fontSize=11.5,
                     leading=16, textColor=MUTED, spaceAfter=18)
H1 = ParagraphStyle("H1", parent=S["Heading1"], fontName="Helvetica-Bold", fontSize=14.5,
                    leading=18, textColor=INK, spaceBefore=20, spaceAfter=7)
H2 = ParagraphStyle("H2", parent=S["Heading2"], fontName="Helvetica-Bold", fontSize=11.5,
                    leading=15, textColor=INK, spaceBefore=13, spaceAfter=4)
BODY = ParagraphStyle("B", parent=S["Normal"], fontName="Helvetica", fontSize=10,
                      leading=15.2, textColor=INK, spaceAfter=8)
SMALL = ParagraphStyle("S", parent=BODY, fontSize=8.6, leading=12.4, textColor=FAINT)
CAP = ParagraphStyle("C", parent=BODY, fontSize=8.6, leading=12.4, textColor=MUTED,
                     spaceBefore=4, spaceAfter=14)
BULLET = ParagraphStyle("Bu", parent=BODY, leftIndent=14, bulletIndent=3, spaceAfter=5)
EYEBROW = ParagraphStyle("E", parent=BODY, fontName="Helvetica-Bold", fontSize=8,
                         textColor=FAINT, spaceAfter=4)

with open(os.path.join(ROOT, "data", "summary.json")) as f:
    D = json.load(f)

M = D["meta"]
SEG = {s["name"]: s for s in D["segments"]}
LEV = {l["lever"]: l for l in D["levers"]}


def usd(v, dp=0):
    return "$" + f"{v:,.{dp}f}"


def musd(v):
    return "$" + f"{v / 1e6:.2f}M"


def kusd(v):
    return "$" + f"{v / 1e3:,.0f}k"


def callout(text, bg=FLAG_BG, bar=FLAG):
    t = Table([[Paragraph(text, ParagraphStyle("CO", parent=BODY, textColor=colors.HexColor("#3F2F06")))]],
              colWidths=[6.5 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 2.5, bar),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return t


def table(header, rows, widths, aligns=None):
    data = [[Paragraph(f"<b>{h}</b>", ParagraphStyle("TH", parent=BODY, fontSize=8.4,
                                                     textColor=FAINT)) for h in header]]
    for r in rows:
        data.append([Paragraph(str(c), ParagraphStyle("TD", parent=BODY, fontSize=9,
                                                      leading=12.5, spaceAfter=0)) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1)
    style = [
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, LINE),
        ("LINEBELOW", (0, 1), (-1, -2), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BAND]),
    ]
    for col in (aligns or []):
        style.append(("ALIGN", (col, 0), (col, -1), "RIGHT"))
    t.setStyle(TableStyle(style))
    return t


def figure(name, width=6.4 * inch):
    path = os.path.join(IMG, name)
    from PIL import Image as PILImage
    w, h = PILImage.open(path).size
    return Image(path, width=width, height=width * h / w)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(FAINT)
    canvas.drawString(1 * inch, 0.55 * inch,
                      "Medical cost segmentation  |  Joshua Croffet  |  simulated data, methodology demonstration")
    canvas.drawRightString(7.5 * inch, 0.55 * inch, f"Page {doc.page}")
    canvas.setStrokeColor(LINE)
    canvas.line(1 * inch, 0.75 * inch, 7.5 * inch, 0.75 * inch)
    canvas.restoreState()


def build(filename, title, subtitle, story):
    doc = SimpleDocTemplate(
        os.path.join(OUT, filename), pagesize=LETTER,
        leftMargin=1 * inch, rightMargin=1 * inch,
        topMargin=0.9 * inch, bottomMargin=0.95 * inch,
        title=title, author="Joshua Croffet",
    )
    head = [
        Paragraph("MEDICAL COST SEGMENTATION", EYEBROW),
        Paragraph(title, TITLE),
        Paragraph(subtitle, SUB),
    ]
    doc.build(head + story, onFirstPage=footer, onLaterPages=footer)
    print("wrote", filename)


PROVENANCE = (
    "<b>Provenance.</b> The source file is the widely circulated Medical Cost Personal Datasets "
    "teaching set, which is simulated rather than drawn from real claims. The findings are real "
    "properties of the data and the methods are the ones that would be used on a live book, but no "
    "conclusion here describes an actual insurer or population."
)

CAUSAL = (
    "<b>These are not causal effects.</b> The dataset has no time dimension, so nothing here can "
    "demonstrate that removing a risk factor causes a cost reduction. Every saving figure is an "
    "association-based ceiling: it moves a segment onto the observed mean of the segment it would "
    "belong to without that risk factor, assuming complete conversion and no residual risk."
)


# ----------------------------------------------------------------------------
# Report 1 — executive summary
# ----------------------------------------------------------------------------

def executive_summary():
    obese_smoker = SEG["Smoker, BMI 30+"]
    l1, l2 = LEV["Smoking cessation - obese smokers"], LEV["Smoking cessation - non-obese smokers"]
    l4 = LEV["Weight programme - obese non-smokers"]

    s = [
        callout(PROVENANCE),
        Spacer(1, 16),

        Paragraph("The recommendation", H1),
        Paragraph(
            f"Point the health intervention budget at smokers with a BMI of 30 or above. There are "
            f"{obese_smoker['n']} of them in a book of {M['rows_analysed']:,} members — "
            f"{obese_smoker['pct_members']:.1f}% of the population — and they account for "
            f"{musd(obese_smoker['total'])}, or {obese_smoker['pct_spend']:.1f}% of total spend. "
            f"Their mean annual cost is {usd(obese_smoker['mean'])} against "
            f"{usd(SEG['Non-smoker, BMI <30']['mean'])} for members carrying neither risk factor.", BODY),
        Paragraph(
            "Smoking cessation is the lever, not weight management. That is the counterintuitive "
            "part of this analysis and it is where the money is.", BODY),

        Paragraph("Why the two risk factors cannot be treated separately", H1),
        Paragraph(
            f"Obesity costs a non-smoker {usd(SEG['Non-smoker, BMI 30+']['mean'] - SEG['Non-smoker, BMI <30']['mean'])} "
            f"a year. It costs a smoker "
            f"{usd(SEG['Smoker, BMI 30+']['mean'] - SEG['Smoker, BMI <30']['mean'])} — a 23-fold "
            f"difference in the same risk factor. Neither variable on its own identifies where to "
            f"intervene; only the intersection does.", BODY),
        figure("segment-population-vs-spend.png"),
        Paragraph(
            "Population and cost are inverted. Only the obese-smoker segment consumes materially more "
            "than its share of the book.", CAP),

        Paragraph("What each option is worth", H1),
        Paragraph(
            "The ceiling column assumes every member in the segment converts and carries no residual "
            "risk. It is an upper bound, not a forecast. The 10% column is the figure to take into a "
            "business case — generous but defensible for cessation programmes, optimistic for weight "
            "programmes.", BODY),
        table(
            ["Lever", "Members", "Ceiling", "% of book", "At 10%"],
            [
                [l1["lever"].replace(" - ", " — "), l1["n"], musd(l1["ceiling_saving"]),
                 f"{l1['ceiling_pct_of_book']:.1f}%", kusd(l1["at_10pct"])],
                [l2["lever"].replace(" - ", " — "), l2["n"], musd(l2["ceiling_saving"]),
                 f"{l2['ceiling_pct_of_book']:.1f}%", kusd(l2["at_10pct"])],
                [l4["lever"].replace(" - ", " — "), l4["n"], musd(l4["ceiling_saving"]),
                 f"{l4['ceiling_pct_of_book']:.1f}%", kusd(l4["at_10pct"])],
            ],
            [2.65 * inch, 0.75 * inch, 0.9 * inch, 0.85 * inch, 0.85 * inch],
            aligns=[1, 2, 3, 4],
        ),
        Spacer(1, 14),
        Paragraph(
            f"The third row is the trap. Obese non-smokers are the single largest group in the book "
            f"at {SEG['Non-smoker, BMI 30+']['n']} members — "
            f"{SEG['Non-smoker, BMI 30+']['pct_members']:.0f}% of the population — and a general "
            f"wellness programme would naturally aim there. The entire theoretical prize is "
            f"{kusd(l4['ceiling_saving'])}, or {usd(l4['per_head'])} a head. The obese-smoker segment "
            f"is a quarter the size and worth {l1['ceiling_saving'] / l4['ceiling_saving']:.1f} times as much.", BODY),

        PageBreak(),

        Paragraph("Three things that change the recommendation", H1),

        Paragraph("Target the young, not the old", H2),
        Paragraph(
            "The smoker-to-non-smoker cost gap is close to constant across the age range: "
            + ", ".join(f"{usd(b['gap'])} at {b['band']}" for b in D["age_bands"]) +
            ". Because the annual gap does not widen, the younger cohort is worth more in total — "
            "the same saving repeats over more remaining years. Outreach aimed at older smokers on "
            "the assumption that they are more expensive to leave untreated is not supported here.", BODY),

        Paragraph("Run it in the southeast first", H2),
        Paragraph(
            "Obese-smoker prevalence is "
            f"{[r for r in D['regions'] if r['region'] == 'southeast'][0]['obese_smoker_pct']:.1f}% "
            "in the southeast against roughly 9% across the other three regions, and that segment "
            "accounts for 45.7% of all southeast spend. Geography is not a separate lever; it is the "
            "delivery sequence.", BODY),

        Paragraph("Do not price anything on the BMI 30 boundary", H2),
        Paragraph(
            f"The apparent {usd(D['bmi_slopes']['smoker']['step_at_cutoff'])} step at BMI 30 is an "
            f"artifact of how this dataset was generated, not a physiological threshold. The full "
            f"argument is in the data quality report. Any eligibility rule or saving estimate built "
            f"on that cutoff inherits the artifact.", BODY),

        Paragraph("What to do next", H1),
        Paragraph(
            "&bull; Commission a cessation programme scoped to the obese-smoker segment, delivered "
            "southeast-first, with explicit outreach to the 18–29 cohort.", BULLET),
        Paragraph(
            "&bull; Instrument the data before the next cycle. A linear model on the six available "
            "inputs reaches R&sup2; = 0.75; the missing quarter is concentrated in members with no "
            "visible risk factors. Diagnosis codes, claim dates and member IDs would close it.", BULLET),
        Paragraph(
            "&bull; Verify smoking status. The entire targeting list rests on a self-reported binary "
            "field, and tobacco use is systematically under-declared in insurance settings.", BULLET),
        Paragraph(
            "&bull; Do not fund a general weight programme on cost-avoidance grounds. It may be "
            "justified on health outcomes; it is not justified by this data on spend.", BULLET),

        Spacer(1, 16),
        callout(CAUSAL, bg=colors.HexColor("#EEF2F5"), bar=colors.HexColor("#63757F")),
    ]
    build("executive-summary.pdf", "Where to spend the health intervention budget",
          "A segmentation of 1,337 members identifying the highest-yield target for "
          "cost-avoidance intervention.", s)


# ----------------------------------------------------------------------------
# Report 2 — segmentation and sizing
# ----------------------------------------------------------------------------

def segmentation():
    rows = [[s["name"], s["n"], f"{s['pct_members']:.1f}%", usd(s["mean"]), usd(s["median"]),
             musd(s["total"]), f"{s['pct_spend']:.1f}%"] for s in D["segments"]]

    lever_rows = []
    for l in D["levers"]:
        lever_rows.append([
            l["lever"].replace(" - ", " — "), l["n"], musd(l["ceiling_saving"]),
            usd(l["per_head"]), kusd(l["at_5pct"]), kusd(l["at_10pct"]), kusd(l["at_20pct"]),
        ])

    s = [
        callout(PROVENANCE),
        Spacer(1, 16),

        Paragraph("Method", H1),
        Paragraph(
            f"The source file contains {M['rows_raw']:,} records and {len(M['columns'])} columns "
            f"with no missing values. One exact duplicate pair was found — two byte-identical rows "
            f"describing a 19-year-old male non-smoker in the northwest — and one copy was removed, "
            f"leaving {M['rows_analysed']:,} records. With no member identifier there is no way to "
            f"distinguish a genuine coincidence from a duplication error; removing it is the "
            f"conservative choice and it moves no published figure materially.", BODY),
        Paragraph(
            f"Members were split into four segments on two binary flags: smoking status as declared, "
            f"and BMI at or above {M['obesity_cutoff']:.0f}, the clinical obesity threshold. No other "
            f"transformation was applied.", BODY),

        Paragraph("Segment structure", H1),
        table(
            ["Segment", "n", "% mem", "Mean", "Median", "Spend", "% spend"],
            rows,
            [1.95 * inch, 0.42 * inch, 0.58 * inch, 0.78 * inch, 0.78 * inch, 0.72 * inch, 0.67 * inch],
            aligns=[1, 2, 3, 4, 5, 6],
        ),
        Spacer(1, 12),
        Paragraph(
            "The mean-to-median gap is the segment's internal skew. It is widest among obese smokers, "
            "where a small number of very large claims pull the mean above the typical member.", BODY),
        Paragraph(
            f"Spend is concentrated: the top 5% of members account for "
            f"{D['concentration']['top_5pct']:.1f}% of the book, the top 10% for "
            f"{D['concentration']['top_10pct']:.1f}%, and the top 20% for "
            f"{D['concentration']['top_20pct']:.1f}%. Charges are right-skewed with a skew "
            f"coefficient of {M['charges_skew']:.2f}: median {usd(M['median_charges'])} against a "
            f"mean of {usd(M['mean_charges'])} and a maximum of {usd(M['max_charges'])}. Any figure "
            f"reported as a mean without its median will overstate the typical member.", BODY),

        Paragraph("The interaction", H1),
        Paragraph(
            f"Moving from BMI under 30 to BMI 30 or above costs a non-smoker "
            f"{usd(SEG['Non-smoker, BMI 30+']['mean'] - SEG['Non-smoker, BMI <30']['mean'])}. The "
            f"same move costs a smoker "
            f"{usd(SEG['Smoker, BMI 30+']['mean'] - SEG['Smoker, BMI <30']['mean'])}. The risk "
            f"factors are not additive, and a targeting model that treats them as independent will "
            f"mis-rank every segment.", BODY),
        figure("segment-population-vs-spend.png"),
        Paragraph("Population share against spend share, by segment.", CAP),

        PageBreak(),

        Paragraph("Age is not the discriminator it appears to be", H1),
        Paragraph(
            "Both smoker and non-smoker costs rise with age, which invites the conclusion that older "
            "smokers are the priority. The gap between the two lines tells a different story.", BODY),
        table(
            ["Age band", "n non-smoker", "n smoker", "Mean non-smoker", "Mean smoker", "Gap"],
            [[b["band"], b["n_non_smoker"], b["n_smoker"], usd(b["mean_non_smoker"]),
              usd(b["mean_smoker"]), usd(b["gap"])] for b in D["age_bands"]],
            [0.9 * inch, 1.0 * inch, 0.8 * inch, 1.25 * inch, 1.1 * inch, 0.9 * inch],
            aligns=[1, 2, 3, 4, 5],
        ),
        Spacer(1, 12),
        figure("age-gap.png"),
        Paragraph(
            "The smoking penalty varies by roughly $2,200 across a 46-year age range. For practical "
            "purposes it is constant.", CAP),
        Paragraph(
            "The implication runs against intuition. If a smoker costs about $24,000 more per year "
            "than a non-smoker regardless of age, then a successful cessation at 25 banks that "
            "difference for forty years and a cessation at 60 banks it for five. Targeting should "
            "skew young, not old.", BODY),

        Paragraph("Regional distribution", H1),
        table(
            ["Region", "n", "Smoker %", "Obese %", "Mean BMI", "Obese smoker %", "Mean charges"],
            [[r["region"], r["n"], f"{r['smoker_pct']:.1f}%", f"{r['obese_pct']:.1f}%",
              f"{r['mean_bmi']:.1f}", f"{r['obese_smoker_pct']:.1f}%", usd(r["mean_charges"])]
             for r in D["regions"]],
            [1.05 * inch, 0.45 * inch, 0.75 * inch, 0.7 * inch, 0.75 * inch, 1.05 * inch, 0.95 * inch],
            aligns=[1, 2, 3, 4, 5, 6],
        ),
        Spacer(1, 12),
        Paragraph(
            "The southeast carries nearly double the obese-smoker prevalence of any other region, and "
            "that segment alone accounts for 45.7% of southeast spend against 28.9% elsewhere. "
            "Whether this reflects population composition or differences in care access cannot be "
            "settled from this file; it needs external deprivation or access data.", BODY),

        PageBreak(),

        Paragraph("Intervention sizing", H1),
        Paragraph(
            "Each lever moves its segment onto the observed mean of the segment it would belong to "
            "with the risk factor removed. The ceiling is the resulting difference across the whole "
            "segment. Uptake columns apply a flat success rate to that ceiling.", BODY),
        table(
            ["Lever", "n", "Ceiling", "Per head", "At 5%", "At 10%", "At 20%"],
            lever_rows,
            [1.95 * inch, 0.42 * inch, 0.75 * inch, 0.78 * inch, 0.62 * inch, 0.68 * inch, 0.68 * inch],
            aligns=[1, 2, 3, 4, 5, 6],
        ),
        Spacer(1, 14),
        callout(CAUSAL, bg=colors.HexColor("#EEF2F5"), bar=colors.HexColor("#63757F")),
        Spacer(1, 14),

        Paragraph("Ranking", H1),
        Paragraph(
            "Levers are scored on impact multiplied by confidence and divided by effort. Confidence "
            "reflects how well the underlying effect is established in this data; effort reflects the "
            "operational difficulty of delivering a sustained change.", BODY),
        table(
            ["Rank", "Lever", "At 10%", "Confidence", "Effort", "Reasoning"],
            [
                ["1", "Cessation — obese smokers", kusd(LEV["Smoking cessation - obese smokers"]["at_10pct"]),
                 "High", "Medium", "Largest effect, smallest segment, established intervention."],
                ["2", "Cessation — non-obese smokers", kusd(LEV["Smoking cessation - non-obese smokers"]["at_10pct"]),
                 "High", "Medium", "Same mechanism, roughly a third of the yield."],
                ["3", "Instrument the data", "—", "High", "Low",
                 "Cheap, and it unlocks the 25% of variance nothing here explains."],
                ["4", "Weight — obese smokers", kusd(LEV["Weight programme - obese smokers"]["at_10pct"]),
                 "Low", "High", "Rests entirely on the BMI 30 artifact. Do not fund on this basis."],
                ["5", "Weight — obese non-smokers", kusd(LEV["Weight programme - obese non-smokers"]["at_10pct"]),
                 "Medium", "High", "Largest population, smallest per-head return."],
            ],
            [0.42 * inch, 1.5 * inch, 0.6 * inch, 0.72 * inch, 0.55 * inch, 2.11 * inch],
            aligns=[2],
        ),
        Spacer(1, 14),
        Paragraph(
            "The ranking says target 11% of members to address 34% of spend, and it puts the largest "
            "population last. That is the whole finding.", BODY),
    ]
    build("segmentation-and-sizing.pdf", "Segmentation and intervention sizing",
          "Full method, segment structure, regional and age breakdowns, and the sizing behind "
          "each candidate intervention.", s)


# ----------------------------------------------------------------------------
# Report 3 — data quality and artifacts
# ----------------------------------------------------------------------------

def data_quality():
    sm, ns = D["bmi_slopes"]["smoker"], D["bmi_slopes"]["non_smoker"]
    u = D["unexplained"]

    s = [
        callout(PROVENANCE),
        Spacer(1, 16),

        Paragraph("Summary", H1),
        Paragraph(
            "The file is technically pristine and that is itself the most important observation about "
            "it. There are no missing values, no impossible entries, and near-perfect balance across "
            "sex and region. Real claims extracts do not look like this. Three specific properties "
            "identify the data as simulated, and one of them directly invalidates a finding that "
            "would otherwise look like the strongest result in the analysis.", BODY),

        Paragraph("Completeness and validity", H1),
        table(
            ["Check", "Result", "Assessment"],
            [
                ["Rows", f"{M['rows_raw']:,} raw, {M['rows_analysed']:,} analysed", "One duplicate pair removed"],
                ["Missing values", f"{M['null_count']} across all columns", "Implausibly clean for real data"],
                ["Impossible values", "None", "No negative charges, no zero BMI"],
                ["Age range", "18 to 64", "Within plausible bounds"],
                ["Sex balance", "676 male / 662 female", "Near-perfect"],
                ["Region balance", "324 to 364 per region", "Near-perfect"],
                ["Charges skew", f"{M['charges_skew']:.2f}", "Right-skewed, as expected for claims"],
            ],
            [1.35 * inch, 2.15 * inch, 2.9 * inch],
        ),

        Paragraph("Issue 1 — the duplicate pair", H1),
        Paragraph(
            "Rows 195 and 581 are byte-identical: a 19-year-old male non-smoker with BMI 30.59, no "
            "children, in the northwest, charged $1,639.56. Because the file carries no member "
            "identifier, a genuine coincidence and a duplication error are indistinguishable. One "
            "copy was removed. The effect on published figures is negligible — total spend falls by "
            "0.009% — but the removal is documented because silent row-dropping is how analyses "
            "become irreproducible.", BODY),

        Paragraph("Issue 2 — ages 18 and 19 are over-sampled", H1),
        Paragraph(
            "The file contains 69 members aged 18 and 68 aged 19, against a flat count of roughly 28 "
            "for every other age from 20 to 64. This is a sampling artifact rather than a population "
            "characteristic. Any unweighted trend across age inherits the bias, which is one reason "
            "the age analysis in this project reports the gap between smoker and non-smoker cost "
            "rather than the absolute level.", BODY),

        PageBreak(),

        Paragraph("Issue 3 — the BMI 30 discontinuity", H1),
        Paragraph(
            "This is the finding that looks strongest and is least trustworthy, and it is worth "
            "setting out in full because a portfolio reader who recognises the dataset will be "
            "looking for it.", BODY),
        Paragraph(
            "Fitting a simple linear trend within each side of the BMI 30 boundary, separately for "
            "smokers and non-smokers, gives the following.", BODY),
        table(
            ["Group", "Slope below 30", "Slope above 30", "Step at the boundary", "n below / above"],
            [
                ["Smokers", usd(sm["slope_below"]) + " per BMI point", usd(sm["slope_above"]) + " per point",
                 usd(sm["step_at_cutoff"]), f"{sm['n_below']} / {sm['n_above']}"],
                ["Non-smokers", usd(ns["slope_below"]) + " per BMI point", usd(ns["slope_above"]) + " per point",
                 usd(ns["step_at_cutoff"]), f"{ns['n_below']} / {ns['n_above']}"],
            ],
            [0.95 * inch, 1.5 * inch, 1.35 * inch, 1.35 * inch, 1.25 * inch],
            aligns=[1, 2, 3, 4],
        ),
        Spacer(1, 12),
        Paragraph(
            f"Among smokers the within-band gradient is roughly {usd(sm['slope_below'])} per BMI point "
            f"below the cutoff and {usd(sm['slope_above'])} above it — almost unchanged. Yet crossing "
            f"the boundary itself is associated with {usd(sm['step_at_cutoff'])}. A biological "
            f"dose-response relationship does not behave like this. Metabolic risk rises "
            f"continuously with adiposity; it does not wait at BMI 29.9 and then discharge twenty "
            f"thousand dollars at 30.0.", BODY),
        figure("bmi-threshold.png"),
        Paragraph(
            "The smoker series is essentially flat within each side of the cutoff and jumps across it.", CAP),
        callout(
            "<b>Conclusion.</b> The threshold is a rule in the data generator, not a property of "
            "human physiology. Any eligibility criterion, saving estimate or risk score built on "
            "BMI 30 in this dataset inherits the artifact. The weight-programme lever aimed at obese "
            "smokers is scored low-confidence for exactly this reason, despite showing the second "
            "largest theoretical ceiling in the analysis."),

        PageBreak(),

        Paragraph("Issue 4 — a quarter of the variance is not in the file", H1),
        Paragraph(
            "An ordinary least squares model on all six available inputs, with categorical variables "
            "one-hot encoded and no interaction terms, reaches R&sup2; = 0.75. The residual is not "
            "randomly distributed. Eighty members sit more than $10,000 above their predicted cost.", BODY),
        Paragraph(
            f"The clearest sub-group is {u['high_cost_non_smokers']} non-smokers billing over $30,000 "
            f"— {u['high_cost_non_smokers'] / u['non_smoker_total'] * 100:.2f}% of all non-smokers, "
            f"accounting for {kusd(u['their_spend'])} or {u['pct_of_book']:.1f}% of the book. Their "
            f"profiles are unremarkable: mostly aged 44 to 64, BMI between 24.7 and 37.7, spread "
            f"across all four regions. Nothing in the available columns distinguishes them from "
            f"members costing a fifth as much.", BODY),
        Paragraph(
            "In a real book this is where a chronic condition registry, an inpatient admission flag "
            "or a claims history would sit. Its absence is the single most valuable thing this "
            "analysis reveals about the data collection, and it is why instrumenting the dataset is "
            "ranked third among the levers despite generating no direct saving of its own.", BODY),

        Paragraph("What the file cannot support", H1),
        Paragraph("&bull; <b>Any causal claim.</b> No time dimension, no baseline, no control.", BULLET),
        Paragraph("&bull; <b>Any trend or before-and-after comparison.</b> No dates.", BULLET),
        Paragraph("&bull; <b>Any per-member tracking.</b> No identifier.", BULLET),
        Paragraph("&bull; <b>Any cost driver analysis.</b> One aggregate charge, no claim lines, no diagnosis.", BULLET),
        Paragraph("&bull; <b>Any external benchmarking.</b> Charges are in an unstated price year.", BULLET),
        Paragraph("&bull; <b>Any conclusion about smoking intensity.</b> The field is a self-reported binary.", BULLET),

        Spacer(1, 14),
        Paragraph(
            "Ten questions covering what would need to be collected to answer the above are set out "
            "on the project dashboard, each with a metric, a measurement window and the decision it "
            "would settle.", BODY),
    ]
    build("data-quality-and-artifacts.pdf", "Data quality and the BMI 30 artifact",
          "Profiling, duplicate handling, sampling bias, and the discontinuity that identifies "
          "this dataset as simulated.", s)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    executive_summary()
    segmentation()
    data_quality()
