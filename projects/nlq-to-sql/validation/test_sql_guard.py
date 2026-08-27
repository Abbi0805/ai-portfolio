"""Executable specification for the SQL guard.

Runs without Azure credentials or a database:

    python validation/test_sql_guard.py

Every case below is a claim the README makes. If a claim stops being true,
this file fails -- which is the point. A guardrail that is only described in
documentation is not a guardrail.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from validation.sql_guard import MAX_ROWS, validate_sql

REJECTED = [
    ("write statement", "DELETE FROM customers"),
    ("write statement", "UPDATE customers SET name = 'x'"),
    ("write statement", "INSERT INTO customers VALUES (1)"),
    ("DDL", "DROP TABLE customers"),
    ("DDL", "CREATE TABLE t (id INT)"),
    ("statement chain", "SELECT 1; DROP TABLE customers"),
    ("statement chain", "SELECT * FROM t; DELETE FROM t;"),
    ("empty input", ""),
    ("whitespace only", "   \n  "),
]

LIMIT_ENFORCED = [
    ("plain select", "SELECT * FROM customers"),
    # A column whose name contains "limit" must not disable the row cap.
    ("limit-like column", "SELECT * FROM customers WHERE credit_limit > 100"),
    ("limit-like column", "select name from t where limit_reached = true"),
    # A LIMIT inside a subquery does not bound the outer result set.
    ("subquery limit", "SELECT * FROM (SELECT * FROM big LIMIT 1) x"),
]

LIMIT_PRESERVED = [
    ("explicit limit", "SELECT * FROM t LIMIT 5"),
    ("limit with offset", "SELECT * FROM t ORDER BY x LIMIT 5 OFFSET 2"),
    ("trailing semicolon", "SELECT * FROM t LIMIT 5;"),
]


def main() -> int:
    failures = []

    for label, query in REJECTED:
        try:
            result = validate_sql(query)
        except ValueError:
            continue
        failures.append(f"{label}: accepted {query!r} -> {result!r}")

    for label, query in LIMIT_ENFORCED:
        try:
            result = validate_sql(query)
        except ValueError as exc:
            failures.append(f"{label}: rejected valid query {query!r} ({exc})")
            continue
        if not result.endswith(f"LIMIT {MAX_ROWS}"):
            failures.append(f"{label}: no row cap applied to {query!r} -> {result!r}")

    for label, query in LIMIT_PRESERVED:
        try:
            result = validate_sql(query)
        except ValueError as exc:
            failures.append(f"{label}: rejected valid query {query!r} ({exc})")
            continue
        if result.count("LIMIT") != 1:
            failures.append(f"{label}: limit rewritten in {query!r} -> {result!r}")

    total = len(REJECTED) + len(LIMIT_ENFORCED) + len(LIMIT_PRESERVED)
    if failures:
        for failure in failures:
            print(f"FAIL  {failure}")
        print(f"\n{len(failures)} of {total} cases failed.")
        return 1

    print(f"{total} cases passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
