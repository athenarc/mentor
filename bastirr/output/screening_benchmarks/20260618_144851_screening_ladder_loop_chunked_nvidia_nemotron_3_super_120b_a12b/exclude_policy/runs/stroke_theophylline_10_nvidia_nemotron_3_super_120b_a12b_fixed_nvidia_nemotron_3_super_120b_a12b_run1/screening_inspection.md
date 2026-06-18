# Screening Inspection

- **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke
- **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full
- **Screening criteria:** Randomised trials of theophylline or an analogue compound compared with placebo or control in people with confirmed or presumed acute ischaemic stroke. Trials were included if treatment was started within one week of stroke onset.
- **Gold label policy:** `exclude_label_0_5`
- **Gold screening rule:** dataset label 1.0 counts as INCLUDE; 0.5 and 0.0 count as EXCLUDE.
- **Matches:** 7 / 10
- **Mismatches:** 3
- **Missing decisions:** 0

## Mismatches

| Index | Predicted | Gold | Gold Outcome | Title | Agent Rationale |
|-------|-----------|------|--------------|-------|-----------------|
| 3 | INCLUDE | EXCLUDE | excluded_after_full_text | Pilot dose‐escalation study of caffeine plus ethanol (caffeinol) in acute ischemic stroke | Meets all criteria: randomised controlled trial of theophylline/analogue in acute ischaemic stroke patients with trea... |
| 5 | INCLUDE | EXCLUDE | excluded_after_full_text | Caffeine reduces cerebral blood flow in patients recovering from an acute ischaemic stroke | Meets criteria for randomised controlled trial of theophylline/analogue in acute ischaemic stroke patients, but uncle... |
| 6 | INCLUDE | EXCLUDE | excluded_after_full_text | Effects of caffeine on cerebral blood flow in stroke patients | Meets criteria for randomised controlled trial of theophylline/analogue in acute ischaemic stroke patients, but uncle... |

## All Studies

| Index | Predicted | Gold | Match | Gold Outcome | Title |
|-------|-----------|------|-------|--------------|-------|
| 1 | INCLUDE | INCLUDE | correct | included_in_review | Lack of effect of theophylline on the outcome of acute cerebral infarction |
| 2 | INCLUDE | INCLUDE | correct | included_in_review | Controlled trial of intravenous aminophylline in acute cerebral infarction |
| 3 | INCLUDE | EXCLUDE | incorrect | excluded_after_full_text | Pilot dose‐escalation study of caffeine plus ethanol (caffeinol) in acute ischemic stroke |
| 4 | EXCLUDE | EXCLUDE | correct | excluded_after_full_text | Effects of vincamin on cerebral metabolism |
| 5 | INCLUDE | EXCLUDE | incorrect | excluded_after_full_text | Caffeine reduces cerebral blood flow in patients recovering from an acute ischaemic stroke |
| 6 | INCLUDE | EXCLUDE | incorrect | excluded_after_full_text | Effects of caffeine on cerebral blood flow in stroke patients |
| 7 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | The effect of intracarotid aminophylline infusion on the cerebral circulation |
| 8 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Responses to surface arteries and blood flow of ischemic and non ischemic cerebral cortex to aminophylline, ergotamine tartrate, and acetazolamide |
| 9 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | A comparative study between the cardiovascular effect of cetiedil, a new vasodilator, and papaverine and aminophylline |
| 10 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | The mechanism of action of aminophylline upon cerebral vascular disorders |
