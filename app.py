import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, date
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PAGE CONFIG & CUSTOM CSS
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Climate Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🌍"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg-primary: #0a0f1e;
    --bg-card: #111827;
    --bg-card2: #1a2235;
    --accent-blue: #3b82f6;
    --accent-cyan: #06b6d4;
    --accent-orange: #f97316;
    --accent-red: #ef4444;
    --accent-green: #22c55e;
    --text-primary: #f1f5f9;
    --text-muted: #94a3b8;
    --border: rgba(59,130,246,0.2);
}

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

.stApp {
    background: linear-gradient(135deg, #0a0f1e 0%, #0d1b2a 50%, #0a0f1e 100%) !important;
}

/* ── HEADER ── */
.hero-header {
    background: linear-gradient(90deg, #0a0f1e, #0d2137, #0a0f1e);
    border-bottom: 1px solid var(--border);
    padding: 2rem 0 1.5rem;
    text-align: center;
    margin-bottom: 2rem;
}
.hero-title {
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(90deg, #3b82f6, #06b6d4, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
    margin: 0;
}
.hero-sub {
    color: var(--text-muted);
    font-size: 1rem;
    margin-top: 0.4rem;
    font-weight: 300;
}

/* ── KPI CARDS ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1rem;
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(59,130,246,0.15);
}
.kpi-label {
    font-size: 0.72rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 0.4rem;
}
.kpi-value {
    font-size: 1.9rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}
.kpi-unit { font-size: 0.9rem; color: var(--text-muted); font-weight: 400; }
.kpi-blue  { color: #3b82f6; }
.kpi-cyan  { color: #06b6d4; }
.kpi-orange{ color: #f97316; }
.kpi-red   { color: #ef4444; }
.kpi-green { color: #22c55e; }
.kpi-yellow{ color: #eab308; }

/* ── SECTION HEADERS ── */
.section-title {
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--text-primary);
    border-left: 3px solid var(--accent-blue);
    padding-left: 0.75rem;
    margin: 2rem 0 1rem;
}

/* ── INSIGHT BOX ── */
.insight-box {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border: 1px solid rgba(6,182,212,0.3);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    font-size: 0.88rem;
    color: #cbd5e1;
    line-height: 1.6;
}
.insight-box strong { color: #06b6d4; }

/* ── ALERT BOXES ── */
.alert-hot {
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.4);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    color: #fca5a5;
    font-size: 0.88rem;
}
.alert-cold {
    background: rgba(59,130,246,0.1);
    border: 1px solid rgba(59,130,246,0.4);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    color: #93c5fd;
    font-size: 0.88rem;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: #080d1a !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}
.sidebar-section {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--accent-cyan) !important;
    padding: 0.5rem 0 0.2rem;
}

/* ── METRIC DELTA COLORS ── */
[data-testid="stMetricDelta"] { font-size: 0.78rem; }

/* ── TABLES ── */
.dataframe { background: var(--bg-card) !important; }

/* ── TAB STYLING ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card);
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: var(--text-muted) !important;
    border-radius: 6px;
    font-size: 0.85rem;
    padding: 0.5rem 1.2rem;
}
.stTabs [aria-selected="true"] {
    background: var(--accent-blue) !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PLOTLY DARK THEME
# ─────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,0.8)",
    font=dict(family="Space Grotesk", color="#94a3b8", size=12),
    title_font=dict(family="Space Grotesk", color="#f1f5f9", size=15),
    margin=dict(l=10, r=10, t=45, b=10),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
    colorway=["#3b82f6","#06b6d4","#f97316","#22c55e","#a855f7","#eab308"],
)

SEASON_MAP = {1:"Winter",2:"Winter",3:"Spring",4:"Spring",5:"Spring",
              6:"Summer",7:"Summer",8:"Summer",9:"Autumn",10:"Autumn",
              11:"Autumn",12:"Winter"}
MONTH_NAMES = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
               7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

# ─────────────────────────────────────────────
# DATABASE CONNECTION
# ─────────────────────────────────────────────
DB_USER     = "postgres"
DB_PASSWORD = "5365"
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "weather_data"

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    query = "SELECT station, year, month, day, tmax, tmin FROM weather_data"
    df = pd.read_sql(query, engine)
    df["avg_temp"]      = (df["tmax"] + df["tmin"]) / 2
    df["diurnal_range"] = df["tmax"] - df["tmin"]
    df["date"]          = pd.to_datetime(
        df[["year","month","day"]].rename(columns={"year":"year","month":"month","day":"day"})
    )
    df["season"]        = df["month"].map(SEASON_MAP)
    df["month_name"]    = df["month"].map(MONTH_NAMES)
    return df

df = load_data()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-section">📡 Station Filter</div>', unsafe_allow_html=True)
    stations = sorted(df["station"].dropna().unique())
    selected_station = st.multiselect("Stations", stations, default=stations[:5])

    st.markdown('<div class="sidebar-section">📅 Date Range</div>', unsafe_allow_html=True)
    date_mode = st.radio("Filter Mode", ["Year/Month", "Exact Date Range"], label_visibility="collapsed")

    if date_mode == "Year/Month":
        years  = sorted(df["year"].dropna().unique())
        months = sorted(df["month"].dropna().unique())
        selected_year  = st.multiselect("Year(s)",  years,  default=years[-3:])
        selected_month = st.multiselect("Month(s)", months, default=months)
        date_filter = (
            df["year"].isin(selected_year) &
            df["month"].isin(selected_month)
        )
    else:
        min_d = df["date"].min().date()
        max_d = df["date"].max().date()
        d_from, d_to = st.date_input(
            "Date Range",
            value=[min_d, max_d],
            min_value=min_d,
            max_value=max_d
        )
        date_filter = (df["date"].dt.date >= d_from) & (df["date"].dt.date <= d_to)

    st.markdown('<div class="sidebar-section">⚙️ Analysis Settings</div>', unsafe_allow_html=True)
    heatwave_thresh = st.slider("Heatwave Threshold (°C)", 35, 50, 40)
    coldwave_thresh = st.slider("Cold Wave Threshold (°C)", -10, 15, 5)
    show_anomaly_base = st.selectbox("Anomaly Baseline", ["Full Dataset", "Selected Period"])

# ─────────────────────────────────────────────
# FILTER
# ─────────────────────────────────────────────
filtered_df = df[df["station"].isin(selected_station) & date_filter].copy()

if filtered_df.empty:
    st.warning("⚠️ No data for selected filters. Adjust sidebar options.")
    st.stop()

# ─────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
  <div class="hero-title">🌍 Climate Dashboard</div>
  <div class="hero-sub">Advanced Climate Intelligence · Powered by PostgreSQL & Streamlit</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# NAVIGATION TABS
# ─────────────────────────────────────────────
tab_overview, tab_trends, tab_extremes, tab_station, tab_search, tab_forecast = st.tabs([
    "📊 Overview", "📈 Trends", "🔥 Extremes", "🌍 Stations", "🔍 Date Search", "🤖 AI Insights"
])

# ═══════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════
with tab_overview:
    # KPI CARDS
    st.markdown('<div class="section-title">Key Climate Indicators</div>', unsafe_allow_html=True)
    hot_days  = (filtered_df["tmax"] > heatwave_thresh).sum()
    cold_days = (filtered_df["tmin"] < coldwave_thresh).sum()
    max_record_row = filtered_df.loc[filtered_df["tmax"].idxmax()]
    min_record_row = filtered_df.loc[filtered_df["tmin"].idxmin()]

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Total Records</div>
            <div class="kpi-value kpi-blue">{len(filtered_df):,}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Avg Max Temp</div>
            <div class="kpi-value kpi-orange">{filtered_df["tmax"].mean():.1f}<span class="kpi-unit">°C</span></div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Avg Min Temp</div>
            <div class="kpi-value kpi-cyan">{filtered_df["tmin"].mean():.1f}<span class="kpi-unit">°C</span></div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Record High</div>
            <div class="kpi-value kpi-red">{filtered_df["tmax"].max():.1f}<span class="kpi-unit">°C</span></div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Record Low</div>
            <div class="kpi-value kpi-blue">{filtered_df["tmin"].min():.1f}<span class="kpi-unit">°C</span></div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Avg Diurnal Range</div>
            <div class="kpi-value kpi-yellow">{filtered_df["diurnal_range"].mean():.1f}<span class="kpi-unit">°C</span></div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Heatwave Days</div>
            <div class="kpi-value kpi-red">{hot_days:,}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Cold Wave Days</div>
            <div class="kpi-value kpi-cyan">{cold_days:,}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # RECORD EVENTS
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1.5rem">
        <div class="alert-hot">🔴 <strong>Record High:</strong> {max_record_row["tmax"]:.1f}°C
        on {max_record_row["date"].strftime("%d %b %Y")} at <strong>{max_record_row["station"]}</strong></div>
        <div class="alert-cold">🔵 <strong>Record Low:</strong> {min_record_row["tmin"]:.1f}°C
        on {min_record_row["date"].strftime("%d %b %Y")} at <strong>{min_record_row["station"]}</strong></div>
    </div>
    """, unsafe_allow_html=True)

    # TEMPERATURE RANGE GAUGE
    col_a, col_b = st.columns(2)
    with col_a:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=round(filtered_df["tmax"].mean(), 1),
            delta={"reference": df["tmax"].mean(), "valueformat": ".1f",
                   "increasing": {"color": "#ef4444"}, "decreasing": {"color": "#22c55e"}},
            title={"text": "Avg Tmax vs Overall Baseline", "font": {"color": "#f1f5f9", "size": 14}},
            gauge={
                "axis": {"range": [df["tmin"].min(), df["tmax"].max()], "tickcolor": "#94a3b8"},
                "bar": {"color": "#f97316"},
                "steps": [
                    {"range": [df["tmin"].min(), 15], "color": "#1e3a5f"},
                    {"range": [15, 30], "color": "#1e4d3a"},
                    {"range": [30, 40], "color": "#4a2c0a"},
                    {"range": [40, df["tmax"].max()], "color": "#4a0f0f"},
                ],
                "threshold": {"line": {"color": "#06b6d4", "width": 3},
                              "thickness": 0.75, "value": df["tmax"].mean()}
            },
            number={"suffix": "°C", "font": {"color": "#f97316", "size": 36}}
        ))
        fig_gauge.update_layout(**PLOT_LAYOUT, height=280)
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_b:
        # SEASON PIE
        season_counts = filtered_df.groupby("season")["avg_temp"].mean().reset_index()
        fig_pie = px.pie(
            season_counts, values="avg_temp", names="season",
            title="Avg Temperature by Season",
            color_discrete_map={"Summer":"#ef4444","Spring":"#22c55e",
                                "Autumn":"#f97316","Winter":"#3b82f6"}
        )
        fig_pie.update_traces(textfont_size=12, hole=0.45)
        fig_pie.update_layout(**PLOT_LAYOUT, height=280)
        st.plotly_chart(fig_pie, use_container_width=True)

    # MONTHLY HEATMAP
    st.markdown('<div class="section-title">Monthly Temperature Heatmap</div>', unsafe_allow_html=True)
    pivot = filtered_df.groupby(["year","month"])["avg_temp"].mean().reset_index()
    pivot_table = pivot.pivot(index="year", columns="month", values="avg_temp")
    pivot_table.columns = [MONTH_NAMES[c] for c in pivot_table.columns]

    fig_heat = px.imshow(
        pivot_table,
        color_continuous_scale="RdBu_r",
        title="Year × Month Average Temperature (°C)",
        labels={"color":"Avg Temp (°C)"},
        aspect="auto"
    )
    fig_heat.update_layout(**PLOT_LAYOUT, height=350)
    st.plotly_chart(fig_heat, use_container_width=True)


# ═══════════════════════════════════════════════════════════
# TAB 2 — TRENDS
# ═══════════════════════════════════════════════════════════
with tab_trends:
    st.markdown('<div class="section-title">Long-Term Temperature Trends</div>', unsafe_allow_html=True)

    # DUAL AXIS TREND
    yearly = filtered_df.groupby("year").agg(
        tmax=("tmax","mean"), tmin=("tmin","mean"), avg_temp=("avg_temp","mean")
    ).reset_index()
    baseline_val = (df["avg_temp"].mean() if show_anomaly_base == "Full Dataset"
                    else yearly["avg_temp"].mean())
    yearly["anomaly"] = yearly["avg_temp"] - baseline_val

    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
    fig_trend.add_trace(go.Scatter(
        x=yearly["year"], y=yearly["tmax"], name="Avg Tmax",
        line=dict(color="#f97316", width=2.5), mode="lines+markers",
        marker=dict(size=5)
    ), secondary_y=False)
    fig_trend.add_trace(go.Scatter(
        x=yearly["year"], y=yearly["tmin"], name="Avg Tmin",
        line=dict(color="#3b82f6", width=2.5), mode="lines+markers",
        marker=dict(size=5)
    ), secondary_y=False)
    fig_trend.add_trace(go.Bar(
        x=yearly["year"], y=yearly["anomaly"], name="Anomaly",
        marker_color=["#ef4444" if v > 0 else "#3b82f6" for v in yearly["anomaly"]],
        opacity=0.5
    ), secondary_y=True)
    fig_trend.update_layout(**PLOT_LAYOUT, height=400,
                            title="Yearly Avg Tmax / Tmin + Temperature Anomaly")
    fig_trend.update_yaxes(title_text="Temperature (°C)", secondary_y=False,
                           gridcolor="rgba(255,255,255,0.05)")
    fig_trend.update_yaxes(title_text="Anomaly (°C)", secondary_y=True,
                           gridcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_trend, use_container_width=True)

    # ROLLING AVERAGE
    st.markdown('<div class="section-title">Monthly Trend with Rolling Average</div>', unsafe_allow_html=True)
    monthly = (filtered_df.groupby(["year","month"])[["tmax","tmin"]]
               .mean().reset_index().sort_values(["year","month"]))
    monthly["label"] = monthly["year"].astype(str) + "-" + monthly["month"].astype(str).str.zfill(2)
    monthly["rolling_tmax"] = monthly["tmax"].rolling(3, center=True).mean()
    monthly["rolling_tmin"] = monthly["tmin"].rolling(3, center=True).mean()

    fig_roll = go.Figure()
    fig_roll.add_trace(go.Scatter(
        x=monthly["label"], y=monthly["tmax"], name="Tmax", opacity=0.25,
        line=dict(color="#f97316", width=1), mode="lines"
    ))
    fig_roll.add_trace(go.Scatter(
        x=monthly["label"], y=monthly["rolling_tmax"], name="Tmax (3mo avg)",
        line=dict(color="#f97316", width=2.5), mode="lines"
    ))
    fig_roll.add_trace(go.Scatter(
        x=monthly["label"], y=monthly["tmin"], name="Tmin", opacity=0.25,
        line=dict(color="#3b82f6", width=1), mode="lines"
    ))
    fig_roll.add_trace(go.Scatter(
        x=monthly["label"], y=monthly["rolling_tmin"], name="Tmin (3mo avg)",
        line=dict(color="#3b82f6", width=2.5), mode="lines"
    ))
    fig_roll.update_layout(**PLOT_LAYOUT, height=380, title="Monthly Temperature with 3-Month Rolling Average")
    st.plotly_chart(fig_roll, use_container_width=True)

    # VIOLIN + BOX
    st.markdown('<div class="section-title">Seasonal Distribution</div>', unsafe_allow_html=True)
    fig_violin = go.Figure()
    for season, color in [("Summer","#ef4444"),("Spring","#22c55e"),
                          ("Autumn","#f97316"),("Winter","#3b82f6")]:
        s_df = filtered_df[filtered_df["season"] == season]
        if not s_df.empty:
            fig_violin.add_trace(go.Violin(
                x=s_df["season"], y=s_df["tmax"], name=season,
                box_visible=True, meanline_visible=True,
                fillcolor=color, line_color=color, opacity=0.6
            ))
    fig_violin.update_layout(**PLOT_LAYOUT, height=360,
                             title="Tmax Distribution by Season (Violin + Box)",
                             violinmode="group")
    st.plotly_chart(fig_violin, use_container_width=True)


# ═══════════════════════════════════════════════════════════
# TAB 3 — EXTREMES
# ═══════════════════════════════════════════════════════════
with tab_extremes:
    st.markdown('<div class="section-title">Extreme Climate Events</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        heatwave_df = filtered_df[filtered_df["tmax"] > heatwave_thresh]
        heat_yearly = heatwave_df.groupby("year").size().reset_index(name="days")
        fig_hw = px.bar(heat_yearly, x="year", y="days",
                        title=f"🔥 Heatwave Days Per Year (Tmax > {heatwave_thresh}°C)",
                        color="days", color_continuous_scale="Reds")
        fig_hw.update_layout(**PLOT_LAYOUT, height=320)
        st.plotly_chart(fig_hw, use_container_width=True)

    with col2:
        cold_df = filtered_df[filtered_df["tmin"] < coldwave_thresh]
        cold_yearly = cold_df.groupby("year").size().reset_index(name="days")
        fig_cw = px.bar(cold_yearly, x="year", y="days",
                        title=f"❄️ Cold Wave Days Per Year (Tmin < {coldwave_thresh}°C)",
                        color="days", color_continuous_scale="Blues_r")
        fig_cw.update_layout(**PLOT_LAYOUT, height=320)
        st.plotly_chart(fig_cw, use_container_width=True)

    # TOP 10 HOTTEST DAYS
    st.markdown('<div class="section-title">Top 10 Hottest Days on Record</div>', unsafe_allow_html=True)
    top10 = (filtered_df.nlargest(10, "tmax")[["date","station","tmax","tmin","diurnal_range"]]
             .rename(columns={"date":"Date","station":"Station","tmax":"Tmax°C",
                              "tmin":"Tmin°C","diurnal_range":"Range°C"}))
    top10["Date"] = top10["Date"].dt.strftime("%d %b %Y")
    st.dataframe(top10.style.background_gradient(subset=["Tmax°C"], cmap="Reds")
                 .format({"Tmax°C":"{:.1f}","Tmin°C":"{:.1f}","Range°C":"{:.1f}"}),
                 use_container_width=True, hide_index=True)

    # DIURNAL RANGE SCATTER
    st.markdown('<div class="section-title">Temperature Extremes Scatter</div>', unsafe_allow_html=True)
    fig_scatter = px.scatter(
        filtered_df.sample(min(5000, len(filtered_df))),
        x="tmin", y="tmax", color="season",
        title="Tmax vs Tmin (sampled) — colored by Season",
        color_discrete_map={"Summer":"#ef4444","Spring":"#22c55e",
                            "Autumn":"#f97316","Winter":"#3b82f6"},
        opacity=0.5, size_max=4
    )
    fig_scatter.update_layout(**PLOT_LAYOUT, height=400)
    st.plotly_chart(fig_scatter, use_container_width=True)


# ═══════════════════════════════════════════════════════════
# TAB 4 — STATIONS
# ═══════════════════════════════════════════════════════════
with tab_station:
    st.markdown('<div class="section-title">Station Comparison</div>', unsafe_allow_html=True)

    station_stats = (filtered_df.groupby("station")
                     .agg(avg_tmax=("tmax","mean"), avg_tmin=("tmin","mean"),
                          hot_days=("tmax", lambda x: (x > heatwave_thresh).sum()),
                          record_high=("tmax","max"), record_low=("tmin","min"),
                          total_days=("tmax","count"))
                     .reset_index().sort_values("avg_tmax", ascending=False))

    fig_st = go.Figure()
    fig_st.add_trace(go.Bar(x=station_stats["station"], y=station_stats["avg_tmax"],
                            name="Avg Tmax", marker_color="#f97316"))
    fig_st.add_trace(go.Bar(x=station_stats["station"], y=station_stats["avg_tmin"],
                            name="Avg Tmin", marker_color="#3b82f6"))
    fig_st.update_layout(**PLOT_LAYOUT, height=380, barmode="group",
                         title="Station-Wise Average Temperatures")
    st.plotly_chart(fig_st, use_container_width=True)

    # RADAR CHART
    st.markdown('<div class="section-title">Station Radar Comparison</div>', unsafe_allow_html=True)
    top5 = station_stats.head(5)
    cats = ["avg_tmax","avg_tmin","hot_days","record_high","total_days"]
    fig_radar = go.Figure()
    for _, row in top5.iterrows():
        norm = [(row[c] - station_stats[c].min()) /
                max(station_stats[c].max() - station_stats[c].min(), 1) * 10
                for c in cats]
        fig_radar.add_trace(go.Scatterpolar(
            r=norm + [norm[0]], theta=["Avg Tmax","Avg Tmin","Hot Days","Record High","Total Days","Avg Tmax"],
            fill="toself", name=row["station"], opacity=0.6
        ))
    fig_radar.update_layout(**PLOT_LAYOUT, height=420,
                            polar=dict(bgcolor="rgba(17,24,39,0.8)",
                                       radialaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
                                       angularaxis=dict(gridcolor="rgba(255,255,255,0.08)")),
                            title="Station Comparison Radar (Normalized)")
    st.plotly_chart(fig_radar, use_container_width=True)

    st.dataframe(station_stats.style.format({c:"{:.1f}" for c in ["avg_tmax","avg_tmin","record_high","record_low"]})
                 .background_gradient(subset=["avg_tmax"], cmap="Reds")
                 .background_gradient(subset=["avg_tmin"], cmap="Blues_r"),
                 use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════
# TAB 5 — DATE SEARCH
# ═══════════════════════════════════════════════════════════
with tab_search:
    st.markdown('<div class="section-title">🔍 Exact Date Lookup</div>', unsafe_allow_html=True)

    col_d1, col_d2 = st.columns([1, 2])
    with col_d1:
        search_date = st.date_input(
            "Pick a specific date",
            value=df["date"].max().date(),
            min_value=df["date"].min().date(),
            max_value=df["date"].max().date(),
            key="exact_search"
        )
        search_btn = st.button("🔎 Search", use_container_width=True)

    if search_btn or True:
        day_data = df[df["date"].dt.date == search_date]
        if day_data.empty:
            st.markdown('<div class="insight-box">No data found for this date.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="section-title">Results for {search_date.strftime("%d %B %Y")}</div>', unsafe_allow_html=True)
            for _, row in day_data.iterrows():
                icon = "🔥" if row["tmax"] > heatwave_thresh else ("❄️" if row["tmin"] < coldwave_thresh else "🌤️")
                st.markdown(f"""
                <div class="insight-box">
                {icon} <strong>{row["station"]}</strong> &nbsp;|&nbsp;
                Tmax: <strong style="color:#f97316">{row["tmax"]:.1f}°C</strong> &nbsp;|&nbsp;
                Tmin: <strong style="color:#3b82f6">{row["tmin"]:.1f}°C</strong> &nbsp;|&nbsp;
                Avg: <strong style="color:#06b6d4">{row["avg_temp"]:.1f}°C</strong> &nbsp;|&nbsp;
                Range: <strong>{row["diurnal_range"]:.1f}°C</strong>
                </div>
                """, unsafe_allow_html=True)

    # DATE RANGE QUICK COMPARE
    st.markdown('<div class="section-title">📅 Compare Two Date Ranges</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("*Period A*")
        pa = st.date_input("Period A", value=[date(2010,1,1), date(2010,12,31)],
                           min_value=df["date"].min().date(),
                           max_value=df["date"].max().date(), key="pa")
    with c2:
        st.markdown("*Period B*")
        pb = st.date_input("Period B", value=[date(2020,1,1), date(2020,12,31)],
                           min_value=df["date"].min().date(),
                           max_value=df["date"].max().date(), key="pb")

    if len(pa) == 2 and len(pb) == 2:
        dfa = df[(df["date"].dt.date >= pa[0]) & (df["date"].dt.date <= pa[1])]
        dfb = df[(df["date"].dt.date >= pb[0]) & (df["date"].dt.date <= pb[1])]
        if not dfa.empty and not dfb.empty:
            metrics = {
                "Avg Tmax": (dfa["tmax"].mean(), dfb["tmax"].mean()),
                "Avg Tmin": (dfa["tmin"].mean(), dfb["tmin"].mean()),
                "Avg Range": (dfa["diurnal_range"].mean(), dfb["diurnal_range"].mean()),
                "Hot Days":  ((dfa["tmax"] > heatwave_thresh).sum(), (dfb["tmax"] > heatwave_thresh).sum()),
            }
            comp_df = pd.DataFrame({
                "Metric": list(metrics.keys()),
                f"Period A ({pa[0]} → {pa[1]})": [v[0] for v in metrics.values()],
                f"Period B ({pb[0]} → {pb[1]})": [v[1] for v in metrics.values()],
            })
            fig_comp = px.bar(comp_df.melt("Metric"), x="Metric", y="value",
                              color="variable", barmode="group",
                              title="Side-by-Side Period Comparison",
                              color_discrete_sequence=["#3b82f6","#f97316"])
            fig_comp.update_layout(**PLOT_LAYOUT, height=350)
            st.plotly_chart(fig_comp, use_container_width=True)


# ═══════════════════════════════════════════════════════════
# TAB 6 — AI INSIGHTS
# ═══════════════════════════════════════════════════════════
with tab_forecast:
    st.markdown('<div class="section-title">🤖 Auto-Generated Climate Insights</div>', unsafe_allow_html=True)

    yearly_ai = filtered_df.groupby("year")["avg_temp"].mean().reset_index()
    if len(yearly_ai) >= 3:
        coeffs = np.polyfit(yearly_ai["year"], yearly_ai["avg_temp"], 1)
        warming_rate = coeffs[0]
        trend_dir = "warming" if warming_rate > 0 else "cooling"
        color_dir = "#ef4444" if warming_rate > 0 else "#3b82f6"
        st.markdown(f"""
        <div class="insight-box">
            📊 <strong>Warming Trend:</strong> The selected data shows a <strong style="color:{color_dir}">
            {trend_dir} trend of {abs(warming_rate):.3f}°C per year</strong>.
            Over a decade that projects to <strong style="color:{color_dir}">{abs(warming_rate*10):.2f}°C</strong> change.
        </div>""", unsafe_allow_html=True)

    hottest_month = filtered_df.groupby("month")["tmax"].mean().idxmax()
    coldest_month = filtered_df.groupby("month")["tmin"].mean().idxmin()
    st.markdown(f"""
    <div class="insight-box">
        🌞 <strong>Seasonal Patterns:</strong> Historically, <strong>{MONTH_NAMES[hottest_month]}</strong> is
        the hottest month and <strong>{MONTH_NAMES[coldest_month]}</strong> is the coldest in the selected data.
    </div>""", unsafe_allow_html=True)

    hot_pct = round(hot_days / len(filtered_df) * 100, 2)
    cold_pct = round(cold_days / len(filtered_df) * 100, 2)
    st.markdown(f"""
    <div class="insight-box">
        🌡️ <strong>Extreme Days:</strong> <strong style="color:#ef4444">{hot_pct}%</strong> of days
        exceeded {heatwave_thresh}°C (heatwave threshold) and
        <strong style="color:#3b82f6">{cold_pct}%</strong> fell below {coldwave_thresh}°C (cold wave threshold).
    </div>""", unsafe_allow_html=True)

    diurnal_trend = filtered_df.groupby("year")["diurnal_range"].mean().reset_index()
    if len(diurnal_trend) >= 3:
        d_coeff = np.polyfit(diurnal_trend["year"], diurnal_trend["diurnal_range"], 1)[0]
        st.markdown(f"""
        <div class="insight-box">
            📉 <strong>Diurnal Range Trend:</strong> The gap between daily high and low temperatures is
            <strong>{"widening" if d_coeff > 0 else "narrowing"}</strong> at
            <strong>{abs(d_coeff):.4f}°C/year</strong>.
            Narrowing ranges can indicate increased humidity or cloud cover.
        </div>""", unsafe_allow_html=True)

    # FORECAST CHART
    st.markdown('<div class="section-title">📡 Linear Projection (Next 5 Years)</div>', unsafe_allow_html=True)
    if len(yearly_ai) >= 5:
        future_years = np.arange(yearly_ai["year"].min(), yearly_ai["year"].max() + 6)
        projected = np.polyval(coeffs, future_years)
        hist_years = yearly_ai["year"].values
        hist_temps = yearly_ai["avg_temp"].values

        fig_proj = go.Figure()
        fig_proj.add_trace(go.Scatter(x=hist_years, y=hist_temps, mode="lines+markers",
                                      name="Historical", line=dict(color="#06b6d4", width=2.5)))
        fig_proj.add_trace(go.Scatter(
            x=future_years[len(hist_years)-1:], y=projected[len(hist_years)-1:],
            mode="lines+markers", name="Projected",
            line=dict(color="#f97316", width=2, dash="dash"),
            marker=dict(symbol="diamond", size=8)
        ))
        fig_proj.add_vrect(x0=yearly_ai["year"].max(), x1=future_years[-1],
                           fillcolor="rgba(249,115,22,0.05)", line_width=0)
        fig_proj.update_layout(**PLOT_LAYOUT, height=380,
                               title="Historical Avg Temperature + 5-Year Linear Projection")
        st.plotly_chart(fig_proj, use_container_width=True)

    st.markdown("""
    <div class="insight-box" style="border-color:rgba(234,179,8,0.3);color:#fde68a">
        ⚠️ <strong>Disclaimer:</strong> Projections use simple linear regression and are for academic demonstration only.
        Real-world climate forecasting requires complex numerical models.
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# RAW DATA PREVIEW
# ─────────────────────────────────────────────
with st.expander("📋 Raw Data Preview (first 200 rows)"):
    st.dataframe(
        filtered_df[["date","station","year","month","day","tmax","tmin","avg_temp","diurnal_range","season"]]
        .head(200)
        .style.format({"tmax":"{:.1f}","tmin":"{:.1f}","avg_temp":"{:.1f}","diurnal_range":"{:.1f}"}),
        use_container_width=True
    )

st.markdown("""
<div style="text-align:center;color:#334155;font-size:0.75rem;margin-top:3rem;padding:1rem;
border-top:1px solid rgba(59,130,246,0.1)">
ClimateIQ Dashboard · Final Year Project · Built with Streamlit + PostgreSQL + Plotly
</div>""", unsafe_allow_html=True)