import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

def load_merged_data_from_sql():
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    print("Executing SQL JOIN query to fetch analytical dataset ")
    query = """
    SELECT 
        r.user_id,
        r.anime_id,
        r.rating,
        a.anime_id
        a.title
        a.score
        a.rank
        a.popularity
        a.members
        a.favorites
        a.episodes
        a.type
        a.duration
        a.status
        a.genres
        a.studios
    FROM user_ratings r JOIN anime_data ON (r.anime_id = a.anime_id)
    """
    df_merged = pd.read_sql(query,con = engine)
    print(f" Successfully loaded dataset. Total records fetched: {len(df_merged):,}")
    return df_merged


def data_cleaning():
    address = r"D:\Full projet\Anime_recommendation_system\Data\my_anime_raw_dataset.csv"
    df = pd.read_csv(address)
    
    
if __name__ == "__main__":
    df_train = load_merged_data_from_sql()
    print(df_train.head())
    print(df_train.info())