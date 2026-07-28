import pickle
import pandas as pd
from surprise.model_selection import train_test_split
from surprise import Dataset, Reader, SVD, BaselineOnly, accuracy
from config import DEMO_MODEL_PATH, DEMO_CLEANED_DATA_PATH, MODEL_DIR, TEST_SIZE, RANDOM_STATE
from Src.model_SVD.train_model import build_dataset, train_SVD

def load_demo_cleaned_data():
    return pd.read_csv(DEMO_CLEANED_DATA_PATH)

if __name__ == "__main__":
    df = load_demo_cleaned_data()
    data = build_dataset(df)
    trainset, testset = train_test_split(data, test_size= TEST_SIZE, random_state= RANDOM_STATE)
        
    # simple baseline (global mean + user/item bias, no latent factors)
    # so the SVD's RMSE has something to be compared against
    print("---- For BaseLineOnly ----")
    baseline = BaselineOnly()
    baseline.fit(trainset)
    print("RMSE is : ")
    accuracy.rmse(baseline.test(testset))

    print("---- For Model SVD ----")
    model = train_SVD(trainset)
    predictions = model.test(testset)
    print("RMSE of SVD is : ")
    accuracy.rmse(predictions)

    #Use all the data for the model in the app.py
    full_trainset = data.build_full_trainset()
    final_model = train_SVD(full_trainset)
    
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    with open(DEMO_MODEL_PATH, "wb") as f:
        pickle.dump(final_model, f)
    print(f"Model saved to {DEMO_MODEL_PATH}")