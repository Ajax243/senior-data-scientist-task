Submission Summary

- Objective: Consolidate analysis, dashboard, decision system, and plans into a reproducible, well-documented structure.

- Parts Overview:
  - Part 1 — Exploration (`part1_exploration.ipynb`): EDA of leads, campaigns, insights; qualified-rate logic; campaign metrics assembly. Outputs (if re-run) write to `part2/data/`.
  - Part 2 — Dashboard (`part2/app.py`): Streamlit app with Executive, Performance, Trends, Cost, and Quality views. Reads from `part2/data/`.
  - Part 3 — Model Design (`part3_model.ipynb`): Data sufficiency assessment, ML use cases, and phased data plan.
  - Part 4 — Strategic Decision System (`part4_model.ipynb`): Heuristic scoring + recommendations; exports CSV reports into `part4/`.
  - Part 5 — AI Agent Design (`part5_ai_agent_design/part5_agent_design.md`): Proposed agent architecture and prompts.
  - Part 6 — Production Plan (`part6_production_plan/*.md`): Architecture diagrams and deployment plan.

- Data Canonicalization:
  - All notebooks and the dashboard read from `part2/data/`.
  - No data duplication across folders; paths are relative to repository root.

- Assumptions:
  - Qualified statuses used in EDA and dashboard: QUALIFIED, DONE_DEAL, MEETING_DONE (configurable in code where applied).
  - CPL/CTR definitions follow standard marketing conventions; CPQL is derived where qualified leads exist.

- How to Run:
  - Install: `python -m venv .venv && .venv\\Scripts\\activate && pip install -r requirements.txt`
  - Dashboard: `streamlit run part2\\app.py`
  - Open notebooks in VS Code or Jupyter and run cells; ensure working dir is repo root to preserve relative paths.
