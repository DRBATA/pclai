import React, { useMemo, useState } from "react";

// Surgical Intake & Decision-Support Form (Prostate)
// Plain React (no Tailwind). Designed as an embeddable widget for clinics.
// - Collects key parameters (PSA, PSAD, PI-RADS, lesion size, Gleason, stage, PSA velocity)
// - Auto-computes PSA Density from PSA and prostate volume when possible
// - Computes transparent, non-prescriptive utilities for AS vs Surgery
// - NEW: Adds MRI_FUSION_INDICATIONS and HIFU_ELIGIBILITY calculators with evidence-tagged weights
// - Emits de-identified agent payload + human-readable summary
// - Built-in guardrails: missing-critical-inputs, evidence disclaimer, availability flags
// NOTE: Weights are placeholders matching your spec; calibrate with surgeons + local data.

const styles = {
  app: { fontFamily: "Inter, system-ui, Segoe UI, Roboto, Helvetica, Arial, sans-serif", color: "#0e1726", background: "#f7f9fc", minHeight: "100vh", padding: 16 },
  card: { background: "#fff", border: "1px solid #e6eaf2", borderRadius: 12, padding: 16, boxShadow: "0 8px 24px rgba(16,24,40,0.06)", marginBottom: 16 },
  h1: { fontSize: 20, margin: 0, marginBottom: 8 },
  h2: { fontSize: 16, margin: 0, marginBottom: 10, color: "#1849a9" },
  row: { display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(240px,1fr))", gap: 12 },
  field: { display: "flex", flexDirection: "column", gap: 6 },
  label: { fontSize: 13, color: "#475467" },
  input: { border: "1px solid #d0d5dd", borderRadius: 8, padding: "8px 10px", fontSize: 14, outline: "none" },
  select: { border: "1px solid #d0d5dd", borderRadius: 8, padding: "8px 10px", fontSize: 14, outline: "none", background: "white" },
  small: { fontSize: 12, color: "#667085" },
  pillRow: { display: "flex", gap: 8, flexWrap: "wrap" },
  pill: { border: "1px solid #d0d5dd", padding: "6px 10px", borderRadius: 999, fontSize: 12, background: "#f8fafc" },
  slider: { width: "100%" },
  btnRow: { display: "flex", gap: 8, flexWrap: "wrap", marginTop: 10 },
  btn: { border: "1px solid #1849a9", background: "#1849a9", color: "#fff", borderRadius: 10, padding: "8px 12px", cursor: "pointer" },
  ghost: { border: "1px solid #d0d5dd", background: "#fff", color: "#0e1726", borderRadius: 10, padding: "8px 12px", cursor: "pointer" },
  code: { background: "#0b1226", color: "#e6edf7", padding: 12, borderRadius: 10, fontSize: 12, overflowX: "auto" },
  warn: { background: "#fff7ed", border: "1px solid #fed7aa", color: "#9a3412", padding: 10, borderRadius: 10 },
  ok: { background: "#ecfdf3", border: "1px solid #bbf7d0", color: "#065f46", padding: 10, borderRadius: 10 },
  tag: { display: "inline-block", fontSize: 12, background: "#eef2ff", color: "#3730a3", padding: "2px 8px", borderRadius: 999, border: "1px solid #c7d2fe", marginRight: 6 },
};

const initial = {
  // Demographics & comorbidity
  age: "",
  comorbidity: "low", // low | moderate | high

  // Labs and imaging
  psa: "", // ng/mL
  prostateVolume: "", // cc (mL)
  psaDensity: "", // computed if possible
  psaVelocity: "", // ng/mL/year
  piradsMax: "4", // 1..5
  lesionSizeMm: "", // mm
  gleason: "3+4", // 3+3, 3+4, 4+3, >=8
  clinicalStage: "T2", // T1, T2, T3

  // Availability flags (site-level)
  fusionSoftwareAvailable: true,
  hifuAvailable: false,

  // Contra/risk flags
  onAnticoagulants: false,
  activeUTI: false,
  priorPelvicRadiation: false,

  // Patient prefs (0..1)
  prefUrinary: 0.5,
  prefSexual: 0.5,
  prefAvoidOvertreat: 0.5,
};

