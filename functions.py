import whisper
import warnings
import openai
import os
from pyannote.audio import Pipeline
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(
    api_key=os.getenv("openai_key")
)

os.environ["HF_TOKEN"] = os.getenv("hf_key")

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

def perform_diarization(audio_file):
    output_dir = "audio/speakers"
    os.makedirs(output_dir, exist_ok=True)
    
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=os.environ["HF_TOKEN"]
    )
    
    diarization = pipeline(audio_file)
    
    audio = AudioSegment.from_wav(audio_file)
    speaker_segments = {}
    
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        start = int(turn.start * 1000)
        end = int(turn.end * 1000)
        
        if speaker not in speaker_segments:
            speaker_segments[speaker] = []
        
        speaker_segments[speaker].append(audio[start:end])
    
    speaker_files = []
    for speaker, segments in speaker_segments.items():
        combined = sum(segments)
        output_file = f"{output_dir}/{speaker}.wav"
        combined.export(output_file, format="wav")
        speaker_files.append(output_file)
    
    return speaker_files

def get_transcript(audio_file):
    model = whisper.load_model("base")
    response = model.transcribe(audio_file)
    transcript = response['text'].strip()
    return transcript

def generate_notes(transcript):
    messages = [
        {"role": "system", "content": "You are a professional meeting note taker for candidate interviews."},
        {"role": "user", "content": ( f"""You specialize in writing notes for meetings and are currently in an interview from your team's side. Below is the transcript of the interview: {transcript}. Write major bullet points highlighting the key moments of the interview in the following format:
                                     
        Observations:
            Describe the candidate's overall behavior and performance during the interview in one 4 line paragraph.
        Strengths:
            Highlight any positive aspects of the candidate's interview performance.
        Weaknesses:
            Detail the areas where the candidate underperformed during the interview.
        Fit for the Role:
            Provide an overall assessment of the candidate’s suitability for the position based on their interview performance.
                                     
        If enough inforamtion cannot be gathered then add a line after each heading's summary that enough information cannot be gathered""" )}
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

def process_meeting_audio(audio_file):
    speaker_files = perform_diarization(audio_file)
    
    transcripts = {}
    for speaker_file in speaker_files:
        speaker = os.path.basename(speaker_file).split('.')[0]
        transcripts[speaker] = get_transcript(speaker_file)
    
    full_transcript = "\n\n".join([f"Speaker {speaker}:\n{transcript}" for speaker, transcript in transcripts.items()])
    
    notes = generate_notes(full_transcript)
    
    return full_transcript, notes

# full_transcript, notes = process_meeting_audio("audio/meeting_audio.wav")
# print(notes)
# print(generate_notes('sorry but im not a good candidate. ok you can leave the meeting'))