import pandas as pd
import json
import time
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass, field

from .detector import DataQualityDetector, DetectionReport
from .imputer import DataImputer
from .validator import DataValidator
from .profiler import DataProfiler
from ..utils.config import PipelineConfig
from ..utils.io_utils import load_data, save_data
from ..utils.logger import setup_logger

logger = setup_logger("orchestrator")

@dataclass
class PipelineResult:
    raw_shape: tuple = (0, 0)
    clean_shape: tuple = (0, 0)
    detection_report: Optional[DetectionReport] = None
    imputation_log: dict = field(default_factory=dict)
    validation_results: list = field(default_factory=list)
    profile_before: dict = field(default_factory=dict)
    profile_after: dict = field(default_factory=dict)
    duration_seconds: float = 0.0
    output_path: Optional[str] = None

class PipelineOrchestrator:
    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.detector = DataQualityDetector(self.config)
        self.imputer = DataImputer(self.config)
        self.validator = DataValidator(self.config)
        self.profiler = DataProfiler()

    def run(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        progress_cb: Optional[Callable[[str, int], None]] = None,
    ) -> PipelineResult:
        start = time.time()
        result = PipelineResult()

        def progress(msg: str, pct: int):
            logger.info(f"[{pct}%] {msg}")
            if progress_cb:
                progress_cb(msg, pct)

        progress("Loading data...", 5)
        df_raw = load_data(input_path)
        result.raw_shape = df_raw.shape
        logger.info(f"Loaded {df_raw.shape[0]} rows × {df_raw.shape[1]} cols")

        progress("Profiling raw data...", 15)
        result.profile_before = self.profiler.profile(df_raw)

        progress("Detecting quality issues...", 30)
        result.detection_report = self.detector.detect(df_raw)
        logger.info(f"Found {len(result.detection_report.issues)} issues. Score: {result.detection_report.total_score}")

        progress("Imputing missing values...", 55)
        df_clean = self.imputer.impute(df_raw)
        result.imputation_log = self.imputer.imputation_log

        progress("Removing duplicates...", 70)
        before = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        dropped = before - len(df_clean)
        if dropped:
            logger.info(f"Removed {dropped} duplicate rows")

        progress("Validating cleaned data...", 85)
        result.validation_results = self.validator.validate(df_clean)

        progress("Profiling cleaned data...", 92)
        result.profile_after = self.profiler.profile(df_clean)
        result.clean_shape = df_clean.shape

        if output_path:
            progress(f"Saving to {output_path}...", 96)
            save_data(df_clean, output_path)
            result.output_path = output_path

        result.duration_seconds = round(time.time() - start, 2)
        progress("Pipeline complete!", 100)
        logger.info(f"Done in {result.duration_seconds}s")
        return result

    def run_from_dataframe(
        self,
        df: pd.DataFrame,
        progress_cb: Optional[Callable[[str, int], None]] = None,
    ) -> tuple[pd.DataFrame, PipelineResult]:
        start = time.time()
        result = PipelineResult()

        def progress(msg: str, pct: int):
            if progress_cb:
                progress_cb(msg, pct)

        result.raw_shape = df.shape
        progress("Profiling raw data...", 15)
        result.profile_before = self.profiler.profile(df)

        progress("Detecting quality issues...", 30)
        result.detection_report = self.detector.detect(df)

        progress("Imputing missing values...", 55)
        df_clean = self.imputer.impute(df)
        result.imputation_log = self.imputer.imputation_log

        progress("Removing duplicates...", 72)
        df_clean = df_clean.drop_duplicates()

        progress("Validating...", 88)
        result.validation_results = self.validator.validate(df_clean)

        progress("Final profiling...", 95)
        result.profile_after = self.profiler.profile(df_clean)
        result.clean_shape = df_clean.shape
        result.duration_seconds = round(time.time() - start, 2)
        progress("Complete!", 100)
        return df_clean, result
