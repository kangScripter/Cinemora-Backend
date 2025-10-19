from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from db import get_all_movies, get_movies_by_genre, get_movie_by_id, get_stream_info, search_movies,get_movies_by_language, paginate_movies, \
    get_all_shows , get_show_by_genre, get_show_by_id, get_episode_info, \
    movies_collection, show_collection, similar_movies
from mangum import Mangum
import json
from datetime import datetime, timedelta, timezone
import urllib.parse

app = FastAPI()

@app.get("/movies")
def list_all_movies():
    movies = get_all_movies()
    return {"movies": movies}

@app.get("/movies/genre/{genre}")
def movies_by_genre(genre: str):
    movies = get_movies_by_genre(genre.capitalize())
    return {"genre": genre, "movies": movies}

@app.get("/movies/language/{language}")
def movies_by_language(language: str):
    movies = get_movies_by_language(language.capitalize())
    if not movies:
        raise HTTPException(status_code=404, detail="No movies found")
    return {"language": language, "movies": movies}

@app.get("/movies/{movie_id}")
def get_movie_metadata(movie_id: str):
    movie = get_movie_by_id(movie_id)
    similarmovies = similar_movies(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"movie": movie, "similar_movies": similarmovies}

@app.get("/movies/{movie_id}/stream")
def get_streaming_info(movie_id: str):
    stream = get_stream_info(movie_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream info not found")
    return {"stream": stream}

@app.get("/search")
def search_movie(query: str):
    query = urllib.parse.unquote(query)
    movies = search_movies(query)
    if not movies:
        raise HTTPException(status_code=404, detail="No movies found")
    return {"movies": movies}

@app.get("/page/next")
def get_next_movies(page: int, type: str, value: str,catalog:str):
    page_size = 20
    print(page, type, value)
    movies = paginate_movies(page, page_size, type, value, catalog)
    if not movies:
        raise HTTPException(status_code=404, detail="No movies found for the query")
    return {"movies": movies}

## SHOW APIs 
@app.get("/shows")
def list_all_shows():
    shows = get_all_shows()
    return {"shows": shows}
    
@app.get("/shows/genre/{genre}")
def shows_by_genre(genre: str):
    shows = get_show_by_genre(genre.capitalize())
    return {"genre": genre, "shows": shows}

# if not shows:
    #     raise HTTPException(status_code=404, detail="No shows found")
    # return {"genre": genre, "shows": shows}

@app.get("/shows/{show_id}")
def get_show_metadata(show_id: str):
    show = get_show_by_id(show_id)
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")
    return {"show": show}

@app.get("/stream/{show_id}/{season_id}/{episode_id}")
def get_episode_metadata(show_id: str, episode_id: str, season_id: str):
    episode = get_episode_info(show_id,season_id, episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return {"stream": episode}

def generate_sitemap(urls):
    """ Generate the full sitemap XML from the list of URLs. """
    body = "\n".join([
        f"""  <url>
    <loc>{url['loc']}</loc>
    <lastmod>{url['lastmod']}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""" for url in urls
    ])

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{body}
</urlset>"""

def valid_date(date):
    TIMEZONE_OFFSET = timezone(timedelta(hours=1)) 
    """ Ensure the date is in the correct ISO 8601 format with timezone offset, without microseconds. """
    if isinstance(date, datetime):
        # Use the datetime directly and ensure it's in the right timezone offset
        localized_date = date.astimezone(TIMEZONE_OFFSET).replace(microsecond=0)  # Remove microseconds
        return localized_date.isoformat()  # Outputs in the correct timezone format
    elif date:  # if date is not None or empty string
        try:
            # Ensure we properly parse string to datetime
            parsed_date = datetime.fromisoformat(date)
            # Convert to a specific timezone (e.g., UTC+1)
            localized_date = parsed_date.astimezone(TIMEZONE_OFFSET).replace(microsecond=0)  # Remove microseconds
            return localized_date.isoformat()
        except ValueError:
            print(f"Invalid date format: {date}, using current date.")
            # Use current time in the same timezone
            return datetime.now(TIMEZONE_OFFSET).replace(microsecond=0).isoformat()  # Adjust as needed
    else:
        # If date is missing, default to current time in the specified timezone
        return datetime.now(TIMEZONE_OFFSET).replace(microsecond=0).isoformat()  # Adjust as needed

@app.get("/sitemap.xml")
def get_sitemap():
    DOMAIN = "https://cinemora.in"
    TIMEZONE_OFFSET = timezone(timedelta(hours=1)) 
    # Get the current date/time in UTC+1 (or adjust to other offsets)
    now = datetime.now(TIMEZONE_OFFSET).isoformat()

    # Static pages (ensure the 'lastmod' is valid)
    static_urls = [
        {"loc": f"{DOMAIN}/", "lastmod": valid_date(None)},
        {"loc": f"{DOMAIN}/movies", "lastmod": valid_date(None)},
        {"loc": f"{DOMAIN}/shows", "lastmod": valid_date(None)},
    ]

    # Dynamic movies
    movies = movies_collection.find()
    movie_urls = [
        {"loc": f"{DOMAIN}/movies/{m.get('_id')}", "lastmod": valid_date(m.get("updatedAt"))}
        for m in movies
    ]

    # Dynamic shows
    shows = show_collection.find()
    show_urls = [
        {"loc": f"{DOMAIN}/shows/{s.get('_id')}", "lastmod": valid_date(s.get("updatedAt"))}
        for s in shows
    ]

    # Combine all URLs
    urls = static_urls + movie_urls + show_urls

    # Build XML
    xml_content = generate_sitemap(urls)
    return Response(content=xml_content, media_type="application/xml")

@app.get('/landingpage')
def get_landing_page():
    movies = get_all_movies()
    shows = get_all_shows()
    return {"movies": movies, "shows": shows}

handler = Mangum(app)
