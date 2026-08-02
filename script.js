const MID = "#8494a0";
const HIGH = "#a63a4a";
const MUTED = "#63757f";
const LINE = "#d3dce2";

const usd0 = new Intl.NumberFormat("en-US", {
  style: "currency", currency: "USD", maximumFractionDigits: 0,
});

function compactUsd(v) {
  if (Math.abs(v) >= 1e6) return "$" + (v / 1e6).toFixed(2) + "M";
  if (Math.abs(v) >= 1e3) return "$" + Math.round(v / 1e3) + "k";
  return usd0.format(v);
}

/* ---------- risk grid interaction ---------- */

const detail = document.getElementById("cellDetail");
const cells = document.querySelectorAll(".cell");

function segmentByName(name) {
  return SUMMARY.segments.find((s) => s.name === name);
}

cells.forEach((cell) => {
  cell.addEventListener("click", () => {
    const active = cell.getAttribute("aria-pressed") === "true";
    cells.forEach((c) => c.setAttribute("aria-pressed", "false"));

    if (active) {
      detail.innerHTML = "Select any cell for the segment detail.";
      return;
    }
    cell.setAttribute("aria-pressed", "true");

    const name = cell.dataset.seg.replace("&lt;", "<");
    const s = segmentByName(name);
    if (!s) return;

    detail.innerHTML =
      `<strong>${s.name}</strong> — ${s.n} members (${s.pct_members.toFixed(1)}% of the book) ` +
      `accounting for <strong>${compactUsd(s.total)}</strong>, or ${s.pct_spend.toFixed(1)}% of ` +
      `total spend. Mean ${usd0.format(s.mean)}, median ${usd0.format(s.median)} — the gap between ` +
      `those two is the segment's internal skew.`;
  });
});

/* ---------- lever table ---------- */

const tagClass = { High: "high", Medium: "med", Low: "low" };
const leverBody = document.getElementById("leverBody");

const rankedLevers = [
  { key: "Smoking cessation - obese smokers", rank: 1 },
  { key: "Smoking cessation - non-obese smokers", rank: 2 },
  { key: "__instrument", rank: 3 },
  { key: "Weight programme - obese smokers", rank: 4 },
  { key: "Weight programme - obese non-smokers", rank: 5 },
];

rankedLevers.forEach((entry) => {
  const tr = document.createElement("tr");

  if (entry.key === "__instrument") {
    tr.innerHTML =
      `<td class="n">3</td>` +
      `<td>Instrument the data — diagnosis codes, dates, member IDs</td>` +
      `<td class="n">—</td>` +
      `<td class="n">unlocks the missing 25%</td>` +
      `<td class="n">—</td>` +
      `<td><span class="tag high">High</span></td>` +
      `<td><span class="tag high">Low</span></td>`;
    leverBody.appendChild(tr);
    return;
  }

  const l = SUMMARY.levers.find((x) => x.lever === entry.key);
  tr.innerHTML =
    `<td class="n">${entry.rank}</td>` +
    `<td>${l.lever.replace(" - ", " — ")}</td>` +
    `<td class="n">${l.n}</td>` +
    `<td class="n">${compactUsd(l.ceiling_saving)} (${l.ceiling_pct_of_book.toFixed(1)}%)</td>` +
    `<td class="n">${compactUsd(l.at_10pct)}</td>` +
    `<td><span class="tag ${tagClass[l.confidence]}">${l.confidence}</span></td>` +
    `<td><span class="tag ${l.effort === "High" ? "low" : "med"}">${l.effort}</span></td>`;
  leverBody.appendChild(tr);
});

/* ---------- questions ---------- */

