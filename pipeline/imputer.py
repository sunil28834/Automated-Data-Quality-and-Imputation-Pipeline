import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import KNNImputer, IterativeImputer
from sklearn.preprocessing import LabelEncoder

class DataImputer:
    def __init__(self, config=None):
        self.numeric_strategy = getattr(config, "numeric_strategy", "knn")
        self.categorical_strategy = getattr(config, "categorical_strategy", "mode")
        self.knn_neighbors = getattr(config, "knn_neighbors", 5)
        self.constant_fill = getattr(config, "constant_fill", "UNKNOWN")
        self.iterative_max_iter = getattr(config, "iterative_max_iter", 10)
        self.imputation_log: Dict[str, Any] = {}

    def impute(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

        if numeric_cols:
            df = self._impute_numeric(df, numeric_cols)
        if cat_cols:
            df = self._impute_categorical(df, cat_cols)

        return df

    def _impute_numeric(self, df: pd.DataFrame, cols: list) -> pd.DataFrame:
        missing_cols = [c for c in cols if df[c].isnull().any()]
        if not missing_cols:
            return df

        if self.numeric_strategy == "mean":
            for col in missing_cols:
                fill = df[col].mean()
                df[col] = df[col].fillna(fill)
                self.imputation_log[col] = {"strategy": "mean", "fill_value": round(fill, 4)}
        elif self.numeric_strategy == "median":
            for col in missing_cols:
                fill = df[col].median()
                df[col] = df[col].fillna(fill)
                self.imputation_log[col] = {"strategy": "median", "fill_value": round(fill, 4)}
        elif self.numeric_strategy == "knn":
            imputer = KNNImputer(n_neighbors=self.knn_neighbors)
            df[cols] = imputer.fit_transform(df[cols])
            for col in missing_cols:
                self.imputation_log[col] = {"strategy": f"knn(k={self.knn_neighbors})"}
        elif self.numeric_strategy == "iterative":
            imputer = IterativeImputer(max_iter=self.iterative_max_iter, random_state=42)
            df[cols] = imputer.fit_transform(df[cols])
            for col in missing_cols:
                self.imputation_log[col] = {"strategy": "iterative_imputer"}
        else:
            for col in missing_cols:
                fill = df[col].mean()
                df[col] = df[col].fillna(fill)
                self.imputation_log[col] = {"strategy": "mean_fallback", "fill_value": round(fill, 4)}
        return df

    def _impute_categorical(self, df: pd.DataFrame, cols: list) -> pd.DataFrame:
        missing_cols = [c for c in cols if df[c].isnull().any()]
        if not missing_cols:
            return df

        for col in missing_cols:
            if self.categorical_strategy == "mode":
                mode_vals = df[col].mode()
                fill = mode_vals[0] if len(mode_vals) > 0 else self.constant_fill
                df[col] = df[col].fillna(fill)
                self.imputation_log[col] = {"strategy": "mode", "fill_value": str(fill)}
            elif self.categorical_strategy == "constant":
                df[col] = df[col].fillna(self.constant_fill)
                self.imputation_log[col] = {"strategy": "constant", "fill_value": self.constant_fill}
            else:
                mode_vals = df[col].mode()
                fill = mode_vals[0] if len(mode_vals) > 0 else self.constant_fill
                df[col] = df[col].fillna(fill)
                self.imputation_log[col] = {"strategy": "mode_fallback", "fill_value": str(fill)}
        return df
