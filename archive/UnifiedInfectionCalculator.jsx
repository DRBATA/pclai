// UnifiedInfectionCalculator.jsx
"use client";

import React, { useState, useEffect } from "react";
import { format } from "date-fns";
import { db } from "../db";
import { computeDifferentialOutcome } from "./differentialCalculations";

// --- Input Arrays for the Wizard UI ---

// Continuous Symptoms: Single sliders for lymph node (anterior), tonsils, pus, and fever.
const continuousSymptoms = [
  { id: "lymphNodes", name: "Lymph Node Swelling (Anterior)", min: 0, max: 100 },
  { id: "tonsils", name: "Tonsil Swelling", min: 0, max: 100 },
  { id: "pus", name: "Pus Coverage on Tonsils", min: 0, max: 100 },
  { id: "fever", name: "Fever (°C)", min: 36, max: 41 },
];

// Discrete Symptoms (checkboxes)
const discreteSymptoms = [
  { id: "blotchyRash", name: "Blotchy Rash" },
  { id: "sandpaperRash", name: "Sandpaper Rash" },
  { id: "sandpaperAfterBlotchy", name: "Sandpaper Rash after Blotchy" },
  { id: "perianalRash", name: "Peri-anal Strep Rash" },
  { id: "soreThroatNoCough", name: "Sore Throat Without Cough" },
  { id: "asymmetricalSwelling", name: "Asymmetrical Swelling" },
  { id: "sneezing", name: "Sneezing" },
  { id: "runnyNose", name: "Runny Nose with Green Discharge" },
  { id: "stickyEyes", name: "Sticky Green Eye Discharge + Conjunctivitis" },
  { id: "normalMood", name: "Normal Mood & Activity" },
  { id: "mildFever", name: "Mild Fever (Below 38°C)" },
  { id: "gradualOnset", name: "Gradual Onset of Symptoms" }
];

// Mental/Behavioral (PANDAS-related) questions
const mentalBehaviorQuestions = [
  { id: "irritability", question: "Increased irritability?" },
  { id: "anxiety", question: "Heightened anxiety?" },
  { id: "depression", question: "Low mood or depression?" },
  { id: "ocd", question: "Increase in obsessive/compulsive behaviors?" },
  { id: "tics", question: "New or worsening tics?" },
  { id: "adhd", question: "Increase in ADHD-like symptoms?" },
  { id: "regression", question: "Regression in age-appropriate behaviors?" },
  { id: "sleep", question: "Significant changes in sleep patterns?" },
  { id: "appetite", question: "Notable change in appetite?" },
  { id: "socialWithdrawal", question: "Social withdrawal observed?" }
];

// Additional Questions (for strep differentiation)
const additionalQuestions = [
  { id: "lymphNodesTender", question: "Lymph nodes tender? (Use slider below)" },
  { id: "tonsileAsymmetry", question: "Tonsil asymmetry present?" },
  { id: "feverResponsive", question: "Fever responsive to medication?" },
  // Also include a dropdown for fever onset.
];

// --- Wizard Step Components ---

function PatientInfoStep({ info, onChange }) {
  return (
    <div>
      <h3>Patient Information</h3>
      <label>
        Age:
        <input
          type="number"
          name="age"
          value={info.age || ""}
          onChange={onChange}
          className="glassmorphic-btn"
          style={{ marginLeft: "0.5rem" }}
        />
      </label>
      <br />
      <label>
        Contact with Infected Person:
        <input
          type="checkbox"
          name="contact"
          checked={info.contact || false}
          onChange={onChange}
          style={{ marginLeft: "0.5rem" }}
        />
      </label>
    </div>
  );
}

function ContinuousSymptomsStep({ data, onChange }) {
  return (
    <div>
      <h3>Continuous Symptoms</h3>
      {continuousSymptoms.map((symptom) => (
        <div key={symptom.id}>
          <label>{symptom.name}</label>
          <input
            type="range"
            name={symptom.id}
            min={symptom.min}
            max={symptom.max}
            value={data[symptom.id] || symptom.min}
            onChange={onChange}
          />
          <span>
            {data[symptom.id] || symptom.min}
            {symptom.id === "fever" ? "°C" : "%"}
          </span>
        </div>
      ))}
    </div>
  );
}

function DiscreteSymptomsStep({ data, onChange }) {
  return (
    <div>
      <h3>Discrete Symptoms</h3>
      {discreteSymptoms.map((symptom) => (
        <div key={symptom.id}>
          <label>
            <input
              type="checkbox"
              name={symptom.id}
              checked={data[symptom.id] || false}
              onChange={onChange}
            />
            {symptom.name}
          </label>
        </div>
      ))}
    </div>
  );
}

