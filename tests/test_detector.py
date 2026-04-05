import pandas as pd
import numpy as np
import pytest
from src.pipeline.detector import DataQualityDetector

@pytest.fixture
def sample_df():
    np.random.seed(42)
    df = pd.DataFrame({
        "age": [25, 30, np.nan, 200, 35, 28, np.nan],
        "name": ["Alice", "Bob", "Carol", "Alice", None, "Dave", "Eve"],
        "score": [0.9, 0.85, 0.78, 0.92, np.nan, 0.88, 0.91],
    })
    return df

def test_detects_missing(sample_df):
    d = DataQualityDetector()
    report = d.detect(sample_df)
    missing = [i for i in report.issues if i.issue_type == "missing_values"]
    assert len(missing) > 0

def test_detects_outliers(sample_df):
    d = DataQualityDetector()
    report = d.detect(sample_df)
    outliers = [i for i in report.issues if i.issue_type == "outliers"]
    assert any(i.column == "age" for i in outliers)

def test_quality_score_range(sample_df):
    d = DataQualityDetector()
    report = d.detect(sample_df)
    assert 0 <= report.total_score <= 100
