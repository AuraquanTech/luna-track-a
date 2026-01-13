\
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class LunaError(Exception):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    retryable: bool = False

    def to_payload(self) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details or {},
                "retryable": self.retryable,
            }
        }


def error_payload(code: str, message: str, *, details: Optional[Dict[str, Any]] = None, retryable: bool = False) -> Dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "retryable": retryable,
        }
    }
