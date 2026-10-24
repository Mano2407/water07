# 💧 My Water Tracker

An animated, responsive hydration tracker built with Streamlit (PC, tablet and phone).

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (Streamlit Community Cloud)
1. Push this folder to a GitHub repository.
2. On https://share.streamlit.io choose the repo and set `app.py` as the main file.

## Notes
- Each visitor gets a private link id (`?u=...`). Bookmark the page to keep your history.
- Data is stored as small JSON files in `data/`. On hosts with temporary disks (e.g. Community Cloud)
  data can be lost when the app restarts. Use a database for long-term storage.
- Times use the server's clock/timezone.
