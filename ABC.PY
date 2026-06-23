import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Excel Data Analysis Tool", layout="wide")

st.title("📊 Excel Data Analysis & Forecasting Readiness Checker")

uploaded_file = st.file_uploader(
    "Upload an Excel File",
    type=["xlsx", "xls"]
)

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)

        st.subheader("Dataset Preview")
        st.dataframe(df.head())

        numeric_cols = df.select_dtypes(include=np.number).columns

        if len(numeric_cols) == 0:
            st.warning("No numerical columns found.")
        else:
            st.subheader("Statistical Analysis")

            results = []

            for col in numeric_cols:

                mean_val = df[col].mean()
                median_val = df[col].median()

                difference_percent = (
                    abs(mean_val - median_val)
                    / abs(mean_val)
                    * 100
                ) if mean_val != 0 else 0

                if difference_percent <= 10:
                    forecast_msg = "Suitable for Forecasting"
                else:
                    forecast_msg = "May Not Be Suitable for Forecasting"

                results.append({
                    "Column": col,
                    "Mean": round(mean_val, 2),
                    "Median": round(median_val, 2),
                    "Difference (%)": round(difference_percent, 2),
                    "Forecasting Assessment": forecast_msg
                })

                st.markdown(f"### {col}")

                fig, ax = plt.subplots(figsize=(6,4))
                ax.hist(df[col].dropna(), bins=15)
                ax.set_title(f"Histogram - {col}")
                ax.set_xlabel(col)
                ax.set_ylabel("Frequency")

                st.pyplot(fig)

                st.write(f"**Mean:** {mean_val:.2f}")
                st.write(f"**Median:** {median_val:.2f}")
                st.write(f"**Difference:** {difference_percent:.2f}%")
                st.write(f"**Assessment:** {forecast_msg}")

                st.divider()

            st.subheader("Summary Table")
            st.dataframe(pd.DataFrame(results))

    except Exception as e:
        st.error(f"Error reading file: {e}")
