# Research Evidence & Opportunity Sizing — CodeArchaeologist

**Prepared:** 19 October 2026  
**Purpose:** Preserve the external source trail and make the opportunity-size assumptions auditable.

> **Evidence rule:** Published facts, project-owner-reported results, participant feedback, and scenario assumptions are different kinds of evidence. This file keeps those categories separate. It is a curated research register created for this submission, not a verbatim export of an earlier AI research session.

## 1. Source register

| ID | Source | Claim captured | How it is used | Limit |
|---|---|---|---|---|
| S1 | GitHub, About page — https://github.com/about | GitHub's current About page displays **225M+ developers**, **4M+ organizations**, and **800M+ repositories**. | Broad platform-scale ceiling for the developer ecosystem. | This does **not** mean all listed developers need CodeArchaeologist, are active buyers, or are reachable by the current MVP. The page does not identify the share that regularly needs historical design rationale. |
| S2 | Stack Overflow, 2025 Developer Survey press release — https://stackoverflow.co/company/press/archive/stack-overflow-2025-developer-survey/ | The survey press release reports that **46% of developers said they do not trust the accuracy of AI-tool output**; it also says 84% use or plan to use AI tools. | Context for why inspectable evidence and clear uncertainty may matter in developer tooling. | This is a survey finding about AI trust, not evidence that respondents want this specific product, would adopt it, or would pay for it. |
| S3 | Stack Overflow, 2025 Developer Survey — Developers — https://survey.stackoverflow.co/2025/developers | The page reports 49,019 responses to the coding-status question; 76% of respondents to that question identified as professional developers and 15% as aspirational or adjacent. | A second contextual view of the developer population and survey methodology. | Survey respondents are not a full census of developers; percentages should not be multiplied by GitHub's population to infer a market without further evidence. |
| S4 | CodeArchaeologist source repository — https://github.com/THEaanya09/Code-Archaeologist | The repository README reports 44/45 classifier benchmark questions correct (97.8%), 25/25 golden retrieval URL matches, and 28 passing backend tests. | Technical evidence supplied by the project repository. | These numbers are **README-reported**; they were not independently rerun during this packaging pass. They are not user-validation or PMF metrics. |
| S5 | Deployed frontend — https://code-archaeologist-tau.vercel.app/ | The landing page loaded during the final review and exposed navigation for Repository, AI Chat, Investigate, and Decisions. | Deployment/landing-page observation. | This was a page-level inspection only; no live question, source-link workflow, or no-evidence response was exercised. |

## 2. Evidence, inference, hypothesis, assumption

- **Evidence:** GitHub's About page displays 225M+ developers; Stack Overflow's 2025 survey reports an AI-output trust concern; the CodeArchaeologist README reports its benchmark and test figures.
- **Inference:** A tool that exposes primary repository sources may address a trust-related friction better than an explanation with no inspectable evidence. The sources support this as a design rationale, not as proven demand.
- **Hypothesis:** Developers who are about to modify unfamiliar or legacy code will use an evidence-grounded history search if it is clearly faster or easier than their current workflow.
- **Assumptions for sizing only:** a small fraction of GitHub's developer ecosystem has a recurring need for historical rationale; a possible individual price is USD $8 per user per month; 1% of the scenario-defined segment converts to paid use. These are sensitivity inputs, not observed facts or validated pricing.

## 3. Opportunity sizing: scenario model, not a forecast

### Population boundary

The **broad ecosystem ceiling** is GitHub's displayed 225M+ developers (S1). It is not a claim that 225M people form CodeArchaeologist's serviceable market. The actual user is narrower: someone working in a GitHub-hosted codebase they did not write, at a moment when the rationale behind a historical decision matters, and who can connect the repository to the tool.

### Transparent scenarios

Because no external source located for this project quantifies the percentage of developers who have this specific recurring need, the eligible-user percentages below are deliberately labelled assumptions. The scenarios are intended to show the sensitivity of the opportunity to assumptions—not to claim a sourced SAM.

| Scenario | Assumed share of 225M+ developer baseline with recurring need | Scenario-defined potential users | Assumed paid conversion within that segment | Illustrative paid seats | Annualised gross revenue at $8/user/month |
|---|---:|---:|---:|---:|---:|
| Conservative | 0.001% | 2,250 | 1% | 23 (rounded) | **$2,208** |
| Planning case | 0.005% | 11,250 | 1% | 113 (rounded) | **$10,848** |
| Stretch case | 0.01% | 22,500 | 1% | 225 | **$21,600** |

**Calculation:** potential users = 225,000,000 × assumed need share. Paid seats = scenario-defined potential users × 1%, rounded to a whole seat. Annualised revenue = paid seats × USD $8 × 12. For the first two cases, the rounded seat counts (23 and 113) produce $2,208 and $10,848 respectively.

### How to read the model

- **TAM boundary:** 225M+ is the broad GitHub developer ecosystem indicator, not a credible count of qualified buyers.
- **SAM proxy:** 2,250–22,500 is an assumption-based range for people with a recurring need, not an externally measured SAM.
- **SOM scenario:** 23–225 paid seats is the result of applying an assumed 1% conversion to that assumed range; it is not an adoption forecast.
- **Revenue:** $2.2K–$21.6K annualised gross revenue is arithmetic under an unvalidated $8 monthly price. It excludes infrastructure, model/API costs, sales, taxes, churn, and free users.
- **Decision:** do not use these figures as a market claim in a pitch. They are a transparent scenario model showing that a defensible market estimate depends on first measuring how frequently the problem occurs, whether current substitutes are insufficient, and whether users will pay.

## 4. Research limitations and provenance

The project files available in the working folder included the current `BUILD_LOG.md` and `PROJECT_SPEC.md`, earlier versions of those documents, and several pasted notes. A dedicated verbatim raw AI-research-output export was not among the materials available for this packaging pass. This file therefore preserves a fresh, curated source register and its calculation assumptions; it does not claim to be that earlier raw-output archive.

The three exploratory developer conversations (P01–P03) and first-time tester record (T01) are summarized in `BUILD_LOG.md` and `PROJECT_SPEC.md`. P02/P03 notes are partial, and T01's later 4/4 description was explicitly hypothetical rather than a new test. The scenario model does not fill those evidence gaps or convert qualitative feedback into an adoption rate.
