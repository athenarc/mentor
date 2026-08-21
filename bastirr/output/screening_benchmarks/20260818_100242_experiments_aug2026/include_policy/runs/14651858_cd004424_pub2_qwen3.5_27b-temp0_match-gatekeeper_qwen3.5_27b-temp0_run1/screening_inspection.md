# Screening Inspection

- **Review:** Antiepileptic drugs for preventing seizures in people with brain tumors
- **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD004424.pub2/full
- **Screening criteria:** Controlled clinical trials with random allocation, blinded or unblinded, and placebo or observation in the control groups.
- **Gold label policy:** `include_label_0_5`
- **Gold screening rule:** dataset labels 1.0 and 0.5 count as INCLUDE; 0.0 counts as EXCLUDE.
- **Matches:** 22 / 33
- **Mismatches:** 11
- **Missing decisions:** 0

## Mismatches

| Index | Predicted | Gold | Gold Outcome | Title | Agent Rationale |
|-------|-----------|------|--------------|-------|-----------------|
| 4 | EXCLUDE | INCLUDE | excluded_after_full_text | Prospective study of postoperative seizure in intracranial meningioma | This is a prospective observational study evaluating risk of postoperative seizures, not a randomized controlled trial. |
| 6 | EXCLUDE | INCLUDE | excluded_after_full_text | The role of anticonvulsant medications in the management of patients with anaplastic gliomas | This is an observational study of 100 patients in a therapy protocol, not a randomized controlled trial. |
| 7 | EXCLUDE | INCLUDE | excluded_after_full_text | Postoperative prophylactic anticonvulsant therapy in cerebral gliomas | This is explicitly stated as a retrospective study, not a randomized controlled trial. |
| 10 | EXCLUDE | INCLUDE | excluded_after_full_text | Prevention of early postoperative seizures in patients with primary brain tumors: preliminary experience with oxcarbazepine | This is a single-arm observational study of 150 patients receiving oxcarbazepine, not a randomized controlled trial w... |
| 16 | EXCLUDE | INCLUDE | excluded_after_full_text | The role of radiation therapy following resection of single brain metastasis from melanoma | This is an observational study about radiation therapy, not a randomized controlled trial of antiepileptic drugs. |
| 22 | EXCLUDE | INCLUDE | excluded_after_full_text | Peri‐operative prophylaxis with phenytoin: dosage and therapeutic plasma levels. Acta neurochirurgica | This is a randomized study comparing two different dosages of phenytoin (10 mg/kg vs 15 mg/kg), but both groups recei... |
| 25 | EXCLUDE | INCLUDE | excluded_after_full_text | Should prophylactic anticonvulsants be administered to patients with newly‐diagnosed cerebral metastases? A retrospective analysis | This is a retrospective analysis of 195 patients, not a randomized controlled trial. |
| 26 | EXCLUDE | INCLUDE | included_in_review | Influence of surgery and antiepileptic drugs on seizures symptomatic of cerebral tumours | This is an observational study of 128 patients, not a randomized controlled trial. |
| 29 | EXCLUDE | INCLUDE | excluded_after_full_text | The course of seizure disorders in patients with malignant gliomas | This is a retrospective review of 65 patients, not a randomized controlled trial. |
| 30 | EXCLUDE | INCLUDE | excluded_after_full_text | Comparative double blind clinical trial of phenytoin and sodium valproate as anticonvulsant prophylaxis after craniotomy: efficacy, tolerability, and cognitive effects | This is a randomized, double-blind trial comparing two active drugs (phenytoin vs valproate), but there is no placebo... |
| 31 | EXCLUDE | INCLUDE | excluded_after_full_text | Brain metastasis from melanoma | This is an observational study of 81 patients with brain metastasis from melanoma, not a randomized controlled trial. |

## All Studies

