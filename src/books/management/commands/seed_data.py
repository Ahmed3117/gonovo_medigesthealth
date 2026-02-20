"""
Management command to seed the database with realistic MKSAP-style dummy data.
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from accounts.models import User
from books.models import Book, Specialty, Topic, UserBookAccess
from questions.models import Question, QuizSession, UserQuestionAttempt
from flashcards.models import Flashcard
from certificates.models import CMEActivity
from webhooks.models import WebhookLog
from datetime import timedelta
from django.utils import timezone
import random


# ── Book & Specialty Data (from MKSAP + MEDIGEST store) ──
BOOKS_DATA = [
    {
        "title": "Cardiovascular Medicine",
        "product_id": "MEDIGEST-CV-001",
        "price": 55.00,
        "status": "active",
        "description": "<p>Comprehensive review of <strong>cardiovascular medicine</strong> covering screening, diagnosis, and management of heart diseases, dyslipidemia, arrhythmias, heart failure, and vascular disorders.</p>",
        "specialties": [
            {"name": "Dyslipidemia", "topics": [
                {"title": "Evaluation of Lipid Levels", "content": """<h2>Evaluation of Lipid Levels</h2>
<p>A standard lipid panel measures <strong>total cholesterol, LDL cholesterol, HDL cholesterol, and triglycerides</strong>. Screening for dyslipidemia with a lipid panel should begin at age 20 years in individuals with cardiovascular risk factors.</p>
<h3>Screening Recommendations</h3>
<p>The ACC/AHA guidelines recommend screening with a fasting lipid panel. Risk factors that warrant early screening include:</p>
<ul><li>Diabetes mellitus</li><li>Hypertension</li><li>Smoking</li><li>Family history of premature CVD</li><li>Obesity (BMI &ge; 30)</li></ul>
<h3>Interpreting Results</h3>
<p>LDL cholesterol levels are the primary target for therapy. Optimal LDL cholesterol is &lt;100 mg/dL, with a target of &lt;70 mg/dL for very high-risk patients.</p>""",
                 "key_points": ["Screening for dyslipidemia with a lipid panel should begin at age 20 in individuals with CV risk factors and at age 40 in those without.", "LDL cholesterol is the primary target for lipid-lowering therapy.", "A fasting lipid panel is preferred for accurate triglyceride measurement."]},
                {"title": "Management of Dyslipidemias", "content": """<h2>Management of Dyslipidemias</h2>
<p>Statin therapy is the cornerstone of treatment for elevated LDL cholesterol. The intensity of statin therapy should be matched to the patient's ASCVD risk.</p>
<h3>Statin Therapy Intensities</h3>
<table><thead><tr><th>Intensity</th><th>Expected LDL Reduction</th><th>Examples</th></tr></thead>
<tbody><tr><td>High</td><td>&ge;50%</td><td>Atorvastatin 40-80 mg, Rosuvastatin 20-40 mg</td></tr>
<tr><td>Moderate</td><td>30-49%</td><td>Atorvastatin 10-20 mg, Rosuvastatin 5-10 mg</td></tr></tbody></table>
<h3>Non-Statin Therapies</h3>
<p>For patients who cannot tolerate statins or need additional LDL lowering, <strong>ezetimibe</strong> and <strong>PCSK9 inhibitors</strong> are recommended.</p>""",
                 "key_points": ["High-intensity statin therapy reduces LDL by ≥50%.", "PCSK9 inhibitors are reserved for patients at very high risk who cannot achieve target LDL with statins.", "Lifestyle modifications including diet and exercise are first-line therapy for all patients."]},
                {"title": "Hypertriglyceridemia", "content": """<h2>Hypertriglyceridemia</h2>
<p>Triglyceride levels &ge;500 mg/dL increase the risk of <strong>acute pancreatitis</strong> and require urgent management. The primary goal is to reduce triglycerides to prevent pancreatitis.</p>
<h3>Treatment Approach</h3>
<ul><li><strong>Lifestyle changes:</strong> Weight loss, dietary modification, alcohol cessation</li><li><strong>Fibrates:</strong> First-line pharmacotherapy for severe hypertriglyceridemia</li><li><strong>Omega-3 fatty acids:</strong> Icosapent ethyl (Vascepa) for ASCVD risk reduction</li></ul>""",
                 "key_points": ["Triglyceride levels ≥500 mg/dL require treatment to prevent acute pancreatitis.", "Fibrates are first-line pharmacotherapy for severe hypertriglyceridemia.", "Icosapent ethyl reduces ASCVD events in patients with elevated triglycerides on statin therapy."]}
            ]},
            {"name": "Heart Failure", "topics": [
                {"title": "Heart Failure Classification and Diagnosis", "content": """<h2>Heart Failure Classification</h2>
