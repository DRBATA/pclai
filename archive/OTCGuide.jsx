import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";

// Expanded master data for OTC treatments and symptom advice
const masterData = [
  {
    condition: "Strep Pharyngitis (Pharyngitis, not tonsillitis)",
    antibiotic: "Penicillin V (or Amoxicillin if indicated)",
    probiotic: "Probiotic (take 2 hrs apart from antibiotic)",
    lozenges: "Strepsils (Honey & Lemon) – provides local throat relief and a mild antiseptic effect",
    painRelief: "Paracetamol or Ibuprofen",
    coughManagement: "Cough Suppressant (if dry, irritating cough)",
    keyInstructions:
      "Finish the full antibiotic course. Use lozenges only if throat pain is present. In patients aged 45+, when using ibuprofen, add a PPI (e.g. Nexium) and Vitamin D3/K2 to reduce GI bleed risk and support bone health.",
    watchFor:
      "Watch for worsening throat pain, difficulty swallowing, or high fever. If you experience severe shortness of breath, chest pain, or become unresponsive, seek immediate medical attention (A&E)."
  },
  {
    condition: "Chest Infection (Possible bronchitis/pneumonia)",
    antibiotic: "Amoxicillin (mild–moderate) or Co-Amoxiclav (if more severe)",
    probiotic: "Probiotic (take ~2 hrs after antibiotic)",
    painRelief: "Paracetamol or Ibuprofen",
    coughManagement:
      "Cough Medicine – use a suppressant if the cough is dry or an expectorant (e.g. Guaifenesin) if productive",
    keyInstructions:
      "If bacterial, finish the full antibiotic course. Use decongestants sparingly (max ~3×/week) to avoid rebound congestion.",
    watchFor:
      "Watch for severe shortness of breath, chest pain on breathing, or unilateral wheeze with accessory muscle use. If these occur, seek immediate care (A&E). If symptoms persist but are not severe, book a GP appointment."
  },
  {
    condition: "Inner Ear Infection (Otitis Media / Labyrinthitis)",
    antibiotic: "Amoxicillin (or Co-Amoxiclav if severe)",
    probiotic: "Probiotic (if on antibiotic)",
    painRelief: "Ibuprofen (preferred for inflammation) or Paracetamol",
    coughManagement: "Nasal Decongestant* – if Eustachian blockage is contributing",
    keyInstructions:
      "Typical duration is about 2 weeks. Use the nasal spray with proper technique (lean forward, spray upward).",
    watchFor:
      "Watch for any sudden hearing loss or severe ear pain. If these occur, seek immediate medical advice."
  },
  {
    condition: "Eustachian Tube Infection",
    antibiotic: "Amoxicillin / Co-Amoxiclav (only if clearly bacterial – e.g. with prior ENT surgery, significant swelling, or blood)",
    probiotic: "Probiotic (if antibiotics are used)",
    painRelief: "Ibuprofen or Paracetamol",
    coughManagement: "Nasal Decongestant / Spray",
    keyInstructions:
      "Usually no antibiotics are needed unless there is prior surgery or significant bleeding. Use the opposite hand to the nostril and aim toward the affected side. May take 6–8 weeks if underlying allergic inflammation exists.",
    watchFor:
      "Watch for worsening symptoms such as significant bleeding or severe pain. If symptoms persist beyond 6–8 weeks, seek GP review."
  },
  {
    condition: "Sinus Infection (Sinusitis)",
    antibiotic: "Amoxicillin (if severe/prolonged) or Co-Amoxiclav",
    probiotic: "Probiotic (if on antibiotic)",
    painRelief: "Paracetamol or Ibuprofen",
    coughManagement: "Saline Nasal Rinse + Decongestant (e.g. Sudafed/Pseudoephedrine; use max ~3×/week)",
    keyInstructions:
      "Sinusitis can last about 3 weeks and be managed with these sprays. Antibiotics are reserved for patients with a history of ENT/sinus surgery or if blood appears in the nasal discharge.",
    watchFor:
      "Watch for severe facial pain, blood in nasal discharge, or if symptoms worsen after 3 weeks. If you have a history of sinus surgery and experience nasal bleeding, seek immediate care."
  },
  {
    condition: "URTI with Sore Throat",
    probiotic: "Probiotic (only if an antibiotic is eventually introduced)",
    lozenges: "Strepsils (Honey & Lemon) – help reduce throat irritation",
    painRelief: "Paracetamol or Ibuprofen",
    keyInstructions:
      "Lozenges provide local relief and may help prevent bacterial progression. Early use of a barrier spray (First Defence) may also reduce viral load.",
    watchFor:
      "Watch for difficulty swallowing, high fever, or severe throat pain. If these occur, seek medical attention (GP or A&E if severe)."
  },
  {
    condition: "URTI with Congestion",
    painRelief: "Paracetamol or Ibuprofen",
    coughManagement:
      "First Defence Nasal Spray (for early use to prevent progression) plus decongestants (Sudafed/Phenylephrine) if blockage persists",
    keyInstructions:
      "Early intervention with First Defence may reduce symptom progression. Use decongestants if nasal blockage is significant.",
    watchFor:
      "Watch for severe shortness of breath or if congestion worsens significantly. Consult a GP or seek emergency care if breathing difficulties occur."
  },
  {
    condition: "Glandular Fever (Mono)",
    painRelief: "Paracetamol or Ibuprofen",
    keyInstructions:
      "Mono typically shows generalized lymph node swelling (neck, armpits, groin) plus mesenteric adenitis. Avoid antibiotics unless a secondary bacterial infection is confirmed.",
    watchFor:
      "Watch for worsening fatigue, shortness of breath, or severe abdominal pain. Seek medical attention if these occur."
  },
  {
    condition: "Sinusitis while on Antibiotics",
    painRelief: "Paracetamol or Ibuprofen",
    coughManagement: "Saline Nasal Rinse + Sudafed/Pseudoephedrine",
    keyInstructions:
      "If sinus congestion persists on antibiotics, adding a saline rinse and decongestant can improve antibiotic effectiveness.",
    watchFor:
      "Watch for persistent congestion or severe facial pain. If symptoms worsen despite treatment, contact your GP."
  },
  {
    condition: "Hay Fever / Postnasal Drip",
    coughManagement:
      "Once-daily Antihistamine (e.g. Loratadine/Clarityn) + Beclometasone Nasal Spray (e.g. Beconase)",
    keyInstructions:
      "The antihistamine relieves sneezing and itch, while the steroid nasal spray targets nasal inflammation and postnasal drip. Use the proper spray technique (lean forward, aim upward toward the back of the nasal cavity).",
    watchFor:
      "Watch for a significant worsening of symptoms (e.g. severe shortness of breath or signs of infection). Seek a GP or pharmacist review if these occur."
  },
  {
    condition: "Flu (Achy Muscles)",
    painRelief: "Paracetamol (and/or Ibuprofen for muscle/joint pain)",
    coughManagement:
      "If chesty – add an expectorant (Guaifenesin); if nasal congestion – add a decongestant (Phenylephrine); an optional caffeine boost may help ~50% of users",
    keyInstructions:
      "If immunocompromised, if symptoms last >2 weeks, or if the illness is debilitating, consider prescription antivirals.",
    watchFor:
      "Watch for severe shortness of breath, unresponsive wheezing, chest pain radiating to the jaw/arm, or if the illness becomes debilitating. In such cases, seek immediate help (A&E) or book a GP appointment."
  },
  {
    // Headaches card
    condition: "Headaches – Understanding Common Symptoms & When to Seek Medical Attention",
    types: `
      <strong>Types of Headaches:</strong><br/>
      • Tension Headaches: Dull, aching pain; often stress-related.<br/>
      • Migraines: Intense, throbbing pain; may include nausea and sensitivity to light.<br/>
      • Cluster Headaches: Severe pain around one eye; occur in clusters over weeks.<br/>
      • Sinus Headaches: Pressure and pain in the face; related to sinus infections.
    `,
    redFlags: `
      <strong>Red Flags (When to Seek Immediate Help):</strong><br/>
      • Sudden, severe headache ("thunderclap" headache)<br/>
      • Headache with fever, stiff neck, confusion, or seizures<br/>
      • After a head injury<br/>
      • Persistent headaches that worsen over time
    `,
    management: `
      <strong>Management and Treatment:</strong><br/>
      • Self-Care: Rest and OTC pain relief (Ibuprofen or Paracetamol).<br/>
      • Migraines: May require high-dose Aspirin (900mg) or OTC triptans (if no meningitic features).<br/>
      • For Eye Strain: Consider lavender, warm baths, meditation, or checking your glasses.
    `,
    keyInstructions:
      "Ensure you do not have signs of meningitis (fever, stiff neck, confusion, seizures). If these occur, seek immediate medical attention (A&E).",
    watchFor:
      "Watch for sudden, severe changes in headache intensity or associated neurological symptoms. Seek help immediately if these occur."
  },
  {
    // Rashes & Eczema card
    condition: "Rashes & Eczema",
    types: `
      <strong>Common Causes:</strong> Allergic reactions, infections, chronic skin conditions (eczema, psoriasis), heat or sun exposure.
    `,
    redFlags: `
      <strong>Red Flags:</strong> Rash with fever or general illness, rapidly spreading rash, signs of infection (warmth, swelling, pus), rash after new medication, rash with breathing difficulties.
    `,
    management: `
      <strong>Management and Treatment:</strong><br/>
      • Use soothing lotions and emollient washes.<br/>
      • For eczema: Moisturize up to 4 times a day using moisturizing hand washes.<br/>
      • Avoid known irritants and keep the area clean.<br/>
      • Consult a pharmacist for topical treatments and antihistamines.
    `,
    keyInstructions:
      "See your GP if the rash persists or worsens.",
    watchFor:
      "Watch for signs of infection (a blistering rash on one side spreadin ould be shingles) or anaphylaxis. Seek immediate help if these occur."
  },
  {
    // Assessing Minor Injury & Strain card
    condition: "Assessing Minor Injury & Strain",
    keyInstructions:
      "For repetitive strain, consider using Tubigrip and use Paracetamol or Ibuprofen for pain relief.",
    watchFor:
      "Symptom Checklist: Severe pain (8–10/10), inability to move or bear weight, visible deformity, significant swelling or bruising, numbness or tingling. If any are present, seek immediate medical attention (A&E or MIU). Otherwise, monitor symptoms and consider consulting a physiotherapist or GP if no improvement."
  },
  {
    // Abdominal Discomfort card
    condition: "Abdominal Discomfort (Diarrhoea and Vomiting)",
    keyInstructions:
      "For diarrhoea and vomiting, use oral rehydration salts (e.g. Dioral) and Imodium to slow the motion. Buscopan may relieve cramping pain, and Paracetamol can be used for pain. If there is severe blood in the diarrhoea, seek immediate care (A&E) for rehydration. If symptoms persist over 2 weeks with weight loss, further investigation is needed.",
    watchFor:
      "Watch for severe dehydration, blood in the stool, or prolonged symptoms with weight loss. Seek immediate help if severe, or book a GP appointment for further evaluation."
  }
];

