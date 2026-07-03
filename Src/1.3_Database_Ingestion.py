import pandas as pd
from sqlalchemy import create_engine, Integer, Float, String, Text, ForeignKey,text
from sqlalchemy.types import Integer,Float
from dotenv import load_dotenv
import os
import urllib.parse


load_dotenv()
raw_password = os.getenv("DB_PASSWORD")
encoded_password = urllib.parse.quote_plus(raw_password)
DATABASE_URL = f"postgresql://postgres:{encoded_password}@127.0.0.1:5432/Anime_recommendation_system_database"
engine = create_engine(DATABASE_URL)
print("Connecting to PostgreSQL database")

anime_csv_path = r"D:\Full projet\Anime_recommendation_system\Data\my_anime_raw_dataset.csv"
user_csv_path = r"D:\Full projet\Anime_recommendation_system\Data\user_rating_small.csv"

#A INGEST ANIME DATA
print("\n ---- Processing Anime Table ----")
df_anime = pd.read_csv(anime_csv_path)

duplicates = df_anime[df_anime.duplicated(subset=['anime_id'], keep=False)]
print(f"The number of duplicate lines anime_id: {len(duplicates)}")
print(duplicates.sort_values('anime_id'))
df_anime = df_anime.drop_duplicates(subset=['anime_id'], keep='first')

anime_data_types = {
    'anime_id' : Integer(),
    'title' : Text(),
    'score' : Float(),
    'rank' : Float(),
    'popularity' : Integer(),
    'members' : Integer(),
    'favorites' : Integer(),
    'episodes' : Float(),
    'type' : Text(),
    'duration' : Text(),
    'status' : Text(),
    'genres' : Text(),
    'studios' : Text()
}

df_anime.to_sql(
    name='anime_data', 
    con=engine, 
    if_exists='replace', 
    index=False, 
    dtype=anime_data_types
)

with engine.connect() as connection:
    connection.execute(text("ALTER TABLE anime_data ADD PRIMARY KEY (anime_id);"))
print(" Successfully created 'anime_data' table with Primary Key.")

# B. INGEST USER RATINGS
print("\n--- Processing User Ratings Table ---")
df_rating = pd.read_csv(user_csv_path)

# Define precise SQL Data Types for the Ratings table
rating_data_types = {
    'user_id': Integer(),
    'anime_id': Text(),
    'user_rating': Integer()
}

# Upload User Ratings to PostgreSQL
df_rating.to_sql(
    name='user_ratings', 
    con=engine, 
    if_exists='replace', 
    index=False, 
    dtype=rating_data_types
)

# Explicitly enforce Foreign Key constraint via raw SQL
# This links 'user_ratings.anime_id' to 'anime_metadata.anime_id'
with engine.connect() as connection:
    connection.execute(
        text("ALTER TABLE user_ratings ADD CONSTRAINT fk_anime FOREIGN KEY (anime_id) REFERENCES anime_data (anime_id);")
    )
    connection.commit()
print(" Successfully created 'user_ratings' table with Foreign Key constraint.")

print("\n Data Ingestion Pipeline completed successfully!")