const QUESTIONS = [
  {
    q: "How concentrated is spend in the obese-smoker segment, and does that hold year to year?",
    metric: "Share of total paid claims from members flagged smoker and BMI ≥ 30.",
    window: "Rolling 12 months, compared across three consecutive plan years.",
    decision: "Whether to ring-fence a dedicated budget line for this segment or fold it into general wellness.",
    status: "Answerable cross-sectionally today (33.9%). The stability half needs three years of data.",
    ok: true,
  },
  {
    q: "Does cessation actually reduce claims, and by how much?",
    metric: "Change in mean per-member paid claims, verified quitters versus a propensity-matched control.",
    window: "12-month pre-enrolment baseline, 24 months post.",
    decision: "Renew, expand or cut the cessation vendor at contract renewal.",
    status: "Needs dated claims and a control group. This is the question the $4.74M ceiling is standing in for.",
  },
  {
    q: "What is the real sustained quit rate?",
    metric: "Percentage of programme enrollees biochemically verified abstinent.",
    window: "Measured at 6 and 12 months post quit-date.",
    decision: "Which vendor to keep, and what uptake assumption goes into the business case.",
    status: "Needs programme enrolment records. The sizing above assumes 10% — this number validates or destroys it.",
  },
  {
    q: "How quickly do savings arrive after someone quits?",
    metric: "Quarterly mean paid claims for verified quitters, indexed to their own pre-quit baseline.",
    window: "Eight quarters post quit-date.",
    decision: "What payback period to commit to, and whether cohort one funds cohort two.",
    status: "Needs longitudinal per-member claims.",
  },
  {
    q: "How wrong is self-reported smoking status?",
    metric: "Discordance rate between declared status and cotinine testing or claims-based tobacco indicators.",
    window: "One annual enrolment cycle.",
    decision: "Keep self-declaration as the targeting field, or pay for verification.",
    status: "Needs verification data. If discordance is high, the 145-member segment is the wrong 145 members.",
  },
  {
    q: "Is there a real BMI threshold, or is 30 an artifact?",
    metric: "Mean annual paid claims per single-point BMI band, smokers and non-smokers computed separately.",
    window: "Three pooled plan years, for cell size.",
    decision: "Set programme eligibility at a BMI cut-off, or move to continuous risk scoring.",
    status: "Partly testable here, and the test fails: the $20,195 step at exactly 30.0 is a generator rule. Real claims data should show a smooth gradient.",
    ok: true,
  },
  {
    q: "What is driving the top spend decile that risk factors do not explain?",
    metric: "Share of top-decile members carrying at least one chronic condition flag or inpatient admission.",
    window: "Rolling 12 months.",
    decision: "Whether to build a chronic-condition registry before the next targeting cycle.",
    status: "Needs diagnosis codes. 25% of variance is currently invisible.",
  },
  {
    q: "Is the southeast concentration a population effect or an access effect?",
    metric: "Obese-smoker prevalence and per-member spend, by region and by ZIP-level deprivation index.",
    window: "Current plan year plus three-year trend.",
    decision: "Weight delivery budget geographically, or run uniform national outreach.",
    status: "Prevalence is answerable today (15.9% versus 8.9%). Separating population from access needs external deprivation data.",
    ok: true,
  },
  {
    q: "Is it better to target young smokers or older ones?",
    metric: "Cumulative modelled paid claims to age 65 for a smoker quitting at 25 versus at 45.",
    window: "40-year projection, calibrated on five years of observed claims.",
    decision: "Where to point outreach spend.",
    status: "The flat age gap found here says the annual saving is the same at every age, which favours the young cohort. Defending that needs a real projection model.",
  },
  {
    q: "Where does the programme funnel leak?",
    metric: "Conversion at each stage: identified → contacted → enrolled → completed → verified quit.",
    window: "Per quarterly cohort, tracked 12 months.",
    decision: "Whether the next marginal dollar goes to targeting, outreach or retention.",
    status: "Needs programme operations data.",
  },
];

