"""Firebase operations helper functions."""
import streamlit as st
from datetime import datetime
from typing import Optional, Dict
from config.firebase_config import get_db
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import uuid


def save_user_info(email: str, name: str, role: str = None, password: str = None) -> None:
    """Save user registration info to Firestore with hashed password."""
    try:
        db = get_db()
        user_data = {
            "name": name,
            "email": email,
            "registered_at": datetime.now(),
        }
        if role:
            user_data["role"] = role
        
        # Hash password for security
        if password:
            user_data["password"] = generate_password_hash(password)
        
        db.collection("users").document(email).set(user_data, merge=True)
    except Exception as e:
        st.error(f"Error saving user info: {e}")


def verify_user(email: str, password: str = None) -> Optional[Dict]:
    """Verify user exists and password is correct."""
    try:
        db = get_db()
        user_doc = db.collection("users").document(email).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            
            # If password provided, verify it
            if password:
                stored_password = user_data.get("password")
                if stored_password and check_password_hash(stored_password, password):
                    return user_data
                else:
                    return None  # Password incorrect
            
            return user_data
        return None
    except Exception:
        return None


def save_assessment(email: str, answers: dict, score: int, risk_level: str) -> None:
    """Save completed assessment to Firestore.
    
    Public users are only allowed one assessment. If they have already
    completed one, this function silently returns without saving again.
    """
    try:
        db = get_db()

        # Enforce one-assessment limit for Public users
        user_doc = db.collection("users").document(email).get()
        if user_doc.exists:
            user_role = user_doc.to_dict().get("role", "Public")
            if user_role == "Public" and has_user_completed_assessment(email):
                st.warning("⚠️ You have already completed your assessment. Public users can only submit once.")
                return

        assessment_data = {
            "email": email,
            "answers": answers,
            "score": score,
            "risk_level": risk_level,
            "completed_at": datetime.now(),
        }
        db.collection("users").document(email).collection("assessments").add(assessment_data)
        st.success("Assessment saved!")
    except Exception as e:
        st.error(f"Error saving assessment: {e}")


def load_user_assessments(email: str) -> list:
    """Load all assessments for a user from Firestore."""
    try:
        db = get_db()
        assessments_query = db.collection("users").document(email).collection("assessments")
        docs = assessments_query.stream()
        assessments = [{"id": doc.id, **doc.to_dict()} for doc in docs]
        # Sort by completed_at in descending order
        assessments.sort(key=lambda x: x.get("completed_at", datetime.now()), reverse=True)
        return assessments
    except Exception:
        return []


def has_user_completed_assessment(email: str) -> bool:
    """Check if a user (public user) has already completed an assessment."""
    try:
        db = get_db()
        assessments = load_user_assessments(email)
        return len(assessments) > 0
    except Exception:
        return False


def get_user_latest_assessment(email: str) -> dict:
    """Get the latest assessment for a user, or None if no assessment exists."""
    try:
        assessments = load_user_assessments(email)
        return assessments[0] if assessments else None
    except Exception:
        return None


def update_user_role(email: str, role: str) -> bool:
    """Update user role in Firestore."""
    try:
        db = get_db()
        db.collection("users").document(email).update({
            "role": role
        })
        return True
    except Exception as e:
        st.error(f"Error updating user role: {e}")
        return False


def load_all_public_users() -> list:
    """Load all public users from Firestore."""
    try:
        db = get_db()
        users_query = db.collection("users").where("role", "==", "Public").stream()
        public_users = []
        for user_doc in users_query:
            user_data = user_doc.to_dict()
            user_data["email"] = user_doc.id
            public_users.append(user_data)
        return public_users
    except Exception:
        return []


def load_public_user_assessments(email: str) -> list:
    """Load all assessments for a public user from Firestore."""
    try:
        db = get_db()
        assessments_query = db.collection("users").document(email).collection("assessments")
        docs = assessments_query.stream()
        assessments = [{"id": doc.id, **doc.to_dict()} for doc in docs]
        assessments.sort(key=lambda x: x.get("completed_at", datetime.now()), reverse=True)
        return assessments
    except Exception:
        return []


