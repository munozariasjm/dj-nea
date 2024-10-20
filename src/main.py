# main.py

import os
from core_logic import start_dj
from config import load_config

def main():
    """
    Main function to start the AI DJ experience.
    """
    config = load_config()

    # Display a welcome message
    print("🎶 Welcome to the AI DJ Experience! 🎶")
    print("Loading configurations...")

    # Check if required API keys are set
    if not config['openai_api_key']:
        print("Error: OpenAI API key is missing. Please set it in the environment variables.")
        return
    if not config['spotify_client_id'] or not config['spotify_client_secret']:
        print("Error: Spotify API keys are missing. Please set them in the environment variables.")
        return

    print("Configurations loaded successfully. Starting your DJ...")

    try:
        # Start the AI DJ with the given configuration
        start_dj(config)
    except KeyboardInterrupt:
        print("\nSession ended by user. Thank you for using the AI DJ!")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Goodbye and keep enjoying the music! 🎵")

if __name__ == "__main__":
    main()
