import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Streamlit runs this file from Src/model_SVD, so add the project root before
# importing config.py from the root directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import MIN_ANIME_RATINGS, SVD_PARAMS, TOP_K
from Src.model_SVD.recommend import (
    get_recommendations,
    load_anime_metadata,
    load_demo_model,
)
from Src.model_SVD.train_demo_model import load_demo_cleaned_data


st.set_page_config(
    page_title="Anime Recommendation System",
    page_icon="🎬",
    layout="centered",
)


@st.cache_resource
def get_model():
    """Load the trained SVD model once while the Streamlit app is running."""
    return load_demo_model()


def build_community_stats(df, anime_meta):
    """Create the small tables used by the community dashboard."""
    top_users = (
        df.groupby("user_id")
        .size()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name="ratings_count")
    )

    anime_stats = (
        df.groupby("anime_id")["rating"]
        .agg(ratings_count="size", average_user_rating="mean")
        .reset_index()
    )

    anime_stats = anime_stats.merge(
        anime_meta[["anime_id", "title"]],
        on="anime_id",
        how="left",
    )
    anime_stats["title"] = anime_stats["title"].fillna("Unknown")

    top_most_rated = anime_stats.sort_values(
        "ratings_count",
        ascending=False,
    ).head(10)

    top_user_rated = anime_stats[
        anime_stats["ratings_count"] >= MIN_ANIME_RATINGS
    ].sort_values("average_user_rating", ascending=False).head(10)

    top_mal_score = anime_meta[["anime_id", "title", "score", "genres"]].copy()
    top_mal_score["score"] = pd.to_numeric(top_mal_score["score"], errors="coerce")
    top_mal_score = top_mal_score.dropna(subset=["score"])
    top_mal_score = top_mal_score.sort_values("score", ascending=False).head(10)

    rating_distribution = (
        df["rating"]
        .value_counts()
        .sort_index()
        .rename_axis("rating")
        .reset_index(name="count")
    )

    return {
        "top_users": top_users,
        "top_most_rated": top_most_rated,
        "top_user_rated": top_user_rated,
        "top_mal_score": top_mal_score,
        "rating_distribution": rating_distribution,
    }


@st.cache_data
def get_dashboard_data():
    """Load the project data and compute dashboard tables only once."""
    df = load_demo_cleaned_data()
    anime_meta = load_anime_metadata()
    community_stats = build_community_stats(df, anime_meta)
    return df, anime_meta, community_stats


