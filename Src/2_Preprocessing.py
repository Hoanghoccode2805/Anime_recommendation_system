import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler,LabelEncoder
from surprise import Dataset, Reader
from surprise.model_selection import train_test_split
from surprise import SVD
from surprise import accuracy

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
model = SVD()
# Train the model
model.fit(trainset)
# Make predictions 
predictions = model.test(testset)
# Evaluate the model
accuracy.rmse(predictions)

# C. Generate Recommendations
def get_recommendations(userid, n=5):
    # build_anti_testset tự động tạo cặp (user, item) chưa rate, hiệu quả hơn loop tay
    anti_testset = trainset.build_anti_testset()
    # lọc chỉ giữ pair của đúng user này (build_anti_testset mặc định làm cho TẤT CẢ user)
    user_pairs = [x for x in anti_testset if x[0] == userid]
    
    predictions = model.test(user_pairs)
    predictions.sort(key=lambda x: x.est, reverse=True)
    return [(p.iid, p.est) for p in predictions[:n]]

# Example: Get top 5 recommendations for user 1
print(get_recommendations(17, 5))



