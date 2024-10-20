# chatgpt_handler.py

from typing import Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage
from pydantic import BaseModel, Field


class SuggestedSong(BaseModel):
    song_name: str = Field(..., title="Song Name", description="The name of the song.")
    artist: Optional[str] = Field(None, title="Artist", description="The artist of the song.")


class NextSongsSuggester:
    """
    This class is responsible for suggesting the next songs to play based on the user's input,
    inferred mood, activity, and previous songs.
    """

    def __init__(
        self,
        n_recommendations: int = 5,
        past_played_songs_num: int = 10,
    ) -> None:
        """
        Initializes the NextSongsSuggester with the specified number of recommendations
        and the number of past played songs to consider.

        Args:
            n_recommendations (int): The number of song recommendations to provide.
            past_played_songs_num (int): The number of past songs to include in the context.
        """
        self.chat_model = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.8,
            max_tokens=500,
            frequency_penalty=0,
            presence_penalty=0,
            top_p=1.0,
        )
        self.mood_model = ChatOpenAI(
            model_name="gpt-3.5-turbo-16k",
            temperature=0.0,
            max_tokens=100,
        )
        self.user_description: str = ""
        self.activity: str = ""
        self.n_recommendations = n_recommendations
        self.past_played_songs_num = past_played_songs_num

    def collect_user_info(self) -> None:
        """
        Initiates a conversation with the user to collect information about their music taste
        and current activity. This information will be used to tailor song recommendations.
        """
        print("🎧 Hello! I'm your AI DJ. Let's get started.")

        # Ask the user for a description of their music taste
        user_input = input(
            "Tell me a bit about your music taste or favorite genres (or press Enter to skip): "
        )
        self.user_description = user_input.strip()

        # Ask the user about their current activity
        user_input = input(
            "What activity are you doing or plan to do while listening to music? (or press Enter to skip): "
        )
        self.activity = user_input.strip()

        print("Great! I'll tailor your music experience based on your input. 🎶")

    def infer_mood(self, user_input: str) -> str:
        """
        Infers the user's mood from their input using the GPT-3.5-turbo-16k model.

        Args:
            user_input (str): The user's input from which to infer mood.

        Returns:
            str: The inferred mood as a lowercase string.
        """
        prompt = (
            "Analyze the following text and determine the user's current mood or emotional state. "
            "Provide a one-word description of the mood, such as 'happy', 'sad', 'energetic', 'calm', etc. "
            "If the mood is not clear, respond with 'neutral'.\n\n"
            f"User input: '{user_input}'\n\nMood:"
        )
        response = self.mood_model.invoke([SystemMessage(content=prompt)]).content.strip().lower()

        # Ensure the response is a single word and sanitize if necessary
        mood = response.split()[0] if response else "neutral"
        return mood

    def build_prompt(
        self,
        input_from_user: str = "",
        prev_songs: Optional[List[str]] = None,
    ) -> str:
        """
        Builds the prompt to be sent to the ChatGPT model based on the collected user information,
        inferred mood, previous songs, and any new input from the user.

        Args:
            input_from_user (str): Additional input from the user during the session.
            prev_songs (List[str], optional): A list of previously played songs.

        Returns:
            str: The constructed prompt for the AI model.
        """
        mood = self.infer_mood(input_from_user)

        context = (
            "You are an AI DJ, the most advanced in the world. Your task is to suggest songs for the user to listen to next, "
            "based on their music taste, inferred mood, activity, and previous songs."
        )

        if self.user_description:
            context += (
                f"\n\nHere is a description of the user's music taste:\n{self.user_description}"
            )

        context += f"\n\nThe user's current mood is inferred to be: {mood}"

        if self.activity:
            context += f"\n\nThe user is currently doing or plans to do the following activity: {self.activity}"

        if prev_songs:
            context += "\n\nHere are the last few songs that the user has been listening to in this playlist:"
            recent_songs = prev_songs[-self.past_played_songs_num:]
            for song in recent_songs:
                context += f"\n- {song}"
        else:
            context += "\n\nThe user has not listened to any songs yet in this playlist."

        if input_from_user:
            context += f"\n\nThe user has provided the following input: '{input_from_user}'"

        context += f"\n\nBased on this information, suggest the next {self.n_recommendations} songs for the user."

        context += "\n\n**Instructions:**"
        context += (
            "\n- Only provide the song titles and artist names, in a comma-separated list like this: "
            "'Song Title - Artist, Song Title - Artist, ...'"
        )
        context += "\n- Ensure that the recommendations match the user's inferred mood, activity, and music taste."
        context += "\n- Do not include any songs that the user has already listened to in this playlist."
        context += "\n- Make sure that the songs exist and are spelled correctly."

        return context

    def extract_titles(self, response: str) -> List[str]:
        """
        Extracts song titles and artist names from the AI model's response.

        Args:
            response (str): The response string from the AI model.

        Returns:
            List[str]: A list of songs in the format 'Song Title - Artist'.
        """
        try:
            songs = [song.strip() for song in response.split(",")]
            return songs
        except Exception as e:
            print(f"Failed to parse response: {e}")
            return []

    def pipeline(
        self,
        input_from_user: str = "",
        prev_songs: Optional[List[str]] = None,
    ) -> List[str]:
        """
        The main pipeline that constructs the prompt, invokes the AI model, and returns song recommendations.

        Args:
            input_from_user (str): Input from the user during the session.
            prev_songs (List[str], optional): A list of previously played songs.

        Returns:
            List[str]: A list of recommended songs.
        """
        prompt = self.build_prompt(input_from_user, prev_songs)
        response = self.chat_model.invoke([SystemMessage(content=prompt)]).content
        recommended_songs = self.extract_titles(response)
        return recommended_songs

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Allows the instance to be called like a function.

        Returns:
            Any: The result of the pipeline method.
        """
        return self.pipeline(*args, **kwargs)
