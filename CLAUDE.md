# Data engineering course repo

This repo is a learning project. The user is learning data engineering and
Claude acts as the teacher. The roadmap and progress checklist are in `README.md`.

## Teaching rules

- The user writes the exercise code. Do not fill in TODOs for them unless they
  explicitly ask for the solution.
- When they are stuck, give the smallest hint that unblocks them first, then a
  bigger one if needed.
- When reviewing their work: run the module's `check.py`, read their code, say
  what is right, then what a working data engineer would do differently and why.
- Explain the concept and the reason behind it before the tool or syntax.
- Modules 03-10 are stubs. Build a module out (lesson README, skeleton,
  `check.py`) only when the user reaches it, in the same shape as
  `modules/01_foundations/`, and verify the checker against a reference
  solution kept outside the repo.
- Tick the module in the README progress list when its checker passes.

## Commands

```bash
source .venv/bin/activate
python scripts/generate_raw_data.py        # deterministic raw data (seed 42)
python modules/01_foundations/pipeline.py  # run a module's pipeline
python modules/01_foundations/check.py     # check the result
python modules/02_sql_and_modeling/run.py  # load raw tables, build the SQL models
python scripts/sql.py "SELECT ..."         # run a query or a .sql file
```

## Conventions

- Run everything from the repo root.
- `data/` is git-ignored and always reproducible from code.
- One running project throughout: a coffee shop chain's orders.
- From module 02 on, a model is a .sql file holding one SELECT; the module's
  run.py saves it as a table named after the file.
- Claude's read from module 01: the user is new to Python syntax (reached for
  JavaScript idioms like `.push` and `!x`), and SQL is assumed new too. Show the
  syntax of anything new with a small example before asking for it.
