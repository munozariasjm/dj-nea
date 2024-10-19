import os

def load_config():
    return {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "spotify_client_id": os.getenv("SPOTIFY_CLIENT_ID"),
        "spotify_client_secret": os.getenv("SPOTIFY_CLIENT_SECRET")
    }
