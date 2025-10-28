// differentialCalculations.js
/*
 * This module implements our unified Bayesian differential diagnosis.
 * It includes functions for:
 * - Continuous symptom scoring for gland/pus swelling, fever, etc.
 * - Specific functions for lymph node tenderness and tonsil swelling,
 *   which include strep (and PANDAS) differentiation.
 * - A points table for discrete symptoms and mental/behavioral (PANDAS) features.
 * - A Bayesian update that combines prior probabilities (adjusted by age and contact)
 *   with the symptom‐derived log‑odds, then uses a softmax to generate posterior probabilities.
 * - A final recommendation based on the highest posterior probability and preset thresholds.
 */

const conditions = [
  "strep",
  "ebv",
  "influenza",
  "adenovirus",
  "enterovirus",
  "hmpv",
  "commonCold",
  "rsv",
  "norovirus"
];

// --- Continuous Functions (for gland/pus, fever, tenderness, tonsils) ---

// For lymph node, tonsils, and pus swelling we use a similar formula.
export function calculateContinuousScore(value, symptomId) {
  if (symptomId === "lymphNodes" || symptomId === "tonsils" || symptomId === "pus") {
    return 1 + Math.pow(value / 100, 2);
  }
  if (symptomId === "fever") {
    return value > 36 ? 1 + Math.log(value - 36) : 1;
  }
  return 1;
}

// For gland/pus swelling, we also add a viral component.
export function calculateGlandOrPusStrepLikelihood(swelling) {
  const sigmoid = 0.2 / (1 + Math.exp(-0.1 * (swelling - 70)));
  const gaussian = 0.6 * Math.exp(-Math.pow(swelling - 85, 2) / (2 * 100));
  return Math.max(0, Math.min(1, sigmoid + gaussian));
}

export function calculateGlandOrPusViralLikelihood(swelling) {
  const peakHeight = 0.8;
  const peakPosition = 25;
  const peakWidth = 100;
  const tailHeight = 0.2;
  const tailDecay = 0.05;
  const peak = peakHeight * Math.exp(-Math.pow(swelling - peakPosition, 2) / (2 * peakWidth));
  const tail = tailHeight * Math.exp(-tailDecay * (swelling - peakPosition));
  const y = swelling < peakPosition ? peak : peak + tail;
  return Math.max(0, Math.min(1, y));
}

// Lymph Node Tenderness – measured on a 0–100 scale.
export function calculateLymphNodeTendernessStrepLikelihood(tenderness) {
  // A sigmoid that increases sharply – tenderness is a strong strep indicator.
  const value = 1 / (1 + Math.exp(-0.2 * (tenderness - 20)));
  return Math.max(0, Math.min(1, value));
}

export function calculateLymphNodeTendernessViralLikelihood(tenderness) {
  // Viral tenderness is negligible above ~25%; narrow Gaussian centered at 10.
  if (tenderness > 25) return 0;
  const peak = 1.0;
  const peakPosition = 10;
  const width = 10;
  const value = peak * Math.exp(-Math.pow(tenderness - peakPosition, 2) / (2 * Math.pow(width, 2)));
  return Math.max(0, Math.min(1, value));
}

// Tonsil Swelling
export function calculateTonsilStrepLikelihood(swelling) {
  // Strep: a sigmoid (giving ~20% even at low swelling) plus a wide Gaussian peaking at ~85.
  const sigmoid = 0.2 / (1 + Math.exp(-0.1 * (swelling - 30)));
  const gaussian = 0.6 * Math.exp(-Math.pow(swelling - 85, 2) / (2 * 100));
  return Math.max(0, Math.min(1, sigmoid + gaussian));
}

export function calculateTonsilViralLikelihood(swelling) {
  // Viral: Sum of three Gaussians (slight, moderate, and high swelling) with the high peak 20% lower.
  const gaussian1 = 0.3 * Math.exp(-Math.pow(swelling - 30, 2) / (2 * 100));
  const gaussian2 = 0.3 * Math.exp(-Math.pow(swelling - 50, 2) / (2 * 100));
  const gaussian3 = 0.24 * Math.exp(-Math.pow(swelling - 70, 2) / (2 * 100));
  const value = gaussian1 + gaussian2 + gaussian3;
  return Math.max(0, Math.min(1, value));
}

// --- Discrete and Mental/Behavioral Points Table ---

