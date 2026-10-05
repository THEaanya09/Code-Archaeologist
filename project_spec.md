# PROJECT SPEC: CodeArchaeologist

> **Code tells you what. History tells you why.**

**Live:** https://code-archaeologist-tau.vercel.app/  
**Target repository:** `pallets/flask`

---

# The 8 Questions

## 1. What is this?

CodeArchaeologist is a repository-intelligence web app that answers:

> **"Why is this code the way it is?"**

Instead of explaining only what code does, it reconstructs historical reasoning from pull requests, issues, discussions and extracted decisions.

Repository history is represented as a Neo4j knowledge graph. The system retrieves relevant evidence, verifies it, and returns a cited answer.

When supporting evidence cannot be found, it returns **`no_evidence` rather than inventing a rationale**.

---

## 2. Who uses it?

The intended user is a developer making a meaningful change to code they did not write.

Typical situations include:

- onboarding to an unfamiliar repository
- preparing a refactor
- reviewing a change whose historical rationale is unclear
- finding a commit but not understanding why it happened
- deciding whether an old constraint is still intentional

This is a **reasoned ICP, not yet validated through real interviews**.

---

## 3. What must it do?

### Input

Accept a natural-language repository question.

### Routing

Classify the question as:

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

Return a structured answer appropriate to the question type.

The answer should expose:

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

Given a question with no useful supporting evidence, the system must return:

```text
no_evidence
```

rather than generate an unsupported historical explanation.

---

## 4. What does it NOT do?

The MVP deliberately does **not**:

- crawl the complete history of every repository
- support multiple repositories in the deployed instance
- preserve chat sessions across restarts
- edit, generate or refactor code
- guarantee that historical rationale exists for every question
- treat benchmark accuracy as proof of product-market fit
- claim real-user validation

### Current MVP boundary

The deployed scope is centered on:

> **`pallets/flask` + curated decisions + sample PR/issue data**

---

## 5. What data does it use?

| Data | Purpose |
|---|---|
| GitHub pull requests | Historical changes and discussions |
| GitHub issues / discussions | Rationale and context |
| Extracted decisions | Searchable historical decision records |
| Contributors / dates | Decision context |
| Repository modules / files | Repository-level context |
| Neo4j graph | Connects decisions and repository relationships |
| Benchmark questions | Routing/retrieval evaluation |
| Chat history | Short-lived conversational context |

The existing project README reports **25 curated golden decisions** and a **45-question benchmark**.

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

API keys must remain server-side and must not be exposed through public frontend environment variables.

### Retrieval

Optional vector retrieval requires an embeddings endpoint.

---

## 7. What does "done" mean?

A technically complete system must satisfy this contract:

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

### Definition-of-done checklist

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
| Real interviews | **Pending** |
| Stranger test | **Pending** |

The project README reports:

- **44/45 (97.8%)** classifier performance
- **25/25** golden retrieval matches
- **28 passing backend tests**

These remain **README-reported results**, not independently re-run results.

---

## 8. What remains unknown?

### User behavior

Do developers actually look through repository history before changing unfamiliar code?

### Trust

Is a cited answer enough to influence a developer's next action?

### Evidence availability

How often does repository history contain enough rationale to answer the questions developers actually ask?

### Retrieval quality

Can the system reliably connect the correct discussion to the correct design decision outside the curated benchmark?

### Transferability

Does the approach work on repositories with sparse, inconsistent or undocumented history?

### Product value

Does the workflow save enough time or reduce enough uncertainty to become part of a developer's normal workflow?

### Market

What is a defensible opportunity size?

### Validation

No real interviews or stranger test have been completed yet.

---

# Core User Flow

> **Unfamiliar code → ask why → classify → retrieve linked history → verify evidence → grounded answer → inspect source → decide whether to change the code.**

### Example

A developer encounters an unfamiliar behavior and asks:

> **"Why was `request.json` deprecated?"**

The system should:

1. identify the question type
2. retrieve relevant evidence
3. verify the evidence
4. synthesize the explanation
5. show the source trail
6. let the developer inspect the evidence before acting

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

Chat adds session handling, caching and rate limiting.

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

The project's core rule is:

> **A plausible answer is not enough.**

### 1. Evidence verification

Retrieved snippets are checked against their underlying source text.

### 2. Claim-level citations

Generated claims must reference an `evidence_id`.

### 3. Unsupported-claim removal

Claims without valid evidence are removed.

### 4. Zero-evidence guard

When retrieval produces no useful evidence, the LLM is bypassed and:

```text
no_evidence
```

is returned.

### 5. Confidence

Confidence is computed outside the LLM from evidence-related signals and citation behavior.

---

# Non-Negotiables

These are product rules, not optional UX choices:

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

These are **README-reported results, not independently re-run**.

The benchmark evaluates system behavior; it does **not** establish user demand or product-market fit.

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

1. **Curated history:** the knowledge base is not the entire Flask history.
2. **Repository specificity:** the MVP is centered on Flask.
3. **Evidence availability:** some design rationale may never have been documented.
4. **Model dependence:** answer wording varies with the configured model.
5. **In-memory state:** chat sessions and rate limiting are not distributed.
6. **Benchmark size:** 45 questions are useful for regression checks but cannot prove broad real-world performance.
7. **Validation:** no real interviews or stranger test have been completed.

---

# Definition of Done

> **A developer can ask a repository question, receive an answer grounded in retrievable evidence, inspect the sources behind it, and receive an explicit refusal when the system cannot support the answer.**

The implementation meets this technical scope.

**Real-world validation remains a separate milestone.**

---

# Open Questions

- Do developers actually reach for repository history before modifying unfamiliar code?
- Is a sourced answer faster or more useful than manually reading the original thread?
- How much rationale exists for the code developers actually care about?
- Can retrieval generalize beyond the curated Flask benchmark?
- Does the workflow transfer to repositories with sparse discussion history?
- Would developers return to the tool repeatedly?
- What would a real stranger test reveal?
- What is a defensible opportunity size?
