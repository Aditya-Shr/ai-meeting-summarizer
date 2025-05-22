# AI Meeting Summarizer Documentation

## API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication
Currently, the API does not require authentication for development purposes.

### Endpoints

#### Meetings
- `GET /api/meetings` - Get all meetings
  - Query Parameters:
    - `skip` (int, optional): Number of records to skip
    - `limit` (int, optional): Maximum number of records to return
    - `status` (string, optional): Filter by meeting status
    - `date_from` (datetime, optional): Filter by start date
    - `date_to` (datetime, optional): Filter by end date

- `GET /api/meetings/{meeting_id}` - Get specific meeting details

- `POST /api/meetings/{meeting_id}/transcribe` - Transcribe meeting audio
  - Parameters:
    - `provider` (string, optional): Transcription provider ("huggingface" or "whisper")

- `POST /api/meetings/transcribe-direct/{file_id}` - Direct transcription
  - Parameters:
    - `file_id` (string): ID of uploaded file

- `POST /api/meetings/summarize-direct/{file_id}` - Direct summarization
  - Parameters:
    - `file_id` (string): ID of uploaded file

#### Action Items
- `GET /api/action-items` - Get all action items
  - Query Parameters:
    - `meeting_id` (int, optional): Filter by meeting
    - `skip` (int, optional): Number of records to skip
    - `limit` (int, optional): Maximum number of records to return

- `GET /api/action-items/{action_item_id}` - Get specific action item

#### Decisions
- `GET /api/decisions` - Get all decisions
  - Query Parameters:
    - `meeting_id` (int, optional): Filter by meeting
    - `skip` (int, optional): Number of records to skip
    - `limit` (int, optional): Maximum number of records to return

- `GET /api/decisions/{decision_id}` - Get specific decision


## User Guide

### Getting Started
1. Clone the repository
2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Mac/Linux
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env`:
   ```
   DATABASE_URL=sqlite:///./app.db
   SECRET_KEY=your_secret_key
   OPENAI_API_KEY=your_openai_key
   ```

4. Start the backend:
   ```bash
   uvicorn app.main:app --reload
   ```

### Using the Application

1. **Uploading a Meeting**
   - Navigate to the meetings page
   - Click "Upload Meeting"
   - Select your audio file
   - Wait for transcription

2. **Viewing Summaries**
   - Go to the meetings list
   - Click on a meeting to view details
   - View the generated summary, action items, and decisions

3. **Managing Action Items**
   - View action items in the meeting details
   - Mark items as complete
   - Add new action items manually

4. **Calendar Integration**
   - Connect your Google Calendar
   - View upcoming meetings
   - Schedule new meetings

## Security

### Required Credentials

1. **Google Calendar Credentials**
   - Required for calendar integration
   - Download `credentials.json` from Google Cloud Console
   - Place in backend directory
   - Enable Google Calendar API in your project

2. **Database**
   - SQLite database by default
   - Configure `DATABASE_URL` in `.env`

3. **Secret Key**
   - Used for session management
   - Generate using:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
   - Set in `.env` as `SECRET_KEY`

### Security Best Practices
1. Never commit `.env` file
2. Keep API keys secure
3. Use HTTPS in production
4. Implement proper authentication
5. Regular security updates

## Models

### 1. Transcription Model
- **Model**: OpenAI Whisper (base)
- **Capabilities**:
  - Audio to text conversion
  - Supports multiple languages
  - High accuracy transcription
  - GPU acceleration available

### 2. Summarization Model
- **Model**: Facebook BART (large-cnn)
- **Capabilities**:
  - Text summarization
  - Extracts key points
  - Maintains context
  - Configurable length

### 3. Action Item & Decision Extraction
- **Model**: Google Flan-T5 (base)
- **Capabilities**:
  - Extracts action items
  - Identifies decisions
  - Structured output
  - Context-aware extraction

### Model Performance
- Transcription: ~1-2x real-time
- Summarization: ~1-2 seconds per page
- Action/Decision extraction: ~1 second per transcript

### Model Limitations
1. **Transcription**:
   - Requires clear audio
   - Limited by audio quality
   - May struggle with accents

2. **Summarization**:
   - Fixed length summaries
   - May miss nuanced context
   - Limited by input length

3. **Action/Decision Extraction**:
   - Requires clear language
   - May miss implicit items
   - Depends on transcript quality 