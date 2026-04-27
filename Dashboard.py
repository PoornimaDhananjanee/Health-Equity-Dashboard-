import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HNP Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Mantis Design System CSS ──────────────────────────────────────────────────
import streamlit.components.v1 as components

def inject_css():
    css = """
    <link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"] { font-family: 'Public Sans', sans-serif !important; font-size: 0.875rem; color: #262626; }
    .stApp { background: #f8f9fa !important; }
    [data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e6ebf1 !important; }
    .sidebar-logo { padding: 20px 20px 16px; border-bottom: 1px solid #e6ebf1; margin-bottom: 8px; display: flex; align-items: center; gap: 10px; }
    .sidebar-logo-icon { width: 36px; height: 36px; border-radius: 8px; background: linear-gradient(135deg, #2196f3, #1565c0); display: flex; align-items: center; justify-content: center; color: white; font-size: 18px; font-weight: 700; }
    .sidebar-logo-text { font-size: 1.1rem; font-weight: 700; color: #1a1a2e; }
    .nav-group { padding: 14px 20px 4px; font-size: 0.68rem; font-weight: 600; color: #8c8c8c; letter-spacing: 0.08em; text-transform: uppercase; }
    [data-testid="stSidebar"] .stRadio > div { gap: 0 !important; }
    [data-testid="stSidebar"] .stRadio label { display: flex !important; align-items: center !important; padding: 9px 20px !important; border-radius: 0 !important; cursor: pointer !important; font-size: 0.875rem !important; font-weight: 400 !important; color: #596172 !important; border-right: 2px solid transparent !important; transition: all 0.15s ease !important; width: 100% !important; margin: 0 !important; }
    [data-testid="stSidebar"] .stRadio label:hover { background: #e8f4fd !important; color: #2196f3 !important; }
    [data-testid="stSidebar"] .stRadio label > div:first-child { display: none !important; }
    [data-testid="stSidebar"] .stRadio label:has(input[type="radio"]:checked) { background: #e8f4fd !important; color: #2196f3 !important; font-weight: 600 !important; border-right: 2px solid #2196f3 !important; }
    [data-testid="stSidebar"] .stRadio label p { color: inherit !important; font-size: inherit !important; font-weight: inherit !important; margin: 0 !important; }
    [data-testid="stSidebar"] .stSelectbox label, [data-testid="stSidebar"] .stMultiSelect label, [data-testid="stSidebar"] .stSlider label { font-size: 0.72rem !important; font-weight: 600 !important; color: #8c8c8c !important; letter-spacing: 0.05em !important; text-transform: uppercase !important; }
    .main .block-container { padding: 24px 28px !important; max-width: 100% !important; }
    .topbar { background: white; border-bottom: 1px solid #e6ebf1; padding: 12px 28px; margin: -24px -28px 20px; display: flex; align-items: center; justify-content: space-between; }
    .topbar-title { font-size: 1rem; font-weight: 600; color: #1a1a2e; }
    .kpi-card { background: #ffffff; border: 1px solid #e6ebf1; border-radius: 4px; padding: 20px; overflow: hidden; }
    .kpi-label { font-size: 0.72rem; font-weight: 600; color: #8c8c8c; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
    .kpi-value { font-size: 1.75rem; font-weight: 700; color: #1a1a2e; line-height: 1; margin-bottom: 6px; }
    .kpi-badge { display: inline-flex; align-items: center; gap: 3px; padding: 2px 8px; border-radius: 3px; font-size: 0.72rem; font-weight: 600; }
    .kpi-badge.primary { background: #e3f2fd; color: #1565c0; border: 1px solid #bbdefb; }
    .kpi-badge.success { background: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
    .kpi-badge.warning { background: #fff8e1; color: #e65100; border: 1px solid #ffecb3; }
    .kpi-badge.error   { background: #ffebee; color: #b71c1c; border: 1px solid #ffcdd2; }
    .kpi-sub { font-size: 0.75rem; color: #8c8c8c; margin-top: 6px; }
    .kpi-sub b { color: #2196f3; }
    .chart-card { background: #ffffff; border: 1px solid #e6ebf1; border-radius: 4px; overflow: hidden; margin-bottom: 0; }
    .chart-card-header { padding: 14px 20px 12px; border-bottom: 1px solid #e6ebf1; display: flex; align-items: center; justify-content: space-between; }
    .chart-card-title { font-size: 0.9375rem; font-weight: 600; color: #1a1a2e; margin: 0; }
    .chart-card-subtitle { font-size: 0.75rem; color: #8c8c8c; margin: 2px 0 0 0; }
    .report-list-item { padding: 11px 20px; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; justify-content: space-between; background: white; }
    .report-list-item:last-child { border-bottom: none; }
    .report-list-name { font-size: 0.85rem; color: #262626; }
    .pill { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }
    .pill-blue  { background: #e3f2fd; color: #1565c0; }
    .pill-green { background: #e8f5e9; color: #2e7d32; }
    .pill-red   { background: #ffebee; color: #b71c1c; }
    header[data-testid="stHeader"] { display: none; }
    #MainMenu, footer { visibility: hidden; }
    .stDownloadButton button { background: #2196f3 !important; color: white !important; border: none !important; border-radius: 4px !important; font-weight: 500 !important; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

inject_css()


# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data
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
    if "Country Name" not in df.columns: df["Country Name"] = df.iloc[:, 0]
    if "Country Code" not in df.columns: df["Country Code"] = df.iloc[:, 1]

    def extract_base(name):
        name = str(name).strip()
        for suffix in [": Q1 (lowest)",": Q1",": Q2",": Q3",": Q4",": Q5 (highest)",": Q5"]:
            if name.endswith(suffix): return name[:-len(suffix)].strip()
        return name

    def extract_quintile(name):
        n = str(name)
        if "Q1" in n: return "Q1 (Poorest)"
        if "Q2" in n: return "Q2"
        if "Q3" in n: return "Q3"
        if "Q4" in n: return "Q4"
        if "Q5" in n: return "Q5 (Richest)"
        return "Unknown"

    df["Base Indicator"] = df["Series Name"].apply(extract_base)
    df["Quintile"]       = df["Series Name"].apply(extract_quintile)
    long = df.melt(
        id_vars=["Country Name","Country Code","Series Name","Base Indicator","Quintile"],
        value_vars=year_cols, var_name="Year Label", value_name="Value",
    )
    long["Year"] = long["Year Label"].str.extract(r"(\d{4})").astype(int)
    long = long.dropna(subset=["Value"])
    return long, sorted(year_cols)

long_df, year_cols = load_data()
all_countries  = sorted(long_df["Country Name"].unique())
all_indicators = sorted(long_df["Base Indicator"].unique())
all_years      = sorted(long_df["Year"].unique())
Q_ORDER        = ["Q1 (Poorest)","Q2","Q3","Q4","Q5 (Richest)"]
COLORS         = ["#2196f3","#4caf50","#ff9800","#f44336","#9c27b0","#00bcd4"]

def mantis_fig(fig, height=320):
    fig.update_layout(
        height=height,
        font=dict(family="Public Sans, sans-serif", size=12, color="#596172"),
        paper_bgcolor="white", plot_bgcolor="white",
        margin=dict(l=10,r=10,t=10,b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1, font=dict(size=11)),
        xaxis=dict(showgrid=False, zeroline=False, linecolor="#e6ebf1",
                   tickcolor="#e6ebf1", tickfont=dict(size=11, color="#8c8c8c")),
        yaxis=dict(gridcolor="#f5f5f5", zeroline=False,
                   tickfont=dict(size=11, color="#8c8c8c")),
    )
    return fig

def filt(countries=None, indicator=None, year=None, quintiles=None):
    d = long_df.copy()
    if countries:  d = d[d["Country Name"].isin(countries)]
    if indicator:  d = d[d["Base Indicator"] == indicator]
    if year:       d = d[d["Year"] == year]
    if quintiles:  d = d[d["Quintile"].isin(quintiles)]
    return d

def kpi(label, value, badge, bclass, sub1, sub2):
    return f"""<div class="kpi-card">
  <div class="kpi-label">{label}</div>
  <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
    <div class="kpi-value">{value}</div>
    <span class="kpi-badge {bclass}">{badge}</span>
  </div>
  <div class="kpi-sub">{sub1} <b>{sub2}</b></div>
