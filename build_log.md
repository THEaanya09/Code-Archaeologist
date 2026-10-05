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
| 5 | PMF research | 🟡 **Partial; senior-developer interview study prepared, execution pending** |
| 6 | Build and systemize | ✅ Complete (implementation); **stranger test pending** |

### Evidence policy

**Real user research:** no completed interviews have been claimed yet.

**Interview study:** a structured interview protocol is prepared for 3–5 senior developers currently working in technology companies. The purpose is to validate the problem from real past behavior rather than ask participants to approve the proposed solution.

**Simulated conversations:** earlier AI-generated conversations were used only to rehearse the interview questions and surface hypotheses. They are not interviews, findings, quotes, or validation.

**Synthetic / offline evaluation:** benchmark, classifier, retrieval and grounding checks evaluate the system itself. They are not user validation.

**README-reported:** evaluation numbers taken from the project README are labeled as such when they have not been independently re-run.

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
3. Generic AI can produce plausible "why" explanations without historical evidence, creating a trust risk.

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

1. **Scope:** start with one real repository, `pallets/flask`.
2. **Evidence quality:** decide what counts as a meaningful decision and trustworthy source.
3. **Refusal policy:** "no evidence" is a valid answer; the system should not invent historical rationale.

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
| **Diligence** | Tests, benchmark questions and smoke checks exist so system changes can be checked rather than judged by fluency. |

### Delegation Map

| Work | Owner |
|---|---|
| Ingestion, normalization, retrieval | **AI / automation-led** |
| Decision extraction | **Shared** — AI proposes, humans curate |
| Answer drafting | **Shared** — AI drafts, grounding gates filter |
| Scope, refusal rules, confidence rules, release | **Human-led** |

### What AI cannot reliably evaluate

- whether extracted rationale truly matches maintainer intent
- whether "no evidence found" means "no reason existed"
- whether an answer is useful enough for a developer to act on

### Three Review Checkpoints

**1. After extraction:** compare candidate decisions with their sources.

**2. After synthesis:** apply grounding and citation checks.

**3. Before release:** run tests, evaluation and smoke checks.

> **Key decision:** 4D AI Fluency became a product property. The tool questions AI output instead of simply presenting it.

### Artifacts

Grounding logic, category-specific prompts, evaluation tooling and test modules.

---

# Activity 3 — Research and Verify

## Six-Part Research Brief

| Part | Definition |
|---|---|
| **Context** | Design rationale for old code is harder to recover than code behavior itself. |
| **Objective** | Determine whether historical rationale can be retrieved from repository history and returned with verifiable evidence. |
| **Task** | Study where rationale appears and design extraction, retrieval and synthesis around it. |
| **Constraints** | Public repository data, one repository, practical service limits, no invented history. |
| **Output** | A decision graph plus a question-answering pipeline. |
| **Success criteria** | Claims trace to real sources; routing/retrieval hit expected evaluation targets; missing evidence produces a refusal. |

## Five Questions Used to Expose Gaps

1. Where does rationale actually live: commits, PRs, issues or comments?
2. How can a retrieved snippet be verified against its source?
3. What should happen when no useful evidence exists?
4. Which question types need different evidence and answer structures?
5. How should routing and retrieval quality be measured?

## Evidence / Inference / Hypothesis / Assumption

| Type | Example |
|---|---|
| **Evidence** | Flask repository PRs, issues and discussions provide linkable historical sources. |
| **Inference** | A graph connecting decisions to PRs, issues, people and dates should make historical context easier to retrieve than isolated search. |
| **Hypothesis** | A developer about to change unfamiliar code would prefer a cited explanation before reconstructing the thread manually. |
| **Assumption** | The reasoning behind a design choice was recorded somewhere in the available history. |

## What Research Changed

| Observation | Product decision |
|---|---|
| Rationale is scattered across repository artifacts | Model relationships as a graph |
| Fluent AI output is not automatically trustworthy | Verify evidence snippets |
| Claims can become detached from sources | Require `evidence_id` |
| Evidence may simply be missing | Make `no_evidence` a first-class outcome |
| Different questions need different evidence | Route historical, repository, general and hybrid questions separately |

### Evaluation

The existing README reports:

- **44/45 (97.8%)** classifier benchmark accuracy
- **25/25** golden retrieval matches

These are **README-reported and not independently re-run for this log**.

### Artifact

Existing benchmark questions, evaluation code and evaluation documentation.

---

# Activity 4 — Challenge the Design

## Five Whys

| Why? | Answer |
|---|---|
| Why do developers hesitate or make mistakes when changing old code? | They do not know whether an unusual design was deliberate. |
| Why don't they know? | The reasoning is rarely in the code itself. |
| Why not? | It often lives in long PR and issue conversations. |
| Why is that hard to reach? | `git blame` and commits identify changes but not the surrounding reasoning. |
| Why is there still a gap? | Repository tools organize *what, who and when* more directly than *why*. |

