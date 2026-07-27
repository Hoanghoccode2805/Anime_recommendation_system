from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR/ "Data"

MY_ANIME_RAW_DATASET = DATA_DIR / "my_anime_raw_dataset.csv"
RAW_DATA_PATH = DATA_DIR / "full_raw_data.csv"
RATING_COMPLETE_PATH = DATA_DIR / "rating_complete.csv"
USER_RATING_SMALL_PATH = DATA_DIR / "user_rating_small.csv"
CLEANED_DATA_PATH = DATA_DIR / "cleaned_data.csv"
ANIME_METADATA_PATH = DATA_DIR / "anime_metadata_unique.csv"
 
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR/ "svd_model.pkl"
 
# Data cleaning thresholds
MIN_USER_RATINGS = 5        # drop users with fewer than this many ratings
MIN_ANIME_RATINGS = 5       # drop anime with fewer than this many ratings
MIN_RATING_STD = 0.5        # drop users whose rating std is below this
                
# Evaluation
RATING_SCALE = (1, 10)
THRESHOLD = 9        # rating >= this counts as "user actually likes it"
TOP_K = 10            # K for Precision@K / Recall@K
TEST_SIZE = 0.20
RANDOM_STATE = 42
 
# Model hyperparameters (SVD)
SVD_PARAMS = {
    "n_factors": 50,
    "n_epochs": 20,
    "lr_all": 0.005,
    "reg_all": 0.02,
    "random_state": RANDOM_STATE,
    "verbose": True,
}