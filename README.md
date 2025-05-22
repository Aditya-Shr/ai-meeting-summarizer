# AI Meeting Summarizer

An intelligent system that transcribes, summarizes, and tracks meetings using AI.

## Features

- Audio file transcription
- Meeting summarization
- Action item extraction
- Decision tracking
- Calendar integration
- RESTful API
- User-friendly error messages and validation

## Backend Setup

### Prerequisites

- Python 3.8+
- SQLite
- FFmpeg (for audio processing)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-meeting-summarizer.git
cd ai-meeting-summarizer
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create a .env file in the backend directory
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your_secret_key
HUGGINGFACE_CACHE_DIR=./.cache/huggingface
```
To generate a secure SECRET_KEY, run:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Copy the generated key and replace `your_secret_key` in the `.env` file.

4. Set up Google Calendar API credentials:
   - Go to the Google Cloud Console
   - Create a new project or select an existing one
   - Enable the Google Calendar API
   - Create OAuth 2.0 credentials (Desktop application)
   - Download the credentials and save as `credentials.json` in the backend directory
   - Note: Never commit `credentials.json` or `token.pickle` to version control

5. Initialize the database:
```bash
python create_db.py
```

### Running the Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## Frontend Setup

### Prerequisites

- Python 3.8+
- Gradio (installed via backend requirements)

### Running the Frontend (Gradio UI)

The Gradio UI is launched automatically from the backend using the `frontend/gradio_app.py` file. To start the Gradio interface:

```bash
cd frontend
python gradio_app.py
```

The frontend will be available at `http://localhost:7860` (or the port Gradio specifies).

### Usage Notes

- **Meeting ID Required:** For all Get, Update, and Delete operations, you must provide a valid Meeting ID. If you do not enter a Meeting ID, the UI will show a clear message: "No Meeting ID provided."
- **User-Friendly Errors:** All error messages are now formatted for clarity. For example, if a meeting is not found, you will see "Meeting not found" instead of a raw JSON error.
- **Update Meeting:** You can update any field of a meeting by providing its Meeting ID and the fields you wish to change. Leave fields blank to keep them unchanged.
- **Delete Meeting:** Enter the Meeting ID to delete a meeting. If the ID is missing or invalid, you will see a clear error message.
- **Get Meeting Details:** Enter a Meeting ID to view its details in a user-friendly format.

### API Documentation

Once the server is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- See also: `API_DOCUMENTATION.md` (not tracked by git)

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| DATABASE_URL | Database connection string | sqlite:///./app.db | No |
| SECRET_KEY | Application secret key | - | Yes |
| HUGGINGFACE_CACHE_DIR | Cache directory for HuggingFace models | ./.cache/huggingface | No |
| ALLOWED_ORIGINS | CORS allowed origins | * | No |

## Important Notes

- Keep your SECRET_KEY secure and never commit it to version control
- The `credentials.json` and `token.pickle` files contain sensitive information and should never be committed
- Use `credentials.json.example` as a template for setting up your credentials
- The database file (`meetings.db`) is excluded from version control as it may contain sensitive information
- If you need to change the SECRET_KEY, generate a new one using the provided command

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Downloading Models

This project uses Hugging Face and Whisper models.  
They will be automatically downloaded the first time you run the backend, or you can manually download them using:

```bash
python -c "import whisper; whisper.load_model('base')"
```