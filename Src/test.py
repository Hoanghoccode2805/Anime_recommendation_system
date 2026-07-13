import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler,LabelEncoder
from surprise import Dataset, Reader
from surprise.model_selection import train_test_split
from surprise import SVD
from surprise import accuracy
from tqdm import tqdm

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
print(f"Số user: {df_raw['user_id'].nunique()}")
print(f"Số anime: {df_raw['anime_id'].nunique()}")
print(f"Tổng dòng rating: {len(df_raw)}")

print('=============================================================')
# 1. Check số dòng bị duplicate hoàn toàn (user_id, anime_id)
print(df_raw.duplicated(subset=['user_id', 'anime_id']).sum())

# 2. Check tổng số anime_id unique trong df_raw đã merge — phải khớp ~9975
print(df_raw['anime_id'].nunique())

# 3. Xem cụ thể user có 178368 dòng là ai, và họ có bao nhiêu anime_id UNIQUE thật
top_user = df_raw[df_raw['rating']>=7].groupby('user_id').size().idxmax()
print(df_raw[df_raw['user_id']==top_user]['anime_id'].nunique())  # nếu số này << 178368 → xác nhận duplicate