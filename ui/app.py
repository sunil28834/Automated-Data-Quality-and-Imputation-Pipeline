import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

st.set_page_config(
    page_title="DataPulse — Quality Pipeline",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── THEME & GLOBAL CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=Syne:wght@400;500;600;700;800&display=swap');

:root {
  --bg: #0a0a0f;
  --surface: #12121a;
  --surface2: #1a1a26;
  --border: #2a2a3d;
  --accent: #7c6af7;
  --accent2: #4af0c4;
  --accent3: #f06a9e;
  --warn: #f0a53a;
  --text: #e8e8f0;
  --muted: #6b6b85;
  --danger: #f06060;
  --success: #4af0c4;
}

html, body, [class*="css"] {
  font-family: 'Syne', sans-serif !important;
  background: var(--bg) !important;
  color: var(--text) !important;
}

.stApp { background: var(--bg) !important; }

/* Sidebar */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Buttons */
.stButton > button {
  background: linear-gradient(135deg, var(--accent) 0%, #5a4fd4 100%) !important;
  color: white !important;
  border: none !important;
  border-radius: 8px !important;
  font-family: 'DM Mono', monospace !important;
  font-size: 13px !important;
  letter-spacing: 0.05em !important;
  padding: 10px 24px !important;
  transition: all 0.2s ease !important;
  box-shadow: 0 0 20px rgba(124,106,247,0.3) !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 0 32px rgba(124,106,247,0.6) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
  background: var(--surface2) !important;
  border: 1px dashed var(--accent) !important;
  border-radius: 12px !important;
}

/* Progress bar */
.stProgress > div > div { background: var(--accent) !important; }

/* Metrics */
[data-testid="metric-container"] {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  padding: 16px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  background: var(--surface2) !important;
  border-radius: 10px !important;
  gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--muted) !important;
  font-family: 'DM Mono', monospace !important;
  border-radius: 8px !important;
}
.stTabs [aria-selected="true"] {
  background: var(--accent) !important;
  color: white !important;
}

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 10px !important; }

/* Select boxes */
.stSelectbox > div > div {
  background: var(--surface2) !important;
  border-color: var(--border) !important;
  color: var(--text) !important;
}

