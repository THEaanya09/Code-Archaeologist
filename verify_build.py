from __future__ import annotations

import ast
from pathlib import Path

root = Path(__file__).resolve().parent
files = sorted((root / "app").glob("*.py"))
errors = []
for path in files:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        errors.append(f"{path}: {exc}")

print(f"Checked {len(files)} Python files")
if errors:
    for error in errors:
        print(error)
    raise SystemExit(1)
print("Python syntax OK")
