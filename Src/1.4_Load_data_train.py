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
    first_chunk = True

    for chunk in pd.read_sql(query, con=engine, chunksize=1000000):
        chunk.to_csv(
            r"D:\Full projet\Anime_recommendation_system\Data\full_raw_data.csv",
            mode="w" if first_chunk else "a",
            header=first_chunk,
            index=False
        )
        first_chunk = False
        print(f"Saved {len(chunk):,} rows")
    
load_merged_data_from_sql()