const symptomPoints = {
  // These points are added to log-odds (you can adjust these values).
  noCough: {
    strep: 3,
    ebv: 1,
    influenza: -3,
    adenovirus: -3,
    enterovirus: -3,
    hmpv: -3,
    commonCold: -3,
    rsv: -3,
    norovirus: 0,
  },
  tonsillarExudates: {
    strep: 3,
    ebv: 2,
    influenza: -2,
    adenovirus: -2,
    enterovirus: -2,
    hmpv: -2,
    commonCold: -2,
    rsv: 0,
    norovirus: 0,
  },
  highFever: {
    strep: 2,
    ebv: 2,
    influenza: 3,
    adenovirus: 1,
    enterovirus: 1,
    hmpv: 1,
    commonCold: 0,
    rsv: 2,
    norovirus: 3,
  },
  extremeFatigue: {
    strep: -1,
    ebv: 4,
    influenza: 2,
    adenovirus: -1,
    enterovirus: -1,
    hmpv: -1,
    commonCold: -1,
    rsv: 0,
    norovirus: 0,
  },
  swollenPosteriorLN: {
    strep: -1,
    ebv: 4,
    influenza: 0,
    adenovirus: 0,
    enterovirus: 0,
    hmpv: 0,
    commonCold: 0,
    rsv: 0,
    norovirus: 0,
  },
  splenomegaly: {
    strep: -1,
    ebv: 3,
    influenza: 0,
    adenovirus: 0,
    enterovirus: 0,
    hmpv: 0,
    commonCold: 0,
    rsv: 0,
    norovirus: 0,
  },
  petechiae: {
    strep: 3,
    ebv: 3,
    influenza: 0,
    adenovirus: 0,
    enterovirus: 0,
    hmpv: 0,
    commonCold: 0,
    rsv: 0,
    norovirus: 0,
  },
  cough: {
    strep: -3,
    ebv: -2,
    influenza: 3,
    adenovirus: 4,
    enterovirus: 3,
    hmpv: 3,
    commonCold: 3,
    rsv: 3,
    norovirus: 0,
  },
  rhinorrhea: {
    strep: -3,
    ebv: -2,
    influenza: 3,
    adenovirus: 4,
    enterovirus: 3,
    hmpv: 3,
    commonCold: 3,
    rsv: 3,
    norovirus: 0,
  },
  conjunctivitis: {
    strep: -3,
    ebv: -3,
    influenza: -2,
    adenovirus: 5,
    enterovirus: -2,
    hmpv: -2,
    commonCold: -2,
    rsv: -1,
    norovirus: -3,
  },
  bodyAches: {
    strep: -1,
    ebv: -1,
    influenza: 3,
    adenovirus: -2,
    enterovirus: -2,
    hmpv: -2,
    commonCold: -2,
    rsv: 0,
    norovirus: 0,
  },
  diarrhea: {
    strep: -3,
    ebv: -2,
    influenza: 2,
    adenovirus: 4,
    enterovirus: 4,
    hmpv: -2,
    commonCold: -2,
    rsv: 0,
    norovirus: 5,
  },
  wheezing: {
    strep: -3,
    ebv: -3,
    influenza: -2,
    adenovirus: -2,
    enterovirus: -2,
    hmpv: 4,
    commonCold: -2,
    rsv: 5,
    norovirus: -3,
  },
  rashAfterAmoxicillin: {
    strep: -3,
    ebv: 5,
    influenza: -2,
    adenovirus: -2,
    enterovirus: -2,
    hmpv: -2,
    commonCold: -2,
    rsv: 0,
    norovirus: 0,
  },
  onsetSpeed: {
    strep: 3,
    ebv: -3,
    influenza: 3,
    adenovirus: -3,
    enterovirus: -3,
    hmpv: -3,
    commonCold: -3,
    rsv: 0,
    norovirus: 0,
  },
};

