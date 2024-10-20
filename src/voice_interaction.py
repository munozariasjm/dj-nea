import openai
from config import OPENAI_KEY
 
openai.api_key = OPENAI_KEY

def transcribe_audio(file_path):
    # Open the audio file in binary mode
    with open(file_path, 'rb') as audio_file:
        # Use the Whisper API to transcribe the audio
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript['text']

def analyze_mood(text):
    # Use OpenAI's language model to analyze the mood
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant that identifies the speaker's mood in one word."},
            {"role": "user", "content": f"Analyze the following text and provide a one-word description of the speaker's mood:\n\n{text}\n\nMood:"}
        ],
        max_tokens=1,
        temperature=0.0,
    )
    mood = response['choices'][0]['message']['content'].strip()
    return mood

def get_text_instruction_and_mood(audio_file_path):
    # Transcribe the audio to text
    text = transcribe_audio(audio_file_path)
    print("Transcribed Text:\n", text)
    
    # Analyze the mood of the text
    mood = analyze_mood(text)
    print("Detected Mood:", mood)
    return text, mood



if __name__ == "__main__":
    main()