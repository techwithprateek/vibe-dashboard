# 🏠 Vibe Dashboard

> From boring PowerBI exports to stunning interactive HTML dashboards — built with Claude Code.

## 🎬 The Workflow
Turn a plain CSV export into a polished, shareable dashboard in one fast loop:

1. Export or download a dataset.
2. Feed Claude Code a prompt describing the KPIs, charts, theme, and filters you want.
3. Let Claude Code transform the data into pre-aggregated JSON.
4. Generate a single `index.html` file with embedded data and interactive charts.
5. Open the file directly in your browser — no server, framework, or build step required.

## 🛠 Stack
- **Chart.js** for interactive visualizations
- **HTML / CSS / JavaScript** in a single file
- **Python** for CSV processing and JSON aggregation
- **No framework needed**

## ✨ Key Features
- 4 KPI cards with animated count-up
- Borough filter that updates all charts
- 6 interactive charts with hover tooltips
- Dark theme, fully responsive
- Single file — no server needed

## 🤖 Claude Code Prompt
Use this prompt pattern to generate similar dashboards for any dataset:

```text
Create a single-file HTML dashboard for [topic] with:
- KPI cards at the top showing [metric1], [metric2], [metric3]
- A bar chart showing [x] vs [y]
- A line chart showing [trend over time]
- A dropdown filter for [dimension]
- Dark theme, modern design, using Chart.js
- Sample data hardcoded as a JS array
```

## 📊 How to Connect to Real Data

### Option 1 — Hardcoded JSON (this project)
This repo uses the simplest possible setup: generate JSON once, then paste or embed it directly inside the HTML file as a JavaScript constant.

```html
<script>
  const RAW_DATA = { /* pre-aggregated JSON goes here */ };
</script>
```

### Option 2 — Fetch from hosted file
Host a JSON file anywhere static files are supported and fetch it at runtime.

```html
<script>
  async function loadData() {
    const response = await fetch('./data/airbnb_data.json');
    return response.json();
  }
</script>
```

### Option 3 — Google Sheets live backend
Publish a Google Sheet as CSV, then parse it client-side with Papa Parse.

```html
<script src="https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js"></script>
<script>
  Papa.parse('https://docs.google.com/spreadsheets/d/e/your-sheet-id/pub?output=csv', {
    download: true,
    header: true,
    complete: ({ data }) => {
      console.log('Rows from Google Sheets:', data);
    }
  });
</script>
```

### Option 4 — REST API
Serve live aggregates from an API such as FastAPI and load them from the dashboard.

```python
# app.py
from fastapi import FastAPI

app = FastAPI()

@app.get('/dashboard-data')
def dashboard_data():
    return {"kpis": {"total_listings": 20590}}
```

```html
<script>
  async function loadData() {
    const response = await fetch('http://127.0.0.1:8000/dashboard-data');
    return response.json();
  }
</script>
```

### Option 5 — Python-generated HTML
For a repeatable reporting pipeline, use Python to read data, aggregate with pandas, inject JSON into a Jinja2 template, and output a ready-to-open HTML file.

```python
import json
import pandas as pd
from jinja2 import Template

frame = pd.read_csv('data.csv')
summary = {
    'rows': len(frame),
    'avg_price': round(frame['price'].mean(), 1)
}
html = Template("<script>const RAW_DATA = {{ data | safe }};</script>").render(
    data=json.dumps(summary)
)
```

## 🚀 Getting Started
1. Clone this repo
2. Open `index.html` in your browser
3. That's it — no npm install, no server

## 📁 Project Structure
```text
.
├── data/
│   ├── airbnb_data.json
│   └── airbnb_listings.csv
├── index.html
├── process_data.py
└── README.md
```
