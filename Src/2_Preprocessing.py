import pandas as pd
import numpy as np

def data_cleaning():
    address = r"D:\Full projet\Anime_recommendation_system\Data\my_anime_raw_dataset.csv"
    df = pd.read_csv(address)
    
    # View data
    print(df.head())
    print(df.info())
    non_null_percentage = df.notna().mean() * 100
    print(non_null_percentage)
    print(df.describe())

    df = df.drop_duplicates()
    print("=== After drop duplicates ===")
    non_null_percentage = df.notna().mean() * 100
    print(non_null_percentage)
data_cleaning()