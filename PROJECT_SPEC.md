# CodeArchaeologist - Project Specification

## Problem
New engineers, contributors, and maintainers can read what code does, but the reasoning behind historical design choices is often scattered across commits, pull requests, issues, comments, people, and dates. CodeArchaeologist reconstructs that reasoning as evidence-backed answers.

## Core flow
User question -> evidence retrieval -> graph traversal + semantic retrieval -> evidence assembly -> answer synthesis -> sources + people/date + graph path.

## MVP scope
One public repository: `pallets/flask`.

The MVP focuses on Files, Commits, PRs, Issues, People, and Decisions. It intentionally avoids multi-repository intelligence, large dashboards, and a fully autonomous repository-wide agent.

## Evidence rule
The LLM is a synthesis layer, not a source of historical facts. A Decision should carry a source type, source ID, URL, evidence snippet, and confidence. Weak evidence should lower confidence rather than trigger invention.

## Current ground truth
`data/golden_questions.json` contains 25 curated WHY questions. The project treats missing commit SHAs as legitimate when the source is issue-only or a non-merged discussion.

## Architecture
GitHub API/PyGithub -> cached raw data -> normalized JSON -> Neo4j AuraDB -> decision extraction -> retrieval -> GraphRAG answer layer -> FastAPI -> minimal web UI.

## Evaluation
The golden questions are replayed through `/ask`. Evaluation compares retrieved source URLs with the curated source URLs and records evidence-match rate, answer, and confidence.
