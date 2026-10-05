# PROJECT SPEC: CodeArchaeologist

> **Code tells you what. History tells you why.**

**Live:** https://code-archaeologist-tau.vercel.app/  
**Target repository:** `pallets/flask`

---

# The 8 Questions

## 1. What is this?

CodeArchaeologist is a repository-intelligence web app that answers:

> **"Why is this code the way it is?"**

It reconstructs historical reasoning from pull requests, issues, discussions and extracted decisions.

Repository history is represented in a Neo4j knowledge graph. The system retrieves evidence, verifies it, and returns a cited answer.

When useful evidence cannot be found, it returns **`no_evidence` rather than inventing historical rationale**.

---

## 2. Who uses it?

The intended user is a developer making a meaningful change to code they did not write.

Typical situations include:

- onboarding to an unfamiliar repository
- preparing a refactor
- reviewing a change whose historical rationale is unclear
- finding a commit but not understanding why it happened
- deciding whether an old constraint is still intentional

This is a **reasoned ICP, not yet validated with real users**.

---

## 3. What must it do?

### Input

Accept a natural-language repository question.

### Routing

Classify it as:

- **Historical**
- **Repository**
- **General**
- **Hybrid**

### Retrieval

Retrieve relevant context including:

- decisions
- pull requests
- issues
- modules
- files
- contributors
- dates

### Answering

Return a structured response with:

- explanation
- supporting evidence
- source links
- relevant people
- dates
- graph/context path where available

### Conversation

Support:

- **Investigate** — focused single-question investigation
- **Chat** — multi-turn exploration

### Failure behavior

Given a question with no useful supporting evidence:

```text
no_evidence
```

must be returned instead of an unsupported historical explanation.

---

## 4. What does it NOT do?

The MVP deliberately does **not**:

- crawl the complete history of every repository
- support multiple repositories in the deployed instance
- preserve chat sessions across restarts
- edit, generate or refactor code
- guarantee historical rationale exists for every question
- treat benchmark performance as product-market-fit evidence
- claim real-user validation

### Current MVP boundary

> **`pallets/flask` + curated decisions + sample PR/issue data**

---

## 5. What data does it use?

| Data | Purpose |
|---|---|
| GitHub pull requests | Historical changes and discussions |
| GitHub issues / discussions | Rationale and context |
| Extracted decisions | Searchable historical decisions |
| Contributors / dates | Decision context |
| Repository modules / files | Repository-level context |
| Neo4j graph | Connects decisions and repository relationships |
| Benchmark questions | Routing/retrieval evaluation |
| Chat history | Short-lived conversational context |

The project README reports **25 curated golden decisions** and a **45-question benchmark**.

---

## 6. What constraints apply?

### Data

The MVP uses curated repository history rather than a complete crawl.

### AI

LLM wording can vary with model versions.

The LLM does not self-report confidence.

### Infrastructure

The system relies on:

- Neo4j Aura
- GitHub data access
- Gemini for Investigate synthesis
- Sarvam AI for Chat/general Q&A

### Sessions

Chat state and rate limiting are in memory and tied to the running process.

### Security

API keys must remain server-side.

### Retrieval

Optional vector retrieval requires an embeddings endpoint.

---

# 7. What does "done" mean?

A technically complete system must satisfy:

```text
question
   ↓
classify
   ↓
retrieve
   ↓
verify
   ↓
synthesize
   ↓
cite
   ↓
answer OR no_evidence
```

## Definition-of-done checklist

| Requirement | State |
|---|---|
| Application deployed | ✅ |
| Repository / AI Chat / Investigate / Decisions navigation | ✅ |
| Deterministic question routing | ✅ |
| Historical / repository / general / hybrid paths | ✅ |
| Evidence retrieval | ✅ |
| Evidence citations | ✅ |
| Deterministic confidence | ✅ |
| Zero-evidence refusal | ✅ |
| Investigate mode | ✅ |
| Chat mode | ✅ |
| Automated test infrastructure | ✅ |
| Benchmark | ✅ |
| Real developer interviews | **Pending** |
| Stranger test | **Pending** |

The README reports:

- **44/45 (97.8%)** classifier performance
- **25/25** golden retrieval matches
- **28 passing backend tests**

These are **README-reported results, not independently re-run**.

---

# 8. What remains unknown?

### User behavior

Do developers actually look through repository history before changing unfamiliar code?

### Trust

Is a cited answer enough to influence what a developer does next?

### Evidence availability

How often does repository history contain enough rationale to answer real developer questions?

### Retrieval quality

Can the system connect the correct discussion to the correct design decision outside the curated benchmark?

### Transferability

Does the approach work on repositories with sparse or inconsistent history?

### Product value

Does this workflow save enough time or reduce enough uncertainty to become part of a developer's normal workflow?

### Market

What is a defensible opportunity size?

### Validation

No real interviews or stranger test have been completed yet.

---

# Core User Flow

> **Unfamiliar code → ask why → classify → retrieve linked history → verify evidence → grounded answer → inspect source → decide whether to change the code.**

### Example

A developer encounters unfamiliar behavior and asks:

> **"Why was `request.json` deprecated?"**

The system should:

1. identify the question type
2. retrieve relevant evidence
3. verify the evidence
4. synthesize the explanation
5. show the source trail
6. let the developer inspect it before acting

---

# Practical User Scenarios

These scenarios are **hypotheses, not observed user behavior**:

