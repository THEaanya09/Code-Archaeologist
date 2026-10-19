# PROJECT SPEC | CodeArchaeologist

> **Code tells you what. History tells you why.**

**Live demo:** [code-archaeologist-tau.vercel.app](https://code-archaeologist-tau.vercel.app/)  
**Source repository:** [THEaanya09/Code-Archaeologist](https://github.com/THEaanya09/Code-Archaeologist)  
**Target repository:** `pallets/flask`

> **Project state:** The implementation is built and deployed. Three exploratory developer conversations (P01–P03) inform a preliminary research synthesis. T01’s reported first-time session records 1/4 tasks independently completed: the question task was completed, the historical-answer task could not be completed, and source verification plus the no-evidence case were not tested. A later 4/4 description was explicitly hypothetical, not a retest, and is excluded from observed results.

| At a glance | Current state |
|---|---|
| Technical implementation | **Built and deployed** |
| Exploratory developer conversations | **3 recorded (P01 dated 14 Oct 2026; P02/P03 dates not recorded)** |
| Preliminary Insight Ledger | **Synthesis of P01–P03; confidence labels included** |
| User research | **Three exploratory conversations; evidence is qualitative and preliminary** |
| First-time usability session | **1/4 tasks independently completed; 1 task not completed; 2 tasks not tested** |
| Reported benchmark and test results | README-reported; command execution and results are documented separately in `TECHNICAL_VALIDATION.md` |

---

# The 8 Questions

## 1. What is this?

CodeArchaeologist is a repository-intelligence web app that answers **"Why is this code the way it is?"** It retrieves historical context from pull requests, issues, discussions, and extracted decisions represented in a Neo4j knowledge graph.

The system is designed to return an evidence-backed explanation—or `no_evidence` when the available sources do not support an answer.

## 2. Who uses it?

**Intended user:** a developer making a meaningful change to code they did not write.

Typical situations include:

- onboarding to an unfamiliar repository
- preparing a refactor
- reviewing a change whose rationale is unclear
- finding a commit but not understanding why it happened
- deciding whether an old design constraint is still intentional

This is the current ICP hypothesis, informed by problem framing and early exploratory input.

## 3. What must it do?

| Capability | Expected behavior |
|---|---|
| **Question routing** | Classify a question as historical, repository, general, or hybrid. |
| **Evidence retrieval** | Retrieve relevant decisions and repository artifacts such as PRs, issues, files, and modules. |
| **Grounded answer** | Return a structured answer appropriate to the question type, with source references and relevant contributors/dates when available. |
| **Evidence inspection** | Let the user open the underlying sources and inspect supporting excerpts. |
| **Investigate mode** | Support a focused, single-question investigation. |
| **Chat mode** | Support multi-turn exploration. |
| **No-evidence behavior** | If useful evidence is unavailable, return `no_evidence` rather than invent a historical explanation. |

### Acceptance examples

| Scenario | Expected behavior | Verification status |
|---|---|---|
| Relevant, source-backed evidence is retrieved | Return an answer with inspectable citations | Implemented per README; not independently rerun here |
| No useful evidence is retrieved | Return `no_evidence` rather than inventing rationale | Reported implemented; live behavior not independently exercised here |
| A snippet does not match its source | Reject the snippet | Grounding behavior described in README; test result not independently verified here |
| A generated claim has no valid evidence reference | Remove or reject the unsupported claim | Grounding behavior described in README; tests not independently rerun here |
| A question is ambiguous across categories | Apply deterministic routing/tie-break behavior | Classifier described in README; benchmark results reported, not rerun here |

### Non-negotiables

- Never invent historical rationale.
- Never present an uncited claim as evidence-backed.
- Do not treat absence of evidence as proof that no reason existed.
- Prefer a clear refusal over unsupported confidence.

## 4. What does it NOT do?

The MVP does not:

- crawl the complete history of every repository
- support multiple repositories in the deployed instance
- persist chat sessions across process restarts
- edit, generate, or refactor code
- guarantee that the original rationale was recorded in repository history
- prove product-market fit through benchmark scores
- claim that the problem is validated across developers after one interview

**Current boundary:** `pallets/flask`, curated decisions, and sample PR/issue data.

## 5. What data does it use?

| Data | Purpose | Coverage note |
|---|---|---|
| GitHub pull requests | Historical changes and discussions | Focused on `pallets/flask` |
| GitHub issues/discussions | Rationale and surrounding context | Sampled/curated; not a complete history crawl |
| Extracted decisions | Searchable historical decision records | README reports 25 curated golden decisions |
| Contributors and dates | Context around a decision | Where available in source records |
| Repository files/modules | Repository-level context | Depends on the ingested dataset |
| Neo4j knowledge graph | Connects decisions to repository artifacts | Requires configured graph service |
| Benchmark questions | Routing and retrieval evaluation | README reports 45 questions |
| Chat history | Short-lived conversation context | In-memory only |

Exact inventory counts should be treated as repository/README-reported unless independently rechecked.

## 6. What constraints apply?

### Data

The MVP uses curated repository history rather than a full crawl. Some design rationale may never have been documented or may live outside GitHub.

### AI

LLM wording can vary across model versions. The model is not trusted to self-report confidence.

### Infrastructure

The documented stack depends on Neo4j Aura, GitHub data access, Gemini for Investigate synthesis, and Sarvam AI for Chat/general Q&A. The backend hosting location is not confirmed in this spec.

### Session behavior

Chat sessions and rate limiting are in memory and tied to the running process; they are not distributed state.

### Security

API credentials must remain server-side and must not be exposed in public frontend environment variables.

### Retrieval

Optional vector retrieval requires a configured embeddings endpoint.

## 7. What does "done" mean?

The technical flow is:

```text
question → classify → retrieve → verify → synthesize → cite → answer OR no_evidence
```

### Definition-of-done checklist

| Requirement | Current state | Evidence status |
|---|---|---|
| Frontend deployed | Landing page and navigation observed live | **Verified: landing page/navigation only** |
| Question routing | Historical/repository/general/hybrid paths described in project README | Implemented; not independently rerun here |
| Evidence retrieval | Graph/context retrieval described in README | Implemented; live behavior not independently exercised here |
| Citation and grounding rules | Snippet verification, claim citations, unsupported-claim removal described in README | Implemented; tests not independently rerun here |
| Zero-evidence refusal | `no_evidence` path described in README | Reported implemented; not independently exercised here |
| Automated test suite | README reports 28 passing tests | README-reported, not independently rerun |
| Classifier benchmark | 44/45 (97.8%) | README-reported, not independently rerun |
| Golden retrieval matches | 25/25 | README-reported, not independently rerun |
| Real developer research | Three exploratory developer conversations recorded (P01–P03); P02/P03 excerpts are partial | **Completed; preliminary only** |
| First-time usability observation | T01 completed the initial question task but could not complete the historical-answer task | Source verification and the no-evidence path were not exercised in this session |

**Implementation completion and product validation are separate milestones.**

## 8. Research questions

- Do developers repeatedly encounter difficulty recovering historical rationale?
- Is the problem common across seniority levels and codebases?
- Is a cited answer useful enough to change a developer's workflow?
- How often does repository history actually contain the rationale being sought?
- Can retrieval connect the right discussion to the right decision outside the curated benchmark?
- Does the approach transfer to repositories with sparse history?
- Which need-share, paid-price, and adoption assumptions would have to hold for the opportunity to be meaningful?

---

# Core User Flow

**Unfamiliar code → ask why → classify → retrieve linked history → verify evidence → grounded answer → inspect source → decide whether to change the code.**

Example: a developer encounters unfamiliar behavior and asks, **"Why was `request.json` deprecated?"** The system should classify the question, retrieve relevant evidence, verify it, produce a cited explanation, and make the original sources inspectable. If supporting evidence is missing, it should refuse rather than guess.

# Architecture

```text
Next.js frontend
       ↓
FastAPI API
       ↓
Deterministic query classifier
       ↓
Retrieval (Neo4j graph + repository context + optional vectors)
       ↓
Category-specific answer synthesis
       ↓
Grounding and verification
       ↓
Structured cited response OR no_evidence
```

Chat also uses a conversation service with in-memory sessions, caching, and rate limiting.

# Stack

| Layer | Technology | Why it is used |
|---|---|---|
| Frontend | Next.js 15, TypeScript | Interactive category-specific UI |
| Backend | FastAPI, Pydantic | Typed API and Python-based model/ingestion integration |
| Graph | Neo4j Aura | Decisions and repository artifacts are relationship-heavy |
| Ingestion | PyGithub / GitHub API | Imports repository artifacts |
| Investigate LLM | Gemini through an OpenAI-compatible endpoint, with failover | Historical answer synthesis |
| Chat LLM | Sarvam AI (`sarvam-2`) | Chat and general Q&A path |
| Hosting | Vercel frontend | Deployment of the frontend |

Backend hosting is not confirmed here.

# Evidence and Grounding

1. Retrieved snippets are checked against source text.
2. Claims are expected to reference an `evidence_id`.
3. Unsupported or uncited claims are removed by the grounding layer.
4. If retrieval produces no useful evidence, the LLM is bypassed and `no_evidence` is returned.
5. Confidence is computed outside the LLM from evidence-related signals and citation behavior.

# Evaluation and Verification

The project README reports:

| Evaluation | Reported result |
|---|---:|
| Historical questions | 25/25 |
| Repository questions | 10/10 |
| General questions | 5/5 |
| Hybrid questions | 4/5 |
| Overall classifier | **44/45 (97.8%)** |
| Golden retrieval URLs | **25/25** |
| Backend tests | **28 passing** |

These are **README-reported, not independently rerun for this spec**. Benchmark results evaluate system behavior; they do not establish user demand, usability, or product-market fit.

# Early User Research

**Three exploratory developer conversations are recorded.** P01 is dated 14 October 2026. Dates, job titles and employers for P02 and P03 were not supplied in the notes reviewed here, so these details are not inferred. P02's supplied excerpt is partial. The P03 excerpt covers workflow-improvement, trust and post-concept-feedback questions but does not include answers to questions 1–7 or a concrete past incident.

### Preliminary observations from P01

> “The commits mostly described what changed, not why.”
>
> “I'd rather see ‘couldn't find enough evidence’ than some made-up reasoning.”

The first quote refers to P01's experience searching history. The second came after the product concept was introduced, so it is concept feedback, not evidence of adoption.

- P01 described understanding how modules, files and request/data flow connect as harder than understanding individual functions.
- P01 described an API call passing through multiple layers; Git history offered clues but did not clearly explain the design rationale.
- P01 described tracing code, checking documentation and Git history, reading tests, reproducing behavior, and testing assumptions before changing code.

### Preliminary observations from P02

- P02 said tests help clarify expected behavior, while commit messages sometimes fail to explain why a design decision was made.
- P02 described having to move across commits, PRs and discussions to connect code with its rationale.
- P02 wanted more than a bare PR link: a concise summary, relevant discussion, and a link back to the actual code.
- P02 identified a key risk: an AI could treat a related commit as proof of the real reason, especially when old discussions are incomplete or outdated. P02 wanted evidence and inference distinguished and a refusal when evidence is insufficient.
- After the concept was introduced, P02 said the tool sounded useful. As prompted concept feedback, this is not proof of actual use or adoption.

### Preliminary observations from P03

> “I wouldn't want another tool that just summarizes everything without actually helping me find the source.”
>
> “I wouldn't want to add another tool to my workflow unless it genuinely saves me time.”

These are excerpts from the supplied later-stage interview responses; the product concept had already been introduced before the adoption-related comment.

- P03 described the current process as fragmented across code, Git history, PRs, and issues, and suggested starting the search from a code location such as a function.
- P03 preferred a combination of original PR/commit, discussion, and current relevant code. The participant said a PR discussion may explain trade-offs better than a commit alone, and emphasized checking whether old reasoning still applies to today's code.
- P03 wanted evidence and inference clearly distinguished, and wanted the tool to acknowledge when no clear rationale could be found.
- After the concept was introduced, P03 named unfamiliar codebases and legacy logic as possible use cases, but questioned how often a dedicated tool would be needed instead of GitHub search or the usual debugging workflow. This is prompted concept feedback, not proof of adoption.
- **Scope limitation:** the supplied P03 excerpt does not include answers to questions 1–7 or a concrete past incident. No specific time saved, frequency, or consequence is inferred.

These are **preliminary observations from three participants**, not evidence that the problem is widespread or that anyone will adopt the product. P02 and P03's supplied notes are partial, and concept feedback is distinguished from reported past behavior.

### First-Time Tester Feedback — T01 (separate from interviews)

T01 is a first-time tester separate from P01–P03. Their date, role, and experience were not supplied, and this feedback is not counted as a fourth developer interview. T01 clarified that the later message describing all four tasks as completed independently was hypothetical, not a new app test. Therefore, it is **not actual usability-test evidence** and must not be counted in the score.

| Task | Actual reported status | Evidence status |
|---|---|---|
| Ask a question in the app | **Completed independently** | T01 said AI Chat and Investigate were easy enough to find. |
| Find an answer explaining a historical design decision | **Could not complete** | T01 said they explored the interface but did not finish the interaction end to end. |
| Open original source links and verify support | **Not tested** | No observed source-opening or claim-verification result is available. |
| Ask a question with no historical evidence and understand the response | **Not tested** | T01 explicitly said they had not verified the app’s actual response. Their comments about desired no-evidence behavior are hypothetical preferences, not an observed outcome. |

**Actual score: 1/4 tasks completed independently.** The proposed criterion is ≥3/4, so it is **not met**. Since tasks 3–4 were not tested, the usability test is incomplete; this does not establish that those app paths fail. The hypothetical 4/4 report is excluded.

### Qualitative feedback

> “I also liked the overall interface—it feels clean and gives the project a proper developer-tool vibe.”
>
> “I'd genuinely be interested in using it on a real project to see how much time it saves.”
>
> “One small improvement I'd suggest is making the difference between AI Chat and Investigate a little more obvious for first-time users.”
>
> “My main suggestion would be to make the evidence and confidence level really clear so users can quickly tell what the history actually confirms versus what the AI is inferring.”

- **Positive impression:** T01 liked the design and developer-tool presentation; this is qualitative feedback, not a usability pass.
- **Perceived value:** T01 could imagine using it on unfamiliar or legacy code, but this does not prove adoption or time saved.
- **Observed usability issue:** T01 completed the question task but could not complete the historical-answer task. The supplied notes do not identify the precise blocker, so the cause is not inferred.
- **Session boundary:** source-link verification and the app's actual no-evidence response were not observed in T01's session.
- **UX suggestion:** make AI Chat versus Investigate easier to distinguish, potentially with a short example. This is one tester's suggestion, not a demonstrated pattern across users.
- **Trust suggestion:** make source evidence, inference, and confidence easy to distinguish. This is a desired product behavior, not proof of current behavior under the no-evidence test.
- **Time-saving is unproven:** no timing data or comparison with a manual workflow was provided.

**Design implication:** give first-time users a clearer distinction between AI Chat and Investigate, potentially through a short example. The tester also recommended making evidence, inference, and confidence visibly distinct. These are qualitative design inputs rather than verified outcomes from the untested source-verification and no-evidence tasks.

### Preliminary Insight Ledger

| Insight | Origin | Type | Confidence | Product implication |
|---|---|---|---|---|
| Connecting modules and request/data flow can be harder than reading individual functions. | P01 | Participant-reported experience | Low; one participant | Preserve repository/architecture context in the investigation experience. |
| Git history can identify what changed without clarifying why, and recovering rationale may require searching across separate artifacts. | P01, P02, P03 | Participant-reported experiences | **Preliminary cross-interview signal**; three accounts, partial notes for P02/P03 | Let users start from code and navigate a connected chain of commits, PRs, issues and discussion. |
| Tests help establish expected behavior but do not necessarily explain the historical rationale. | P02 | Participant-reported workflow | Low; one participant | Treat tests as context, not a substitute for historical source evidence. |
| A useful answer should connect historical discussion to relevant current code; a commit link alone may not explain the rationale. | P02, P03 | Reported workflow / trust requirement | Low; two participants; concept feedback included | Show the original discussion, linked code and whether the historical explanation still applies. |
| Trust depends on an inspectable source trail and a clear distinction between evidence and inference. | P01, P02, P03; T01 valued source links and evidence/confidence clarity, but did not actually test source verification or the no-evidence path | Reported trust requirements / concept feedback | Preliminary; three accounts plus one tester, partly prompted; T01’s hypothetical 4/4 report is not test evidence | Show exact sources, relevant excerpts and uncertainty; preserve `no_evidence`. |
| First-time users may benefit from a clearer explanation of AI Chat versus Investigate. | T01 usability suggestion | Qualitative usability feedback | Low; one tester | Product-design option: a brief example or use-case hint for each mode. |
| Users need to distinguish history-confirmed evidence from AI inference, with a clear confidence/evidence display. | T01 qualitative feedback | Qualitative trust / UX suggestion | Low; one tester; preference only, not evidence the current no-evidence path behaved this way | Consider labels for evidence, inference, and confidence; evaluate with additional first-time users rather than assuming a design solution. |
| A dedicated tool must beat existing search/debugging workflows on speed, relevance and setup effort. | P03, after concept introduction | Counter-hypothesis / adoption condition | Preliminary; one participant, concept-focused | Test time-to-answer and verification effort against current workflows before claiming demand. |

**Research synthesis:** Three exploratory developer conversations yield early examples of fragmented historical search and a desire for verifiable reasoning. T01's recorded usability result is 1/4 independently completed; the later 4/4 account was hypothetical and is not treated as a retest. The session suggests a clearer AI Chat/Investigate distinction and more visible evidence-versus-inference cues. The available evidence supports product-design hypotheses but does not establish widespread demand or product-market fit.

# Opportunity Sizing

The detailed source trail and calculation are in `RESEARCH_EVIDENCE.md`. GitHub's About page displays **225M+ developers**, used here only as a broad ecosystem ceiling—not as a qualified buyer count. The 2025 Stack Overflow Developer Survey reports an AI-output trust concern, which provides context for evidence-first design but does not establish demand for CodeArchaeologist.

Because the share of developers who regularly need historical design rationale is not established by the sources reviewed, the sizing is scenario-based:

| Scenario | Assumed recurring-need share | Scenario-defined potential users | Assumed paid conversion | Paid seats | Annualised gross revenue at $8/seat/month |
|---|---:|---:|---:|---:|---:|
| Conservative | 0.001% of 225M | 2,250 | 1% | 23 | $2,208 |
| Planning case | 0.005% of 225M | 11,250 | 1% | 113 | $10,848 |
| Stretch case | 0.01% of 225M | 22,500 | 1% | 225 | $21,600 |

The recurring-need percentages, $8 monthly price, and 1% conversion are **unvalidated assumptions**. These are sensitivity scenarios, not measured TAM/SAM/SOM or a revenue forecast. They make the underlying assumptions explicit without claiming that all GitHub developers are potential buyers.

# Technical Validation Record

The landing page was reachable during a page-level review, and its primary navigation was visible. This did not exercise a repository question or verify source-link and no-evidence behavior. The README reports 28 passing backend tests, 44/45 classifier accuracy, and 25/25 golden retrieval matches; those figures remain README-reported because the repository code was not available in the local working folder for execution. The test commands and scope of the inspection are listed in `TECHNICAL_VALIDATION.md`.

# Limitations

1. The knowledge base is curated and does not contain the complete Flask history.
2. The MVP is centered on one repository.
3. Relevant rationale may not exist in the available source history.
4. Model-generated wording may vary.
5. Sessions and rate limiting use in-memory state.
6. A 45-question benchmark cannot prove broad real-world performance.
7. User validation is preliminary: three exploratory conversations, including two partial excerpts, plus one first-time tester are not enough to establish PMF. T01 completed 1/4 tasks independently; the later 4/4 description was explicitly hypothetical, so the proposed usability threshold is not met.

# Validation Boundary

The current project record separates four kinds of evidence: implementation descriptions, README-reported technical evaluation, exploratory interview material, and a first-time tester's observed task results. The technical figures are not presented as independently rerun results. Interview excerpts are qualitative and partial for P02/P03. T01's recorded session supports an initial-interface observation, not a successful end-to-end usability score: 1/4 tasks were independently completed, the historical-answer task could not be completed, and source verification plus no-evidence behavior were not tested.

The evidence is useful for guiding product decisions—especially clearer mode selection, inspectable source links, and visible distinction between history-supported claims and inference—but does not establish broad product-market fit or measured time savings. These boundaries describe the strength of the current evidence; they do not imply that the implementation is unfinished.


## Supporting assessment artifacts

- `BUILD_LOG.md` — activity-by-activity process and evidence history.
- `RESEARCH_EVIDENCE.md` — public sources, evidence classification, and opportunity-sizing arithmetic.
- `TECHNICAL_VALIDATION.md` — documented commands and review boundaries.
