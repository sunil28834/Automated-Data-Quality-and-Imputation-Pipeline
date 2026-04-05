import pandas as pd
import numpy as np
from src.pipeline.imputer import DataImputer
from src.utils.config import PipelineConfig

def test_no_missing_after_impute():
    df = pd.DataFrame({"a": [1.0, np.nan, 3.0], "b": ["x", None, "z"]})
    cfg = PipelineConfig(numeric_strategy="mean", categorical_strategy="mode")
    imputer = DataImputer(cfg)
    result = imputer.impute(df)
    assert result.isnull().sum().sum() == 0

def test_knn_impute():
    df = pd.DataFrame({"a": [1.0, 2.0, np.nan, 4.0], "b": [10.0, 20.0, 30.0, 40.0]})
    cfg = PipelineConfig(numeric_strategy="knn", knn_neighbors=2)
    imputer = DataImputer(cfg)
    result = imputer.impute(df)
    assert not result["a"].isnull().any()