<p>Heart failure is classified by <strong>left ventricular ejection fraction (LVEF)</strong>:</p>
<ul><li><strong>HFrEF:</strong> LVEF &le;40% (Heart Failure with Reduced Ejection Fraction)</li>
<li><strong>HFmrEF:</strong> LVEF 41-49% (Heart Failure with Mildly Reduced EF)</li>
<li><strong>HFpEF:</strong> LVEF &ge;50% (Heart Failure with Preserved EF)</li></ul>
<h3>Diagnostic Evaluation</h3>
<p>Initial evaluation includes BNP/NT-proBNP levels, echocardiography, ECG, and chest radiography. BNP &gt;100 pg/mL or NT-proBNP &gt;300 pg/mL suggests heart failure.</p>""",
                 "key_points": ["HFrEF is defined as LVEF ≤40%.", "BNP >100 pg/mL or NT-proBNP >300 pg/mL suggests heart failure.", "Echocardiography is the primary imaging modality for heart failure evaluation."]},
                {"title": "Medical Therapy for Heart Failure", "content": """<h2>Guideline-Directed Medical Therapy (GDMT)</h2>
<p>The four pillars of HFrEF treatment are:</p>
<ol><li><strong>ACE inhibitor/ARB/ARNI</strong> — Sacubitril-valsartan (ARNI) is preferred over ACEi/ARB</li>
<li><strong>Beta-blocker</strong> — Carvedilol, metoprolol succinate, or bisoprolol</li>
<li><strong>Mineralocorticoid receptor antagonist (MRA)</strong> — Spironolactone or eplerenone</li>
<li><strong>SGLT2 inhibitor</strong> — Dapagliflozin or empagliflozin</li></ol>
<p>All four medication classes should be initiated and titrated to target doses as tolerated.</p>""",
                 "key_points": ["The four pillars of HFrEF treatment are ARNI, beta-blocker, MRA, and SGLT2 inhibitor.", "Sacubitril-valsartan is preferred over ACEi/ARB for HFrEF.", "SGLT2 inhibitors reduce heart failure hospitalizations regardless of diabetes status."]}
            ]},
            {"name": "Arrhythmias", "topics": [
                {"title": "Atrial Fibrillation", "content": """<h2>Atrial Fibrillation</h2>
<p>Atrial fibrillation (AF) is the most common sustained cardiac arrhythmia, affecting approximately 2-3% of the population. Management focuses on rate control, rhythm control, and stroke prevention.</p>
<h3>Stroke Risk Assessment</h3>
<p>The <strong>CHA₂DS₂-VASc score</strong> guides anticoagulation decisions. Anticoagulation is recommended for scores &ge;2 in men and &ge;3 in women.</p>""",
                 "key_points": ["CHA₂DS₂-VASc score guides anticoagulation in atrial fibrillation.", "DOACs are preferred over warfarin for stroke prevention in non-valvular AF.", "Rate control target is resting heart rate <110 bpm in the lenient strategy."]}
            ]},
        ]
    },
    {
        "title": "Pulmonary and Critical Care Medicine",
        "product_id": "MEDIGEST-PULM-001",
        "price": 60.00,
        "status": "active",
        "description": "<p>In-depth coverage of <strong>pulmonary diseases</strong> and <strong>critical care</strong>, including airways disease, pulmonary vascular disease, pleural disease, diffuse lung diseases, and ICU management.</p>",
        "specialties": [
            {"name": "Airways Disease", "topics": [
                {"title": "Asthma", "content": """<h2>Asthma</h2>
