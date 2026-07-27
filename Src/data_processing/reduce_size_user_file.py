import pandas as pd
from config import RATING_COMPLETE_PATH, USER_RATING_SMALL_PATH


def reduce_user_ratings(
    large_file_path,
    output_file_path,
    chunk_size=500_000,
    min_ratings=1000,
):
    print("STEP 1: Scanning the file to count ratings per user...")

    # Dictionary to keep track of the frequency of each user_id
    user_counts = {}

    # Read only user_id to optimize RAM usage
    for chunk in pd.read_csv(
        large_file_path,
        chunksize=chunk_size,
        usecols=["user_id"],
    ):
        counts = chunk["user_id"].value_counts()

        for user_id, count in counts.items():
            user_counts[user_id] = user_counts.get(user_id, 0) + count

    # Keep active users only
    active_users = {
        user_id
        for user_id, count in user_counts.items()
        if count >= min_ratings
    }

    print(
        f"Found {len(active_users)} active users "
        f"(rated >= {min_ratings} anime titles)."
    )

    print("\nSTEP 2: Filtering and saving data...")

    is_first_chunk = True
    total_rows_saved = 0

    # Stream the source file again and retain active users
    for chunk in pd.read_csv(large_file_path, chunksize=chunk_size):
        filtered_chunk = chunk[chunk["user_id"].isin(active_users)]

        if not filtered_chunk.empty:
            filtered_chunk.to_csv(
                output_file_path,
                mode="w" if is_first_chunk else "a",
                index=False,
                header=is_first_chunk,
            )

            is_first_chunk = False
            total_rows_saved += len(filtered_chunk)

            print(
                f"--- Chunk processed. "
                f"Total rows saved so far: {total_rows_saved:,}"
            )

    print(f"\nProcess finished! Output saved to: {output_file_path}")
    print(f"Total rows remaining: {total_rows_saved:,}")


if __name__ == "__main__":
    reduce_user_ratings(
        large_file_path=RATING_COMPLETE_PATH,
        output_file_path=USER_RATING_SMALL_PATH,
        chunk_size=500_000,
        min_ratings=1000,
    )