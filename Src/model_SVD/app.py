import streamlit as st
from config import MODEL_PATH
from Src.model_SVD.recommend import load_model, load_anime_metadata, get_recommendations
from Src.model_SVD.train_model import load_cleaned_data

st.title("Anime Recommendation System")

@st.cache_resource
def get_model():
    model = load_model()
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
    known_user_ids = set(df["user_id"].unique())
    if user_id not in known_user_ids:
        st.warning("This UserID does not have a review history in the system")
        st.stop()

    with st.spinner("Taking suggestions ..."):
        recs = get_recommendations(model, df, userid=user_id, n=5)
        for anime_id, pred_rating in recs:
            row = anime_meta[anime_meta['anime_id'] == anime_id]
            title = row['title'].values[0] if len(row) else "Unknown"
            genres = row['genres'].values[0] if len(row) else "Unknown"
            st.write(f"**{title}** ({genres}) → predicted rating: {pred_rating:.2f}")
