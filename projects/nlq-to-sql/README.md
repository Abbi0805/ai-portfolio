# nlq-to-sql

Natural-language analytics that turns business questions into validated SQL, runs them against a relational database, and explains the result in plain business language.

## Problem

LLM "chat-with-your-data" demos break in production:
- generated SQL writes to the database
- no schema grounding — hallucinated columns, runaway queries
- raw result tables, no business interpretation

## Solution

Deterministic pipeline that constrains the LLM to one validated step at a time:

1. **NL → SQL chain** with schema-grounded prompt
2. **Guardrail layer** — runs *before* execution: rejects anything that is not
   exactly one SELECT statement, then enforces a row cap
3. **DuckDB execution** — fast analytical engine, no production DB required
4. **Result → text chain** — explains the answer using the question, the SQL, and the result rows

## Architecture

```
question
   │
   ▼
NL → SQL chain ──► sqlparse guard ──► reject: nothing is executed
   │
   ▼ validated SQL (row cap applied)
DuckDB execution
   │
   ▼ result rows
Result → text chain (question + sql + rows)
   │
   ▼
business explanation
```

## Stack

Python 3.11 · LangChain · Azure OpenAI (GPT-4o) · DuckDB · sqlparse · Faker (synthetic data)

## Guardrail behaviour

The guard is an executable specification, not a description. Run it without
credentials or a database:

```bash
python validation/test_sql_guard.py
```

| Input | Outcome |
|---|---|
| `DELETE` / `UPDATE` / `INSERT` / `DROP` / `CREATE` | rejected, nothing executed |
| `SELECT 1; DROP TABLE customers` | rejected — statement chains are not allowed |
| `SELECT * FROM customers` | `LIMIT 100` appended |
| `SELECT * FROM t WHERE credit_limit > 100` | `LIMIT 100` appended — a column name containing "limit" does not disable the cap |
| `SELECT * FROM (SELECT * FROM big LIMIT 1) x` | `LIMIT 100` appended — a subquery LIMIT does not bound the outer result |
| `SELECT * FROM t LIMIT 5` | passed through unchanged |

Two limits worth stating plainly:

- **CTEs are rejected.** `WITH ... SELECT` is reported as `UNKNOWN` by sqlparse,
  and the guard fails closed rather than guessing.
- **"SELECT-only" is not the same as "safe".** A legitimate read query can still
  be expensive or surface data the caller should not see. Row caps and statement
  limits bound the blast radius; they do not replace least-privilege database
  credentials.

Latency and cost per question are not measured yet.

## Run

```bash
pip install -r requirements.txt

# Initialise a minimal demo database
python db/init_db.py

# Or generate a larger synthetic analytics dataset
python db/generate_data.py

# Configure Azure OpenAI credentials
cp .env.example .env  # then fill in the values

python app.py
```

### Required environment variables

```env
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_DEPLOYMENT=<your-deployment-name>
AZURE_OPENAI_API_VERSION=2024-02-15-preview  # optional, default shown
```

### Example questions

- "What is the revenue per region?"
- "Which products generate the highest revenue?"
- "Who are the top 5 customers by order value?"
- "How did revenue evolve over time?"

## Project structure

```
nlq-to-sql/
├── app.py                  # CLI entry point
├── chains/
│   ├── nl_to_sql.py        # NL → SQL chain
│   └── sql_to_text.py      # SQL result → explanation
├── config/
│   └── settings.py
├── db/
│   ├── analytics.db        # DuckDB database
│   ├── init_db.py          # minimal demo dataset
│   └── generate_data.py    # synthetic analytics dataset
├── prompts/
│   ├── nl_to_sql.txt
│   └── sql_to_text.txt
└── validation/
    ├── sql_guard.py        # SELECT-only guard, runs before execution
    └── test_sql_guard.py   # executable spec, no credentials needed
```

## Design choices

- **Deterministic chains, not autonomous agents** — analytical Q&A needs predictable behavior, not exploration loops.
- **DuckDB instead of Postgres in the demo** — analytical engine, zero setup, drop-in replaceable with Postgres / Snowflake.
- **Result explanation is its own chain** — keeps the SQL prompt focused; the explanation prompt can be tuned per audience (analyst vs. executive).
