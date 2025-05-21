import gradio as gr
import requests
import threading
import time
import uuid

BACKEND_URL = "http://localhost:8000"

# Global variable to store the current process ID
current_process_id = None
cancellation_event = threading.Event()

def cancel_process():
    """Cancel the current process"""
    global current_process_id
    if current_process_id:
        try:
            response = requests.post(f"{BACKEND_URL}/api/meetings/cancel/{current_process_id}")
            if response.status_code == 200:
                cancellation_event.set()
                return "Process cancellation requested"
            return f"Error cancelling process: {response.text}"
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
                action_items = result.get("action_items", [])
                decisions = result.get("decisions", [])

                def format_items(items, no_text, no_message):
                    if not items or (isinstance(items, list) and len(items) == 1 and items[0].get("title", "").lower().startswith(no_text)):
                        return no_message
                    if isinstance(items, list):
                        return "\n\n".join(
                            "\n".join(f"{k.capitalize()}: {v}" for k, v in item.items() if v) for item in items
                        )
                    return no_message
                
                action_items_str = format_items(action_items, "no action", "No Action Items found")
                decisions_str = format_items(decisions, "no decision", "No Decisions made")
                return transcript, summary, action_items_str, decisions_str
            elif response.status_code == 499:
                return "Process cancelled by user", "", "No Action Items found", "No Decisions made"
            else:
                return f"Error: {response.status_code} - {response.text}", "", "No Action Items found", "No Decisions made"
    except Exception as e:
        return f"Exception: {str(e)}", "", "No Action Items found", "No Decisions made"
    finally:
        current_process_id = None

with gr.Blocks(title="AI Meeting Summarizer") as demo:
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

if __name__ == "__main__":
    demo.launch() 