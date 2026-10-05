# BUILD LOG: CodeArchaeologist

> **Code tells you what. History tells you why.**

You join a project, open a file, and understand what it does in ten minutes. Understanding **why it was written that way** can take much longer.

The reasoning may be spread across commits, pull requests, issues, discussions, and the people who were involved at the time. CodeArchaeologist turns that history into a searchable, evidence-grounded system for asking **why**.

**Live:** https://code-archaeologist-tau.vercel.app/  
**Target repository:** `pallets/flask`

---

## Project Status

| # | Activity | Status |
|---|---|---|
| 1 | Problem, leverage map, human-owned decisions | ✅ Complete |
| 2 | 4D AI Fluency | ✅ Complete |
| 3 | Research brief and verification | ✅ Complete |
| 4 | Critical design thinking | ✅ Complete; 48-hour tests proposed, not run |
| 5 | PMF research | 🟡 Partial; real interviews pending |
| 6 | Build and systemize | ✅ Implementation complete; stranger test pending |

### Evidence policy

**Real user research:** none yet.

**Simulated conversations:** three AI-generated conversations were used only to rehearse interview questions and surface hypotheses. They are not interviews, findings, quotes, or validation.

**Synthetic / offline evaluation:** benchmark, classifier, retrieval and grounding checks evaluate the system itself. They are not user validation.

**README-reported:** where evaluation numbers come from the project's README and were not independently re-run, they are labeled as such.

---

# Activity 1 — Find a Problem Worth Solving

### What we were trying to solve

The starting question was not:

> "What can we build with AI?"

It was:

> **"Where does AI create real leverage while important judgment stays human?"**

### Problem

Developers can usually understand **what** unfamiliar code does before they understand **why** it exists.

A typical investigation becomes:

```text
code
  ↓
git blame
  ↓
commit
  ↓
PR
  ↓
issue / discussion
  ↓
finally find the context
```

The information exists, but the connections are expensive to reconstruct.

### Who experiences it

The initial target situations are:

- a developer onboarding to a repository they did not write
- an engineer preparing a refactor of unfamiliar or legacy code
- a reviewer facing a change with unclear original rationale
- a developer who found the relevant commit but still cannot explain why it happened
- an engineer deciding whether an old constraint is still intentional

These are **reasoned target situations, not validated user findings**.

### When it happens

The problem appears immediately before or during a consequential change:

- onboarding
- refactoring
- reviewing unfamiliar code
- debugging historical behavior
- deciding whether an apparently unnecessary constraint can safely be removed

### Cost / friction

The current workflow creates:

- repeated context switching between code and history
- manual searching across multiple GitHub artifacts
- uncertainty about whether a design choice was deliberate
- risk of removing or changing behavior whose original rationale is not obvious

No measured time-saved or monetary-cost figure was collected.

### Why now

The opportunity exists because:

1. LLMs can summarize long technical discussions.
2. Graph retrieval can connect decisions, PRs, issues, people, and dates.
3. Generic AI can produce plausible explanations without historical evidence, creating a trust problem.

So the goal was not simply **"use AI to explain code."**

The goal became:

> **Use AI to recover historical reasoning, but make the answer checkable.**

### Intended build

Build a system that ingests repository history into a knowledge graph and answers **why** questions with:

- linked evidence
- source URLs
- contributors and dates
- a traceable retrieval path
- deterministic confidence
- an explicit refusal when supporting evidence is missing

---

## Leverage Map

| Task | AI role |
|---|---|
| Pull PRs, issues and discussions from GitHub | **Automation** |
| Normalize and deduplicate raw records | **Automation** |
| Propose candidate decisions from technical discussions | **Augmentation** |
| Classify incoming questions | **Automation** |
| Retrieve connected historical evidence | **Automation** |
| Draft a readable explanation from retrieved evidence | **Augmentation** |
| Bounded automatic routing in Chat | **Agency** |

### Human-owned decisions

Humans retain ownership of:

1. **Scope** — start with one real repository, `pallets/flask`, rather than claiming universal repository support.
2. **Evidence quality** — decide what counts as a meaningful decision and trustworthy source.
3. **Refusal policy** — "no evidence" is a valid answer; the system should not invent historical rationale.

### Artifact

