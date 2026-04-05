import pandas as pd
import numpy as np
from typing import Dict, Any

class DataProfiler:
    def profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        profile = {
            "shape": {"rows": len(df), "columns": len(df.columns)},
            "memory_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 3),
            "columns": {},
        }
        for col in df.columns:
            series = df[col]
            col_info: Dict[str, Any] = {
                "dtype": str(series.dtype),
                "missing": int(series.isnull().sum()),
                "missing_pct": round(series.isnull().mean() * 100, 2),
                "unique": int(series.nunique()),
            }
            if pd.api.types.is_numeric_dtype(series):
                desc = series.describe()
                col_info.update({
                    "mean": round(float(desc["mean"]), 4) if not np.isnan(desc["mean"]) else None,
                    "std": round(float(desc["std"]), 4) if not np.isnan(desc.get("std", np.nan)) else None,
                    "min": float(desc["min"]),
                    "max": float(desc["max"]),
                    "q25": float(desc["25%"]),
                    "q50": float(desc["50%"]),
                    "q75": float(desc["75%"]),
                    "skewness": round(float(series.skew()), 4),
                })
            else:
                top = series.value_counts().head(5).to_dict()
                col_info["top_values"] = {str(k): int(v) for k, v in top.items()}
            profile["columns"][col] = col_info
        return profile