function MentalBehaviorStep({ data, onChange }) {
  return (
    <div>
      <h3>Mental & Behavioral (PANDAS) Assessment</h3>
      {mentalBehaviorQuestions.map((q) => (
        <div key={q.id}>
          <label>
            <input
              type="checkbox"
              name={q.id}
              checked={data[q.id] || false}
              onChange={onChange}
            />
            {q.question}
          </label>
        </div>
      ))}
    </div>
  );
}

function AdditionalQuestionsStep({ data, onChange }) {
  return (
    <div>
      <h3>Additional Questions</h3>
      {additionalQuestions.map((q) => (
        <div key={q.id}>
          <label>
            <input
              type="checkbox"
              name={q.id}
              checked={data[q.id] || false}
              onChange={onChange}
            />
            {q.question}
          </label>
        </div>
      ))}
      <div>
        <label>Fever Onset:</label>
        <select name="feverOnset" value={data.feverOnset || ""} onChange={onChange}>
          <option value="">Select...</option>
          <option value="sudden">Sudden</option>
          <option value="gradual">Gradual</option>
        </select>
      </div>
      <div>
        <label>
          Lymph Node Tenderness (0-100):
          <input
            type="range"
            name="tenderness"
            min="0"
            max="100"
            value={data.tenderness || 0}
            onChange={onChange}
            className="glassmorphic-btn"
          />
          <span>{data.tenderness || 0}</span>
        </label>
      </div>
    </div>
  );
}

function AnalyseStep({ result }) {
  return (
    <div>
      <h3>Analysis Outcome</h3>
      <p style={{ fontWeight: "bold", fontSize: "1.2em" }}>{result.recommendation || "Outcome will be displayed here."}</p>
      <div style={{ background: "#f0f0f0", padding: "1em", borderRadius: "8px", marginTop: "1em" }}>
        <h4>Mathematical Details</h4>
        <p>
          <em>Gland/Pus Swelling:</em> Sigmoid component: <code>0.2/(1+e^(-0.1*(swelling-70)))</code>, Gaussian: <code>0.6*e^(-((swelling-85)^2)/(200))</code>
        </p>
        <p>
          <em>Lymph Node Tenderness (Strep):</em> <code>1/(1+e^(-0.2*(tenderness-20)))</code>
        </p>
        <p>
          <em>Tonsil Swelling (Strep):</em> Sigmoid + Gaussian: <code>0.2/(1+e^(-0.1*(swelling-30))) + 0.6*e^(-((swelling-85)^2)/(200))</code>
        </p>
        <p>
          Bayesian Update: Prior (adjusted for age & contact) converted to odds, multiplied by symptom likelihood ratio, then converted back to probability.
        </p>
      </div>
      <p style={{ marginTop: "1em" }}>
        <strong>Posterior Strep Probability:</strong> {(result.probabilities.strep * 100).toFixed(1)}% | <strong>Viral (Combined):</strong> {(((1 - result.probabilities.strep) * 100)).toFixed(1)}%
      </p>
    </div>
  );
}

