import pandas as pd
from pathlib import Path
from typing import Union

SUPPORTED = {".csv", ".xlsx", ".xls", ".parquet", ".json"}

def load_data(path: Union[str, Path]) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    ext = path.suffix.lower()
    if ext == ".csv":
        return pd.read_csv(path)
    elif ext in (".xlsx", ".xls"):
        return pd.read_excel(path)
    elif ext == ".parquet":
        return pd.read_parquet(path)
    elif ext == ".json":
        return pd.read_json(path)
    raise ValueError(f"Unsupported format: {ext}. Supported: {SUPPORTED}")

def save_data(df: pd.DataFrame, path: Union[str, Path]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ext = path.suffix.lower()
    if ext == ".csv":
        df.to_csv(path, index=False)
    elif ext in (".xlsx", ".xls"):
        df.to_excel(path, index=False)
    elif ext == ".parquet":
        df.to_parquet(path, index=False)
    elif ext == ".json":
        df.to_json(path, orient="records", indent=2)
    else:
        df.to_csv(path, index=False)
