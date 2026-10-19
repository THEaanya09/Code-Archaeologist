# PROJECT SPEC | CodeArchaeologist

> **Code tells you what. History tells you why.**

**Live demo:** [code-archaeologist-tau.vercel.app](https://code-archaeologist-tau.vercel.app/)  
**Source repository:** [THEaanya09/Code-Archaeologist](https://github.com/THEaanya09/Code-Archaeologist)  
**Target repository:** `pallets/flask`

> **Project state:** Implementation is built. One exploratory developer interview has been completed; broader user validation remains open.

| At a glance | Current state |
|---|---|
| Technical implementation | **Built and deployed** |
| Exploratory developer interviews | **1 completed (P01, 14 Oct 2026)** |
| Initial Insight Ledger | **3 preliminary entries from P01** |
| PMF / broader user validation | **Pending** |
| Stranger test | **Pending** |
| Reported benchmark and test results | README-reported; not independently re-run for this spec |

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

This ICP is reasoned, not yet validated across multiple users.

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
| Real developer research | One exploratory interview, P01 | **Completed; preliminary only** |
| Broader user validation | Additional interviews and a stranger test | **Pending** |

**Implementation completion and product validation are separate milestones.**

## 8. What remains unknown?

- Do developers repeatedly encounter difficulty recovering historical rationale?
- Is the problem common across seniority levels and codebases?
- Is a cited answer useful enough to change a developer's workflow?
- How often does repository history actually contain the rationale being sought?
- Can retrieval connect the right discussion to the right decision outside the curated benchmark?
- Does the approach transfer to repositories with sparse history?
- What is a defensible opportunity size?

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

**One exploratory developer interview was completed on 14 October 2026.** The participant is anonymized as P01. The shared transcript does not record the participant's exact job title or employer, so these are not inferred.

### Preliminary observations from P01

> “The commits mostly described what changed, not why.”
>
> “I'd rather see ‘couldn't find enough evidence’ than some made-up reasoning.”

The first quote refers to the participant's experience searching history. The second came after the product concept was introduced, so it is recorded as concept feedback, not evidence of adoption.

- P01 described understanding the overall structure, connections between modules, and request/data flow as harder than understanding individual functions.
- P01 described an example in which an API call passed through multiple layers; Git history offered clues but did not clearly explain the design rationale.
- P01 described tracing code, reading documentation and tests, examining Git history, and reproducing behavior as ways to reduce uncertainty.
- After the product concept was introduced, P01 emphasized source links, verifiable evidence, visible confidence, and a refusal when support is insufficient.

These are **one participant's reported experiences and preferences**, not evidence that the same problem is widespread or that P01 will adopt the tool. The concept was disclosed before the final feedback questions, so positive reactions are treated as preliminary concept feedback.

### Initial Insight Ledger

| Insight | Origin | Type | Confidence | Product implication |
|---|---|---|---|---|
| Connecting modules and request/data flow can be harder than reading individual functions. | P01 | Participant-reported experience | Low; one participant | Preserve repository/architecture context in the investigation experience. |
| Git history can identify what changed without clarifying why. | P01 | Participant-reported experience | Low; one participant | Link answers to the original commit, PR, issue, and supporting excerpt. |
| Trust requires evidence that can be checked; unsupported certainty is a risk. | P01, including concept feedback | Reported trust requirement | Preliminary | Show evidence and uncertainty clearly and keep `no_evidence` as a valid result. |

**Validation status:** 1 exploratory interview completed; additional interviews, broader PMF validation, opportunity sizing, and the stranger test remain pending.

**Next research step:** interview 2–4 additional developers using the same neutral script, then compare raw notes across participants before promoting any preliminary pattern to a recurring insight.

# Limitations

1. The knowledge base is curated and does not contain the complete Flask history.
2. The MVP is centered on one repository.
3. Relevant rationale may not exist in the available source history.
4. Model-generated wording may vary.
5. Sessions and rate limiting use in-memory state.
6. A 45-question benchmark cannot prove broad real-world performance.
7. User validation is preliminary: one exploratory interview is not enough to establish PMF.

# Remaining Validation Work

| Item | Status |
|---|---|
| Additional developer interviews | **Pending** |
| Compare insights across participants | **Pending** |
| Run the three proposed 48-hour tests | **Pending** |
| Conduct a stranger test | **Pending** |
| Independent test/benchmark rerun | **Pending** |
| Opportunity sizing with defensible sources | **Pending** |

These are validation tasks, not missing implementation features. The current documents do not treat interview setup, synthetic evaluation or reported benchmark results as proof of product-market fit.

# Open Questions

- Do additional developers describe the same historical-search problem from their own experience?
- Is the source trail sufficient for developers to trust the answer?
- How often is useful rationale present in repository history?
- How well does retrieval generalize outside the curated Flask benchmark?
- What would a stranger test reveal about usability?
- What is a defensible opportunity size?
