# Technical Validation Record — CodeArchaeologist

**Review date:** 19 October 2026

## Source and deployment inspection

- Public source repository: https://github.com/THEaanya09/Code-Archaeologist
- Live frontend: https://code-archaeologist-tau.vercel.app/
- The deployed landing page loaded during review, showing the repository label `pallets/flask` and navigation for AI Chat, Investigate, and Decisions.
- The README defines the evaluation commands and reports its results. The application was not interacted with end-to-end during this review; the landing page observation is not an API, source-verification, or `no_evidence` test.

## Repository-defined commands

Run from a local clone of the repository, with its dependencies and required credentials configured.

### Backend unit tests

```bash
cd backend
pytest
```

The README reports **28 passing tests across 8 test modules**. This report was not independently reproduced in the current working environment.

### Classifier and retrieval evaluation

```bash
cd backend
python3 -m app.eval
```

The README reports classifier accuracy of **44/45 (97.8%)** and golden retrieval matches of **25/25**. These are repository-reported metrics, not fresh execution results for this package.

### Live smoke checks

```bash
cd backend
python3 -m app.smoke
```

This command may require configured backend services and valid environment variables for Neo4j and model providers.

### Frontend TypeScript check

```bash
cd frontend
npx tsc --noEmit
```

The repository README recommends this check before pushing. No fresh TypeScript output is claimed in this package.

## Execution boundary for this package

The repository source tree was not present in the local working folder. A source checkout was attempted, but the environment could not resolve `github.com`; therefore the backend suite, evaluation command, smoke checks, and frontend TypeScript check could not be executed here. No test pass is inferred from this access failure. The README-reported metrics remain useful project evidence, but they remain labelled as reported rather than independently verified.

## What the current evidence establishes

- The public landing page was reachable during inspection.
- The repository README documents reproducible commands and reports evaluation/test numbers.
- This review does **not** independently establish backend health, live LLM/Neo4j connectivity, end-to-end historical answer quality, source-link correctness, or actual `no_evidence` behavior.