Problem framing, leverage map, scope decision and product principles are reflected in the project design and README.

---

# Activity 2 — Work With AI Deliberately: 4D Fluency

The goal was to use AI as a **work partner**, not an answer machine.

| D | How it appears in the project |
|---|---|
| **Delegation** | AI handles reading, extraction, drafting and synthesis; humans own scope, rules and release decisions. |
| **Description** | Historical, repository, general and hybrid questions use different prompts and evidence expectations instead of one vague prompt. |
| **Discernment** | Model output is never accepted raw: snippets are verified, citations are enforced, and confidence is computed outside the model. |
| **Diligence** | Tests, a benchmark and smoke checks exist so system changes can be checked rather than judged by fluency. |

### Delegation Map

| Work | Owner |
|---|---|
| Ingestion, normalization, retrieval | **AI / automation-led** |
| Decision extraction | **Shared** — AI proposes, humans curate |
| Answer drafting | **Shared** — AI drafts, grounding gates filter |
| Scope, refusal rules, confidence rules, release | **Human-led** |

### What AI cannot reliably evaluate

The model cannot reliably decide:

- whether extracted rationale truly matches what maintainers intended
- whether "no evidence found" means "no reason existed"
- whether an answer is useful enough for a developer to act on

### Three Review Checkpoints

**1. After extraction**  
Candidate decisions are compared with their source before becoming graph evidence.

**2. After synthesis**  
Grounding rules and citation checks operate before the answer reaches the user.

**3. Before release**  
Tests, evaluation and smoke checks are used to check changes.

> **Key decision:** 4D AI Fluency became a product property. The tool questions AI output the same way we tried to question our own assumptions.

### Artifacts

Grounding logic, category-specific prompts, evaluation tooling and test modules.

---

# Activity 3 — Research and Verify

## Six-Part Research Brief

| Part | Definition |
|---|---|
| **Context** | Design rationale for old code is harder to recover than code behavior itself. |
| **Objective** | Determine whether historical rationale can be retrieved from repository history and returned with verifiable evidence. |
| **Task** | Study where rationale appears in repository history and design extraction, retrieval and synthesis around it. |
| **Constraints** | Public repository data, one repository, practical service limits, no invented history. |
| **Output** | A decision graph plus a question-answering pipeline. |
| **Success criteria** | Claims trace to real sources; routing/retrieval hit expected evaluation targets; missing evidence produces a refusal. |

## Five Questions Used to Expose Gaps

1. Where does rationale actually live: commits, PRs, issues or comments?
2. How can a retrieved snippet be verified against its original source?
3. What should happen when no useful evidence exists?
4. Which question types need different evidence and answer structures?
5. How should routing and retrieval quality be measured?

## Evidence / Inference / Hypothesis / Assumption

| Type | Example |
|---|---|
| **Evidence** | Flask repository PRs, issues and discussions provide linkable historical sources. |
| **Inference** | A graph connecting decisions to PRs, issues, people and dates should make historical context easier to retrieve than isolated text search. |
| **Hypothesis** | A developer about to change unfamiliar code would prefer a cited explanation before manually reconstructing the full thread. |
| **Assumption** | The reasoning behind a design choice was recorded somewhere in the available repository history. |

## What Research Changed

| What we learned / recognized | Product decision |
|---|---|
| Rationale is scattered across repository artifacts | Model relationships as a graph rather than isolated documents |
| Fluent AI output is not automatically trustworthy | Verify evidence snippets before allowing them into answers |
| Claims can become detached from sources during synthesis | Require `evidence_id` citations |
| Evidence may simply be missing | Make `no_evidence` a first-class outcome |
| Different questions need different evidence | Route historical, repository, general and hybrid questions separately |

### Verification Step

The product checks evidence against its source text, requires claim-level citations, and uses benchmark evaluation for routing and retrieval.

### Evaluation

The existing project README reports:

- **44/45 (97.8%)** classifier benchmark accuracy
- **25/25** golden retrieval matches

These are **README-reported results and were not independently re-run for this documentation**.

### Artifacts

Existing benchmark questions, evaluation code and evaluation documentation.

---

# Activity 4 — Challenge the Design

## Five Whys

