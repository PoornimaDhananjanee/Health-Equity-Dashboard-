# 🌍 Health, Nutrition & Population Dashboard

An interactive Streamlit dashboard exploring World Bank Health, Nutrition & Population Statistics disaggregated by Wealth Quintile (2012–2021).

## 📊 Features

- **Overview** — KPIs, quintile trends, Q1 vs Q5 bar chart, pie chart
- **Country Deep-Dive** — Per-country trend lines + indicator heatmap
- **Inequality Explorer** — Gap analysis, scatter plot, country ranking table
- **Global Map** — Choropleth world map per quintile and year
- **Data Table** — Filter, explore, and download raw data as CSV

---

## 🚀 Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Create a virtual environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add the data file
Place the Excel file in the same directory as `app.py`:
```
P_Data_Extract_From_Health_Nutrition_and_Population_Statistics_by_Wealth_Quintile.xlsx
```

### 5. Run the app
```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`

---

## ☁️ Deploy on Streamlit Cloud (Free)

1. Push your code + data file to a **public GitHub repository**
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **"New app"**
4. Select your repo, branch (`main`), and set **Main file path** to `app.py`
5. Click **Deploy** — your app will be live in ~2 minutes!

> ⚠️ The `.xlsx` file must be in the repo for Streamlit Cloud to access it.

---

## 📁 File Structure

```
.
├── app.py                          # Main Streamlit dashboard
├── requirements.txt                # Python dependencies
├── .gitignore                      # Files to exclude from Git
├── README.md                       # This file
└── P_Data_Extract_From_Health_...xlsx   # Data file (required)
```

---

## 🛠 Tech Stack

| Tool | Purpose |
|------|---------|
| Streamlit | Web app framework |
| Pandas | Data loading & processing |
| Plotly | Interactive charts & maps |
| NumPy | Numerical operations |
| OpenPyXL | Excel file reading |

---

## 📌 Data Source

World Bank — [Health Nutrition and Population Statistics by Wealth Quintile](https://databank.worldbank.org/source/health-nutrition-and-population-statistics-by-wealth-quintile)
