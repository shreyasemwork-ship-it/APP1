import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Excel Data Analyzer",
    page_icon="📊",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background-color: #0f1117; }

    .metric-card {
        background: #1e2130;
        border: 1px solid #2d3250;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 10px;
    }
    .metric-card h4 { color: #a0aec0; font-size: 0.78rem; font-weight: 600;
                       letter-spacing: 0.08em; text-transform: uppercase; margin: 0 0 6px; }
    .metric-card p  { color: #e2e8f0; font-size: 1.4rem; font-weight: 700; margin: 0; }

    .badge-green {
        display: inline-block;
        background: #1a4731; color: #4ade80;
        border: 1px solid #22c55e;
        border-radius: 20px; padding: 4px 14px;
        font-size: 0.78rem; font-weight: 600; letter-spacing: 0.05em;
    }
    .badge-yellow {
        display: inline-block;
        background: #3d2e00; color: #facc15;
        border: 1px solid #eab308;
        border-radius: 20px; padding: 4px 14px;
        font-size: 0.78rem; font-weight: 600; letter-spacing: 0.05em;
    }
    .col-header {
        font-size: 1.05rem; font-weight: 700;
        color: #e2e8f0; margin: 0 0 4px;
    }
    .divider { border: none; border-top: 1px solid #2d3250; margin: 28px 0; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 📊 Excel Data Analyzer")
st.markdown("Upload an Excel file to explore numeric columns — histograms, statistics, and forecasting readiness.")
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── File upload ───────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("Choose an Excel file (.xlsx or .xls)", type=["xlsx", "xls"])

# ── Threshold slider ──────────────────────────────────────────────────────────
threshold_pct = st.slider(
    "Mean–Median closeness threshold (%)",
    min_value=1, max_value=30, value=10,
    help="If |mean − median| / mean ≤ this %, the column is considered 'forecast-ready'."
)

# ── Main logic ────────────────────────────────────────────────────────────────
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Could not read file: {e}")
        st.stop()

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if not numeric_cols:
        st.warning("No numeric columns found in this file.")
        st.stop()

    st.markdown(f"**{len(numeric_cols)} numeric column(s) found:** {', '.join(numeric_cols)}")
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Per-column analysis ───────────────────────────────────────────────────
    for col in numeric_cols:
        series = df[col].dropna()

        if len(series) == 0:
            st.info(f"Column **{col}** has no non-null values — skipping.")
            continue

        mean_val   = series.mean()
        median_val = series.median()

        # Compute closeness
        if mean_val != 0:
            diff_pct = abs(mean_val - median_val) / abs(mean_val) * 100
        else:
            diff_pct = 0.0 if median_val == 0 else 100.0

        is_forecast_ready = diff_pct <= threshold_pct

        # ── Layout: chart left, stats right ──────────────────────────────────
        left, right = st.columns([2, 1])

        with left:
            st.markdown(f'<p class="col-header">{col}</p>', unsafe_allow_html=True)

            fig, ax = plt.subplots(figsize=(6, 3))
            fig.patch.set_facecolor("#1e2130")
            ax.set_facecolor("#1e2130")

            n_bins = min(30, max(10, len(series) // 5))
            ax.hist(series, bins=n_bins, color="#6366f1", edgecolor="#0f1117", linewidth=0.4, alpha=0.9)

            ax.axvline(mean_val,   color="#f472b6", linewidth=1.6, linestyle="--", label=f"Mean {mean_val:,.2f}")
            ax.axvline(median_val, color="#34d399", linewidth=1.6, linestyle=":",  label=f"Median {median_val:,.2f}")

            ax.legend(fontsize=8, framealpha=0.2, labelcolor="white")
            ax.tick_params(colors="#a0aec0", labelsize=8)
            for spine in ax.spines.values():
                spine.set_edgecolor("#2d3250")
            ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
            ax.set_xlabel("Value", color="#a0aec0", fontsize=8)
            ax.set_ylabel("Count",  color="#a0aec0", fontsize=8)

            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        with right:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="metric-card">
                <h4>Mean</h4><p>{mean_val:,.4f}</p>
            </div>
            <div class="metric-card">
                <h4>Median</h4><p>{median_val:,.4f}</p>
            </div>
            <div class="metric-card">
                <h4>|Mean − Median| / Mean</h4><p>{diff_pct:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)

            if is_forecast_ready:
                st.markdown(
                    '<span class="badge-green"> Suitable for Forecasting</span>',
                    unsafe_allow_html=True
                )
                st.caption("Mean ≈ Median → roughly symmetric distribution.")
            else:
                st.markdown(
                    '<span class="badge-yellow"> Review Before Forecasting</span>',
                    unsafe_allow_html=True
                )
                st.caption("Mean and Median differ significantly → skewed distribution.")

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

else:
    st.info("Upload an Excel file above to get started.")