<p>Asthma is a chronic inflammatory disease of the airways characterized by variable airflow obstruction, bronchial hyperresponsiveness, and airway inflammation.</p>
<h3>Stepwise Therapy</h3>
<p>Treatment follows a stepwise approach based on symptom severity:</p>
<ul><li><strong>Step 1:</strong> Low-dose ICS-formoterol as needed (preferred) or SABA as needed</li>
<li><strong>Step 2:</strong> Low-dose ICS daily + SABA as needed</li>
<li><strong>Step 3:</strong> Low-dose ICS-LABA</li>
<li><strong>Step 4:</strong> Medium-dose ICS-LABA</li>
<li><strong>Step 5:</strong> High-dose ICS-LABA + add-on therapy (anti-IgE, anti-IL5)</li></ul>""",
                 "key_points": ["ICS-formoterol as needed is preferred for mild intermittent asthma.", "Stepping up therapy is based on symptom frequency and exacerbation risk.", "Biologic therapies target specific inflammatory pathways in severe asthma."]},
                {"title": "COPD", "content": """<h2>Chronic Obstructive Pulmonary Disease (COPD)</h2>
<p>COPD is defined by persistent airflow limitation confirmed by post-bronchodilator <strong>FEV₁/FVC &lt;0.70</strong>. Smoking cessation is the most important intervention to slow disease progression.</p>
<h3>GOLD Classification</h3>
<ul><li><strong>Group A:</strong> Low risk, fewer symptoms — bronchodilator as needed</li>
<li><strong>Group B:</strong> Low risk, more symptoms — LABA or LAMA</li>
<li><strong>Group E:</strong> High risk (exacerbations) — LABA + LAMA ± ICS</li></ul>""",
                 "key_points": ["COPD diagnosis requires post-bronchodilator FEV₁/FVC <0.70.", "Smoking cessation is the only intervention proven to slow FEV₁ decline.", "Triple therapy (ICS-LABA-LAMA) is reserved for patients with frequent exacerbations and eosinophilia."]}
            ]},
            {"name": "Critical Care Medicine", "topics": [
                {"title": "Sepsis and Septic Shock", "content": """<h2>Sepsis and Septic Shock</h2>
<p>Sepsis is defined as life-threatening organ dysfunction caused by a dysregulated host response to infection. The <strong>qSOFA score</strong> (≥2 criteria: altered mental status, SBP ≤100 mmHg, RR ≥22) identifies patients at risk.</p>
<h3>Management Bundle (Hour-1 Bundle)</h3>
<ol><li>Measure lactate level</li><li>Obtain blood cultures before antibiotics</li><li>Administer broad-spectrum antibiotics</li><li>Begin rapid IV crystalloid (30 mL/kg) for hypotension or lactate &ge;4</li><li>Apply vasopressors for MAP &lt;65 despite fluid resuscitation</li></ol>""",
                 "key_points": ["Sepsis is defined by suspected infection + organ dysfunction (SOFA score ≥2).", "Norepinephrine is the first-line vasopressor for septic shock.", "The Hour-1 Bundle should be initiated immediately upon sepsis recognition."]},
                {"title": "Mechanical Ventilation", "content": """<h2>Mechanical Ventilation</h2>
<p>Lung-protective ventilation is the standard of care for patients with ARDS. Key parameters include:</p>
<ul><li><strong>Tidal volume:</strong> 6 mL/kg predicted body weight</li>
<li><strong>Plateau pressure:</strong> &le;30 cm H₂O</li>
<li><strong>PEEP:</strong> Titrated to maintain adequate oxygenation</li></ul>
<h3>ARDS Berlin Definition</h3>
<table><thead><tr><th>Severity</th><th>PaO₂/FiO₂</th></tr></thead>
<tbody><tr><td>Mild</td><td>200-300</td></tr><tr><td>Moderate</td><td>100-200</td></tr><tr><td>Severe</td><td>&lt;100</td></tr></tbody></table>""",
                 "key_points": ["Lung-protective ventilation uses tidal volume of 6 mL/kg PBW.", "Plateau pressure should be maintained ≤30 cm H₂O.", "Prone positioning improves survival in moderate-severe ARDS (P/F <150)."]}
            ]},
            {"name": "Pleural Disease", "topics": [
                {"title": "Pleural Effusion", "content": """<h2>Pleural Effusion</h2>
