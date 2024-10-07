import whisper
import warnings
import openai
import os
import json
from pyannote.audio import Pipeline
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(
    api_key=os.getenv("openai_key")
)

# os.environ["HF_TOKEN"] = os.getenv("hf_key")

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def convert_to_json(input_string):
    # Clean up any unwanted spaces or characters
    input_string = input_string.strip()

    try:
        json_data = json.loads(input_string)
        return json_data
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

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
        {"role": "user", "content": ( f"""You specialize in writing notes for meetings and are currently in an interview from your team's side. Below is the transcript of the interview: {transcript}. 
            
            Start with an overall summary which tells how did the candidate perform on the basis of the provided observations. Summarize the overall observation of the interview of the candidate in a detailed and interactive manner. Consider all the questions asked, the interview summary, and the intent behind each question. Provide a comprehensive assessment by highlighting the candidate's strength. Take into account all the questions asked, the interview summary, and the intent behind each question. Generate the response in the form of a list ONLY. If no strengths found, give "No perticular strengths found" in the list. Highlight the candidate's weaknesses as observed during the interview. Consider all the questions asked, the interview summary, and the intent behind each question. Generate the response in the form of a list ONLY. If no weaknesses found, give "No perticular weaknesses found" in the list. Assess the candidate's fit for the role. Consider their responses, the overall interview summary, and the intent behind each question. Even if the questions are skipped most of the times, ALWAYS provide the intents json in the output       
            Format of output json: {{"Overall_Observation": <Overall Obsevation>, "Strengths": [<Strength1>, <Strength2>, ...], "Weaknesses": [<Weakness1>, <Weakness2>, ...], "Fit for the role": <Fit for the role>, "intents":  {{"<intent 1>": "<overall summary for intent 1>", "<intent 2>": "<overall summary for intent 2>"...}}}}

            Note: It is a MUST for all fields to be present in the output. AND THE JSON OUTPUT SHOULD BE A SINGLE LINE JSON WITH NO LINE SPACES AND LINE CHANGES.""" )}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.3
        )
        summary = response.choices[0].message.content
        summary = convert_to_json(summary)
        with open('response.json', 'w', encoding='utf-8') as f:
             f.write(json.dumps(summary, indent=4))
        return summary

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
# tra = get_transcript('audio/meeting_audio.wav')
# print(generate_notes(''))