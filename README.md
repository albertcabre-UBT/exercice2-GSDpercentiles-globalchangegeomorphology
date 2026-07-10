# Grain Size Distribution Analyzer

A Streamlit app to analyze grain-size measurement data.

## Features

- Paste up to 10 columns (samples) of grain-size data directly from Excel.
- Automatically computes the **D16, D50, and D84** percentiles for each sample.
- Plots the **cumulative distribution function (CDF)** for any selection of samples.
- Optional logarithmic X-axis, common for grain-size analysis.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub (see below).
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click "Create app" → select this repository, branch `main`, and file `app.py`.
4. Deploy. Your app will be live at a `*.streamlit.app` URL.

## Push this project to GitHub

```bash
cd grain-size-app
git init
git add .
git commit -m "Initial commit: grain size distribution analyzer"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```