<p>Pleural effusions are classified as <strong>transudative or exudative</strong> using Light's criteria:</p>
<ul><li>Pleural fluid protein / serum protein &gt;0.5</li><li>Pleural fluid LDH / serum LDH &gt;0.6</li><li>Pleural fluid LDH &gt;2/3 upper limit of normal serum LDH</li></ul>
<p>Meeting any ONE criterion classifies the effusion as exudative.</p>""",
                 "key_points": ["Light's criteria distinguish transudative from exudative effusions.", "Heart failure is the most common cause of transudative effusion.", "Complicated parapneumonic effusions and empyema require drainage."]}
            ]}
        ]
    },
    {
        "title": "Nephrology",
        "product_id": "MEDIGEST-NEPH-001",
        "price": 50.00,
        "status": "active",
        "description": "<p>Complete review of <strong>nephrology</strong> covering fluid and electrolyte disorders, acid-base balance, acute kidney injury, chronic kidney disease, and glomerular diseases.</p>",
        "specialties": [
            {"name": "Acute Kidney Injury", "topics": [
                {"title": "AKI Classification and Diagnosis", "content": """<h2>Acute Kidney Injury</h2>
<p>AKI is defined by the <strong>KDIGO criteria</strong>: increase in serum creatinine by &ge;0.3 mg/dL within 48 hours, or increase to &ge;1.5x baseline within 7 days, or urine output &lt;0.5 mL/kg/h for 6 hours.</p>
<h3>Classification</h3>
<ul><li><strong>Pre-renal:</strong> Volume depletion, heart failure, hepatorenal syndrome</li>
<li><strong>Intrinsic:</strong> ATN, AIN, glomerulonephritis</li>
<li><strong>Post-renal:</strong> Obstruction (BPH, stones, tumors)</li></ul>""",
                 "key_points": ["AKI is diagnosed by KDIGO criteria: ≥0.3 mg/dL creatinine rise in 48h or ≥1.5x baseline in 7 days.", "FENa <1% suggests pre-renal AKI; FENa >2% suggests intrinsic AKI.", "Urinalysis with muddy brown granular casts indicates ATN."]}
            ]},
            {"name": "Chronic Kidney Disease", "topics": [
                {"title": "CKD Staging and Management", "content": """<h2>Chronic Kidney Disease</h2>
<p>CKD is staged by GFR and albuminuria. Management focuses on slowing progression and managing complications.</p>
<h3>Key Interventions</h3>
<ul><li><strong>ACEi/ARB:</strong> For proteinuria reduction</li>
<li><strong>SGLT2 inhibitors:</strong> Proven to slow CKD progression (DAPA-CKD, EMPA-KIDNEY trials)</li>
<li><strong>Blood pressure:</strong> Target &lt;130/80 mmHg</li>
<li><strong>Finerenone:</strong> Non-steroidal MRA for diabetic kidney disease</li></ul>""",
                 "key_points": ["SGLT2 inhibitors slow CKD progression regardless of diabetes status.", "ACEi/ARB are first-line for proteinuric CKD.", "Refer to nephrology when GFR <30 or rapidly declining."]}
            ]}
        ]
    },
    {
        "title": "Infectious Diseases",
        "product_id": "MEDIGEST-ID-001",
        "price": 50.00,
        "status": "active",
        "description": "<p>Comprehensive coverage of <strong>infectious diseases</strong> including antimicrobial stewardship, HIV, hepatitis, respiratory infections, and healthcare-associated infections.</p>",
        "specialties": [
            {"name": "Community-Acquired Pneumonia", "topics": [
                {"title": "CAP Diagnosis and Management", "content": """<h2>Community-Acquired Pneumonia</h2>
<p>CAP is diagnosed based on clinical features (cough, fever, dyspnea) and confirmed by chest imaging. The <strong>CURB-65 score</strong> guides site-of-care decisions.</p>
<h3>Empiric Antibiotic Therapy</h3>
<ul><li><strong>Outpatient (no comorbidities):</strong> Amoxicillin or doxycycline</li>
<li><strong>Outpatient (with comorbidities):</strong> Amoxicillin-clavulanate + macrolide, or respiratory fluoroquinolone</li>
<li><strong>Inpatient:</strong> Beta-lactam + macrolide, or respiratory fluoroquinolone</li></ul>""",
                 "key_points": ["CURB-65 score guides disposition: 0-1 outpatient, 2 consider admission, ≥3 ICU.", "Procalcitonin can help distinguish bacterial from viral pneumonia.", "Obtain sputum and blood cultures for all hospitalized patients with CAP."]}
            ]}
        ]
    },
    {
        "title": "Hematology and Oncology",
        "product_id": "MEDIGEST-HEMONC-001",
        "price": 60.00,
        "status": "active",
        "description": "<p>Review of <strong>hematology and oncology</strong> covering anemias, coagulation disorders, hematologic malignancies, and solid tumors.</p>",
        "specialties": [
            {"name": "Anemia", "topics": [
                {"title": "Approach to Anemia", "content": """<h2>Approach to Anemia</h2>