def load_all_assessments_aggregated() -> list:
    """Load all assessments from all public users for doctor dashboard."""
    try:
        db = get_db()
        all_assessments = []
        
        # Get ALL users
        all_users = db.collection("users").stream()
        
        for user_doc in all_users:
            user_email = user_doc.id
            user_data = user_doc.to_dict()
            user_role = user_data.get("role", "Public")  # Default to Public if no role
            
            # Skip only "Doctor" role - include "Public" and users with no role
            if user_role != "Doctor":
                assessments_query = db.collection("users").document(user_email).collection("assessments").stream()
                
                for assessment_doc in assessments_query:
                    assessment_data = assessment_doc.to_dict()
                    assessment_data["user_email"] = user_email
                    assessment_data["user_name"] = user_data.get("name", "Unknown")
                    assessment_data["assessment_id"] = assessment_doc.id
                    all_assessments.append(assessment_data)
        
        all_assessments.sort(key=lambda x: x.get("completed_at", datetime.now()), reverse=True)
        return all_assessments
    except Exception:
        return []


# ═══════════════════════════════════════════════════════════════
# APPOINTMENT AND NOTIFICATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def generate_google_meet_link(appointment_id: str) -> str:
    """Generate a Google Meet link for an appointment."""
    # Create a deterministic meeting ID based on appointment
    hash_input = f"breast_aid_{appointment_id}"
    hash_obj = hashlib.md5(hash_input.encode())
    meeting_id = hash_obj.hexdigest()[:12]  # Use first 12 chars
    
    # Format as Google Meet URL (using the meeting ID)
    # Note: This generates a URL format compatible with Google Meet
    return f"https://meet.google.com/{meeting_id}"


def request_appointment(public_email: str, public_name: str, appointment_type: str = "ftf") -> bool:
    """Request appointment - creates notification for admin."""
    try:
        db = get_db()
        
        # Create appointment request
        appointment_data = {
            "public_email": public_email,
            "public_name": public_name,
            "appointment_type": appointment_type,  # "ftf" or "online"
            "requested_at": datetime.now(),
            "status": "pending",  # pending, scheduled, confirmed, completed, cancelled
            "appointment_date": None,
            "appointment_time": None,
            "doctor_email": None,
            "doctor_name": None,
            "public_accepted": None,
            "doctor_accepted": None,
            "meeting_link": None,
        }
        
        apt_ref = db.collection("appointments").add(appointment_data)
        appointment_id = apt_ref[1].id
        
        # Create notification for admin
        apt_type_display = "Online Consultation" if appointment_type == "online" else "Face-to-Face"
        create_notification(
            recipient_email="admin@gmail.com",
            recipient_role="Admin",
            notification_type="appointment_request",
            message=f"New {apt_type_display} appointment request from {public_name} ({public_email})",
            related_id=appointment_id
        )
        
        return True
    except Exception as e:
        st.error(f"Error requesting appointment: {e}")
        return False


def get_all_appointments() -> list:
    """Get all appointments for admin."""
    try:
        db = get_db()
        appointments = []
        docs = db.collection("appointments").stream()
        for doc in docs:
            apt = doc.to_dict()
            apt["id"] = doc.id
            appointments.append(apt)
        
        appointments.sort(key=lambda x: x.get("requested_at", datetime.now()), reverse=True)
        return appointments
    except Exception:
        return []


def get_user_appointments(email: str) -> list:
    """Get appointments for a specific user (public or doctor)."""
    try:
        db = get_db()
        appointments = []
        
        # Get as public user
        public_apts = db.collection("appointments").where("public_email", "==", email).stream()
        for doc in public_apts:
            apt = doc.to_dict()
            apt["id"] = doc.id
            appointments.append(apt)
        
        # Get as doctor
        doctor_apts = db.collection("appointments").where("doctor_email", "==", email).stream()
        for doc in doctor_apts:
            apt = doc.to_dict()
            apt["id"] = doc.id
            if apt not in appointments:
                appointments.append(apt)
        
        appointments.sort(key=lambda x: x.get("requested_at", datetime.now()), reverse=True)
        return appointments
    except Exception:
        return []


