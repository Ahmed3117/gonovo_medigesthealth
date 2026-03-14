"""
Management command: seed_demo_data
Creates a demo student user + full rich content so every GET endpoint returns data.

Demo Student Credentials:
  Email   : student@medigest.com
  Password: Student123!

Run: python manage.py seed_demo_data
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta
import random

# ─────────────────────────────────────────────
# DEMO STUDENT
# ─────────────────────────────────────────────
DEMO_STUDENT = {
    "email": "student@medigest.com",
    "password": "Student123!",
    "first_name": "Alex",
    "last_name": "Carter",
    "role": "student",
    "theme": "dark",
    "font_size": "medium",
    "current_study_streak": 7,
    "longest_study_streak": 14,
}

# ─────────────────────────────────────────────
# BOOKS + SPECIALTIES + TOPICS
# ─────────────────────────────────────────────
BOOKS = [
    {
        "title": "Cardiovascular Medicine",
        "product_id": "MEDIGEST-CV-001",
        "price": 55.00,
        "status": "active",
        "display_order": 1,
        "estimated_pages": 870,
        "description": "<p>Comprehensive review of <strong>cardiovascular medicine</strong> covering screening, diagnosis, and management of heart diseases, dyslipidemia, arrhythmias, heart failure, and vascular disorders.</p>",
        "specialties": [
            {
                "name": "Dyslipidemia",
                "is_core": True,
                "core_order": 1,
                "topics": [
                    {
                        "title": "Evaluation of Lipid Levels",
                        "board_basics": True,
                        "estimated_tasks": 3,
                        "content": "<h2>Evaluation of Lipid Levels</h2><p>A standard lipid panel measures <strong>total cholesterol, LDL cholesterol, HDL cholesterol, and triglycerides</strong>.</p><h3>Screening Recommendations</h3><ul><li>Diabetes mellitus</li><li>Hypertension</li><li>Smoking</li><li>Family history of premature CVD</li></ul><h3>Interpreting Results</h3><p>Optimal LDL cholesterol is &lt;100 mg/dL, with a target of &lt;70 mg/dL for very high-risk patients.</p>",
                        "key_points": ["Screening for dyslipidemia should begin at age 20 in those with CV risk factors.", "LDL cholesterol is the primary target for lipid-lowering therapy.", "A fasting lipid panel is preferred for accurate triglyceride measurement."],
                    },
                    {
                        "title": "Management of Dyslipidemias",
                        "board_basics": True,
                        "estimated_tasks": 4,
                        "content": "<h2>Management of Dyslipidemias</h2><p>Statin therapy is the cornerstone of treatment for elevated LDL cholesterol.</p><h3>Statin Intensities</h3><table><thead><tr><th>Intensity</th><th>LDL Reduction</th><th>Examples</th></tr></thead><tbody><tr><td>High</td><td>&ge;50%</td><td>Atorvastatin 40-80 mg</td></tr><tr><td>Moderate</td><td>30-49%</td><td>Atorvastatin 10-20 mg</td></tr></tbody></table><h3>Non-Statin Therapies</h3><p>Ezetimibe and PCSK9 inhibitors for statin-intolerant patients.</p>",
                        "key_points": ["High-intensity statin therapy reduces LDL by ≥50%.", "PCSK9 inhibitors are reserved for very high-risk patients.", "Lifestyle modifications are first-line for all patients."],
                    },
                ],
            },
            {
                "name": "Heart Failure",
                "is_core": True,
                "core_order": 2,
                "topics": [
                    {
                        "title": "Heart Failure Classification",
                        "board_basics": True,
                        "estimated_tasks": 3,
                        "content": "<h2>Heart Failure Classification</h2><p>Heart failure is classified by <strong>LVEF</strong>:</p><ul><li><strong>HFrEF:</strong> LVEF &le;40%</li><li><strong>HFmrEF:</strong> LVEF 41-49%</li><li><strong>HFpEF:</strong> LVEF &ge;50%</li></ul><h3>Diagnostic Evaluation</h3><p>BNP &gt;100 pg/mL or NT-proBNP &gt;300 pg/mL suggests heart failure.</p>",
                        "key_points": ["HFrEF is defined as LVEF ≤40%.", "BNP >100 pg/mL suggests heart failure.", "Echocardiography is the primary imaging modality."],
                    },
                    {
                        "title": "Medical Therapy for HFrEF",
                        "board_basics": False,
                        "estimated_tasks": 4,
                        "content": "<h2>Guideline-Directed Medical Therapy</h2><p>The four pillars of HFrEF treatment:</p><ol><li><strong>ARNI</strong> (sacubitril-valsartan)</li><li><strong>Beta-blocker</strong></li><li><strong>MRA</strong> (spironolactone)</li><li><strong>SGLT2 inhibitor</strong> (dapagliflozin)</li></ol>",
                        "key_points": ["Four pillars: ARNI, beta-blocker, MRA, SGLT2i.", "Sacubitril-valsartan is preferred over ACEi/ARB.", "SGLT2 inhibitors reduce HF hospitalizations regardless of diabetes."],
                    },
                ],
            },
            {
                "name": "Arrhythmias",
                "is_core": True,
                "core_order": 3,
                "topics": [
                    {
                        "title": "Atrial Fibrillation",
                        "board_basics": True,
                        "estimated_tasks": 3,
                        "content": "<h2>Atrial Fibrillation</h2><p>AF is the most common sustained cardiac arrhythmia. Management focuses on rate control, rhythm control, and stroke prevention.</p><h3>Stroke Risk — CHA₂DS₂-VASc</h3><p>Anticoagulation recommended for scores &ge;2 (men) and &ge;3 (women).</p>",
                        "key_points": ["CHA₂DS₂-VASc guides anticoagulation.", "DOACs preferred over warfarin for non-valvular AF.", "Rate control target: resting HR <110 bpm (lenient strategy)."],
                    },
                ],
            },
        ],
    },
    {
        "title": "Pulmonary and Critical Care Medicine",
        "product_id": "MEDIGEST-PULM-001",
        "price": 60.00,
        "status": "active",
        "display_order": 2,
        "estimated_pages": 640,
        "description": "<p>In-depth coverage of <strong>pulmonary diseases</strong> and <strong>critical care</strong>, including airways disease, pulmonary vascular disease, pleural disease, and ICU management.</p>",
        "specialties": [
            {
                "name": "Airways Disease",
                "is_core": True,
                "core_order": 4,
                "topics": [
                    {
                        "title": "Asthma",
                        "board_basics": True,
                        "estimated_tasks": 4,
                        "content": "<h2>Asthma</h2><p>Chronic inflammatory airways disease with variable airflow obstruction.</p><h3>Stepwise Therapy</h3><ul><li><strong>Step 1:</strong> Low-dose ICS-formoterol as needed</li><li><strong>Step 2:</strong> Low-dose ICS daily + SABA as needed</li><li><strong>Step 3:</strong> Low-dose ICS-LABA</li><li><strong>Step 5:</strong> High-dose ICS-LABA + biologic</li></ul>",
                        "key_points": ["ICS-formoterol as needed preferred for mild asthma.", "Stepping up based on symptom frequency.", "Biologics target specific pathways in severe asthma."],
                    },
                    {
                        "title": "COPD",
                        "board_basics": True,
                        "estimated_tasks": 4,
                        "content": "<h2>COPD</h2><p>Persistent airflow limitation: post-bronchodilator <strong>FEV₁/FVC &lt;0.70</strong>.</p><h3>GOLD Groups</h3><ul><li><strong>Group A:</strong> Low risk, few symptoms — bronchodilator PRN</li><li><strong>Group B:</strong> Low risk, more symptoms — LABA or LAMA</li><li><strong>Group E:</strong> High exacerbation risk — LABA+LAMA ± ICS</li></ul>",
                        "key_points": ["Diagnosis: post-bronchodilator FEV₁/FVC <0.70.", "Smoking cessation is the only intervention proven to slow FEV₁ decline.", "Triple therapy for frequent exacerbators with eosinophilia."],
                    },
                ],
            },
            {
                "name": "Critical Care Medicine",
                "is_core": True,
                "core_order": 5,
                "topics": [
                    {
                        "title": "Sepsis and Septic Shock",
                        "board_basics": True,
                        "estimated_tasks": 5,
                        "content": "<h2>Sepsis</h2><p>Life-threatening organ dysfunction from dysregulated host response to infection.</p><h3>Hour-1 Bundle</h3><ol><li>Measure lactate</li><li>Blood cultures before antibiotics</li><li>Broad-spectrum antibiotics</li><li>30 mL/kg IV crystalloid</li><li>Vasopressors for MAP &lt;65</li></ol>",
                        "key_points": ["Sepsis: suspected infection + SOFA ≥2.", "Norepinephrine is first-line vasopressor.", "Hour-1 Bundle should start immediately."],
                    },
                    {
                        "title": "Mechanical Ventilation",
                        "board_basics": False,
                        "estimated_tasks": 3,
                        "content": "<h2>Mechanical Ventilation</h2><p>Lung-protective ventilation for ARDS:</p><ul><li><strong>Tidal volume:</strong> 6 mL/kg PBW</li><li><strong>Plateau pressure:</strong> &le;30 cmH₂O</li><li><strong>PEEP:</strong> Titrated to oxygenation</li></ul>",
                        "key_points": ["TV: 6 mL/kg predicted body weight.", "Keep plateau pressure ≤30 cmH₂O.", "Prone positioning improves survival in P/F <150."],
                    },
                ],
            },
        ],
    },
    {
        "title": "Nephrology",
        "product_id": "MEDIGEST-NEPH-001",
        "price": 50.00,
        "status": "active",
        "display_order": 3,
        "estimated_pages": 480,
        "description": "<p>Complete review of <strong>nephrology</strong> covering AKI, CKD, fluid/electrolyte disorders, and glomerular diseases.</p>",
        "specialties": [
            {
                "name": "Acute Kidney Injury",
                "is_core": True,
                "core_order": 6,
                "topics": [
                    {
                        "title": "AKI Classification and Diagnosis",
                        "board_basics": True,
                        "estimated_tasks": 3,
                        "content": "<h2>Acute Kidney Injury</h2><p>KDIGO criteria: sCr increase &ge;0.3 mg/dL in 48h, or &ge;1.5× baseline in 7 days, or UO &lt;0.5 mL/kg/h for 6h.</p><ul><li><strong>Pre-renal:</strong> Volume depletion, HF</li><li><strong>Intrinsic:</strong> ATN, AIN, GN</li><li><strong>Post-renal:</strong> Obstruction</li></ul>",
                        "key_points": ["AKI: ≥0.3 mg/dL sCr rise in 48h or ≥1.5× in 7 days.", "FENa <1% = pre-renal; FENa >2% = intrinsic.", "Muddy brown casts = ATN."],
                    },
                ],
            },
            {
                "name": "Chronic Kidney Disease",
                "is_core": True,
                "core_order": 7,
                "topics": [
                    {
                        "title": "CKD Staging and Management",
                        "board_basics": True,
                        "estimated_tasks": 4,
                        "content": "<h2>Chronic Kidney Disease</h2><p>Staged by GFR and albuminuria.</p><h3>Key Interventions</h3><ul><li><strong>ACEi/ARB</strong> for proteinuria</li><li><strong>SGLT2i</strong> to slow progression</li><li><strong>BP target</strong> &lt;130/80 mmHg</li><li><strong>Finerenone</strong> for diabetic CKD</li></ul>",
                        "key_points": ["SGLT2 inhibitors slow CKD progression regardless of diabetes.", "ACEi/ARB first-line for proteinuric CKD.", "Refer to nephrology when GFR <30."],
                    },
                ],
            },
        ],
    },
    {
        "title": "Infectious Diseases",
        "product_id": "MEDIGEST-ID-001",
        "price": 50.00,
        "status": "active",
        "display_order": 4,
        "estimated_pages": 520,
        "description": "<p>Coverage of <strong>infectious diseases</strong> including HIV, hepatitis, respiratory infections, and antimicrobial stewardship.</p>",
        "specialties": [
            {
                "name": "Community-Acquired Pneumonia",
                "is_core": True,
                "core_order": 8,
                "topics": [
                    {
                        "title": "CAP Diagnosis and Treatment",
                        "board_basics": True,
                        "estimated_tasks": 3,
                        "content": "<h2>Community-Acquired Pneumonia</h2><p>CURB-65 guides site-of-care: 0-1 outpatient, 2 consider admission, &ge;3 ICU.</p><h3>Empiric Antibiotics</h3><ul><li><strong>Outpatient:</strong> Amoxicillin or doxycycline</li><li><strong>Inpatient:</strong> Beta-lactam + macrolide, or respiratory FQ</li></ul>",
                        "key_points": ["CURB-65 guides disposition.", "Procalcitonin helps distinguish bacterial vs viral.", "Blood cultures for all hospitalized CAP patients."],
                    },
                ],
            },
        ],
    },
    {
        "title": "Hematology and Oncology",
        "product_id": "MEDIGEST-HEMONC-001",
        "price": 60.00,
        "status": "active",
        "display_order": 5,
        "estimated_pages": 700,
        "description": "<p>Review of <strong>hematology and oncology</strong> covering anemias, coagulation, hematologic malignancies, and solid tumors.</p>",
        "specialties": [
            {
                "name": "Anemia",
                "is_core": True,
                "core_order": 9,
                "topics": [
                    {
                        "title": "Approach to Anemia",
                        "board_basics": True,
                        "estimated_tasks": 3,
                        "content": "<h2>Approach to Anemia</h2><p>Classified by MCV:</p><ul><li><strong>Microcytic (MCV &lt;80):</strong> Fe deficiency, thalassemia</li><li><strong>Normocytic (80-100):</strong> CKD, chronic disease</li><li><strong>Macrocytic (&gt;100):</strong> B12/folate deficiency</li></ul><h3>Iron Deficiency</h3><p>Ferritin &lt;30 ng/mL is diagnostic.</p>",
                        "key_points": ["Ferritin <30 ng/mL diagnoses iron deficiency.", "Reticulocyte count distinguishes production vs destruction.", "Iron deficiency in men/postmenopausal women → GI evaluation."],
                    },
                ],
            },
        ],
    },
    {
        "title": "Gastroenterology and Hepatology",
        "product_id": "MEDIGEST-GI-001",
        "price": 55.00,
        "status": "coming_soon",
        "display_order": 6,
        "estimated_pages": 0,
        "description": "<p>Coming soon — comprehensive coverage of GI and liver diseases.</p>",
        "specialties": [],
    },
    {
        "title": "Endocrinology",
        "product_id": "MEDIGEST-ENDO-001",
        "price": 55.00,
        "status": "coming_soon",
        "display_order": 7,
        "estimated_pages": 0,
        "description": "<p>Coming soon — diabetes, thyroid, adrenal, and metabolic disorders.</p>",
        "specialties": [],
    },
]

# ─────────────────────────────────────────────
# QUESTIONS
# ─────────────────────────────────────────────
QUESTIONS = [
    {
        "specialty": "Dyslipidemia",
        "stem": "<p>A 55-year-old man with type 2 diabetes and hypertension has LDL 145 mg/dL despite lifestyle changes. 10-year ASCVD risk is 18%. No prior ASCVD. Which is the most appropriate next step?</p>",
        "a": "Ezetimibe alone",
        "b": "High-intensity statin therapy",
        "c": "Moderate-intensity statin therapy",
        "d": "PCSK9 inhibitor",
        "e": "Omega-3 fatty acids",
        "correct": "B",
        "difficulty": "medium",
        "care_type": "ambulatory",
        "demographic": "adult",
        "explanation": "<p><strong>High-intensity statin</strong> is indicated for patients 40-75 with diabetes and 10-year ASCVD risk ≥7.5%. High-intensity statins reduce LDL by ≥50%.</p>",
        "objective": "Prescribe high-intensity statin for diabetic patients with elevated ASCVD risk.",
        "key_point": "For patients with diabetes aged 40-75, high-intensity statin is indicated regardless of baseline LDL if 10-year ASCVD risk ≥7.5%.",
        "references": [{"text": "Grundy SM et al. 2018 ACC/AHA Cholesterol Guideline. JACC 2019.", "pmid": "30423393"}],
        "lab_values": [{"name": "LDL Cholesterol", "value": "145", "unit": "mg/dL", "flag": "H", "ref_range": "<100"}],
    },
    {
        "specialty": "Heart Failure",
        "stem": "<p>A 62-year-old woman with NYHA class III HF and LVEF 28% takes lisinopril, carvedilol, and spironolactone. BP 118/72 mmHg. Which medication should be added?</p>",
        "a": "Amlodipine",
        "b": "Dapagliflozin",
        "c": "Digoxin",
        "d": "Hydralazine-isosorbide dinitrate",
        "e": "Ivabradine",
        "correct": "B",
        "difficulty": "medium",
        "care_type": "ambulatory",
        "demographic": "adult",
        "explanation": "<p><strong>Dapagliflozin</strong> (SGLT2 inhibitor) is the fourth pillar of HFrEF therapy. DAPA-HF trial showed 26% reduction in CV death and HF hospitalization.</p>",
        "objective": "Add SGLT2 inhibitor as the fourth pillar of GDMT for HFrEF.",
        "key_point": "SGLT2 inhibitors reduce HF hospitalizations and CV death in HFrEF patients regardless of diabetes status.",
        "references": [{"text": "McMurray JJV et al. DAPA-HF Trial. NEJM 2019.", "pmid": "31535829"}],
        "lab_values": [],
    },
    {
        "specialty": "Airways Disease",
        "stem": "<p>A 45-year-old smoker (30 pack-years) has FEV₁/FVC 0.62, FEV₁ 55% predicted, and 2 exacerbations last year requiring oral corticosteroids. Best initial maintenance therapy?</p>",
        "a": "ICS alone",
        "b": "LABA alone",
        "c": "LABA + LAMA combination",
        "d": "LAMA alone",
        "e": "Short-acting bronchodilator PRN",
        "correct": "C",
        "difficulty": "medium",
        "care_type": "ambulatory",
        "demographic": "adult",
        "explanation": "<p>Per GOLD guidelines, this patient is <strong>Group E</strong> (≥2 moderate exacerbations). Recommended: <strong>LABA + LAMA</strong>. Add ICS if eosinophils ≥300 cells/µL.</p>",
        "objective": "Initiate LABA + LAMA for COPD GOLD Group E patients.",
        "key_point": "GOLD Group E COPD (≥2 exacerbations or ≥1 hospitalization) requires LABA+LAMA as initial maintenance therapy.",
        "references": [{"text": "GOLD 2024 Report. Global Initiative for Chronic Obstructive Lung Disease.", "pmid": ""}],
        "lab_values": [{"name": "FEV₁/FVC", "value": "0.62", "unit": "", "flag": "L", "ref_range": ">0.70"}, {"name": "FEV₁ % predicted", "value": "55", "unit": "%", "flag": "L", "ref_range": ">80"}],
    },
    {
        "specialty": "Critical Care Medicine",
        "stem": "<p>A 68-year-old with CAP develops septic shock. After 30 mL/kg crystalloid, MAP remains 58 mmHg. Lactate 4.8 mmol/L. Broad-spectrum antibiotics given. Next step?</p>",
        "a": "Additional 30 mL/kg IV crystalloid",
        "b": "Dobutamine infusion",
        "c": "Epinephrine infusion",
        "d": "Norepinephrine infusion",
        "e": "Vasopressin infusion",
        "correct": "D",
        "difficulty": "easy",
        "care_type": "icu",
        "demographic": "elderly",
        "explanation": "<p><strong>Norepinephrine</strong> is the first-line vasopressor for septic shock. Vasopressin can be added as a second agent. Dobutamine is for cardiac dysfunction.</p>",
        "objective": "Select norepinephrine as first-line vasopressor for septic shock.",
        "key_point": "Norepinephrine is the vasopressor of choice for septic shock; it reduces mortality compared to dopamine.",
        "references": [{"text": "Rhodes A et al. Surviving Sepsis Guidelines 2016. Intensive Care Med.", "pmid": "27738085"}],
        "lab_values": [{"name": "MAP", "value": "58", "unit": "mmHg", "flag": "L", "ref_range": ">65"}, {"name": "Lactate", "value": "4.8", "unit": "mmol/L", "flag": "H", "ref_range": "<2.0"}],
    },
    {
        "specialty": "Acute Kidney Injury",
        "stem": "<p>A 72-year-old man has oliguria and sCr 3.2 mg/dL (baseline 1.1). Recently started ibuprofen. FENa 0.4%, no casts, no hydronephrosis on US. Most likely diagnosis?</p>",
        "a": "Acute interstitial nephritis",
        "b": "Acute tubular necrosis",
        "c": "Post-renal obstruction",
        "d": "Pre-renal azotemia",
        "e": "Rapidly progressive glomerulonephritis",
        "correct": "D",
        "difficulty": "easy",
        "care_type": "ambulatory",
        "demographic": "elderly",
        "explanation": "<p>Low <strong>FENa (&lt;1%)</strong> with bland urinalysis = <strong>pre-renal azotemia</strong>. NSAIDs cause afferent arteriolar vasoconstriction. ATN has FENa &gt;2% and muddy brown casts.</p>",
        "objective": "Diagnose NSAID-induced pre-renal azotemia based on FENa and urinalysis.",
        "key_point": "FENa <1% with bland urinalysis and recent NSAID use = pre-renal AKI. Discontinue the offending agent and volume resuscitate.",
        "references": [{"text": "Pannu N, Nadim MK. An overview of drug-induced AKI. Crit Care Med 2008.", "pmid": "18382196"}],
        "lab_values": [{"name": "Creatinine", "value": "3.2", "unit": "mg/dL", "flag": "H", "ref_range": "0.6-1.2"}, {"name": "FENa", "value": "0.4", "unit": "%", "flag": "L", "ref_range": ">1 for ATN"}],
    },
    {
        "specialty": "Anemia",
        "stem": "<p>A 34-year-old woman has Hgb 8.1 g/dL, MCV 71 fL. Ferritin is 8 ng/mL. She has menorrhagia. What is the most appropriate treatment?</p>",
        "a": "B12 injections",
        "b": "Erythropoiesis-stimulating agents",
        "c": "Folate supplementation",
        "d": "Oral iron supplementation",
        "e": "Packed red blood cell transfusion",
        "correct": "D",
        "difficulty": "easy",
        "care_type": "ambulatory",
        "demographic": "adult",
        "explanation": "<p>Microcytic anemia (MCV &lt;80) with low ferritin (8 ng/mL) confirms <strong>iron deficiency anemia</strong> from menorrhagia. First-line treatment is <strong>oral iron</strong>.</p>",
        "objective": "Treat iron deficiency anemia with oral iron supplementation.",
        "key_point": "Ferritin <30 ng/mL confirms iron deficiency. Oral iron is first-line in hemodynamically stable patients.",
        "references": [{"text": "Short MW, Domagalski JE. Iron deficiency anemia. AFP 2013.", "pmid": "23362099"}],
        "lab_values": [{"name": "Hemoglobin", "value": "8.1", "unit": "g/dL", "flag": "L", "ref_range": "12-16"}, {"name": "MCV", "value": "71", "unit": "fL", "flag": "L", "ref_range": "80-100"}, {"name": "Ferritin", "value": "8", "unit": "ng/mL", "flag": "L", "ref_range": "12-150"}],
    },
    {
        "specialty": "Community-Acquired Pneumonia",
        "stem": "<p>A 58-year-old with COPD presents with fever, productive cough, and RR 24. CXR shows right lower lobe infiltrate. CURB-65 score is 2. Most appropriate management?</p>",
        "a": "Admit to ICU",
        "b": "Admit to general ward with IV antibiotics",
        "c": "Outpatient amoxicillin",
        "d": "Outpatient azithromycin alone",
        "e": "Repeat chest X-ray in 48 hours",
        "correct": "B",
        "difficulty": "medium",
        "care_type": "inpatient",
        "demographic": "adult",
        "explanation": "<p>CURB-65 of 2 indicates hospital admission is warranted. Inpatient regimen: beta-lactam + macrolide, or respiratory fluoroquinolone monotherapy.</p>",
        "objective": "Use CURB-65 to guide CAP disposition and antibiotic selection.",
        "key_point": "CURB-65 score 2 → consider hospital admission. Score ≥3 → ICU evaluation.",
        "references": [{"text": "Mandell LA et al. IDSA/ATS CAP Guidelines. CID 2007.", "pmid": "17278083"}],
        "lab_values": [{"name": "RR", "value": "24", "unit": "/min", "flag": "H", "ref_range": "12-20"}],
    },
    {
        "specialty": "Arrhythmias",
        "stem": "<p>A 70-year-old with hypertension and AF has CHA₂DS₂-VASc score of 3. He has no prior bleeding history. Which anticoagulation is most appropriate?</p>",
        "a": "Aspirin 81 mg daily",
        "b": "Aspirin + clopidogrel",
        "c": "Dabigatran 150 mg twice daily",
        "d": "Low-molecular-weight heparin",
        "e": "No anticoagulation needed",
        "correct": "C",
        "difficulty": "easy",
        "care_type": "ambulatory",
        "demographic": "elderly",
        "explanation": "<p>CHA₂DS₂-VASc ≥2 (men) or ≥3 (women) indicates anticoagulation. <strong>DOACs</strong> (dabigatran, rivaroxaban, apixaban) are preferred over warfarin for non-valvular AF.</p>",
        "objective": "Select appropriate anticoagulation for AF based on CHA₂DS₂-VASc score.",
        "key_point": "DOACs are preferred over warfarin for stroke prevention in non-valvular AF with CHA₂DS₂-VASc ≥2 (men).",
        "references": [{"text": "Hindricks G et al. 2020 ESC AF Guidelines. Eur Heart J 2021.", "pmid": "32860505"}],
        "lab_values": [],
    },
]

# ─────────────────────────────────────────────
# FLASHCARDS
# ─────────────────────────────────────────────
FLASHCARDS = [
    {"specialty": "Dyslipidemia", "front": "High-intensity statin: expected LDL reduction?", "back": "≥50% reduction (e.g., atorvastatin 40-80 mg, rosuvastatin 20-40 mg)"},
    {"specialty": "Dyslipidemia", "front": "When are PCSK9 inhibitors indicated?", "back": "Very high ASCVD risk who cannot reach target LDL with max statin + ezetimibe"},
    {"specialty": "Dyslipidemia", "front": "Triglyceride level that risks acute pancreatitis?", "back": "≥500 mg/dL — treat with fibrates as first-line"},
    {"specialty": "Heart Failure", "front": "Four pillars of HFrEF treatment?", "back": "1. ARNI (sacubitril-valsartan)\n2. Beta-blocker (carvedilol, metoprolol succinate)\n3. MRA (spironolactone)\n4. SGLT2 inhibitor (dapagliflozin)"},
    {"specialty": "Heart Failure", "front": "LVEF cutoff for HFrEF?", "back": "LVEF ≤ 40%"},
    {"specialty": "Heart Failure", "front": "BNP level suggesting heart failure?", "back": "BNP >100 pg/mL or NT-proBNP >300 pg/mL"},
    {"specialty": "Arrhythmias", "front": "CHA₂DS₂-VASc components?", "back": "C – Congestive HF\nH – Hypertension\nA₂ – Age ≥75 (2 pts)\nD – Diabetes\nS₂ – Stroke/TIA (2 pts)\nV – Vascular disease\nA – Age 65-74\nSc – Sex category (female)"},
    {"specialty": "Arrhythmias", "front": "Rate control target in AF (lenient strategy)?", "back": "Resting heart rate < 110 bpm"},
    {"specialty": "Airways Disease", "front": "COPD diagnosis spirometry criterion?", "back": "Post-bronchodilator FEV₁/FVC < 0.70"},
    {"specialty": "Airways Disease", "front": "Most effective intervention to slow COPD progression?", "back": "Smoking cessation — the only proven intervention to slow FEV₁ decline"},
    {"specialty": "Critical Care Medicine", "front": "First-line vasopressor for septic shock?", "back": "Norepinephrine"},
    {"specialty": "Critical Care Medicine", "front": "ARDS lung-protective tidal volume?", "back": "6 mL/kg predicted body weight"},
    {"specialty": "Critical Care Medicine", "front": "ARDS: survival benefit from prone positioning?", "back": "P/F ratio < 150 (moderate-severe ARDS) — PROSEVA trial"},
    {"specialty": "Acute Kidney Injury", "front": "FENa in pre-renal vs ATN?", "back": "Pre-renal: FENa < 1%\nATN (intrinsic): FENa > 2%"},
    {"specialty": "Chronic Kidney Disease", "front": "SGLT2 inhibitors in CKD: key benefit?", "back": "Slow CKD progression regardless of diabetes status (DAPA-CKD, EMPA-KIDNEY)"},
    {"specialty": "Community-Acquired Pneumonia", "front": "CURB-65 components?", "back": "C – Confusion\nU – Urea >7 mmol/L\nR – RR ≥30\nB – BP (SBP<90 or DBP≤60)\n65 – Age ≥65"},
    {"specialty": "Anemia", "front": "Ferritin level diagnostic of iron deficiency?", "back": "Ferritin < 30 ng/mL (< 15 ng/mL is diagnostic with high specificity)"},
    {"specialty": "Anemia", "front": "Peripheral smear findings in iron deficiency anemia?", "back": "Hypochromic, microcytic RBCs with pencil cells (elliptocytes) and target cells"},
]

# ─────────────────────────────────────────────
# CME ACTIVITIES
# ─────────────────────────────────────────────
CME_ACTIVITIES = [
    {"title": "Cardiovascular Medicine — Syllabus Review", "type": "syllabus", "credits": 2.5, "specialty": "Dyslipidemia"},
    {"title": "Heart Failure GDMT Quiz", "type": "quiz", "credits": 1.0, "specialty": "Heart Failure"},
    {"title": "Pulmonary Board Basics", "type": "board_basics", "credits": 1.5, "specialty": "Airways Disease"},
    {"title": "Critical Care — Individual Questions", "type": "question", "credits": 0.25, "specialty": "Critical Care Medicine"},
    {"title": "Nephrology — Syllabus Review", "type": "syllabus", "credits": 2.0, "specialty": "Acute Kidney Injury"},
    {"title": "Infectious Disease — CAP Quiz", "type": "quiz", "credits": 0.75, "specialty": "Community-Acquired Pneumonia"},
    {"title": "Hematology Board Basics", "type": "board_basics", "credits": 1.25, "specialty": "Anemia"},
]


class Command(BaseCommand):
    help = (
        "Seed demo data for frontend testing.\n"
        "Creates student@medigest.com / Student123! with complete activity data."
    )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("\n🌱 Seeding MEDIGEST demo data...\n"))

        student = self._create_student()
        self._create_books_and_specialties()
        self._create_questions()
        self._create_flashcards()
        self._grant_book_access(student)
        self._create_cme(student)
        self._create_student_activity(student)
        self._create_webhook_logs()

        self.stdout.write(self.style.SUCCESS(
            "\n✅ Demo data seeded successfully!\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  Student Login\n"
            "  Email   : student@medigest.com\n"
            "  Password: Student123!\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        ))

    # ── Helpers ──────────────────────────────────────────────

    def _create_student(self):
        from accounts.models import User
        d = DEMO_STUDENT
        user, created = User.objects.get_or_create(
            email=d["email"],
            defaults={
                "first_name": d["first_name"],
                "last_name": d["last_name"],
                "role": d["role"],
                "theme": d["theme"],
                "font_size": d["font_size"],
                "current_study_streak": d["current_study_streak"],
                "longest_study_streak": d["longest_study_streak"],
                "last_study_date": timezone.now().date() - timedelta(days=1),
            }
        )
        if created:
            user.set_password(d["password"])
            user.save()
            self.stdout.write(f"  👤 Created student: {d['email']}")
        else:
            self.stdout.write(f"  ⏭️  Student exists: {d['email']}")
        return user

    def _create_books_and_specialties(self):
        from books.models import Book, Specialty, Topic
        for book_data in BOOKS:
            book, created = Book.objects.get_or_create(
                product_id=book_data["product_id"],
                defaults={
                    "title": book_data["title"],
                    "slug": slugify(book_data["title"]),
                    "price": book_data["price"],
                    "status": book_data["status"],
                    "display_order": book_data["display_order"],
                    "estimated_pages": book_data["estimated_pages"],
                    "description": book_data["description"],
                }
            )
            self.stdout.write(f"  📚 {'Created' if created else 'Exists'}: {book.title}")
            for j, sd in enumerate(book_data.get("specialties", [])):
                spec, _ = Specialty.objects.get_or_create(
                    book=book,
                    slug=slugify(sd["name"]),
                    defaults={
                        "name": sd["name"],
                        "display_order": j,
                        "is_core_specialty": sd.get("is_core", False),
                        "core_display_order": sd.get("core_order", 0),
                        "description": f"Topics related to {sd['name']}.",
                    }
                )
                for k, td in enumerate(sd.get("topics", [])):
                    Topic.objects.get_or_create(
                        specialty=spec,
                        slug=slugify(td["title"]),
                        defaults={
                            "title": td["title"],
                            "key_points": td.get("key_points", []),
                            "display_order": k,
                            "is_board_basics": td.get("board_basics", False),
                            "estimated_tasks": td.get("estimated_tasks", 3),
                        }
                    )
                    self.stdout.write(f"      📖 {td['title']}")

    def _create_questions(self):
        from books.models import Specialty
        from questions.models import Question
        for qd in QUESTIONS:
            spec = Specialty.objects.filter(name=qd["specialty"]).first()
            if not spec:
                self.stdout.write(self.style.ERROR(f"  ⚠️  Specialty not found: {qd['specialty']}"))
                continue
            topic = spec.topics.first()
            q, created = Question.objects.get_or_create(
                educational_objective=qd["objective"],
                defaults={
                    "specialty": spec,
                    "topic": topic,
                    "question_text": qd["stem"],
                    "option_a": qd["a"],
                    "option_b": qd["b"],
                    "option_c": qd["c"],
                    "option_d": qd["d"],
                    "option_e": qd.get("e", ""),
                    "correct_answer": qd["correct"],
                    "difficulty": qd["difficulty"],
                    "explanation": qd["explanation"],
                    "key_point": qd["key_point"],
                    "references": qd.get("references", []),
                    "lab_values": qd.get("lab_values", []),
                    "care_type": qd.get("care_type", ""),
                    "patient_demographic": qd.get("demographic", ""),
                }
            )
            if created:
                self.stdout.write(f"  ❓ Question: {qd['objective'][:60]}")

    def _create_flashcards(self):
        from books.models import Specialty
        from flashcards.models import Flashcard
        for i, fd in enumerate(FLASHCARDS):
            spec = Specialty.objects.filter(name=fd["specialty"]).first()
            if not spec:
                continue
            Flashcard.objects.get_or_create(
                front_text=fd["front"],
                defaults={
                    "specialty": spec,
                    "book": spec.book,
                    "topic": spec.topics.first(),
                    "back_text": fd["back"],
                    "display_order": i,
                }
            )
        self.stdout.write(f"  ⚡ {len(FLASHCARDS)} flashcards created/verified")

    def _grant_book_access(self, student):
        from books.models import Book, UserBookAccess
        active_books = Book.objects.filter(status="active")
        for book in active_books:
            UserBookAccess.objects.get_or_create(
                user=student,
                book=book,
                defaults={
                    "order_id": f"DEMO-{random.randint(10000, 99999)}",
                    "source": "manual_admin",
                }
            )
        self.stdout.write(f"  🔑 Book access granted to {student.email} for {active_books.count()} books")

    def _create_cme(self, student):
        from books.models import Specialty
        from questions.models import Question
        from certificates.models import CMEActivity, UserCMECredit, CMESubmission, UserCOREProgress, Certificate
        now = timezone.now()

        for cd in CME_ACTIVITIES:
            spec = Specialty.objects.filter(name=cd["specialty"]).first()
            activity, _ = CMEActivity.objects.get_or_create(
                title=cd["title"],
                defaults={
                    "activity_type": cd["type"],
                    "credits": cd["credits"],
                    "specialty": spec,
                    "description": f"Earn {cd['credits']} CME credits by completing this activity.",
                }
            )
            # Earn the credit for student
            credit, created = UserCMECredit.objects.get_or_create(
                user=student,
                activity=activity,
                defaults={
                    "credits_earned": cd["credits"],
                    "status": "earned",
                    "credit_year": 2026,
                }
            )

        total_credits = UserCMECredit.objects.filter(user=student).count() * 1.0
        # CME Submission
        sub, _ = CMESubmission.objects.get_or_create(
            user=student,
            accreditation_body="ama",
            credit_year=2026,
            defaults={
                "credits_claimed": 4.25,
                "status": "pending",
            }
        )

        # CORE progress for core specialties
        from books.models import Specialty as Spec
        core_specs = Spec.objects.filter(is_core_specialty=True)
        statuses = ["completed", "in_progress", "pending"]
        for i, spec in enumerate(core_specs):
            q_count = spec.questions.count()
            correct = int(q_count * 0.72)
            UserCOREProgress.objects.get_or_create(
                user=student,
                specialty=spec,
                defaults={
                    "badge_status": statuses[i % 3],
                    "questions_answered": q_count,
                    "questions_correct": correct,
                    "last_30_correct": min(20, correct),
                    "last_30_total": min(30, q_count),
                    "core_quiz_unlocked": i % 3 != 2,
                    "badge_earned_at": now if i % 3 == 0 else None,
                    "last_accessed_at": now - timedelta(days=i),
                }
            )

        # Certificate
        Certificate.objects.get_or_create(
            user=student,
            certificate_type="cme",
            title="CME Credit Certificate 2026",
            defaults={
                "description": "Certificate of Completion for CME activities completed in 2026.",
                "total_credits": 4.25,
                "credit_year": 2026,
            }
        )
        self.stdout.write(f"  🏆 CME activities, credits, CORE progress, and certificate created")

    def _create_student_activity(self, student):
        from books.models import Topic, Specialty
        from questions.models import Question, QuizSession, UserQuestionAttempt
        from flashcards.models import Flashcard, UserFlashcardProgress, UserCustomFlashcard
        from learning.models import (
            UserTopicProgress, UserHighlight, UserNote, UserBookmark,
            UserLearningPlanTopic, UserStudySession, RecentActivity
        )
        now = timezone.now()

        topics = list(Topic.objects.all())
        questions = list(Question.objects.all())
        flashcards = list(Flashcard.objects.all())

        # Topic progress
        for i, topic in enumerate(topics[:8]):
            UserTopicProgress.objects.get_or_create(
                user=student, topic=topic,
                defaults={
                    "is_completed": i < 5,
                    "reading_time_seconds": random.randint(300, 1800),
                    "tasks_completed": random.randint(1, 3),
                }
            )

        # Highlights
        for i, topic in enumerate(topics[:4]):
            UserHighlight.objects.get_or_create(
                user=student, topic=topic,
                highlighted_text=f"Sample highlighted text from {topic.title}",
                defaults={
                    "start_offset": i * 100,
                    "end_offset": i * 100 + 40,
                    "color": ["yellow", "green", "blue", "pink"][i % 4],
                }
            )

        # Notes
        for i, topic in enumerate(topics[:3]):
            UserNote.objects.get_or_create(
                user=student, topic=topic,
                content=f"Study note for {topic.title}: Remember the key clinical pearls.",
                defaults={"position_offset": i * 50}
            )

        # Bookmarks
        for i, topic in enumerate(topics[:4]):
            UserBookmark.objects.get_or_create(
                user=student, topic=topic,
                section_anchor=f"section-{i+1}",
                defaults={"label": f"Important section in {topic.title}"}
            )

        # Learning Plan
        for topic in topics[:5]:
            UserLearningPlanTopic.objects.get_or_create(user=student, topic=topic)

        # Quiz session + attempts
        if questions:
            session, _ = QuizSession.objects.get_or_create(
                user=student,
                title="Cardiology Practice Quiz",
                defaults={
                    "mode": "practice",
                    "total_questions": min(8, len(questions)),
                    "correct_count": 6,
                    "total_time_seconds": 720,
                    "is_completed": True,
                    "show_explanations": True,
                    "completed_at": now - timedelta(hours=2),
                }
            )
            for q in questions[:8]:
                is_correct = random.random() > 0.3
                sel = q.correct_answer if is_correct else (
                    "A" if q.correct_answer != "A" else "B"
                )
                UserQuestionAttempt.objects.get_or_create(
                    user=student, question=q,
                    defaults={
                        "selected_answer": sel,
                        "is_correct": is_correct,
                        "time_spent_seconds": random.randint(30, 150),
                        "is_saved": random.random() > 0.7,
                        "quiz_session": session,
                    }
                )

        # Flashcard progress
        for fc in flashcards[:12]:
            UserFlashcardProgress.objects.get_or_create(
                user=student, flashcard=fc,
                defaults={
                    "confidence": random.randint(1, 4),
                    "times_reviewed": random.randint(1, 5),
                    "last_reviewed_at": now - timedelta(days=random.randint(0, 5)),
                }
            )

        # Custom flashcard
        if topics:
            UserCustomFlashcard.objects.get_or_create(
                user=student,
                front_text="What are the 4 pillars of HFrEF treatment?",
                defaults={
                    "back_text": "ARNI, Beta-blocker, MRA, SGLT2 inhibitor",
                    "topic": topics[0],
                }
            )

        # Study sessions
        session_types = ["reading", "quiz", "flashcard", "board_basics"]
        books_qs = list(__import__("books").models.Book.objects.filter(status="active"))
        for i, stype in enumerate(session_types):
            started = now - timedelta(days=i, hours=random.randint(1, 5))
            UserStudySession.objects.get_or_create(
                user=student,
                session_type=stype,
                started_at=started,
                defaults={
                    "duration_seconds": random.randint(900, 5400),
                    "book": books_qs[i % len(books_qs)] if books_qs else None,
                    "ended_at": started + timedelta(seconds=random.randint(900, 5400)),
                }
            )

        # Recent activity
        activity_entries = [
            ("reading", "Dyslipidemia — Evaluation of Lipid Levels", "Completed topic reading"),
            ("quiz", "Cardiology Practice Quiz — 6/8 correct", "75% score"),
            ("flashcard", "Heart Failure Flashcard Deck", "12 cards reviewed"),
            ("board_basics", "COPD Board Basics", "Read key points"),
            ("core", "Arrhythmias CORE Practice", "Badge in progress"),
        ]
        for atype, title, desc in activity_entries:
            RecentActivity.objects.get_or_create(
                user=student, title=title,
                defaults={"activity_type": atype, "description": desc}
            )

        self.stdout.write(f"  📊 Student activity seeded (progress, highlights, notes, quizzes, flashcards)")

    def _create_webhook_logs(self):
        from webhooks.models import WebhookLog
        logs = [
            {"order_id": "DEMO-ORD-001", "email": "student@medigest.com", "status": "processed",
             "sig": True, "user_created": False, "books": 5},
            {"order_id": "DEMO-ORD-002", "email": "newstudent@example.com", "status": "processed",
             "sig": True, "user_created": True, "books": 2},
            {"order_id": "DEMO-ORD-003", "email": "bad@test.com", "status": "failed",
             "sig": False, "user_created": False, "books": 0},
        ]
        for log in logs:
            WebhookLog.objects.get_or_create(
                order_id=log["order_id"],
                defaults={
                    "customer_email": log["email"],
                    "payload_json": {
                        "order_id": log["order_id"],
                        "customer": {"email": log["email"]},
                        "products": [{"product_id": "MEDIGEST-CV-001"}],
                    },
                    "signature_valid": log["sig"],
                    "processing_status": log["status"],
                    "user_created": log["user_created"],
                    "books_granted": log["books"],
                    "ip_address": "203.0.113.42",
                    "error_message": "Invalid signature" if not log["sig"] else "",
                }
            )
        self.stdout.write(f"  📡 {len(logs)} webhook logs created/verified")
