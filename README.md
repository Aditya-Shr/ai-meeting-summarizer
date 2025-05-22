# AI Meeting Summarizer

The AI Meeting Summarizer is a Gradio-powered application that turns your meeting audio recordings into transcripts, clear summaries, action items, and decisions. It uses OpenAI Whisper for transcription, BART for summarization, and Flan-T5 for extracting key points—all in a simple web interface. This tool is perfect for quickly capturing what matters most from your meetings.

## Features
- Audio-to-text transcription (Whisper)
- Meeting summarization
- Action item and decision extraction
- Calendar integration
- User-friendly Gradio web interface

- ## Models Used
- Transcription: [OpenAI Whisper](https://github.com/openai/whisper) (default: `base` model)
- Summarization: [facebook/bart-large-cnn](https://huggingface.co/facebook/bart-large-cnn) (Hugging Face BART)
- Action Item & Decision Extraction: [google/flan-t5-base](https://huggingface.co/google/flan-t5-base) (Hugging Face Flan-T5, prompt-based)

## Prerequisites
- Python 3.8+
- FFmpeg (for audio processing)
- Google Calendar API credentials (for calendar features)

### Installing FFmpeg
- **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html) and add to PATH
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`

## Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/yourusername/ai-meeting-summarizer.git
cd ai-meeting-summarizer
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -e .
pip install -r requirements.txt
```

### 2.1. Frontend Setup 
In the New Terminal,
```bash
cd frontend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install Gradio
pip install gradio

```

### 3. Database Setup
```bash
python create_db.py
```

### 4. Google Calendar Setup (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download credentials and save as `credentials.json` in the `backend` directory

### 5. Environment Setup
Create a `.env` file in the backend directory with the following content:
```
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your_secret_key
```
To generate a secure SECRET_KEY (works in all shells):
```
python -c "import secrets; print(secrets.token_hex(32))"
```
**Copy the output key from the terminal, open your `.env` file, and paste it as the value for SECRET_KEY:**
```
SECRET_KEY=your_copied_key_here
```
For example, if the command outputs:
```
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```
then your `.env` file should contain:
```
SECRET_KEY=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

### 6. Run the Application
1. Start Backend:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

2. Start Frontend (in new terminal):
```bash
cd frontend
python gradio_app.py
```

Access the application:
- API: http://localhost:8000
- Web UI: http://localhost:7860


## Troubleshooting
- If you get "FFmpeg not found" error, ensure FFmpeg is installed and in your PATH
- For calendar integration issues, verify `credentials.json` is in the correct location
- Check console output for detailed error messages

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Downloading Models

This project uses Hugging Face and Whisper models.  
They will be automatically downloaded the first time you run the backend, or you can manually download them using:

```bash
python -c "import whisper; whisper.load_model('base')"
