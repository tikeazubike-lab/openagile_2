Continue HO-160 §12. The first brief is `docs/handovers/HO-160-brief-builder-s12.md`; read only its STEPS.
STATE (do not redo):
- Step 1 is DONE: `51c8fcc6057ab3947b059202ba6a1f8b7b54a413` (RED tests). Do not change those tests.
- Your half-finished step 2 is committed as `1f5e19e98c51dda06e96ae0a9af97cd67d1f71d1`. Unit state: 41 failed, 165 passed.
DO NOT query documentation, Context7 or the web. Do not re-read the whole spec: §12 is the only section you need. Spend no time re-planning.
Run only the F-026c unit file while you iterate:
  from backend/: DATABASE_URL=postgresql+asyncpg://nobody@127.0.0.1:1/none /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/backend/.venv/bin/python -m pytest tests/unit/test_import_registrar_research.py -q -p no:cacheprovider -x
1. Finish step 2 until that file passes. Commit `fix(f-026c): §12 D-1..D-6`.
2. Step 3 (integration test edits, do not run them). Commit.
3. Full unit suite (drop the filename and `-x`); paste the raw summary line.
Commit messages end with `Co-Authored-By: OpenCode <noreply@opencode.ai>`. REPORT: 40-char SHAs, raw summary line, any assertion changed.
