import pickle
import pandas as pd
from surprise import Dataset, Reader, SVD, BaselineOnly, accuracy
from surprise.model_selection import train_test_split
import config 
from config import MODEL_PATH, RATING_SCALE, CLEANED_DATA_PATH, SVD_PARAMS, RANDOM_STATE, MODEL_DIR, TEST_SIZE

def load_cleaned_data():
    return pd.read_csv(CLEANED_DATA_PATH)

def build_dataset(df):
    reader = Reader(rating_scale= RATING_SCALE)
    return Dataset.load_from_df(df[['user_id','anime_id','rating']],reader)

def train_SVD(trainset):
    model = SVD(**SVD_PARAMS)
    model.fit(trainset)
    return model

if __name__ == "__main__":
    df = load_cleaned_data()
    data = build_dataset(df)
    trainset, testset = train_test_split(data, test_size= TEST_SIZE, random_state= RANDOM_STATE)
    
    # simple baseline (global mean + user/item bias, no latent factors)
    # so the SVD's RMSE has something to be compared against
    baseline = BaselineOnly()
    baseline.fit(trainset)
    print("RMSE is : ")
    accuracy.rmse(baseline.test(testset))

    model = train_SVD(trainset)
    predictions = model.test(testset)
    print("RMSE of SVD is : ")
    accuracy.rmse(predictions)

    #Use all the data for the model in the app.py
    full_trainset = data.build_full_trainset()
    final_model = train_SVD(full_trainset)
    
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(final_model, f)
    print(f"Model saved to {MODEL_PATH}")

