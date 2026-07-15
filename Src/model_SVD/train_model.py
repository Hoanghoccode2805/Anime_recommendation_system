import os
import pickle
import pandas as pd
from surprise import Dataset, Reader, SVD, BaselineOnly, accuracy
from surprise.model_selection import train_test_split
import config 

def load_cleaned_data():
    return pd.read_csv(config.CLEANED_DATA_PATH)

def build_dataset(df):
    reader = Reader(rating_scale= config.RATING_SCALE)
    return Dataset.load_from_df(df[['user_id','anime_id','rating']],reader)

def train_SVD(trainset):
    model = SVD(verbose=True, random_state=config.RANDOM_STATE)
    model.fit(trainset)
    return model

if __name__ == "__main__":
    df = load_cleaned_data()
    data = build_dataset(df)
    trainset, testset = train_test_split(data, test_size= config.TEST_SIZE, random_state= config.RANDOM_STATE)
    
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
    
    os.makedirs(os.path.dirname(config.MODEL_PATH), exist_ok=True)
    with open(config.MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"Model saved to {config.MODEL_PATH}")

