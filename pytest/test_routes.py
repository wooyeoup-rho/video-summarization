from unittest.mock import patch
import io

def test_home_route(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    response = client.get("/")

    assert response.status_code == 200
    assert b"Video Summarizer" in response.data
    assert b"Summarize Video Content" in response.data

def test_upload_no_file(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/upload' page is requested (POST) with no data
    THEN check that the status code is 400 and an error is raised
    """
    response = client.post("/upload", data={})

    assert response.status_code == 400
    assert response.json["error"] == "No file uploaded"

@patch("app.routes.ffmpeg.input")
def test_upload_with_file(mock_ffmpeg, client, tmp_path):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/upload' page is requested (POST) with a valid video path
    THEN check that the response is valid
    """
    (
        mock_ffmpeg.return_value
        .output.return_value
        .overwrite_output.return_value
        .run
    ).return_value = None

    data = {
        "video": (io.BytesIO(b"Very cool content"), "real-video.mp4")
    }

    client.application.config["UPLOAD_FOLDER"] = tmp_path / "uploads"
    client.application.config["AUDIO_FOLDER"] = tmp_path / "audio"
    client.application.config["UPLOAD_FOLDER"].mkdir()
    client.application.config["AUDIO_FOLDER"].mkdir()

    response = client.post("/upload", data=data)

    assert response.status_code == 200
    mp3_path = response.json["mp3_path"]
    assert mp3_path.endswith("real-video.mp3")

def test_transcribe_no_file(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/transcribe' page is requested (POST) with no file
    THEN check that the status code is 400 and an error is raised
    """
    response = client.post("/transcribe", json={"wooyeoup": "rho"})

    assert response.status_code == 400
    assert response.json["error"] == "Invalid or missing audio path"

@patch("app.routes.transcribe_audio")
# @patch("app.routes.os.path.exists", return_value=True)
def test_transcribe_with_file(mock_transcribe_audio, client, tmp_path):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/transcribe' page is requested (POST) with a valid audio path
    THEN check that the response is valid
    """
    audio_file = tmp_path / "mock.mp3"
    audio_file.write_bytes(b"mock audio content")
    mock_transcribe_audio.return_value = "mock transcript"

    response = client.post("/transcribe", json={"audio_path": str(audio_file)})

    assert response.status_code == 200
    assert response.json["transcript"] == mock_transcribe_audio.return_value

def test_summarize_no_file(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/summarize' page is requested (POST) with no file
    THEN check that the status code is 400 and an error is raised
    """
    response = client.post("/summarize", json={"key": "value"})

    assert response.status_code == 400
    assert response.json["error"] == "No text provided"

@patch("app.routes.summarize_transcript")
def test_summarize_with_file(mock_summarize_transcript, client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/summarize' page is requested (POST) with a valid text file
    THEN check that the response is valid
    """
    mock_summarize_transcript.return_value = "mock summary"

    response = client.post("/summarize", json={"text": "cool text"})

    assert response.status_code == 200
    assert response.json["summary"] == mock_summarize_transcript.return_value