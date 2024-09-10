from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import uvicorn
from functions import generate_notes, get_transcript
from utils import record_meeting
import asyncio

app = FastAPI()

class MeetRequest(BaseModel):
    url: str
    duration: int

@app.post("/start-meeting-bot")
def make_notes(request: MeetRequest):
    
    meet_url = request.url
    duration = request.duration
    output_filename = "audio/meeting_audio.wav"

    asyncio.run(record_meeting(meet_url, duration, output_filename))
    transcript = get_transcript(output_filename)
    notes = generate_notes(transcript)
    return JSONResponse(content=notes)
    
if __name__ == "__main__":
    uvicorn.run("server:app", port=8080, reload=True)