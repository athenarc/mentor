# Screening Inspection

- **Review:** De‐escalation of antimicrobial treatment for adults with sepsis, severe sepsis or septic shock
- **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD007934.pub3/full
- **Screening criteria:** We planned to include randomized controlled trials (RCTs) comparing de‐escalation (based on culture results) versus standard therapy for adults with sepsis, severe sepsis or septic shock. The primary outcome was mortality (at 28 days, hospital discharge or at the end of the follow‐up period). Studies including patients initially treated with an empirical but not adequate antimicrobial therapy were not considered for inclusion.
- **Gold label policy:** `include_label_0_5`
- **Gold screening rule:** dataset labels 1.0 and 0.5 count as INCLUDE; 0.0 counts as EXCLUDE.
- **Matches:** 76 / 96
- **Mismatches:** 20
- **Missing decisions:** 0

## Mismatches

| Index | Predicted | Gold | Gold Outcome | Title | Agent Rationale |
|-------|-----------|------|--------------|-------|-----------------|
| 3 | EXCLUDE | INCLUDE | excluded_after_full_text | Prospective, randomized, controlled study comparing two dosing regimens of gentamicin/oral ciprofloxacin switch therapy for acute pyelonephritis | RCT comparing dosing regimens for pyelonephritis, not de-escalation based on culture results for sepsis. |
| 10 | EXCLUDE | INCLUDE | excluded_after_full_text | Antibiotic usage in an intensive care unit in a Danish university hospital | Observational study on antibiotic usage patterns, not an RCT. |
| 12 | EXCLUDE | INCLUDE | excluded_after_full_text | Use of procalcitonin to reduce patients' exposure to antibiotics in intensive care units (PRORATA trial): a multicentre randomised controlled trial | RCT on procalcitonin-guided therapy, not de-escalation based on culture results vs standard therapy. |
| 17 | EXCLUDE | INCLUDE | excluded_after_full_text | Comparison of procalcitonin (PCT) and C‐reactive protein (CRP) plasma concentrations at different SOFA scores during the course of sepsis and MODS | Observational study on PCT and CRP levels, not an RCT. |
| 20 | EXCLUDE | INCLUDE | excluded_after_full_text | The potential role of procalcitonin and interleukin 8 in the prediction of infected necrosis in acute pancreatitis | Observational study on PCT in pancreatitis, not sepsis/septic shock, not an RCT. |
| 24 | EXCLUDE | INCLUDE | excluded_after_full_text | Once‐daily versus twice‐daily administration of ceftazidime in the preterm infant | RCT on ceftazidime dosing in preterm infants, not adults, not sepsis/septic shock. |
| 27 | EXCLUDE | INCLUDE | excluded_after_full_text | The Procalcitonin And Survival Study (PASS) ‐ a randomised multi‐center investigator‐initiated trial to investigate whether daily measurements biomarker Procalcitonin and pro‐active diagnostic and therapeutic responses to abnormal Procalcitonin levels, can improve survival in intensive care unit patients. Calculated sample size (target population): 1000 patients | Study protocol for PCT trial, not completed RCT results. |
| 32 | EXCLUDE | INCLUDE | excluded_after_full_text | Procalcitonin to guide duration of antibiotic therapy in intensive care patients: a randomized prospective controlled trial | RCT on PCT-guided therapy in surgical ICU, not de-escalation based on culture results vs standard. |
| 38 | EXCLUDE | INCLUDE | excluded_after_full_text | Meta‐analysis of procalcitonin for sepsis detection | Letter to editor on meta-analysis, not an RCT. |
| 39 | EXCLUDE | INCLUDE | excluded_after_full_text | APACHE II: a severity of disease classification system | Methodological paper on APACHE II scoring, not an RCT. |
| 52 | EXCLUDE | INCLUDE | excluded_after_full_text | Procalcitonin in liver transplant patients ‐ yet another stone turned | Review article on PCT in liver transplant, not an RCT. |
| 55 | EXCLUDE | INCLUDE | excluded_after_full_text | Procalcitonin increase in early identification of critically ill patients at high risk of mortality | Observational cohort study on PCT and mortality, not an RCT. |
| 56 | EXCLUDE | INCLUDE | excluded_after_full_text | Piperacillin penetration into tissue of critically ill patients with sepsis‐‐bolus versus continuous administration? | RCT on piperacillin dosing (bolus vs continuous), not de-escalation based on culture results. |
| 69 | EXCLUDE | INCLUDE | excluded_after_full_text | The prevalence of nosocomial infection in intensive care units in Europe. Results of the European Prevalence of Infection in Intensive Care (EPIC) Study. EPIC International Advisory Committee | Prevalence study (EPIC study), not an RCT. |
| 77 | EXCLUDE | INCLUDE | excluded_after_full_text | Procalcitonin (PCT)‐guided algorithm reduces length of antibiotic treatment in surgical intensive care patients with severe sepsis: results of a prospective randomized study | RCT on PCT-guided therapy in surgical ICU with severe sepsis, not de-escalation based on culture results vs standard. |
| 83 | EXCLUDE | INCLUDE | excluded_after_full_text | Indications for antibiotic use in ICU patients: a one‐year prospective surveillance | Observational surveillance study, not an RCT. |
| 84 | EXCLUDE | INCLUDE | excluded_after_full_text | Narrow‐ versus broad‐spectrum parenteral anatimicrobials against common infections of childhood: a prospective and randomised comparison between penicillin and cefuroxime | RCT on narrow vs broad spectrum in children, not adults, not sepsis/septic shock. |
| 86 | EXCLUDE | INCLUDE | excluded_after_full_text | Effect of procalcitonin‐guided treatment on antibiotic use and outcome in lower respiratory tract infections: cluster‐randomised, single‐blinded intervention trial | Cluster-randomized trial on PCT-guided treatment in LRTI, not de-escalation based on culture results for sepsis. |
| 87 | EXCLUDE | INCLUDE | excluded_after_full_text | G‐CSF and IL‐8 for early diagnosis of sepsis in neonates and critically ill children ‐ safety and cost effectiveness of a new laboratory prediction model: study protocol of a randomized controlled trial [ISRCTN91123847] | Study protocol for RCT in neonates/children, not adults, not completed results. |
| 90 | EXCLUDE | INCLUDE | excluded_after_full_text | Impact of adequate empirical antibiotic therapy on the outcome of patients admitted to the intensive care unit with sepsis | Prospective cohort study, not an RCT. |

