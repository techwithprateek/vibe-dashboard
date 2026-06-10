# 🏠 Vibe Dashboard

> From boring CSV exports to stunning interactive HTML dashboards — pick your level and build it your way.

---

## 🟢 Level 1 — Beginner: Let Claude / ChatGPT Do Everything

No code required. Just a CSV and the right prompt.

### How it works
1. Export or download your dataset as a **CSV file**.
2. Open [Claude](https://claude.ai) or [ChatGPT](https://chatgpt.com).
3. Upload the CSV and paste one of the prompts below.
4. The AI will analyse the data and generate a complete, self-contained `index.html` dashboard.
5. Save the response as `index.html` and open it in your browser — done.

### 🛠 Tools Needed
| Tool | Purpose |
|------|---------|
| [Claude](https://claude.ai) or [ChatGPT](https://chatgpt.com) | Generate the dashboard |
| Any modern browser | Open the HTML file |
| Your CSV file | The data source |

### 🤖 Prompt — Quick Dashboard
Use this when you want a fast, good-looking dashboard from any CSV:

```text
I've attached a CSV file. Please:
1. Analyse the data and identify the most important KPIs and trends.
2. Generate a single self-contained index.html dashboard with:
   - 3–4 KPI cards at the top (pick the most meaningful metrics)
   - A bar chart and a line chart showing key trends
   - A dropdown filter for the most useful categorical column
   - Dark theme, modern card layout, using Chart.js from CDN
   - All data hardcoded as a JS array inside the HTML file
3. Do not use any external files — everything must be in one HTML file.
```

### 🤖 Prompt — Detailed Report
Use this when you want written analysis alongside the visuals:

```text
I've attached a CSV file. Please:
1. Write a short executive summary (3–5 bullet points) of the key findings.
2. Identify the top 3 insights or anomalies in the data.
3. Generate a single self-contained index.html file that includes:
   - The executive summary rendered as styled HTML at the top
   - KPI cards for [metric1], [metric2], [metric3]
   - Charts that support each of the 3 insights
   - Dark theme, using Chart.js from CDN, all data embedded inline
```

> 💡 **Tip:** The more context you give (e.g. "this is Airbnb listing data for NYC, the key metric is revenue per listing"), the better the output.

---

## 🟡 Level 2 — Intermediate: Python + Pandas Processing

Use Python to clean and aggregate the data yourself, then feed the result to an AI or write the HTML manually.

### How it works
1. Load your CSV with **pandas** and compute the metrics you care about.
2. Export the aggregated data as **JSON**.
3. Embed the JSON in an HTML template (manually or with Jinja2), or pass it to Claude Code with a targeted prompt.
4. Open `index.html` in your browser.

### 🛠 Tools Needed
| Tool | Purpose |
|------|---------|
| Python 3.8+ | Runtime |
| pandas | Data cleaning & aggregation |
| Jinja2 *(optional)* | HTML templating |
| [Claude Code](https://claude.ai/code) or VS Code + Copilot | Generate / refine the HTML |
| Chart.js (CDN) | Interactive charts |

### 📦 Install dependencies
```bash
pip install pandas jinja2
```

### Example: process and embed data
```python
# process_data.py
import json
import pandas as pd
from jinja2 import Template

df = pd.read_csv('data/listings.csv')

summary = {
    'total_listings': len(df),
    'avg_price': round(df['price'].mean(), 1),
    'avg_rating': round(df['rating'].mean(), 2),
    'by_borough': df.groupby('borough')['price'].mean().round(1).to_dict(),
    'monthly_trend': df.groupby('month')['revenue'].sum().to_dict(),
}

# Inject into HTML template
template_str = open('template.html').read()
html = Template(template_str).render(data=json.dumps(summary))
open('index.html', 'w').write(html)
print("Dashboard generated → index.html")
```

```html
<!-- template.html -->
<script>
  const RAW_DATA = {{ data | safe }};
</script>
```

### 🤖 Prompt for Claude Code (after processing)
```text
Here is my pre-aggregated JSON data: [paste JSON]

Generate a single-file index.html dashboard with:
- KPI cards for total_listings, avg_price, avg_rating
- A bar chart of price by borough (from by_borough)
- A line chart of monthly revenue trend (from monthly_trend)
- A dropdown filter to switch between metrics
- Dark theme, Chart.js from CDN, all data inline
```

---

## 🔴 Level 3 — Advanced: Live Data Connections

Move beyond static files — connect your dashboard to data that updates automatically.

### 🛠 Tools Needed
| Tool | Purpose |
|------|---------|
| Python + FastAPI | Serve live aggregates via REST API |
| pandas / SQLAlchemy | Query and transform data |
| Google Sheets + Papa Parse | Lightweight live spreadsheet backend |
| JavaScript `fetch` API | Pull data at runtime |
| Any static host (GitHub Pages, Netlify) | Deploy the dashboard |

---

### Option A — Fetch from a hosted JSON file
Best for data that refreshes on a schedule (e.g. a nightly cron job).

```html
<script>
  async function loadData() {
    const res = await fetch('./data/dashboard.json');
    return res.json();
  }
</script>
```

---

### Option B — Google Sheets as a live backend
Publish your Google Sheet as CSV and parse it in-browser with **Papa Parse** — no backend needed.

```html
<script src="https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js"></script>
<script>
  const SHEET_URL = 'https://docs.google.com/spreadsheets/d/e/YOUR_SHEET_ID/pub?output=csv';

  Papa.parse(SHEET_URL, {
    download: true,
    header: true,
    complete: ({ data }) => renderDashboard(data),
  });
</script>
```

> 💡 In Google Sheets: **File → Share → Publish to web → CSV**, then copy the link.

---

### Option C — FastAPI REST backend
Best when data lives in a database or needs server-side computation.

```python
# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])

@app.get('/dashboard-data')
def dashboard_data():
    df = pd.read_csv('data/listings.csv')   # swap for a DB query
    return {
        'total_listings': len(df),
        'avg_price': round(df['price'].mean(), 1),
        'by_borough': df.groupby('borough')['price'].mean().round(1).to_dict(),
    }
```

```bash
pip install fastapi uvicorn pandas
uvicorn app:app --reload
```

```html
<script>
  async function loadData() {
    const res = await fetch('http://127.0.0.1:8000/dashboard-data');
    return res.json();
  }
</script>
```

---

## 🚀 Quick Start (this repo)

```bash
git clone <repo-url>
cd vibe-dashboard
open index.html          # macOS
# or: start index.html   # Windows
# or: xdg-open index.html # Linux
```

No npm install, no server, no build step.

## 📁 Project Structure
```text
.
├── data/
│   ├── airbnb_listings.csv   # raw data
│   └── airbnb_data.json      # pre-aggregated output
├── index.html                # dashboard (open in browser)
├── process_data.py           # Level 2 processing script
└── README.md
```
