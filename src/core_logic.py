import threading
import time
import sys
import select
from chatgpt_handler import NextSongsSuggester
from spotify_api import SpotifyPlayer  # Assumed function for playing a song
from voice_interaction import speak_text, listen_user
import os
from dotenv import load_dotenv

import sounddevice as sd
import numpy as np
import wave
import threading

# Shared variables
recording = False
audio_frames = []
sample_rate = 44100
device_info = sd.query_devices(kind="input")
max_channels = device_info["max_input_channels"]
dtype = "int16"
filename = "output.wav"
lock = threading.Lock()


def audio_callback(indata, frames, time, status):
    """This callback function is called for each audio block."""
    with lock:
        audio_frames.append(indata.copy())


def start_recording():
    """Starts recording audio."""
    global recording
    recording = True
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


# Load environment variables
path = os.path.dirname(os.path.abspath(__file__))
path2secrets = os.path.join(path, "../secrets/.env")
load_dotenv(path2secrets)

REDIRECT_URI = "http://localhost:8888/callback"

# Global flag for controlling the interaction loop
is_listening = False
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


def timed_input(prompt, timeout=10):
    """
    Custom function to wait for user input with a timeout.
    If no input is received within the timeout, returns None.
    """
    print(prompt, end="", flush=True)
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

    # Collect user information and give a personalized greeting
    suggester.collect_user_info()
    if suggester.user_description:
        speak_text(
            f"Hey there! Based on your love for {suggester.user_description}, I'm sure we'll have a great time!"
        )
    else:
        speak_text("Hey there! I'm excited to build a playlist just for you!")

    # Add a personalized DJ introduction
    speak_text(
        "Okay... DJ NEA is building this playlist for you. Sit back, relax, and enjoy!"
    )

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
                song_artist = [current_song.split(" - ")]
                player.play_song(song_artist, device_id)
                break
            except Exception as e:
                print(f"An error occurred while finding the song: {recommendation}")
                speak_text(
                    f"Sorry, I couldn't find the song {recommendation}. Let's try another."
                )

    print("🎧 Your AI DJ is ready and waiting for your commands...")

    while True:
        input("Press Enter to start recording.")
        # Start the recording in a separate thread
        recording_thread = threading.Thread(target=start_recording)
        recording_thread.start()
        # Wait for user input to stop recording
        input()
        stop_recording()
        # Wait for the recording thread to finish
        recording_thread.join()
        # Check for user input with a 10-second timeout
        # user_input = timed_input(
        #     "Press 'space' for a request or type 'quit' to exit", timeout=10.0
        # )
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
                        song_artist = [current_song.split(" - ")]
                        player.play_song(song_artist, device_id)
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
