import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Health & Wealth Inequality Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #1e293b; }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stSlider label { color: #94a3b8 !important; font-size: 0.78rem !important; text-transform: uppercase; letter-spacing: 0.05em; }
    [data-testid="stSidebar"] hr { border-color: #334155; }
    .metric-card {
        background: white;
        padding: 1.1rem 1.4rem;
        border-radius: 14px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.06);
        border-left: 4px solid #2563eb;
        text-align: left;
    }
    .metric-card h3 { font-size: 1.9rem; color: #1e40af; margin: 0; font-weight: 700; }
    .metric-card p  { font-size: 0.82rem; color: #64748b; margin: 0; margin-top: 2px; }
    .section-header {
        font-size: 1.05rem; font-weight: 700; color: #0f172a;
        padding-bottom: 0.3rem;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 0.8rem;
    }
    .insight-box {
        background: #eff6ff;
        border-left: 4px solid #2563eb;
        border-radius: 0 8px 8px 0;
        padding: 0.75rem 1rem;
        font-size: 0.875rem;
        color: #1e40af;
        margin-top: 0.5rem;
    }
    div[data-testid="stMetricValue"] { font-size: 2rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading dataset…")
def load_data():
    FILE = "P_Data_Extract_From_Health_Nutrition_and_Population_Statistics_by_Wealth_Quintile.xlsx"

    xl = pd.ExcelFile(FILE)
    sheet_name = xl.sheet_names[0]
    for s in xl.sheet_names:
        tmp = xl.parse(s, nrows=3)
        if "Series Name" in tmp.columns:
            sheet_name = s
            break

    df = xl.parse(sheet_name)
    df = df.dropna(subset=["Series Name"])
    df.columns = [str(c).strip() for c in df.columns]

    year_cols = [c for c in df.columns if str(c)[:4].isdigit() and str(c)[:2] == "20"]
    df[year_cols] = df[year_cols].replace("..", np.nan)
    for col in year_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if "Country Name" not in df.columns:
        df["Country Name"] = df.iloc[:, 0]
    if "Country Code" not in df.columns:
        df["Country Code"] = df.iloc[:, 1]

    def extract_base(name):
        name = str(name).strip()
        for suffix in [": Q1 (lowest)", ": Q1", ": Q2", ": Q3", ": Q4",
                       ": Q5 (highest)", ": Q5"]:
            if name.endswith(suffix):
                return name[: -len(suffix)].strip()
        return name

    def extract_quintile(name):
        name = str(name)
        if "Q1" in name: return "Q1 (Poorest)"
        if "Q2" in name: return "Q2"
        if "Q3" in name: return "Q3"
        if "Q4" in name: return "Q4"
        if "Q5" in name: return "Q5 (Richest)"
        return "Unknown"

    df["Base Indicator"] = df["Series Name"].apply(extract_base)
    df["Quintile"]       = df["Series Name"].apply(extract_quintile)

    long = df.melt(
        id_vars=["Country Name", "Country Code", "Series Name",
                  "Base Indicator", "Quintile"],
        value_vars=year_cols,
        var_name="Year Label",
        value_name="Value",
    )
    long["Year"] = long["Year Label"].str.extract(r"(\d{4})").astype(int)
    long = long.dropna(subset=["Value"])
    return long, sorted(year_cols)

long_df, year_cols = load_data()

all_countries  = sorted(long_df["Country Name"].unique())
all_indicators = sorted(long_df["Base Indicator"].unique())
all_years      = sorted(long_df["Year"].unique())
quintile_order = ["Q1 (Poorest)", "Q2", "Q3", "Q4", "Q5 (Richest)"]

QUINTILE_COLORS = {
    "Q1 (Poorest)": "#ef4444",
    "Q2":           "#f97316",
    "Q3":           "#eab308",
    "Q4":           "#22c55e",
    "Q5 (Richest)": "#3b82f6",
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌍 HNP Dashboard")
    st.caption("World Bank · Wealth Quintile Data")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["📊 Overview", "🔍 Country Deep-Dive",
         "⚖️ Inequality Explorer", "🗺️ Global Map", "📋 Data Explorer"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("**Filters**")

    default_ind = "Total fertility rate (TFR) (births per woman)"
    selected_indicator = st.selectbox(
        "Indicator",
        all_indicators,
        index=all_indicators.index(default_ind) if default_ind in all_indicators else 0,
    )

    default_countries = [c for c in ["Bangladesh", "Nigeria", "India", "Brazil", "Indonesia"] if c in all_countries]
    selected_countries = st.multiselect("Countries", all_countries, default=default_countries)

    selected_year = st.select_slider("Year", options=all_years, value=all_years[-2])

    selected_quintiles = st.multiselect("Wealth Quintiles", quintile_order, default=quintile_order)

    st.markdown("---")
    st.caption(f"Dataset: {long_df['Country Name'].nunique()} countries · {long_df['Base Indicator'].nunique()} indicators · {len(long_df):,} data points")

# ── Helper ────────────────────────────────────────────────────────────────────
def filter_data(countries=None, indicator=None, year=None, quintiles=None):
    d = long_df.copy()
    if countries:  d = d[d["Country Name"].isin(countries)]
    if indicator:  d = d[d["Base Indicator"] == indicator]
    if year:       d = d[d["Year"] == year]
    if quintiles:  d = d[d["Quintile"].isin(quintiles)]
    return d

def q_colors(qs):
    return [QUINTILE_COLORS.get(q, "#888") for q in qs]

def chart_layout(fig, height=380):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
if page == "📊 Overview":
    st.markdown(f"## 📊 Health, Nutrition & Population Statistics")
    st.caption("Explore World Bank data disaggregated by wealth quintile (2012–2021)")

    # KPI row
    c1, c2, c3, c4 = st.columns(4)
    for col, val, label in [
        (c1, long_df["Country Name"].nunique(), "Countries"),
        (c2, long_df["Base Indicator"].nunique(), "Indicators"),
        (c3, f"{len(long_df):,}", "Data Points"),
        (c4, f"{all_years[0]}–{all_years[-1]}", "Years Covered"),
    ]:
        col.markdown(f'<div class="metric-card"><h3>{val}</h3><p>{label}</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Trend chart
    st.markdown(f'<p class="section-header">📈 Quintile Trend — {selected_indicator}</p>', unsafe_allow_html=True)

    d = filter_data(
        countries=selected_countries or all_countries[:5],
        indicator=selected_indicator,
        quintiles=selected_quintiles,
    )

    if not d.empty:
        trend = d.groupby(["Year", "Quintile"], as_index=False)["Value"].mean()
        fig = px.line(
            trend, x="Year", y="Value", color="Quintile",
            color_discrete_map=QUINTILE_COLORS,
            markers=True, line_shape="spline",
        )
        fig = chart_layout(fig)
        fig.update_traces(line_width=2.5)
        st.plotly_chart(fig, use_container_width=True)

        # Auto-insight
        q1_last = trend[trend["Quintile"] == "Q1 (Poorest)"]["Value"].iloc[-1] if "Q1 (Poorest)" in trend["Quintile"].values else None
        q5_last = trend[trend["Quintile"] == "Q5 (Richest)"]["Value"].iloc[-1] if "Q5 (Richest)" in trend["Quintile"].values else None
        if q1_last and q5_last:
            diff = abs(q1_last - q5_last)
            st.markdown(f'<div class="insight-box">💡 The gap between the poorest (Q1) and richest (Q5) quintile is <strong>{diff:.2f}</strong> units for the most recent available year across selected countries.</div>', unsafe_allow_html=True)
    else:
        st.info("No data for the selected filters.")

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown(f'<p class="section-header">📊 Q1 vs Q5 by Country — {selected_year}</p>', unsafe_allow_html=True)
        d2 = filter_data(
            countries=selected_countries or all_countries[:5],
            indicator=selected_indicator,
            year=selected_year,
            quintiles=["Q1 (Poorest)", "Q5 (Richest)"],
        )
        if not d2.empty:
            fig2 = px.bar(
                d2, x="Country Name", y="Value", color="Quintile",
                barmode="group",
                color_discrete_map=QUINTILE_COLORS,
            )
            fig2 = chart_layout(fig2, 340)
            fig2.update_layout(xaxis_tickangle=-30)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No data available.")

    with col_r:
        st.markdown(f'<p class="section-header">🥧 Quintile Distribution — {selected_year}</p>', unsafe_allow_html=True)
        d3 = filter_data(
            countries=selected_countries or all_countries[:5],
            indicator=selected_indicator,
            year=selected_year,
            quintiles=selected_quintiles,
        )
        if not d3.empty:
            pie_data = d3.groupby("Quintile", as_index=False)["Value"].mean()
            pie_data = pie_data[pie_data["Quintile"].isin(quintile_order)]
            pie_data["Quintile"] = pd.Categorical(pie_data["Quintile"], categories=quintile_order, ordered=True)
            pie_data = pie_data.sort_values("Quintile")
            fig3 = px.pie(
                pie_data, names="Quintile", values="Value",
                color="Quintile", color_discrete_map=QUINTILE_COLORS,
                hole=0.45,
            )
            fig3 = chart_layout(fig3, 340)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No data available.")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 — COUNTRY DEEP-DIVE
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Country Deep-Dive":
    st.markdown("## 🔍 Country Deep-Dive")

    col_a, col_b = st.columns([1, 2])
    with col_a:
        country = st.selectbox(
            "Select Country",
            all_countries,
            index=all_countries.index("Bangladesh") if "Bangladesh" in all_countries else 0,
        )

    d_country = long_df[long_df["Country Name"] == country]

    st.markdown(f"### {country} — {selected_indicator}")
    d_ind = d_country[
        (d_country["Base Indicator"] == selected_indicator) &
        (d_country["Quintile"].isin(selected_quintiles))
    ]

    if not d_ind.empty:
        fig = px.line(
            d_ind, x="Year", y="Value", color="Quintile",
            color_discrete_map=QUINTILE_COLORS,
            markers=True, line_shape="spline",
        )
        fig = chart_layout(fig, 360)
        fig.update_traces(line_width=2.5)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for this indicator and country.")

    # Heatmap
    st.markdown("---")
    st.markdown(f"#### 🔥 Inequality Heatmap — All Indicators (Q1 vs Q5, latest values)")

    pivot = (
        d_country[d_country["Quintile"].isin(["Q1 (Poorest)", "Q5 (Richest)"])]
        .sort_values("Year")
        .groupby(["Base Indicator", "Quintile"])["Value"]
        .last()
        .unstack("Quintile")
        .dropna()
    )

    if not pivot.empty:
        pivot["Inequality Ratio"] = pivot["Q5 (Richest)"] / pivot["Q1 (Poorest)"].replace(0, np.nan)
        top_inds = pivot["Inequality Ratio"].abs().nlargest(20).index
        heat_data = pivot.loc[top_inds].reset_index()

        fig_h = go.Figure(go.Heatmap(
            z=heat_data[["Q1 (Poorest)", "Q5 (Richest)"]].values.T,
            x=heat_data["Base Indicator"].str[:45],
            y=["Q1 (Poorest)", "Q5 (Richest)"],
            colorscale="RdYlGn",
            hoverongaps=False,
        ))
        fig_h.update_layout(
            template="plotly_white", height=360,
            xaxis_tickangle=-40,
            margin=dict(t=10, b=160, l=120, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_h, use_container_width=True)
    else:
        st.info("Not enough data for heatmap.")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 3 — INEQUALITY EXPLORER
# ═════════════════════════════════════════════════════════════════════════════
elif page == "⚖️ Inequality Explorer":
    st.markdown("## ⚖️ Wealth Inequality Explorer")
    st.caption("Comparing the poorest (Q1) vs richest (Q5) quintile across all countries")

    d = filter_data(
        indicator=selected_indicator,
        year=selected_year,
        quintiles=["Q1 (Poorest)", "Q5 (Richest)"],
    )
    pivot = (
        d.groupby(["Country Name", "Country Code", "Quintile"])["Value"]
        .mean()
        .unstack("Quintile")
        .dropna()
        .reset_index()
    )
    pivot.columns.name = None
    if "Q1 (Poorest)" in pivot.columns and "Q5 (Richest)" in pivot.columns:
        pivot["Gap (Q5 - Q1)"]  = pivot["Q5 (Richest)"] - pivot["Q1 (Poorest)"]
        pivot["Ratio (Q5/Q1)"]  = pivot["Q5 (Richest)"] / pivot["Q1 (Poorest)"].replace(0, np.nan)
    else:
        st.warning("Not enough data for the selected filters.")
        st.stop()

    # Summary stats
    c1, c2, c3 = st.columns(3)
    max_gap_row = pivot.loc[pivot["Gap (Q5 - Q1)"].abs().idxmax()]
    c1.metric("Largest Gap", f"{max_gap_row['Country Name']}", f"{max_gap_row['Gap (Q5 - Q1)']:.2f}")
    c2.metric("Countries with data", pivot.shape[0])
    c3.metric("Avg Gap (Q5 − Q1)", f"{pivot['Gap (Q5 - Q1)'].mean():.2f}")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Top 15 Countries by Inequality Gap")
        top15 = pivot.nlargest(15, "Gap (Q5 - Q1)")
        fig = px.bar(
            top15, x="Gap (Q5 - Q1)", y="Country Name", orientation="h",
            color="Gap (Q5 - Q1)", color_continuous_scale="Reds",
        )
        fig = chart_layout(fig, 480)
        fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Q1 vs Q5 Scatter")
        fig2 = px.scatter(
            pivot, x="Q1 (Poorest)", y="Q5 (Richest)",
            hover_name="Country Name",
            color="Gap (Q5 - Q1)", size=pivot["Ratio (Q5/Q1)"].clip(1, 10),
            color_continuous_scale="RdYlGn_r",
            labels={"Q1 (Poorest)": "Q1 — Poorest Quintile", "Q5 (Richest)": "Q5 — Richest Quintile"},
        )
        x_range = [pivot["Q1 (Poorest)"].min(), pivot["Q1 (Poorest)"].max()]
        fig2.add_shape(type="line", x0=x_range[0], x1=x_range[1],
                       y0=x_range[0], y1=x_range[1],
                       line=dict(color="#94a3b8", dash="dash"))
        fig2 = chart_layout(fig2, 480)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Full Country Table")
    display_df = pivot[["Country Name", "Q1 (Poorest)", "Q5 (Richest)", "Gap (Q5 - Q1)", "Ratio (Q5/Q1)"]].sort_values("Gap (Q5 - Q1)", ascending=False).round(2).reset_index(drop=True)
    st.dataframe(display_df, use_container_width=True, height=360)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 4 — GLOBAL MAP
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🗺️ Global Map":
    st.markdown("## 🗺️ Global Choropleth Map")

    col_a, col_b = st.columns(2)
    with col_a:
        quintile_sel = st.selectbox("Select Quintile for Map", quintile_order, index=0)
    with col_b:
        scale_choice = st.selectbox("Colour Scale", ["YlOrRd", "Blues", "RdYlGn", "Viridis"], index=0)

    d = filter_data(indicator=selected_indicator, year=selected_year, quintiles=[quintile_sel])
    map_data = d.groupby(["Country Name", "Country Code"], as_index=False)["Value"].mean()

    if not map_data.empty:
        fig = px.choropleth(
            map_data,
            locations="Country Code",
            color="Value",
            hover_name="Country Name",
            hover_data={"Value": ":.2f", "Country Code": False},
            color_continuous_scale=scale_choice,
            title=f"{selected_indicator[:60]}… | {quintile_sel} | {selected_year}",
        )
        fig.update_layout(
            geo=dict(showframe=False, showcoastlines=True,
                     projection_type="natural earth",
                     showland=True, landcolor="#f1f5f9",
                     showocean=True, oceancolor="#e0f2fe"),
            height=540,
            margin=dict(t=50, b=0, l=0, r=0),
            paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_colorbar=dict(title="Value", thickness=14),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Top & Bottom 5 Countries")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Highest values**")
            st.dataframe(map_data.nlargest(5, "Value")[["Country Name", "Value"]].round(2).reset_index(drop=True), use_container_width=True)
        with c2:
            st.markdown("**Lowest values**")
            st.dataframe(map_data.nsmallest(5, "Value")[["Country Name", "Value"]].round(2).reset_index(drop=True), use_container_width=True)
    else:
        st.info("No data available for the selected combination.")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 5 — DATA EXPLORER
# ═════════════════════════════════════════════════════════════════════════════
elif page == "📋 Data Explorer":
    st.markdown("## 📋 Data Explorer")

    d = filter_data(
        countries=selected_countries or None,
        indicator=selected_indicator,
        quintiles=selected_quintiles or None,
    )
    d_show = (
        d[["Country Name", "Country Code", "Base Indicator", "Quintile", "Year", "Value"]]
        .sort_values(["Country Name", "Year"])
        .reset_index(drop=True)
    )

    st.markdown(f"**{len(d_show):,} rows** match the current filters")

    col_a, col_b = st.columns([2, 1])
    with col_a:
        search = st.text_input("🔍 Search country", placeholder="e.g. Kenya")
        if search:
            d_show = d_show[d_show["Country Name"].str.contains(search, case=False)]

    with col_b:
        year_range = st.slider("Filter by year range", int(all_years[0]), int(all_years[-1]),
                               (int(all_years[0]), int(all_years[-1])))
        d_show = d_show[(d_show["Year"] >= year_range[0]) & (d_show["Year"] <= year_range[1])]

    st.dataframe(d_show, use_container_width=True, height=480)

    csv = d_show.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download as CSV", csv, "hnp_filtered_data.csv", "text/csv")

    # Summary stats
    if not d_show.empty:
        st.markdown("#### Summary Statistics")
        st.dataframe(d_show.groupby("Quintile")["Value"].describe().round(2), use_container_width=True)