// --- Conservative default weights (placeholder) ---
// These are simple illustrative contributions to a relative utility, not clinical probabilities.
const DEFAULT_WEIGHTS = {
  // Harm multipliers for AS (risk of progression/upgrading)
  AS_progression_lr: (psad, pirads, gleason) => {
    let lr = 1.0;
    if (psad >= 0.15) lr *= 2.0; // NICE flag
    if (Number(pirads) >= 5) lr *= 1.5;
    if (["4+3", ">=8", "8", "9", "10"].includes(String(gleason))) lr *= 2.0;
    if (String(gleason) === "3+3") lr *= 0.7;
    return lr;
  },
  // Benefit/harms Surgery (RP) with basic age/comorbidity scaling
  RP_cancer_control: (gleason, pirads) => {
    let b = 0.25; // base benefit unit
    if (["4+3", ">=8"].includes(String(gleason))) b += 0.15;
    if (Number(pirads) >= 5) b += 0.1;
    return b; // higher = more benefit
  },
  RP_harms: (age, comorbidity, prefs) => {
    const a = Number(age || 0);
    const com = { low: 0, moderate: 0.08, high: 0.15 }[comorbidity] ?? 0;
    // Disutility scaled by patient sensitivity to urinary/sexual outcomes
    const prefScale = 0.5 * (Number(prefs.prefUrinary) + Number(prefs.prefSexual));
    let harm = 0.18 + com + prefScale; // base + comorbidity + preference weight
    if (a >= 70) harm += 0.07; // age effect
    return harm; // higher = more harm
  },
};

// === Evidence-tagged calculators as specified ===
const MRI_FUSION_SPEC = {
  name: "MRI_FUSION_INDICATIONS",
  decisions: [{ name: "Discuss_MRI_Fusion_Biopsy", output_weight: 1.0, consent_template: "Consent_Biopsy@v1.1" }],
  criteria: [{ key: "Indication_High_MRI_Fusion", supports: [
    { feature: "PIRADS", threshold: 4, lr: 3.2, weight: 1.3, evidence: "EAU-2025-PI-RADS" },
    { feature: "PSAD", threshold: 0.15, lr: 2.5, weight: 1.0, evidence: "NICE-NG131-2024" },
    { feature: "PSAV", threshold: 1.5, lr: 1.8, weight: 0.6, evidence: "Carter-JAMA-2021" },
    { feature: "LESION", threshold: 8, lr: 1.7, weight: 0.5, evidence: "Radiology-2020-Mehralivand" },
  ]}],
  thresholds: { score_low: 0.5, score_high: 1.5 },
};

const HIFU_SPEC = {
  name: "HIFU_ELIGIBILITY",
  decisions: [{ name: "Discuss_Focal_HIFU", output_weight: 1.0, consent_template: "Consent_HIFU@v1.3" }],
  criteria: [{ key: "Eligibility_HIFU_Focal", supports: [
    { feature: "PIRADS", threshold: 4, lr: 1.6, weight: 0.6, evidence: "EAU-2023" },
    { feature: "LESION", threshold: 8, lr: 1.9, weight: 0.8, evidence: "Ahmed-2021-LancetOnc" },
    { feature: "GLEASON_MAX", threshold: 7, lr: 2.1, weight: 0.9, evidence: "EAU-2023" },
  ]}],
  thresholds: { score_low: 0.4, score_high: 1.3 },
  contraindications: [{ decision: "Discuss_Focal_HIFU", feature: "PROSTATE_VOL", op: ">", value: 60, weight: 0.8, evidence: "EAU-2023" }],
};

function clamp01(x){ return Math.max(0, Math.min(1, x)); }

