import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Automated Data Quality Dashboard", layout="wide")

st.title("Automated Data Quality & Imputation Pipeline")
st.write("Upload dataset and analyze data quality.")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    
    df = pd.read_csv(uploaded_file)
    
    st.subheader("Dataset Preview")
    st.dataframe(df)

    st.subheader("Missing Values")
    st.write(df.isnull().sum())

    st.subheader("Basic Statistics")
    st.write(df.describe())

    if st.button("Run Data Quality Pipeline"):
        
        response = requests.post("http://127.0.0.1:8000/process-data")

        if response.status_code == 200:
            result = response.json()

            st.subheader("Pipeline Results")

            st.write("Validation")
            st.write(result["validation"])

            st.write("Outliers")
            st.write(result["outliers"])

            st.write("Quality Score")
            st.success(result["quality_score"])

        else:
            st.error("Pipeline execution failed")