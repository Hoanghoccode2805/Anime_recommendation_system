import pickle
import pandas as pd
import config
from train_model import load_cleaned_data
from tqdm import tqdm
 
def load_model():
    with open(config.MODEL_PATH, "rb") as f:
        return pickle.load(f)
 
 
def load_anime_metadata():
    return pd.read_csv(config.ANIME_METADATA_PATH)
 
 
def get_recommendations(model, df, userid, n=5):
    all_anime_ids = df['anime_id'].unique()
    user_animes = df[df['user_id'] == userid]['anime_id'].unique()
 
    # only build pairs for THIS user, not build_anti_testset() for everyone
    user_pairs = [
        (userid, aid, 0) 
        for aid in tqdm(all_anime_ids, desc="Building pairs")  
        if aid not in user_animes
    ]
 
    # score all pairs in one call instead of looping model.test() one by one
    predictions = []
    for pair in tqdm(user_pairs, desc="Predicting"):   
        predictions.append(model.test([pair])[0])
    
    predictions.sort(key=lambda x: x.est, reverse=True)
    return [(p.iid, p.est) for p in predictions[:n]]
 
 
if __name__ == "__main__":
    model = load_model()
    df = load_cleaned_data()
    anime_meta = load_anime_metadata()
    
    recs = get_recommendations(model, df, userid = 17, n = 5)
    for anime_id, pred_rating in recs:
        row = anime_meta[anime_meta['anime_id'] == anime_id]
        title = row['title'].values[0] if len(row) else "Unknown"
        genres = row['genres'].values[0] if len(row) else "Unknown"
        print(f"{title} (id = {anime_id}) (genres = {genres}) -> predicted rating: {pred_rating:.2f}")