def schedule_appointment(appointment_id: str, doctor_email: str, doctor_name: str, appointment_date: str, appointment_time: str) -> bool:
    """Admin schedules appointment with specific doctor."""
    try:
        db = get_db()
        
        # Get appointment to check type
        apt_doc = db.collection("appointments").document(appointment_id).get()
        if not apt_doc.exists:
            st.error(f"❌ Appointment not found. ID: {appointment_id}")
            return False
        
        apt = apt_doc.to_dict()
        appointment_type = apt.get("appointment_type", "ftf")
        
        # Generate meeting link if online
        meeting_link = None
        if appointment_type == "online":
            meeting_link = generate_google_meet_link(appointment_id)
        
        # Update appointment
        update_data = {
            "doctor_email": doctor_email,
            "doctor_name": doctor_name,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "status": "scheduled",
            "meeting_link": meeting_link,
        }
        
        db.collection("appointments").document(appointment_id).update(update_data)
        
        # Build notification messages
        apt_type_display = "Online Consultation" if appointment_type == "online" else "Face-to-Face Appointment"
        meeting_info = f"\n\n🔗 Meeting Link: {meeting_link}" if meeting_link else ""
        
        # Notify doctor
        doctor_msg = f"{apt_type_display} scheduled with {apt['public_name']} on {appointment_date} at {appointment_time}. Please accept or decline.{meeting_info}"
        create_notification(
            recipient_email=doctor_email,
            recipient_role="Doctor",
            notification_type="appointment_scheduled",
            message=doctor_msg,
            related_id=appointment_id
        )
        
        # Notify public user
        public_msg = f"Your {apt_type_display.lower()} has been scheduled with Dr. {doctor_name} on {appointment_date} at {appointment_time}. Please accept or decline.{meeting_info}"
        create_notification(
            recipient_email=apt['public_email'],
            recipient_role="Public",
            notification_type="appointment_scheduled",
            message=public_msg,
            related_id=appointment_id
        )
        
        return True
    except Exception as e:
        st.error(f"Error scheduling appointment: {e}")
        return False


def accept_appointment(appointment_id: str, user_email: str, user_role: str) -> bool:
    """User (public or doctor) accepts appointment."""
    try:
        db = get_db()
        
        # First verify the appointment exists
        apt_doc = db.collection("appointments").document(appointment_id).get()
        if not apt_doc.exists:
            st.error(f"❌ Appointment not found. ID: {appointment_id}")
            return False
        
        apt = apt_doc.to_dict()
        
        # Update the acceptance status
        update_data = {}
        if user_role == "Public":
            update_data["public_accepted"] = True
        elif user_role == "Doctor":
            update_data["doctor_accepted"] = True
        else:
            st.error(f"❌ Invalid user role: {user_role}")
            return False
        
        db.collection("appointments").document(appointment_id).update(update_data)
        
        # Re-fetch to check if both have accepted
        apt_doc = db.collection("appointments").document(appointment_id).get()
        apt = apt_doc.to_dict()
        
        if apt.get("public_accepted") and apt.get("doctor_accepted"):
            db.collection("appointments").document(appointment_id).update({"status": "confirmed"})
            
            # Build confirmation message with meeting link if applicable
            appointment_type = apt.get("appointment_type", "ftf")
            apt_type_display = "Online Consultation" if appointment_type == "online" else "Face-to-Face Appointment"
            meeting_info = f"\n\n🔗 Meeting Link: {apt.get('meeting_link')}" if apt.get("meeting_link") else ""
            
            # Notify admin of confirmation
            create_notification(
                recipient_email="admin@gmail.com",
                recipient_role="Admin",
                notification_type="appointment_confirmed",
                message=f"{apt_type_display} confirmed between {apt['public_name']} and Dr. {apt['doctor_name']} on {apt.get('appointment_date')} at {apt.get('appointment_time')}.{meeting_info}",
                related_id=appointment_id
            )
        
        return True
    except Exception as e:
        st.error(f"Error accepting appointment: {e}")
        return False


