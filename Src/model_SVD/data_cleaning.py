import pandas as pd
import config 
 
 
def load_data():
    df = pd.read_csv(config.RAW_DATA_PATH)
    print(f"Loaded {len(df)} rows, {df['user_id'].nunique()} users, {df['anime_id'].nunique()} anime")
    return df
 
 
def remove_duplicates(df):
    before = len(df)
    df = df.drop_duplicates(subset=['user_id', 'anime_id'])
    print(f"Removed {before - len(df)} duplicate (user_id, anime_id) rows")
    return df
 
 
def save_anime_metadata(df):
    # one row per anime_id, so recommend.py can look up title/genres fast
    cols = [c for c in ['anime_id', 'title', 'genres', 'score', 'type', 'studios'] if c in df.columns]
    anime_meta = df[cols].drop_duplicates(subset='anime_id')
    anime_meta.to_csv(config.ANIME_METADATA_PATH, index=False)
    print(f"Saved {len(anime_meta)} unique anime to {config.ANIME_METADATA_PATH}")
 
 
def remove_low_variance_users(df):
    # users who rate almost everything the same value (e.g. always 7)
    # give the model no real signal about their taste, so we drop them
    user_std = df.groupby('user_id')['rating'].std()
    good_users = user_std[user_std >= config.MIN_RATING_STD].index
    before = df['user_id'].nunique()
    df = df[df['user_id'].isin(good_users)]
    print(f"Removed {before - df['user_id'].nunique()} low-variance users")
    return df
 
 
def filter_sparsity(df):
    # keep only users/anime with enough ratings
    # loop because removing one can push another below the limit
    while True:
        before = len(df)
        user_counts = df['user_id'].value_counts()
        anime_counts = df['anime_id'].value_counts()
        df = df[df['user_id'].isin(user_counts[user_counts >= config.MIN_USER_RATINGS].index)]
        df = df[df['anime_id'].isin(anime_counts[anime_counts >= config.MIN_ANIME_RATINGS].index)]
        if len(df) == before:
            break
    print(f"After sparsity filter: {len(df)} rows, {df['user_id'].nunique()} users, {df['anime_id'].nunique()} anime")
    return df
 
 
if __name__ == "__main__":
    df = load_data()
    df = remove_duplicates(df)
    save_anime_metadata(df)
    df = remove_low_variance_users(df)
    df = filter_sparsity(df)
    df.to_csv(config.CLEANED_DATA_PATH, index=False)
    print(f"Cleaned data saved to {config.CLEANED_DATA_PATH}")
 