| Why? | Answer |
|---|---|
| Why do developers hesitate or make mistakes when changing old code? | They do not know whether an unusual design was deliberate. |
| Why don't they know? | The reasoning is rarely in the code itself. |
| Why not? | It often lives in long PR and issue conversations. |
| Why is that hard to reach? | `git blame` and commits identify changes but do not reconstruct the surrounding reasoning. |
| Why is there still a gap? | Repository tools organize *what, who and when* more directly than *why*. |

### Root Cause

> **Historical rationale is unstructured and poorly linked to the code it explains.**

## Two Reframes

### Reframe 1

**From:** "Explain this code."

**To:** **"Was this design choice intentional, and why?"**

### Reframe 2

**From:** "Give me a good answer."

**To:** **"Give me an answer I can check before I change anything."**

### What Changed

The product moved from a generic code-explainer idea toward an **evidence-retrieval product with refusal built in**.

## Two Critics

| Critic | Objection | Design response |
|---|---|---|
| **Skeptical engineer** | "I can just read the PR myself." | Fair for one change; the proposed value is reducing the work across multiple linked sources. |
| **Hallucination critic** | "An LLM can invent plausible history." | Verbatim verification, mandatory citations and zero-evidence refusal. |

## Three Assumptions + Proposed 48-Hour Tests

These are **test criteria, not completed results**.

| Assumption | Type | Proposed test | Pass | Fail | Result |
|---|---|---|---|---|---|
| **A1. Rationale exists in repository history** | Evidence availability | Inspect 10 known Flask design changes and check whether a source explicitly states the reason | ≥7/10 contain rationale | <5/10 | **Pending** |
| **A2. Retrieval connects the right discussion to the right decision** | Technical | Run 20 "why" questions and compare returned evidence with expected threads | ≥90% expected-source match | <75% | **Pending** |
| **A3. Developers trust sourced answers enough to use them** | User | Give real developers a "why" question and observe whether they inspect the sources and would act on the result | Most inspect and trust the evidence | Most ignore/distrust it | **Pending** |

> **These thresholds are proposed tests. No user-validation result is claimed.**

## Problem Statement v2

> **A developer about to modify unfamiliar code needs to know whether an old design choice was intentional. Today they chain blame, commits, PRs and issue threads by hand. We provide sourced answers linking each decision to its history, and say plainly when no evidence exists.**

---

# Activity 5 — Product-Market Fit Research

## PMF Hypothesis

> **A developer is about to modify unfamiliar code and needs to know whether an old design choice was intentional. If a tool can show the original reasoning with sources, they will check it before changing the code.**

## Specific ICP

A developer making a **non-trivial change to a mature or legacy codebase they did not write**.

### Five Practical ICP Scenarios

These are representative scenarios, **not five real interviewed users**:

1. A new developer onboarding to a large open-source repository.
2. An engineer inheriting an older internal service.
3. A developer preparing a refactor around code they did not author.
4. A reviewer investigating a change with unclear historical rationale.
5. A maintainer deciding whether an old compatibility constraint is still necessary.

## Current Substitutes

| Substitute | What works | Remaining friction |
|---|---|---|
| `git blame` / `git log` | Quickly identifies who/when | Weak on why |
| GitHub search + PR threads | Usually authoritative | Slow across connected discussions |
| General AI chat | Fast explanation | May explain intent without historical evidence |
| Ask a teammate | High-context answer | Depends on availability |

## Mechanism

A **decision graph** connects:

```text
decision ↔ PR ↔ issue ↔ contributor ↔ date ↔ repository context
```

Retrieval finds the relevant chain. Grounding rules make trust depend on the underlying evidence rather than model confidence.

## One User Flow

> **Unfamiliar code → ask why → classify → retrieve linked history → verify evidence → grounded answer → inspect source → decide whether to change the code.**

## Simulated Conversations

Three AI-generated conversations were used only to **rehearse the interview questions and shape hypotheses**.

They suggested questions worth testing around:

- whether developers understand *what* before *why*
- how difficult Git history is to search
- whether source links affect trust
- whether incomplete history could lead to misleading conclusions

These are **hypotheses, not findings**.

## Validation Status

