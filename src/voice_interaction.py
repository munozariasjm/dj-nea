import openai
from openai import OpenAI
import os
import tempfile
from gtts import gTTS
import playsound
from dotenv import load_dotenv

# Load environment variables
path = os.path.dirname(os.path.abspath(__file__))
path2secrets = os.path.join(path, "../secrets/.env")
load_dotenv(path2secrets)
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()


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


def listen_user(audio_file_path):
    """
    Records audio from the user's microphone and transcribes it using OpenAI's Whisper API.

    Args:
        audio_file_path (str): Path to the audio file to transcribe.

    Returns:
        str: The transcribed text from the user's speech.
    """
    try:
        # Open the audio file
        with open(audio_file_path, "rb") as audio_file:
            # Call OpenAI's Whisper API using the 'transcribe' method
            response = client.audio.transcriptions.create(
                model="whisper-1", file=audio_file
            )
        # Extract the transcribed text from the response
        transcribed_text = response.text.strip()
    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        transcribed_text = ""
    finally:
        # Clean up the temporary audio file if it exists
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)

    return transcribed_text
