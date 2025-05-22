import gradio as gr
import requests
import threading
import time
import uuid
from datetime import datetime
import json

BACKEND_URL = "http://localhost:8000"

# Global variable to store the current process ID
current_process_id = None
cancellation_event = threading.Event()

def _format_error_message(status_code, response_text):
    """Helper function to format error messages from backend response."""
    try:
        error_json = json.loads(response_text)
        detail = error_json.get("detail")
        if detail:
            if isinstance(detail, list) and detail:
                first_error = detail[0]
                msg = first_error.get('msg', 'Unknown error')
                loc = first_error.get('loc', [])
                if loc and len(loc) > 1:
                    return f"Error: Invalid input for '{'.'.join(map(str, loc[1:]))}': {msg}" # Removed status code for this specific format
                return f"Error: {msg}" # Removed status code
            elif isinstance(detail, str):
                if detail == "Meeting not found": # Specific case for "Meeting not found"
                    return "Meeting not found"
                return f"Error: {status_code} - {detail}" # Standard format for other string details
        # Fallback if detail is not helpful or not present
        return f"Error: {status_code} - Could not parse error details from response: {response_text[:100]}..."
    except json.JSONDecodeError:
        # Fallback if response_text is not JSON
        return f"Error: {status_code} - {response_text[:100]}..." # Truncate long non-JSON errors

def cancel_process():
    """Cancel the current process"""
    global current_process_id
    if current_process_id:
        try:
            response = requests.post(f"{BACKEND_URL}/api/meetings/cancel/{current_process_id}")
            if response.status_code == 200:
                cancellation_event.set()
                return "Process cancellation requested"
            return _format_error_message(response.status_code, response.text)
        except Exception as e:
            return f"Error cancelling process: {str(e)}"
    return "No active process to cancel"

