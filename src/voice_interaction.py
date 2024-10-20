# voice_interaction.py

import openai
import pyttsx3
import tempfile
import os
import threading


def speak_text(text):
    """
    Converts text to speech and plays it aloud.

    Args:
        text (str): The text to be spoken.
    """
    engine = pyttsx3.init()
    # Optionally, set properties like voice, rate, and volume
    engine.setProperty("rate", 150)  # Adjust the speech rate
    engine.setProperty("volume", 1.0)  # Set volume between 0 and 1

    # Run the text-to-speech conversion in a separate thread to prevent blocking
    def run_speech():
        engine.say(text)
        engine.runAndWait()

    threading.Thread(target=run_speech).start()


def listen_user(openai_api_key):
    """
    Records audio from the user's microphone and transcribes it using OpenAI's Whisper API.

    Args:
        openai_api_key (str): The OpenAI API key for authentication.

    Returns:
        str: The transcribed text from the user's speech.
    """
    import sounddevice as sd
    from scipy.io.wavfile import write

    fs = 16000  # Sample rate
    duration = 5  # Duration of recording in seconds

    print("🎤 Listening... Please speak now.")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()  # Wait until recording is finished
    print("Finished recording. Transcribing...")

    # Save the recording to a temporary WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
        write(temp_audio_file.name, fs, recording)
        temp_audio_file_path = temp_audio_file.name

    # Transcribe the audio file using OpenAI's Whisper API
    try:
        with open(temp_audio_file_path, "rb") as audio_file:
            response = openai.Audio.transcribe(
                "whisper-1", audio_file, api_key=openai_api_key
            )
        transcribed_text = response["text"].strip()
    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        transcribed_text = ""
    finally:
        # Clean up the temporary audio file
        os.remove(temp_audio_file_path)

    return transcribed_text
