# Part 2 — Streamlit Dashboard Documentation

- Purpose: Provide decision-makers with exploratory and performance views across campaigns.
- Data: Reads all CSVs from `dashboard/data/` (no duplication elsewhere).

How to Run (Windows cmd)
```
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run dashboard\part2_dashboard\app.py
```

Key Views
- Executive Summary: KPIs (Spend, Leads, Avg CPL, Avg CTR) + top 10 charts.
- Campaign Performance: Scatter (Spend vs Leads), CPL distribution, detailed table.
- Campaign Trends: Daily spend/clicks/impressions/reach/leads; CPC & CTR trends; business overview.
- Cost & Budget: Budget vs spend, utilization histogram, Budget/Lead vs Actual CPL.
- Lead Quality & Efficiency: CTR and qualified% distributions, stacked qualified vs non-qualified, efficiency score ranking.

Filters
- Business filter (`user_id`) available in sidebar for all dashboards.

Assumptions
- CTR in `%` as provided; CPL = spend / leads; qualified% recomputed using statuses
  (QUALIFIED, DONE_DEAL, MEETING_DONE) vs non-qualified list.

Notes
- If you add new CSVs, place them under `dashboard/data/` and follow existing columns.
- For large files, Streamlit caches loads via `@st.cache_data`.
