# Neo4j Schema

## Nodes
- `File`: `key`, `repo`
- `Commit`: `sha`, `message`, `date`, `author_login`, `url`
- `PR`: `number`, `title`, `body`, `created_at`, `merged_at`, `author_login`, `url`
- `Issue`: `number`, `title`, `body`, `created_at`, `author_login`, `url`
- `Person`: `login`
- `Decision`: `id`, `summary`, `rationale`, `tradeoffs`, `confidence`, `source_type`, `source_id`, `source_url`, `evidence_snippet`, `person_login`, `decision_date`

## Relationships
- Commit -> MODIFIES -> File
- Commit/PR/Issue -> AUTHORED -> Person
- Decision -> JUSTIFIES -> PR/Issue/Commit

Every Decision retains provenance so the UI can always open the original source.
