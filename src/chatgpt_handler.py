from typing import Any, List
from langchain import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.prompts.few_shot import FewShotPromptTemplate


class NextSongsSuggester:
    """
    This class is responsible for taking the previosly played songs, mood,
    input from the user and suggest the next K songs to play.
    """

    def __init__(
        self,
        user_description: str = "",
        prev_songs: List[str] = [],
        mood="",
        input_from_user: str = "",
        n_recommendations: int = 5,
    ) -> None:
        self.model = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.8,
            max_tokens=2500,
            frequency_penalty=0,
            presence_penalty=0,
            top_p=1.0,
        )
        self.user_descriptions = user_description
        self.prev_songs = prev_songs
        self.mood = mood
        self.n_recommendations = n_recommendations
        self.mood = mood

        self.prompt = self.build_prompt()

    def build_prompt(self) -> str:
        context = "Assitant is the most advanced AI DJ in the world. With years of experience, I can suggest the best songs for you to listen to next."
        if self.user_descriptions:
            context += (
                "Your task is to build a perfect personalized playlist for a user. Here is a description of the user's music taste based on spotify:\n"
                + self.user_descriptions
                + "\n"
            )
        if self.mood:
            context += f"The user mood is to {self.mood}.\n"

        if self.prev_songs:
            context += "Here are the last few songs that the user has been listening to in this playlist:\n"
            for i, song in enumerate(self.prev_songs):
                context += f"- {song}\n"

        context += """Remeber I only need the titles and not other information.
            Here are some rules:
            - Your recommendations should take into account the users profile, as listed in their previous viewing history.
            - You should aim to provide a balanced set of recommendations that encompass a variety of genres and themes while also aligning with the user's interests.
            - Include a mix of popular and lesser-known titles. Also, please do not include any titles that the user has already watched.
            - Make sure that the titles exist and are spelled correctly. Give them to me as a comma-separated list, like this: title1, title2, title3, etc.
            """
        return context

    def pipeline(self) -> str:
        print("*" * 50)
        print("self.prompt", self.prompt)
        return self.model([SystemMessage(content=self.prompt)]).content

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.pipeline(*args, **kwds)
