Here's the refined and more professional version of the `README.md` file without emojis:

---

# DJ NEA - The AI DJ Experience

Welcome to **DJ NEA**, an interactive AI-based music recommendation system that dynamically curates Spotify playlists based on your mood, activities, and preferences. Developed during a high-intensity hackathon, this project leverages OpenAI's GPT models and Whisper for a conversational AI DJ experience, combined with Spotify's API for real-time music playback.

## Project Overview

DJ NEA was developed by **[Your Name]** and **[Collaborator's Name]** over the course of **5 hours** as part of a hackathon challenge. The goal was to create a proof-of-concept (PoC) for an AI-powered DJ that:

- Takes user input (mood, activities, preferences) through voice and text.
- Dynamically generates and modifies Spotify playlists based on real-time interactions.
- Allows users to pause the music and give new instructions to the AI DJ at any point.

## Features

- **Real-Time Music Recommendations:** Uses OpenAI's GPT-4 for generating song suggestions based on user input and inferred mood.
- **Voice Interaction with Whisper:** Utilizes OpenAI's Whisper for speech-to-text conversion, allowing users to interact with the AI DJ via voice commands.
- **Spotify Integration:** Uses the Spotify API to search for tracks, manage playback, and control the playlist directly from your terminal.
- **Dynamic Playlist Adjustments:** Users can change their mood or activity at any time, and DJ NEA will adapt the playlist on the fly.

## Installation

To get started with DJ NEA, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/munozariasjm/dj-nea.git
   cd dj-nea
   ```

2. **Set up a virtual environment (recommended):**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows, use `env\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Create a `.env` file inside the `secrets/` folder with your API keys:
     ```
     OPENAI_API_KEY=your_openai_api_key
     SPOTIFY_CLIENT_ID=your_spotify_client_id
     SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
     ```

5. **Run the AI DJ:**
   ```bash
   python main.py
   ```

## Usage

1. **Launch the DJ:**
   - Run the command `python main.py` to start the AI DJ experience.
   - The AI DJ will greet you and ask for your mood.

2. **Interact with the DJ:**
   - Provide your mood, such as "chill," "energetic," or "romantic."
   - The AI will curate a playlist based on your input and start playing songs via Spotify.

3. **Control the DJ:**
   - Press `Enter` at any time to pause the current song and give new instructions.
   - Speak your request (e.g., "Play something more upbeat").
   - The AI will adjust the playlist based on your latest input.

4. **End the Session:**
   - Type "quit" when you want to end the DJ session.

## Future Enhancements

The project was developed as a PoC within a time constraint of 5 hours. Here are some potential features for future development:

- **Biometric Data Integration:** Sync with biometric sensors (e.g., heart rate monitors or smartwatches) to automatically detect changes in the user's state (e.g., stress levels, physical activity) and adapt the playlist accordingly.
- **Real-Time OpenAI API Usage:** Enhance the real-time response capabilities by using OpenAI’s streaming API for faster and more interactive conversations.
- **Interactive GUI:** Create a user-friendly interface with interactive controls, visualizations of the playlist, and a seamless experience for adjusting the DJ's recommendations.
- **Enhanced Sentiment Analysis:** Improve mood detection by using a more sophisticated sentiment analysis model, taking into account the user's voice tone and context.
- **Social Features:** Allow users to share their curated playlists or interact with other AI DJs.
- **Multi-Device Playback:** Add support for selecting and controlling multiple playback devices, such as home speakers or car systems.

## Technologies Used

- **Python**: For the core logic and interactions between APIs.
- **OpenAI GPT-4 & Whisper**: For generating song suggestions and voice interactions.
- **Spotify API**: To control playback, search for songs, and manage playlists.
- **LangChain**: For managing GPT prompts and enhancing the conversational flow.
- **SoundDevice & NumPy**: For handling audio input during voice interactions.

## Acknowledgements

- Juan Sebastian Duitama
- Jose M Munoz

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