const list = document.getElementById("questionList");
QUESTIONS.forEach((item) => {
  const el = document.createElement("article");
  el.className = "q";
  el.innerHTML =
    `<h3>${item.q}</h3>` +
    `<div class="qfields">` +
    `<div><span class="qf-key">Metric</span><span class="qf-val">${item.metric}</span></div>` +
    `<div><span class="qf-key">Window</span><span class="qf-val">${item.window}</span></div>` +
    `<div><span class="qf-key">Decision</span><span class="qf-val">${item.decision}</span></div>` +
    `</div>` +
    `<p class="status${item.ok ? " ok" : ""}">${item.status}</p>`;
  list.appendChild(el);
});

/* ---------- charts ---------- */

const baseScale = {
  ticks: { color: MUTED, font: { size: 11 } },
  grid: { color: LINE, drawTicks: false },
  border: { color: LINE },
};

Chart.defaults.font.family = "'Public Sans', system-ui, sans-serif";

const segOrder = ["Smoker, BMI 30+", "Non-smoker, BMI 30+", "Non-smoker, BMI <30", "Smoker, BMI <30"];
const segRows = segOrder.map((n) => segmentByName(n));

new Chart(document.getElementById("segChart"), {
  type: "bar",
  data: {
    labels: segOrder,
    datasets: [
      {
        label: "Share of members",
        data: segRows.map((s) => Number(s.pct_members.toFixed(1))),
        backgroundColor: MID, borderRadius: 3, barThickness: 18,
      },
      {
        label: "Share of spend",
        data: segRows.map((s) => Number(s.pct_spend.toFixed(1))),
        backgroundColor: HIGH, borderRadius: 3, barThickness: 18,
      },
    ],
  },
  options: {
    indexAxis: "y", responsive: true, maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${c.parsed.x.toFixed(1)}%` } },
    },
    scales: {
      x: { ...baseScale, beginAtZero: true, max: 46,
           ticks: { ...baseScale.ticks, callback: (v) => v + "%" } },
      y: { ...baseScale, grid: { display: false } },
    },
  },
});

new Chart(document.getElementById("bmiChart"), {
  type: "bar",
  data: {
    labels: SUMMARY.bmi_bands.map((b) => b.band),
    datasets: [
      {
        label: "Non-smoker",
        data: SUMMARY.bmi_bands.map((b) => Math.round(b.mean_non_smoker)),
        backgroundColor: MID, borderRadius: 3, barThickness: 26,
      },
      {
        label: "Smoker",
        data: SUMMARY.bmi_bands.map((b) => Math.round(b.mean_smoker)),
        backgroundColor: HIGH, borderRadius: 3, barThickness: 26,
      },
    ],
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${usd0.format(c.parsed.y)}` } },
    },
    scales: {
      y: { ...baseScale, beginAtZero: true,
           ticks: { ...baseScale.ticks, callback: (v) => compactUsd(v) } },
      x: { ...baseScale, grid: { display: false } },
    },
  },
});

new Chart(document.getElementById("ageChart"), {
  type: "line",
  data: {
    labels: SUMMARY.age_bands.map((b) => b.band),
    datasets: [
      {
        label: "Non-smoker",
        data: SUMMARY.age_bands.map((b) => Math.round(b.mean_non_smoker)),
        borderColor: MID, backgroundColor: MID, borderWidth: 2,
        pointRadius: 5, pointStyle: "circle", tension: 0.1,
      },
      {
        label: "Smoker",
        data: SUMMARY.age_bands.map((b) => Math.round(b.mean_smoker)),
        borderColor: HIGH, backgroundColor: HIGH, borderWidth: 2,
        borderDash: [6, 3], pointRadius: 5, pointStyle: "rect", tension: 0.1,
      },
    ],
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (c) => `${c.dataset.label}: ${usd0.format(c.parsed.y)}`,
          afterBody: (items) => {
            const b = SUMMARY.age_bands[items[0].dataIndex];
            return `Gap: ${usd0.format(b.gap)}`;
          },
        },
      },
    },
    scales: {
      y: { ...baseScale, beginAtZero: true,
           ticks: { ...baseScale.ticks, callback: (v) => compactUsd(v) } },
      x: { ...baseScale, grid: { display: false } },
    },
  },
});