// --- Main Differential Function ---
// This function takes the symptom data (continuous, discrete, and mental/behavioral)
// along with patient info (age and contact) to compute log‑odds for each condition,
// applies a softmax conversion, and then returns posterior probabilities and a final recommendation.
export function computeDifferentialOutcome(data, patientInfo) {
  // Set baseline priors (from epidemiological data).
  let priors = {
    strep: patientInfo.age < 18 ? 0.25 : 0.10,
    ebv: 0.10,
    influenza: 0.10,
    adenovirus: 0.05,
    enterovirus: 0.05,
    hmpv: 0.05,
    commonCold: 0.30,
    rsv: 0.05,
    norovirus: 0.05,
  };
  // Adjust priors based on contact history.
  if (patientInfo.contact) {
    priors.strep += 0.10;
    priors.influenza += 0.05;
  }
  // Convert priors to log‑odds.
  let logOdds = {};
  conditions.forEach((cond) => {
    const p = priors[cond];
    logOdds[cond] = Math.log(p / (1 - p));
  });

  // Add contributions from discrete/checkbox symptoms.
  // Handle special cases:
  if (!data.cough) {
    Object.keys(symptomPoints.noCough).forEach((cond) => {
      logOdds[cond] += symptomPoints.noCough[cond];
    });
  }
  const fever = parseFloat(data.fever);
  if (!isNaN(fever) && fever >= 38.5) {
    Object.keys(symptomPoints.highFever).forEach((cond) => {
      logOdds[cond] += symptomPoints.highFever[cond];
    });
  }
  if (data.onsetSpeed && data.onsetSpeed.toLowerCase() === "rapid") {
    Object.keys(symptomPoints.onsetSpeed).forEach((cond) => {
      logOdds[cond] += symptomPoints.onsetSpeed[cond];
    });
  }
  // For other discrete symptoms:
  Object.keys(symptomPoints).forEach((symptom) => {
    if (["noCough", "highFever", "onsetSpeed"].includes(symptom)) return;
    if (data[symptom]) {
      Object.keys(symptomPoints[symptom]).forEach((cond) => {
        logOdds[cond] += symptomPoints[symptom][cond];
      });
    }
  });

  // Now add contributions from continuous inputs using our dedicated functions.
  // For gland/pus swelling:
  const glandSwelling = parseFloat(data.glandSwelling) || 50;
  const glandStrep = calculateGlandOrPusStrepLikelihood(glandSwelling);
  const glandViral = calculateGlandOrPusViralLikelihood(glandSwelling);
  // For lymph node tenderness:
  const tenderness = parseFloat(data.tenderness) || 0;
  const tendernessStrep = calculateLymphNodeTendernessStrepLikelihood(tenderness);
  const tendernessViral = calculateLymphNodeTendernessViralLikelihood(tenderness);
  // For tonsil swelling:
  const tonsilSwelling = parseFloat(data.tonsilSwelling) || 50;
  const tonsilStrep = calculateTonsilStrepLikelihood(tonsilSwelling);
  const tonsilViral = calculateTonsilViralLikelihood(tonsilSwelling);

  // We'll add these continuous likelihoods as additional log-odds.
  // (For simplicity, we add their log ratios.)
  const addLogRatio = (strepVal, viralVal) => {
    // Avoid log(0)
    const safeStrep = strepVal > 0 ? strepVal : 0.0001;
    const safeViral = viralVal > 0 ? viralVal : 0.0001;
    return Math.log(safeStrep / safeViral);
  };
  const continuousLogRatio = addLogRatio(glandStrep, glandViral)
    + addLogRatio(tendernessStrep, tendernessViral)
    + addLogRatio(tonsilStrep, tonsilViral);
  // Distribute this log-ratio evenly among conditions.
  conditions.forEach((cond) => {
    // For strep, add; for viral conditions, subtract.
    if (cond === "strep") {
      logOdds[cond] += continuousLogRatio / 3;
    } else {
      logOdds[cond] -= continuousLogRatio / (3 * (conditions.length - 1));
    }
  });

  // Additionally, adjust for extra viral symptoms (vomiting, wheezing)
  if (data.vomiting) {
    conditions.forEach((cond) => {
      if (cond === "norovirus" || cond === "adenovirus" || cond === "enterovirus" || cond === "influenza") {
        logOdds[cond] += 0.5;
      }
    });
  }
  if (data.wheezing) {
    conditions.forEach((cond) => {
      if (cond === "rsv" || cond === "hmpv") {
        logOdds[cond] += 0.5;
      }
    });
  }

  // Convert logOdds to probabilities using softmax.
  const expOdds = {};
  let sumExp = 0;
  conditions.forEach((cond) => {
    expOdds[cond] = Math.exp(logOdds[cond]);
    sumExp += expOdds[cond];
  });
  const probabilities = {};
  conditions.forEach((cond) => {
    probabilities[cond] = expOdds[cond] / sumExp;
  });

  // Determine final recommendation.
  let recommendation = "";
  const sorted = conditions.slice().sort((a, b) => probabilities[b] - probabilities[a]);
  const topCondition = sorted[0];
  if (topCondition === "strep" && probabilities.strep > 0.55) {
    recommendation = "Antibiotics recommended for Strep";
  } else if (topCondition === "strep" && probabilities.strep > 0.45) {
    recommendation = "Test recommended to rule in/out Strep (uncertain, borderline probability)";
  } else if (topCondition !== "strep" && probabilities.strep < 0.40) {
    recommendation = `Viral infection likely (Viral probability: ${((1 - probabilities.strep) * 100).toFixed(0)}%). Consider monitoring and rapid testing if necessary.`;
  } else {
    recommendation = `Test recommended due to overlapping symptoms (Strep: ${(probabilities.strep * 100).toFixed(0)}%, Viral: ${((1 - probabilities.strep) * 100).toFixed(0)}%) – further evaluation is advised.`;
  }

  return {
    probabilities,
    recommendation,
    logOdds,
    glandStrep, glandViral,
    tendernessStrep, tendernessViral,
    tonsilStrep, tonsilViral,
  };
}
