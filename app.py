from flask import Flask, render_template, request, jsonify
import ffmpeg
import os
from ai.ai import transcribe_audio, summarize_transcript

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

UPLOAD_FOLDER = os.path.join(DATA_DIR, "uploads")
AUDIO_FOLDER = os.path.join(DATA_DIR, "audio")

for folder in [UPLOAD_FOLDER, AUDIO_FOLDER]:
    os.makedirs(folder, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "video" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    video_file = request.files["video"]
    video_path = os.path.join(UPLOAD_FOLDER, video_file.filename)
    video_file.save(video_path)

    # Convert to MP3
    mp3_filename = os.path.splitext(os.path.basename(video_path))[0] + ".mp3"
    mp3_path = os.path.join(AUDIO_FOLDER, mp3_filename)

    (
        ffmpeg
        .input(video_path)
        .output(mp3_path, format='mp3', acodec='libmp3lame')
        .overwrite_output()
        .run()
    )

    return jsonify({"mp3_path": mp3_path})

@app.route("/transcribe", methods=["POST"])
def transcribe():
    data = request.get_json()
    audio_path = data.get("audio_path")

    if not audio_path or not os.path.exists(audio_path):
        return jsonify({"error": "Invalid or missing audio path"}), 400

    transcript = transcribe_audio(audio_path)

    return jsonify({"transcript": transcript})

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    text = data.get("text")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    summary = summarize_transcript(text)

    return jsonify({"summary": summary})

if __name__ == "__main__":
    app.run(debug=True)