# Health Equity by Wealth Quintile — Dashboard

An interactive Streamlit dashboard exploring how wealth inequality shapes maternal and reproductive health outcomes across countries worldwide.

## Dataset
**Health, Nutrition and Population Statistics by Wealth Quintile** — World Bank Open Data  
Covers 27 countries, 4 health indicators broken down by 5 wealth quintiles (Q1=poorest → Q5=richest), 2012–2021.

## Features
-  **Overview** — KPI cards, grouped bar charts, inequality heatmap
-  **Country Deep-Dive** — Trend lines and snapshots per country
-  **Cross-Country Compare** — Country ranking + Q1 vs Q5 scatter
-  **Inequality Gap** — Q5−Q1 gap over time with data table

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Ensure `data.xlsx` is in the same directory as `app.py`.

## Deployment
Deploy via [Streamlit Community Cloud](https://streamlit.io/cloud):
1. Push this repo to GitHub (public)
2. Go to share.streamlit.io → New app → select this repo
3. Set main file path to `app.py`

## SDG Alignment
- **SDG 3** – Good Health and Well-Being
- **SDG 10** – Reduced Inequalities