</div>"""

def card_head(title, subtitle=""):
    s = f'<div class="chart-card-subtitle">{subtitle}</div>' if subtitle else ""
    return f"""<div class="chart-card"><div class="chart-card-header">
  <div><div class="chart-card-title">{title}</div>{s}</div>
</div></div>"""

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div class="sidebar-logo">
      <div class="sidebar-logo-icon">H</div>
      <div class="sidebar-logo-text">HNP Analytics</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="nav-group">Navigation</div>', unsafe_allow_html=True)
    page = st.radio("Home","Overview","Country Deep-Dive",
                             "Inequality","Global Map","Data Table",
                    label_visibility="collapsed")

    st.markdown('<div class="nav-group" style="margin-top:14px;">Filters</div>', unsafe_allow_html=True)
    selected_indicator = st.selectbox("Indicator", all_indicators,
        index=all_indicators.index("Total fertility rate (TFR) (births per woman)")
        if "Total fertility rate (TFR) (births per woman)" in all_indicators else 0)
    selected_countries = st.multiselect("Countries", all_countries,
        default=["Bangladesh","Nigeria","India","Brazil","Indonesia"]
        if all(c in all_countries for c in ["Bangladesh","Nigeria","India","Brazil","Indonesia"])
        else all_countries[:5])
    selected_year = st.select_slider("Year", options=all_years, value=all_years[-1])
    selected_quintiles = st.multiselect("Quintiles", Q_ORDER, default=Q_ORDER)

# ═══════════════════════════════════════════════════════════════════════════════
#  HOME
# ═══════════════════════════════════════════════════════════════════════════════
if "Home" in page:
    st.markdown("""
    <div class="topbar">
      <div class="topbar-title">Home</div>
      <div style="font-size:0.75rem;color:#8c8c8c;">World Bank · HNP Statistics by Wealth Quintile</div>
    </div>""", unsafe_allow_html=True)

    # ── Hero banner ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style="
      background: linear-gradient(135deg, #1565c0 0%, #2196f3 60%, #42a5f5 100%);
      border-radius: 4px; padding: 48px 44px; margin-bottom: 24px;
      position: relative; overflow: hidden;">
      <div style="position:absolute;top:-40px;right:-40px;width:220px;height:220px;
        border-radius:50%;background:rgba(255,255,255,0.07);"></div>
      <div style="position:absolute;bottom:-60px;right:80px;width:160px;height:160px;
        border-radius:50%;background:rgba(255,255,255,0.05);"></div>
      <div style="position:relative;z-index:1;">
        <div style="display:inline-block;background:rgba(255,255,255,0.18);
          border-radius:20px;padding:4px 14px;font-size:0.72rem;font-weight:600;
          color:white;letter-spacing:0.06em;text-transform:uppercase;margin-bottom:16px;">
          World Bank Open Data
        </div>
        <h1 style="color:white;font-size:2rem;font-weight:700;margin:0 0 12px;line-height:1.25;">
          Health, Nutrition & Population<br>Statistics Dashboard
        </h1>
        <p style="color:rgba(255,255,255,0.85);font-size:0.95rem;
          max-width:620px;line-height:1.7;margin:0 0 24px;">
          Explore how health and nutrition outcomes differ across wealth quintiles in
          low- and middle-income countries. This dashboard covers
          <strong style="color:white;">91,000+ data points</strong> across
          <strong style="color:white;">multiple countries</strong>,
          disaggregated from the poorest (Q1) to the richest (Q5) households.
        </p>
        <div style="display:flex;gap:12px;flex-wrap:wrap;">
          <div style="background:rgba(255,255,255,0.2);border-radius:4px;
            padding:8px 18px;color:white;font-size:0.8rem;font-weight:600;">
            📅 2012 – 2021
          </div>
          <div style="background:rgba(255,255,255,0.2);border-radius:4px;
            padding:8px 18px;color:white;font-size:0.8rem;font-weight:600;">
            🌍 Multiple Countries
          </div>
          <div style="background:rgba(255,255,255,0.2);border-radius:4px;
            padding:8px 18px;color:white;font-size:0.8rem;font-weight:600;">
            💰 5 Wealth Quintiles
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── About section ────────────────────────────────────────────────────────
    col_left, col_right = st.columns([6, 4])

    with col_left:
        st.markdown("""
        <div class="chart-card">
          <div class="chart-card-header">
            <div class="chart-card-title">About This Dashboard</div>
          </div>
          <div style="padding: 20px 24px;">
            <p style="color:#434343;line-height:1.8;font-size:0.875rem;margin-bottom:16px;">
              <strong>Health, Nutrition and Population (HNP)</strong> outcomes are among the
              most powerful indicators of a country's development. Yet behind national
              averages lie dramatic inequalities — a child born into the poorest 20% of
              households faces vastly different life chances than one born into the richest 20%.
            </p>
            <p style="color:#434343;line-height:1.8;font-size:0.875rem;margin-bottom:16px;">
              This dashboard uses the <strong>World Bank's HNP Statistics by Wealth Quintile</strong>
              dataset to make those inequalities visible. By breaking each indicator into five
              wealth quintiles — Q1 (poorest) through Q5 (richest) — we can examine who is
              being left behind and where progress is most unequal.
            </p>
            <p style="color:#434343;line-height:1.8;font-size:0.875rem;margin-bottom:0;">
              The data spans <strong>2012 to 2021</strong> and covers indicators including
              fertility rates, child mortality, stunting, skilled birth attendance,
              contraceptive use, antenatal care coverage, and more — all disaggregated
              by household wealth.
            </p>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div class="chart-card">
          <div class="chart-card-header">
            <div class="chart-card-title">Why Wealth Quintiles?</div>
          </div>
          <div style="padding: 20px 24px;">
            <p style="color:#434343;line-height:1.8;font-size:0.875rem;margin-bottom:14px;">
              National averages can mask extreme disparities. Wealth quintiles split
              a country's population into five equal groups ranked by household
              living standards — revealing the true gap between rich and poor.
            </p>
            <div style="display:flex;flex-direction:column;gap:8px;">
              <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#f44336;flex-shrink:0;"></div>
                <span style="font-size:0.82rem;color:#434343;"><b>Q1</b> — Poorest 20% of households</span>
              </div>
              <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#ff9800;flex-shrink:0;"></div>
                <span style="font-size:0.82rem;color:#434343;"><b>Q2</b> — Second poorest quintile</span>
              </div>
              <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#ffc107;flex-shrink:0;"></div>
                <span style="font-size:0.82rem;color:#434343;"><b>Q3</b> — Middle quintile</span>
              </div>
              <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#66bb6a;flex-shrink:0;"></div>
                <span style="font-size:0.82rem;color:#434343;"><b>Q4</b> — Second richest quintile</span>
              </div>
              <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#2196f3;flex-shrink:0;"></div>
                <span style="font-size:0.82rem;color:#434343;"><b>Q5</b> — Richest 20% of households</span>
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Key themes ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="chart-card">
      <div class="chart-card-header">
        <div class="chart-card-title">Key Global Health Themes</div>
        <div class="chart-card-subtitle">Core areas covered in this dataset</div>
      </div>
    </div>""", unsafe_allow_html=True)

    themes = [
        ("🍼", "Child Nutrition", "#e3f2fd", "#1565c0",
         "Stunting, wasting, and underweight rates among children under 5 remain critically high in the poorest quintiles across Sub-Saharan Africa and South Asia, with gaps of 20–40 percentage points between Q1 and Q5."),
        ("👶", "Child Mortality", "#fce4ec", "#b71c1c",
         "Under-5 mortality rates are dramatically higher for children from the poorest households. In many countries, a child born in Q1 is 3–5× more likely to die before age 5 than one born in Q5."),
        ("🤰", "Maternal Health", "#f3e5f5", "#6a1b9a",
         "Access to skilled birth attendance and antenatal care is heavily skewed toward wealthier quintiles. Women in Q1 are far less likely to deliver in a health facility, raising risks of maternal mortality."),
        ("💊", "Family Planning", "#e8f5e9", "#2e7d32",
         "Contraceptive prevalence is significantly lower among the poorest women, contributing to higher fertility rates in Q1 households and perpetuating cycles of poverty and poor health outcomes."),
        ("📉", "Fertility Rates", "#fff8e1", "#e65100",
         "Total fertility rates are consistently higher among poorer quintiles. This reflects lower education, reduced access to reproductive health services, and limited women's autonomy in decision-making."),
        ("🏥", "Healthcare Access", "#e0f7fa", "#006064",
         "Utilisation of health services — from vaccinations to treatment-seeking behaviour — is strongly correlated with household wealth. Bridging this gap is central to achieving Universal Health Coverage."),
    ]

    cols = st.columns(3)
    for i, (icon, title, bg, color, desc) in enumerate(themes):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:{bg};border-radius:4px;padding:20px;margin-bottom:16px;height:100%;">
              <div style="font-size:1.6rem;margin-bottom:8px;">{icon}</div>
              <div style="font-size:0.875rem;font-weight:700;color:{color};margin-bottom:8px;">{title}</div>
              <p style="font-size:0.8rem;color:#434343;line-height:1.7;margin:0;">{desc}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Navigation guide ─────────────────────────────────────────────────────
    st.markdown("""
    <div class="chart-card">
      <div class="chart-card-header">
        <div class="chart-card-title">How to Use This Dashboard</div>
        <div class="chart-card-subtitle">Navigate using the sidebar — each page focuses on a different lens</div>
      </div>
      <div style="padding:16px 24px 20px;display:flex;flex-wrap:wrap;gap:12px;">
        <div style="flex:1;min-width:160px;background:#f8f9fa;border-radius:4px;padding:14px 16px;">
          <div style="font-size:1rem;margin-bottom:4px;">📊</div>
          <div style="font-weight:600;font-size:0.82rem;color:#1a1a2e;margin-bottom:4px;">Overview</div>
          <div style="font-size:0.77rem;color:#8c8c8c;line-height:1.5;">KPIs, trends across quintiles, Q1 vs Q5 comparison and distribution charts.</div>
        </div>
        <div style="flex:1;min-width:160px;background:#f8f9fa;border-radius:4px;padding:14px 16px;">
          <div style="font-size:1rem;margin-bottom:4px;">🔍</div>
          <div style="font-weight:600;font-size:0.82rem;color:#1a1a2e;margin-bottom:4px;">Country Deep-Dive</div>
          <div style="font-size:0.77rem;color:#8c8c8c;line-height:1.5;">Per-country trends for any indicator, plus a heatmap of all indicators.</div>
        </div>
        <div style="flex:1;min-width:160px;background:#f8f9fa;border-radius:4px;padding:14px 16px;">
          <div style="font-size:1rem;margin-bottom:4px;">⚖️</div>
          <div style="font-weight:600;font-size:0.82rem;color:#1a1a2e;margin-bottom:4px;">Inequality</div>
          <div style="font-size:0.77rem;color:#8c8c8c;line-height:1.5;">Ranks countries by the wealth gap between Q1 and Q5 for any indicator.</div>
        </div>
        <div style="flex:1;min-width:160px;background:#f8f9fa;border-radius:4px;padding:14px 16px;">
          <div style="font-size:1rem;margin-bottom:4px;">🗺️</div>
          <div style="font-weight:600;font-size:0.82rem;color:#1a1a2e;margin-bottom:4px;">Global Map</div>
          <div style="font-size:0.77rem;color:#8c8c8c;line-height:1.5;">Choropleth world map to visualise geographic patterns by quintile and year.</div>
        </div>
        <div style="flex:1;min-width:160px;background:#f8f9fa;border-radius:4px;padding:14px 16px;">
          <div style="font-size:1rem;margin-bottom:4px;">📋</div>
          <div style="font-weight:600;font-size:0.82rem;color:#1a1a2e;margin-bottom:4px;">Data Table</div>
          <div style="font-size:0.77rem;color:#8c8c8c;line-height:1.5;">Filter, browse, and download the raw data as CSV for your own analysis.</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;padding:24px 0 8px;font-size:0.75rem;color:#bdbdbd;">
      Data source: World Bank — Health Nutrition and Population Statistics by Wealth Quintile &nbsp;·&nbsp;
      <a href="https://databank.worldbank.org" target="_blank" style="color:#2196f3;text-decoration:none;">databank.worldbank.org</a>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