- onboarding to a mature repository
- preparing a refactor of code someone else wrote
- reviewing an old design decision
- tracing a surprising behavior to the original change
- deciding whether a compatibility constraint can safely be removed

---

# Simulated User Research

> **Not real interviews. Not validation.**

Three AI-generated conversations were used to rehearse interview questions and shape hypotheses.

A representative simulated conversation explored a common situation:

> **Builder:** "If you find code that looks strange but works, how do you usually decide whether it's safe to change?"

> **Simulated developer:** "I'd look at the code first, then probably the commit or PR that introduced it. The annoying part is finding the right discussion."

> **Builder:** "What would you want from a tool answering 'why was this designed this way?'"

> **Simulated developer:** "I'd want the original PR or issue linked. If the tool just gives me an explanation without the source, I wouldn't fully trust it."

> **Builder:** "What would worry you?"

> **Simulated developer:** "Incomplete history. It could find something related and make it sound like that's definitely the reason."

These lines are **simulation only** and should not be interpreted as participant quotes.

They identify hypotheses worth testing with actual developers:
- source visibility may matter for trust
- historical search may be harder than code reading
- incomplete history may be a significant failure mode
- the tool may be most useful immediately before a code change

---

# Architecture

```text
                    ┌─────────────────────┐
                    │     Next.js UI      │
                    │ Investigate / Chat  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       FastAPI       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Deterministic Query │
                    │     Classifier      │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
      ┌─────────────────┐           ┌─────────────────┐
      │  Neo4j Retrieval│           │ Optional Vector │
      │ + repo context  │           │ Retrieval       │
      └────────┬────────┘           └────────┬────────┘
               └──────────────┬─────────────┘
                              ▼
                    ┌─────────────────────┐
                    │ Category-specific   │
                    │ answer synthesis    │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Grounding / Verify  │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Structured answer   │
                    │ or no_evidence      │
                    └─────────────────────┘
```

Chat additionally uses session handling, caching and rate limiting.

---

# Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | Next.js 15 + TypeScript | Interactive category-specific interface |
| Backend | FastAPI + Pydantic | Typed Python API and model integration |
| Graph | Neo4j Aura | Decisions and repository artifacts are relationship-heavy |
| Ingestion | PyGithub / GitHub API | Source repository data |
| Investigate LLM | Gemini via OpenAI-compatible interface | Historical answer synthesis with failover |
| Chat LLM | Sarvam AI (`sarvam-2`) | Chat and general Q&A |
| Hosting | Vercel frontend | Straightforward deployment |

---

# Evidence & Grounding

The core rule is:

> **A plausible answer is not enough.**

### Evidence verification

Retrieved snippets are checked against the underlying source text.

### Claim-level citations

Generated claims must reference an `evidence_id`.

### Unsupported-claim removal

Claims without valid evidence are removed.

### Zero-evidence guard

When retrieval produces no useful evidence, the LLM is bypassed and:

```text
no_evidence
```

is returned.

### Confidence

Confidence is computed outside the LLM from evidence-related signals and citation behavior.

---

# Non-Negotiables

- **Never invent historical rationale.**
- **Never present an uncited claim as evidence-backed.**
- **Never treat absence of evidence as evidence of absence.**
- **Prefer a clear refusal over unsupported confidence.**

---

# Verification & Evaluation

The project exposes:

- `pytest`
- `app.eval`
- `app.smoke`

### Reported system evaluation

| Evaluation | Result |
|---|---|
| Historical questions | 25/25 |
| Repository questions | 10/10 |
| General questions | 5/5 |
| Hybrid questions | 4/5 |
| Overall classifier | **44/45 = 97.8%** |
| Golden retrieval URLs | **25/25** |
| Backend tests | **28 passing** |

These are **README-reported, not independently re-run**.

The benchmark evaluates system behavior. It does **not** establish user demand, PMF, or usability.

---

# Current Scope

### Included

- one repository: `pallets/flask`
- Investigate mode
- Chat mode
- four question categories
- curated historical decisions
- PR / issue context
- evidence-grounded responses
- deterministic routing
- deterministic confidence
- refusal when evidence is missing

### Excluded

- complete repository-history crawling
- multi-repository deployment
- persistent sessions across restarts
- code editing/refactoring
- real-user validation

---

# Limitations

1. **Curated history:** the knowledge base is not the complete Flask history.
2. **Repository specificity:** the MVP is centered on Flask.
3. **Evidence availability:** some rationale may never have been documented.
4. **Model dependence:** answer wording varies with the configured model.
5. **In-memory state:** chat sessions and rate limiting are not distributed.
6. **Benchmark size:** 45 questions cannot establish broad real-world performance.
7. **User validation:** no real interviews or stranger test have been completed.

---

# Validation Status

| Validation item | Status |
|---|---|
| Technical implementation | ✅ Complete |
| Offline/system evaluation | ✅ Exists |
| PMF hypothesis | ✅ Reasoned |
| Simulated interview rehearsal | ✅ Complete |
| Real developer interviews | **Pending** |
| Real Insight Ledger | **Pending** |
| Opportunity sizing | **Pending** |
| Stranger test | **Pending** |
| Independent re-run of reported metrics | **Pending** |

---

# Definition of Done

> **A developer can ask a repository question, receive an answer grounded in retrievable evidence, inspect the sources behind it, and receive an explicit refusal when the system cannot support the answer.**

The implementation meets this technical scope.

**Real-world validation remains a separate milestone.**
