# <img src="static/assets/video_summarizer_icon.svg" alt="Video Summarization Logo" width="50px"/> Video Summarization
A lightweight **Flask web app** that lets users upload a video and get an AI-generated summary of its content.
The app extracts audio, transcribes speech, and produces a text summary using OpenAI’s API in **Markdown** - suitable for notetaking apps like **Notion**.

**Features**
1. 🎥 Upload video files directly from your browser
2. 🧠 AI-powered transcription and summarization
3. ⚡ Responsive, single-page interface with loading and result views
4. 📜 Scrollable summary display for longer outputs
5. 🔐 Local processing – no data stored on the server

**Tech Stack**
- Backend: Flask, OpenAI API, ffmpeg
- Frontend: HTML, CSS, JavaScript

---

### Demo

https://github.com/user-attachments/assets/11ca34d0-6cfd-434a-82f9-83c130248584

---

### Requirements
1. Python
2. openai api key
3. openai
4. ffmpeg
    - Make sure the ffmpeg/bin folder is added to your environment variables (so the app can call it directly).
    - You can verify by running ffmpeg -version in your terminal.
5. ffmpeg_python
6. Flask
7. python-dotenv

---

### Installation
1. Clone the repository:

```commandline
git clone https://github.com/wooyeoup-rho/video-summarization
cd video-summarization
```

2. Install dependencies
```commandline
pip install -r requirements.txt
```

3. Set your OpenAPI API key

There are two options:

**Option A: Using a .env file (recommended)**

Create a file named .env in the project root with the following line:
```commandline
echo OPENAI_API_KEY="your_api_key_here" > .env
```

This will be automatically loaded when the app runs.


**Option B: Using environment variables directly**
```commandline
# macOS/Linux
export OPENAI_API_KEY="your_api_key_here"

# Windows (temporary, current session only)
set OPENAI_API_KEY="your_api_key_here"

# Windows (permanent, requires terminal restart)
setx OPENAI_API_KEY "your_api_key_here"
```

---

### Usage

Run the Flask development server:

```commandline
python run.py
```

Then open your browser and visit http://localhost:5000

1. Choose a video file through the explorer or drag and drop one.
2. After the upload is complete, continue to transcription & summarization.
   - **Action will use your API key.**
3. View the transcription and summary in the accordion tabs.
5. Export output as PDF if required.

---

### License

MIT License.
Feel free to use, modify, and share.