def decline_appointment(appointment_id: str, user_email: str, user_role: str) -> bool:
    """User (public or doctor) declines appointment."""
    try:
        db = get_db()
        
        # Get appointment details - verify it exists first
        apt_doc = db.collection("appointments").document(appointment_id).get()
        if not apt_doc.exists:
            st.error(f"❌ Appointment not found. ID: {appointment_id}")
            return False
        
        apt = apt_doc.to_dict()
        if not apt:
            st.error("❌ Could not read appointment data")
            return False
        
        # Notify admin of decline
        decliner_name = apt.get('public_name') if user_role == "Public" else apt.get('doctor_name')
        create_notification(
            recipient_email="admin@gmail.com",
            recipient_role="Admin",
            notification_type="appointment_declined",
            message=f"Appointment declined by {decliner_name}. Please reschedule.",
            related_id=appointment_id
        )
        
        # Set status to needs rescheduling
        update_data = {
            "status": "needs_reschedule"
        }
        if user_role == "Public":
            update_data["public_accepted"] = False
        elif user_role == "Doctor":
            update_data["doctor_accepted"] = False
        else:
            st.error(f"❌ Invalid user role: {user_role}")
            return False
        
        db.collection("appointments").document(appointment_id).update(update_data)
        
        return True
    except Exception as e:
        st.error(f"Error declining appointment: {e}")
        return False


def create_notification(recipient_email: str, recipient_role: str, notification_type: str, message: str, related_id: str = None) -> bool:
    """Create a notification for a user."""
    try:
        db = get_db()
        
        notification_data = {
            "recipient_email": recipient_email,
            "recipient_role": recipient_role,
            "notification_type": notification_type,
            "message": message,
            "read": False,
            "created_at": datetime.now(),
            "related_id": related_id,
        }
        
        db.collection("notifications").add(notification_data)
        return True
    except Exception as e:
        st.error(f"Error creating notification: {e}")
        return False


def get_user_notifications(email: str, unread_only: bool = False) -> list:
    """Get notifications for a user."""
    try:
        db = get_db()
        
        query = db.collection("notifications").where("recipient_email", "==", email)
        
        if unread_only:
            query = query.where("read", "==", False)
        
        notifications = []
        docs = query.stream()
        for doc in docs:
            notif = doc.to_dict()
            notif["id"] = doc.id
            notifications.append(notif)
        
        notifications.sort(key=lambda x: x.get("created_at", datetime.now()), reverse=True)
        return notifications
    except Exception:
        return []


def get_unread_notification_count(email: str) -> int:
    """Get count of unread notifications."""
    try:
        db = get_db()
        notifications = db.collection("notifications").where("recipient_email", "==", email).where("read", "==", False).stream()
        return len(list(notifications))
    except Exception:
        return 0


def mark_notification_as_read(notification_id: str) -> bool:
    """Mark a notification as read."""
    try:
        db = get_db()
        db.collection("notifications").document(notification_id).update({
            "read": True
        })
        return True
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════
# CHAT SYSTEM FUNCTIONS (Real-time messaging)
# ═══════════════════════════════════════════════════════════════

def send_chat_message(conversation_id: str, sender_email: str, sender_name: str, 
                      sender_role: str, content: str, recipient_email: str, 
                      message_type: str = "text") -> bool:
    """Send a chat message to a conversation."""
    try:
        db = get_db()
        message_data = {
            "conversation_id": conversation_id,
            "sender_email": sender_email,
            "sender_name": sender_name,
            "sender_role": sender_role,
            "recipient_email": recipient_email,
            "content": content,
            "message_type": message_type,
            "timestamp": datetime.now(),
            "read": False,
        }
        
        db.collection("conversations").document(conversation_id).collection("messages").add(message_data)
        
        # Update conversation metadata
        db.collection("conversations").document(conversation_id).set({
            "last_message": content,
            "last_message_time": datetime.now(),
            "participants": [sender_email, recipient_email],
            "updated_at": datetime.now(),
        }, merge=True)
        
        return True
    except Exception as e:
        st.error(f"Error sending message: {e}")
        return False


