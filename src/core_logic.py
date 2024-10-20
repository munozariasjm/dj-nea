import threading
import time
import keyboard
from chatgpt_handler import NextSongsSuggester
from spotify_api import authenticate_spotify, play_spotify_song  # Assumed function for playing a song
from voice_interaction import speak_text

# Global flag for controlling the interaction loop
is_listening = False

def user_interaction_thread(suggester, spotify, config):
    """
    Handles user interactions, such as pausing the song and listening for voice prompts.
    """
    global is_listening
    previous_songs = []
    current_song = None

    suggester.collect_user_info()

    recommendations = suggester.pipeline(prev_songs=previous_songs)
    if recommendations:
        current_song = recommendations[0]  # Get the first recommended song
        speak_text(f"Playing {current_song}")
        play_spotify_song(spotify, current_song)  # Play the first song

    while True:
        if keyboard.read_key() == "space":
            is_listening = True
            print("\n🎤 Speak now or type your request:")

            user_input = input("Your input: ").strip()

            if user_input.lower() == "quit":
                print("Goodbye! Thanks for listening with your AI DJ!")
                break

            recommendations = suggester(
                input_from_user=user_input,
                prev_songs=previous_songs
            )

            if recommendations:
                current_song = recommendations[0]

                previous_songs.append(current_song)
                if len(previous_songs) > suggester.past_played_songs_num:
                    previous_songs.pop(0)

                # Announce and play the new song
                speak_text(f"Playing {current_song}")
                play_spotify_song(spotify, current_song)

            is_listening = False
        time.sleep(0.1)  # Small delay to avoid busy-waiting

def play_song_thread(spotify, song_title, artist):
    """
    This thread plays the current song while allowing user interaction in the background.
    """
    play_spotify_song(spotify, song_title, artist)

def start_dj(config):
    """
    Entry point for starting the AI DJ in the terminal.
    """
    suggester = NextSongsSuggester(
        n_recommendations=5,
        past_played_songs_num=10
    )
    spotify = authenticate_spotify(
        config['spotify_client_id'],
        config['spotify_client_secret']
    )

    interaction_thread = threading.Thread(
        target=user_interaction_thread,
        args=(suggester, spotify, config),
        daemon=True
    )
    interaction_thread.start()

    print("🎧 Your AI DJ is ready and waiting for your commands... Press 'space' to interact.")
    interaction_thread.join()

    print("DJ session has ended. Goodbye!")

