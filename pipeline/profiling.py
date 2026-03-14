import pandas as pd

def profile_data(df):

    profile = {}

    profile["columns"] = list(df.columns)
    profile["rows"] = df.shape[0]
    profile["missing_values"] = df.isnull().sum().to_dict()
    profile["data_types"] = df.dtypes.astype(str).to_dict()

    return profile