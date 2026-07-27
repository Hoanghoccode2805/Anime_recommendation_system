import requests
import pandas as pd
import time
from config import MY_ANIME_RAW_DATASET

def collect_raw_anime_data(total_pages = 400):
    # This empty list will temporarily hold our clean data rows
    list_anime_record = []
    for page in range(1,total_pages+1):
            print(f"Fetching data in page {page}")

            url = f"https://api.jikan.moe/v4/top/anime?page={page}"
            try: 
                response = requests.get(url, timeout = 30)
                if response.status_code == 200 :
                    data = response.json()
                    for anime in data['data']:
                        genres = [g['name'] for g in anime['genres']]
                        genres_str = ",".join(genres)

                        studios = ",".join(studio["name"] for studio in anime["studios"])
                        record = {
                            "anime_id" : anime["mal_id"],
                            "title" : anime["title"],

                            "score" : anime["score"],
                            "rank" : anime["rank"],
                            "popularity" : anime["popularity"],
                            "members" : anime["members"],
                            "favorites" : anime["favorites"],

                            "episodes" : anime["episodes"],
                            "type" : anime["type"],
                            "duration" : anime["duration"],
                            "status" : anime["status"],

                            "genres" : genres_str,
                            "studios" : studios
                        
                        }
                        list_anime_record.append(record)

                elif response.status_code == 429:
                    print("Rate limit reached. Waiting 5 seconds...")
                    time.sleep(5)
                    continue
                     
                else :
                    print(f"Failed to get data in page {page}. Error : {response.status_code}")

                time.sleep(0.7)

            except requests.exceptions.RequestException as error:
                print(f"Request failed on page {page}: {error}")
                time.sleep(5)
                continue
    

    df = pd.DataFrame(list_anime_record)
    df.to_csv(MY_ANIME_RAW_DATASET, index=False)
    print("Successfully saved data to 'my_anime_dataset.csv'!")

if __name__ == "__main__":
    collect_raw_anime_data(total_pages=400)
    


