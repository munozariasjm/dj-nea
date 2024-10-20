import threading
import time
import sys
import select
from chatgpt_handler import NextSongsSuggester
from spotify_api import SpotifyPlayer
from voice_interaction import speak_text, listen_user
import os
from dotenv import load_dotenv

import sounddevice as sd
import numpy as np
import wave

# Shared variables
recording = False
audio_frames = []
sample_rate = 44100
device_info = sd.query_devices(kind="input")
max_channels = device_info["max_input_channels"]
dtype = "int16"
filename = "output.wav"
lock = threading.Lock()
REDIRECT_URI = "http://localhost:8888/callback"

# Global flag for controlling the interaction loop
is_listening = False
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Initialize the SpotifyPlayer
player = SpotifyPlayer(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

# Get available devices and select one
devices = player.get_devices()
if devices:
    device_id = devices[0]["id"]  # Select the first available device
else:
    print("No devices available.")
    exit()

# Load environment variables
path = os.path.dirname(os.path.abspath(__file__))
path2secrets = os.path.join(path, "../secrets/.env")
path2user_settings = os.path.join(path, "../settings/user_settings.txt")
load_dotenv(path2secrets)


# Read user description from 'settings/user_settings'
def read_user_description():
    try:
        with open(path2user_settings, "r", encoding="utf-8") as f:
            user_description = f.read().strip()
            return user_description
    except FileNotFoundError:
        print(f"User settings file not found at {path2user_settings}.")
        return ""
    except Exception as e:
        print(f"Error reading user settings: {e}")
        return ""


def audio_callback(indata, frames, time, status):
    """This callback function is called for each audio block."""
    with lock:
        audio_frames.append(indata.copy())


def start_recording():
    """Starts recording audio."""
    global recording
    recording = True
    player.pause(device_id=device_id)
    print("Recording started. Press Enter to stop.")
    with sd.InputStream(
        samplerate=sample_rate,
        channels=max_channels,
        dtype=dtype,
        callback=audio_callback,
    ):
        while recording:
            sd.sleep(100)


def stop_recording():
    """Stops recording audio and saves the file."""
    global recording
    recording = False
    save_audio()
    print(f"Recording stopped. Audio saved to {filename}")


def save_audio():
    """Saves the recorded audio to a WAV file."""
    with lock:
        if audio_frames:
            np_frames = np.concatenate(audio_frames)
            with wave.open(filename, "wb") as wf:
                wf.setnchannels(max_channels)
                wf.setsampwidth(np.dtype(dtype).itemsize)
                wf.setframerate(sample_rate)
                wf.writeframes(np_frames.tobytes())
        else:
            print("No audio frames recorded.")


def user_interaction_thread(suggester):
    """
    Handles user interactions, such as pausing the song and listening for voice prompts.
    """
    global is_listening
    previous_songs = []
    current_song = None

    # Read user description from file and set it in the suggester
    user_description = read_user_description()
    suggester.user_description = user_description

    # Collect user mood (now only asks for mood)
    suggester.collect_user_info()

    # Provide a personalized greeting
    if suggester.user_description:
        speak_text(
            f"Hey there! Based on your music taste from spotify, I see what you enjoy. Let's get started!"
        )
    else:
        speak_text("Hey there! I'm excited to build a playlist just for you!")

    # Add a personalized DJ introduction
    speak_text("Alright, DJ NEA is crafting a playlist just for you. Enjoy!")

    # Get initial song recommendations
    recommendations = suggester.pipeline(prev_songs=previous_songs)
    if recommendations:
        for recommendation in recommendations:
            try:
                current_song = recommendation
                previous_songs.append(current_song)
                if len(previous_songs) > suggester.past_played_songs_num:
                    previous_songs.pop(0)

                # Announce and play the new song
                speak_text(f"Got it! Now playing {current_song}. Hope you enjoy it!")
                song_artist = (
                    current_song.replace('"', "").replace("'", "").split(" - ")
                )
                print(song_artist)
                player.play_song([song_artist], device_id)
                break
            except Exception as e:
                print(
                    f"An error occurred while finding the song: {recommendation}, {e}"
                )
                speak_text(f"Sorry, I couldn't find the song. Let's try another.")
    print("🎧 Your AI DJ is ready and waiting for your commands...")

    while True:
        input("Press Enter to start recording.")
        # Start the recording in a separate thread
        recording_thread = threading.Thread(
            target=start_recording,
        )
        recording_thread.start()
        # Wait for user input to stop recording
        input()
        stop_recording()
        # Wait for the recording thread to finish
        recording_thread.join()
        # Use Whisper for voice input processing
        user_input = listen_user(filename)
        if user_input:
            is_listening = True

            if user_input.lower() == "quit":
                speak_text(
                    "Goodbye! Thanks for listening with DJ NEA! Catch you next time!"
                )
                print("Goodbye! Thanks for listening with your AI DJ!")
                break

            # Get updated song recommendations based on user input and past songs
            recommendations = suggester(
                input_from_user=user_input, prev_songs=previous_songs
            )

            if recommendations:
                for recommendation in recommendations:
                    try:
                        current_song = recommendation
                        previous_songs.append(current_song)
                        if len(previous_songs) > suggester.past_played_songs_num:
                            previous_songs.pop(0)

                        # Announce and play the new song
                        speak_text(
                            f"Got it! Now playing {current_song}. Hope you enjoy it!"
                        )
                        song_artist = current_song.split(" - ")
                        player.play_song([song_artist], device_id)
                        break
                    except Exception as e:
                        print(
                            f"An error occurred while finding the song: {recommendation}"
                        )
                        speak_text(
                            f"Sorry, I couldn't find the song {recommendation}. Let's try another."
                        )

            is_listening = False

        time.sleep(0.1)  # Small delay to avoid busy-waiting


def start_dj():
    """
    Entry point for starting the AI DJ in the terminal.
    """
    suggester = NextSongsSuggester(n_recommendations=5, past_played_songs_num=10)

    interaction_thread = threading.Thread(
        target=user_interaction_thread, args=(suggester,), daemon=True
    )
    interaction_thread.start()

    print(
        "🎧 Your AI DJ is ready and waiting for your commands... Type your requests or 'quit' to exit."
    )
    interaction_thread.join()

    print("DJ session has ended. Goodbye!")
