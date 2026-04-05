import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

def load_config(path: str = "config/pipeline_config.yaml") -> Dict[str, Any]:
    with open(path) as f:
        return yaml.safe_load(f)

@dataclass
class PipelineConfig:
    missing_threshold: float = 0.05
    outlier_method: str = "iqr"
    outlier_threshold: float = 1.5
    numeric_strategy: str = "knn"
    categorical_strategy: str = "mode"
    knn_neighbors: int = 5
    constant_fill: str = "UNKNOWN"
    iterative_max_iter: int = 10
    duplicate_subset: Optional[list] = None
    cardinality_threshold: int = 50

    @classmethod
    def from_yaml(cls, path: str = "config/pipeline_config.yaml") -> "PipelineConfig":
        cfg = load_config(path)
        d = {**cfg.get("detection", {}), **cfg.get("imputation", {})}
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