# Function to handle audio upload and processing
def process_audio(audio_file):
    global current_process_id, cancellation_event
    
    if audio_file is None:
        return "No file uploaded.", "", "No Action Items found", "No Decisions made"
    
    try:
        # Reset cancellation event
        cancellation_event.clear()
        process_id = str(uuid.uuid4())
        current_process_id = process_id  # Set immediately so cancel works
        
        with open(audio_file, "rb") as f:
            files = {"file": (audio_file, f, "audio/mpeg")}
            data = {"transcribe": "true", "summarize": "true", "process_id": process_id}
            
            response = requests.post(f"{BACKEND_URL}/api/meetings/upload-direct", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                transcript = result.get("transcript", "")
                summary = result.get("summary", "")
                action_items = result.get("action_items", "")
                decisions = result.get("decisions", "")

                action_items_str = action_items if action_items else "No Action Items found"
                decisions_str = decisions if decisions else "No Decisions made"
                return transcript, summary, action_items_str, decisions_str
            elif response.status_code == 499:
                return "Process cancelled by user", "", "No Action Items found", "No Decisions made"
            else:
                return _format_error_message(response.status_code, response.text), "", "No Action Items found", "No Decisions made"
    except Exception as e:
        return f"Exception: {str(e)}", "", "No Action Items found", "No Decisions made"
    finally:
        current_process_id = None

# --- Meeting Management Tab Functions ---
def schedule_meeting(title, description, start_time, end_time, attendees):
    try:
        attendees_list = []
        if attendees:
            for email in attendees.split(","):
                email = email.strip()
                if email:
                    attendees_list.append({"email": email})
        payload = {
            "title": title,
            "description": description,
            "start_time": start_time,
            "end_time": end_time,
            "attendees": attendees_list
        }
        response = requests.post(f"{BACKEND_URL}/api/meetings/schedule", json=payload)
        if response.status_code == 200:
            data = response.json()
            calendar_link = data.get("calendar_link")
            meet_link = data.get("meet_link")
            meeting_id = data.get("id")
            result = ""
            if calendar_link:
                result += f'<div style="text-align:center; margin-top: 16px;"><a href="{calendar_link}" target="_blank" style="font-size:1.3em; font-weight:bold; color:#2563eb; text-decoration:underline;">Meeting Link{f" (Meeting ID - {meeting_id})" if meeting_id else ""}</a></div>'
            if meet_link:
                result += f'<div style="text-align:center; margin-top: 8px;"><a href="{meet_link}" target="_blank" style="font-size:1.1em; color:#2563eb; text-decoration:underline;">Google Meet Link</a></div>'
            if not result:
                result = "<div style='text-align:center;'>No calendar link available.</div>"
            return result
        else:
            return _format_error_message(response.status_code, response.text)
    except Exception as e:
        return f"Exception: {str(e)}"

def get_all_meetings():
    try:
        response = requests.get(f"{BACKEND_URL}/api/meetings/")
        if response.status_code == 200:
            meetings = response.json()
            if not meetings:
                return "No meetings found."
            out = ""
            for m in meetings:
                out += f"ID: {m['id']}\n"
            return out
        else:
            return _format_error_message(response.status_code, response.text)
    except Exception as e:
        return f"Exception: {str(e)}"

def get_meeting_details(meeting_id):
    if not meeting_id or not str(meeting_id).strip():
        return "No Meeting ID provided."
    try:
        response = requests.get(f"{BACKEND_URL}/api/meetings/{str(meeting_id).strip()}")
        if response.status_code == 200:
            m = response.json()
            if not isinstance(m, dict):
                return "Error: Received unexpected data format from server."
            # Format the meeting details into a readable string
            details_str = f"Meeting ID: {m.get('id', 'N/A')}\n"
            details_str += f"Title: {m.get('title', 'N/A')}\n"
            details_str += f"Description: {m.get('description', 'N/A')}\n"
            details_str += f"Date: {m.get('date', 'N/A')}\n"
            details_str += f"Duration: {m.get('duration', 'N/A')}\n"
            details_str += f"Participants: {m.get('participants', 'N/A')}\n"
            details_str += f"Status: {m.get('status', 'N/A')}\n"
            details_str += f"Calendar Event ID: {m.get('calendar_event_id', 'N/A')}\n"
            details_str += f"Created At: {m.get('created_at', 'N/A')}\n"
            details_str += f"Updated At: {m.get('updated_at', 'N/A')}"
            # Add other fields as needed, e.g., audio_file_path, transcript, summary if you want to show them
            return details_str
        else:
            return _format_error_message(response.status_code, response.text)
    except Exception as e:
        return f"Exception: {str(e)}"

def update_meeting(meeting_id, title, description, date, duration, participants, status):
    if not meeting_id or not str(meeting_id).strip():
        return "No Meeting ID provided for update."
    try:
        payload = {
            "title": title,
            "description": description,
            "date": date if date else None,  # Send None if empty, backend should handle
            "duration": duration if duration else None, # Send None if empty
            "participants": participants if participants else None, # Send None if empty, expect comma-separated string
            "status": status if status else None # Send None if empty
        }
        # Filter out None values to only send provided fields
        payload = {k: v for k, v in payload.items() if v is not None}

        if not payload:
            return "No update information provided."

        response = requests.put(f"{BACKEND_URL}/api/meetings/{str(meeting_id).strip()}", json=payload)
        if response.status_code == 200:
            return "Meeting updated successfully!"
        else:
            return _format_error_message(response.status_code, response.text)
    except Exception as e:
        return f"Exception: {str(e)}"

def delete_meeting(meeting_id):
    if not meeting_id or not str(meeting_id).strip():
        return "No Meeting ID provided for delete."
    try:
        response = requests.delete(f"{BACKEND_URL}/api/meetings/{str(meeting_id).strip()}")
        if response.status_code == 200:
            return "Meeting deleted successfully!"
        else:
            return _format_error_message(response.status_code, response.text)
    except Exception as e:
        return f"Exception: {str(e)}"

with gr.Blocks(title="AI Meeting Summarizer") as demo:
    with gr.Tabs():
        with gr.TabItem("Meeting Summarizer"):
            gr.Markdown("""
            <div style='text-align: center;'>
                <h1>AI Meeting Summarizer</h1>
                <p>Upload a meeting audio file to get the transcript, summary, action items, and decisions.</p>
            </div>
            """, elem_id="centered-header")
            with gr.Row():
                with gr.Column(scale=1):
                    audio_input = gr.Audio(type="filepath", label="Upload Meeting Audio (.mp3, .wav, etc.)")
                    with gr.Row():
                        submit_btn = gr.Button("Transcribe & Summarize")
                        cancel_btn = gr.Button("Cancel", variant="stop")
                with gr.Column(scale=2):
                    transcript_output = gr.Textbox(label="Transcript", lines=6)
                    summary_output = gr.Textbox(label="Summary", lines=4)
                    action_items_output = gr.Textbox(label="Action Items", lines=4)
                    decisions_output = gr.Textbox(label="Decisions", lines=4)
            submit_btn.click(
                fn=process_audio,
                inputs=audio_input,
                outputs=[transcript_output, summary_output, action_items_output, decisions_output]
            )
            cancel_btn.click(
                fn=cancel_process,
                inputs=[],
                outputs=[]
            )
        with gr.TabItem("Schedule & Manage Meetings"):
            gr.Markdown("""
            <div style='text-align: center;'>
                <h2>Schedule & Manage Meetings</h2>
            </div>
            """)
            with gr.Row():
                # --- LEFT COLUMN ---
                with gr.Column(scale=1): # Adjusted scale for potentially more content
                    # Schedule Meeting Section
                    gr.Markdown("### Schedule New Meeting")
                    title_sched = gr.Textbox(label="Title")
                    description_sched = gr.Textbox(label="Description")
                    
                    # Get current time for placeholder
                    current_time_formatted = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                    
                    start_time_sched = gr.Textbox(
                        label="Start Time", 
                        placeholder=current_time_formatted, 
                        info="Format: YYYY-MM-DDTHH:MM:SS"
                    )
                    end_time_sched = gr.Textbox(
                        label="End Time", 
                        placeholder=current_time_formatted, # Or calculate a default end time e.g., current_time + 1 hour
                        info="Format: YYYY-MM-DDTHH:MM:SS"
                    )
                    attendees_sched = gr.Textbox(label="Attendees (Separate emails by Comma)")
                    schedule_btn = gr.Button("Schedule Meeting")
                    schedule_result = gr.HTML(label="Meeting Link")
                    schedule_btn.click(
                        fn=schedule_meeting,
                        inputs=[title_sched, description_sched, start_time_sched, end_time_sched, attendees_sched],
                        outputs=schedule_result
                    )

                    gr.Markdown("---") # Separator

                    # Update Meeting Section
                    gr.Markdown("### Update Existing Meeting")
                    meeting_id_update = gr.Textbox(label="Meeting ID to Update") # Dedicated ID for update
                    
                    gr.Markdown("#### Fields to Update (leave blank if no change)")
                    update_title = gr.Textbox(label="New Title")
                    update_desc = gr.Textbox(label="New Description")
                    update_date = gr.Textbox(label="New Date (YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD)")
                    update_duration = gr.Textbox(label="New Duration (e.g., 30m, 1h)") 
                    update_participants = gr.Textbox(label="New Participants (comma-separated emails)")
                    update_status = gr.Textbox(label="New Status (e.g., scheduled, completed)")
                    
                    update_btn = gr.Button("Update Meeting")
                    update_result = gr.Textbox(label="Update Result", interactive=False)
                    update_btn.click(
                        fn=update_meeting, 
                        inputs=[
                            meeting_id_update, update_title, update_desc, 
                            update_date, update_duration, update_participants, update_status
                        ], 
                        outputs=update_result
                    )

                # --- RIGHT COLUMN ---
                with gr.Column(scale=1): # Adjusted scale
                    # Meetings List Section
                    gr.Markdown("### Get All Meetings")
                    meetings_list = gr.Textbox(label="Meetings List", lines=10) # Reduced lines a bit
                    get_all_btn = gr.Button("Get All Meetings")
                    get_all_btn.click(fn=get_all_meetings, inputs=[], outputs=meetings_list)

                    gr.Markdown("---") # Separator

                    # Get Meeting Details Section
                    gr.Markdown("### Get Meeting Details")
                    meeting_id_get = gr.Textbox(label="Meeting ID for Details") # Dedicated ID for get
                    get_details_btn = gr.Button("Get Details")
                    details_box = gr.Textbox(label="Meeting Details", lines=5, interactive=False) # Reduced lines
                    get_details_btn.click(fn=get_meeting_details, inputs=meeting_id_get, outputs=details_box)
                    
                    gr.Markdown("---") # Separator
                    
                    # Delete Meeting Section
                    gr.Markdown("### Delete Meeting") # Changed to H3 for consistency
                    delete_meeting_id_input = gr.Textbox(label="Meeting ID to Delete") # Renamed for clarity
                    delete_btn = gr.Button("Delete Meeting", variant="stop")
                    delete_result = gr.Textbox(label="Delete Result", interactive=False)
                    # Ensure this uses the correct input: delete_meeting_id_input
                    delete_btn.click(fn=delete_meeting, inputs=delete_meeting_id_input, outputs=delete_result)

if __name__ == "__main__":
    demo.launch() 