function numberOrNull(v){
  if (v === null || v === undefined || v === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

function fmt(n, d=2){
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return Number(n).toFixed(d);
}

function log10(x){ return Math.log(x) / Math.log(10); }

function meets(feature, threshold, value){
  if (value === null || value === undefined) return false;
  // For this spec, all thresholds are interpreted as ">=" unless noted
  return Number(value) >= Number(threshold);
}

function gleasonLeq7(gleasonStr){
  // interpret threshold 7 as <=7 (3+3, 3+4). Treat 4+3 and >=8 as >7
  const g = String(gleasonStr || "");
  if (g === "3+3" || g === "3+4") return true;
  return false;
}

export default function SurgicalIntakeForm(){
  const [form, setForm] = useState(initial);
  const [outJson, setOutJson] = useState("");

  // Compute PSA density if PSA & volume available
  const computedPSAD = useMemo(() => {
    const psa = numberOrNull(form.psa);
    const vol = numberOrNull(form.prostateVolume);
    if (psa !== null && vol && vol > 0) {
      return psa / vol; // ng/mL per cc
    }
    return null;
  }, [form.psa, form.prostateVolume]);

  // Effective psad used (prefer explicit number if entered)
  const psadEff = useMemo(() => {
    const entered = numberOrNull(form.psaDensity);
    return entered !== null ? entered : computedPSAD;
  }, [form.psaDensity, computedPSAD]);

  const criticalMissing = useMemo(() => {
    const missing = [];
    if (!form.age) missing.push("age");
    if (!form.piradsMax) missing.push("PI-RADS");
    if (!form.gleason) missing.push("Gleason");
    if (!form.clinicalStage) missing.push("clinical stage");
    if (psadEff === null) missing.push("PSA density (enter or provide PSA + volume)");
    // For MRI fusion calculator, PSA velocity and lesion size improve confidence
    if (form.psaVelocity === "") missing.push("PSA velocity");
    if (form.lesionSizeMm === "") missing.push("lesion size");
    return missing;
  }, [form, psadEff]);

  // --- Non-prescriptive AS vs Surgery sketch ---
  const scores = useMemo(() => {
    const baseAS = 0.6;
    const lr = DEFAULT_WEIGHTS.AS_progression_lr(psadEff ?? 0, form.piradsMax, form.gleason);
    const asHarm = 0.15 * (lr - 1);
    const asPref = 0.25 * clamp01(Number(form.prefAvoidOvertreat));
    const AS = baseAS + asPref - asHarm;

    const rpBenefit = DEFAULT_WEIGHTS.RP_cancer_control(form.gleason, form.piradsMax);
    const rpHarm = DEFAULT_WEIGHTS.RP_harms(form.age, form.comorbidity, { prefUrinary: form.prefUrinary, prefSexual: form.prefSexual });
    const RP = 0.4 + rpBenefit - rpHarm;

    const tr = [
      { key: "psa_density", value: psadEff, note: `PSAD used = ${fmt(psadEff,3)} ng/mL/cc` },
      { key: "pirads_max", value: form.piradsMax, note: `PI-RADS ${form.piradsMax}` },
      { key: "gleason", value: form.gleason, note: `Gleason ${form.gleason}` },
      { key: "rp_benefit", value: rpBenefit, note: `RP cancer-control benefit proxy = ${fmt(rpBenefit,2)}` },
      { key: "rp_harm", value: rpHarm, note: `RP harm proxy (age/comorb/prefs) = ${fmt(rpHarm,2)}` },
      { key: "as_lr", value: lr, note: `AS progression LR proxy = ${fmt(lr,2)}` },
      { key: "as_pref_avoid_overtx", value: form.prefAvoidOvertreat, note: `Preference to avoid overtreatment = ${fmt(form.prefAvoidOvertreat,2)}` },
    ];

    return { AS, RP, trace: tr };
  }, [form, psadEff]);

  // --- MRI_FUSION_INDICATIONS calculator ---
  const mriFusion = useMemo(() => {
    const s = MRI_FUSION_SPEC;
    const sup = s.criteria[0].supports;
    const piradsMet = meets("PIRADS", 4, Number(form.piradsMax));
    const psadMet = meets("PSAD", 0.15, psadEff);
    const psavMet = meets("PSAV", 1.5, numberOrNull(form.psaVelocity));
    const lesionMet = meets("LESION", 8, numberOrNull(form.lesionSizeMm));

    const parts = [];
    if (piradsMet) parts.push({ label: "PI-RADS ≥4", add: sup[0].weight + log10(sup[0].lr), ev: sup[0].evidence });
    if (psadMet) parts.push({ label: "PSAD ≥0.15", add: sup[1].weight + log10(sup[1].lr), ev: sup[1].evidence });
    if (psavMet) parts.push({ label: "PSA velocity ≥1.5/yr", add: sup[2].weight + log10(sup[2].lr), ev: sup[2].evidence });
    if (lesionMet) parts.push({ label: "Lesion ≥8 mm", add: sup[3].weight + log10(sup[3].lr), ev: sup[3].evidence });

    const raw = s.decisions[0].output_weight + parts.reduce((a,b)=> a + b.add, 0);
    const band = raw >= s.thresholds.score_high ? "strong" : raw >= s.thresholds.score_low ? "consider" : "weak";

    const siteBlock = !form.fusionSoftwareAvailable ? "Fusion software not available on site" : null;

    return {
      name: s.name,
      decision: s.decisions[0],
      rawScore: Number(raw.toFixed(3)),
      band,
      met: { piradsMet, psadMet, psavMet, lesionMet },
      parts,
      thresholds: s.thresholds,
      siteBlock,
    };
  }, [form.piradsMax, psadEff, form.psaVelocity, form.lesionSizeMm, form.fusionSoftwareAvailable]);

  // --- HIFU_ELIGIBILITY calculator ---
  const hifu = useMemo(() => {
    const s = HIFU_SPEC;
    const sup = s.criteria[0].supports;
    const piradsMet = meets("PIRADS", 4, Number(form.piradsMax));
    const lesionVal = numberOrNull(form.lesionSizeMm);
    const lesionMet = meets("LESION", 8, lesionVal);
    const gleasonMet = gleasonLeq7(form.gleason); // ≤7 interpreted

    const parts = [];
    if (piradsMet) parts.push({ label: "PI-RADS ≥4", add: sup[0].weight + log10(sup[0].lr), ev: sup[0].evidence });
    if (lesionMet) parts.push({ label: "Lesion ≥8 mm", add: sup[1].weight + log10(sup[1].lr), ev: sup[1].evidence });
    if (gleasonMet) parts.push({ label: "Gleason ≤7 (3+3/3+4)", add: sup[2].weight + log10(sup[2].lr), ev: sup[2].evidence });

    let raw = s.decisions[0].output_weight + parts.reduce((a,b)=> a + b.add, 0);

    // Contraindication: PROSTATE_VOL > 60 subtracts weight
    const vol = numberOrNull(form.prostateVolume);
    const contraHit = vol !== null && vol > 60;
    if (contraHit){ raw -= s.contraindications[0].weight; }

    const band = raw >= s.thresholds.score_high ? "strong" : raw >= s.thresholds.score_low ? "consider" : "weak";

    const siteBlock = !form.hifuAvailable ? "HIFU not available on site" : null;

    // Optional window note: ideal lesion window 8–15 mm (informational only)
    const windowNote = lesionVal !== null ? (lesionVal >= 8 && lesionVal <= 15 ? "Lesion size in ideal focal window (8–15 mm)" : lesionVal > 15 ? "Lesion >15 mm — focal margins may be challenging" : "Lesion <8 mm — lower HIFU yield") : null;

    return {
      name: s.name,
      decision: s.decisions[0],
      rawScore: Number(raw.toFixed(3)),
      band,
      met: { piradsMet, lesionMet, gleasonMet },
      parts,
      thresholds: s.thresholds,
      siteBlock,
      contraHit,
      windowNote,
    };
  }, [form.piradsMax, form.lesionSizeMm, form.gleason, form.prostateVolume, form.hifuAvailable]);

  const ranking = useMemo(() => {
    const entries = [ ["ACTIVE_SURVEILLANCE", scores.AS], ["SURGERY_RP", scores.RP] ];
    entries.sort((a,b)=> b[1]-a[1]);
    return entries;
  }, [scores]);

  function update(k, v){ setForm(prev => ({ ...prev, [k]: v })); }

  function exportPayload(){
    const payload = {
      mode: "intake_decision_support_v2",
      inputs: {
        age: numberOrNull(form.age),
        psa: numberOrNull(form.psa),
        prostate_volume_cc: numberOrNull(form.prostateVolume),
        psa_density: psadEff,
        psa_velocity_per_year: numberOrNull(form.psaVelocity),
        pirads_max: Number(form.piradsMax),
        lesion_size_mm: numberOrNull(form.lesionSizeMm),
        gleason: form.gleason,
        clinical_stage: form.clinicalStage,
        comorbidity: form.comorbidity,
        availability: {
          fusion_software: !!form.fusionSoftwareAvailable,
          hifu: !!form.hifuAvailable,
        },
        contraindications: {
          anticoagulants: !!form.onAnticoagulants,
          active_uti: !!form.activeUTI,
          prior_pelvic_radiation: !!form.priorPelvicRadiation,
          large_prostate_volume_gt60: numberOrNull(form.prostateVolume) !== null && numberOrNull(form.prostateVolume) > 60,
        },
        preferences: {
          urinary: clamp01(Number(form.prefUrinary)),
          sexual: clamp01(Number(form.prefSexual)),
          avoid_overtreatment: clamp01(Number(form.prefAvoidOvertreat)),
        },
      },
      result: {
        summary_scores: { ACTIVE_SURVEILLANCE: Number(scores.AS.toFixed(3)), SURGERY_RP: Number(scores.RP.toFixed(3)) },
        calculators: {
          MRI_FUSION_INDICATIONS: {
            decision: mriFusion.decision.name,
            consent_template: mriFusion.decision.consent_template,
            raw_score: mriFusion.rawScore,
            band: mriFusion.band,
            thresholds: mriFusion.thresholds,
            site_block: mriFusion.siteBlock,
            parts: mriFusion.parts,
          },
          HIFU_ELIGIBILITY: {
            decision: hifu.decision.name,
            consent_template: hifu.decision.consent_template,
            raw_score: hifu.rawScore,
            band: hifu.band,
            thresholds: hifu.thresholds,
            site_block: hifu.siteBlock,
            contraindication_large_prostate_gt60: hifu.contraHit,
            parts: hifu.parts,
            window_note: hifu.windowNote,
          },
        },
        rank_order: ranking.map(([k])=>k),
        margin: Number((ranking[0][1]-ranking[1][1]).toFixed(3)),
        confidence: criticalMissing.length ? "low" : "moderate",
        disclaimers: [
          "For decision support only — not a medical directive.",
          "Scores reflect feature-threshold matches using evidence-tagged weights (non-probabilistic).",
          "Calibrate thresholds/weights to local outcomes and MDT consensus.",
        ],
      },
    };
    setOutJson(JSON.stringify(payload, null, 2));
  }

  function copy(){ if (outJson) navigator.clipboard.writeText(outJson); }

  return (
    <div style={styles.app}>
      <div style={styles.card}>
        <h1 style={styles.h1}>Prostate Intake — Decision-Support (AS vs Surgery + Biopsy/HIFU)</h1>
        <div style={styles.pillRow}>
          <span style={styles.pill}>⚖️ Decision support only</span>
          <span style={styles.pill}>🔒 No PHI required</span>
          <span style={styles.pill}>🧪 PSA density auto-calculated</span>
        </div>
      </div>

      <div style={styles.card}>
        <h2 style={styles.h2}>1) Patient & Disease Parameters</h2>
        <div style={styles.row}>
          <div style={styles.field}><label style={styles.label}>Age (years)</label>
            <input style={styles.input} type="number" min={18} max={99} value={form.age} onChange={e=>update("age", e.target.value)} /></div>
          <div style={styles.field}><label style={styles.label}>Comorbidity</label>
            <select style={styles.select} value={form.comorbidity} onChange={e=>update("comorbidity", e.target.value)}>
              <option value="low">Low</option>
              <option value="moderate">Moderate</option>
              <option value="high">High</option>
            </select></div>
          <div style={styles.field}><label style={styles.label}>PSA (ng/mL)</label>
            <input style={styles.input} type="number" step="0.1" value={form.psa} onChange={e=>update("psa", e.target.value)} /></div>
          <div style={styles.field}><label style={styles.label}>Prostate Volume (cc)</label>
            <input style={styles.input} type="number" step="1" value={form.prostateVolume} onChange={e=>update("prostateVolume", e.target.value)} /></div>
          <div style={styles.field}><label style={styles.label}>PSA Density (ng/mL/cc)</label>
            <input style={styles.input} type="number" step="0.01" value={form.psaDensity} onChange={e=>update("psaDensity", e.target.value)} placeholder={computedPSAD?`Auto: ${fmt(computedPSAD,3)}`:"Enter or provide PSA+Volume"} /></div>
          <div style={styles.field}><label style={styles.label}>PSA Velocity (ng/mL/year)</label>
            <input style={styles.input} type="number" step="0.1" value={form.psaVelocity} onChange={e=>update("psaVelocity", e.target.value)} placeholder="e.g. 1.5" /></div>
          <div style={styles.field}><label style={styles.label}>PI‑RADS (max)</label>
            <select style={styles.select} value={form.piradsMax} onChange={e=>update("piradsMax", e.target.value)}>
              {[1,2,3,4,5].map(n=> <option key={n} value={String(n)}>{n}</option>)}
            </select></div>
          <div style={styles.field}><label style={styles.label}>Lesion Size (mm)</label>
            <input style={styles.input} type="number" step="1" value={form.lesionSizeMm} onChange={e=>update("lesionSizeMm", e.target.value)} /></div>
          <div style={styles.field}><label style={styles.label}>Gleason</label>
            <select style={styles.select} value={form.gleason} onChange={e=>update("gleason", e.target.value)}>
              <option>3+3</option>
              <option>3+4</option>
              <option>4+3</option>
              <option>&gt;=8</option>
            </select></div>
          <div style={styles.field}><label style={styles.label}>Clinical Stage</label>
            <select style={styles.select} value={form.clinicalStage} onChange={e=>update("clinicalStage", e.target.value)}>
              <option>T1</option>
              <option>T2</option>
              <option>T3</option>
            </select></div>
        </div>
        <div style={{ marginTop: 8, color: "#475467", fontSize: 12 }}>
          PSA Density used: <strong>{fmt(psadEff,3)}</strong> ng/mL/cc {computedPSAD!==null && form.psaDensity==="" ? <span>(auto from PSA/volume)</span> : null}
        </div>
      </div>

      <div style={styles.card}>
        <h2 style={styles.h2}>2) Site Availability & Contraindications</h2>
        <div style={styles.row}>
          <div style={styles.field}><label style={styles.label}><input type="checkbox" checked={form.fusionSoftwareAvailable} onChange={e=>update("fusionSoftwareAvailable", e.target.checked)} /> MR/US Fusion Software Available</label></div>
          <div style={styles.field}><label style={styles.label}><input type="checkbox" checked={form.hifuAvailable} onChange={e=>update("hifuAvailable", e.target.checked)} /> HIFU Available</label></div>
          <div style={styles.field}><label style={styles.label}><input type="checkbox" checked={form.onAnticoagulants} onChange={e=>update("onAnticoagulants", e.target.checked)} /> On Anticoagulants</label></div>
          <div style={styles.field}><label style={styles.label}><input type="checkbox" checked={form.activeUTI} onChange={e=>update("activeUTI", e.target.checked)} /> Active UTI</label></div>
          <div style={styles.field}><label style={styles.label}><input type="checkbox" checked={form.priorPelvicRadiation} onChange={e=>update("priorPelvicRadiation", e.target.checked)} /> Prior Pelvic Radiation</label></div>
        </div>
      </div>

      <div style={styles.card}>
        <h2 style={styles.h2}>3) Patient Preferences (0 = not concerned, 1 = highly concerned)</h2>
        <div style={styles.row}>
          <div style={styles.field}><label style={styles.label}>Urinary function</label>
            <input style={styles.slider} type="range" min={0} max={1} step={0.05} value={form.prefUrinary} onChange={e=>update("prefUrinary", e.target.value)} />
            <small style={styles.small}>{fmt(form.prefUrinary,2)}</small></div>
          <div style={styles.field}><label style={styles.label}>Sexual function</label>
            <input style={styles.slider} type="range" min={0} max={1} step={0.05} value={form.prefSexual} onChange={e=>update("prefSexual", e.target.value)} />
            <small style={styles.small}>{fmt(form.prefSexual,2)}</small></div>
          <div style={styles.field}><label style={styles.label}>Avoid overtreatment</label>
            <input style={styles.slider} type="range" min={0} max={1} step={0.05} value={form.prefAvoidOvertreat} onChange={e=>update("prefAvoidOvertreat", e.target.value)} />
            <small style={styles.small}>{fmt(form.prefAvoidOvertreat,2)}</small></div>
        </div>
      </div>

      <div style={styles.card}>
        <h2 style={styles.h2}>4) Non‑prescriptive Scoring (AS vs Surgery)</h2>
        {criticalMissing.length ? (
          <div style={styles.warn}><strong>Low confidence.</strong> Missing: {criticalMissing.join(", ")}. Add these before using results for clinical discussion.</div>
        ) : (
          <div style={styles.ok}>Inputs present for a preview comparison. This is decision support, not a directive.</div>
        )}
        <div style={{ display: "flex", gap: 12, marginTop: 10, flexWrap: "wrap" }}>
          <div style={{ ...styles.card, flex: "1 1 240px", margin: 0 }}>
            <div style={{ fontSize: 13, color: "#475467", marginBottom: 6 }}>ACTIVE SURVEILLANCE (relative utility)</div>
            <div style={{ fontSize: 28, fontWeight: 700 }}>{fmt(scores.AS, 3)}</div>
            <div style={{ marginTop: 8 }}>
              <span style={styles.tag}>PSAD {fmt(psadEff,3)}</span>
              <span style={styles.tag}>PI‑RADS {form.piradsMax}</span>
              <span style={styles.tag}>Gleason {form.gleason}</span>
            </div>
          </div>
          <div style={{ ...styles.card, flex: "1 1 240px", margin: 0 }}>
            <div style={{ fontSize: 13, color: "#475467", marginBottom: 6 }}>SURGERY / RP (relative utility)</div>
            <div style={{ fontSize: 28, fontWeight: 700 }}>{fmt(scores.RP, 3)}</div>
            <div style={{ marginTop: 8 }}>
              <span style={styles.tag}>Age {form.age || "?"}</span>
              <span style={styles.tag}>Comorbidity {form.comorbidity}</span>
              <span style={styles.tag}>PI‑RADS {form.piradsMax}</span>
            </div>
          </div>
        </div>
      </div>

      <div style={styles.card}>
        <h2 style={styles.h2}>5) Calculators — MRI Fusion & HIFU</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(280px,1fr))", gap: 12 }}>
          <div style={{ ...styles.card, margin: 0 }}>
            <div style={{ fontSize: 13, color: "#475467", marginBottom: 6 }}>MRI_FUSION_INDICATIONS → {mriFusion.decision.name}</div>
            <div><strong>Raw score:</strong> {fmt(mriFusion.rawScore,3)} <span style={styles.tag}>{mriFusion.band}</span></div>
            {mriFusion.siteBlock ? <div style={styles.warn}>{mriFusion.siteBlock}</div> : null}
            <div style={{ marginTop: 6, fontSize: 12, color: "#475467" }}>Thresholds: low ≥ {mriFusion.thresholds.score_low}, high ≥ {mriFusion.thresholds.score_high}</div>
            <ul style={{ margin: 0, paddingLeft: 16, marginTop: 6 }}>
              {mriFusion.parts.map((p,i)=>(<li key={i} style={{ fontSize: 12 }}>{p.label} → +{fmt(p.add,2)} <em style={{ color: "#64748b" }}>({p.ev})</em></li>))}
              {mriFusion.parts.length===0 ? <li style={{ fontSize: 12, color: "#64748b" }}>No feature thresholds met.</li> : null}
            </ul>
          </div>
          <div style={{ ...styles.card, margin: 0 }}>
            <div style={{ fontSize: 13, color: "#475467", marginBottom: 6 }}>HIFU_ELIGIBILITY → {hifu.decision.name}</div>
            <div><strong>Raw score:</strong> {fmt(hifu.rawScore,3)} <span style={styles.tag}>{hifu.band}</span></div>
            {hifu.siteBlock ? <div style={styles.warn}>{hifu.siteBlock}</div> : null}
            {hifu.contraHit ? <div style={styles.warn}>Relative contraindication applied: Prostate volume &gt; 60 cc (−{HIFU_SPEC.contraindications[0].weight})</div> : null}
            {hifu.windowNote ? <div style={styles.ok}>{hifu.windowNote}</div> : null}
            <div style={{ marginTop: 6, fontSize: 12, color: "#475467" }}>Thresholds: low ≥ {hifu.thresholds.score_low}, high ≥ {hifu.thresholds.score_high}</div>
            <ul style={{ margin: 0, paddingLeft: 16, marginTop: 6 }}>
              {hifu.parts.map((p,i)=>(<li key={i} style={{ fontSize: 12 }}>
                {p.label} → +{fmt(p.add,2)} <em style={{ color: "#64748b" }}>({p.ev})</em>
              </li>))}
              {hifu.parts.length===0 ? <li style={{ fontSize: 12, color: "#64748b" }}>No feature thresholds met.</li> : null}
            </ul>
          </div>
        </div>
      </div>

      <div style={styles.card}>
        <div style={styles.btnRow}>
          <button style={styles.btn} onClick={exportPayload}>Export Agent JSON</button>
          <button style={styles.ghost} onClick={copy} disabled={!outJson}>Copy</button>
        </div>
      </div>

      {outJson ? (
        <div style={styles.card}>
          <h2 style={styles.h2}>Export</h2>
          <pre style={styles.code}>{outJson}</pre>
          <div style={{ fontSize: 12, color: "#667085", marginTop: 8 }}>
            Disclaimers:
            <ul>
              <li>For decision support/education. Not medical advice. Consult a urologist/MDT.</li>
              <li>Scores reflect feature-threshold matches using evidence-tagged weights (non-probabilistic).</li>
              <li>HIFU/fusion availability toggles are site-level constraints and may alter pathways.</li>
            </ul>
          </div>
        </div>
      ) : null}

      <div style={{ ...styles.card, background: "#f8fafc" }}>
        <div style={{ fontSize: 12, color: "#475467" }}>
          <strong>Implementation notes:</strong> Hook this component into your booking/orchestration layer to:
          <ol>
            <li>Send the exported JSON to your agent for stratified evidence + counselling text.</li>
            <li>If confidence is low or margin is small, auto-flag for nurse specialist review.</li>
            <li>If HIFU unavailable but eligible, suggest specialist referral, else alternative pathways.</li>
            <li>Store only de-identified features; PHI stays with the surgeon’s EMR.</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