/* Headings */
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* Glow animation */
@keyframes glow-pulse {
  0%, 100% { box-shadow: 0 0 20px rgba(124,106,247,0.2); }
  50% { box-shadow: 0 0 40px rgba(124,106,247,0.5); }
}
@keyframes slide-in {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
.animated-card { animation: slide-in 0.4s ease forwards; }
</style>
""", unsafe_allow_html=True)

# ─── PLOTLY THEME ─────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(18,18,26,0.6)",
    font=dict(family="DM Mono, monospace", color="#e8e8f0", size=12),
    xaxis=dict(gridcolor="#2a2a3d", linecolor="#2a2a3d", tickcolor="#6b6b85"),
    yaxis=dict(gridcolor="#2a2a3d", linecolor="#2a2a3d", tickcolor="#6b6b85"),
    colorway=["#7c6af7", "#4af0c4", "#f06a9e", "#f0a53a", "#60c0f0", "#a0f060"],
    margin=dict(l=40, r=20, t=40, b=40),
)

COLOR_SEV = {"critical": "#f06060", "high": "#f0a53a", "medium": "#7c6af7", "low": "#4af0c4"}

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
  background: linear-gradient(135deg, #12121a 0%, #1a1226 100%);
  border: 1px solid #2a2a3d;
  border-radius: 16px;
  padding: 28px 36px;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
">
  <div style="position:absolute;top:-40px;right:-40px;width:200px;height:200px;
    background:radial-gradient(circle, rgba(124,106,247,0.15) 0%, transparent 70%);
    border-radius:50%;"></div>
  <div style="position:absolute;bottom:-60px;left:20%;width:280px;height:150px;
    background:radial-gradient(circle, rgba(74,240,196,0.08) 0%, transparent 70%);"></div>
  <div style="display:flex;align-items:center;gap:16px;">
    <div style="font-size:36px;filter:drop-shadow(0 0 12px rgba(124,106,247,0.8));">◈</div>
    <div>
      <div style="font-family:'Syne',sans-serif;font-size:26px;font-weight:800;
        background:linear-gradient(135deg,#7c6af7,#4af0c4);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        DataPulse
      </div>
      <div style="font-family:'DM Mono',monospace;font-size:12px;color:#6b6b85;letter-spacing:0.1em;margin-top:2px;">
        AUTOMATED DATA QUALITY & IMPUTATION PIPELINE
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:11px;letter-spacing:0.15em;
      color:#6b6b85;padding:8px 0 16px;">PIPELINE CONFIG</div>
    """, unsafe_allow_html=True)

    numeric_strategy = st.selectbox("Numeric imputation", ["knn", "mean", "median", "iterative"], index=0)
    cat_strategy = st.selectbox("Categorical imputation", ["mode", "constant", "knn"], index=0)
    knn_k = st.slider("KNN neighbors", 2, 15, 5)
    outlier_method = st.selectbox("Outlier detection", ["iqr", "zscore"], index=0)
    iqr_multiplier = st.slider("IQR multiplier", 1.0, 3.0, 1.5, 0.1)
    missing_thresh = st.slider("Missing threshold (%)", 1, 50, 5)

    st.divider()
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:11px;letter-spacing:0.15em;
      color:#6b6b85;padding:8px 0 12px;">QUICK COMMANDS</div>
    """, unsafe_allow_html=True)
    st.code("python run.py run data.csv", language="bash")
    st.code("python run.py profile data.csv", language="bash")
    st.code("python run.py ui", language="bash")
    st.code("pytest tests/ -v", language="bash")

# ─── LOAD CONFIG & ORCHESTRATOR ──────────────────────────────────────────────
@st.cache_resource
def get_orchestrator(num_strat, cat_strat, k, out_method, iqr_mult, miss_t):
    from src.utils.config import PipelineConfig
    from src.pipeline.orchestrator import PipelineOrchestrator
    cfg = PipelineConfig(
        numeric_strategy=num_strat, categorical_strategy=cat_strat,
        knn_neighbors=k, outlier_method=out_method, outlier_threshold=iqr_mult,
        missing_threshold=miss_t / 100,
    )
    return PipelineOrchestrator(cfg)

orchestrator = get_orchestrator(
    numeric_strategy, cat_strategy, knn_k,
    outlier_method, iqr_multiplier, missing_thresh
)

# ─── UPLOAD & DEMO DATA ───────────────────────────────────────────────────────
col_up, col_demo = st.columns([3, 1])
with col_up:
    uploaded = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls", "parquet"])
with col_demo:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    use_demo = st.button("▶ Load demo dataset", use_container_width=True)

df_input = None

if use_demo or "demo_loaded" in st.session_state:
    st.session_state["demo_loaded"] = True
    np.random.seed(0)
    n = 400
    df_input = pd.DataFrame({
        "age":       np.where(np.random.rand(n) < 0.08, np.nan,
                     np.concatenate([np.random.normal(35, 10, int(n*0.95)),
                                     np.random.uniform(120, 200, int(n*0.05))])),
        "income":    np.where(np.random.rand(n) < 0.12, np.nan, np.random.lognormal(10.5, 0.6, n)),
        "score":     np.where(np.random.rand(n) < 0.06, np.nan, np.random.beta(5, 2, n) * 100),
        "tenure":    np.where(np.random.rand(n) < 0.1, np.nan, np.random.exponential(3, n)),
        "dept":      np.where(np.random.rand(n) < 0.07, None,
                     np.random.choice(["Engineering","Marketing","Finance","Operations","HR"], n,
                                      p=[0.35,0.2,0.2,0.15,0.1])),
        "region":    np.where(np.random.rand(n) < 0.04, None,
                     np.random.choice(["North","South","East","West"], n)),
        "status":    np.where(np.random.rand(n) < 0.05, None,
                     np.random.choice(["Active","Inactive","Pending"], n, p=[0.7,0.2,0.1])),
        "projects":  np.random.randint(0, 12, n).astype(float),
        "rating":    np.where(np.random.rand(n) < 0.09, np.nan,
                     np.random.choice([1,2,3,4,5], n, p=[0.05,0.1,0.25,0.35,0.25])),
    })
    idx_dup = np.random.choice(n, 15, replace=False)
    df_input = pd.concat([df_input, df_input.iloc[idx_dup]], ignore_index=True)
    st.info(f"Demo dataset loaded — {len(df_input):,} rows × {len(df_input.columns)} columns")

elif uploaded:
    try:
        if uploaded.name.endswith(".csv"):
            df_input = pd.read_csv(uploaded)
        elif uploaded.name.endswith((".xlsx", ".xls")):
            df_input = pd.read_excel(uploaded)
        elif uploaded.name.endswith(".parquet"):
            df_input = pd.read_parquet(uploaded)
        st.success(f"Loaded **{uploaded.name}** — {len(df_input):,} rows × {len(df_input.columns)} cols")
    except Exception as e:
        st.error(f"Error loading file: {e}")

# ─── MAIN PIPELINE UI ─────────────────────────────────────────────────────────
if df_input is not None:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["◈ Overview", "⚠ Issues", "⟳ Imputation", "✓ Validation", "∿ Analysis"]
    )

    # ── Run button ────────────────────────────────────────────────────────────
    if "pipeline_result" not in st.session_state:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        run_col, _ = st.columns([1, 3])
        with run_col:
            if st.button("◈  Run Pipeline", use_container_width=True):
                prog_placeholder = st.empty()
                status_placeholder = st.empty()

                steps = []
                with prog_placeholder.container():
                    prog_bar = st.progress(0)
                    status_text = st.empty()

                def on_progress(msg, pct):
                    prog_bar.progress(pct / 100)
                    status_text.markdown(
                        f"<div style='font-family:DM Mono,monospace;font-size:12px;color:#7c6af7;'>"
                        f"[{pct:3d}%] {msg}</div>", unsafe_allow_html=True
                    )
                    steps.append((pct, msg))
                    time.sleep(0.08)

                df_clean, result = orchestrator.run_from_dataframe(df_input, on_progress)
                st.session_state["pipeline_result"] = result
                st.session_state["df_clean"] = df_clean
                st.session_state["df_raw"] = df_input
                prog_placeholder.empty()
                st.rerun()

    if "pipeline_result" not in st.session_state:
        st.markdown("""
        <div style='text-align:center;padding:60px 20px;color:#6b6b85;'>
          <div style='font-size:40px;margin-bottom:12px;filter:drop-shadow(0 0 10px rgba(124,106,247,0.3))'>◈</div>
          <div style='font-family:DM Mono,monospace;font-size:13px;letter-spacing:0.1em;'>
            CONFIGURE ABOVE & CLICK RUN PIPELINE
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        result = st.session_state["pipeline_result"]
        df_clean = st.session_state["df_clean"]
        df_raw = st.session_state["df_raw"]
        dr = result.detection_report

        # Reset button
        rcol1, rcol2 = st.columns([1, 5])
        with rcol1:
            if st.button("↺ Reset", use_container_width=True):
                del st.session_state["pipeline_result"]
                del st.session_state["df_clean"]
                del st.session_state["df_raw"]
                st.rerun()

        # ── TAB 1: OVERVIEW ───────────────────────────────────────────────────
        with tab1:
            score = dr.total_score
            score_color = "#4af0c4" if score >= 80 else "#f0a53a" if score >= 60 else "#f06060"

            # Score gauge
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=score,
                delta={"reference": 50, "valueformat": ".1f"},
                title={"text": "Quality Score", "font": {"family": "Syne", "size": 18, "color": "#e8e8f0"}},
                number={"font": {"family": "DM Mono", "size": 48, "color": score_color}, "suffix": "/100"},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#6b6b85", "tickfont": {"family": "DM Mono", "size": 10}},
                    "bar": {"color": score_color, "thickness": 0.25},
                    "bgcolor": "#1a1a26",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, 40], "color": "rgba(240,96,96,0.15)"},
                        {"range": [40, 70], "color": "rgba(240,165,58,0.1)"},
                        {"range": [70, 100], "color": "rgba(74,240,196,0.1)"},
                    ],
                    "threshold": {"line": {"color": score_color, "width": 3}, "thickness": 0.8, "value": score},
                }
            ))
            fig_gauge.update_layout(**PLOTLY_LAYOUT, height=280)

            # KPI metrics
            m1, m2, m3, m4 = st.columns(4)
            metrics = [
                (m1, "Quality Score", f"{score:.1f}/100", score_color),
                (m2, "Issues Found", str(len(dr.issues)), "#f0a53a" if dr.issues else "#4af0c4"),
                (m3, "Missing Cells", f"{dr.summary['missing_cells']:,}", "#7c6af7"),
                (m4, "Duration", f"{result.duration_seconds}s", "#60c0f0"),
            ]
            for col, label, val, color in metrics:
                with col:
                    st.markdown(f"""
                    <div class="animated-card" style="background:#12121a;border:1px solid #2a2a3d;
                      border-radius:12px;padding:20px;text-align:center;
                      border-top:2px solid {color};">
                      <div style="font-family:'DM Mono',monospace;font-size:11px;color:#6b6b85;
                        letter-spacing:0.12em;margin-bottom:8px;">{label.upper()}</div>
                      <div style="font-family:'Syne',sans-serif;font-size:28px;font-weight:700;
                        color:{color};">{val}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            gcol, scol = st.columns([1, 1])
            with gcol:
                st.plotly_chart(fig_gauge, use_container_width=True)
            with scol:
                # Issue severity breakdown donut
                sev_counts = {}
                for issue in dr.issues:
                    sev_counts[issue.severity] = sev_counts.get(issue.severity, 0) + 1
                if sev_counts:
                    fig_donut = go.Figure(go.Pie(
                        labels=list(sev_counts.keys()),
                        values=list(sev_counts.values()),
                        hole=0.65,
                        marker=dict(colors=[COLOR_SEV.get(k, "#888") for k in sev_counts],
                                    line=dict(color="#0a0a0f", width=2)),
                        textfont=dict(family="DM Mono", size=11),
                    ))
                    fig_donut.add_annotation(
                        text=f"<b>{len(dr.issues)}</b><br><span style='font-size:10px'>issues</span>",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(family="Syne", size=18, color="#e8e8f0")
                    )
                    fig_donut.update_layout(**PLOTLY_LAYOUT, height=280,
                                           title=dict(text="Issues by Severity", font=dict(size=14)))
                    st.plotly_chart(fig_donut, use_container_width=True)
                else:
                    st.success("No quality issues detected!")

            # Before/After shape
            ba1, ba2, ba3, ba4 = st.columns(4)
            pairs = [
                (ba1, "Rows (before)", f"{result.raw_shape[0]:,}", "#6b6b85"),
                (ba2, "Rows (after)", f"{result.clean_shape[0]:,}", "#4af0c4"),
                (ba3, "Cols (before)", str(result.raw_shape[1]), "#6b6b85"),
                (ba4, "Cols (after)", str(result.clean_shape[1]), "#4af0c4"),
            ]
            for col, label, val, color in pairs:
                with col:
                    st.markdown(f"""
                    <div style="background:#12121a;border:1px solid #2a2a3d;border-radius:10px;
                      padding:14px;text-align:center;">
                      <div style="font-family:'DM Mono',monospace;font-size:10px;color:#6b6b85;">{label}</div>
                      <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:600;color:{color};">{val}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # ── TAB 2: ISSUES ─────────────────────────────────────────────────────
        with tab2:
            if not dr.issues:
                st.markdown("""
                <div style='text-align:center;padding:40px;color:#4af0c4;'>
                  <div style='font-size:32px;'>✓</div>
                  <div style='font-family:DM Mono,monospace;font-size:13px;margin-top:8px;'>
                    NO QUALITY ISSUES DETECTED
                  </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Missing values heatmap
                miss_pct = (df_raw.isnull().mean() * 100).reset_index()
                miss_pct.columns = ["column", "missing_pct"]
                miss_pct = miss_pct[miss_pct["missing_pct"] > 0].sort_values("missing_pct", ascending=True)

                if not miss_pct.empty:
                    fig_miss = go.Figure(go.Bar(
                        x=miss_pct["missing_pct"],
                        y=miss_pct["column"],
                        orientation="h",
                        marker=dict(
                            color=miss_pct["missing_pct"],
                            colorscale=[[0, "#2a2a3d"], [0.3, "#7c6af7"], [0.7, "#f0a53a"], [1, "#f06060"]],
                            showscale=True,
                            colorbar=dict(title=dict(text="% Missing", font=dict(family="DM Mono", size=11)),
                                         tickfont=dict(family="DM Mono", size=10)),
                        ),
                        text=[f"{v:.1f}%" for v in miss_pct["missing_pct"]],
                        textposition="outside",
                        textfont=dict(family="DM Mono", size=10, color="#e8e8f0"),
                    ))
                    fig_miss.update_layout(**PLOTLY_LAYOUT, height=max(200, len(miss_pct)*40 + 80),
                                          title=dict(text="Missing Values by Column (%)", font=dict(size=14)),
                                          xaxis_title="% Missing", yaxis_title="")
                    st.plotly_chart(fig_miss, use_container_width=True)

                # Issue table
                st.markdown("""
                <div style="font-family:'DM Mono',monospace;font-size:11px;letter-spacing:0.1em;
                  color:#6b6b85;padding:16px 0 8px;">ALL DETECTED ISSUES</div>
                """, unsafe_allow_html=True)

                for issue in sorted(dr.issues, key=lambda i: {"critical":0,"high":1,"medium":2,"low":3}[i.severity]):
                    color = COLOR_SEV.get(issue.severity, "#888")
                    st.markdown(f"""
                    <div class="animated-card" style="background:#12121a;border:1px solid #2a2a3d;
                      border-left:3px solid {color};border-radius:8px;padding:14px 20px;margin-bottom:8px;
                      display:flex;align-items:center;gap:20px;">
                      <div style="min-width:90px;">
                        <span style="background:{color}20;color:{color};border:1px solid {color}40;
                          border-radius:4px;padding:2px 8px;font-family:'DM Mono',monospace;font-size:10px;
                          letter-spacing:0.1em;">{issue.severity.upper()}</span>
                      </div>
                      <div style="min-width:140px;font-family:'DM Mono',monospace;font-size:12px;
                        color:#7c6af7;">{issue.column}</div>
                      <div style="min-width:160px;font-family:'DM Mono',monospace;font-size:11px;
                        color:#6b6b85;">{issue.issue_type.replace('_',' ')}</div>
                      <div style="font-family:'DM Mono',monospace;font-size:11px;color:#e8e8f0;">
                        {issue.details}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Outlier boxplots
                numeric_cols = df_raw.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_cols:
                    st.markdown("""
                    <div style="font-family:'DM Mono',monospace;font-size:11px;letter-spacing:0.1em;
                      color:#6b6b85;padding:20px 0 8px;">OUTLIER DISTRIBUTION</div>
                    """, unsafe_allow_html=True)
                    n_box = min(len(numeric_cols), 4)
                    fig_box = make_subplots(rows=1, cols=n_box,
                                           subplot_titles=numeric_cols[:n_box])
                    for i, col in enumerate(numeric_cols[:n_box]):
                        fig_box.add_trace(
                            go.Box(y=df_raw[col].dropna(), name=col,
                                   marker_color="#7c6af7", line_color="#4af0c4",
                                   fillcolor="rgba(124,106,247,0.2)",
                                   boxpoints="outliers", jitter=0.3,
                                   marker_size=4),
                            row=1, col=i+1
                        )
                    fig_box.update_layout(**PLOTLY_LAYOUT, height=320, showlegend=False,
                                         title=dict(text="Numeric Column Distributions", font=dict(size=14)))
                    st.plotly_chart(fig_box, use_container_width=True)

        # ── TAB 3: IMPUTATION ─────────────────────────────────────────────────
        with tab3:
            if not result.imputation_log:
                st.info("No imputation was needed — dataset had no missing values.")
            else:
                st.markdown("""
                <div style="font-family:'DM Mono',monospace;font-size:11px;letter-spacing:0.1em;
                  color:#6b6b85;padding:8px 0 16px;">IMPUTATION LOG</div>
                """, unsafe_allow_html=True)
                for col, info in result.imputation_log.items():
                    strat = info.get("strategy", "unknown")
                    fill = info.get("fill_value", "—")
                    st.markdown(f"""
                    <div style="background:#12121a;border:1px solid #2a2a3d;border-radius:8px;
                      padding:12px 20px;margin-bottom:6px;display:flex;gap:20px;align-items:center;">
                      <div style="min-width:140px;font-family:'DM Mono',monospace;font-size:13px;
                        color:#7c6af7;">{col}</div>
                      <div style="font-family:'DM Mono',monospace;font-size:11px;
                        background:#7c6af720;color:#7c6af7;padding:2px 10px;border-radius:4px;">
                        {strat}</div>
                      <div style="font-family:'DM Mono',monospace;font-size:11px;color:#6b6b85;">
                        fill → <span style="color:#4af0c4;">{fill}</span></div>
                    </div>
                    """, unsafe_allow_html=True)

                # Before/after missing comparison
                miss_before = df_raw.isnull().sum()
                miss_after = df_clean.isnull().sum()
                common = [c for c in miss_before.index if miss_before[c] > 0]
                if common:
                    fig_ba = go.Figure()
                    fig_ba.add_trace(go.Bar(name="Before", x=common,
                                            y=[miss_before[c] for c in common],
                                            marker_color="#f06060", opacity=0.8))
                    fig_ba.add_trace(go.Bar(name="After", x=common,
                                            y=[miss_after.get(c, 0) for c in common],
                                            marker_color="#4af0c4", opacity=0.8))
                    fig_ba.update_layout(**PLOTLY_LAYOUT, barmode="group",
                                         height=320,
                                         title=dict(text="Missing Values: Before vs After", font=dict(size=14)),
                                         xaxis_title="Column", yaxis_title="Missing count")
                    st.plotly_chart(fig_ba, use_container_width=True)

                # Before/after distribution for numeric
                imputed_numeric = [c for c in result.imputation_log
                                   if c in df_raw.select_dtypes(include=[np.number]).columns]
                if imputed_numeric:
                    sel_col = st.selectbox("Compare distribution for column:", imputed_numeric)
                    fig_dist = go.Figure()
                    fig_dist.add_trace(go.Histogram(
                        x=df_raw[sel_col].dropna(), name="Before",
                        opacity=0.6, marker_color="#f06060",
                        histnorm="probability density", nbinsx=30,
                    ))
                    fig_dist.add_trace(go.Histogram(
                        x=df_clean[sel_col].dropna(), name="After",
                        opacity=0.6, marker_color="#4af0c4",
                        histnorm="probability density", nbinsx=30,
                    ))
                    fig_dist.update_layout(**PLOTLY_LAYOUT, barmode="overlay", height=300,
                                           title=dict(text=f"Distribution shift: {sel_col}", font=dict(size=14)))
                    st.plotly_chart(fig_dist, use_container_width=True)

        # ── TAB 4: VALIDATION ─────────────────────────────────────────────────
        with tab4:
            if not result.validation_results:
                st.info("No custom validation rules were configured. Add rules in the orchestrator.")
            else:
                passed = sum(1 for r in result.validation_results if r.passed)
                total = len(result.validation_results)
                vc1, vc2 = st.columns(2)
                with vc1:
                    st.metric("Rules Passed", f"{passed}/{total}")
                with vc2:
                    st.metric("Pass Rate", f"{passed/total*100:.0f}%")

                for r in result.validation_results:
                    color = "#4af0c4" if r.passed else "#f06060"
                    icon = "✓" if r.passed else "✗"
                    st.markdown(f"""
                    <div style="background:#12121a;border:1px solid #2a2a3d;border-left:3px solid {color};
                      border-radius:8px;padding:12px 20px;margin-bottom:6px;display:flex;gap:16px;">
                      <span style="color:{color};font-size:16px;">{icon}</span>
                      <span style="font-family:'DM Mono',monospace;font-size:12px;color:#7c6af7;">{r.column}</span>
                      <span style="font-family:'DM Mono',monospace;font-size:11px;color:#6b6b85;">{r.rule}</span>
                      <span style="font-family:'DM Mono',monospace;font-size:11px;color:#e8e8f0;">{r.details}</span>
                    </div>
                    """, unsafe_allow_html=True)

            # Clean data preview
            st.markdown("""
            <div style="font-family:'DM Mono',monospace;font-size:11px;letter-spacing:0.1em;
              color:#6b6b85;padding:20px 0 8px;">CLEANED DATASET PREVIEW</div>
            """, unsafe_allow_html=True)
            st.dataframe(df_clean.head(50), use_container_width=True, height=300)

            # Download
            buf = io.BytesIO()
            df_clean.to_csv(buf, index=False)
            st.download_button(
                "↓ Download cleaned CSV",
                data=buf.getvalue(),
                file_name="cleaned_data.csv",
                mime="text/csv",
                use_container_width=False,
            )

        # ── TAB 5: ANALYSIS ───────────────────────────────────────────────────
        with tab5:
            numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()

            if len(numeric_cols) >= 2:
                # Correlation heatmap
                corr = df_clean[numeric_cols].corr()
                fig_corr = go.Figure(go.Heatmap(
                    z=corr.values,
                    x=corr.columns.tolist(),
                    y=corr.columns.tolist(),
                    colorscale=[[0, "#f06060"], [0.5, "#1a1a26"], [1, "#4af0c4"]],
                    zmid=0, zmin=-1, zmax=1,
                    text=np.round(corr.values, 2),
                    texttemplate="%{text}",
                    textfont=dict(family="DM Mono", size=10, color="#e8e8f0"),
                    hoverongaps=False,
                    colorbar=dict(tickfont=dict(family="DM Mono", size=10)),
                ))
                fig_corr.update_layout(**PLOTLY_LAYOUT, height=400,
                                       title=dict(text="Correlation Matrix (cleaned data)", font=dict(size=14)))
                st.plotly_chart(fig_corr, use_container_width=True)

                # Scatter matrix for top 4 numeric
                top4 = numeric_cols[:4]
                if len(top4) >= 2:
                    cat_cols = df_clean.select_dtypes(include=["object"]).columns.tolist()
                    color_col = cat_cols[0] if cat_cols else None
                    fig_scatter = px.scatter_matrix(
                        df_clean[top4 + ([color_col] if color_col else [])].dropna(),
                        dimensions=top4,
                        color=color_col,
                        color_discrete_sequence=["#7c6af7","#4af0c4","#f06a9e","#f0a53a","#60c0f0"],
                        opacity=0.6,
                    )
                    fig_scatter.update_traces(marker=dict(size=3))
                    fig_scatter.update_layout(**PLOTLY_LAYOUT, height=500,
                                              title=dict(text="Scatter Matrix", font=dict(size=14)))
                    st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("Need at least 2 numeric columns for analysis charts.")

            # Profile summary table
            prof = result.profile_after
            st.markdown("""
            <div style="font-family:'DM Mono',monospace;font-size:11px;letter-spacing:0.1em;
              color:#6b6b85;padding:16px 0 8px;">COLUMN PROFILE (AFTER CLEANING)</div>
            """, unsafe_allow_html=True)
            rows = []
            for col, info in prof["columns"].items():
                row = {"Column": col, "Type": info["dtype"],
                       "Missing %": f"{info['missing_pct']}%",
                       "Unique": info["unique"]}
                if "mean" in info:
                    row["Mean"] = info["mean"]
                    row["Std"] = info["std"]
                    row["Skew"] = info["skewness"]
                rows.append(row)
            st.dataframe(pd.DataFrame(rows), use_container_width=True, height=300)

else:
    st.markdown("""
    <div style='text-align:center;padding:80px 20px;'>
      <div style='font-size:52px;margin-bottom:16px;
        filter:drop-shadow(0 0 20px rgba(124,106,247,0.4))'>◈</div>
      <div style='font-family:Syne,sans-serif;font-size:20px;font-weight:600;
        color:#e8e8f0;margin-bottom:8px;'>Upload a file or load the demo dataset</div>
      <div style='font-family:DM Mono,monospace;font-size:12px;color:#6b6b85;'>
        CSV · Excel · Parquet · JSON supported
      </div>
    </div>
    """, unsafe_allow_html=True)
