# Training Dashboard

Interactive dashboard for certification data.

## Streamlit Dashboard

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

- Loads a `certifications.xlsx` file placed next to the script or uploaded via the sidebar (up to 75,000 rows).
- Provides filters for year, gender, region, certificate type, and text search.
- Charts update automatically and each includes a PNG download button.

If no Excel file is supplied, a random sample of 500 records is generated for demonstration.

## Static Web Version

Open `index.html` in a web browser to explore filters and charts without Python.
