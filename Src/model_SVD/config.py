import os
 
BASE_DIR = r"D:\Full projet\Anime_recommendation_system"
 
RAW_DATA_PATH = os.path.join(BASE_DIR, "Data", "full_raw_data.csv")
CLEANED_DATA_PATH = os.path.join(BASE_DIR, "Data", "cleaned_data.csv")
ANIME_METADATA_PATH = os.path.join(BASE_DIR, "Data", "anime_metadata_unique.csv")
 
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "svd_model.pkl")
 
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