| Index | Predicted | Gold | Match | Gold Outcome | Title |
|-------|-----------|------|-------|--------------|-------|
| 1 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | The importance of drug interactions in epilepsy therapy |
| 2 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Interaction of dexamethasone with phenytoin |
| 3 | INCLUDE | INCLUDE | correct | excluded_after_full_text | Add‐on phenytoin fails to prevent early seizures after surgery for supratentorial brain tumors: A randomized controlled study |
| 4 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Prospective study of postoperative seizure in intracranial meningioma |
| 5 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Practice parameter: anticonvulsant prophylaxis in patients with newly diagnosed brain tumors. Report of the Quality Standards Subcommittee of the American Academy of Neurology |
| 6 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | The role of anticonvulsant medications in the management of patients with anaplastic gliomas |
| 7 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Postoperative prophylactic anticonvulsant therapy in cerebral gliomas |
| 8 | INCLUDE | INCLUDE | correct | included_in_review | Phenytoin and postoperative epilepsy. A double‐blind study |
| 9 | INCLUDE | INCLUDE | correct | excluded_after_full_text | Diazepam prophylaxis of contrast media‐induced seizures during computed tomography of patients with brain metastases |
| 10 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Prevention of early postoperative seizures in patients with primary brain tumors: preliminary experience with oxcarbazepine |
| 11 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Dexamethasone/phenytoin interactions: neurooncological concerns |
| 12 | INCLUDE | INCLUDE | correct | excluded_after_full_text | Postoperative epilepsy: a double‐blind trial of phenytoin after craniotomy |
| 13 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Optimizing therapy of seizures in patients with brain tumors |
| 14 | INCLUDE | INCLUDE | correct | excluded_after_full_text | Prophylactic diazepam in prevention of contrast media‐associated seizures in glioma patients undergoing cerebral computed tomography |
| 15 | INCLUDE | INCLUDE | correct | included_in_review | Prophylactic anticonvulsants for prevention of immediate and early postcraniotomy seizures |
| 16 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | The role of radiation therapy following resection of single brain metastasis from melanoma |
| 17 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Can surveying practitioners about their practices help identify priority clinical practice guideline topics? |
| 18 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Results of a survey of neurosurgical practice patterns regarding the prophylactic use of anti‐epilepsy drugs in patients with brain tumors |
| 19 | INCLUDE | INCLUDE | correct | included_in_review | Prophylactic anticonvulsants in patients with brain tumour |
| 20 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Seizure prophylaxis in patients with brain tumors: a meta‐analysis |
| 21 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Seizure prophylaxis for brain tumour patients. Brief review and guide for family physicians |
| 22 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Peri‐operative prophylaxis with phenytoin: dosage and therapeutic plasma levels. Acta neurochirurgica |
| 23 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Effectiveness of antiepileptic prophylaxis used with supratentorial craniotomies: a meta‐analysis |
| 24 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Epileptic seizures during follow‐up of patients treated for primary brain tumors |
| 25 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Should prophylactic anticonvulsants be administered to patients with newly‐diagnosed cerebral metastases? A retrospective analysis |
| 26 | EXCLUDE | INCLUDE | incorrect | included_in_review | Influence of surgery and antiepileptic drugs on seizures symptomatic of cerebral tumours |
| 27 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Anticonvulsant prophylaxis in neurological surgery |
| 28 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Seizures during the immediate post‐operative period |
| 29 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | The course of seizure disorders in patients with malignant gliomas |
| 30 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Comparative double blind clinical trial of phenytoin and sodium valproate as anticonvulsant prophylaxis after craniotomy: efficacy, tolerability, and cognitive effects |
| 31 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Brain metastasis from melanoma |
| 32 | INCLUDE | INCLUDE | correct | excluded_after_full_text | Do prophylactic anticonvulsant drugs alter the pattern of seizures after craniotomy? |
| 33 | INCLUDE | INCLUDE | correct | included_in_review | A randomized, blinded, placebo‐controlled trial of divalproex sodium prophylaxis in adults with newly diagnosed brain tumors |
