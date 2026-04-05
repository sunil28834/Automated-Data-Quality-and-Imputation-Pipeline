# ◈ DataPulse — Automated Data Quality & Imputation Pipeline

A production-grade pipeline for detecting, reporting, and fixing data quality issues — with an advanced animated dashboard.

---

## Project Structure

```
data-quality-pipeline/
├── config/
│   ├── pipeline_config.yaml      # Pipeline settings
│   └── logging_config.yaml       # Logging settings
├── data/
│   ├── raw/                      # Input datasets
│   ├── processed/                # Cleaned outputs
│   └── reports/                  # Generated reports
├── logs/                         # Pipeline run logs
├── notebooks/                    # Jupyter exploration
├── src/
│   ├── pipeline/
│   │   ├── detector.py           # Quality issue detection
│   │   ├── imputer.py            # Missing value imputation
│   │   ├── validator.py          # Custom validation rules
│   │   ├── profiler.py           # Column-level statistics
│   │   └── orchestrator.py       # Full pipeline runner
│   ├── ui/
│   │   └── app.py                # Streamlit dashboard
│   ├── utils/
│   │   ├── config.py             # Config dataclass
│   │   ├── io_utils.py           # File I/O helpers
│   │   └── logger.py             # Logging setup
│   └── api/
│       ├── routes.py             # FastAPI routes
│       └── schemas.py            # Pydantic schemas
├── tests/
│   ├── test_detector.py
│   ├── test_imputer.py
│   └── test_pipeline.py
├── run.py                        # CLI entry point
├── requirements.txt
└── setup.py
```

---

## Quick Start

```bash
# 1. Clone and set up environment
git clone <repo-url>
cd data-quality-pipeline
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Run the pipeline on a CSV
python run.py run data/raw/your_file.csv --output data/processed/cleaned.csv --report

# 3. Profile a dataset
python run.py profile data/raw/your_file.csv

# 4. Launch the dashboard
python run.py ui
# OR directly:
streamlit run src/ui/app.py

# 5. Run tests
pytest tests/ -v
```

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `python run.py run <file>` | Full pipeline on a file |
| `python run.py run <file> -o out.csv -r` | With output path + report |
| `python run.py profile <file>` | Column statistics table |
| `python run.py ui` | Launch Streamlit dashboard |
| `pytest tests/ -v` | Run test suite |

---

## Detection Capabilities

- Missing values (per-column %, severity classification)
- Duplicate rows
- Numeric outliers (IQR or Z-score)
- High-cardinality categorical columns
- Type mismatches (numeric stored as string)

## Imputation Strategies

| Type | Strategies |
|------|-----------|
| Numeric | `mean`, `median`, `knn`, `iterative` |
| Categorical | `mode`, `constant`, `knn` |

## Quality Score

Each issue deducts from 100: critical=15, high=7, medium=3, low=1.

---

## Deployment (Streamlit Cloud)

1. Push to GitHub
2. Go to share.streamlit.io
3. Set main file: `src/ui/app.py`
4. Deploy