### Root Cause

> **Historical rationale is unstructured and poorly linked to the code it explains.**

## Two Reframes

**From:** "Explain this code."  
**To:** **"Was this design choice intentional, and why?"**

**From:** "Give me a good answer."  
**To:** **"Give me an answer I can check before I change anything."**

### Two Critics

| Critic | Objection | Response |
|---|---|---|
| **Skeptical engineer** | "I can just read the PR myself." | Fair for one change; the proposed value is reducing work across multiple linked sources. |
| **Hallucination critic** | "An LLM can invent plausible history." | Verbatim verification, mandatory citations and zero-evidence refusal. |

## Three Assumptions + Proposed 48-Hour Tests

These are **proposed tests, not completed results**.

| Assumption | Type | Proposed test | Pass | Fail | Result |
|---|---|---|---|---|---|
| **A1. Rationale exists in repository history** | Evidence availability | Inspect 10 known Flask changes and check whether a source explicitly states the reason | ≥7/10 | <5/10 | **Pending** |
| **A2. Retrieval connects the right discussion to the right decision** | Technical | Run 20 "why" questions and compare returned evidence with expected threads | ≥90% | <75% | **Pending** |
| **A3. Developers trust sourced answers enough to use them** | User | Test with real developers and observe whether they inspect sources and would act on the answer | Most do | Most ignore/distrust | **Pending** |

## Problem Statement v2

> **A developer about to modify unfamiliar code needs to know whether an old design choice was intentional. Today they chain blame, commits, PRs and issue threads by hand. We provide sourced answers linking each decision to its history, and say plainly when no evidence exists.**

---

# Activity 5 — Product-Market Fit Research

## PMF Hypothesis

> **A developer is about to modify unfamiliar code and needs to know whether an old design choice was intentional. If a tool can show the original reasoning with sources, they will check it before changing the code.**

## Specific ICP

A developer making a **non-trivial change to a mature or legacy codebase they did not write**.

### Practical Situations

- onboarding to an unfamiliar repository
- preparing a refactor
- reviewing a change with unclear rationale
- finding a commit but not understanding why it happened
- deciding whether an old constraint is still intentional

These are **scenario hypotheses, not observed user behavior**.

## Substitutes

| Substitute | What works | Friction |
|---|---|---|
| `git blame` / `git log` | Finds who and when | Weak on why |
| GitHub search + PR threads | Usually authoritative | Slow across connected discussions |
| General AI | Fast explanation | May explain intent without historical evidence |
| Ask a teammate | High-context answer | Depends on availability |

## Mechanism

```text
decision ↔ PR ↔ issue ↔ contributor ↔ date ↔ repository context
```

Retrieval finds the connected history. Grounding makes the final answer depend on evidence rather than model confidence.

## One User Flow

> **Unfamiliar code → ask why → classify → retrieve linked history → verify evidence → grounded answer → inspect source → decide whether to change the code.**

---

## Real Interview Study

The interview study is designed to validate the problem with **experienced developers who have already worked in real production codebases**.

### Target participants

Recruit **3–5 senior developers / software engineers currently working at technology companies**.

Prefer participants who have experience with:

- maintaining an existing production codebase
- onboarding to a large engineering repository
- reviewing or refactoring code they did not author
- debugging regressions caused by changes to old code
- tracing historical decisions through GitHub/Git history

The goal is to speak to people who have actually experienced the problem, rather than people who are simply interested in AI tools.

### Interview format

**10–15 minutes, one-on-one.**

Do not pitch CodeArchaeologist at the beginning.

First understand the participant's current workflow and a specific recent incident. Only introduce the concept near the end.

### Interview script

**Opening**

> "Hey, I'm working on a small developer-tool project and I'm researching how experienced engineers deal with unfamiliar code. I don't want to sell you anything — I'm mainly interested in how you actually work. Could I ask you a few questions about a recent example?"

**Question 1 — Recent situation**

> "Think about the last time you had to change code that someone else had written. What were you working on?"

**Question 2 — First move**

> "When you first got into that code, what did you actually do to understand it?"

**Question 3 — The turning point**

> "Was there a point where you understood what the code was doing but still didn't understand why it had been designed that way?"

**Question 4 — History**

> "What did you check then — Git history, blame, PRs, issues, docs, Slack, someone on the team? Walk me through what you actually did."

**Question 5 — Friction**

> "What was the hardest part of finding that context?"

**Question 6 — Consequence**

> "Did that uncertainty change what you did? For example, did you delay the change, leave the code alone, ask someone, or make a smaller change?"

**Question 7 — Missing owner**

> "What happens when the person who originally worked on it isn't available?"

**Question 8 — Trust**

> "Suppose you got an automated explanation of why a design decision existed. What would you need to see before you trusted it?"

**Question 9 — Evidence**

