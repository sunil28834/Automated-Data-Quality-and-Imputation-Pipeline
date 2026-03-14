def quality_score(df):

    total_cells = df.shape[0] * df.shape[1]

    missing_cells = df.isnull().sum().sum()

    score = (1 - (missing_cells / total_cells)) * 100

    return round(score,2)