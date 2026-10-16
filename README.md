<div align="center">

# Dashboard Co-pilot Agent

**Turn any Excel or CSV file into an interactive, AI-assisted dashboard in seconds.**

[![Live App](https://img.shields.io/badge/Live_App-Open_Dashboard-2563EB?style=for-the-badge&logo=streamlit&logoColor=white)](https://dashboard-copilot-agent.streamlit.app)

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-8E75B2?style=flat-square&logo=googlegemini&logoColor=white)

</div>

---

## Overview

Dashboard Co-pilot Agent is a bilingual (English / Arabic) analytics web app built for people who want answers from their data without writing code. Users upload a spreadsheet and immediately get KPI cards, interactive charts, Power BI-style filtering and design recommendations, with an AI assistant on hand to explain the data and suggest Excel formulas or Pandas code.

The project combines data analysis, dashboard design and applied AI in a single, deployable product.

## Key Features

| Area | What it does |
|------|--------------|
| **Interactive filtering** | Date range, multi-select category and numeric range filters that update every KPI, chart and table instantly. |
| **Cross-filtering charts** | Click any bar, point or slice to filter the entire dashboard, similar to Power BI. |
| **Smart KPI cards** | Totals, averages and maximums with context: share of total, change vs. overall average, and period-over-period comparison. |
| **Chart builder** | Bar, Line, Donut and Scatter charts with Sum / Average / Count aggregation and automatic date detection. |
| **AI assistant** | A floating Gemini-powered assistant that understands the uploaded columns and active filters, with streamed replies and automatic model fallback. |
| **Design recommendations** | Detects the data's domain (healthcare, finance, HR, general) and suggests a color palette, headline KPIs and suitable chart types. |
| **Data export** | Download the filtered dataset as CSV or Excel. |
| **Bilingual and responsive** | Guided onboarding with language selection, full right-to-left Arabic support, and a layout that adapts to mobile, tablet and desktop. |

## How It Works

1. **Upload** an Excel or CSV file.
2. **Explore** the generated KPIs and charts, and narrow the view with filters or by clicking on a chart.
3. **Ask** the AI assistant to explain the data or provide the formula for a calculation.
4. **Export** the filtered results for further work.

## Tech Stack

| Layer | Tools |
|-------|-------|
| Language | Python |
| Web framework | Streamlit |
| Data processing | Pandas, OpenPyXL |
| Visualization | Plotly Express |
| AI | Google Gemini API (`google-genai`) |
| Deployment | Streamlit Community Cloud |

## Project Structure

```
dashboard-copilot-agent/
├── app.py              # Application: UI, analytics logic and AI assistant
├── requirements.txt    # Python dependencies
└── README.md
```

## Getting Started

**1. Clone the repository**
```bash
git clone https://github.com/wajd-cs/dashboard-copilot-agent.git
cd dashboard-copilot-agent
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your Gemini API key** in a `.env` file at the project root
```
GEMINI_API_KEY=your_api_key
```

**4. Run the app**
```bash
streamlit run app.py
```

## Deployment

The app is deployed on Streamlit Community Cloud. To deploy your own copy, point a new app at `app.py` and add the key under **Settings → Secrets**:

```toml
GEMINI_API_KEY = "your_api_key"
```

## Data Privacy

Uploaded files are processed in memory and are not stored. When the assistant is used, only the column names, a five-row sample and summary statistics of the current view are sent to Google Gemini to generate an answer.

---

<div align="center">

**Developed by Wajd Al-Luhaibi**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/YOUR-LINKEDIN-USERNAME)

</div>
