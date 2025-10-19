from pymongo import MongoClient
from helper import get_native_language_name
import re
from datetime import datetime, timedelta
import dateutil.parser
import os

MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    # Fallback to the previous hard-coded URI for users who haven't set env var yet.
    MONGO_URI = "mongodb+srv://telexmovies:telex9949@streamripper.ks7lydv.mongodb.net/?retryWrites=true&w=majority&appName=Streamripper"

client = MongoClient(MONGO_URI)
db = client[os.environ.get("MONGO_DB", "streamripper")]
movies_collection = db[os.environ.get("MOVIES_COLLECTION", "movies")]
show_collection = db[os.environ.get("SHOWS_COLLECTION", "shows")]

# def get_all_movies():
#     return list(movies_collection.find({}, {
#         "_id": True, "title": 1, "year": 1, "images": 1, "description": 1, "genre": 1
#     }).sort("_id", -1).limit(10))

def get_all_movies():
    movies = list(movies_collection.find(
         {
            "imdb_rating": {"$ne": 10},           # imdb_rating NOT equal to 10
            "imdb_votes": {"$gt": 200}              # imdb_votes greater than 200
        },
        {"_id": True, "title": 1, "year": 1, "images": 1, "description": 1, "genre": 1, "imdb_rating": 1, "imdb_votes": 1}
    ).sort("imdb_rating", -1).limit(10))
    return movies  

def get_top_rated_movies():
        return list(movies_collection.find(
         {
            "imdb_rating": {"$ne": 10},           # imdb_rating NOT equal to 10
            "imdb_votes": {"$gt": 20}              # imdb_votes greater than 20
        },
        {"_id": True, "title": 1, "year": 1, "images": 1, "description": 1, "genre": 1, "imdb_rating": 1, "imdb_votes": 1}
    ).sort("imdb_rating", -1).limit(20))[::-1]

def get_movies_by_genre(genre: str):
    
    if genre.lower()  == "top rated":
        print(get_top_rated_movies())
        return get_top_rated_movies()
    
    if genre.lower() == "newly released":
        return get_new_releases()[::-1]

    query = {"genre": {"$elemMatch": {"$eq": genre}}}
    projection = {"_id": True, "title": 1, "year": 1, "images": 1, "duration": 1, "genre": 1, "rating": 1,"description": 1}
    return list(movies_collection.find(query, projection).limit(10))

def get_movie_by_id(movie_id: str):
    return movies_collection.find_one({"_id": movie_id})

def get_stream_info(movie_id: str):
    movie = movies_collection.find_one({"_id": movie_id})
    if not movie:
        return None
    return {
        "manifest": movie.get("mpd"),
        "keys": movie.get("keys"),
        "subtitles": movie.get("subtitle_url"),
        "title": movie.get("title"),
    }

def search_movies(query: str):
    # Clean and split the query into words
    words = re.findall(r'\w+', query)  # Extract words like ["Spider", "Man", "Homecoming"]
    data = []
    # Create regex patterns for each word (case-insensitive)
    regexes = [{"$regex": word, "$options": "i"} for word in words]

    # Match if all words are found in any of the fields
    search_criteria = {
        "$and": [
            {
                "$or": [
                    {"title": regex},
                    {"description": regex},
                    {"genre": regex}
                ]
            } for regex in regexes
        ]
    }

    projection = {
        "_id": True,
        "title": 1,
        "year": 1,
        "images": 1,
        "duration": 1,
        "genre": 1,
        "rating": 1,
        "description": 1,
        "total_seasons": 1
    }
    data.extend(list(movies_collection.find(search_criteria)))
    data.extend(list(show_collection.find(search_criteria)))
    return data

def get_movies_by_language(language: str, page=10):
        language = get_native_language_name(language)
        print(language)
        # query = {"languages": {"$eleMatch": {"$eq": language}}}
        query = {"languages": {"$elemMatch": {"$eq": language}} }
        projection = {"_id": True, "title": 1, "year": 1, "images": 1, "duration": 1, "genre": 1, "rating": 1,"description": 1}
        return list(movies_collection.find(query, projection).limit(page))
        
def paginate_movies(page: int, page_size: int, type :str, value: str, catalog: str):
    if type == "genre":
        query = {"genre": {"$elemMatch": {"$eq": value}}}
    elif type == "language":
        query = {"languages": {"$elemMatch": {"$eq": value}}}
    else:
        query = {}
 
    skip = (page - 1) * page_size
    if catalog == "shows":
        collection = show_collection
    else:
        collection = movies_collection
    movies = list(collection.find(query, {
       "_id": True, "title": 1, "year": 1, "images": 1, "duration": 1, "genre": 1, "rating": 1,"description": 1
    }).sort("_id", -1).skip(skip).limit(page_size))
    return movies

def get_all_shows():
    return list(show_collection.find({}, {
        "_id": True, "title": 1, "year": 1, "images": 1, "description": 1, "genre": 1,"episodes": 1
    }))[-10:]

def get_show_by_genre(genre: str):
    # Make sure 'genre' is a string and the query checks if it's in the genres array
    query = {"genre": {"$elemMatch": {"$eq": genre}}}
    projection = {"_id": True, "title": 1, "year": 1, "images": 1, "duration": 1, "genre": 1, "rating": 1,"description": 1}
    return list(show_collection.find(query, projection).sort("_id", -1).limit(10))

def get_show_by_id(show_id: str):
    return show_collection.find_one({"_id": show_id})

def get_episode_info(show_id: str,season_id: str, id: str):
    show = show_collection.find_one({"_id": show_id})
    if not show:
        return None
    for season in show.get("seasons", []):
        if season.get("_id") == season_id:
            for episode in season.get("episodes", []):
                if episode.get("_id") == id:
                    return {
                        "manifest": episode.get("mpd"),
                        "keys": episode.get("keys"),
                        "subtitles": episode.get("subtitle_url"),
                        "title": episode.get("title"),
                    }
    return None

# def get_top_rated_movies():
#     return list(movies_collection.find({}, {
#         "_id": True, "title": 1, "year": 1, "images": 1, "duration": 1, "genre": 1, "imdb_rating": 1,"description": 1
#     }).sort("imdb_rating", -1).limit(10))


def similar_movies(movie_id: str):
    movie = movies_collection.find_one({"_id": movie_id})
    if not movie:
        return None
    genre = movie.get("genre", [])[0]
    language = movie.get("languages", [])[0]
    query = {
        "genre": {"$elemMatch": {"$eq": genre}},
        "languages": {"$elemMatch": {"$eq": language}}
        }
    projection = {"_id": True, "title": 1, "year": 1, "images": 1, "duration": 1, "genre": 1, "rating": 1,"description": 1}
    return list(movies_collection.find(query, projection).limit(10))


def get_new_releases():
    all_movies = list(movies_collection.find(
        {}
    ))

    new_releases = []
    today = datetime.now()
    cutoff = today - timedelta(days=30)  # Change to your desired range

    for movie in all_movies:
        raw_date = movie.get("release_date")
        if not raw_date:
            continue

        try:
            # Handles both "February 28, 2025" and "2025-01-14"
            parsed_date = dateutil.parser.parse(raw_date)
            if parsed_date >= cutoff and parsed_date <= today:
                new_releases.append(movie)
        except Exception as e:
            print(f"Skipping invalid date '{raw_date}':", e)

    return new_releases