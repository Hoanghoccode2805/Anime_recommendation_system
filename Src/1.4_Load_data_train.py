import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import urllib.parse

def load_merged_data_from_sql():
    load_dotenv()
    raw_password = os.getenv("DB_PASSWORD")
    encoded_password = urllib.parse.quote_plus(raw_password)
    DATABASE_URL = f"postgresql://postgres:{encoded_password}@127.0.0.1:5432/Anime_recommendation_system_database"
    engine = create_engine(DATABASE_URL)
    print("Connecting to PostgreSQL database")
    print("Executing SQL JOIN query to fetch analytical dataset ")
    query = """
    SELECT 
        r.user_id,
        r.anime_id,
        r.rating,
        a.title,
        a.score,
        a.rank,
        a.popularity,
        a.members,
        a.favorites,
        a.episodes,
        a.type,
        a.duration,
        a.status,
        a.genres,
        a.studios   
    FROM user_ratings r JOIN anime_data a ON (r.anime_id = a.anime_id)
    """
    chunk_size = 1000000
    chunks = []
    
    for chunk in pd.read_sql(query, con=engine, chunksize=chunk_size):
        chunks.append(chunk)
        print(f"   -> Loaded chunk {len(chunks)} ({len(chunk):,} rows fetched)")
        
    # Gộp các khối lại thành một DataFrame duy nhất nếu RAM máy bạn còn đủ chứa
    df_merged = pd.concat(chunks, ignore_index=True)
    print(f" Successfully loaded dataset. Total records fetched: {len(df_merged):,}")
    return df_merged  
    
if __name__ == "__main__":
    df_train = load_merged_data_from_sql()
    print(df_train.head())
    print(df_train.info())
    df_train.to_csv("D:\Full projet\Anime_recommendation_system\Data\full_raw_data.csv", index=False)
    print("Successfully saved data to 'full_raw_data.csv'!")
