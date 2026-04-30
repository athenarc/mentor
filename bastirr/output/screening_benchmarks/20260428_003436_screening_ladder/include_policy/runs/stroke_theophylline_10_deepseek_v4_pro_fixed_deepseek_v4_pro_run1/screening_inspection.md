# Screening Inspection

- **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke
- **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full
- **Screening criteria:** Randomised trials of theophylline or an analogue compound compared with placebo or control in people with confirmed or presumed acute ischaemic stroke. Trials were included if treatment was started within one week of stroke onset.
- **Gold label policy:** `include_label_0_5`
- **Gold screening rule:** dataset labels 1.0 and 0.5 count as INCLUDE; 0.0 counts as EXCLUDE.
- **Matches:** 8 / 10
- **Mismatches:** 2
- **Missing decisions:** 0

## Mismatches

| Index | Predicted | Gold | Gold Outcome | Title | Agent Rationale |
|-------|-----------|------|--------------|-------|-----------------|
| 3 | EXCLUDE | INCLUDE | excluded_after_full_text | Pilot dose‐escalation study of caffeine plus ethanol (caffeinol) in acute ischemic stroke | Open-label, single-arm dose-escalation study without randomisation or a concurrent control group. Does not meet the m... |
| 4 | EXCLUDE | INCLUDE | excluded_after_full_text | Effects of vincamin on cerebral metabolism | Studies the drug vincamin, not a theophylline analogue. No mention of participants having acute ischaemic stroke. Ami... |

## All Studies

| Index | Predicted | Gold | Match | Gold Outcome | Title |
|-------|-----------|------|-------|--------------|-------|
| 1 | INCLUDE | INCLUDE | correct | included_in_review | Lack of effect of theophylline on the outcome of acute cerebral infarction |
| 2 | INCLUDE | INCLUDE | correct | included_in_review | Controlled trial of intravenous aminophylline in acute cerebral infarction |
| 3 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Pilot dose‐escalation study of caffeine plus ethanol (caffeinol) in acute ischemic stroke |
| 4 | EXCLUDE | INCLUDE | incorrect | excluded_after_full_text | Effects of vincamin on cerebral metabolism |
| 5 | INCLUDE | INCLUDE | correct | excluded_after_full_text | Caffeine reduces cerebral blood flow in patients recovering from an acute ischaemic stroke |
| 6 | INCLUDE | INCLUDE | correct | excluded_after_full_text | Effects of caffeine on cerebral blood flow in stroke patients |
| 7 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | The effect of intracarotid aminophylline infusion on the cerebral circulation |
| 8 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Responses to surface arteries and blood flow of ischemic and non ischemic cerebral cortex to aminophylline, ergotamine tartrate, and acetazolamide |
| 9 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | A comparative study between the cardiovascular effect of cetiedil, a new vasodilator, and papaverine and aminophylline |
| 10 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | The mechanism of action of aminophylline upon cerebral vascular disorders |
