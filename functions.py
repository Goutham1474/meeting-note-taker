import whisper
import warnings
import openai
import os

from dotenv import load_dotenv
load_dotenv()

client = openai.OpenAI(
    api_key=os.getenv("openai_key")
)

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

def get_transcript(audio_file):
    model = whisper.load_model("base")
    response = model.transcribe(audio_file)
    transcript = response['text'].strip()
    return transcript

def generate_notes(transcript):
    messages = [
        {"role": "system", "content": "You are a professional meeting note taker."},
        {"role": "user", "content": ( f"You specilize in writing notes for meetings. You are currently in a meeting with your team. The transcipt of the meeting is as follows: {transcript}. Write major bullet points highlighting the major points from the meeting in numbered bullet points." )}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# print(get_transcript("audio/sample_convo.wav"))
# print(generate_notes("We need to talk about the investors and the new project we are working on."))