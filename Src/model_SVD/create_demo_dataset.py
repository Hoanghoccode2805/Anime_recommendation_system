import random
import pandas as pd
from config import CLEANED_DATA_PATH, DEMO_CLEANED_DATA_PATH


DEFAULT_NUMBER_OF_USERS = 300
DEFAULT_CHUNK_SIZE = 250_000
RANDOM_STATE = 42


def get_user_ids(input_path, chunk_size):
    """Read only user_id in chunks to avoid loading the full CSV into RAM."""
    user_ids = set()

    for chunk in pd.read_csv(
        input_path,
        usecols=["user_id"],
        chunksize=chunk_size,
    ):
        user_ids.update(chunk["user_id"].dropna().unique())

    return sorted(user_ids)


def create_demo_dataset(
    input_path,
    output_path,
    number_of_users=DEFAULT_NUMBER_OF_USERS,
    chunk_size=DEFAULT_CHUNK_SIZE,
    random_state=RANDOM_STATE,
):
    """Create a smaller rating-only dataset for the public Streamlit demo."""
    if not input_path.exists():
        raise FileNotFoundError(f"Input dataset was not found: {input_path}")

    print("Step 1: Reading user IDs from the cleaned dataset...")
    all_user_ids = get_user_ids(input_path, chunk_size)

    if number_of_users > len(all_user_ids):
        raise ValueError(
            f"Requested {number_of_users} users, but only "
            f"{len(all_user_ids)} users are available."
        )

    random_generator = random.Random(random_state)
    selected_user_ids = set(
        random_generator.sample(all_user_ids, number_of_users)
    )

    print(
        f"Step 2: Keeping all ratings from {number_of_users} randomly "
        "selected users..."
    )

    # A new run must not append to an older demo dataset.
    if output_path.exists():
        output_path.unlink()

    is_first_chunk = True
    total_rows_saved = 0

    for chunk in pd.read_csv(input_path, chunksize=chunk_size):
        demo_chunk = chunk[
            chunk["user_id"].isin(selected_user_ids)
        ][["user_id", "anime_id", "rating"]]

        if demo_chunk.empty:
            continue

        demo_chunk.to_csv(
            output_path,
            mode="w" if is_first_chunk else "a",
            header=is_first_chunk,
            index=False,
        )

        is_first_chunk = False
        total_rows_saved += len(demo_chunk)

    if total_rows_saved == 0:
        raise RuntimeError("The demo dataset contains no ratings.")

    print(f"Demo dataset saved to: {output_path}")
    print(f"Users selected: {number_of_users:,}")
    print(f"Ratings saved: {total_rows_saved:,}")


if __name__ == "__main__":
    create_demo_dataset(
        input_path=CLEANED_DATA_PATH,
        output_path=DEMO_CLEANED_DATA_PATH,
        number_of_users=DEFAULT_NUMBER_OF_USERS,
    )
