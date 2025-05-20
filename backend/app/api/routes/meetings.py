from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.core.database import get_db
from app.models.models import Meeting
from app.schemas.schemas import Meeting as MeetingSchema, MeetingCreate, MeetingUpdate
from app.services.meeting_service import MeetingService
from app.services.transcription_service import TranscriptionService
from app.services.summarization_service import SummarizationService
from app.services.calendar_service import CalendarService
from app.services.action_item_service import ActionItemService
from app.services.decision_service import DecisionService
import json
import os
import shutil
from datetime import datetime, timedelta

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

router = APIRouter()

@router.post("/", response_model=MeetingSchema)
async def create_meeting(
    meeting: MeetingCreate,
    db: Session = Depends(get_db)
):
    """Create a new meeting with all available fields"""
    return MeetingService.create_meeting(db, meeting)

@router.get("/", response_model=List[MeetingSchema])
async def get_meetings(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get all meetings with optional filtering"""
    return MeetingService.get_meetings(
        db, 
        skip=skip, 
        limit=limit,
        status=status,
        date_from=date_from,
        date_to=date_to
    )

@router.get("/{meeting_id}", response_model=MeetingSchema)
async def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific meeting by ID with all details"""
    meeting = MeetingService.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

@router.put("/{meeting_id}", response_model=MeetingSchema)
async def update_meeting(
    meeting_id: int,
    meeting_update: MeetingUpdate,
    db: Session = Depends(get_db)
):
    """Update a meeting"""
    meeting = MeetingService.update_meeting(db, meeting_id, meeting_update)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

@router.delete("/{meeting_id}")
async def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_db)
):
    """Delete a meeting and its associated calendar event"""
    try:
        # First check if meeting exists
        meeting = MeetingService.get_meeting(db, meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        # Try to delete from calendar if it exists
        try:
            print(f"Attempting to delete calendar event for meeting {meeting_id}")
            print(f"Calendar event ID: {meeting.calendar_event_id}")
            
            if meeting.calendar_event_id:
                print(f"Deleting calendar event with ID: {meeting.calendar_event_id}")
                CalendarService.delete_meeting_event(meeting.calendar_event_id)
                print("Calendar event deleted successfully")
            else:
                print("No calendar event ID found for this meeting")
        except Exception as calendar_error:
            print(f"Error deleting calendar event: {str(calendar_error)}")
            # Continue with database deletion even if calendar deletion fails
        
        # Delete the meeting from database
        success = MeetingService.delete_meeting(db, meeting_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete meeting")
        
        return {
            "message": "Meeting and associated calendar event deleted successfully",
            "meeting_id": meeting_id,
            "calendar_event_id": meeting.calendar_event_id if hasattr(meeting, 'calendar_event_id') else None
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in delete_meeting: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting meeting: {str(e)}")

@router.post("/{meeting_id}/upload-audio")
async def upload_audio(
    meeting_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload audio file for a meeting"""
    meeting = MeetingService.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Create meeting directory if it doesn't exist
    meeting_dir = f"uploads/meeting_{meeting_id}"
    os.makedirs(meeting_dir, exist_ok=True)
    
    # Save file
    file_path = f"{meeting_dir}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update meeting with audio file path
    meeting_update = MeetingUpdate(audio_file_path=file_path)
    updated_meeting = MeetingService.update_meeting(db, meeting_id, meeting_update)
    
    return {"message": f"Audio file {file.filename} uploaded for meeting {meeting_id}", "file_path": file_path}

@router.get("/{meeting_id}/transcript")
async def get_transcript(
    meeting_id: int,
    db: Session = Depends(get_db)
):
    """Get transcript for a meeting"""
    meeting = MeetingService.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if not meeting.transcript:
        raise HTTPException(status_code=400, detail="No transcript available for this meeting")
    
    return {"transcript": meeting.transcript}

@router.get("/{meeting_id}/action-items")
async def get_meeting_action_items(
    meeting_id: int,
    db: Session = Depends(get_db)
):
    """Get all action items for a meeting"""
    meeting = MeetingService.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    action_items = ActionItemService.get_meeting_action_items(db, meeting_id)
    return action_items

@router.get("/{meeting_id}/decisions")
async def get_meeting_decisions(
    meeting_id: int,
    db: Session = Depends(get_db)
):
    """Get all decisions for a meeting"""
    meeting = MeetingService.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    decisions = DecisionService.get_meeting_decisions(db, meeting_id)
    return decisions

@router.post("/{meeting_id}/transcribe")
async def transcribe_meeting(
    meeting_id: int,
    provider: str = "huggingface",
    db: Session = Depends(get_db)
):
    """Transcribe audio for a meeting"""
    meeting = MeetingService.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if not meeting.audio_file_path:
        raise HTTPException(status_code=400, detail="No audio file has been uploaded for this meeting")
    
    # Check if file exists
    if not os.path.exists(meeting.audio_file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        # Create UploadFile from file path for transcription
        with open(meeting.audio_file_path, "rb") as audio_file:
            file_content = audio_file.read()
        
        upload_file = UploadFile(
            filename=os.path.basename(meeting.audio_file_path),
            file=None
        )
        upload_file.file = open(meeting.audio_file_path, "rb")
        
        # Transcribe audio with selected provider
        transcript = await TranscriptionService.transcribe_audio(upload_file, provider)
        
        # Update meeting with transcript
        meeting_update = MeetingUpdate(transcript=transcript)
        updated_meeting = MeetingService.update_meeting(db, meeting_id, meeting_update)
        
        return {
            "message": f"Transcription completed for meeting {meeting_id}",
            "transcript": transcript
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")
    finally:
        if upload_file and upload_file.file:
            upload_file.file.close()

@router.post("/{meeting_id}/summarize")
async def summarize_meeting(
    meeting_id: int,
    db: Session = Depends(get_db)
):
    """Generate summary, extract action items and decisions for a meeting"""
    meeting = MeetingService.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if not meeting.transcript:
        raise HTTPException(status_code=400, detail="No transcript available for this meeting. Please transcribe first.")
    
    try:
        # Generate summary
        summary = SummarizationService.summarize_text(meeting.transcript)
        
        # Extract action items and decisions
        action_items = SummarizationService.extract_action_items(meeting.transcript)
        decisions = SummarizationService.extract_decisions(meeting.transcript)
        
        # Ensure action_items and decisions are lists
        if action_items is None:
            action_items = []
        if decisions is None:
            decisions = []
            
        # Update meeting with summary
        meeting_update = MeetingUpdate(summary=summary)
        updated_meeting = MeetingService.update_meeting(db, meeting_id, meeting_update)
        
        # Save action items
        saved_action_items = []
        for item in action_items:
            if not item.get('title'):
                continue
                
            action_item = ActionItemCreate(
                meeting_id=meeting_id,
                title=item.get('title', ''),
                description=item.get('description', ''),
                assignee=item.get('assignee', ''),
                due_date=item.get('due_date')
            )
            saved_item = ActionItemService.create_action_item(db, action_item)
            saved_action_items.append(saved_item)
        
        # Save decisions
        saved_decisions = []
        for decision in decisions:
            if not decision.get('title'):
                continue
                
            decision_item = DecisionCreate(
                meeting_id=meeting_id,
                title=decision.get('title', ''),
                description=decision.get('description', ''),
                decision_maker=decision.get('decision_maker', ''),
                rationale=decision.get('rationale', '')
            )
            saved_decision = DecisionService.create_decision(db, decision_item)
            saved_decisions.append(saved_decision)
        
        return {
            "message": f"Summarization completed for meeting {meeting_id}",
            "summary": summary,
            "action_items": saved_action_items if saved_action_items else [],
            "decisions": saved_decisions if saved_decisions else []
        }
    except Exception as e:
        print(f"Error during summarization: {str(e)}")
        return {
            "message": f"Summarization completed for meeting {meeting_id}",
            "summary": summary if 'summary' in locals() else "",
            "action_items": [],
            "decisions": []
        }

@router.post("/{meeting_id}/schedule")
async def schedule_meeting(
    meeting_id: int,
    start_time: datetime = Body(...),
    end_time: datetime = Body(...),
    attendees: Optional[List[Dict[str, str]]] = Body(None),
    db: Session = Depends(get_db)
):
    """Schedule meeting in calendar"""
    meeting = MeetingService.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    try:
        # Format meeting description
        description = f"Meeting Title: {meeting.title}\n\n"
        if meeting.description:
            description += f"Description: {meeting.description}\n\n"
        if meeting.summary:
            description += f"Summary: {meeting.summary}\n\n"
        
        # Schedule in calendar
        event = CalendarService.create_meeting_event(
            summary=meeting.title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            attendees=attendees
        )
        
        # Update meeting with calendar event ID
        meeting_update = MeetingUpdate(calendar_event_id=event.get("event_id"))
        MeetingService.update_meeting(db, meeting_id, meeting_update)
        
        return {
            "message": f"Meeting scheduled successfully",
            "event_id": event.get("event_id"),
            "calendar_link": event.get("html_link"),
            "meet_link": event.get("meet_link")
        }
    except HTTPException as e:
        # Re-raise HTTPExceptions from the service
        raise e
    except Exception as e:
        print(f"Error scheduling meeting: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error scheduling meeting: {str(e)}")

@router.get("/calendar/upcoming")
async def get_upcoming_meetings(
    max_results: int = 10,
    db: Session = Depends(get_db)
):
    """Get upcoming calendar events"""
    try:
        events = CalendarService.get_upcoming_meetings(max_results=max_results)
        return {"events": events}
    except HTTPException as e:
        # Re-raise HTTPExceptions from the service
        raise e
    except Exception as e:
        print(f"Error retrieving calendar events: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving calendar events: {str(e)}") 