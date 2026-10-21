# Anime Recommendation System

An end-to-end anime recommendation project that combines data collection, PostgreSQL, data cleaning, collaborative filtering with SVD, evaluation, and an interactive Streamlit dashboard.

The repository includes both a full local workflow and a smaller, shareable demo workflow. The demo lets reviewers run the dashboard without downloading the multi-gigabyte training data or the full model.

## Highlights

- Collects anime metadata from the [Jikan API](https://docs.api.jikan.moe/), an unofficial MyAnimeList API.
- Filters a large ratings CSV in chunks to keep memory use manageable.
- Ingests metadata and ratings into PostgreSQL with primary- and foreign-key constraints.
- Validates ratings and removes duplicates, sparse interactions, and low-variance users.
- Trains an SVD collaborative-filtering model with [scikit-surprise](https://surpriselib.com/).
- Compares SVD with a `BaselineOnly` model using RMSE and includes Precision@K / Recall@K evaluation.
- Provides Streamlit dashboards for personalised recommendations and community-level insights.

## Architecture

```text
Jikan API ──> anime metadata CSV ──┐
                                   ├──> PostgreSQL ──> joined raw CSV
Ratings CSV ──> chunk filtering ───┘                       │
                                                           ▼
                                             validation and data cleaning
                                                           │
                                      ┌────────────────────┴────────────────────┐
                                      ▼                                         ▼
                            full SVD model                           sampled demo dataset
                                      │                                         │
                                      ▼                                         ▼
                         local Streamlit dashboard                 demo SVD model + app
```

## Recommendation method

This project uses **collaborative filtering**. The SVD model learns latent preference patterns from users who rate anime similarly, then estimates ratings for anime a selected user has not rated.

For a known user, the app:

1. Finds anime the user has already rated.
2. Creates candidates from unseen anime.
3. Predicts ratings for all candidates in one batch.
4. Returns the highest predicted top-K titles.

The active SVD configuration is:

```python
{
    "n_factors": 50,
    "n_epochs": 20,
    "lr_all": 0.005,
    "reg_all": 0.02,
    "random_state": 42,
}
```

The model is evaluated on an 80/20 train-test split, then a final model is retrained on all available interactions before it is saved for the app.

## Demo snapshot

The tracked demo data is generated with a fixed random seed (`42`) and preserves complete histories for selected users rather than sampling arbitrary rows.

| Metric | Value |
| --- | ---: |
| Selected users | 600 |
| Demo ratings | 433,780 |
| Anime in demo ratings | 6,974 |
| Anime metadata records | 7,168 |
| Mean demo rating | 7.36 / 10 |

The full raw/cleaned data and full SVD model are intentionally not committed because of their size.

## Tech stack

| Area | Tools |
| --- | --- |
| Language | Python |
| Data processing | pandas, NumPy |
| Data collection | requests, Jikan API |
| Database | PostgreSQL, SQLAlchemy, psycopg2 |
| Recommender | scikit-surprise (`SVD`, `BaselineOnly`) |
| Dashboard | Streamlit |
| Configuration | python-dotenv |

## Dashboard features

The Streamlit interface has three sections:

- **For You** — validates the selected user, displays their rating profile and genre preferences, then shows top-K personalised recommendations.
- **Community Insights** — shows the most active users, rating distribution, most-rated anime, highest user-rated anime, and top MyAnimeList scores.
- **About Model** — explains the SVD approach and exposes the model settings used by the project.

The app warns when a user ID is not present in the dataset instead of presenting a non-personalised cold-start prediction as a recommendation.

## Repository structure

```text
.
├── config.py                         # Shared paths, cleaning thresholds, model settings
├── requirements.txt
├── Data/
│   ├── anime_metadata_unique.csv     # Metadata used by the dashboards
│   └── demo_cleaned_data.csv         # Tracked demo ratings
├── models/
│   └── demo_svd_model.pkl            # Tracked model trained on demo ratings
└── Src/
    ├── data_processing/
    │   ├── collect_data_with_api.py  # Jikan collection with retry handling
    │   ├── reduce_size_user_file.py  # Chunked active-user filtering
    │   ├── database_ingestion.py     # PostgreSQL ingestion and constraints
    │   └── load_data_train.py        # SQL join export for modelling
    ├── model_SVD/
    │   ├── data_cleaning.py          # Validation and interaction filtering
    │   ├── train_model.py            # Full-model training
    │   ├── evaluate.py               # Precision@K and Recall@K helpers
    │   ├── recommend.py              # Model loading and candidate ranking
    │   ├── app.py                    # Full local dashboard
    │   ├── create_demo_dataset.py    # Builds the demo sample
    │   ├── train_demo_model.py       # Trains the demo model
    │   └── app_deploy.py             # Dashboard backed by demo artifacts
    └── data_checks.py                # Data consistency checks
```

## Installation

Clone the repository and enter its directory:

```bash
git clone https://github.com/Hoanghoccode2805/Anime_recommendation_system.git
cd Anime_recommendation_system
```

Create and activate a virtual environment.

```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the demo dashboard

The demo requires neither PostgreSQL nor the full local data. From the repository root, run:

```bash
streamlit run Src/model_SVD/app_deploy.py
```

Then open the local Streamlit URL, normally `http://localhost:8501`.

> Use a user ID included in `Data/demo_cleaned_data.csv`. The dashboard will display a helpful warning for an unknown ID.

## Run the full local pipeline

Rebuilding the full pipeline requires a local PostgreSQL server, the large `rating_complete.csv` source file, sufficient disk space, and substantially more RAM than the demo. Full data/model artifacts are not included in the repository.

### PostgreSQL configuration

Create the database:

```sql
CREATE DATABASE Anime_recommendation_system_database;
```

Create a `.env` file at the repository root (never commit it):

```env
DB_PASSWORD=your_postgresql_password
```

The current scripts use PostgreSQL at `127.0.0.1:5432`, the `postgres` user, and the database name above.

### Workflow

Run commands from the repository root, in this order:

```bash
# 1. Collect anime metadata (optional if the metadata CSV is already available)
python -m Src.data_processing.collect_data_with_api

# 2. Keep users with at least 1,000 ratings from rating_complete.csv
python -m Src.data_processing.reduce_size_user_file

# 3. Create/replace PostgreSQL anime_data and user_ratings tables
python -m Src.data_processing.database_ingestion

# 4. Join the database tables and export the raw modelling dataset
python -m Src.data_processing.load_data_train

# 5. Validate and clean the interactions
python -m Src.model_SVD.data_cleaning

# 6. Report Precision@K and Recall@K
python -m Src.model_SVD.evaluate

# 7. Train, evaluate, and save the full SVD model
python -m Src.model_SVD.train_model

# 8. Launch the full local dashboard
streamlit run Src/model_SVD/app.py
```

### Rebuild the demo artifacts

Once the full workflow has produced `Data/cleaned_data.csv`, regenerate the smaller demo dataset and its model with:

```bash
python -m Src.model_SVD.create_demo_dataset
python -m Src.model_SVD.train_demo_model
```

## Data-quality rules

Before training, `data_cleaning.py`:

- checks that `user_id`, `anime_id`, and `rating` exist;
- removes null or non-numeric ratings and ratings outside the 1–10 scale;
- removes duplicate `(user_id, anime_id)` interactions;
- removes users with rating standard deviation below `0.5`;
- iteratively removes users and anime with fewer than five ratings;
- creates one metadata record per anime for fast title/genre lookup in the app.

## Evaluation

Two complementary evaluations are implemented:

- **RMSE** on an 80/20 train-test split, reported for both `BaselineOnly` and SVD.
- **Precision@10 and Recall@10**, where a real rating of at least `9` counts as relevant.

Run ranking evaluation independently with:

```bash
python -m Src.model_SVD.evaluate
```

`Src/data_checks.py` is also available for exploratory checks on the exported raw dataset.

## Data and security notes

- Large artifacts such as the full cleaned CSV, full raw data, and full SVD model are excluded from Git.
- The compact demo CSV, anime metadata CSV, and demo SVD model are retained so a reviewer can run the demo after cloning.
- `.env` is ignored by Git. Never commit PostgreSQL credentials.
- Anime metadata is collected from Jikan. If the underlying user-rating source is redistributed or published, its original licence and attribution should be added.

## Future improvements

- Add a genre/popularity-based cold-start strategy for new users.
- Add automated tests for cleaning, evaluation, and recommendation functions.
- Move PostgreSQL host, port, user, and database name to environment variables.
- Containerise the project and add CI checks.
- Deploy the demo dashboard publicly and add its link here.

## Author

**Hoang** — personal machine-learning and data-engineering portfolio project.
