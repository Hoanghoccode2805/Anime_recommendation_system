import streamlit as st
import joblib
from config import MODEL_PATH
from recommend import load_model, load_anime_metadata, get_recommendations
from train_model import load_cleaned_data

st.title("Anime Recommendation System")

@st.cache_resource
def get_model():
    model = joblib.load(MODEL_PATH)
    return model

@st.cache_data
def get_data():
    df = load_cleaned_data()
    anime_meta = load_anime_metadata()
    return df, anime_meta

with st.spinner("Load model and data..."):
    model = get_model()
    df, anime_meta = get_data()

user_id = st.number_input("Enter User ID", min_value=1, step=1)
if st.button('Recommend'):
    with st.spinner("Taking suggestions ..."):
        recs = get_recommendations(model, df, userid=user_id, n=5)
        for anime_id, pred_rating in recs:
            row = anime_meta[anime_meta['anime_id'] == anime_id]
            title = row['title'].values[0] if len(row) else "Unknown"
            genres = row['genres'].values[0] if len(row) else "Unknown"
            st.write(f"**{title}** ({genres}) → predicted rating: {pred_rating:.2f}")
