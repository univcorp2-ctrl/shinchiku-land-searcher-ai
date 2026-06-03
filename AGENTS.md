# Agent Guide

Use this repo as a CLI-first automation project. Keep commands reproducible and safe.

## Quality gate

```bash
ruff check .
pytest
```

## Safety boundary

Document-request automation must stop before final submission. The operator must review each site page and click final submit manually.
