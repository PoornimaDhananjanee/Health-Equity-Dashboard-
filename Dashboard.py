import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Health, Nutrition & Population Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .metric-card {
        background: white;
        padding: 1rem 1.4rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        text-align: center;
    }
    .metric-card h3 { font-size: 2rem; color: #2563eb; margin: 0; }
    .metric-card p  { font-size: 0.85rem; color: #6b7280; margin: 0; }
    .section-title  { font-size: 1.15rem; font-weight: 700; color: #1e293b; margin-bottom: 0.3rem; }
</style>
""", unsafe_allow_html=True)

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    FILE = "P_Data_Extract_From_Health_Nutrition_and_Population_Statistics_by_Wealth_Quintile.xlsx"

    # Auto-detect the correct sheet (no hardcoded "Data")
    xl = pd.ExcelFile(FILE)
    sheet_name = xl.sheet_names[0]
    for s in xl.sheet_names:
        tmp = xl.parse(s, nrows=3)
        if "Series Name" in tmp.columns:
            sheet_name = s
            break

    df = xl.parse(sheet_name)
    df = df.dropna(subset=["Series Name"])

    # Normalise column names to strings
    df.columns = [str(c).strip() for c in df.columns]

    # Detect year columns (e.g. "2012 [YR2012]" or plain "2012")
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

all_countries   = sorted(long_df["Country Name"].unique())
all_indicators  = sorted(long_df["Base Indicator"].unique())
all_years       = sorted(long_df["Year"].unique())
quintile_order  = ["Q1 (Poorest)", "Q2", "Q3", "Q4", "Q5 (Richest)"]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/8/87/Color_icon_blue.svg",
             width=40)
    st.title("Filters")

    page = st.radio(
        "📄 Page",
        ["Overview", "Country Deep-Dive", "Inequality (Q1 vs Q5)", "Global Map", "Data Table"],
    )

    st.markdown("---")

    selected_indicator = st.selectbox(
        "📊 Indicator",
        all_indicators,
        index=all_indicators.index("Total fertility rate (TFR) (births per woman)")
        if "Total fertility rate (TFR) (births per woman)" in all_indicators
        else 0,
    )

    selected_countries = st.multiselect(
        "🌍 Countries",
        all_countries,
        default=["Bangladesh", "Nigeria", "India", "Brazil", "Indonesia"]
        if all(c in all_countries for c in ["Bangladesh", "Nigeria", "India", "Brazil", "Indonesia"])
        else all_countries[:5],
    )

    selected_year = st.select_slider("📅 Year", options=all_years, value=all_years[-1])

    selected_quintiles = st.multiselect(
        "💰 Wealth Quintiles",
        quintile_order,
        default=quintile_order,
    )

# ── Helper filter ─────────────────────────────────────────────────────────────
def base_filter(countries=None, indicator=None, year=None, quintiles=None):
    d = long_df.copy()
    if countries:
        d = d[d["Country Name"].isin(countries)]
    if indicator:
        d = d[d["Base Indicator"] == indicator]
    if year:
        d = d[d["Year"] == year]
    if quintiles:
        d = d[d["Quintile"].isin(quintiles)]
    return d

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
if page == "Overview":
    st.title("🌍 Health, Nutrition & Population Statistics")
    st.caption("World Bank data disaggregated by wealth quintile (2012–2021)")

    # KPI row
    total_countries = long_df["Country Name"].nunique()
    total_indicators = long_df["Base Indicator"].nunique()
    total_records = len(long_df)
    years_covered = f"{all_years[0]}–{all_years[-1]}"

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label in [
        (c1, total_countries, "Countries"),
        (c2, total_indicators, "Indicators"),
        (c3, f"{total_records:,}", "Data Points"),
        (c4, years_covered, "Years Covered"),
    ]:
        col.markdown(
            f'<div class="metric-card"><h3>{val}</h3><p>{label}</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Chart 1: Quintile trend for selected indicator + countries
    st.markdown(f'<p class="section-title">📈 Trend by Wealth Quintile — {selected_indicator}</p>',
                unsafe_allow_html=True)

    d = base_filter(
        countries=selected_countries if selected_countries else all_countries[:5],
        indicator=selected_indicator,
        quintiles=selected_quintiles,
    )
    if not d.empty and len(selected_countries) == 1:
        fig = px.line(
            d.groupby(["Year", "Quintile"], as_index=False)["Value"].mean(),
            x="Year", y="Value", color="Quintile",
            color_discrete_sequence=px.colors.sequential.Blues_r,
            markers=True,
        )
        fig.update_layout(template="plotly_white", height=380, margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)
    elif not d.empty:
        fig = px.line(
            d.groupby(["Year", "Quintile"], as_index=False)["Value"].mean(),
            x="Year", y="Value", color="Quintile",
            color_discrete_sequence=px.colors.sequential.Blues_r,
            markers=True,
            title=f"Average across selected countries",
        )
        fig.update_layout(template="plotly_white", height=380, margin=dict(t=30))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for the selected filters.")

    st.markdown("---")

    # ── Chart 2: Bar chart — latest year, Q1 vs Q5 across countries
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown(f'<p class="section-title">📊 Q1 vs Q5 — {selected_year}</p>',
                    unsafe_allow_html=True)
        d2 = base_filter(
            countries=selected_countries if selected_countries else all_countries[:8],
            indicator=selected_indicator,
            year=selected_year,
            quintiles=["Q1 (Poorest)", "Q5 (Richest)"],
        )
        if not d2.empty:
            fig2 = px.bar(
                d2,
                x="Country Name", y="Value", color="Quintile",
                barmode="group",
                color_discrete_map={"Q1 (Poorest)": "#ef4444", "Q5 (Richest)": "#22c55e"},
            )
            fig2.update_layout(template="plotly_white", height=340,
                                xaxis_tickangle=-30, margin=dict(t=10))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No data available.")

    with col_r:
        st.markdown(f'<p class="section-title">🥧 Quintile Distribution — {selected_year}</p>',
                    unsafe_allow_html=True)
        d3 = base_filter(
            countries=selected_countries if selected_countries else all_countries[:5],
            indicator=selected_indicator,
            year=selected_year,
            quintiles=selected_quintiles,
        )
        if not d3.empty:
            pie_data = d3.groupby("Quintile", as_index=False)["Value"].mean()
            fig3 = px.pie(
                pie_data, names="Quintile", values="Value",
                color_discrete_sequence=px.colors.sequential.RdBu,
                hole=0.4,
            )
            fig3.update_layout(height=340, margin=dict(t=10))
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No data available.")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 — COUNTRY DEEP-DIVE
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Country Deep-Dive":
    st.title("🔍 Country Deep-Dive")

    country = st.selectbox("Select a country", all_countries,
                            index=all_countries.index("Bangladesh")
                            if "Bangladesh" in all_countries else 0)

    d = long_df[long_df["Country Name"] == country]

    st.markdown(f"### {country} — {selected_indicator}")

    d_ind = d[d["Base Indicator"] == selected_indicator]
    if not d_ind.empty:
        fig = px.line(
            d_ind[d_ind["Quintile"].isin(selected_quintiles)],
            x="Year", y="Value", color="Quintile",
            markers=True,
            color_discrete_sequence=px.colors.sequential.Plasma_r,
        )
        fig.update_layout(template="plotly_white", height=380, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for this indicator and country.")

    # Heatmap: all indicators × quintile for latest available year per indicator
    st.markdown("---")
    st.markdown(f"#### Indicator Heatmap — All indicators, latest value (Q1 vs Q5)")

    pivot = (
        d[d["Quintile"].isin(["Q1 (Poorest)", "Q5 (Richest)"])]
        .sort_values("Year")
        .groupby(["Base Indicator", "Quintile"])["Value"]
        .last()
        .unstack("Quintile")
        .dropna()
    )

    if not pivot.empty:
        pivot["Inequality Ratio (Q5/Q1)"] = pivot["Q5 (Richest)"] / pivot["Q1 (Poorest)"].replace(0, np.nan)
        top_indicators = pivot["Inequality Ratio (Q5/Q1)"].abs().nlargest(20).index
        heat_data = pivot.loc[top_indicators].reset_index()

        fig_h = go.Figure(
            go.Heatmap(
                z=heat_data[["Q1 (Poorest)", "Q5 (Richest)"]].values.T,
                x=heat_data["Base Indicator"].str[:40],
                y=["Q1 (Poorest)", "Q5 (Richest)"],
                colorscale="RdYlGn",
                hoverongaps=False,
            )
        )
        fig_h.update_layout(
            template="plotly_white", height=400,
            xaxis_tickangle=-40, margin=dict(t=10, b=150),
        )
        st.plotly_chart(fig_h, use_container_width=True)
    else:
        st.info("Not enough data for heatmap.")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 3 — INEQUALITY
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Inequality (Q1 vs Q5)":
    st.title("⚖️ Wealth Inequality Explorer")
    st.caption("Compares poorest (Q1) vs richest (Q5) quintile across countries")

    d = base_filter(
        indicator=selected_indicator,
        year=selected_year,
        quintiles=["Q1 (Poorest)", "Q5 (Richest)"],
    )

    pivot = (
        d.groupby(["Country Name", "Quintile"])["Value"]
        .mean()
        .unstack("Quintile")
        .dropna()
        .reset_index()
    )
    pivot.columns.name = None
    pivot["Gap (Q5 - Q1)"] = pivot["Q5 (Richest)"] - pivot["Q1 (Poorest)"]
    pivot["Ratio (Q5/Q1)"] = pivot["Q5 (Richest)"] / pivot["Q1 (Poorest)"].replace(0, np.nan)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Top 15 Countries by Inequality Gap")
        top15 = pivot.nlargest(15, "Gap (Q5 - Q1)")
        fig = px.bar(
            top15, x="Gap (Q5 - Q1)", y="Country Name", orientation="h",
            color="Gap (Q5 - Q1)", color_continuous_scale="Reds",
        )
        fig.update_layout(template="plotly_white", height=450,
                           yaxis=dict(autorange="reversed"), margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Q1 vs Q5 Scatter")
        fig2 = px.scatter(
            pivot, x="Q1 (Poorest)", y="Q5 (Richest)", hover_name="Country Name",
            color="Gap (Q5 - Q1)", size="Ratio (Q5/Q1)",
            color_continuous_scale="RdYlGn_r",
        )
        fig2.add_shape(type="line",
                        x0=pivot["Q1 (Poorest)"].min(), x1=pivot["Q1 (Poorest)"].max(),
                        y0=pivot["Q1 (Poorest)"].min(), y1=pivot["Q1 (Poorest)"].max(),
                        line=dict(color="gray", dash="dash"))
        fig2.update_layout(template="plotly_white", height=450, margin=dict(t=10))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Full Country Table")
    st.dataframe(
        pivot.sort_values("Gap (Q5 - Q1)", ascending=False)
             .round(2)
             .reset_index(drop=True),
        use_container_width=True,
        height=350,
    )

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 4 — GLOBAL MAP
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Global Map":
    st.title("🗺️ Global Choropleth Map")

    quintile_sel = st.selectbox("Select Quintile", quintile_order, index=0)

    d = base_filter(
        indicator=selected_indicator,
        year=selected_year,
        quintiles=[quintile_sel],
    )
    map_data = d.groupby(["Country Name", "Country Code"], as_index=False)["Value"].mean()

    if not map_data.empty:
        fig = px.choropleth(
            map_data,
            locations="Country Code",
            color="Value",
            hover_name="Country Name",
            color_continuous_scale="YlOrRd",
            title=f"{selected_indicator} — {quintile_sel} — {selected_year}",
        )
        fig.update_layout(
            geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
            height=520,
            margin=dict(t=50),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected combination.")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 5 — DATA TABLE
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Data Table":
    st.title("📋 Raw Data Explorer")

    d = base_filter(
        countries=selected_countries if selected_countries else None,
        indicator=selected_indicator,
        quintiles=selected_quintiles if selected_quintiles else None,
    )
    d_show = (
        d[["Country Name", "Country Code", "Base Indicator", "Quintile", "Year", "Value"]]
        .sort_values(["Country Name", "Year"])
        .reset_index(drop=True)
    )

    st.write(f"**{len(d_show):,} rows** matching current filters")
    st.dataframe(d_show, use_container_width=True, height=500)

    csv = d_show.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, "filtered_data.csv", "text/csv")
