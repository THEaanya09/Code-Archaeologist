# BUILD LOG | CodeArchaeologist

> **Code tells you what. History tells you why.**

You join a project, open a file, and understand what it does in ten minutes. Understanding **why it was written that way** can take much longer.

The reasoning may be spread across commits, pull requests, issues, discussions, and the people who were involved at the time. CodeArchaeologist turns that history into a searchable, evidence-grounded system for asking **why**.

**Live demo:** [code-archaeologist-tau.vercel.app](https://code-archaeologist-tau.vercel.app/)  
**Source repository:** [THEaanya09/Code-Archaeologist](https://github.com/THEaanya09/Code-Archaeologist)  
**Target repository:** `pallets/flask`

> **Snapshot:** The implementation is built and deployed. Three exploratory developer conversations (P01–P03) and one first-time tester feedback record (T01) inform the current product direction. T01 independently completed the initial question task, could not complete the historical-answer task, and did not test source verification or the no-evidence response. A later 4/4 description was explicitly hypothetical, not a retest, and is excluded from the observed results.

## At a Glance

| Area | Current evidence |
|---|---|
| Implementation | Existing deployed app and six-activity project documentation |
| Developer research | Three exploratory conversations, with partial notes for P02 and P03 |
| First-time usability | T01 completed 1 of 4 tasks independently; 1 task could not be completed; 2 tasks were not tested |
| Technical evaluation | README reports 28 tests passing, 44/45 classifier accuracy, and 25/25 retrieval matches; this packaging pass did not execute those commands |
| Product-market fit | Early qualitative signals only; no adoption, time-saved, or willingness-to-pay result is claimed |

## Quick Navigation

- [Activity 1 — Problem and leverage](#activity-1--find-a-problem-worth-solving)
- [Activity 2 — 4D AI Fluency](#activity-2--work-with-ai-deliberately-4d-fluency)
- [Activity 3 — Research and verification](#activity-3--research-and-verify)
- [Activity 4 — Critical design thinking](#activity-4--challenge-the-design)
- [Activity 5 — PMF research and developer interviews](#activity-5--product-market-fit-research)
- [Activity 6 — Build and systemize](#activity-6--build-and-systemize)

---

## Project Status

| # | Activity | Status |
|---|---|---|
| 1 | Problem, leverage map, human-owned decisions | ✅ Complete |
| 2 | 4D AI Fluency | ✅ Complete |
| 3 | Research brief and verification | ✅ Complete |
| 4 | Critical design thinking | ✅ Problem reframes, critics, assumptions, and test criteria documented |
| 5 | PMF research | ✅ Three exploratory conversations synthesized; findings remain preliminary |
| 6 | Build and systemize | ✅ Implementation built; first-time usability evidence summarized below |

### Evidence policy

**Real user research:** three exploratory developer conversations (P01–P03) have been reported by the project owner. P01 is dated **14 October 2026**. The dates, exact job titles, and employers for P02 and P03 were not supplied in the notes reviewed here, so they are not inferred. The supplied P02 notes are partial; the P03 excerpt covers the later workflow-improvement, trust, and post-concept-feedback questions, but does not include answers to questions 1–7 or a concrete past incident. Findings are preliminary and do not establish market-wide validation.

**Interview study:** the protocol below is structured for conversations with developers who have worked in unfamiliar or inherited codebases, using past behavior and concrete examples as the primary evidence.

**Simulated conversations:** three AI-generated conversations from an earlier session were used only to rehearse interview questions. They are not interviews, findings, quotes, or validation, and are kept separate from P01, P02, and P03.

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

### One task through the 4D lens: answering a historical “why” question

| D | Applied to this task |
|---|---|
| **Delegation** | Let the system retrieve candidate context and draft an answer from repository evidence. |
| **Description** | Specify that historical claims must use retrieved evidence and cite valid `evidence_id` values. |
| **Discernment** | Reject unsupported snippets/claims and return `no_evidence` when evidence is insufficient. |
| **Diligence** | Check behavior with grounding tests, benchmark questions and a smoke check; the recorded project metrics remain README-reported until rerun. |

This is an implementation walkthrough of the project's approach, not a claim that a new test was run for this document.

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

### Artifacts and evidence trail

- **Existing project artifacts (README-reported):** benchmark question set, evaluation code and evaluation documentation.
- **Interview evidence:** the participant notes shared by the project owner are summarized in Activity 5, with partial-note boundaries identified.
- **Source register and sizing model:** `RESEARCH_EVIDENCE.md` records public sources, claim limits, and the assumptions used in the illustrative opportunity scenarios. It is a curated register created for this submission, not a verbatim export of earlier AI research output.

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

| Assumption | Type | Proposed test | Pass | Inconclusive | Fail |
|---|---|---|---|---|---|
| **A1. Rationale exists in repository history** | Evidence availability | Inspect 10 known Flask changes and check whether a source explicitly states the reason | ≥7/10 | 5–6/10 | ≤4/10 |
| **A2. Retrieval connects the right discussion to the right decision** | Technical | Run 20 “why” questions and compare returned evidence with expected threads | ≥90% | 75–89% | <75% |
| **A3. Developers trust sourced answers enough to use them** | User | Run a moderated trial with 3 developers; observe source inspection and ask whether the answer would inform a real change | ≥2/3 inspect evidence and say it could help | Mixed behavior or unclear usefulness | 0/3 find it useful or trust the evidence |

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

The interview study is designed to validate the problem with **developers who have worked in real, unfamiliar or inherited codebases**.

### Target participants

Aim for **3–5 developers**, ideally experienced engineers currently working on software teams. Record seniority and employer only when the participant confirms those details; do not infer them from the conversation.

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

### Completed Exploratory Interview — P01

| Interview detail | Record |
|---|---|
| **Date** | 14 October 2026 (from the shared message timestamps) |
| **Participant** | P01 (anonymized) |
| **Format** | Informal, exploratory conversation |
| **Evidence source** | Conversation transcript shared by the project owner |

> **Scope note:** The transcript discusses the participant's developer experience but does not specify an exact job title or employer. Those details are not assumed here.

#### What P01 described

> “The commits mostly described what changed, not why.”
>
> “I'd rather see ‘couldn't find enough evidence’ than some made-up reasoning.”

The first quote describes the participant's history-search experience. The second was said after the product concept was introduced, so it is treated as concept feedback rather than evidence of adoption.

- **Understanding the whole system was harder than understanding individual functions.** P01 described difficulty connecting files and modules, tracing data flow, and understanding what happened when a request arrived.
- **The reason behind a design could remain unclear even after the code was traced.** In one example, the same API call passed through multiple layers. P01 could follow what each layer did, but could not confidently establish why it had been structured that way.
- **Git history gave clues, not always rationale.** P01 said commits often described what changed rather than why. Documentation and history helped partially, but did not always tell the whole story.
- **The fallback workflow was hands-on investigation.** P01 described tracing the code, checking documentation and Git history, reading tests, reproducing behavior, and testing assumptions before changing anything.
- **Trust depends on inspectable evidence.** After CodeArchaeologist was introduced, P01 emphasized exact commit/PR links, visible confidence, and a clear refusal when evidence was insufficient. This is concept feedback after the idea was disclosed—not proof of adoption.

#### Preliminary Insight Ledger

| Insight | Origin | Type | Confidence | Product implication |
|---|---|---|---|---|
| Understanding how modules and request/data flow connect can be harder than understanding individual functions. | P01 transcript | Participant-reported experience | **Low** — one participant | Keep repository and architecture context visible alongside historical rationale. |
| Git history may identify a change without explaining why it was made. | P01 transcript | Participant-reported experience | **Low** — one participant | Prioritize linking an answer to the relevant commit, PR, issue, and source excerpt. |
| A useful explanation must be verifiable; a confident but unsupported explanation could be misleading. | P01 transcript, including concept feedback | Reported trust requirement | **Preliminary** — concept was introduced | Make sources and uncertainty visible, and preserve the `no_evidence` refusal behavior. |

#### What this interview changes

The first conversation gives a concrete example to investigate further: the problem may include both **understanding system-level flow** and **recovering the rationale behind a particular design choice**. That suggests the product should connect historical evidence to repository context rather than return a standalone explanation.

This interview does **not** establish how common the problem is, quantify time saved, prove willingness to adopt the product, or validate PMF. Further interviews must test whether these themes recur independently.

### Validation threshold

A practical first threshold is:

> **At least 3 of 5 eligible developers independently describe a recurring difficulty in recovering historical rationale, and at least 3 of 5 say source-backed historical context would be useful in that workflow.**

This is a **future validation criterion, not a completed result**.

---

### Second Exploratory Interview — P02

| Interview detail | Record |
|---|---|
| **Participant** | P02 (anonymized) |
| **Format** | Exploratory developer conversation; supplied notes cover workflow, trust, and concept feedback |
| **Date** | Not recorded in the notes supplied for this participant |
| **Role / employer** | Not specified; not inferred |
| **Evidence source** | Responses shared by the project owner |

#### What P02 described

- **Tests and Git history are useful but incomplete.** P02 said tests help clarify expected behavior, while commit messages sometimes fail to explain the reason behind a design decision. When the context remains unclear, the participant tries to understand impact and test assumptions before making a change.
- **Historical context takes searching across repository artifacts.** P02 described needing to move across commits, PRs, and discussions to connect code with the reason it was written that way.
- **Source links alone are a starting point, not the whole experience.** P02 wanted a concise explanation, relevant discussion, and a link back to the actual code so they would not have to read an entire PR for one detail.
- **The main failure mode is a convincing but unsupported explanation.** P02 raised the risk of treating a related commit as proof of the real reason, especially when old discussions are incomplete or outdated. They wanted the system to distinguish evidence from inference and refuse when evidence is insufficient.
- **Concept feedback was positive but prompted.** After the tool was introduced, P02 said the idea could be useful. Because this response followed the product explanation, it is recorded as concept feedback—not evidence of actual usage or adoption.

#### P02's contribution to the Insight Ledger

| Insight | Origin | Type | Confidence | Product implication |
|---|---|---|---|---|
| Tests help establish expected behavior, but may not explain why a design choice was made. | P02 interview notes | Participant-reported workflow | **Low** — one participant | Treat tests as useful context, not a substitute for historical rationale. |
| Finding rationale can require jumping across commits, PRs, and discussions. | P02 interview notes | Participant-reported friction | **Low** — one participant | Present a connected source trail and concise, traceable excerpts. |
| A related source must not be presented as proof unless it supports the claim. | P02 interview notes, including concept feedback | Reported trust requirement | **Preliminary** — concept was introduced | Clearly separate evidence from inference; refuse when support is insufficient or ambiguous. |

#### What changes after P02

P02 reinforces several themes also present in P01's account: commit history may explain *what* changed without explaining *why*, and evidence needs to be easy to inspect. P02 adds a useful emphasis on linking the explanation back to the relevant code and treating tests as context for expected behavior.

These were **early cross-interview signals, not robust recurring findings**. At that stage only two participants had been recorded, and P02's notes were partial. The positive reaction to the concept did not prove adoption or PMF.

### Third Exploratory Interview — P03

| Interview detail | Record |
|---|---|
| **Participant** | P03 (anonymized) |
| **Format** | Exploratory developer conversation; the supplied excerpt covers workflow-improvement, trust, and post-concept-feedback questions |
| **Date** | Not supplied |
| **Role / employer** | Not specified; not inferred |
| **Evidence source** | Responses shared by the project owner |
| **Completeness note** | The excerpt begins at the question about what could be easier and does not include answers to questions 1–7 or a concrete past incident. No specific time cost or past outcome is inferred. |

P03's supplied wording included:

> “I wouldn't want another tool that just summarizes everything without actually helping me find the source.”
>
> “If there's no clear evidence for a design decision, it should say that rather than generate a convincing explanation based on guesses.”
>
> “I wouldn't want to add another tool to my workflow unless it genuinely saves me time.”

These statements come from the supplied excerpt; the source/trust and tool-adoption comments were made during the later interview discussion, including after the concept was introduced.

#### What P03 described

- **The current workflow feels fragmented.** P03 described jumping between code, Git history, PRs, and issues, and wanted searching across these artifacts to start from the code itself.
- **The preferred result is a connected evidence trail, not a summary alone.** P03 described an ideal flow of selecting a function, seeing relevant history, receiving a short explanation, and opening the original discussions and code.
- **A PR discussion was considered more informative than a commit alone.** P03 said the discussion may reveal trade-offs, while a commit may show what changed without establishing why. The participant preferred a combination of PR/commit, discussion, and relevant current code.
- **Historical rationale must be checked against the current code.** P03 specifically raised the possibility that an old explanation may no longer apply after later changes.
- **Inference must be labeled and missing evidence acknowledged.** P03 wanted the tool to state when it could not find a clear reason rather than generate a plausible story from guesses.
- **Usefulness depends on a real workflow advantage.** After the concept was introduced, P03 identified unfamiliar codebases and legacy logic as possible use cases, but said ordinary changes may not justify a separate tool. Results must be fast, relevant, easy to verify, and worth the setup cost.
- **Demand remains uncertain.** In closing concept feedback, P03 explicitly questioned how often developers would need a dedicated product versus GitHub search or their normal debugging workflow. This is prompted concept feedback, not evidence of adoption.

#### P03's contribution to the Insight Ledger

| Insight | Origin | Type | Confidence | Product implication |
|---|---|---|---|---|
| Connecting code to its history can require searching across separate repository artifacts. | P03 supplied excerpt | Participant-reported friction | **Low** — one participant; excerpt is partial | Let users begin from a code location and connect relevant commits, PRs, issues, and discussions. |
| A useful rationale needs evidence plus current-code context; a commit link by itself may not establish why. | P03 supplied excerpt | Reported trust and workflow requirement | **Low** — one participant; concept discussion included | Show the most relevant source discussion alongside the changed code and make the relationship to the current code inspectable. |
| A system should label inference, acknowledge missing rationale, and avoid inventing an explanation. | P03 supplied excerpt, including post-concept discussion | Reported trust requirement | **Preliminary** — stated in a concept-focused section | Separate source-backed claims from inference and preserve the `no_evidence` behavior. |
| Adoption depends on being faster and easier than the existing workflow, not merely producing a plausible answer. | P03 supplied excerpt, including post-concept discussion | Reported adoption condition / concept feedback | **Preliminary** — concept was introduced | Measure end-to-end time and verification effort; test whether GitHub search or current debugging habits already solve the need. |

#### What changes after P03

P03 adds specificity to the workflow hypothesis: developers may want to start from a function and retrieve a linked chain of historical context, including discussion and current code—not just receive a standalone summary. P03 also raises a key counter-hypothesis that should remain open: the pain may be real but too infrequent, or existing GitHub search may be good enough to reduce demand for a dedicated tool.

Across P01–P03, source traceability and caution about unsupported explanations appear in all three supplied accounts, while the detailed workflow and context needs differ. This is a **preliminary cross-interview signal**, not proof that the problem is widespread. P02 and P03 excerpts are partial, several trust statements occurred after the concept was introduced, and no adoption, time-saved, or willingness-to-pay behavior has been demonstrated.

## Earlier Simulated Conversations

Three AI-generated conversations from an earlier session were used only to rehearse interview questions. They remain separate from the reported P01, P02, and P03 conversations and are **not real participants, findings, quotes, or validation**. They do not contribute to the Insight Ledger.


## First-Time Tester Feedback — T01

T01 is a first-time tester separate from P01–P03. Their date, experience, and background were not supplied. The tester liked the interface and concept, but the **actual task-level report is incomplete**. T01 clarified that a later message describing all four tasks as completed independently was hypothetical, not a new test attempt; it must not be counted as observed usability evidence.

### Actual task-level status

| Stranger-test task | Actual reported status | What is known |
|---|---|---|
| 1. Ask a question in the app | **Completed independently** | T01 said AI Chat and Investigate were easy enough to find. |
| 2. Find an answer explaining a historical design decision | **Could not complete** | T01 said they explored the interface but did not complete this interaction end to end. |
| 3. Open original source links and check the explanation | **Not tested** | No observed source-opening or claim-verification result is available. |
| 4. Test a question with little/no expected historical evidence | **Not tested** | T01 explicitly clarified they had not verified the app’s actual response. Their comments about ideal no-evidence behavior are preferences, not an observed result. |

**Scoring:** 1/4 tasks were completed independently. The proposed criterion is at least 3/4, so the criterion is **not met**. Because tasks 3–4 were not tested, this is an incomplete usability test—not proof that those features fail. The hypothetical 4/4 response is excluded from the actual score.

### What the tester said

> “I also liked the overall interface—it feels clean and gives the project a proper developer-tool vibe.”
>
> “I'd genuinely be interested in using it on a real project to see how much time it saves.”
>
> “One small improvement I'd suggest is making the difference between AI Chat and Investigate a little more obvious for first-time users.”
>
> “My main suggestion would be to make the evidence and confidence level really clear so users can quickly tell what the history actually confirms versus what the AI is inferring.”

### Evidence-backed interpretation

- **Positive first impression:** T01 liked the interface and developer-tool presentation. This is qualitative feedback, not a usability pass.
- **Perceived value:** T01 could imagine using the concept on unfamiliar or legacy code. Their interest in testing it on a real project is not evidence of measured time savings or adoption.
- **Observed usability issue:** T01 completed the initial question task but could not complete the historical-answer task. The supplied notes do not identify the exact point of failure, so the cause is not inferred.
- **Session boundary:** source-link verification and the app’s response to a low-evidence question were not observed in this tester’s session.
- **UX suggestion:** make AI Chat versus Investigate easier to distinguish, potentially with a short example. This is one tester’s suggestion and should be checked with another first-time user before treating it as a broad issue.
- **Trust suggestion:** distinguish source-backed evidence from AI inference and make evidence/confidence easy to inspect. This is a desired behavior, not proof that the current UI handles the tested case correctly.
- **Time-saving is unmeasured:** T01 wants to evaluate the tool on a real project; no timing or comparison with the existing workflow was supplied.

**Design implication:** clarify the difference between AI Chat and Investigate with a short example, and make evidence, inference, and confidence easy to distinguish. These are product recommendations from one tester, not claims that the corresponding interaction has been validated. T01 is a tester feedback record, not an additional developer interview or PMF proof.

---

## Evidence Snapshot

| Area | Current record |
|---|---|
| Problem, ICP, substitutes, and product mechanism | Documented as the current product hypothesis |
| Exploratory developer conversations | Three records (P01–P03); P02/P03 excerpts are partial |
| Insight Ledger | Preliminary synthesis across P01–P03, with confidence labels |
| Assumption tests | Test designs and pass/inconclusive/fail bands documented; no outcomes are represented as observed |
| First-time usability | T01 independently completed 1/4 tasks; task 2 could not be completed; tasks 3–4 were not tested |
| Opportunity sizing | Source-backed ecosystem boundary plus clearly labelled assumption-based scenarios in `RESEARCH_EVIDENCE.md` |
| Technical benchmarks | README-reported results; exact commands and execution boundary documented in `TECHNICAL_VALIDATION.md` |

### Opportunity Sizing — Scenario Model

The source register in `RESEARCH_EVIDENCE.md` uses GitHub's published **225M+ developers** as a broad ecosystem ceiling, not as a count of qualified buyers. The same file cites the 2025 Stack Overflow survey's AI-output trust finding as context for evidence-first design, not as proof of demand.

Because public sources do not quantify how many developers repeatedly need historical rationale, the model uses explicit sensitivity assumptions rather than presenting a fabricated market statistic:

| Scenario | Assumed share of broad GitHub developer baseline with recurring need | Scenario-defined users | Assumed 1% paid conversion | Annualised gross revenue at $8/user/month |
|---|---:|---:|---:|---:|
| Conservative | 0.001% | 2,250 | 23 seats | $2,208 |
| Planning case | 0.005% | 11,250 | 113 seats | $10,848 |
| Stretch case | 0.01% | 22,500 | 225 seats | $21,600 |

The $8 monthly price and the need-share/conversion rates are **assumptions, not research findings**. The resulting 23–225 paid seats and $2.2K–$21.6K annualised gross revenue are scenario outputs, not forecasts or validated TAM/SAM/SOM claims. The model is useful for showing which assumptions control the answer; it does not establish willingness to pay or product-market fit. See `RESEARCH_EVIDENCE.md` for sources and arithmetic.
### PMF Conclusion

The three exploratory conversations provide early examples of difficulty recovering historical rationale and make evidence traceability a candidate product requirement. P01 emphasized modules and request/data flow; P02 discussed tests and incomplete Git rationale; P03 described fragmented searching across repository artifacts and preferred links among discussion, commits, and current code. P02/P03 notes are partial, and some trust or usefulness comments followed the concept introduction. P03 also raised a counter-hypothesis: GitHub search or normal debugging workflows may be sufficient for many changes.

The current evidence supports a preliminary problem hypothesis, not a market-wide conclusion. T01 independently completed 1/4 tasks, could not complete the historical-answer task, and did not test source verification or the no-evidence response; a later 4/4 description was hypothetical and is excluded. The proposed ≥3/4 criterion was not met in the reported session. No measured time saved, willingness-to-pay, or adoption result is claimed.

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

## Technical Validation Record

The public landing page loaded during the final review and showed the `pallets/flask` label plus Repository, AI Chat, Investigate, and Decisions navigation. This is a page-level observation only; no end-to-end question was submitted.

The repository README defines these commands:

```bash
cd backend && pytest
cd backend && python3 -m app.eval
cd backend && python3 -m app.smoke
cd frontend && npx tsc --noEmit
```

The repository source tree was not mounted in the working folder, and this environment could not resolve `github.com` when a checkout was attempted. Those commands therefore were not executed for this package. See `TECHNICAL_VALIDATION.md` for the distinction between observed, README-reported, and unexecuted checks. No fresh test result is inferred.

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
| Human / AI review record | The project README documents automated unit, benchmark, and smoke-check methods; a separate AI-review transcript is not part of this assessment pack |
| **Stranger-test observation** | **1/4 tasks independently completed in the reported session; 2 were not tested** |

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

# Evidence Boundary

The implementation is built and deployed. The documentation includes three exploratory developer conversations, a preliminary Insight Ledger, the T01 first-time tester report, proposed assumption-test criteria, and README-reported technical evaluation results. These evidence types answer different questions: automated benchmarks assess selected system behaviors, interviews reveal reported experiences and preferences, and observed usability tasks show what one first-time tester actually completed. They should not be treated as interchangeable proof of product-market fit.

T01's recorded result is 1/4 tasks independently completed; the historical-answer task could not be completed, and source verification and the no-evidence path were not tested. A later 4/4 message was explicitly hypothetical, not a retest, and is excluded. The project therefore makes no claim that the proposed usability threshold was achieved.

> **Implementation completion ≠ product validation.**

---

# The Through-Line

We started with a developer problem, not an AI feature.

We asked where AI could help, kept judgment human-owned, challenged the assumption that fluent answers are trustworthy, and built the product around a simple rule:

> **Make the answer easier to check, not merely easier to believe.**

The technical implementation is built and deployed; the available automated test metrics remain README-reported in this assessment pack.

## Assessment artifacts

- `PROJECT_SPEC.md` — product contract and implementation boundaries.
- `RESEARCH_EVIDENCE.md` — source register, evidence labels, and opportunity-sizing assumptions.
- `TECHNICAL_VALIDATION.md` — repository test commands and the exact scope of the final review.
