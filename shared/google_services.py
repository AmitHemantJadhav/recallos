from google.cloud import storage, firestore
from datetime import datetime
import os

# Initialize clients
storage_client = storage.Client()
firestore_client = firestore.Client(project='recallos-476300', database='(default)')

BUCKET_NAME = 'recallos-audio-files'

def upload_to_storage(file_path: str, destination_name: str) -> str:
    """Upload file to Cloud Storage and return public URL"""
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(destination_name)
        blob.upload_from_filename(file_path)
        
        print(f"✅ Uploaded {destination_name} to Cloud Storage")
        return f"gs://{BUCKET_NAME}/{destination_name}"
    except Exception as e:
        print(f"❌ Storage upload failed: {str(e)}")
        raise

def save_session(session_id: str, data: dict) -> None:
    """Save session metadata to Firestore"""
    try:
        doc_ref = firestore_client.collection('sessions').document(session_id)
        data['updated_at'] = datetime.now()
        doc_ref.set(data, merge=True)
        
        print(f"✅ Saved session {session_id} to Firestore")
    except Exception as e:
        print(f"❌ Firestore save failed: {str(e)}")
        raise

def get_session(session_id: str) -> dict:
    """Get session data from Firestore"""
    try:
        doc_ref = firestore_client.collection('sessions').document(session_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"❌ Firestore read failed: {str(e)}")
        return None

def log_agent_action(agent_name: str, action: str, details: dict):
    """Log agent actions (using print for now)"""
    print(f"📊 [{agent_name}] {action}: {details}")