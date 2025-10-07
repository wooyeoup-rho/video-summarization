from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key=os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("Missing OPENAI_API_KEY. Please set it in your environment or .env file.")

client = OpenAI(api_key=api_key)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TRANSCRIPT_FOLDER = os.path.join(DATA_DIR, "transcripts")

def transcribe_audio(audio_path):
    audio_file = open(audio_path, "rb")
    transcript = client.audio.transcriptions.create(
      model="whisper-1",
      file=audio_file
    )

    return transcript

def summarize_transcript(transcription):
    prompt = f"""You are a note-taking assistant that formats information into clean, structured, and Markdown-compatible notes for Notion.
    Your goal:
    - Analyze the following transcript.
    - Identify the key ideas, sections, and action points.
    - Rewrite the content as concise, organized notes.
    - Use clear Markdown formatting:
      - `#` for main titles
      - `##` for sections
      - `###` for subtopics
      - `-` for bullet points
      - `**bold**` for emphasis
      - `> Quote` for any direct quotes or key statements
    
    If the transcript is conversational (e.g., a meeting or discussion), summarize what each speaker said clearly and note any important decisions or takeaways.
    
    If the transcript is educational (e.g., a lecture or presentation), extract main concepts, examples, and supporting details.
    
    Do not include filler words or unnecessary repetition. Keep it concise but informative.
    
    ---
    
    Transcript:
    {transcription}
    """

    response = client.responses.create(
        model="gpt-5-mini",
        reasoning={"effort": "low"},
        input=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.output_text