// --- Main Component: UnifiedInfectionCalculator ---
export default function UnifiedInfectionCalculator() {
  const [patientInfo, setPatientInfo] = useState({ age: "", contact: false });
  const [data, setData] = useState({});
  const [startDate, setStartDate] = useState("");
  const [currentStep, setCurrentStep] = useState(0);
  const [result, setResult] = useState(null);
  const [logs, setLogs] = useState([]);

  // Steps for the wizard:
  const steps = [
    { title: "Patient Info", component: <PatientInfoStep info={patientInfo} onChange={(e) => {
        const { name, value, type, checked } = e.target;
        setPatientInfo((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
      }} /> },
    { title: "Continuous Symptoms", component: <ContinuousSymptomsStep data={data} onChange={(e) => {
        const { name, value, type, checked } = e.target;
        setData((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
      }} /> },
    { title: "Discrete Symptoms", component: <DiscreteSymptomsStep data={data} onChange={(e) => {
        const { name, value, type, checked } = e.target;
        setData((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
      }} /> },
    { title: "Mental/Behavior & Additional", component: <div>
          <MentalBehaviorStep data={data} onChange={(e) => {
            const { name, value, type, checked } = e.target;
            setData((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
          }} />
          <AdditionalQuestionsStep data={data} onChange={(e) => {
            const { name, value, type, checked } = e.target;
            setData((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
          }} />
      </div> },
    { title: "Analyse", component: <AnalyseStep result={result || {}} /> },
  ];

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    const allLogs = await db.logs.orderBy("observationDate").reverse().toArray();
    setLogs(allLogs);
  };

  const nextStep = () => {
    // On moving from the last data-entry step to Analyse, compute the differential.
    if (currentStep === steps.length - 2) {
      const analysis = computeDifferentialOutcome(data, {
        age: parseFloat(patientInfo.age) || 0,
        contact: patientInfo.contact,
      });
      setResult(analysis);
    }
    setCurrentStep(Math.min(currentStep + 1, steps.length - 1));
  };

  const prevStep = () => {
    setCurrentStep(Math.max(currentStep - 1, 0));
  };

  const handleChange = (e) => {
    // Generic change handler for any input in the symptom steps.
    const { name, value, type, checked } = e.target;
    setData((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
  };

  const handleLog = async (e) => {
    e.preventDefault();
    const logEntry = {
      startDate: startDate,
      observationDate: new Date().toISOString(),
      patientInfo,
      symptoms: data,
      analysis: result,
    };
    await db.logs.add(logEntry);
    fetchLogs();
    alert("Entry logged successfully!");
  };

  const handleClearAndRestart = () => {
    if (window.confirm("Are you sure you want to clear the current data? Log your symptoms first if you wish to keep a record.")) {
      setPatientInfo({ age: "", contact: false });
      setData({});
      setResult(null);
      setCurrentStep(0);
      setStartDate("");
    }
  };

  return (
    <div className="home-container">
      <div className="hero-section">
        <h1>Unified Infection Calculator</h1>
        <p className="subtitle">
          Enter your patient info and symptoms for an evidence-based differential diagnosis.
        </p>
      </div>

      {/* Start Date Input */}
      <div style={{ marginBottom: "1rem" }}>
        <label>
          Symptom Start Date:
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="glassmorphic-btn"
            style={{ marginLeft: "0.5rem" }}
          />
        </label>
      </div>

      {/* Wizard Form */}
      <form onSubmit={handleLog} style={{ marginBottom: "1rem" }}>
        <h2>
          Step {currentStep + 1}: {steps[currentStep].title}
        </h2>
        {steps[currentStep].component}
        <div className="navigation-buttons" style={{ marginTop: "1rem" }}>
          {currentStep > 0 && <button type="button" onClick={prevStep} className="glassmorphic-btn">Back</button>}
          {currentStep < steps.length - 1 && (
            <button type="button" onClick={nextStep} className="glassmorphic-btn">
              {currentStep === steps.length - 2 ? "Analyze" : "Next"}
            </button>
          )}
          {currentStep === steps.length - 1 && (
            <button type="submit" className="glassmorphic-btn">Log Entry</button>
          )}
          <button type="button" onClick={handleClearAndRestart} className="glassmorphic-btn" style={{ marginLeft: "1rem" }}>
            Clear & Restart Tool
          </button>
        </div>
      </form>

      {/* Export / Import Buttons */}
      <div style={{ marginBottom: "1rem" }}>
        <button
          onClick={async () => {
            const allData = await db.logs.toArray();
            if (allData.length === 0) {
              alert("No data to export.");
              return;
            }
            const defaultFileName = `UnifiedExport-${new Date().toISOString().slice(0, 10)}.json`;
            const fileName = prompt("Enter file name for export:", defaultFileName);
            if (!fileName) return;
            const jsonString = JSON.stringify(allData, null, 2);
            const blob = new Blob([jsonString], { type: "application/json" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = fileName.endsWith(".json") ? fileName : fileName + ".json";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            await db.logs.clear();
            alert("Data exported and local log cleared.");
          }}
          className="glassmorphic-btn"
          style={{ marginRight: "1rem" }}
        >
          Export Data
        </button>
        <button onClick={() => alert("Import functionality not implemented yet.")} className="glassmorphic-btn">
          Import Data
        </button>
      </div>

      {/* Logged Entries */}
      <div className="feature-card">
        <h2>Logged Entries</h2>
        {logs.length === 0 ? (
          <p>No entries yet.</p>
        ) : (
          <ul>
            {logs.map((log) => (
              <li key={log.id}>
                <strong>{format(new Date(log.observationDate), "PPpp")}</strong> - Outcome: {log.analysis?.recommendation}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
