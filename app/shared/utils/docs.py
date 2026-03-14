"""Shared utilities for OpenAPI endpoint documentation."""

from typing import Any

from app.core.exceptions.exceptions import BaseAppException
from app.shared.schemas import ErrorResponse


def error_response(
    *exceptions: type[BaseAppException],
    description: str = "",
) -> dict[str, Any]:
    """Build an OpenAPI response entry from one or more exception classes.

    Single exception  → uses ``example`` with the class-level detail.
    Multiple exceptions → uses ``examples`` with one named entry each.
    """
    if len(exceptions) == 1:
        exc = exceptions[0]
        return {
            "model": ErrorResponse,
            "description": description or exc.detail,
            "content": {
                "application/json": {
                    "example": {
                        "detail": exc.detail,
                        "status_code": exc.status_code,
                    },
                },
            },
        }

    examples: dict[str, Any] = {}
    for exc in exceptions:
        examples[exc.__name__] = {
            "summary": exc.__name__,
            "value": {
                "detail": exc.detail,
                "status_code": exc.status_code,
            },
        }

    return {
        "model": ErrorResponse,
        "description": description,
        "content": {
            "application/json": {
                "examples": examples,
            },
        },
    }