> "Would the original PR, issue, commit, date, or people involved matter? Which of those would you actually check?"

**Question 10 — Failure mode**

> "What could a tool like that get wrong in a way that would be dangerous or misleading?"

**Only now introduce the concept**

> "We're exploring a tool that searches repository history and tries to answer 'why was this designed this way?' while showing the original evidence. What would you expect it to do before you would consider using something like that?"

**Closing**

> "Is there anything about this problem that I'm missing?"

### Interview rules

- Ask about **specific past behavior**, not idealized behavior.
- Do not lead participants toward CodeArchaeologist.
- Do not ask for positive feedback.
- Do not tell participants what you expect them to say.
- Capture exact wording where useful.
- Separate raw notes from interpretation.
- Do not turn a single participant's opinion into a general finding.
- Do not create an Insight Ledger entry unless it is supported by actual notes.

### Capture template

```text
Participant ID:
Role:
Years of experience:
Company type:
Codebase situation:
Recent example:
What they actually did:
Where they got stuck:
Current workaround:
Time / effort involved:
Consequence of uncertainty:
Evidence they trusted:
What they distrusted:
Notable quote:
Researcher interpretation:
Follow-up hypothesis:
```

### Validation threshold

A practical first threshold is:

> **3 of 5 senior developers independently describe a recurring difficulty in recovering historical rationale, and at least 3 of 5 say source-backed historical context would be useful in that workflow.**

This is a **future validation criterion, not a completed result**.

---

## Simulated Conversations

Earlier AI-generated conversations were used only to rehearse the interview questions.

They surfaced hypotheses around:

- understanding *what* before *why*
- difficulty navigating Git history
- importance of source links for trust
- incomplete history as a possible failure mode

They are **not real participants, findings, quotes, or validation**.

---

## Validation Status

| Item | Status |
|---|---|
| PMF hypothesis | ✅ Reasoned |
| ICP | ✅ Reasoned |
| Practical ICP scenarios | ✅ Documented |
| Substitutes | ✅ Documented |
| Mechanism | ✅ Documented |
| One user flow | ✅ Documented |
| Senior-developer interview target | ✅ Defined |
| Interview script | ✅ Prepared |
| Interview capture template | ✅ Prepared |
| Validation threshold | ✅ Defined |
| Real interviews | **Pending execution** |
| Real Insight Ledger | **Pending** |
| Real user validation | **Pending** |
| Opportunity sizing | **Pending** |
| Stranger test | **Pending** |

### Opportunity Sizing

The challenge framework is:

> **Findable users × realistic price × realistic adoption**

No defensible figures were gathered, so no opportunity number is claimed.

### PMF Conclusion

The problem is **plausible and clearly scoped**.

The next evidence needed is not another theoretical exercise. It is whether experienced developers describe the same pain when recalling real work they've already done.

---

# Activity 6 — Build and Systemize

The existing deployed application is the implementation documented here.

## Meaningful User Flow

```text
Ask "why?"
    ↓
Classify
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
| **Neo4j Aura** | Repository history is naturally relationship-heavy |
| **Gemini via OpenAI-compatible endpoint** | Investigate synthesis with failover |
| **Sarvam AI** | Chat and general Q&A path |
| **Deterministic classifier** | Predictable and testable routing |
| **Next.js 15 / Vercel** | Interactive frontend and straightforward deployment |

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

Chat additionally uses session handling, caching and rate limiting.

## Evidence + Confidence

1. Evidence snippets are checked against source text.
2. Claims require `evidence_id`.
3. Unsupported claims are removed.
4. No useful evidence → bypass the LLM.
5. Return `no_evidence` instead of inventing rationale.
6. Confidence is computed outside the model.

## System Evaluation

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

## Failure / Break Cases

The existing project includes tests for:

- fabricated evidence rejection
- uncited-claim stripping
- partial-confidence handling
- rate limiting
- session isolation
- API contract behavior

A dedicated adversarial break-test log was not separately verified.

## Review

| Review | Status |
|---|---|
| Automated tests | Exists; README-reported |
| Benchmark | Exists; README-reported |
| Human code review | Not documented |
| AI review | Not documented |
| **Stranger test** | **Pending** |

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

The implementation is built.

The remaining work is **real-world validation**:

- execute the senior-developer interviews
- capture raw notes
- build the real Insight Ledger
- test the PMF hypothesis
- run the proposed 48-hour tests
- run a stranger test
- gather defensible opportunity-sizing inputs
- independently re-run reported benchmark/test numbers

> **Implementation completion ≠ product validation.**

---

# The Through-Line

We started with a developer problem, not an AI feature.

We asked where AI could help, kept judgment human-owned, challenged the assumption that fluent answers are trustworthy, and built the product around a simple rule:

> **Make the answer easier to check, not merely easier to believe.**

The technical system is built.

The next meaningful test is with experienced developers who have actually had to recover the history behind unfamiliar code.