if "Overview" in page:
    ind_short = selected_indicator[:55]+"…" if len(selected_indicator)>55 else selected_indicator
    st.markdown(f"""<div class="topbar">
      <div class="topbar-title">Overview Dashboard</div>
      <div style="font-size:0.75rem;color:#8c8c8c;">{ind_short} &nbsp;·&nbsp; {selected_year}</div>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    dq1 = filt(indicator=selected_indicator, year=selected_year, quintiles=["Q1 (Poorest)"])
    dq5 = filt(indicator=selected_indicator, year=selected_year, quintiles=["Q5 (Richest)"])
    aq1 = round(dq1["Value"].mean(),2) if not dq1.empty else "—"
    aq5 = round(dq5["Value"].mean(),2) if not dq5.empty else "—"
    c1.markdown(kpi("Total Countries", long_df["Country Name"].nunique(), "Active","primary","Across","all regions"), unsafe_allow_html=True)
    c2.markdown(kpi("Indicators", long_df["Base Indicator"].nunique(), "Tracked","success","From","World Bank HNP"), unsafe_allow_html=True)
    c3.markdown(kpi("Avg Value Q1", aq1, "Poorest","warning","Quintile","Q1 (Poorest)"), unsafe_allow_html=True)
    c4.markdown(kpi("Avg Value Q5", aq5, "Richest","error","Quintile","Q5 (Richest)"), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns([8,4])
    with col_a:
        st.markdown(card_head("Quintile Trend Over Time","Average across selected countries"), unsafe_allow_html=True)
        d_t = filt(countries=selected_countries or all_countries[:8],
                   indicator=selected_indicator,
                   quintiles=selected_quintiles or Q_ORDER
                  ).groupby(["Year","Quintile"],as_index=False)["Value"].mean()
        if not d_t.empty:
            fig = px.line(d_t, x="Year", y="Value", color="Quintile",
                          markers=True, color_discrete_sequence=COLORS)
            fig = mantis_fig(fig, 300)
            fig.update_traces(line_width=2)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        else:
            st.info("No data for selected filters.")

    with col_b:
        d_rep = filt(indicator=selected_indicator, year=selected_year,
                     quintiles=["Q1 (Poorest)","Q5 (Richest)"])
        piv = (d_rep.groupby(["Country Name","Quintile"])["Value"].mean()
               .unstack("Quintile").dropna().reset_index())
        piv.columns.name = None
        st.markdown("""<div class="chart-card">
          <div class="chart-card-header"><div class="chart-card-title">Country Summary</div></div>""",
          unsafe_allow_html=True)
        if not piv.empty and "Q1 (Poorest)" in piv.columns and "Q5 (Richest)" in piv.columns:
            piv["Gap"] = (piv["Q5 (Richest)"] - piv["Q1 (Poorest)"]).round(2)
            for _, row in piv.head(7).iterrows():
                gc = "pill-green" if row["Gap"] >= 0 else "pill-red"
                st.markdown(f"""<div class="report-list-item">
                  <span class="report-list-name">{row['Country Name']}</span>
                  <span class="pill {gc}">gap {row['Gap']:+.1f}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("Select countries to compare.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    col_c, col_d = st.columns([8,4])

    with col_c:
        st.markdown(card_head("Q1 vs Q5 by Country","Grouped bar — selected year"), unsafe_allow_html=True)
        d_b = filt(countries=selected_countries or all_countries[:8],
                   indicator=selected_indicator, year=selected_year,
                   quintiles=["Q1 (Poorest)","Q5 (Richest)"])
        if not d_b.empty:
            fig2 = px.bar(d_b, x="Country Name", y="Value", color="Quintile", barmode="group",
                          color_discrete_map={"Q1 (Poorest)":"#f44336","Q5 (Richest)":"#4caf50"})
            fig2 = mantis_fig(fig2, 300)
            fig2.update_layout(xaxis_tickangle=-30)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})
        else:
            st.info("No data.")

    with col_d:
        st.markdown(card_head("Quintile Share","Average value distribution"), unsafe_allow_html=True)
        d_p = filt(countries=selected_countries or all_countries[:5],
                   indicator=selected_indicator, year=selected_year,
                   quintiles=selected_quintiles or Q_ORDER
                  ).groupby("Quintile",as_index=False)["Value"].mean()
        if not d_p.empty:
            fig3 = px.pie(d_p, names="Quintile", values="Value", hole=0.55,
                          color_discrete_sequence=COLORS)
            fig3 = mantis_fig(fig3, 300)
            fig3.update_traces(textfont_size=11)
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})
        else:
            st.info("No data.")

