"""Firebase configuration and initialization."""
import firebase_admin
from firebase_admin import credentials, firestore

def init_firebase():
    """Initialize Firebase app if not already initialized."""
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)

def get_db():
    """Get Firestore database instance."""
    init_firebase()
    return firestore.client()
