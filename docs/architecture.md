# Architecture

```text
GitHub API
   |
   v
raw cache -> normalized JSON
   |
   +----> Decision extraction
   |             |
   |             v
   +----------> Neo4j AuraDB
                  |
            lexical / optional vector retrieval
                  |
                  v
             evidence assembly
                  |
                  v
              local Qwen
                  |
                  v
          FastAPI /ask response
                  |
                  v
              minimal UI
```

The evidence boundary is intentional: retrieval happens before generation, and the answer generator receives only retrieved evidence.
