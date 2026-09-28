# Evaluation

## Golden set
`data/golden_questions.json` contains 25 historical WHY questions.

## Run
```powershell
python -m app.eval
```

The harness records the expected source URLs, returned sources, confidence, mode, and answer in `data/processed/eval_results.json`.

## Hallucination check
Use the unsupported PostgreSQL/MongoDB question from `app/smoke.py`. It should return no evidence and low confidence.

## Manual review
For at least 10 questions, open the linked GitHub source and verify that the extracted rationale is actually supported by the source discussion.
