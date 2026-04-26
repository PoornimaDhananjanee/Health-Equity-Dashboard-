import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Health Equity by Wealth Quintile",
    layout="wide",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] { background: #0f2044; }
    .block-container { padding-top: 1rem !important; }
    [data-testid="stSidebar"] * { color: #e8f0fe !important; }
    [data-testid="stSidebar"] .stRadio label { font-size: 1.05rem !important; font-weight: 600 !important; padding: 6px 0 !important; }
    [data-testid="stSidebar"] .stRadio > div { gap: 6px !important; }
    [data-testid="stSidebar"] p { font-size: 0.95rem !important; }
    [data-testid="stSidebar"] hr { border-color: #2a4a8a !important; margin: 12px 0 !important; }
    .metric-card {
        background: linear-gradient(135deg, #1a3a6b 0%, #0f2044 100%);
        border-radius: 12px;
        padding: 18px 22px;
        color: white;
        margin-bottom: 8px;
        border-left: 4px solid #4a9eff;
    }
    .metric-card h3 { font-size: 0.85rem; margin: 0 0 6px 0; opacity: 0.75; }
    .metric-card .val { font-size: 2rem; font-weight: 700; }
    .metric-card .sub { font-size: 0.8rem; opacity: 0.65; margin-top: 4px; }
    .section-header {
        font-size: 1.15rem; font-weight: 600; color: #1a3a6b;
        border-bottom: 2px solid #4a9eff; padding-bottom: 6px; margin: 24px 0 14px 0;
    }
    .insight-box {
        background: #f0f6ff; border-left: 4px solid #4a9eff;
        border-radius: 6px; padding: 12px 16px; font-size: 0.9rem; margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("P_Data_Extract_From_Health_Nutrition_and_Population_Statistics_by_Wealth_Quintile.xlsx")
    year_cols = [c for c in df.columns if "YR" in c]
    df[year_cols] = df[year_cols].replace("..", np.nan).apply(pd.to_numeric, errors="coerce")

    df_long = df.melt(
        id_vars=["Country Name", "Country Code", "Series Name", "Series Code"],
        value_vars=year_cols,
        var_name="Year",
        value_name="Value",
    )
    df_long["Year"] = df_long["Year"].str.extract(r"(\d{4})").astype(int)
    df_long = df_long.dropna(subset=["Value"])

    df_long["Quintile"] = df_long["Series Name"].str.extract(r"(Q\d)")
    df_long["Quintile_Label"] = df_long["Series Name"].str.extract(r"(Q\d \([^)]+\)|Q\d$)")
    df_long["Quintile_Label"] = df_long["Quintile_Label"].str.strip()
    df_long["Indicator"] = (
        df_long["Series Name"]
        .str.replace(r":\s*Q\d.*$", "", regex=True)
        .str.strip()
    )

    # Short indicator names
    indicator_map = {
        "Total fertility rate (TFR) (births per woman)": "Fertility Rate (TFR)",
        "Antenatal care (any skilled personnel) (% of women with a birth)": "Antenatal Care – Any Skilled",
        "Antenatal care (doctor) (% of women with a birth)": "Antenatal Care – Doctor",
        "Anti-malarial drug use by pregnant women (SP/Fansidar two or more doses) (% of women with a birth)": "Anti-Malarial Drug Use",
    }
    df_long["Indicator_Short"] = df_long["Indicator"].map(indicator_map).fillna(df_long["Indicator"])

    quintile_order = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4, "Q5": 5}
    df_long["Q_num"] = df_long["Quintile"].map(quintile_order)
    df_long = df_long.sort_values(["Country Name", "Indicator", "Q_num", "Year"])

    return df_long

df = load_data()

countries = sorted(df["Country Name"].unique())
indicators = sorted(df["Indicator_Short"].unique())
years = sorted(df["Year"].unique())

QUINTILE_COLORS = {
    "Q1": "#d62728",  # poorest – red
    "Q2": "#ff7f0e",
    "Q3": "#bcbd22",
    "Q4": "#2ca02c",
    "Q5": "#1f77b4",  # richest – blue
}
QUINTILE_LABELS = {
    "Q1": "Q1 – Poorest",
    "Q2": "Q2",
    "Q3": "Q3 – Middle",
    "Q4": "Q4",
    "Q5": "Q5 – Richest",
}

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="text-align:center; padding: 20px 0 10px 0;">
    <div style="font-size: 3.5rem; line-height:1;">🌍</div>
    <div style="font-size: 1.4rem; font-weight: 800; color: white; margin-top: 10px; line-height: 1.2;">
        Health Equity Explorer
    </div>
    <div style="font-size: 0.78rem; color: #a8c4f0; margin-top: 8px; line-height: 1.4;">
        World Bank – Health, Nutrition &amp;<br>Population by Wealth Quintile
    </div>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["📊 Overview", "🔍 Country Deep-Dive", "🌐 Cross-Country Compare", "📈 Inequality Gap", "ℹ️ About"],
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Filters**")

sel_countries = st.sidebar.multiselect(
    "Countries", countries, default=[]
)
sel_indicator = st.sidebar.selectbox("Indicator", indicators, index=0)
sel_year = st.sidebar.selectbox("Year (where applicable)", years, index=len(years) - 1)

if not sel_countries:
    sel_countries = countries[:5]

# ── Helper: filter ─────────────────────────────────────────────────────────────
def filt(countries=None, indicator=None, year=None):
    d = df.copy()
    if countries:
        d = d[d["Country Name"].isin(countries)]
    if indicator:
        d = d[d["Indicator_Short"] == indicator]
    if year:
        d = d[d["Year"] == year]
    return d

# ──────────────────────────────────────────────────────────────────────────────
# PAGE 1 – OVERVIEW
# ──────────────────────────────────────────────────────────────────────────────
if page == "📊 Overview":
    st.markdown("<h1 style='text-align:center; color:white;'>🌍 Global Health Equity by Wealth Quintile</h1>", unsafe_allow_html=True)
    st.markdown(
        "Health outcomes vary dramatically between the richest and poorest populations. "
        "This dashboard explores how **antenatal care access**, **fertility rates**, and "
        "**maternal health interventions** differ across wealth quintiles in countries worldwide."
    )

    # KPI row
    d_all = filt(sel_countries, sel_indicator)
    d_q1 = d_all[d_all["Quintile"] == "Q1"]["Value"].mean()
    d_q5 = d_all[d_all["Quintile"] == "Q5"]["Value"].mean()
    gap = abs(d_q5 - d_q1)
    n_countries = d_all["Country Name"].nunique()
    n_years = d_all["Year"].nunique()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <h3>Countries with Data</h3><div class="val">{n_countries}</div>
            <div class="sub">in selection</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <h3>Avg – Poorest (Q1)</h3><div class="val">{d_q1:.1f}</div>
            <div class="sub">{sel_indicator}</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <h3>Avg – Richest (Q5)</h3><div class="val">{d_q5:.1f}</div>
            <div class="sub">{sel_indicator}</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
            <h3>Wealth Gap</h3><div class="val">{gap:.1f}</div>
            <div class="sub">Q5 minus Q1 (avg)</div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Indicator by Wealth Quintile – Selected Countries</div>', unsafe_allow_html=True)

    # Latest year per country per indicator
    d_latest = (
        d_all.sort_values("Year")
        .groupby(["Country Name", "Quintile", "Q_num"], as_index=False)
        .last()
    )
    d_latest["Q_label"] = d_latest["Quintile"].map(QUINTILE_LABELS)

    fig = px.bar(
        d_latest.sort_values(["Country Name", "Q_num"]),
        x="Country Name",
        y="Value",
        color="Quintile",
        barmode="group",
        color_discrete_map=QUINTILE_COLORS,
        labels={"Value": sel_indicator, "Country Name": ""},
        title=f"{sel_indicator} — Latest Available Year by Wealth Quintile",
        height=420,
    )
    fig.update_layout(legend_title="Wealth Quintile", plot_bgcolor="white", paper_bgcolor="white")
    fig.update_xaxes(tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

    # Heatmap – all indicators, all countries (latest year)
    st.markdown('<div class="section-header">Health Equity Heatmap – Inequality Gap (Q5 − Q1)</div>', unsafe_allow_html=True)

    gaps = []
    for ind in indicators:
        for ctry in countries:
            d_sub = df[(df["Country Name"] == ctry) & (df["Indicator_Short"] == ind)]
            if d_sub.empty:
                continue
            latest = d_sub["Year"].max()
            q1v = d_sub[(d_sub["Year"] == latest) & (d_sub["Quintile"] == "Q1")]["Value"].values
            q5v = d_sub[(d_sub["Year"] == latest) & (d_sub["Quintile"] == "Q5")]["Value"].values
            if len(q1v) and len(q5v):
                gaps.append({"Country": ctry, "Indicator": ind, "Gap": round(q5v[0] - q1v[0], 2)})

    if gaps:
        gap_df = pd.DataFrame(gaps)
        pivot = gap_df.pivot(index="Indicator", columns="Country", values="Gap")
        fig2 = px.imshow(
            pivot,
            color_continuous_scale="RdYlGn",
            color_continuous_midpoint=0,
            text_auto=".1f",
            aspect="auto",
            title="Inequality Gap (Richest Q5 − Poorest Q1) — Positive = richest better off",
            height=320,
        )
        fig2.update_layout(paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

    # Insights
    st.markdown('<div class="section-header">🔑 Key Insights</div>', unsafe_allow_html=True)
    for txt in [
        "Antenatal care access consistently favours wealthier quintiles — the richest populations often see 20–40 percentage points higher coverage than the poorest.",
        "Fertility rates show the opposite pattern: in most countries, poorer quintiles have higher fertility rates, reflecting less access to family planning services.",
        "Bangladesh shows the most complete time-series data, revealing sustained inequality improvements over a decade.",
        "Benin shows the largest anti-malarial drug use gaps by wealth quintile among African nations in the dataset.",
    ]:
        st.markdown(f'<div class="insight-box">💡 {txt}</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 2 – COUNTRY DEEP-DIVE
# ──────────────────────────────────────────────────────────────────────────────
elif page == "🔍 Country Deep-Dive":
    st.title("Country Deep-Dive")

    country = st.selectbox("Select a country", countries, index=countries.index("Bangladesh") if "Bangladesh" in countries else 0)
    d_country = df[df["Country Name"] == country]
    avail_indicators = sorted(d_country["Indicator_Short"].unique())

    if not avail_indicators:
        st.warning("No data available for this country.")
    else:
        ind = st.selectbox("Select indicator", avail_indicators)
        d_ind = d_country[d_country["Indicator_Short"] == ind].sort_values(["Year", "Q_num"])

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="section-header">Trend Over Time by Quintile</div>', unsafe_allow_html=True)
            if d_ind["Year"].nunique() > 1:
                fig = px.line(
                    d_ind,
                    x="Year",
                    y="Value",
                    color="Quintile",
                    markers=True,
                    color_discrete_map=QUINTILE_COLORS,
                    labels={"Value": ind},
                    title=f"{country} — {ind}",
                    height=370,
                )
                fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                st.plotly_chart(fig, use_container_width=True)
            else:
                yr = d_ind["Year"].max()
                fig = px.bar(
                    d_ind[d_ind["Year"] == yr].sort_values("Q_num"),
                    x="Quintile",
                    y="Value",
                    color="Quintile",
                    color_discrete_map=QUINTILE_COLORS,
                    labels={"Value": ind},
                    title=f"{country} — {ind} ({yr})",
                    height=370,
                )
                fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="section-header">Quintile Breakdown (Latest Year)</div>', unsafe_allow_html=True)
            latest_yr = d_ind["Year"].max()
            d_latest = d_ind[d_ind["Year"] == latest_yr].sort_values("Q_num")

            fig2 = go.Figure(go.Bar(
                x=d_latest["Quintile"].tolist(),
                y=d_latest["Value"].tolist(),
                marker_color=[QUINTILE_COLORS[q] for q in d_latest["Quintile"]],
                text=d_latest["Value"].round(1).tolist(),
                textposition="outside",
            ))
            fig2.update_layout(
                title=f"Latest data: {latest_yr}",
                xaxis_title="Wealth Quintile (Q1=Poorest, Q5=Richest)",
                yaxis_title=ind,
                plot_bgcolor="white", paper_bgcolor="white",
                height=370,
                showlegend=False,
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Show all indicators as small multiples
        st.markdown('<div class="section-header">All Indicators — Latest Year Snapshot</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(avail_indicators), 2))
        for i, ind2 in enumerate(avail_indicators):
            d2 = d_country[d_country["Indicator_Short"] == ind2]
            latest_yr2 = d2["Year"].max()
            d2_latest = d2[d2["Year"] == latest_yr2].sort_values("Q_num")
            with cols[i % 2]:
                fig3 = px.bar(
                    d2_latest,
                    x="Quintile",
                    y="Value",
                    color="Quintile",
                    color_discrete_map=QUINTILE_COLORS,
                    title=f"{ind2} ({latest_yr2})",
                    labels={"Value": ""},
                    height=260,
                )
                fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white", showlegend=False, margin=dict(t=40, b=20))
                st.plotly_chart(fig3, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 3 – CROSS-COUNTRY COMPARE
# ──────────────────────────────────────────────────────────────────────────────
elif page == "🌐 Cross-Country Compare":
    st.title("Cross-Country Comparison")
    st.markdown("Compare how a single wealth quintile performs across multiple countries.")

    col1, col2 = st.columns(2)
    with col1:
        comp_indicator = st.selectbox("Indicator", indicators, key="comp_ind")
    with col2:
        comp_quintile = st.selectbox("Wealth Quintile", ["Q1", "Q2", "Q3", "Q4", "Q5"],
                                     format_func=lambda q: QUINTILE_LABELS[q])

    d_comp = df[
        (df["Indicator_Short"] == comp_indicator) &
        (df["Quintile"] == comp_quintile)
    ]

    # Latest value per country
    d_comp_latest = (
        d_comp.sort_values("Year")
        .groupby("Country Name", as_index=False)
        .last()
        .sort_values("Value", ascending=True)
    )

    st.markdown('<div class="section-header">Country Ranking</div>', unsafe_allow_html=True)
    fig = px.bar(
        d_comp_latest,
        x="Value",
        y="Country Name",
        orientation="h",
        color="Value",
        color_continuous_scale="Blues",
        labels={"Value": comp_indicator, "Country Name": ""},
        title=f"{comp_indicator} — {QUINTILE_LABELS[comp_quintile]} — Latest Available Data",
        height=420,
        text="Value",
    )
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    # Q1 vs Q5 scatter for selected indicator
    st.markdown('<div class="section-header">Richest vs Poorest — Scatter Plot</div>', unsafe_allow_html=True)
    scatter_rows = []
    for ctry in countries:
        d_sub = df[(df["Country Name"] == ctry) & (df["Indicator_Short"] == comp_indicator)]
        if d_sub.empty:
            continue
        latest = d_sub["Year"].max()
        q1v = d_sub[(d_sub["Year"] == latest) & (d_sub["Quintile"] == "Q1")]["Value"].values
        q5v = d_sub[(d_sub["Year"] == latest) & (d_sub["Quintile"] == "Q5")]["Value"].values
        if len(q1v) and len(q5v):
            scatter_rows.append({"Country": ctry, "Q1 (Poorest)": q1v[0], "Q5 (Richest)": q5v[0], "Year": latest})

    if scatter_rows:
        sdf = pd.DataFrame(scatter_rows)
        mn = min(sdf["Q1 (Poorest)"].min(), sdf["Q5 (Richest)"].min()) * 0.9
        mx = max(sdf["Q1 (Poorest)"].max(), sdf["Q5 (Richest)"].max()) * 1.05
        fig2 = px.scatter(
            sdf, x="Q1 (Poorest)", y="Q5 (Richest)", text="Country",
            labels={"Q1 (Poorest)": f"{comp_indicator} — Q1 (Poorest)", "Q5 (Richest)": f"{comp_indicator} — Q5 (Richest)"},
            title="Points above the diagonal = richer quintile has higher value",
            height=430,
        )
        fig2.add_shape(type="line", x0=mn, y0=mn, x1=mx, y1=mx,
                       line=dict(color="grey", dash="dash"))
        fig2.update_traces(textposition="top center", marker=dict(size=10, color="#1a3a6b"))
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Grey dashed line = equality line. Points above → richest better off; below → poorest better off.")


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 4 – INEQUALITY GAP
# ──────────────────────────────────────────────────────────────────────────────
elif page == "📈 Inequality Gap":
    st.title("Wealth Inequality Gap Analysis")
    st.markdown(
        "The **inequality gap** is calculated as Q5 (richest) minus Q1 (poorest). "
        "A positive gap means the richest quintile has a higher value — for antenatal care "
        "this means *better access*; for fertility rate it reflects a different dynamic."
    )

    gap_rows = []
    for ctry in countries:
        for ind in indicators:
            d_sub = df[(df["Country Name"] == ctry) & (df["Indicator_Short"] == ind)]
            for yr in sorted(d_sub["Year"].unique()):
                d_yr = d_sub[d_sub["Year"] == yr]
                q1v = d_yr[d_yr["Quintile"] == "Q1"]["Value"].values
                q5v = d_yr[d_yr["Quintile"] == "Q5"]["Value"].values
                if len(q1v) and len(q5v):
                    gap_rows.append({
                        "Country": ctry, "Indicator": ind, "Year": yr,
                        "Gap (Q5−Q1)": round(q5v[0] - q1v[0], 2),
                        "Q1": q1v[0], "Q5": q5v[0],
                    })

    gap_df = pd.DataFrame(gap_rows)

    col1, col2 = st.columns(2)
    with col1:
        gap_ind = st.selectbox("Indicator", indicators, key="gap_ind")
    with col2:
        gap_countries = st.multiselect("Countries", countries, default=sel_countries[:5], key="gap_ctry")

    if not gap_countries:
        gap_countries = countries[:5]

    d_gap = gap_df[(gap_df["Indicator"] == gap_ind) & (gap_df["Country"].isin(gap_countries))]

    st.markdown('<div class="section-header">Inequality Gap Over Time</div>', unsafe_allow_html=True)
    if d_gap["Year"].nunique() > 1:
        fig = px.line(
            d_gap, x="Year", y="Gap (Q5−Q1)", color="Country",
            markers=True,
            title=f"Wealth Inequality Gap — {gap_ind}",
            labels={"Gap (Q5−Q1)": "Gap (Q5 − Q1)"},
            height=380,
        )
    else:
        fig = px.bar(
            d_gap.sort_values("Gap (Q5−Q1)"), x="Country", y="Gap (Q5−Q1)",
            color="Country",
            title=f"Wealth Inequality Gap — {gap_ind}",
            height=380,
        )
    fig.add_hline(y=0, line_dash="dash", line_color="grey", annotation_text="No gap")
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">Gap Summary Table</div>', unsafe_allow_html=True)
    latest_gaps = (
        d_gap.sort_values("Year")
        .groupby("Country", as_index=False)
        .last()[["Country", "Year", "Q1", "Q5", "Gap (Q5−Q1)"]]
        .sort_values("Gap (Q5−Q1)", ascending=False)
    )
    latest_gaps.columns = ["Country", "Latest Year", "Q1 (Poorest)", "Q5 (Richest)", "Gap (Q5−Q1)"]
    st.dataframe(
        latest_gaps.style
        .background_gradient(subset=["Gap (Q5−Q1)"], cmap="RdYlGn")
        .format({"Q1 (Poorest)": "{:.1f}", "Q5 (Richest)": "{:.1f}", "Gap (Q5−Q1)": "{:.1f}"}),
        use_container_width=True,
        hide_index=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 5 – ABOUT
# ──────────────────────────────────────────────────────────────────────────────
elif page == "ℹ️ About":
    st.title("About This Dashboard")
    st.markdown("""
    ### Dataset
    **Health, Nutrition and Population Statistics by Wealth Quintile**  
    Source: [The World Bank](https://data.worldbank.org)

    This dataset captures key maternal and reproductive health indicators across **wealth quintiles (Q1=poorest to Q5=richest)** 
    for countries worldwide, covering years 2012–2021.

    ### Indicators Covered
    | Indicator | Unit |
    |-----------|------|
    | Total Fertility Rate (TFR) | Births per woman |
    | Antenatal Care – Any Skilled Personnel | % of women with a birth |
    | Antenatal Care – Doctor | % of women with a birth |
    | Anti-Malarial Drug Use (SP/Fansidar ≥2 doses) | % of women with a birth |

    ### Methodology
    - Data is reshaped from wide (year columns) to long format for analysis
    - The latest available year is used for cross-country comparisons
    - The **inequality gap** is defined as Q5 (richest) − Q1 (poorest)
    - Countries with no available data are excluded from charts

    ### Purpose
    This dashboard was created to support decision-makers, finance professionals, and 
    global health researchers in understanding **how wealth inequality shapes health outcomes** — 
    a core sustainability concern aligned with **UN SDG 3 (Good Health and Well-Being)** 
    and **SDG 10 (Reduced Inequalities)**.

    ### Tech Stack
    - **Python** · **Streamlit** · **Plotly** · **Pandas**
    - Source data: World Bank Open Data (CC BY 4.0)
    """)
