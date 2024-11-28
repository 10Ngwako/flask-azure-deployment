from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from textblob import TextBlob

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# TMDB API Configuration
TMDB_API_KEY = '1ef1ea6f866acc829f302ab64aa7c747'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

# Route for serving the landing page
@app.route('/')
def index():
    return render_template('land.html')

@app.route('/index')
def index_page():
    return render_template('index.html')




# Endpoint to fetch trending movies
@app.route('/trending', methods=['GET'])
def trending_movies():
    url = f"{TMDB_BASE_URL}/trending/movie/week"
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return jsonify(data)
    else:
        return jsonify({"error": "Failed to fetch trending movies"}), response.status_code


# Endpoint to search for movies based on user input
@app.route('/search', methods=['GET'])
def search_movies():
    query = request.args.get('query', '')
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "query": query,
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return jsonify(data)
    else:
        return jsonify({"error": "Failed to fetch search results"}), response.status_code


@app.route('/recommend-by-genre', methods=['GET'])
def recommend_by_genre():
    genre_id = request.args.get('genre_id')

    # Fetch movies based on genre
    url = f"{TMDB_BASE_URL}/discover/movie"
    params = {
        'api_key': TMDB_API_KEY,
        'with_genres': genre_id,
        'language': 'en-US',
        'sort_by': 'popularity.desc'
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Failed to fetch data from TMDB'}), response.status_code


# Map sentiment to genres
GENRE_MAPPING = {
    'positive': ['28', '12'],  # Action, Adventure
    'neutral': ['35', '10749'],  # Comedy, Romance
    'negative': ['9648', '53']  # Mystery, Thriller
}

# Endpoint for sentiment analysis and genre recommendations
@app.route('/analyze-mood', methods=['POST'])
def analyze_mood():
    user_input = request.json.get('mood', '')

    # Analyze sentiment using TextBlob
    sentiment_score = TextBlob(user_input).sentiment.polarity

    # Map sentiment to genres
    if sentiment_score > 0.3:
        sentiment = 'positive'
    elif sentiment_score < 0:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'

    genres = ','.join(GENRE_MAPPING[sentiment])

    # Fetch movies from TMDB based on genres
    url = f"{TMDB_BASE_URL}/discover/movie"
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US',
        'with_genres': genres,
        'sort_by': 'popularity.desc'
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Failed to fetch data from TMDB'}), response.status_code




if __name__ == '__main__':
    app.run(debug=True)