export default function OTCPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [filteredData, setFilteredData] = useState(masterData);

  // Update filtered data whenever the search term changes
  useEffect(() => {
    if (searchTerm.trim() !== "") {
      const lowerTerm = searchTerm.toLowerCase();
      const filtered = masterData.filter((item) =>
        // Search across all string properties in the item
        Object.values(item).some(
          (val) =>
            typeof val === "string" && val.toLowerCase().includes(lowerTerm)
        )
      );
      setFilteredData(filtered);
    } else {
      setFilteredData(masterData);
    }
  }, [searchTerm]);

  return (
    <div className="otc-page">
      {/* Explanation Section */}
      <div className="otc-explanation">
        <p>
          <strong>Note:</strong> This tool is not a symptom checker or diagnostic device.
          Once you have received a diagnosis, you can use this tool to help understand the best over‐the‐counter treatment options. You need to read the leaflets with the medication to check for interactions with other medication you are on or if there are reasons you cant take it like being on aspirin with ibuprofen or long term paracetamol use when on statins. You can use our QuickAsk* function for peronsalised advice such as when taking iburpfoen (takes 3 days of regular use with food to create a true anitinflammatory affect great for strains or inflamed throat) it might be a good idea to take a tummy protector tablet; but those can stop vitamin D or calcium absorbtion so you can supplement those with tablet or spray - vitmain K with that helps the calcium stay in the bones rather than sitffen up you blood vessels contributing to blood pressure /heart disease risk. Or Order a WellBox** with every thing in one easy delivered package. *Quick ask and Wellbox coming soon **Wellbox includes free usw of the QuickAsk tool
        </p>
        <br></br>
        <b>How to use this tool:</b>
        <p>
          After you search, you’ll see a selection of cards with detailed treatment options and important warnings.
          When you find the card that best fits your condition, please review the “Watch For” section for escalation advice.
          If necessary, use the <Link to="/book-now">Book Now</Link> page to schedule an appointment with your GP.
        </p>
      </div>

      {/* Search Bar */}
      <div className="otc-search">
        <input
          type="search"
          placeholder="Search OTC treatments..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          aria-label="Search OTC treatments"
          className="otc-search-input"
        />
      </div>

      {/* Cards Container */}
      <div className="otc-cards">
        {filteredData.length === 0 ? (
          <p>No results found.</p>
        ) : (
          filteredData.map((item, index) => (
            <div key={index} className="otc-card">
              <h2>{item.condition}</h2>
              <ul>
                {item.antibiotic && (
                  <li>
                    <strong>Antibiotic:</strong>{" "}
                    <span dangerouslySetInnerHTML={{ __html: item.antibiotic }} />
                  </li>
                )}
                {item.probiotic && (
                  <li>
                    <strong>Probiotic:</strong>{" "}
                    <span dangerouslySetInnerHTML={{ __html: item.probiotic }} />
                  </li>
                )}
                {item.lozenges && (
                  <li>
                    <strong>Lozenges:</strong>{" "}
                    <span dangerouslySetInnerHTML={{ __html: item.lozenges }} />
                  </li>
                )}
                {item.painRelief && (
                  <li>
                    <strong>Pain Relief:</strong>{" "}
                    <span dangerouslySetInnerHTML={{ __html: item.painRelief }} />
                  </li>
                )}
                {item.coughManagement && (
                  <li>
                    <strong>Cough/Other:</strong>{" "}
                    <span dangerouslySetInnerHTML={{ __html: item.coughManagement }} />
                  </li>
                )}
                {item.types && (
                  <li>
                    <strong>Types:</strong>{" "}
                    <span dangerouslySetInnerHTML={{ __html: item.types }} />
                  </li>
                )}
                {item.redFlags && (
                  <li>
                    <strong>Red Flags:</strong>{" "}
                    <span dangerouslySetInnerHTML={{ __html: item.redFlags }} />
                  </li>
                )}
                {item.management && (
                  <li>
                    <strong>Management:</strong>{" "}
                    <span dangerouslySetInnerHTML={{ __html: item.management }} />
                  </li>
                )}
                {item.keyInstructions && (
                  <li>
                    <strong>Key Instructions:</strong>{" "}
                    <span dangerouslySetInnerHTML={{ __html: item.keyInstructions }} />
                  </li>
                )}
                {item.watchFor && (
                  <li>
                    <strong>Watch For:</strong>{" "}
                    <span dangerouslySetInnerHTML={{ __html: item.watchFor }} />
                  </li>
                )}
              </ul>
              <div className="card-actions">
                <Link to="/book-now" className="book-now-btn">
                  Book Now
                </Link>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
