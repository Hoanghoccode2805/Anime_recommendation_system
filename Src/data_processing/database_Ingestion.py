import os
import urllib.parse

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import Float, Integer, Text, create_engine, text

from config import MY_ANIME_RAW_DATASET, USER_RATING_SMALL_PATH


def create_database_engine():
    load_dotenv()

    raw_password = os.getenv("DB_PASSWORD")
    if not raw_password:
        raise ValueError("DB_PASSWORD is missing. Check your .env file.")

    encoded_password = urllib.parse.quote_plus(raw_password)

    database_url = (
        "postgresql://postgres:"
        f"{encoded_password}@127.0.0.1:5432/"
        "Anime_recommendation_system_database"
    )

    print("Connecting to PostgreSQL database")
    return create_engine(database_url)


def drop_user_ratings_foreign_key(engine):
    print("Checking and cleaning old database constraints...")

    with engine.connect() as connection:
        connection.execute(
            text(
                "ALTER TABLE IF EXISTS user_ratings "
                "DROP CONSTRAINT IF EXISTS fk_anime;"
            )
        )
        connection.commit()

    print("Constraints cleaned successfully. Ready for ingestion.")


def ingest_anime_data(engine, anime_csv_path):
    print("\n--- Processing Anime Table ---")

    df_anime = pd.read_csv(anime_csv_path)

    duplicates_anime = df_anime[
        df_anime.duplicated(subset=["anime_id"], keep=False)
    ]

    print(f"Number of duplicate anime_id rows: {len(duplicates_anime)}")

    if not duplicates_anime.empty:
        print("\n--- Displaying duplicated anime rows ---")
        print(duplicates_anime.sort_values("anime_id"))

    df_anime = df_anime.drop_duplicates(
        subset=["anime_id"],
        keep="first",
    )

    anime_data_types = {
        "anime_id": Integer(),
        "title": Text(),
        "score": Float(),
        "rank": Float(),
        "popularity": Integer(),
        "members": Integer(),
        "favorites": Integer(),
        "episodes": Float(),
        "type": Text(),
        "duration": Text(),
        "status": Text(),
        "genres": Text(),
        "studios": Text(),
    }

    df_anime.to_sql(
        name="anime_data",
        con=engine,
        if_exists="replace",
        index=False,
        dtype=anime_data_types,
    )

    with engine.connect() as connection:
        connection.execute(
            text("ALTER TABLE anime_data ADD PRIMARY KEY (anime_id);")
        )
        connection.commit()

    print("Successfully created 'anime_data' table with Primary Key.")


def ingest_user_ratings(engine, user_csv_path, chunk_size=500_000):
    print("\n--- Processing User Ratings Table ---")

    df_rating = pd.read_csv(user_csv_path)

    duplicates_user = df_rating[
        df_rating.duplicated(subset=["user_id", "anime_id"], keep=False)
    ]

    print(
        "Number of duplicate rows based on user_id and anime_id: "
        f"{len(duplicates_user)}"
    )

    if not duplicates_user.empty:
        print("\n--- Displaying duplicated user-rating rows ---")
        print(duplicates_user.sort_values(by=["user_id", "anime_id"]))

    df_rating = df_rating.drop_duplicates(
        subset=["user_id", "anime_id"],
        keep="first",
    )

    print(
        "Duplicates handled. Total remaining interaction records: "
        f"{len(df_rating):,}"
    )

    rating_data_types = {
        "user_id": Integer(),
        "anime_id": Integer(),
        "rating": Integer(),
    }

    total_chunks = (len(df_rating) + chunk_size - 1) // chunk_size

    print(
        f"\nUploading {len(df_rating):,} rows to PostgreSQL "
        f"in {total_chunks} chunks."
    )

    for index in range(total_chunks):
        start_index = index * chunk_size
        end_index = min((index + 1) * chunk_size, len(df_rating))

        chunk = df_rating.iloc[start_index:end_index]
        write_mode = "replace" if index == 0 else "append"

        chunk.to_sql(
            name="user_ratings",
            con=engine,
            if_exists=write_mode,
            index=False,
            dtype=rating_data_types,
        )

        print(
            f"-> Loaded chunk {index + 1}/{total_chunks} "
            f"(rows {start_index:,} to {end_index:,})"
        )

    print("Successfully uploaded all user rating records.")


def add_anime_foreign_key(engine):
    with engine.connect() as connection:
        connection.execute(
            text(
                """
                DELETE FROM user_ratings AS rating
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM anime_data AS anime
                    WHERE anime.anime_id = rating.anime_id
                );
                """
            )
        )

        connection.execute(
            text(
                """
                ALTER TABLE user_ratings
                ADD CONSTRAINT fk_anime
                FOREIGN KEY (anime_id)
                REFERENCES anime_data (anime_id);
                """
            )
        )

        connection.commit()

    print("Successfully created foreign key 'fk_anime'.")


def run_ingestion(anime_csv_path, user_csv_path):
    engine = create_database_engine()

    try:
        drop_user_ratings_foreign_key(engine)
        ingest_anime_data(engine, anime_csv_path)
        ingest_user_ratings(engine, user_csv_path)
        add_anime_foreign_key(engine)

        print("\nData ingestion pipeline completed successfully!")
    finally:
        engine.dispose()


if __name__ == "__main__":
    run_ingestion(
        anime_csv_path=MY_ANIME_RAW_DATASET,
        user_csv_path=USER_RATING_SMALL_PATH,
    )