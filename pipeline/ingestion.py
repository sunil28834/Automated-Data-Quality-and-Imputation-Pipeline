import pandas as pd

def ingest_data(file_path):
    df = pd.read_csv(file_path)
    return df