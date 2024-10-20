import threading
import time
import sys
import select
from chatgpt_handler import NextSongsSuggester
from spotify_api import SpotifyPlayer  # Assumed function for playing a song
from voice_interaction import speak_text
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

# Global flag for controlling the interaction loop
is_listening = False


def timed_input(prompt, timeout=10):
    """
    Custom function to wait for user input with a timeout.
    If no input is received within the timeout, returns None.
    """
    print(prompt, end=": ", flush=True)
    inputs, _, _ = select.select([sys.stdin], [], [], timeout)
    if inputs:
        return sys.stdin.readline().strip()
    return None


def user_interaction_thread(suggester):
    """
    Handles user interactions, such as pausing the song and listening for voice prompts.
    """
    global is_listening
    previous_songs = []
    current_song = None

    # Initialize the SpotifyPlayer
    player = SpotifyPlayer(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

    # Get available devices and select one
    devices = player.get_devices()
    if devices:
        device_id = devices[0]["id"]  # Select the first available device
    else:
        print("No devices available.")
        exit()

    suggester.collect_user_info()

    # Get initial song recommendations
    recommendations = suggester.pipeline(prev_songs=previous_songs)
    print(recommendations)
    if recommendations:
        current_song = recommendations[0]
        speak_text(f"Playing {current_song}")
        song_artist = current_song.split(" - ")
        player.play_song(song_artist, device_id)  # Play the first song

    while True:
        # Check for user input with a 10-second timeout
        user_input = timed_input("\n🎤 Speak now or type your request", timeout=0.5)
        if user_input:
            is_listening = True

            if user_input.lower() == "quit":
                print("Goodbye! Thanks for listening with your AI DJ!")
                break

            # Get updated song recommendations based on user input and past songs
            recommendations = suggester(
                input_from_user=user_input, prev_songs=previous_songs
            )

            if recommendations:
                current_song = recommendations[0]

                previous_songs.append(current_song)
                if len(previous_songs) > suggester.past_played_songs_num:
                    previous_songs.pop(0)

                # Announce and play the new song
                speak_text(f"Playing {current_song}")
                song_artist = current_song.split(" - ")
                player.play_song(song_artist, device_id)

            is_listening = False

        time.sleep(0.1)  # Small delay to avoid busy-waiting


def start_dj():
    """
    Entry point for starting the AI DJ in the terminal.
    """
    suggester = NextSongsSuggester(n_recommendations=5, past_played_songs_num=10)

    interaction_thread = threading.Thread(
        target=user_interaction_thread, args=([suggester]), daemon=True
    )
    interaction_thread.start()

    print(
        "🎧 Your AI DJ is ready and waiting for your commands... Type your requests or 'quit' to exit."
    )
    interaction_thread.join()

    print("DJ session has ended. Goodbye!")