| Item | Status |
|---|---|
| PMF hypothesis | ✅ Reasoned |
| ICP | ✅ Reasoned |
| Five practical ICP scenarios | ✅ Documented as scenarios |
| Substitutes | ✅ Documented |
| Mechanism | ✅ Documented |
| One user flow | ✅ Documented |
| Real interviews | **Pending** |
| Real Insight Ledger | **Pending** |
| Real user validation | **Pending** |
| Opportunity sizing | **Pending** |

### Opportunity Sizing

The challenge framework is:

> **Findable users × realistic price × realistic adoption**

No defensible figures were gathered, so no opportunity number is claimed.

### Current PMF Conclusion

The problem is **plausible and well-defined**, but whether developers actually change their workflow because of CodeArchaeologist remains an open question.

---

# Activity 6 — Build and Systemize

The existing deployed CodeArchaeologist application is the implementation documented here.

## Meaningful User Flow

```text
Ask "why?"
    ↓
Classify the question
    ↓
Retrieve decisions / PRs / issues
    ↓
Verify evidence
    ↓
Synthesize grounded answer
    ↓
Show sources / people / dates
    ↓
Developer decides what to do next
```

## Stack + Why

| Choice | Why |
|---|---|
| **FastAPI / Python** | One backend language for ingestion, API and model integration |
| **Neo4j Aura** | Decisions and repository history are naturally relationship-heavy |
| **Gemini via OpenAI-compatible endpoint** | Investigate synthesis with provider failover |
| **Sarvam AI** | Chat and general Q&A path |
| **Deterministic classifier** | Predictable and testable routing without an extra LLM call |
| **Next.js 15 / Vercel** | Interactive frontend with straightforward deployment |

## Architecture

```text
Next.js
   ↓
FastAPI
   ↓
Query Classifier
   ↓
Retrieval
 ├── Neo4j graph
 ├── repository context
 └── optional vectors
   ↓
Category-specific synthesis
   ↓
Grounding / Verification
   ↓
Structured answer + evidence
```

Chat additionally uses a conversation service with session handling, caching and rate limiting.

## Evidence + Confidence

The core design rule is:

> **A fluent answer is not enough.**

The system therefore:

1. verifies evidence snippets against source text
2. requires `evidence_id` citations for claims
3. removes unsupported claims
4. bypasses the LLM when useful evidence is absent
5. returns `no_evidence` instead of inventing historical rationale
6. computes confidence from evidence-related signals outside the LLM

## System Evaluation

The existing README reports:

| Evaluation | Result |
|---|---|
| Historical questions | 25/25 |
| Repository questions | 10/10 |
| General questions | 5/5 |
| Hybrid questions | 4/5 |
| Overall classifier | **44/45 = 97.8%** |
| Golden retrieval URLs | **25/25** |
| Backend tests | **28 passing** |

These results are **README-reported and not independently re-run for this document**.

The one classifier miss is a hybrid question routed as repository.

## Failure / Break Cases

The existing project includes tests for failure-oriented behavior such as:

- fabricated evidence rejection
- uncited-claim stripping
- partial-confidence handling
- rate limiting
- session isolation
- API contract behavior

A separate adversarial break-test log was not independently verified.

## Review

| Review | Status |
|---|---|
| Automated tests | Exists; README-reported |
| Benchmark | Exists; README-reported |
| Human code review | Not documented |
| AI review | Not documented |
| Stranger test | **Pending** |

## Reusable Workflow

```text
github_ingest
    ↓
normalize
    ↓
extract_decisions
    ↓
neo4j_schema
    ↓
neo4j_ingest
    ↓
eval
    ↓
smoke
```

This is the intended repeatable workflow for changing the repository/data source.

---

# What Remains

The implementation is built. The unresolved work is mostly **outside the code**:

- real developer interviews
- a real Insight Ledger
- opportunity sizing with defensible inputs
- proposed 48-hour tests
- a stranger test
- independent re-runs of reported benchmark/test numbers
- evidence about whether the product changes developer behavior

That distinction matters:

> **Implementation completion ≠ product validation.**

---

# The Through-Line

We started with a developer problem, not an AI feature.

We asked where AI could help, kept judgment human-owned, challenged the assumption that fluent answers are trustworthy, and built the product around a simple rule:

> **Make the answer easier to check, not merely easier to believe.**

The technical system is built.

The next meaningful test is with real developers.