## All Studies

| Index | Predicted | Gold | Match | Gold Outcome | Title |
|-------|-----------|------|-------|--------------|-------|
| 1 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Initiation of inappropriate antimicrobial therapy results in a fivefold reduction of survival in human septic shock |
| 2 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Cotrimoxazole plus rifampicin in the treatment of staphylococcal osteoarticular infection |
| 3 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Prospective, randomized, controlled study comparing two dosing regimens of gentamicin/oral ciprofloxacin switch therapy for acute pyelonephritis |
| 4 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Association of length of stay and total hospital charges with antimicrobial regimen changes |
| 5 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Surviving Sepsis Campaign: international guidelines for management of severe sepsis and septic shock |
| 6 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Prescription of antibiotic agents in Swedish intensive care units is empiric and precise |
| 7 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Epidemiology and costs of severe sepsis in Madrid. A hospital discharge study |
| 8 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | A new paradigm for treating infections: "go hard and go home" initiation of antimicrobial therapy |
| 9 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Antibiotic strategies in severe nosocomial sepsis: why do we not de‐escalate more often? |
| 10 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Antibiotic usage in an intensive care unit in a Danish university hospital |
| 11 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Sepsis management ‐‐ antibiotic therapy |
| 12 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Use of procalcitonin to reduce patients' exposure to antibiotics in intensive care units (PRORATA trial): a multicentre randomised controlled trial |
| 13 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Adequacy of early empiric antibiotic treatment and survival in severe sepsis: experience from the MONARCS trial |
| 14 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Limited effect of patient and disease characteristics on compliance with hospital antimicrobial guidelines |
| 15 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Optimizing antimicrobial therapy in sepsis and septic shock |
| 16 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Current perspectives on antibiotic use in the treatment of surgical infections |
| 17 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Comparison of procalcitonin (PCT) and C‐reactive protein (CRP) plasma concentrations at different SOFA scores during the course of sepsis and MODS |
| 18 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Quantifying heterogeneity in a meta‐analysis |
| 19 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | The therapeutic challenge of gram‐negative sepsis: Prolonging the lifespan of a scarce resource |
| 20 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | The potential role of procalcitonin and interleukin 8 in the prediction of infected necrosis in acute pancreatitis |
| 21 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Two decades of imipenem therapy |
| 22 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Streamlining antimicrobial therapy for lower respiratory tract infections |
| 23 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Dosing of antibiotics in critically ill patients undergoing renal replacement therapy |
| 24 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Once‐daily versus twice‐daily administration of ceftazidime in the preterm infant |
| 25 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | An update on the synthesis and antibacterial effects of carbapenems |
| 26 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Bench‐to‐bedside review: Appropriate antibiotic therapy in severe sepsis and septic shock‐‐does the dose matter? |
| 27 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | The Procalcitonin And Survival Study (PASS) ‐ a randomised multi‐center investigator‐initiated trial to investigate whether daily measurements biomarker Procalcitonin and pro‐active diagnostic and therapeutic responses to abnormal Procalcitonin levels, can improve survival in intensive care unit patients. Calculated sample size (target population): 1000 patients |
| 28 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Acute kidney injury in septic shock: clinical outcomes and impact of duration of hypotension prior to initiation of antimicrobial therapy |
| 29 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Surviving sepsis campaign in Brazil |
| 30 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Characterization of CSP‐1, a novel extended‐spectrum beta‐lactamase produced by a clinical isolate of Capnocytophaga sputigena |
| 31 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Antibiotic combinations with redundant antimicrobial spectra: clinical epidemiology and pilot intervention of computer‐assisted surveillance |
| 32 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Procalcitonin to guide duration of antibiotic therapy in intensive care patients: a randomized prospective controlled trial |
| 33 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Urinary Tract Infections |
| 34 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Pseudomonas aeruginosa bloodstream infection: importance of appropriate initial antimicrobial treatment |
| 35 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | The CONSORT Statement: revised recommendations for improving the quality of reports of parallel‐group randomized trials 2001 |
| 36 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Delays in the administration of antibiotics are associated with mortality from adult acute bacterial meningitis |
| 37 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Sepsis and septic shock: selection of empiric antimicrobial therapy |
| 38 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Meta‐analysis of procalcitonin for sepsis detection |
| 39 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | APACHE II: a severity of disease classification system |
| 40 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Inflammation and the host response to injury, a large‐scale collaborative project: patient‐oriented research core‐‐standard operating procedures for clinical care VII‐‐Guidelines for antibiotic administration in severely injured patients |
| 41 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Short‐course empiric antibiotic therapy for patients with pulmonary infiltrates in the intensive care unit. A proposed solution for indiscriminate antibiotic prescription |
| 42 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | De‐escalation as part of a global strategy of empiric antibiotherapy management. A retrospective study in a medico‐surgical intensive care unit |
| 43 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Antibiotic strategies in the treatment of infection in critically ill patients |
| 44 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Antibiotic therapy in patients with septic shock |
| 45 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Successful control of Clostridium difficile infection in an elderly care unit through use of a restrictive antibiotic policy |
| 46 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Blood culture isolates in hemodialysis vascular catheter‐related bacteremia |
| 47 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Severe pseudomonal infections |
| 48 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Effect of an antibiotic algorithm on the adequacy of empiric antibiotic therapy given by a medical emergency team |
| 49 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Antibiotic therapy of infectious endocarditis (when, with what drug, how long?) |
| 50 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Severe soft tissue infections |
| 51 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Diagnosis and causal treatment of sepsis |
| 52 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Procalcitonin in liver transplant patients ‐ yet another stone turned |
| 53 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Inappropriate initial antimicrobial therapy and its effect on survival in a clinical trial of immunomodulating therapy for severe sepsis |
| 54 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Antibiotic use and misuse in the neonatal intensive care unit |
| 55 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Procalcitonin increase in early identification of critically ill patients at high risk of mortality |
| 56 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Piperacillin penetration into tissue of critically ill patients with sepsis‐‐bolus versus continuous administration? |
| 57 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | How to break the vicious circle of antibiotic resistances? |
| 58 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Epidemiology of severe sepsis in critically ill surgical patients in ten university hospitals in China |
| 59 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Update on antimicrobial chemotherapy |
| 60 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | De‐escalation of antimicrobial treatment for adults with sepsis, severe sepsis or septic shock |
| 61 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Appropriate and timely empirical antimicrobial treatment of icu infections‐‐a role for carbapenems |
| 62 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Use of procalcitonin (PCT) to guide discontinuation of antibiotic use in an unspecified sepsis is an antimicrobial stewardship program (ASP) |
| 63 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Duration of hypotension before initiation of effective antimicrobial therapy is the critical determinant of survival in human septic shock |
| 64 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Duration of empiric antibiotics for suspected early‐onset sepsis in extremely low birth weight infants |
| 65 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Multidisciplinary approach to the treatment of invasive fungal infections in adult patients. Prophylaxis, empirical, preemptive or targeted therapy, which is the best in the different hosts? |
| 66 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Guideline‐concordant therapy and reduced mortality and length of stay in adults with community‐acquired pneumonia: playing by the rules |
| 67 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Sepsis in European intensive care units: results of the SOAP study |
| 68 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Clinical impact of an infectious disease service on the management of bloodstream infection |
| 69 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | The prevalence of nosocomial infection in intensive care units in Europe. Results of the European Prevalence of Infection in Intensive Care (EPIC) Study. EPIC International Advisory Committee |
| 70 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Empiric de‐escalation strategy of antibiotic treatment |
| 71 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Diagnosis and management of urinary tract infection and pyelonephritis |
| 72 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | 2001 SCCM/ESICM/ACCP/ATS/SIS International Sepsis Definitions Conference |
| 73 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | De‐escalation therapy in ventilator‐associated pneumonia |
| 74 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Optimum treatment of severe sepsis and septic shock: Evidence in support of the recommendations |
| 75 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Investigation methods in clinical cardiology. IV. Clinical measurements incardiology: validity and errors of measurements |
| 76 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Antimicrobial use and the influence of inadequate empiric antimicrobial therapy on the outcomes of nosocomial bloodstream infections in a neonatal intensive care unit |
| 77 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Procalcitonin (PCT)‐guided algorithm reduces length of antibiotic treatment in surgical intensive care patients with severe sepsis: results of a prospective randomized study |
| 78 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Effects of selective decontamination of digestive tract on mortality and acquisition of resistant bacteria in intensive care: a randomised controlled trial |
| 79 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Prevalence of severe sepsis in intensive care units. A national multicentric study |
| 80 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Antibiotic dose adjustment in the treatment of MRSA infections in patients with acute renal failure undergoing continuous renal replacement therapies |
| 81 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Brazilian Sepsis Epidemiological Study (BASES study) |
| 82 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Antibiotic usage in intensive care units: a pharmaco‐epidemiological multicentre study |
| 83 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Indications for antibiotic use in ICU patients: a one‐year prospective surveillance |
| 84 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Narrow‐ versus broad‐spectrum parenteral anatimicrobials against common infections of childhood: a prospective and randomised comparison between penicillin and cefuroxime |
| 85 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Impact of increasing antimicrobial resistance on wound management |
| 86 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Effect of procalcitonin‐guided treatment on antibiotic use and outcome in lower respiratory tract infections: cluster‐randomised, single‐blinded intervention trial |
| 87 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | G‐CSF and IL‐8 for early diagnosis of sepsis in neonates and critically ill children ‐ safety and cost effectiveness of a new laboratory prediction model: study protocol of a randomized controlled trial [ISRCTN91123847] |
| 88 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Rapid increase in hospitalization and mortality rates for severe sepsis in the United States: a trend analysis from 1993 to 2003 |
| 89 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Utilization and diagnostic yield of blood cultures in a surgical intensive care unit |
| 90 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Impact of adequate empirical antibiotic therapy on the outcome of patients admitted to the intensive care unit with sepsis |
| 91 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Antibiotic de‐escalation |
| 92 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Adjustment of antibiotic treatment according to the results of blood cultures leads to decreased antibiotic use and costs |
| 93 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Nosocomial pneumonia: The importance of a de‐escalating strategy for antibiotic treatment of pneumonia in the ICU |
| 94 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Ventilator‐associated pneumonia: Breaking the vicious circle of antibiotic overuse |
| 95 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Principles of antibiotic therapy in severe infections: optimizing the therapeutic approach by use of laboratory and clinical data |
| 96 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | De‐escalation of antimicrobials in the treatment of bacteraemia due to antibiotic‐sensitive pathogens in immunocompetent patients |
