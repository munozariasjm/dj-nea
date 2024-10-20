import os
from core_logic import start_dj
from pathlib import Path
from dotenv import load_dotenv

# path to this folder
path = os.path.dirname(os.path.abspath(__file__))
print(path)
path2secrets = os.path.join(path, "../secrets/.env")
print(load_dotenv(path2secrets))


def main():
    """
    Main function to start the AI DJ experience.
    """
    # Display a welcome message
    print("🎶 Welcome to the AI DJ Experience! 🎶")
    print("Loading configurations...")

    # Check if required API keys are set
    if not os.getenv("OPENAI_API_KEY"):
        print(
            "Error: OpenAI API key is missing. Please set it in the environment variables."
        )
        return
    if not os.getenv("CLIENT_ID") or not os.getenv("CLIENT_SECRET"):
        print(
            "Error: Spotify API keys are missing. Please set them in the environment variables."
        )
        return

    print("Configurations loaded successfully. Starting your DJ...")

    try:
        # Start the AI DJ with the given configuration
        start_dj()
    except KeyboardInterrupt:
        print("\nSession ended by user. Thank you for using the AI DJ!")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Goodbye and keep enjoying the music! 🎵")


if __name__ == "__main__":
    main()