class AnimeRecommendationDashboard:
    def __init__(self, model, df, anime_meta, community_stats):
        self.model = model
        self.df = df
        self.anime_meta = anime_meta
        self.community_stats = community_stats

    def show_kpis(self):
        average_rating = self.df["rating"].mean()

        user_col, anime_col, rating_col, average_col = st.columns(4)
        user_col.metric("Users", f"{self.df['user_id'].nunique():,}")
        anime_col.metric("Anime", f"{self.df['anime_id'].nunique():,}")
        rating_col.metric("Ratings", f"{len(self.df):,}")
        average_col.metric("Average rating", f"{average_rating:.2f}/10")

    def get_user_genres(self, user_ratings):
        """Return genres the selected user has rated most often."""
        user_anime = user_ratings[["anime_id"]].merge(
            self.anime_meta[["anime_id", "genres"]],
            on="anime_id",
            how="left",
        )

        genres = user_anime["genres"].dropna().str.split(",").explode().str.strip()

        return (
            genres[genres != ""]
            .value_counts()
            .head(10)
            .rename_axis("genre")
            .reset_index(name="count")
        )

    def show_user_profile(self, user_id):
        user_ratings = self.df[self.df["user_id"] == user_id]

        rating_count = len(user_ratings)
        average_rating = user_ratings["rating"].mean()
        liked_count = (user_ratings["rating"] >= 9).sum()

        count_col, average_col, liked_col = st.columns(3)
        count_col.metric("Anime rated", f"{rating_count:,}")
        average_col.metric("Your average rating", f"{average_rating:.2f}/10")
        liked_col.metric("Ratings of 9 or 10", f"{liked_count:,}")

        left_col, right_col = st.columns(2)

        with left_col:
            st.subheader("Your rating distribution")
            user_rating_distribution = (
                user_ratings["rating"]
                .value_counts()
                .sort_index()
                .rename_axis("rating")
                .reset_index(name="count")
            )
            st.bar_chart(user_rating_distribution, x="rating", y="count")

        with right_col:
            st.subheader("Your most-rated genres")
            user_genres = self.get_user_genres(user_ratings)

            if user_genres.empty:
                st.info("Genre data is not available for this user yet.")
            else:
                st.bar_chart(user_genres, x="genre", y="count")

    def show_recommendations(self, user_id):
        st.subheader("Personalized recommendations")

        with st.spinner("Finding anime you may enjoy..."):
            recommendations = get_recommendations(
                self.model,
                self.df,
                userid=user_id,
                n=TOP_K,
            )

        if not recommendations:
            st.info("No unseen anime is available to recommend.")
            return

        recommendation_df = pd.DataFrame(
            recommendations,
            columns=["anime_id", "predicted_rating"],
        )

        recommendation_df = recommendation_df.merge(
            self.anime_meta[["anime_id", "title", "genres", "score"]],
            on="anime_id",
            how="left",
        )
        recommendation_df["title"] = recommendation_df["title"].fillna("Unknown")
        recommendation_df["genres"] = recommendation_df["genres"].fillna("Unknown")
        recommendation_df["predicted_rating"] = recommendation_df[
            "predicted_rating"
        ].round(2)

        st.dataframe(
            recommendation_df[
                ["title", "genres", "score", "predicted_rating"]
            ],
            hide_index=True,
            use_container_width=True,
        )

        st.caption("Predicted rating is generated by the SVD recommendation model.")
        st.bar_chart(
            recommendation_df.set_index("title")["predicted_rating"],
        )

    def show_for_you_tab(self):
        st.subheader("Find recommendations for a user")

        user_id = st.number_input(
            "Enter User ID",
            min_value=1,
            step=1,
        )

        if st.button("Recommend anime", type="primary"):
            known_user_ids = set(self.df["user_id"].unique())

            if user_id not in known_user_ids:
                st.warning("This User ID does not have a rating history in the system.")
                return

            self.show_user_profile(user_id)
            self.show_recommendations(user_id)

    def show_community_tab(self):
        st.subheader("Community insights")

        left_col, right_col = st.columns(2)

        with left_col:
            st.markdown("#### Most active users")
            st.bar_chart(
                self.community_stats["top_users"],
                x="user_id",
                y="ratings_count",
            )
            st.dataframe(
                self.community_stats["top_users"],
                hide_index=True,
                use_container_width=True,
            )

        with right_col:
            st.markdown("#### Ratings across the community")
            st.bar_chart(
                self.community_stats["rating_distribution"],
                x="rating",
                y="count",
            )

        st.markdown("#### Most-rated anime")
        st.dataframe(
            self.community_stats["top_most_rated"][
                ["title", "ratings_count", "average_user_rating"]
            ],
            hide_index=True,
            use_container_width=True,
        )

        st.markdown("#### Highest rated by users")
        st.caption(
            f"Only anime with at least {MIN_ANIME_RATINGS} ratings are included."
        )
        st.dataframe(
            self.community_stats["top_user_rated"][
                ["title", "ratings_count", "average_user_rating"]
            ],
            hide_index=True,
            use_container_width=True,
        )

        st.markdown("#### Highest MyAnimeList scores")
        st.dataframe(
            self.community_stats["top_mal_score"][
                ["title", "score", "genres"]
            ],
            hide_index=True,
            use_container_width=True,
        )

    def show_about_tab(self):
        st.subheader("About this project")
        st.write(
            "This application uses SVD collaborative filtering to predict how "
            "a user may rate anime they have not rated yet."
        )

        st.markdown("#### Model settings")
        st.json(SVD_PARAMS)

        st.markdown("#### How recommendations work")
        st.write(
            "The model learns rating patterns from users with similar tastes. "
            "It then estimates a rating for anime that the selected user has "
            "not watched or rated."
        )

    def run(self):
        st.title("🎬 Anime Recommendation System")
        st.caption("Personalized anime suggestions and community rating insights")

        self.show_kpis()
        st.divider()

        for_you_tab, community_tab, about_tab = st.tabs(
            ["🎯 For You", "📊 Community Insights", "ℹ️ About Model"]
        )

        with for_you_tab:
            self.show_for_you_tab()

        with community_tab:
            self.show_community_tab()

        with about_tab:
            self.show_about_tab()


def main():
    with st.spinner("Loading model and dashboard data..."):
        model = get_model()
        df, anime_meta, community_stats = get_dashboard_data()

    dashboard = AnimeRecommendationDashboard(
        model=model,
        df=df,
        anime_meta=anime_meta,
        community_stats=community_stats,
    )
    dashboard.run()


if __name__ == "__main__":
    main()
