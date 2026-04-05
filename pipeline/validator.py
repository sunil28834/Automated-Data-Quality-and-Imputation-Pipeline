import pandas as pd
import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass, field

@dataclass
class ValidationResult:
    passed: bool
    rule: str
    column: str
    details: str = ""
    failed_count: int = 0

class DataValidator:
    def __init__(self, config=None):
        self.rules: List[Dict[str, Any]] = []

    def add_range_rule(self, col: str, min_val=None, max_val=None):
        self.rules.append({"type": "range", "column": col, "min": min_val, "max": max_val})

    def add_not_null_rule(self, col: str):
        self.rules.append({"type": "not_null", "column": col})

    def add_regex_rule(self, col: str, pattern: str):
        self.rules.append({"type": "regex", "column": col, "pattern": pattern})

    def validate(self, df: pd.DataFrame) -> List[ValidationResult]:
        results = []
        for rule in self.rules:
            col = rule["column"]
            if col not in df.columns:
                results.append(ValidationResult(False, rule["type"], col, "Column not found"))
                continue
            if rule["type"] == "not_null":
                fail = df[col].isnull().sum()
                results.append(ValidationResult(fail == 0, "not_null", col,
                                                f"{fail} nulls found", int(fail)))
            elif rule["type"] == "range":
                series = pd.to_numeric(df[col], errors="coerce")
                mask = pd.Series([False] * len(df))
                if rule.get("min") is not None:
                    mask |= series < rule["min"]
                if rule.get("max") is not None:
                    mask |= series > rule["max"]
                fail = mask.sum()
                results.append(ValidationResult(fail == 0, "range_check", col,
                                                f"{fail} values out of range [{rule.get('min')}, {rule.get('max')}]",
                                                int(fail)))
            elif rule["type"] == "regex":
                import re
                fail = df[col].dropna().apply(lambda x: not bool(re.match(rule["pattern"], str(x)))).sum()
                results.append(ValidationResult(fail == 0, "regex_check", col,
                                                f"{fail} values don't match pattern", int(fail)))
        return results
