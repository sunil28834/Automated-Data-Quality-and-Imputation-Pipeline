import pandas as pd

def detect_outliers(df):

    outliers = {}

    for col in df.select_dtypes(include=['int64','float64']).columns:

        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)

        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outlier_count = df[(df[col] < lower) | (df[col] > upper)].shape[0]

        outliers[col] = int(outlier_count)

    return outliers