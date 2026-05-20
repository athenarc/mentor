# Screening Inspection

- **Review:** Adjuvant progestagens for endometrial cancer
- **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001040.pub2/full
- **Screening criteria:** Randomised controlled trials (RCTs) of progestagen therapy in women who have had surgery for endometrial cancer.
- **Gold label policy:** `include_label_0_5`
- **Gold screening rule:** dataset labels 1.0 and 0.5 count as INCLUDE; 0.0 counts as EXCLUDE.
- **Matches:** 8 / 10
- **Mismatches:** 2
- **Missing decisions:** 0

## Mismatches

| Index | Predicted | Gold | Gold Outcome | Title | Agent Rationale |
|-------|-----------|------|--------------|-------|-----------------|
| 9 | EXCLUDE | INCLUDE | included_in_review | Aduvant progesterone therapy for stage 1 endometrial cancer | Not an RCT of progestagen therapy in post‑surgical endometrial cancer (e.g., review or methodological paper). |
| 10 | EXCLUDE | INCLUDE | included_in_review | Adjuvant progestagen therapy improves survival in patients with endometrial cancer after hysterectomy. results of one‐institutional prospective clinical trial | Not an RCT of progestagen therapy in post‑surgical endometrial cancer (e.g., review or methodological paper). |

## All Studies

| Index | Predicted | Gold | Match | Gold Outcome | Title |
|-------|-----------|------|-------|--------------|-------|
| 1 | INCLUDE | INCLUDE | correct | included_in_review | Treatment of FIGO (1971) stage 1 endometrial carcinoma with intensive surgery, radiotherapy and hormonotherapy according to pathological prognostic groups. Long term results of a randomised multicentre trial |
| 2 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Progestin therapy of endometrial, breast and ovarian carcinoma. A review of clinical observations. |
| 3 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Measuring inconsistency in meta‐analyses |
| 4 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Statistical methods for examining heterogeneity and combining results from several studies in meta‐analysis |
| 5 | INCLUDE | INCLUDE | correct | included_in_review | A randomised trial of adjuvant progestagens in early endometrial cancer |
| 6 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Meta‐analysis in clinical trials |
| 7 | INCLUDE | INCLUDE | correct | included_in_review | A randomised trial of progestagens in the primary treatment of endometrial carcinoma |
| 8 | EXCLUDE | EXCLUDE | correct | excluded_at_screening | Extracting summary statistics to perform meta‐analyses of the published literature for survival endpoints |
| 9 | EXCLUDE | INCLUDE | incorrect | included_in_review | Aduvant progesterone therapy for stage 1 endometrial cancer |
| 10 | EXCLUDE | INCLUDE | incorrect | included_in_review | Adjuvant progestagen therapy improves survival in patients with endometrial cancer after hysterectomy. results of one‐institutional prospective clinical trial |
