# core_logic.py

import threading
import time
import sys

from chatgpt_handler import NextSongsSuggester
from spotify_api import authenticate_spotify, play_song, pause_playback
from config import load_config

# For detecting key presses
try:
    import keyboard  # Requires 'keyboard' package
except ImportError:
    print("Please install the 'keyboard' package to run this script.")
    sys.exit(1)

def parse_song(song_str):
    """
    Parses a song string formatted as 'Song Title - Artist' and returns the title and artist.

    Args:
        song_str (str): The song string to parse.

    Returns:
        tuple: A tuple containing the song title and artist.
    """
    parts = song_str.split(' - ')
    if len(parts) == 2:
        song_title, artist = parts
    else:
        song_title = song_str
        artist = ''
    return song_title.strip(), artist.strip()

def generate_dj_response(user_input, openai_api_key):
    """
    Generates a DJ-like response using OpenAI's ChatGPT API.

    Args:
        user_input (str): The user's input.
        openai_api_key (str): The OpenAI API key.

    Returns:
        str: The DJ's response.
    """
    import openai
    openai.api_key = openai_api_key

    prompt = f"You are an AI DJ. The user said: '{user_input}'. Respond in a friendly, DJ-like manner."

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': prompt}]
    )

    dj_response = response['choices'][0]['message']['content']
    return dj_response.strip()

def key_listener(spotify, suggester, previous_songs, config):
    """
    Listens for the 'space' key to pause playback and receive new user instructions.

    Args:
        spotify (spotipy.Spotify): The authenticated Spotify client.
        suggester (NextSongsSuggester): The song suggestion engine.
        previous_songs (list): The list of previously played songs.
        config (dict): Configuration dictionary with API keys.
    """
    while True:
        try:
            if keyboard.is_pressed('space'):
                # Pause playback
                pause_playback(spotify)
                print("Playback paused. Listening for your instructions...")

                # Wait for 'space' to be released to avoid multiple triggers
                while keyboard.is_pressed('space'):
                    time.sleep(0.1)

                # Get user input
                user_input = input("You: ")

                # Generate DJ's response
                dj_response = generate_dj_response(user_input, config['openai_api_key'])
                print(f"DJ: {dj_response}")
                # Optionally, use TTS to speak the DJ's response
                # speak_text(dj_response)

                # Get new recommendations
                recommendations = suggester(
                    input_from_user=user_input,
                    prev_songs=previous_songs,
                )

                if not recommendations:
                    print("No recommendations were generated.")
                    continue

                # Play the next song
                current_song = recommendations.pop(0)
                song_title, artist = parse_song(current_song)
                play_song(spotify, song_title, artist)
                previous_songs.append(current_song)

            else:
                time.sleep(0.1)
        except Exception as e:
            print(f"An error occurred in key_listener: {e}")
            time.sleep(1)

def main():
    """
    The main function that initializes the application and starts the interaction loop.
    """
    config = load_config()

    # Authenticate with Spotify
    spotify = authenticate_spotify(config['spotify_client_id'], config['spotify_client_secret'])

    # Initialize NextSongsSuggester
    suggester = NextSongsSuggester(
        n_recommendations=5,
    )

    # Collect user information
    suggester.collect_user_info()

    # Initial song recommendations
    previous_songs = []
    user_input = ""

    recommendations = suggester(
        input_from_user=user_input,
        prev_songs=previous_songs,
    )

    if not recommendations:
        print("No recommendations were generated.")
        return

    # Play the first song
    current_song = recommendations.pop(0)
    song_title, artist = parse_song(current_song)
    play_song(spotify, song_title, artist)
    previous_songs.append(current_song)

    # Start key listener thread
    key_listener_thread = threading.Thread(target=key_listener, args=(spotify, suggester, previous_songs, config))
    key_listener_thread.daemon = True
    key_listener_thread.start()

    # Keep the main thread running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting program.")

if __name__ == "__main__":
    main()
