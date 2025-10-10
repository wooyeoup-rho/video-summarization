import pytest
from pydub.generators import Sine
import app.ai.ai as ai
from app.ai.ai import AIServiceError, transcribe_audio, summarize_transcript

# Mock Openai client to handle both calls
class MockClient:
    class audio:
        class transcriptions:
            @staticmethod
            def create(**kwargs):
                class Result: text = "mock transcription"

                return Result()

    class responses:
        @staticmethod
        def create(**kwargs):
            class Result: output_text = "mock response"

            return Result()

def make_test_audio(path, duration_ms=5000):
    sine = Sine(440).to_audio_segment(duration=duration_ms)
    sine.export(path, format="mp3", bitrate="128k")

@pytest.fixture
def mock_client():
    return MockClient()

def test_transcribe_audio_invalid(tmp_path, mock_client):
    """
    GIVEN the transcribe_audio function
    WHEN the function is called with an invalid audio path
    THEN check that an OS error is raised
    """

    path = tmp_path / "missing.mp3"
    with pytest.raises(AIServiceError):
        transcribe_audio(str(path), mock_client)

def test_transcribe_audio_lg_valid(tmp_path, mock_client):
    """
    GIVEN the transcribe_audio function
    WHEN the function is called with a large valid file
    THEN check that the audio is chunked and expected transcription is present
    """
    path = tmp_path / "mock.mp3"
    make_test_audio(path, duration_ms=6000)

    result = transcribe_audio(
        str(path),
        ai_client=mock_client,
        chunk_duration_ms=2000,
        output_dir=tmp_path,
        max_file_size=0
    )

    chunks = list(tmp_path.glob("**/chunk_*.mp3"))

    assert len(chunks) >= 2

    for chunk in chunks:
        assert chunk.stat().st_size > 0

    assert "mock transcription" in result

def test_transcribe_audio_sm_valid(tmp_path, mock_client):
    """
    GIVEN the transcribe_audio function
    WHEN the function is called with a small valid file
    THEN check that the expected transcription is present
    """
    path = tmp_path / "mock.mp3"
    make_test_audio(path, duration_ms=6000)

    result = transcribe_audio(
        str(path),
        ai_client=mock_client,
        output_dir=tmp_path
    )

    assert "mock transcription" in result

def test_summarize_transcript_nonempty_valid(mock_client):
    """
    GIVEN the summarize_transcript_function
    WHEN the function is called with a non-empty transcription
    THEN check that a summary is returned
    """
    result = summarize_transcript("not empty", mock_client)

    assert result == "mock response"


def test_summarize_transcript_empty_valid(mock_client):
    """
    GIVEN the summarize_transcript_function
    WHEN the function is called with a non-empty transcription
    THEN check that a summary is returned
    """
    result = summarize_transcript(None, mock_client)

    assert result == "mock response"

