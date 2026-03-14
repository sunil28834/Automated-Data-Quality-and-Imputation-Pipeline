import pandas as pd
from sklearn.impute import SimpleImputer

def ml_imputation(df):

    num_cols = df.select_dtypes(include=['int64','float64']).columns

    imputer = SimpleImputer(strategy="mean")

    df[num_cols] = imputer.fit_transform(df[num_cols])

    return df