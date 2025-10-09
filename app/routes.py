from flask import Blueprint, render_template, request, jsonify, current_app
import ffmpeg
import os
from .ai.ai import transcribe_audio, summarize_transcript

bp = Blueprint("main", __name__)

@bp.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")

@bp.route("/upload", methods=["POST"])
def upload():
    if "video" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    video_file = request.files["video"]
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    audio_folder = current_app.config["AUDIO_FOLDER"]

    video_path = os.path.join(upload_folder, video_file.filename)
    video_file.save(video_path)

    # Convert to MP3
    mp3_filename = os.path.splitext(os.path.basename(video_path))[0] + ".mp3"
    mp3_path = os.path.join(audio_folder, mp3_filename)

    (
        ffmpeg
        .input(video_path)
        .output(mp3_path, format='mp3', acodec='libmp3lame')
        .overwrite_output()
        .run()
    )

    return jsonify({"mp3_path": mp3_path})

@bp.route("/transcribe", methods=["POST"])
def transcribe():
    data = request.get_json()
    audio_path = data.get("audio_path")

    if not audio_path or not os.path.exists(audio_path):
        return jsonify({"error": "Invalid or missing audio path"}), 400

    transcript = transcribe_audio(audio_path)

    return jsonify({"transcript": transcript})

@bp.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    text = data.get("text")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    summary = summarize_transcript(text)

    return jsonify({"summary": summary})