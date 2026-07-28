import requests
import pandas as pd
import time
from config import MY_ANIME_RAW_DATASET

def collect_raw_anime_data(total_pages = 400):
    # This empty list will temporarily hold our clean data rows
    list_anime_record = []
    failed_pages = []
    
    for page in range(1,total_pages+1):
            print(f"Fetching data in page {page}")

            url = f"https://api.jikan.moe/v4/top/anime?page={page}"
            for attempt in range(3):
                try:
                    response = requests.get(url, timeout=30)

                    if response.status_code == 200:
                        data = response.json()

                        for anime in data["data"]:
                            genres = [genre["name"] for genre in anime["genres"]]
                            genres_str = ",".join(genres)

                            studios = ",".join(
                                studio["name"] for studio in anime["studios"]
                            )

                            record = {
                                "anime_id": anime["mal_id"],
                                "title": anime["title"],
                                "score": anime["score"],
                                "rank": anime["rank"],
                                "popularity": anime["popularity"],
                                "members": anime["members"],
                                "favorites": anime["favorites"],
                                "episodes": anime["episodes"],
                                "type": anime["type"],
                                "duration": anime["duration"],
                                "status": anime["status"],
                                "genres": genres_str,
                                "studios": studios,
                            }

                            list_anime_record.append(record)

                        break

                    if response.status_code in {429, 500, 502, 503, 504}:
                        wait_seconds = 5 * (attempt + 1)

                        print(
                            f"Page {page} returned {response.status_code}. "
                            f"Retrying in {wait_seconds} seconds..."
                        )

                        time.sleep(wait_seconds)
                        continue

                    print(f"Failed to get page {page}. Error: {response.status_code}")
                    break

                except requests.exceptions.RequestException as error:
                    wait_seconds = 5 * (attempt + 1)

                    print(
                        f"Request failed on page {page}: {error}. "
                        f"Retrying in {wait_seconds} seconds..."
                    )

                    time.sleep(wait_seconds)

            else:
                failed_pages.append(page)
                print(f"Could not collect page {page} after 3 attempts.")

            time.sleep(0.7)

    if failed_pages:
        raise RuntimeError(
            f"Failed pages: {failed_pages}. "
            "Existing CSV was not overwritten."
        )
    
    if not list_anime_record:
        raise RuntimeError(
        "No anime data was collected. Existing dataset was not overwritten."
        )
    
    df = pd.DataFrame(list_anime_record)
    df.to_csv(MY_ANIME_RAW_DATASET, index=False)
    print("Successfully saved data to 'my_anime_dataset.csv'!")

if __name__ == "__main__":
    collect_raw_anime_data(total_pages=400)
    


