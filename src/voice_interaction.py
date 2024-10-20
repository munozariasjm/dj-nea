import openai
import pyttsx3
import tempfile
import os
import threading

from gtts import gTTS
import os
import tempfile
import playsound


def speak_text(text):
    """
    Uses Google Text-to-Speech (gTTS) for more natural-sounding TTS.
    """
    try:
        tts = gTTS(text, lang="en")
        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as temp_audio_file:
            tts.save(temp_audio_file.name)
            playsound.playsound(temp_audio_file.name)
    except Exception as e:
        print(f"Error using gTTS: {e}")


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
