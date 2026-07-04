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

print(" Checking and cleaning old database constraints ")
with engine.connect() as connection:
    connection.execute(text("ALTER TABLE IF EXISTS user_ratings DROP CONSTRAINT IF EXISTS fk_anime;"))
    connection.commit()
print(" Constraints cleaned successfully. Ready for ingestion.")

#A INGEST ANIME DATA
print("\n ---- Processing Anime Table ----")
df_anime = pd.read_csv(anime_csv_path)

duplicates_anime = df_anime[df_anime.duplicated(subset=['anime_id'], keep=False)]
print(f"The number of duplicate lines anime_id: {len(duplicates_anime)}")
print("\n--- Displaying duplicated anime interaction rows ---")
print(duplicates_anime.sort_values('anime_id'))
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
    connection.commit()
print(" Successfully created 'anime_data' table with Primary Key.")

# B. INGEST USER RATINGS
print("\n--- Processing User Ratings Table ---")
df_rating = pd.read_csv(user_csv_path)

# Find and display duplicated ratings (same user rating the same anime multiple times)
duplicates_user = df_rating[df_rating.duplicated(subset=['user_id', 'anime_id'], keep=False)]
print(f"The number of duplicate lines based on user_id and anime_id: {len(duplicates_user)}")

# Optional: Print out the duplicated rows sorted by user_id to easily inspect them
if not duplicates_user.empty:
    print("\n--- Displaying duplicated user interaction rows ---")
    print(duplicates_user.sort_values(by=['user_id', 'anime_id']))

# Drop the duplicate records, keeping only the first occurrence
df_rating = df_rating.drop_duplicates(subset=['user_id', 'anime_id'], keep='first')
print(f"Duplicates handled. Total remaining interaction records: {len(df_rating):,}")
with engine.connect() as connection:
    connection.execute(text("ALTER TABLE IF EXISTS user_ratings DROP CONSTRAINT IF EXISTS fk_anime;"))
    connection.commit()
# Define precise SQL Data Types for the Ratings table
rating_data_types = {
    'user_id': Integer(),
    'anime_id': Integer(),
    'rating': Integer()
}

# OPTIMIZED DATA UPLOAD USING CHUNKING
chunk_size = 500000
total_chunks = (len(df_rating) // chunk_size) + 1
print(f"\n Uploading {len(df_rating):,} rows to PostgreSQL in {total_chunks} chunks ")

# Upload User Ratings to PostgreSQL
for i in range(total_chunks):
    start_idx = i*chunk_size
    end_idx = min((i + 1) * chunk_size, len(df_rating))
    chunk = df_rating.iloc[start_idx:end_idx]
    mode = 'replace' if i == 0 else 'append'
    chunk.to_sql(
        name='user_ratings', 
        con=engine, 
        if_exists=mode, 
        index=False, 
        dtype=rating_data_types
    )
    
    print(f"   -> Successfully loaded chunk {i+1}/{total_chunks} (Rows {start_idx:,} to {end_idx:,})")
print(" Successfully uploaded all user rating records.")

# Explicitly enforce Foreign Key constraint via raw SQL
# This links 'user_ratings.anime_id' to 'anime_metadata.anime_id'
with engine.connect() as connection:
    connection.execute(
        text("""DELETE FROM user_ratings r
        WHERE NOT EXISTS (
            SELECT 1 FROM anime_data a WHERE a.anime_id = r.anime_id
        );""")
    )
    connection.execute(
        text("ALTER TABLE user_ratings ADD CONSTRAINT fk_anime FOREIGN KEY (anime_id) REFERENCES anime_data (anime_id);")
    )
    connection.commit()
print(" Successfully created 'user_ratings' table with Foreign Key constraint.")

print("\n Data Ingestion Pipeline completed successfully!")