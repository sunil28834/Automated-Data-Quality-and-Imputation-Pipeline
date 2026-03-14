from pipeline.ingestion import ingest_data
from pipeline.validation import validate_data
from pipeline.profiling import profile_data
from pipeline.imputation import ml_imputation
from pipeline.outlier import detect_outliers
from pipeline.quality_score import quality_score

def run_pipeline(file):

    df = ingest_data(file)

    validation = validate_data(df)

    profile = profile_data(df)

    outliers = detect_outliers(df)

    df = ml_imputation(df)

    score = quality_score(df)

    return validation, profile, outliers, score