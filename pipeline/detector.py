import pandas as pd
import numpy as np
from typing import Dict, Any, List
from dataclasses import dataclass, field

@dataclass
class QualityIssue:
    issue_type: str
    column: str
    severity: str          # low | medium | high | critical
    count: int
    pct: float
    details: str = ""

@dataclass
class DetectionReport:
    issues: List[QualityIssue] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)

    def add(self, issue: QualityIssue):
        self.issues.append(issue)

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "critical")

    @property
    def total_score(self) -> float:
        """Quality score 0–100 (higher = better)"""
        if not self.issues:
            return 100.0
        penalty = sum({"low": 1, "medium": 3, "high": 7, "critical": 15}.get(i.severity, 0)
                      for i in self.issues)
        return max(0.0, 100.0 - penalty)


class DataQualityDetector:
    def __init__(self, config=None):
        self.missing_threshold = getattr(config, "missing_threshold", 0.05)
        self.outlier_method = getattr(config, "outlier_method", "iqr")
        self.outlier_threshold = getattr(config, "outlier_threshold", 1.5)
        self.cardinality_threshold = getattr(config, "cardinality_threshold", 50)

    def detect(self, df: pd.DataFrame) -> DetectionReport:
        report = DetectionReport()
        n = len(df)

        self._check_missing(df, report, n)
        self._check_duplicates(df, report, n)
        self._check_outliers(df, report, n)
        self._check_cardinality(df, report)
        self._check_type_issues(df, report)

        report.summary = {
            "rows": n,
            "columns": len(df.columns),
            "total_issues": len(report.issues),
            "quality_score": round(report.total_score, 1),
            "missing_cells": int(df.isnull().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum()),
        }
        return report

    def _check_missing(self, df, report, n):
        for col in df.columns:
            miss = df[col].isnull().sum()
            if miss == 0:
                continue
            pct = miss / n
            severity = "critical" if pct > 0.5 else "high" if pct > 0.2 else "medium" if pct > self.missing_threshold else "low"
            report.add(QualityIssue("missing_values", col, severity, int(miss), round(pct * 100, 2),
                                    f"{miss} missing ({pct*100:.1f}%)"))

    def _check_duplicates(self, df, report, n):
        dupes = df.duplicated().sum()
        if dupes > 0:
            pct = dupes / n
            severity = "high" if pct > 0.1 else "medium"
            report.add(QualityIssue("duplicate_rows", "ALL", severity, int(dupes), round(pct * 100, 2),
                                    f"{dupes} duplicate rows ({pct*100:.1f}%)"))

    def _check_outliers(self, df, report, n):
        numeric = df.select_dtypes(include=[np.number]).columns
        for col in numeric:
            series = df[col].dropna()
            if len(series) < 4:
                continue
            if self.outlier_method == "iqr":
                q1, q3 = series.quantile(0.25), series.quantile(0.75)
                iqr = q3 - q1
                mask = (series < q1 - self.outlier_threshold * iqr) | (series > q3 + self.outlier_threshold * iqr)
            else:
                z = np.abs((series - series.mean()) / series.std())
                mask = z > 3
            count = mask.sum()
            if count > 0:
                pct = count / n
                severity = "high" if pct > 0.05 else "medium" if pct > 0.01 else "low"
                report.add(QualityIssue("outliers", col, severity, int(count), round(pct * 100, 2),
                                        f"{count} outliers ({pct*100:.1f}%)"))

    def _check_cardinality(self, df, report):
        for col in df.select_dtypes(include=["object", "category"]).columns:
            n_unique = df[col].nunique()
            if n_unique > self.cardinality_threshold:
                report.add(QualityIssue("high_cardinality", col, "low", n_unique, 0.0,
                                        f"{n_unique} unique values"))

    def _check_type_issues(self, df, report):
        for col in df.select_dtypes(include=["object"]).columns:
            sample = df[col].dropna().head(200)
            numeric_like = pd.to_numeric(sample, errors="coerce").notna().sum()
            if len(sample) > 0 and numeric_like / len(sample) > 0.8:
                report.add(QualityIssue("type_mismatch", col, "medium", int(numeric_like), 0.0,
                                        "Stored as string but looks numeric"))