# ═══════════════════════════════════════════════════════════════════════════════
#  COUNTRY DEEP-DIVE
# ═══════════════════════════════════════════════════════════════════════════════
elif "Country" in page:
    st.markdown("""<div class="topbar">
      <div class="topbar-title">Country Deep-Dive</div></div>""", unsafe_allow_html=True)

    country = st.selectbox("Select Country", all_countries,
        index=all_countries.index("Bangladesh") if "Bangladesh" in all_countries else 0)
    d_c = long_df[long_df["Country Name"] == country]

    vq1 = d_c[(d_c["Base Indicator"]==selected_indicator)&(d_c["Quintile"]=="Q1 (Poorest)")]["Value"].mean()
    vq5 = d_c[(d_c["Base Indicator"]==selected_indicator)&(d_c["Quintile"]=="Q5 (Richest)")]["Value"].mean()
    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kpi("Indicators",d_c["Base Indicator"].nunique(),"Total","primary","For",country), unsafe_allow_html=True)
    c2.markdown(kpi("Years of Data",d_c["Year"].nunique(),"Years","success","From",f"{all_years[0]}–{all_years[-1]}"), unsafe_allow_html=True)
    c3.markdown(kpi("Q1 Avg",round(vq1,2) if not np.isnan(vq1) else "—","Poorest","warning","Selected","indicator"), unsafe_allow_html=True)
    c4.markdown(kpi("Q5 Avg",round(vq5,2) if not np.isnan(vq5) else "—","Richest","error","Selected","indicator"), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    st.markdown(card_head(selected_indicator[:70], f"All quintiles over time — {country}"), unsafe_allow_html=True)
    d_ind = d_c[(d_c["Base Indicator"]==selected_indicator)&
                (d_c["Quintile"].isin(selected_quintiles or Q_ORDER))]
    if not d_ind.empty:
        fig = px.line(d_ind, x="Year", y="Value", color="Quintile",
                      markers=True, color_discrete_sequence=COLORS)
        fig = mantis_fig(fig, 320); fig.update_traces(line_width=2)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    else:
        st.info("No data for this indicator and country.")

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    st.markdown(card_head("Indicator Heatmap","Top 20 by Q1 vs Q5 inequality ratio"), unsafe_allow_html=True)
    pivot = (d_c[d_c["Quintile"].isin(["Q1 (Poorest)","Q5 (Richest)"])]
             .sort_values("Year").groupby(["Base Indicator","Quintile"])["Value"].last()
             .unstack("Quintile").dropna())
    if not pivot.empty and "Q1 (Poorest)" in pivot.columns and "Q5 (Richest)" in pivot.columns:
        pivot["Ratio"] = pivot["Q5 (Richest)"] / pivot["Q1 (Poorest)"].replace(0,np.nan)
        top = pivot["Ratio"].abs().nlargest(20).index
        heat = pivot.loc[top].reset_index()
        fig_h = go.Figure(go.Heatmap(
            z=heat[["Q1 (Poorest)","Q5 (Richest)"]].values.T,
            x=heat["Base Indicator"].str[:45],
            y=["Q1 (Poorest)","Q5 (Richest)"],
            colorscale="RdYlGn", hoverongaps=False,
            colorbar=dict(thickness=12,len=0.8),
        ))
        fig_h.update_layout(height=240,font=dict(family="Public Sans",size=10),
                             paper_bgcolor="white",plot_bgcolor="white",
                             margin=dict(l=10,r=10,t=10,b=130),xaxis_tickangle=-40)
        st.plotly_chart(fig_h, use_container_width=True, config={"displayModeBar":False})
    else:
        st.info("Not enough data.")

# ═══════════════════════════════════════════════════════════════════════════════
#  INEQUALITY
# ═══════════════════════════════════════════════════════════════════════════════
elif "Inequality" in page:
    st.markdown("""<div class="topbar">
      <div class="topbar-title">Wealth Inequality Explorer</div></div>""", unsafe_allow_html=True)

    d = filt(indicator=selected_indicator, year=selected_year,
             quintiles=["Q1 (Poorest)","Q5 (Richest)"])
    piv = (d.groupby(["Country Name","Quintile"])["Value"].mean()
           .unstack("Quintile").dropna().reset_index())
    piv.columns.name = None

    if "Q1 (Poorest)" in piv.columns and "Q5 (Richest)" in piv.columns:
        piv["Gap"]   = piv["Q5 (Richest)"] - piv["Q1 (Poorest)"]
        piv["Ratio"] = (piv["Q5 (Richest)"] / piv["Q1 (Poorest)"].replace(0,np.nan)).round(2)
        c1,c2,c3 = st.columns(3)
        c1.markdown(kpi("Countries Compared",len(piv),"Total","primary","Indicator",selected_indicator[:28]+"…"), unsafe_allow_html=True)
        c2.markdown(kpi("Max Gap",round(piv["Gap"].max(),2),"Highest","warning","Country",piv.loc[piv["Gap"].idxmax(),"Country Name"]), unsafe_allow_html=True)
        c3.markdown(kpi("Avg Ratio Q5/Q1",round(piv["Ratio"].mean(),2),"Average","error","Across","all countries"), unsafe_allow_html=True)

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown(card_head("Top 15 by Inequality Gap","Q5 minus Q1 value"), unsafe_allow_html=True)
            fig = px.bar(piv.nlargest(15,"Gap"), x="Gap", y="Country Name", orientation="h",
                         color="Gap", color_continuous_scale=["#ffe0e0","#f44336"])
            fig = mantis_fig(fig, 400)
            fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        with col_r:
            st.markdown(card_head("Q1 vs Q5 Scatter","Points above diagonal = richer quintile dominates"), unsafe_allow_html=True)
            fig2 = px.scatter(piv, x="Q1 (Poorest)", y="Q5 (Richest)",
                               hover_name="Country Name", color="Gap",
                               size="Ratio", color_continuous_scale="RdYlGn_r")
            mn = min(piv["Q1 (Poorest)"].min(), piv["Q5 (Richest)"].min())
            mx = max(piv["Q1 (Poorest)"].max(), piv["Q5 (Richest)"].max())
            fig2.add_shape(type="line",x0=mn,x1=mx,y0=mn,y1=mx,
                           line=dict(color="#bdbdbd",dash="dash",width=1))
            fig2 = mantis_fig(fig2, 400)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        st.markdown(card_head("Full Country Table"), unsafe_allow_html=True)
        st.dataframe(piv.sort_values("Gap",ascending=False).round(2).reset_index(drop=True),
                     use_container_width=True, height=340)
    else:
        st.info("No data. Try a different indicator or year.")

# ═══════════════════════════════════════════════════════════════════════════════
#  GLOBAL MAP
# ═══════════════════════════════════════════════════════════════════════════════
elif "Map" in page:
    st.markdown("""<div class="topbar">
      <div class="topbar-title">Global Choropleth Map</div></div>""", unsafe_allow_html=True)

    quintile_sel = st.selectbox("Wealth Quintile", Q_ORDER, index=0)
    d = filt(indicator=selected_indicator, year=selected_year, quintiles=[quintile_sel])
    mp = d.groupby(["Country Name","Country Code"],as_index=False)["Value"].mean()

    st.markdown(card_head(selected_indicator[:70], f"{quintile_sel} · {selected_year}"), unsafe_allow_html=True)
    if not mp.empty:
        fig = px.choropleth(mp, locations="Country Code", color="Value",
                             hover_name="Country Name", color_continuous_scale="YlOrRd")
        fig.update_layout(
            geo=dict(showframe=False, showcoastlines=True,
                     projection_type="natural earth", bgcolor="white",
                     landcolor="#f5f5f5", lakecolor="white", coastlinecolor="#bdbdbd"),
            height=520, paper_bgcolor="white",
            margin=dict(l=0,r=0,t=10,b=0),
            font=dict(family="Public Sans, sans-serif"),
            coloraxis_colorbar=dict(thickness=14,len=0.6,tickfont=dict(size=11)),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    else:
        st.info("No data for this combination.")

# ═══════════════════════════════════════════════════════════════════════════════
#  DATA TABLE
# ═══════════════════════════════════════════════════════════════════════════════
elif "Data" in page:
    st.markdown("""<div class="topbar">
      <div class="topbar-title">Data Explorer</div></div>""", unsafe_allow_html=True)

    d = filt(countries=selected_countries or None, indicator=selected_indicator,
             quintiles=selected_quintiles or None)
    d_show = (d[["Country Name","Country Code","Base Indicator","Quintile","Year","Value"]]
              .sort_values(["Country Name","Year"]).reset_index(drop=True))

    c1,c2,c3 = st.columns(3)
    yr_range = f"{d_show['Year'].min()}–{d_show['Year'].max()}" if not d_show.empty else "—"
    c1.markdown(kpi("Rows",f"{len(d_show):,}","Filtered","primary","Matching","current filters"), unsafe_allow_html=True)
    c2.markdown(kpi("Countries",d_show["Country Name"].nunique(),"Unique","success","In","filtered set"), unsafe_allow_html=True)
    c3.markdown(kpi("Years",d_show["Year"].nunique(),"Unique","warning","Range",yr_range), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    st.markdown(card_head("Filtered Records"), unsafe_allow_html=True)
    st.dataframe(d_show, use_container_width=True, height=460)
    st.download_button("⬇️  Download as CSV",
                       d_show.to_csv(index=False).encode("utf-8"),
                       "hnp_filtered.csv","text/csv")
