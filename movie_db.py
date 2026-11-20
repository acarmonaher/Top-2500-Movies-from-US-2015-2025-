###########################################################
##### Codi obtingut mijtançant IA Generativa (Gemini) #####
###########################################################

####################################################################
# Aquest codi recull les 2500 pelicules amb més recaptació de TMDB #
####################################################################

import requests
import pandas as pd
import time

API_KEY = "f213db530c2ec2a5b10ac3db88511902"
BASE_URL = "https://api.themoviedb.org/3"

movies_data = []

TOTAL_PAGES = 200

with requests.Session() as session:
    session.params = {"api_key": API_KEY}

    for page in range(1, TOTAL_PAGES + 1):
        discover_url = f"{BASE_URL}/discover/movie"
        params = {
            "primary_release_date.gte": "2015-01-01",
            "primary_release_date.lte": "2025-12-31",
            "with_origin_country": "US",   # Només produccions dels EUA
            "sort_by": "revenue.desc",     # Més proper al pressupost que l'API permet
            "page": page
        }
        
        try:
            resp = session.get(discover_url, params=params, timeout=10)
            resp.raise_for_status()
            results = resp.json().get("results", [])
        except requests.RequestException as e:
            print(f"Error on page {page}: {e}")
            continue
        
        for item in results:
            movie_id = item["id"]
            detail_url = f"{BASE_URL}/movie/{movie_id}"
            
            try:
                detail_resp = session.get(detail_url, timeout=10)
                detail_resp.raise_for_status()
                details = detail_resp.json()
                
                budget = details.get("budget", 0)
                
                # Ignorem pel·lícules sense pressupost registrat (budget == 0)
                if budget > 0:
                    movies_data.append({
                        "id": details.get("id"),
                        "title": details.get("title"),
                        "original_title": details.get("original_title"),
                        "release_date": details.get("release_date"),
                        "origin_country": ", ".join(details.get("origin_country", [])),
                        "original_language": details.get("original_language"),
                        "runtime": details.get("runtime"),
                        "budget": budget,
                        "revenue": details.get("revenue"),
                        "vote_average": details.get("vote_average"),
                        "vote_count": details.get("vote_count"),
                        "popularity": details.get("popularity"),
                        "genres": ", ".join(g["name"] for g in details.get("genres", []))
                    })
            except requests.RequestException as e:
                print(f"Error on movie {movie_id}: {e}")
            
            time.sleep(0.03)
            
        if page % 10 == 0:
            print(f"Processed {page}/{TOTAL_PAGES} pages ({len(movies_data)} movies with budget found)...")

# Creem el DataFrame, eliminem possibles duplicats i ordenem pel pressupost real
df = pd.DataFrame(movies_data)
df = df.drop_duplicates(subset=["id"])
df = df.sort_values(by="budget", ascending=False).head(2500)

df.to_csv("top_2500_us_budget_2015_2025.csv", index=False, encoding="utf-8-sig")
print(f"Saved top {len(df)} US movies by budget.")