"""PRISMA 2020 checklist template (items 1–27 with sub-items).

Item text follows Table 1 in Page et al., BMJ 2021;372:n71 (PRISMA 2020 statement).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

FillMode = Literal["deterministic", "llm", "reference", "manual"]


@dataclass(frozen=True)
class ChecklistItem:
    id: str
    section: str
    label: str
    description: str
    fill_mode: FillMode


def get_prisma_checklist_items() -> list[ChecklistItem]:
    """Return the PRISMA 2020 checklist items used for Bastirr reporting."""
    return [
        # TITLE
        ChecklistItem(
            "1", "TITLE",
            "Title",
            "Identify the report as a systematic review.",
            "deterministic",
        ),
        ChecklistItem(
            "2", "TITLE",
            "Abstract",
            "See the PRISMA 2020 for Abstracts checklist (table 2).",
            "reference",
        ),
        # INTRODUCTION
        ChecklistItem(
            "3", "INTRODUCTION",
            "Rationale",
            "Describe the rationale for the review in the context of existing knowledge.",
            "deterministic",
        ),
        ChecklistItem(
            "4", "INTRODUCTION",
            "Objectives",
            "Provide an explicit statement of the objective(s) or question(s) the review addresses.",
            "deterministic",
        ),
        # METHODS
        ChecklistItem(
            "5", "METHODS",
            "Eligibility criteria",
            "Specify the inclusion and exclusion criteria for the review and how studies were "
            "grouped for the syntheses.",
            "deterministic",
        ),
        ChecklistItem(
            "6", "METHODS",
            "Information sources",
            "Specify all databases, registers, websites, organisations, reference lists and "
            "other sources searched or consulted to identify studies. Specify the date when "
            "each source was last searched or consulted.",
            "deterministic",
        ),
        ChecklistItem(
            "7", "METHODS",
            "Search strategy",
            "Present the full search strategies for all databases, registers and websites, "
            "including any filters and limits used.",
            "deterministic",
        ),
        ChecklistItem(
            "8", "METHODS",
            "Selection process",
            "Specify the methods used to decide whether a study met the inclusion criteria of "
            "the review, including how many reviewers screened each record and each report "
            "retrieved, whether they worked independently, and if applicable, details of "
            "automation tools used in the process.",
            "llm",
        ),
        ChecklistItem(
            "9", "METHODS",
            "Data collection process",
            "Specify the methods used to collect data from reports, including how many reviewers "
            "collected data from each report, whether they worked independently, any processes "
            "for obtaining or confirming data from study investigators, and if applicable, "
            "details of automation tools used in the process.",
            "llm",
        ),
        ChecklistItem(
            "10a", "METHODS",
            "Data items",
            "List and define all outcomes for which data were sought. Specify whether all "
            "results that were compatible with each outcome domain in each study were sought "
            "(e.g. for all measures, time points, analyses), and if not, the methods used to "
            "decide which results to collect.",
            "llm",
        ),
        ChecklistItem(
            "10b", "METHODS",
            "Data items",
            "List and define all other variables for which data were sought (e.g. participant "
            "and intervention characteristics, funding sources). Describe any assumptions made "
            "about any missing or unclear information.",
            "llm",
        ),
        ChecklistItem(
            "11", "METHODS",
            "Study risk of bias assessment",
            "Specify the methods used to assess risk of bias in the included studies, including "
            "details of the tool(s) used, how many reviewers assessed each study and whether "
            "they worked independently, and if applicable, details of automation tools used in "
            "the process.",
            "llm",
        ),
        ChecklistItem(
            "12", "METHODS",
            "Effect measures",
            "Specify for each outcome the effect measure(s) (e.g. risk ratio, mean difference) "
            "used in the synthesis or presentation of results.",
            "llm",
        ),
        ChecklistItem(
            "13a", "METHODS",
            "Synthesis methods",
            "Describe the processes used to decide which studies were eligible for each "
            "synthesis (e.g. tabulating the study intervention characteristics and comparing "
            "against the planned groups for each synthesis (item #5)).",
            "llm",
        ),
        ChecklistItem(
            "13b", "METHODS",
            "Synthesis methods",
            "Describe any methods required to prepare the data for presentation or synthesis, "
            "such as handling of missing summary statistics, or data conversions.",
            "llm",
        ),
        ChecklistItem(
            "13c", "METHODS",
            "Synthesis methods",
            "Describe any methods used to tabulate or visually display results of individual "
            "studies and syntheses.",
            "llm",
        ),
        ChecklistItem(
            "13d", "METHODS",
            "Synthesis methods",
            "Describe any methods used to synthesise results and provide a rationale for the "
            "choice(s). If meta-analysis was performed, describe the model(s), method(s) to "
            "identify the presence and extent of statistical heterogeneity, and software "
            "package(s) used.",
            "llm",
        ),
        ChecklistItem(
            "13e", "METHODS",
            "Synthesis methods",
            "Describe any methods used to explore possible causes of heterogeneity among study "
            "results (e.g. subgroup analysis, meta-regression).",
            "llm",
        ),
        ChecklistItem(
            "13f", "METHODS",
            "Synthesis methods",
            "Describe any sensitivity analyses conducted to assess robustness of the synthesised "
            "results.",
            "llm",
        ),
        ChecklistItem(
            "14", "METHODS",
            "Reporting bias assessment",
            "Describe any methods used to assess risk of bias due to missing results in a "
            "synthesis (arising from reporting biases).",
            "llm",
        ),
        ChecklistItem(
            "15", "METHODS",
            "Certainty assessment",
            "Describe any methods used to assess certainty (or confidence) in the body of "
            "evidence for an outcome.",
            "llm",
        ),
        # RESULTS
        ChecklistItem(
            "16a", "RESULTS",
            "Study selection",
            "Describe the results of the search and selection process, from the number of "
            "records identified in the search to the number of studies included in the review, "
            "ideally using a flow diagram (see fig 1).",
            "reference",
        ),
        ChecklistItem(
            "16b", "RESULTS",
            "Study selection",
            "Cite studies that might appear to meet the inclusion criteria, but which were "
            "excluded, and explain why they were excluded.",
            "reference",
        ),
        ChecklistItem(
            "17", "RESULTS",
            "Study characteristics",
            "Cite each included study and present its characteristics.",
            "deterministic",
        ),
        ChecklistItem(
            "18", "RESULTS",
            "Risk of bias in studies",
            "Present assessments of risk of bias for each included study.",
            "deterministic",
        ),
        ChecklistItem(
            "19", "RESULTS",
            "Results of individual studies",
            "For all outcomes, present, for each study: (a) summary statistics for each group "
            "(where appropriate) and (b) an effect estimate and its precision (e.g. "
            "confidence/credible interval), ideally using structured tables or plots.",
            "llm",
        ),
        ChecklistItem(
            "20a", "RESULTS",
            "Results of syntheses",
            "For each synthesis, briefly summarise the characteristics and risk of bias among "
            "contributing studies.",
            "llm",
        ),
        ChecklistItem(
            "20b", "RESULTS",
            "Results of syntheses",
            "Present results of all statistical syntheses conducted. If meta-analysis was done, "
            "present for each the summary estimate and its precision (e.g. confidence/credible "
            "interval) and measures of statistical heterogeneity. If comparing groups, describe "
            "the direction of the effect.",
            "deterministic",
        ),
        ChecklistItem(
            "20c", "RESULTS",
            "Results of syntheses",
            "Present results of all investigations of possible causes of heterogeneity among "
            "study results.",
            "deterministic",
        ),
        ChecklistItem(
            "20d", "RESULTS",
            "Results of syntheses",
            "Present results of all sensitivity analyses conducted to assess the robustness of "
            "the synthesised results.",
            "deterministic",
        ),
        ChecklistItem(
            "21", "RESULTS",
            "Reporting biases",
            "Present assessments of risk of bias due to missing results (arising from reporting "
            "biases) for each synthesis assessed.",
            "manual",
        ),
        ChecklistItem(
            "22", "RESULTS",
            "Certainty of evidence",
            "Present assessments of certainty (or confidence) in the body of evidence for each "
            "outcome assessed.",
            "deterministic",
        ),
        # DISCUSSION
        ChecklistItem(
            "23a", "DISCUSSION",
            "Discussion",
            "Provide a general interpretation of the results in the context of other evidence.",
            "llm",
        ),
        ChecklistItem(
            "23b", "DISCUSSION",
            "Discussion",
            "Discuss any limitations of the evidence included in the review.",
            "llm",
        ),
        ChecklistItem(
            "23c", "DISCUSSION",
            "Discussion",
            "Discuss any limitations of the review processes used.",
            "llm",
        ),
        ChecklistItem(
            "23d", "DISCUSSION",
            "Discussion",
            "Discuss implications of the results for practice, policy, and future research.",
            "llm",
        ),
        # OTHER INFORMATION
        ChecklistItem(
            "24a", "OTHER INFORMATION",
            "Registration and protocol",
            "Provide registration information for the review, including register name and "
            "registration number, or state that the review was not registered.",
            "manual",
        ),
        ChecklistItem(
            "24b", "OTHER INFORMATION",
            "Registration and protocol",
            "Indicate where the review protocol can be accessed, or state that a protocol was "
            "not prepared.",
            "manual",
        ),
        ChecklistItem(
            "24c", "OTHER INFORMATION",
            "Registration and protocol",
            "Describe and explain any amendments to information provided at registration or in "
            "the protocol.",
            "manual",
        ),
        ChecklistItem(
            "25", "OTHER INFORMATION",
            "Support",
            "Describe sources of financial or non-financial support for the review, and the role "
            "of the funders or sponsors in the review.",
            "manual",
        ),
        ChecklistItem(
            "26", "OTHER INFORMATION",
            "Competing interests",
            "Declare any competing interests of review authors.",
            "manual",
        ),
        ChecklistItem(
            "27", "OTHER INFORMATION",
            "Availability of data, code, and other materials",
            "Report which of the following are publicly available and where they can be found: "
            "template data collection forms; data extracted from included studies; data used "
            "for all analyses; analytic code; any other materials used in the review.",
            "manual",
        ),
    ]
