# Screening Inspection

- **Review:** Tricyclic drugs for depression in children and adolescents
- **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD002317.pub2/full
- **Screening criteria:** Randomised controlled trials comparing the efficacy of orally administered tricyclic drugs with placebo in depressed people aged 6 to 18 years.
- **Gold label policy:** `include_label_0_5`
- **Gold screening rule:** dataset labels 1.0 and 0.5 count as INCLUDE; 0.0 counts as EXCLUDE.
- **Matches:** 21 / 25
- **Mismatches:** 4
- **Missing decisions:** 0

## Mismatches

| Index | Predicted | Gold | Gold Outcome | Title | Agent Rationale |
|-------|-----------|------|--------------|-------|-----------------|
| 1 | EXCLUDE | INCLUDE | excluded_after_full_text | Pulse intravenous clomipramine for depressed adolescents: double‐blind, controlled trial | Study uses INTRAVENOUS (IV) clomipramine, not orally administered. Selection criteria require oral administration. |
| 15 | EXCLUDE | INCLUDE | included_in_review | The effect of concomitant disorders in childhood depression on predicting treatment response | This appears to be a secondary analysis of treatment response based on concomitant disorders, not a primary RCT. |
| 23 | EXCLUDE | INCLUDE | excluded_after_full_text | Depression in children: relationship between plasma imipramine levels and response | This is an observational study examining relationship between plasma levels and response, not a placebo-controlled RCT. |
| 25 | EXCLUDE | INCLUDE | included_in_review | Imipramine compliance in adolescents | This is a secondary analysis focused on compliance and side effects, not a primary efficacy RCT comparing tricyclics ... |

## All Studies

| Index | Predicted | Gold | Match | Gold Outcome | Title |
|-------|-----------|------|-------|--------------|-------|
| 1 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Pulse intravenous clomipramine for depressed adolescents: double‐blind, controlled trial |
| 2 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | A double‐blind, randomized, placebo‐controlled trial of fluoxetine in children and adolescents with depression |
| 3 | INCLUDE | INCLUDE | correct | included_in_review | Double‐blind placebo‐controlled study of nortriptyline in depressed adolescents using a "fixed plasma level" design |
| 4 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Childhood and adolescent depression: a review of the past 10 years. Part I |
| 5 | INCLUDE | INCLUDE | correct | included_in_review | Imipramine treatment of depressed children: a double‐blind pilot study |
| 6 | INCLUDE | INCLUDE | correct | included_in_review | Amitriptyline in children with major depressive disorder: a double‐blind crossover pilot study |
| 7 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Newer generation antidepressants for depressive disorders in children and adolescents |
| 8 | INCLUDE | INCLUDE | correct | included_in_review | Imipramine plus cognitive‐behavioural therapy in the treatment of school refusal |
| 9 | INCLUDE | INCLUDE | correct | included_in_review | Imipramine in prepubertal major depressive disorders |
| 10 | INCLUDE | INCLUDE | correct | included_in_review | Efficacy of paroxetine treatment in the treatment of adolescent depression: a randomized, controlled trial |
| 11 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Mechanism of action of antidepressant medications |
| 12 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | SSRI safety in overdose |
| 13 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Measuring inconsistency in meta‐analyses |
| 14 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Clinical, electrocardiographic, and laboratory findings in children with amitriptyline intoxication |
| 15 | EXCLUDE | INCLUDE | incorrect | included_in_review | The effect of concomitant disorders in childhood depression on predicting treatment response |
| 16 | INCLUDE | INCLUDE | correct | included_in_review | Adolescent depression: controlled desipramine treatment and atypical features |
| 17 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Psychopharmacology of child and adolescent major depression: present status and future directions |
| 18 | INCLUDE | INCLUDE | correct | included_in_review | Comparative studies of pharmacotherapy for school refusal |
| 19 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Selected tricyclic antidepressant ingestions involving children 6 years old or less |
| 20 | INCLUDE | INCLUDE | correct | included_in_review | A randomized, controlled trial of amitriptyline in the acute treatment of adolescent major depression |
| 21 | INCLUDE | INCLUDE | correct | excluded_after_full_text | School phobia: a therapeutic trial with clomipramine and short‐term outcome |
| 22 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Meta‐analysis of early phase II studies with paroxetine in hospitalised depressed patients |
| 23 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Depression in children: relationship between plasma imipramine levels and response |
| 24 | INCLUDE | INCLUDE | correct | included_in_review | Randomized, controlled trial of amitriptyline versus placebo for adolescents with "treatment‐resistant" major depression |
| 25 | EXCLUDE | INCLUDE | incorrect | included_in_review | Imipramine compliance in adolescents |
