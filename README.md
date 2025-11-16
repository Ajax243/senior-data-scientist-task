Senior Data Scientist Task — Submission Repo

Setup
- Python: 3.9–3.11 recommended
- Create venv (Windows cmd): `python -m venv .venv` then `.venv\Scripts\activate`
- Install deps: `pip install -r requirements.txt`

Run Dashboard (Part 2)
- Command: `streamlit run part2\app.py`
- Or with venv: `part2\.venv\Scripts\python.exe -m streamlit run part2\app.py`
- Data source: `part2\data\` (all CSVs)

Notebooks
- Part 1 (Exploration): `part1_exploration.ipynb`
  - Reads data from `part2/data` and writes any derived CSVs back into `part2/data`.
- Part 3 (Model Design & Data Sufficiency): `part3_model.ipynb`
  - Narrative and analysis (no data dependency).
- Part 4 (Strategic Decision System): `part4_model.ipynb`
  - Reads from `part2/data`.
  - Exports recommendations to the `part4\` folder.

Data
- Canonical data directory: `part2\data\`
- Do not duplicate data under other folders; all code references this path relatively.

Project Structure
- `part2/`: Streamlit app, data, and docs for Part 2
- `part4/`: Generated decision reports (CSV) + documentation
- `part5_ai_agent_design/`: Agent design notes
- `part6_production_plan/`: Architecture and deployment plans

Notes
- If you move notebooks, keep data paths relative to repo root (e.g., `part2/data/...`).
- Large CSVs are expected; operations assume sufficient memory for analysis workloads.
