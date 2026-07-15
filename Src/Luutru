import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler,LabelEncoder
from surprise import Dataset, Reader
from surprise.model_selection import train_test_split
from surprise import SVD
from surprise import accuracy
from tqdm import tqdm
from collections import defaultdict

# A. Load and Prepare the Data
# Load the dataset
address = r"D:\Full projet\Anime_recommendation_system\Data\full_raw_data.csv"
df_raw = pd.read_csv(address)

# Define the reader
reader = Reader(rating_scale=(1,10))

# Load the data into Surprise
data = Dataset.load_from_df(df_raw[['user_id', 'anime_id', 'rating']], reader)

# Split the data into training and testing sets
trainset,testset = train_test_split(data, test_size=0.25, random_state = 42 )

# B. Train the SVD Model
# Initialize the SVD model
model = SVD(verbose=True, random_state = 42)
# Train the model
model.fit(trainset)
# Make predictions 
predictions = model.test(testset)
# Evaluate the model
accuracy.rmse(predictions)

def precision_recall_at_k(predictions, k=10, threshold = 9):
    user_est_true = defaultdict(list)
    #uid = userID, iid = itemID, true_r = rating real in data by user, est = rating by model
    for uid, iid, true_r, est, _ in predictions:
        user_est_true[uid].append((est,true_r))
    
    precisions = {}
    recalls = {}
    for uid, user_ratings in user_est_true.items():
        # lambda input: ouput
        # reverse = True --> from large to small value
        #         = False --> from small to large value
        user_ratings.sort(key = lambda x: x[0], reverse = True) 

        # Number of anime that users actually like (real ratings >= threshold)
        n_rel = sum((true_r >= threshold) for (_,true_r) in user_ratings)
        # In top-K, the number of recommended anime models
        n_rec_k =  min(k,len(user_ratings))
        # In that top-K, the number of anime that are actually relevant
        n_rel_and_rec_k = sum(
            (true_r >= threshold) for (est, true_r) in user_ratings[:k]
        )

        precisions[uid] = n_rel_and_rec_k / n_rec_k if n_rec_k != 0 else 0
        recalls[uid] = n_rel_and_rec_k / n_rel if n_rel != 0 else 0

    return precisions, recalls


# C. Generate Recommendations
def get_recommendations(userid, n=5):

    all_anime_ids = df_raw['anime_id'].unique()

    user_animes = df_raw[df_raw['user_id'] == userid]['anime_id'].unique()
    
    user_pairs = [
        (userid, aid, 0) 
        for aid in tqdm(all_anime_ids, desc="Building pairs")  
        if aid not in user_animes
    ]
    
    predictions = []
    for pair in tqdm(user_pairs, desc="Predicting"):   
        predictions.append(model.test([pair])[0])
    
    predictions.sort(key=lambda x: x.est, reverse=True)
    return [(p.iid, p.est) for p in predictions[:n]]

# Example: Get top 5 recommendations for user 17
anime_meta = pd.read_csv(r"D:\Full projet\Anime_recommendation_system\Data\full_raw_data.csv") 

recs = get_recommendations(17, 5)
for anime_id, pred_rating in recs:
    title = anime_meta[anime_meta['anime_id'] == anime_id]['title'].values
    title = title[0] if len(title) else "Unknown"
    genres = anime_meta[anime_meta['anime_id'] == anime_id]['genres'].values
    genres = genres[0] if len(genres) else "Unknown"
    print(f"{title} (id = {anime_id}) (genres = {genres}) → predicted rating: {pred_rating:.2f}")
    
# Calcul precision and recall of this system
precisions, recalls = precision_recall_at_k(predictions, k=10, threshold=9)

avg_precision = sum(prec for prec in precisions.values()) / len(precisions)
avg_recall = sum(rec for rec in recalls.values()) / len(recalls)

print(f"Precision@10: {avg_precision:.4f}")
print(f"Recall@10: {avg_recall:.4f}")