<p>Anemia is classified by <strong>mean corpuscular volume (MCV)</strong>:</p>
<ul><li><strong>Microcytic (MCV &lt;80):</strong> Iron deficiency, thalassemia, chronic disease</li>
<li><strong>Normocytic (MCV 80-100):</strong> Chronic disease, CKD, mixed deficiency</li>
<li><strong>Macrocytic (MCV &gt;100):</strong> B12/folate deficiency, MDS, liver disease</li></ul>
<h3>Iron Deficiency Anemia</h3>
<p>Most common cause of anemia worldwide. Diagnosis: low ferritin (&lt;30 ng/mL), low iron, high TIBC, low transferrin saturation (&lt;20%).</p>""",
                 "key_points": ["Ferritin <30 ng/mL is diagnostic of iron deficiency.", "Reticulocyte count distinguishes production problems from destruction/blood loss.", "Iron deficiency in men and postmenopausal women warrants GI evaluation."]}
            ]}
        ]
    },
    {
        "title": "Gastroenterology and Hepatology",
        "product_id": "MEDIGEST-GI-001",
        "price": 55.00,
        "status": "coming_soon",
        "description": "<p>Coming soon — comprehensive coverage of GI and liver diseases.</p>",
        "specialties": []
    },
    {
        "title": "Endocrinology",
        "product_id": "MEDIGEST-ENDO-001",
        "price": 55.00,
        "status": "coming_soon",
        "description": "<p>Coming soon — coverage of diabetes, thyroid, adrenal, and metabolic disorders.</p>",
        "specialties": []
    },
]

# ── Question Data ──
QUESTIONS_DATA = [
    {
        "specialty_ref": "Dyslipidemia",
        "question_text": "<p>A 55-year-old man with type 2 diabetes mellitus and hypertension presents for routine follow-up. His LDL cholesterol is 145 mg/dL despite lifestyle modifications. His 10-year ASCVD risk score is 18%. He has no history of ASCVD events.</p><p>Which of the following is the most appropriate next step in management?</p>",
        "options": ["Ezetimibe", "High-intensity statin therapy", "Moderate-intensity statin therapy", "PCSK9 inhibitor", ""],
        "correct": "B", "difficulty": "medium",
        "explanation": "<p><strong>High-intensity statin therapy</strong> is recommended for patients aged 40-75 with diabetes and a 10-year ASCVD risk ≥7.5%. This patient's risk of 18% places him in the high-risk category. High-intensity statins (atorvastatin 40-80 mg or rosuvastatin 20-40 mg) reduce LDL by ≥50%.</p><p>Moderate-intensity statin would be insufficient given his elevated risk. PCSK9 inhibitors are reserved for patients who fail to reach goals despite maximally tolerated statin + ezetimibe. Ezetimibe alone would not provide adequate LDL reduction.</p>",
        "educational_objective": "Prescribe high-intensity statin therapy for patients with diabetes and elevated ASCVD risk.",
    },
    {
        "specialty_ref": "Heart Failure",
        "question_text": "<p>A 62-year-old woman with NYHA class III heart failure and LVEF of 28% is currently taking lisinopril, carvedilol, and spironolactone. She has no contraindications to additional therapy. Her blood pressure is 118/72 mmHg.</p><p>Which of the following medications should be added to optimize her heart failure regimen?</p>",
        "options": ["Amlodipine", "Dapagliflozin", "Digoxin", "Hydralazine-isosorbide dinitrate", "Ivabradine"],
        "correct": "B", "difficulty": "medium",
        "explanation": "<p><strong>Dapagliflozin</strong>, an SGLT2 inhibitor, is one of the four pillars of guideline-directed medical therapy for HFrEF. The DAPA-HF trial demonstrated that dapagliflozin reduced cardiovascular death and heart failure hospitalization by 26%. This patient is on three of the four pillars and should have an SGLT2 inhibitor added.</p><p>Additionally, switching her ACEi (lisinopril) to sacubitril-valsartan (ARNI) would further optimize therapy per guidelines.</p>",
        "educational_objective": "Add SGLT2 inhibitor as the fourth pillar of guideline-directed medical therapy for HFrEF.",
    },
    {
        "specialty_ref": "Airways Disease",
        "question_text": "<p>A 45-year-old man with a 30-pack-year smoking history presents with progressive dyspnea and chronic productive cough for 2 years. Spirometry shows FEV₁/FVC of 0.62 and FEV₁ of 55% predicted, with minimal bronchodilator response. He has had two exacerbations requiring oral corticosteroids in the past year.</p><p>Which of the following is the most appropriate initial maintenance therapy?</p>",
        "options": ["Inhaled corticosteroid alone", "LABA alone", "LABA + LAMA", "LAMA alone", "Short-acting bronchodilator as needed"],
        "correct": "C", "difficulty": "medium",
        "explanation": "<p>Per the updated GOLD guidelines, this patient falls into <strong>Group E</strong> (high exacerbation risk: ≥2 moderate or ≥1 severe exacerbation). The recommended initial therapy for Group E is <strong>LABA + LAMA</strong> combination therapy. ICS may be added if the patient has eosinophilia (blood eosinophils ≥300 cells/µL).</p>",
        "educational_objective": "Initiate LABA + LAMA for COPD patients with frequent exacerbations (GOLD Group E).",
    },
    {
        "specialty_ref": "Critical Care Medicine",
        "question_text": "<p>A 68-year-old woman with community-acquired pneumonia develops septic shock. She has received 30 mL/kg of IV crystalloid but remains hypotensive with MAP of 58 mmHg. Her lactate is 4.8 mmol/L. Broad-spectrum antibiotics have been administered.</p><p>Which of the following is the most appropriate next step?</p>",
        "options": ["Additional 30 mL/kg IV crystalloid", "Dobutamine infusion", "Epinephrine infusion", "Norepinephrine infusion", "Vasopressin infusion"],
        "correct": "D", "difficulty": "easy",
        "explanation": "<p><strong>Norepinephrine</strong> is the first-line vasopressor for septic shock when adequate fluid resuscitation fails to restore MAP ≥65 mmHg. Vasopressin can be added as a second agent if needed. Dobutamine is reserved for sepsis-associated cardiac dysfunction. Epinephrine is a second-line agent.</p>",
        "educational_objective": "Select norepinephrine as first-line vasopressor for septic shock.",
    },
    {
        "specialty_ref": "Acute Kidney Injury",
        "question_text": "<p>A 72-year-old man presents with oliguria and serum creatinine of 3.2 mg/dL (baseline 1.1 mg/dL). He was recently started on ibuprofen for knee pain. His FENa is 0.4%, and urinalysis shows no casts. Renal ultrasound shows no hydronephrosis.</p><p>What is the most likely diagnosis?</p>",
        "options": ["Acute interstitial nephritis", "Acute tubular necrosis", "Post-renal obstruction", "Pre-renal azotemia", ""],
        "correct": "D", "difficulty": "easy",
        "explanation": "<p>The low <strong>FENa (&lt;1%)</strong> and bland urinalysis with no casts are classic for <strong>pre-renal azotemia</strong>. NSAIDs like ibuprofen cause pre-renal AKI through afferent arteriolar vasoconstriction, reducing renal blood flow. ATN would show FENa &gt;2% and muddy brown casts. AIN would show white blood cell casts and eosinophils.</p>",
        "educational_objective": "Diagnose NSAID-induced pre-renal azotemia based on low FENa and bland urinalysis.",
    },
]

# ── Flashcard Data ──
FLASHCARDS_DATA = [
    {"specialty_ref": "Dyslipidemia", "front": "What LDL reduction is expected with high-intensity statin therapy?", "back": "≥50% reduction in LDL cholesterol (e.g., atorvastatin 40-80 mg, rosuvastatin 20-40 mg)"},
    {"specialty_ref": "Dyslipidemia", "front": "When should PCSK9 inhibitors be considered?", "back": "In patients at very high ASCVD risk who cannot achieve target LDL despite maximally tolerated statin + ezetimibe"},
    {"specialty_ref": "Heart Failure", "front": "What are the four pillars of HFrEF treatment?", "back": "1. ARNI (sacubitril-valsartan)\n2. Beta-blocker\n3. MRA (spironolactone)\n4. SGLT2 inhibitor"},
    {"specialty_ref": "Heart Failure", "front": "LVEF cutoff for HFrEF", "back": "LVEF ≤40%"},
    {"specialty_ref": "Arrhythmias", "front": "CHA₂DS₂-VASc components", "back": "Congestive HF, Hypertension, Age ≥75 (2pts), Diabetes, Stroke/TIA (2pts), Vascular disease, Age 65-74, Sex category (female)"},
    {"specialty_ref": "Airways Disease", "front": "Spirometry diagnostic criterion for COPD", "back": "Post-bronchodilator FEV₁/FVC < 0.70"},
    {"specialty_ref": "Airways Disease", "front": "Most important intervention to slow COPD progression", "back": "Smoking cessation"},
    {"specialty_ref": "Critical Care Medicine", "front": "First-line vasopressor for septic shock", "back": "Norepinephrine"},
    {"specialty_ref": "Critical Care Medicine", "front": "ARDS lung-protective ventilation tidal volume", "back": "6 mL/kg predicted body weight"},
    {"specialty_ref": "Acute Kidney Injury", "front": "FENa in pre-renal vs. intrinsic AKI", "back": "Pre-renal: FENa < 1%\nIntrinsic (ATN): FENa > 2%"},
    {"specialty_ref": "Chronic Kidney Disease", "front": "SGLT2 inhibitor benefit in CKD", "back": "Slows CKD progression regardless of diabetes status (DAPA-CKD, EMPA-KIDNEY trials)"},
    {"specialty_ref": "Community-Acquired Pneumonia", "front": "CURB-65 score components", "back": "Confusion, Urea >7mmol/L, Respiratory rate ≥30, Blood pressure (SBP<90 or DBP≤60), Age ≥65"},
    {"specialty_ref": "Anemia", "front": "Ferritin level diagnostic of iron deficiency", "back": "Ferritin < 30 ng/mL"},
    {"specialty_ref": "Pleural Disease", "front": "Light's criteria for exudative effusion", "back": "ANY one of:\n• Pleural protein/serum protein > 0.5\n• Pleural LDH/serum LDH > 0.6\n• Pleural LDH > 2/3 ULN serum LDH"},
]


class Command(BaseCommand):
    help = 'Seed the database with realistic MKSAP-style medical content'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n🌱 Seeding MEDIGEST database...\n'))

        # 1. Create demo users
        self._create_users()
        # 2. Create books, specialties, topics
        self._create_books()
        # 3. Create questions
        self._create_questions()
        # 4. Create flashcards
        self._create_flashcards()
        # 5. Create user book access
        self._create_access()
        # 6. Create CME activities
        self._create_cme()
        # 7. Create webhook logs
        self._create_webhook_logs()

        self.stdout.write(self.style.SUCCESS('\n✅ Seed data created successfully!\n'))

    def _create_users(self):
        users = [
            ("dr.sarah@example.com", "Sarah", "Johnson", "student"),
            ("dr.ahmed@example.com", "Ahmed", "Hassan", "student"),
            ("dr.maria@example.com", "Maria", "Garcia", "student"),
        ]
        for email, first, last, role in users:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"first_name": first, "last_name": last, "role": role}
            )
            if created:
                user.set_password("demo123")
                user.save()
                self.stdout.write(f"  👤 Created user: {email}")
            else:
                self.stdout.write(f"  ⏭️  User exists: {email}")

    def _create_books(self):
        for i, book_data in enumerate(BOOKS_DATA):
            book, created = Book.objects.get_or_create(
                product_id=book_data["product_id"],
                defaults={
                    "title": book_data["title"],
                    "slug": slugify(book_data["title"]),
                    "price": book_data["price"],
                    "status": book_data["status"],
                    "description": book_data["description"],
                    "display_order": i,
                }
            )
            action = "Created" if created else "Exists"
            self.stdout.write(f"  📚 {action} book: {book.title}")

            for j, spec_data in enumerate(book_data.get("specialties", [])):
                specialty, _ = Specialty.objects.get_or_create(
                    book=book, slug=slugify(spec_data["name"]),
                    defaults={
                        "name": spec_data["name"],
                        "description": f"Topics related to {spec_data['name']}.",
                        "display_order": j,
                    }
                )
                self.stdout.write(f"    🎯 Specialty: {specialty.name}")

                for k, topic_data in enumerate(spec_data.get("topics", [])):
                    Topic.objects.get_or_create(
                        specialty=specialty, slug=slugify(topic_data["title"]),
                        defaults={
                            "title": topic_data["title"],
                            "content": topic_data["content"],
                            "key_points": topic_data.get("key_points", []),
                            "display_order": k,
                            "is_board_basics": random.choice([True, False]),
                        }
                    )
                    self.stdout.write(f"      📖 Topic: {topic_data['title']}")

    def _create_questions(self):
        for q_data in QUESTIONS_DATA:
            specialty = Specialty.objects.filter(name=q_data["specialty_ref"]).first()
            if not specialty:
                continue
            topic = specialty.topics.first()
            q, created = Question.objects.get_or_create(
                educational_objective=q_data["educational_objective"],
                defaults={
                    "specialty": specialty,
                    "topic": topic,
                    "question_text": q_data["question_text"],
                    "option_a": q_data["options"][0],
                    "option_b": q_data["options"][1],
                    "option_c": q_data["options"][2],
                    "option_d": q_data["options"][3],
                    "option_e": q_data["options"][4] if len(q_data["options"]) > 4 else "",
                    "correct_answer": q_data["correct"],
                    "explanation": q_data["explanation"],
                    "difficulty": q_data["difficulty"],
                }
            )
            if created:
                self.stdout.write(f"  ❓ Created question: {q_data['educational_objective'][:60]}")

    def _create_flashcards(self):
        for fc_data in FLASHCARDS_DATA:
            specialty = Specialty.objects.filter(name=fc_data["specialty_ref"]).first()
            if not specialty:
                continue
            Flashcard.objects.get_or_create(
                front_text=fc_data["front"],
                defaults={
                    "specialty": specialty,
                    "topic": specialty.topics.first(),
                    "back_text": fc_data["back"],
                }
            )
        self.stdout.write(f"  ⚡ Created {len(FLASHCARDS_DATA)} flashcards")

    def _create_access(self):
        users = User.objects.filter(role="student")
        books = Book.objects.filter(status="active")
        for user in users:
            for book in books[:3]:  # Give first 3 books to each user
                UserBookAccess.objects.get_or_create(
                    user=user, book=book,
                    defaults={"order_id": f"ORD-{random.randint(10000,99999)}", "source": "webhook"}
                )
        self.stdout.write(f"  🔑 Granted book access to {users.count()} users")

    def _create_cme(self):
        specialties = Specialty.objects.all()[:5]
        for spec in specialties:
            CMEActivity.objects.get_or_create(
                title=f"{spec.name} — Syllabus Review",
                defaults={
                    "activity_type": "syllabus",
                    "credits": round(random.uniform(1.0, 3.0), 1),
                    "specialty": spec,
                }
            )
        self.stdout.write(f"  🏆 Created {specialties.count()} CME activities")

    def _create_webhook_logs(self):
        now = timezone.now()
        logs = [
            {"order_id": "ORD-78234", "email": "dr.sarah@example.com", "status": "processed",
             "sig": True, "user_created": True, "books": 3},
            {"order_id": "ORD-78235", "email": "dr.ahmed@example.com", "status": "processed",
             "sig": True, "user_created": True, "books": 2},
            {"order_id": "ORD-78236", "email": "invalid@test.com", "status": "failed",
             "sig": False, "user_created": False, "books": 0},
        ]
        for i, log in enumerate(logs):
            WebhookLog.objects.get_or_create(
                order_id=log["order_id"],
                defaults={
                    "customer_email": log["email"],
                    "payload_json": {
                        "order_id": log["order_id"],
                        "customer": {"email": log["email"], "first_name": "Demo", "last_name": "User"},
                        "products": [{"product_id": "MEDIGEST-CV-001", "title": "Cardiovascular Medicine"}],
                    },
                    "signature_valid": log["sig"],
                    "processing_status": log["status"],
                    "user_created": log["user_created"],
                    "books_granted": log["books"],
                    "ip_address": "203.0.113.42",
                    "error_message": "HMAC signature verification failed" if not log["sig"] else "",
                }
            )
        self.stdout.write(f"  📡 Created {len(logs)} webhook logs")
