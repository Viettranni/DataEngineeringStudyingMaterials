# Learning Data Engineering

A hands-on course built around one running project: the data platform for a
small (fictional) coffee shop chain. Each module adds a real piece to it, so by
the end you have an end-to-end pipeline you understand line by line.

## How this works

1. Open the module's `README.md` and read the concepts (10-15 minutes).
2. Do the exercise. You write the code; the skeleton only marks where.
3. Run the module's `check.py` to see whether your result is right.
4. Ask Claude to review your work, give a hint, or start the next module.

## Setup

```bash
source .venv/bin/activate              # every new terminal
python scripts/generate_raw_data.py    # (re)creates data/raw/
python scripts/sql.py "SELECT 1"       # run any query against the warehouse
```

## Roadmap

| #  | Module                  | You learn                                              | You build                                  |
|----|-------------------------|--------------------------------------------------------|--------------------------------------------|
| 01 | Foundations             | ETL, data layers, idempotency                          | A CSV -> DuckDB pipeline in plain Python   |
| 02 | SQL and data modeling   | ELT, joins, window functions, star schemas             | The same pipeline in SQL, plus fact/dim tables |
| 03 | Ingestion               | APIs, pagination, incremental loads, schema drift      | An extractor that only pulls what is new   |
| 04 | Storage and formats     | Row vs columnar, Parquet, partitioning, data lakes     | A partitioned Parquet lake                 |
| 05 | Transformation with dbt | Models, lineage, tests, documentation                  | A dbt project over the warehouse           |
| 06 | Orchestration           | Scheduling, dependencies, retries, backfills           | A scheduled DAG running in Docker          |
| 07 | Data quality            | Testing pipelines, data contracts, monitoring          | Checks that stop bad data before it lands  |
| 08 | Streaming               | Events, logs, consumers, batch vs stream               | A small Kafka-style event pipeline         |
| 09 | Cloud and warehouses    | Cloud storage, warehouses, cost, infrastructure as code | The pipeline deployed to a cloud warehouse |
| 10 | Capstone                | Designing a platform end to end                        | A portfolio project on a dataset you pick  |

## Progress

- [x] 01 Foundations
- [ ] 02 SQL and data modeling
- [ ] 03 Ingestion
- [ ] 04 Storage and formats
- [ ] 05 Transformation with dbt
- [ ] 06 Orchestration
- [ ] 07 Data quality
- [ ] 08 Streaming
- [ ] 09 Cloud and warehouses
- [ ] 10 Capstone

## Layout

```
modules/     one folder per module: lesson, exercise skeleton, checker
scripts/     shared helpers (raw data generator, sql.py to run queries)
data/raw/        source files exactly as they arrived (never edited by hand)
data/warehouse/  the DuckDB database your pipelines write to
```

Everything under `data/` is git-ignored: data is rebuilt by code, not stored in git.