def get_chat_messages(conversation_id: str) -> list:
    """Get all messages in a conversation."""
    try:
        db = get_db()
        messages = []
        docs = db.collection("conversations").document(conversation_id).collection("messages").stream()
        
        for doc in docs:
            message = doc.to_dict()
            message["id"] = doc.id
            messages.append(message)
        
        # Sort by timestamp
        messages.sort(key=lambda x: x.get("timestamp", datetime.now()))
        return messages
    except Exception:
        return []


def get_chat_participants(user_email: str, user_role: str) -> list:
    """Get list of people user can chat with based on role."""
    try:
        db = get_db()
        participants = []
        
        if user_role == "Admin":
            # Admin can chat with doctors
            doctors = db.collection("users").where("role", "==", "Doctor").stream()
            for doc in doctors:
                doctor_data = doc.to_dict()
                participants.append({
                    "email": doc.id,
                    "name": doctor_data.get("name", "Unknown"),
                    "role": "Doctor"
                })
        
        elif user_role == "Doctor":
            # Doctor can chat with admin
            participants.append({
                "email": "admin@gmail.com",
                "name": "Admin",
                "role": "Admin"
            })
            
            # Doctor can chat with assigned patients (approved appointments)
            apts = db.collection("appointments").where("doctor_email", "==", user_email)\
                .where("status", "==", "confirmed").stream()
            for apt_doc in apts:
                apt = apt_doc.to_dict()
                participants.append({
                    "email": apt.get("public_email"),
                    "name": apt.get("public_name", "Unknown"),
                    "role": "Patient"
                })
        
        else:  # Public/Patient
            # Patient can chat with assigned doctor (if approved)
            apts = db.collection("appointments").where("public_email", "==", user_email)\
                .where("status", "==", "confirmed").stream()
            for apt_doc in apts:
                apt = apt_doc.to_dict()
                if apt.get("doctor_email"):
                    participants.append({
                        "email": apt.get("doctor_email"),
                        "name": apt.get("doctor_name", "Unknown"),
                        "role": "Doctor"
                    })
        
        return participants
    except Exception:
        return []


def get_pending_appointments() -> list:
    """Get all pending appointment requests for admin."""
    try:
        db = get_db()
        appointments = []
        docs = db.collection("appointments").where("status", "==", "pending").stream()
        
        for doc in docs:
            apt = doc.to_dict()
            apt["id"] = doc.id
            appointments.append(apt)
        
        appointments.sort(key=lambda x: x.get("requested_at", datetime.now()), reverse=True)
        return appointments
    except Exception:
        return []


def approve_appointment_chat(appointment_id: str, user_email: str, user_name: str, 
                             user_role: str, conversation_id: str) -> bool:
    """Approve appointment and send chat message."""
    try:
        db = get_db()
        
        apt_doc = db.collection("appointments").document(appointment_id).get()
        if not apt_doc.exists:
            return False
        
        apt = apt_doc.to_dict()
        
        if user_role == "Admin":
            # Admin message: ready to assign doctor
            message = f"✅ Appointment request from {apt['public_name']} has been approved. Awaiting doctor assignment."
            
            db.collection("appointments").document(appointment_id).update({
                "status": "admin_approved",
                "admin_email": user_email,
            })
        
        else:  # Doctor
            # Doctor approves appointment
            message = f"✅ Dr. {user_name} has approved your appointment. Consultation confirmed!"
            apt_type_display = "Online Consultation" if apt.get("appointment_type") == "online" else "Face-to-Face"
            
            db.collection("appointments").document(appointment_id).update({
                "status": "confirmed",
                "doctor_accepted": True,
            })
            
            # Generate meeting link for online
            if apt.get("appointment_type") == "online":
                meeting_link = generate_google_meet_link(appointment_id)
                db.collection("appointments").document(appointment_id).update({
                    "meeting_link": meeting_link
                })
                message += f"\n\n🔗 Meeting Link: {meeting_link}"
        
        # Send chat message
        send_chat_message(
            conversation_id=conversation_id,
            sender_email=user_email,
            sender_name=user_name,
            sender_role=user_role,
            content=message,
            recipient_email=apt.get("public_email") if user_role == "Doctor" else apt.get("doctor_email"),
            message_type="approval"
        )
        
        return True
    except Exception as e:
        st.error(f"Error approving appointment: {e}")
        return False


