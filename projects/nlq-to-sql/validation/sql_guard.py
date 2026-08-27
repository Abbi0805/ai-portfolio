"""Read-only guard for LLM-generated SQL.

Contract: the caller MUST execute the string returned by `validate_sql`, never
the query it passed in. Validating a query that has already run is logging,
not a control.
"""

import sqlparse
from sqlparse import tokens as T

MAX_ROWS = 100


def validate_sql(query: str) -> str:
    """Return an executable, read-limited version of `query`.

    Raises ValueError if the input is not exactly one SELECT statement.
    Fails closed: anything sqlparse cannot classify as SELECT is rejected,
    including CTEs (`WITH ... SELECT`), which sqlparse reports as UNKNOWN.
    """
    statements = [s for s in sqlparse.parse(query) if str(s).strip(" \t\r\n;")]

    if not statements:
        raise ValueError("Empty query.")
    if len(statements) > 1:
        raise ValueError(
            f"Only a single statement is allowed, got {len(statements)}."
        )

    statement = statements[0]
    if statement.get_type() != "SELECT":
        raise ValueError(
            f"Only SELECT statements are allowed, got {statement.get_type()}."
        )

    safe = str(statement).strip().rstrip(";").strip()
    if not _has_row_limit(statement):
        safe += f" LIMIT {MAX_ROWS}"
    return safe


def _has_row_limit(statement) -> bool:
    """True if the statement carries a LIMIT clause at its top level.

    Deliberately not `"limit" in query.lower()`: a column named `credit_limit`
    would silently disable the row cap. Deliberately top-level only: a LIMIT
    inside a subquery does not bound the outer result set.
    """
    return any(
        token.ttype is T.Keyword and token.normalized.upper() == "LIMIT"
        for token in statement.tokens
    )
