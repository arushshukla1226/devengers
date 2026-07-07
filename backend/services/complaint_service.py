import uuid
from datetime import datetime

# In-memory DB (replace with Firestore in production)
COMPLAINTS_DB = {}

def file_complaint(user_name, category, description, location, ai_analysis=""):
    complaint_id = f"SB-{uuid.uuid4().hex[:8].upper()}"
    complaint = {
        "id": complaint_id,
        "user": user_name,
        "category": category,
        "description": description,
        "location": location,
        "ai_analysis": ai_analysis,
        "status": "Filed",
        "filed_at": datetime.now().isoformat(),
        "eta": "5-7 working days"
    }
    COMPLAINTS_DB[complaint_id] = complaint
    return complaint

def track_complaint(complaint_id):
    return COMPLAINTS_DB.get(complaint_id, {"error": "Complaint not found"})

def list_all_complaints():
    return list(COMPLAINTS_DB.values())