def decline_appointment_chat(appointment_id: str, user_email: str, user_name: str, 
                            user_role: str, conversation_id: str) -> bool:
    """Decline appointment and send chat message."""
    try:
        db = get_db()
        
        apt_doc = db.collection("appointments").document(appointment_id).get()
        if not apt_doc.exists:
            return False
        
        apt = apt_doc.to_dict()
        message = f"❌ Dr. {user_name} has declined the appointment. Please request a new time or contact admin."
        
        db.collection("appointments").document(appointment_id).update({
            "status": "declined",
            "doctor_accepted": False,
        })
        
        # Send chat message
        send_chat_message(
            conversation_id=conversation_id,
            sender_email=user_email,
            sender_name=user_name,
            sender_role=user_role,
            content=message,
            recipient_email=apt.get("public_email"),
            message_type="decline"
        )
        
        return True
    except Exception as e:
        st.error(f"Error declining appointment: {e}")
        return False


def get_doctor_approved_appointments(doctor_email: str) -> list:
    """Get confirmed/approved appointments for a doctor."""
    try:
        db = get_db()
        appointments = []
        docs = db.collection("appointments").where("doctor_email", "==", doctor_email)\
            .where("status", "==", "confirmed").stream()
        
        for doc in docs:
            apt = doc.to_dict()
            apt["id"] = doc.id
            appointments.append(apt)
        
        return appointments
    except Exception:
        return []


def get_patient_approved_appointments(patient_email: str) -> list:
    """Get confirmed/approved appointments for a patient."""
    try:
        db = get_db()
        appointments = []
        docs = db.collection("appointments").where("public_email", "==", patient_email)\
            .where("status", "==", "confirmed").stream()
        
        for doc in docs:
            apt = doc.to_dict()
            apt["id"] = doc.id
            appointments.append(apt)
        
        return appointments
    except Exception:
        return []


def load_all_doctors() -> list:
    """Load all doctors from database."""
    try:
        db = get_db()
        doctors = []
        docs = db.collection("users").where("role", "==", "Doctor").stream()
        
        for doc in docs:
            doctor_data = doc.to_dict()
            doctor_data["email"] = doc.id
            doctors.append(doctor_data)
        
        return doctors
    except Exception:
        return []


# ═══════════════════════════════════════════════════════════════
# PROFILE MANAGEMENT FUNCTIONS (VIEW, UPDATE)
# ═══════════════════════════════════════════════════════════════

def get_user_profile(email: str) -> Optional[Dict]:
    """Get complete user profile information."""
    try:
        db = get_db()
        user_doc = db.collection("users").document(email).get()
        if user_doc.exists:
            profile = user_doc.to_dict()
            profile["email"] = email
            return profile
        return None
    except Exception as e:
        st.error(f"Error fetching profile: {e}")
        return None


def update_user_profile(email: str, update_data: Dict) -> bool:
    """Update user profile with new information."""
    try:
        db = get_db()
        
        # Handle password separately if provided (needs hashing)
        if "password" in update_data and update_data["password"]:
            raw_password = update_data.pop("password")
            if len(raw_password) >= 6:
                update_data["password"] = generate_password_hash(raw_password)
            else:
                st.error("Password must be at least 6 characters long")
                return False
        
        # Add updated timestamp
        update_data["updated_at"] = datetime.now()
        
        db.collection("users").document(email).update(update_data)
        return True
    except Exception as e:
        st.error(f"Error updating profile: {e}")
        return False


def change_user_password(email: str, current_password: str, new_password: str) -> bool:
    """Change user password after verifying current password."""
    try:
        # Verify current password
        user_data = verify_user(email, current_password)
        if not user_data:
            st.error("Current password is incorrect")
            return False
        
        if len(new_password) < 6:
            st.error("New password must be at least 6 characters long")
            return False
        
        # Update with new password
        db = get_db()
        hashed_password = generate_password_hash(new_password)
        db.collection("users").document(email).update({
            "password": hashed_password,
            "updated_at": datetime.now()
        })
        
        return True
    except Exception as e:
        st.error(f"Error changing password: {e}")
        return False


