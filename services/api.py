from fastapi import FastAPI
import pandas as pd
from main import run_pipeline

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Automated Data Quality Pipeline API Running"}

@app.post("/process-data")
def process_data():
    
    file = "data/raw/sample.csv"

    validation, profile, outliers, score = run_pipeline(file)

    return {
        "validation": validation,
        "outliers": outliers,
        "quality_score": score
    }