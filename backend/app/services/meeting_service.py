from sqlalchemy.orm import Session
from app.models.models import Meeting
from app.schemas.schemas import MeetingCreate, MeetingUpdate
from datetime import datetime
from typing import Optional
import json

class MeetingService:
    @staticmethod
    def create_meeting(db: Session, meeting: MeetingCreate):
        # Explicitly pick fields that exist in the Meeting SQLAlchemy model
        meeting_model_data = {
            "title": meeting.title,
            "description": meeting.description,
            "date": meeting.date,
            "duration": meeting.duration,
            "status": meeting.status
        }
        if meeting.participants:
            meeting_model_data['participants'] = json.dumps(meeting.participants)
        
        db_meeting = Meeting(**meeting_model_data)
        db.add(db_meeting)
        db.commit()
        db.refresh(db_meeting)
        return db_meeting
    
    @staticmethod
    def get_meeting(db: Session, meeting_id: int):
        db_meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        
        # Convert participants from JSON string back to list if present
        if db_meeting and db_meeting.participants:
            try:
                db_meeting.participants = json.loads(db_meeting.participants)
            except:
                db_meeting.participants = []
                
        return db_meeting
    
    @staticmethod
    def get_meetings(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ):
        query = db.query(Meeting)
        
        # Apply filters if provided
        if status:
            query = query.filter(Meeting.status == status)
        if date_from:
            query = query.filter(Meeting.date >= date_from)
        if date_to:
            query = query.filter(Meeting.date <= date_to)
        
        # Apply pagination and order by date if available, otherwise by created_at
        query = query.order_by(Meeting.created_at.desc())
        meetings = query.offset(skip).limit(limit).all()
        
        # Convert participants from JSON string back to list for each meeting
        for meeting in meetings:
            if meeting.participants:
                try:
                    meeting.participants = json.loads(meeting.participants)
                except:
                    meeting.participants = []
        
        return meetings
    
    @staticmethod
    def update_meeting(db: Session, meeting_id: int, meeting_update: MeetingUpdate):
        db_meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if db_meeting:
            # Get update data, excluding unset fields
            update_data = meeting_update.dict(exclude_unset=True)
            
            # Convert participants list to JSON string if present
            if 'participants' in update_data and update_data['participants'] is not None:
                update_data['participants'] = json.dumps(update_data['participants'])
            
            # Update each field if it's provided
            for field, value in update_data.items():
                setattr(db_meeting, field, value)
            
            # Update the updated_at timestamp
            db_meeting.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(db_meeting)
            
            # Convert participants back to a list for the returned object
            if db_meeting.participants:
                try:
                    db_meeting.participants = json.loads(db_meeting.participants)
                except:
                    db_meeting.participants = []
        
        return db_meeting
    
    @staticmethod
    def delete_meeting(db: Session, meeting_id: int):
        db_meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if db_meeting:
            db.delete(db_meeting)
            db.commit()
            return True
        return False 