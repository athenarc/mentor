# Screening Inspection

- **Review:** Adjuvant progestagens for endometrial cancer
- **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001040.pub2/full
- **Screening criteria:** Randomised controlled trials (RCTs) of progestagen therapy in women who have had surgery for endometrial cancer.
- **Gold label policy:** `exclude_label_0_5`
- **Gold screening rule:** dataset label 1.0 counts as INCLUDE; 0.5 and 0.0 count as EXCLUDE.
- **Matches:** 5 / 10
- **Mismatches:** 5
- **Missing decisions:** 0

## Mismatches

| Index | Predicted | Gold | Gold Outcome | Title | Agent Rationale |
|-------|-----------|------|--------------|-------|-----------------|
| 2 | INCLUDE | EXCLUDE | excluded_at_screening | Progestin therapy of endometrial, breast and ovarian carcinoma. A review of clinical observations. | RCT: No Progestagen therapy: Yes Post-surgery endometrial cancer population: No Uncertainty noted; included conservat... |
| 3 | INCLUDE | EXCLUDE | excluded_at_screening | Measuring inconsistency in meta‐analyses | RCT: No Progestagen therapy: No Post-surgery endometrial cancer population: No Uncertainty noted; included conservati... |
| 4 | INCLUDE | EXCLUDE | excluded_at_screening | Statistical methods for examining heterogeneity and combining results from several studies in meta‐analysis | RCT: No Progestagen therapy: No Post-surgery endometrial cancer population: No Uncertainty noted; included conservati... |
| 6 | INCLUDE | EXCLUDE | excluded_at_screening | Meta‐analysis in clinical trials | RCT: No Progestagen therapy: No Post-surgery endometrial cancer population: No Uncertainty noted; included conservati... |
| 8 | INCLUDE | EXCLUDE | excluded_at_screening | Extracting summary statistics to perform meta‐analyses of the published literature for survival endpoints | RCT: No Progestagen therapy: No Post-surgery endometrial cancer population: No Uncertainty noted; included conservati... |

## All Studies

| Index | Predicted | Gold | Match | Gold Outcome | Title |
|-------|-----------|------|-------|--------------|-------|
| 1 | INCLUDE | INCLUDE | correct | included_in_review | Treatment of FIGO (1971) stage 1 endometrial carcinoma with intensive surgery, radiotherapy and hormonotherapy according to pathological prognostic groups. Long term results of a randomised multicentre trial |
| 2 | INCLUDE | EXCLUDE | incorrect | excluded_at_screening | Progestin therapy of endometrial, breast and ovarian carcinoma. A review of clinical observations. |
| 3 | INCLUDE | EXCLUDE | incorrect | excluded_at_screening | Measuring inconsistency in meta‐analyses |
| 4 | INCLUDE | EXCLUDE | incorrect | excluded_at_screening | Statistical methods for examining heterogeneity and combining results from several studies in meta‐analysis |
| 5 | INCLUDE | INCLUDE | correct | included_in_review | A randomised trial of adjuvant progestagens in early endometrial cancer |
| 6 | INCLUDE | EXCLUDE | incorrect | excluded_at_screening | Meta‐analysis in clinical trials |
| 7 | INCLUDE | INCLUDE | correct | included_in_review | A randomised trial of progestagens in the primary treatment of endometrial carcinoma |
| 8 | INCLUDE | EXCLUDE | incorrect | excluded_at_screening | Extracting summary statistics to perform meta‐analyses of the published literature for survival endpoints |
| 9 | INCLUDE | INCLUDE | correct | included_in_review | Aduvant progesterone therapy for stage 1 endometrial cancer |
| 10 | INCLUDE | INCLUDE | correct | included_in_review | Adjuvant progestagen therapy improves survival in patients with endometrial cancer after hysterectomy. results of one‐institutional prospective clinical trial |
