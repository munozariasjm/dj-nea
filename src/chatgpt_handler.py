from typing import Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage
from pydantic import BaseModel, Field


class SuggestedSong(BaseModel):
    song_name: str = Field(..., title="Song Name", description="The name of the song.")
    artist: Optional[str] = Field(
        None, title="Artist", description="The artist of the song."
    )


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
        self.mood: str = ""
        self.n_recommendations = n_recommendations
        self.past_played_songs_num = past_played_songs_num

    def collect_user_info(self) -> None:
        """
        Collects information about the user's current mood.
        """
        print("🎧 Hello! I'm your AI DJ. Let's get started.")

        # Ask the user about their current mood
        user_input = input("How are you feeling today? (e.g., happy, sad, energetic): ")
        self.mood = user_input.strip().lower()

        print("Great! I'll tailor your music experience based on your mood. 🎶")

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
        response = (
            self.mood_model.invoke([SystemMessage(content=prompt)])
            .content.strip()
            .lower()
        )

        # Ensure the response is a single word and sanitize if necessary
        mood = response.split()[0] if response else "neutral"
        return mood

    def build_prompt(
        self,
        input_from_user: str = "",
        prev_songs: Optional[List[str]] = None,
    ) -> str:
        """
        Builds the prompt to be sent to the ChatGPT model based on collected user information.

        Args:
            input_from_user (str): Additional input from the user during the session.
            prev_songs (List[str], optional): A list of previously played songs.

        Returns:
            str: The constructed prompt for the AI model.
        """
        context = (
            "You are an AI DJ, the most advanced in the world. Your task is to suggest songs for the user to listen to next, "
            "based on their music taste, mood, activity, and previous songs."
        )

        if self.user_description:
            context += f"\n\nHere is a description of the user's music taste:\n{self.user_description}"

        if self.mood:
            context += f"\n\nThe user's current mood is: {self.mood}"

        if prev_songs:
            context += "\n\nHere are the last few songs that the user has been listening to in this playlist:"
            recent_songs = prev_songs[-self.past_played_songs_num :]
            for song in recent_songs:
                context += f"\n- {song}"
        else:
            context += (
                "\n\nThe user has not listened to any songs yet in this playlist."
            )

        if input_from_user:
            context += (
                f"\n\nThe user has provided the following input: '{input_from_user}'"
            )

        context += f"\n\nBased on this information, suggest the next {self.n_recommendations} songs for the user."

        context += "\n\n**Instructions:**"
        context += (
            "\n- Only provide the song titles and artist names, in a comma-separated list like this: "
            "'Song Title - Artist, Song Title - Artist, ...'"
        )
        context += "\n- Ensure that the recommendations match the user's mood, activity, and music taste."
        context += "\n- If there is no specific input/information, you can provide general recommendations (and) you think the user will enjoy based on his description."
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
