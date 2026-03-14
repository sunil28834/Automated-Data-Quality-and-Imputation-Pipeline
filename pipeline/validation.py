import pandas as pd

def validate_data(df):

    validation_report = {}

    # check missing values
    missing_values = df.isnull().sum().to_dict()

    # check duplicate rows
    duplicates = df.duplicated().sum()

    validation_report["missing_values"] = missing_values
    validation_report["duplicates"] = int(duplicates)

    return validation_report