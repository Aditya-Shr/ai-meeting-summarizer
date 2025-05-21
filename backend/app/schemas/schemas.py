from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

# Meeting schemas
class MeetingBase(BaseModel):
    title: str
    description: Optional[str] = None
    date: Optional[datetime] = None
    duration: Optional[int] = None
    participants: Optional[List[str]] = None
    status: Optional[str] = None

class MeetingCreate(MeetingBase):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    attendees: Optional[List[Dict[str, str]]] = None

class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    duration: Optional[int] = None
    participants: Optional[List[str]] = None
    status: Optional[str] = None
    audio_file_path: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    calendar_event_id: Optional[str] = None

class Meeting(MeetingBase):
    id: int
    audio_file_path: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    calendar_event_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Action Item schemas
class ActionItemBase(BaseModel):
    title: str
    description: str
    assignee: str
    due_date: Optional[datetime] = None

class ActionItemCreate(ActionItemBase):
    meeting_id: int

class ActionItemUpdate(ActionItemBase):
    pass

class ActionItem(ActionItemBase):
    id: int
    meeting_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Decision schemas
class DecisionBase(BaseModel):
    title: str
    description: str
    decision_maker: str
    rationale: str

class DecisionCreate(DecisionBase):
    meeting_id: int

class DecisionUpdate(DecisionBase):
    pass

class Decision(DecisionBase):
    id: int
    meeting_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 