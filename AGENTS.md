# AGENTS.md

Small Flask + pandas hotel-recommendation demo. Flat repo (no package layout), Python 3.13, Flask 3.1, pandas 3.0. Run everything from the repo root.

## Run the app

- `python app.py` — the **only** working way to start the dev server (`127.0.0.1:5000`, debug on).
- `flask --app app run`, `python -m flask ...`, and `import app` all crash (see below). Do not "fix" the entrypoint to these.

## Critical: `model.pkl` is pickled against `__main__`

- It is not a trained model. It is `{"df": DataFrame, "recommend": recommend_hotels}` written by the last cell of `hotel_data.ipynb`.
- `recommend_hotels` was dumped from the notebook's `__main__`, so unpickling requires that name to already exist in `__main__`.
  - In `app.py`, line 3 (`from hotel_recommendation import recommend_hotels`) **must execute before** line 8 (`pickle.load`). Do not reorder them.
  - Any other importer (pytest, gunicorn, flask CLI, `import app`) fails with `AttributeError: Can't get attribute 'recommend_hotels' on <module '__main__'>`. If you add tests, load `model.pkl` in a way that binds `recommend_hotels` into `__main__` first, or regenerate the pickle with `recommend_hotels` imported from `hotel_recommendation` (module-qualified pickles unpickle anywhere).
- `open("model.pkl")` is CWD-relative → starting the app from any other directory fails.

## Data / logic sources of truth

- `hotels.csv` — raw data, 56 rows, 12 columns, contains NaNs.
- `hotel_recommendation.py::recommend_hotels` — the live recommendation logic used by the app.
- `hotel_data.ipynb` cell 32 holds a **duplicate copy** of that function. It is only kept for the pickle; if you change filtering behavior, update both (or better, have the notebook import from `hotel_recommendation.py`).
- The pickle's `recommend` entry is unused by `app.py` (only `["df"]` is read).

## Regenerating `model.pkl` (required whenever `hotels.csv` changes)

- The pickled `df` is the **processed** frame: mean-imputed columns plus `Location_encoded` / `RoomType_encoded` (14 columns), not the raw CSV shape.
- Notebook cell 23 originally used `df['col'].fillna(..., inplace=True)` — a **silent no-op** under pandas 3.0.3 Copy-on-Write (only a `ChainedAssignmentError` warning), so a fresh run left NaNs in the pickle. It has been rewritten to `df['col'] = df['col'].fillna(...)`; keep that assignment form if you touch it.
- The pickled `recommend_hotels` must resolve in `__main__` when the app loads it (the notebook does this naturally; keep it that way).

## HTTP contract (both routes in `app.py`)

- `GET|POST /` — form fields: `location`, `min_price`, `max_price`, `amenities` (comma-separated), `rating`; returns top 5. Non-numeric price/rating returns **400** with an inline error message (no more 500s).
- `POST /api/recommend` — JSON: `location`, `budget: [low, high]` (default `[0, 20000]`), `amenities: []`, `rating`, `top_n` (default 3); returns JSON rows. Malformed `budget`/`rating`/`top_n` returns **400** with `{"error": ...}`.

## Verification

There is **no** test suite, linter, typechecker, CI, or `requirements.txt`. Verify by running the app and hitting it:

```
python app.py
# GET  http://127.0.0.1:5000/                    -> 200
# POST http://127.0.0.1:5000/api/recommend
#   body {"location":"Moulvibazar","budget":[0,50000],"amenities":["Pool"],"rating":4.0,"top_n":2} -> 200 + JSON
```

Runtime deps: Flask, pandas (required just to unpickle). The notebook additionally needs matplotlib, seaborn, scikit-learn (`LabelEncoder`).

## Repo hygiene

- No `.gitignore`; `__pycache__/*.pyc` is already tracked. Be deliberate about `git add`.
