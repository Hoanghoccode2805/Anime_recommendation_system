import pandas as pd
import os

# File paths configuration
large_file_path = r"D:\Full projet\Anime_recommendation_system\Data\rating_complete.csv"  
output_file_path = r"D:\Full projet\Anime_recommendation_system\Data\user_rating_small.csv"

# Number of rows per chunk processed in RAM (Safe threshold for laptops)
chunk_size = 500000 

print(" STEP 1: Scanning the file to count ratings per user...")

# Dictionary to keep track of the frequency of each user_id
user_counts = {}

# Read only the 'user_id' column during the counting phase to optimize speed and RAM
for chunk in pd.read_csv(large_file_path, chunksize=chunk_size, usecols=['user_id']):
    # Count occurrences in the current chunk
    counts = chunk['user_id'].value_counts()
    for user_id, count in counts.items():
        user_counts[user_id] = user_counts.get(user_id, 0) + count

# Filter out high-quality active users (users who rated >= 2000 anime titles)
active_users = {user_id for user_id, count in user_counts.items() if count >= 4000}
print(f" Found {len(active_users)} active users (rated >= 4000 anime titles).")


print("\n STEP 2: Filtering and appending data to the output file...")

# Flags to manage the file header and track total saved rows
is_first_chunk = True
total_rows_saved = 0

# Stream the large file again and apply the active users filter
for chunk in pd.read_csv(large_file_path, chunksize=chunk_size):
    # Keep rows where the user_id belongs to the active_users set
    filtered_chunk = chunk[chunk['user_id'].isin(active_users)]
    
    if not filtered_chunk.empty:
        # Append data incrementally to avoid high memory overhead
        filtered_chunk.to_csv(
            output_file_path, 
            mode='a', 
            index=False, 
            header=is_first_chunk # Write header only for the first chunk
        )
        is_first_chunk = False
        total_rows_saved += len(filtered_chunk)
        print(f"--- Chunk processed. Total rows saved so far: {total_rows_saved:,}")

print(f"\n Process finished! The filtered dataset has been saved to: {output_file_path}")
print(f"Total rows remaining after filtering: {total_rows_saved:,} rows (RAM load successfully reduced!).")