def update_user_email(old_email: str, new_email: str, password: str) -> bool:
    """Change user email address after password verification."""
    try:
        # Verify password
        user_data = verify_user(old_email, password)
        if not user_data:
            st.error("Password is incorrect")
            return False
        
        # Check if new email already exists
        existing_user = verify_user(new_email)
        if existing_user:
            st.error("Email already in use")
            return False
        
        db = get_db()
        
        # Copy user data to new email document
        user_data["email"] = new_email
        user_data["updated_at"] = datetime.now()
        db.collection("users").document(new_email).set(user_data)
        
        # Delete old email document
        db.collection("users").document(old_email).delete()
        
        return True
    except Exception as e:
        st.error(f"Error changing email: {e}")
        return False


# ═══════════════════════════════════════════════════════════════
# CONSULTATION NOTES FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def save_consultation_notes(appointment_id: str, doctor_email: str, doctor_name: str,
                           patient_email: str, patient_name: str, notes_content: str) -> bool:
    """Save consultation notes after a consultation is completed."""
    try:
        db = get_db()
        
        consultation_data = {
            "appointment_id": appointment_id,
            "doctor_email": doctor_email,
            "doctor_name": doctor_name,
            "patient_email": patient_email,
            "patient_name": patient_name,
            "notes": notes_content,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        
        # Save in a new collection
        db.collection("consultation_notes").add(consultation_data)
        
        # Mark appointment as completed
        db.collection("appointments").document(appointment_id).update({
            "status": "completed",
            "completed_at": datetime.now(),
            "has_notes": True
        })
        
        return True
    except Exception as e:
        st.error(f"Error saving consultation notes: {e}")
        return False


def get_consultation_notes_by_appointment(appointment_id: str) -> Optional[Dict]:
    """Get consultation notes for a specific appointment."""
    try:
        db = get_db()
        notes_query = db.collection("consultation_notes").where("appointment_id", "==", appointment_id).stream()
        
        for doc in notes_query:
            notes = doc.to_dict()
            notes["id"] = doc.id
            return notes
        
        return None
    except Exception:
        return None


def get_consultation_notes_for_doctor(doctor_email: str) -> list:
    """Get all consultation notes written by a doctor."""
    try:
        db = get_db()
        notes_list = []
        docs = db.collection("consultation_notes").where("doctor_email", "==", doctor_email).stream()
        
        for doc in docs:
            notes = doc.to_dict()
            notes["id"] = doc.id
            notes_list.append(notes)
        
        # Sort by created_at in descending order
        notes_list.sort(key=lambda x: x.get("created_at", datetime.now()), reverse=True)
        return notes_list
    except Exception:
        return []


def get_consultation_notes_for_patient(patient_email: str) -> list:
    """Get all consultation notes for a patient (visible to both doctor and patient)."""
    try:
        db = get_db()
        notes_list = []
        docs = db.collection("consultation_notes").where("patient_email", "==", patient_email).stream()
        
        for doc in docs:
            notes = doc.to_dict()
            notes["id"] = doc.id
            notes_list.append(notes)
        
        # Sort by created_at in descending order
        notes_list.sort(key=lambda x: x.get("created_at", datetime.now()), reverse=True)
        return notes_list
    except Exception:
        return []


def get_all_consultation_notes() -> list:
    """Get all consultation notes (for admin view)."""
    try:
        db = get_db()
        notes_list = []
        docs = db.collection("consultation_notes").stream()
        
        for doc in docs:
            notes = doc.to_dict()
            notes["id"] = doc.id
            notes_list.append(notes)
        
        # Sort by created_at in descending order
        notes_list.sort(key=lambda x: x.get("created_at", datetime.now()), reverse=True)
        return notes_list
    except Exception:
        return []


def update_consultation_notes(notes_id: str, updated_notes_content: str) -> bool:
    """Update consultation notes (only doctor can do this)."""
    try:
        db = get_db()
        db.collection("consultation_notes").document(notes_id).update({
            "notes": updated_notes_content,
            "updated_at": datetime.now()
        })
        return True
    except Exception as e:
        st.error(f"Error updating consultation notes: {e}")
        return False