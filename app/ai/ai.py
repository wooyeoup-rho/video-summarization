from openai import OpenAI, OpenAIError
import os
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()
api_key=os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("Missing OPENAI_API_KEY. Please set it in your environment or .env file.")

client = OpenAI(api_key=api_key)

class AIServiceError(Exception):
    pass

def transcribe_audio(audio_path, ai_client=client, chunk_duration_ms=(2 * 60 * 1000), output_dir=None, max_file_size=(20*1000000)):
    try:
        file_size_bytes = os.path.getsize(audio_path)
    except OSError as e:
        raise AIServiceError(f"Could not access file: {e}") from e

    # If file size > 20MB, need to chunk it for openai
    if file_size_bytes > max_file_size:
        transcriptions = []

        try:
            chunks, output_dir = _split_audio(audio_path, chunk_duration_ms=chunk_duration_ms, output_dir=output_dir)
        except Exception as e:
            raise AIServiceError(f"Audio splitting failed: {e}")

        try:
            for i in range(len(chunks)):
                chunk_path = os.path.join(output_dir, f"chunk_{i}.mp3")
                with open(chunk_path, "rb") as f:
                    result = ai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=f
                    )
                    transcriptions.append(result.text)
            transcript = " ".join(transcriptions)
        except (OSError, OpenAIError) as e:
            raise AIServiceError(f"Transcription failed: {e}") from e
    else:
        try:
            with open(audio_path, "rb") as audio_file:
                result = ai_client.audio.transcriptions.create(
                  model="whisper-1",
                  file=audio_file
                )

            transcript = result.text
        except (OSError, OpenAIError) as e:
            raise AIServiceError(f"Transcription failed: {e}") from e

    return transcript

def _split_audio(audio_path, chunk_duration_ms, output_dir=None):
    audio = AudioSegment.from_file(audio_path)

    video_name = os.path.splitext(os.path.basename(audio_path))[0]
    output_dir = output_dir or f"data/audio/{video_name}"
    os.makedirs(output_dir, exist_ok=True)

    chunks = []

    for i in range(0, len(audio), chunk_duration_ms):
        chunk = audio[i:i + chunk_duration_ms]
        chunks.append(chunk)
        chunk.export(os.path.join(output_dir, f"chunk_{i//chunk_duration_ms}.mp3"),
                 format="mp3", bitrate="128k")

    return chunks, output_dir

def summarize_transcript(transcription, ai_client=client):
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
    try:
        response = ai_client.responses.create(
            model="gpt-5-mini",
            reasoning={"effort": "low"},
            input=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        if not hasattr(response, "output_text"):
            raise AIServiceError("Invalid response from AI service")

        return response.output_text
    except (OpenAIError, AttributeError) as e:
        raise AIServiceError(f"Summarization failed: {e}") from e