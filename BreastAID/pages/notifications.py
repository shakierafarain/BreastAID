"""Notifications page for viewing appointment notifications."""
import streamlit as st
from datetime import datetime
from utils.firebase_helper import (
    get_user_notifications,
    accept_appointment,
    request_reschedule_appointment,
    get_user_appointments,
    mark_notification_as_read,
)
from utils.navigation import show_sidebar


def show_notifications_page():
    """Display notifications page."""
    show_sidebar()
    
    st.markdown(
        """
        <style>
            .notification-card {
                background: white;
                border-left: 4px solid #ff1493;
                padding: 1.5rem;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                margin-bottom: 1rem;
            }
            
            .notification-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 0.5rem;
            }
            
            .notification-type {
                font-size: 0.85rem;
                color: #888;
                font-weight: 600;
                text-transform: uppercase;
            }
            
            .notification-time {
                font-size: 0.8rem;
                color: #aaa;
            }
            
            .notification-message {
                font-size: 1rem;
                color: #333;
                margin-bottom: 0.75rem;
                line-height: 1.5;
            }
            
            .unread-badge {
                display: inline-block;
                background: #ff1493;
                color: white;
                font-size: 0.7rem;
                padding: 0.2rem 0.5rem;
                border-radius: 12px;
                font-weight: 700;
                margin-right: 0.5rem;
            }
            
            .empty-state {
                text-align: center;
                padding: 2rem;
                color: #888;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("📬 Notifications")

    def action_feedback(action: str, detail: str = ""):
        if detail:
            st.success(f"✅ {action}. {detail}")
        else:
            st.success(f"✅ {action}")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        pass
    with col2:
        if st.button("← Back to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
    
    # Get notifications
    notifications = get_user_notifications(st.session_state.user_email)
    
    if not notifications:
        st.markdown(
            '<div class="empty-state"><p>No notifications yet</p></div>',
            unsafe_allow_html=True,
        )
        return
    
    # Mark all unread notifications as read
    for notif in notifications:
        if not notif.get("read"):
            mark_notification_as_read(notif["id"])
            notif["read"] = True  # Update in-memory to reflect the change
    
    # Display notifications
    for notif in notifications:
        with st.container():
            unread_badge = '<span class="unread-badge">NEW</span>' if not notif.get("read") else ""
            
            notif_type = notif.get("notification_type", "").replace("_", " ").title()
            created_at = notif.get("created_at")
            if isinstance(created_at, datetime):
                time_str = created_at.strftime("%b %d, %I:%M %p")
            else:
                time_str = "Recently"
            
            st.markdown(
                f"""
                <div class="notification-card">
                    <div class="notification-header">
                        <span>{unread_badge}<span class="notification-type">{notif_type}</span></span>
                        <span class="notification-time">{time_str}</span>
                    </div>
                    <div class="notification-message">{notif.get("message", "")}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            # Show action buttons based on notification type
            notif_type_key = notif.get("notification_type")
            
            if notif_type_key == "appointment_scheduled":
                apt_id = notif.get("related_id")
                user_role = st.session_state.get("user_role", "Public")
                appointments = get_user_appointments(st.session_state.user_email)
                apt = next((a for a in appointments if a.get("id") == apt_id), None)
                
                # Use persisted Firestore acceptance flags so the action only appears once.
                if user_role == "Doctor":
                    st.markdown("**Action Required:** Please accept this appointment")
                    if apt and apt.get("doctor_accepted"):
                        st.success("✅ Appointment accepted. You can now chat with your assigned patient.")
                    else:
                        if st.button("✅ Accept Appointment", key=f"accept_{notif['id']}", use_container_width=True):
                            if apt_id:
                                if accept_appointment(apt_id, st.session_state.user_email, st.session_state.user_role):
                                    action_feedback("Appointment accepted", "You can now chat with your assigned patient.")
                                    st.rerun()
                            else:
                                st.error("❌ Missing appointment ID in notification - Contact admin")

                elif apt and apt.get("public_accepted"):
                    st.success("✅ Appointment accepted. You can now chat with your assigned doctor/patient.")
                else:
                    st.markdown("**Action Required:** Please accept or request a reschedule")
                    col_accept, col_reschedule = st.columns(2)
                    
                    with col_accept:
                        if st.button("✅ Accept Appointment", key=f"accept_{notif['id']}", use_container_width=True):
                            if apt_id:
                                if accept_appointment(apt_id, st.session_state.user_email, st.session_state.user_role):
                                    action_feedback("Appointment accepted", "You can now chat with your assigned doctor.")
                                    st.rerun()
                            else:
                                st.error("❌ Missing appointment ID in notification - Contact admin")
                    
                    if user_role == "Public":
                        with col_reschedule:
                            if st.button("📞 Request Reschedule", key=f"reschedule_{notif['id']}", use_container_width=True):
                                if apt_id:
                                    if request_reschedule_appointment(apt_id, st.session_state.user_email, st.session_state.user_role):
                                        action_feedback("Reschedule requested", "Admin will contact you soon to reschedule.")
                                        st.rerun()
                                else:
                                    st.error("❌ Missing appointment ID in notification - Contact admin")
            
            elif notif_type_key == "appointment_confirmed":
                st.success("✅ Appointment confirmed. Consultation is ready.")
                
                # Get appointment details to check if it's online and show meeting link
                apt_id = notif.get("related_id")
                if apt_id:
                    try:
                        appointments = get_user_appointments(st.session_state.user_email)
                        apt = next((a for a in appointments if a.get("id") == apt_id), None)
                        
                        if apt and apt.get("appointment_type") == "online" and apt.get("meeting_link"):
                            st.info(f"🎥 **Online Meeting**\n\nJoin Link: `{apt.get('meeting_link')}`")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button(f"🔗 Join Meeting", key=f"join_{apt_id}", use_container_width=True):
                                    st.markdown(f"[Click here to join the meeting]({apt.get('meeting_link')})", unsafe_allow_html=True)
                            
                            with col2:
                                if st.button(f"📋 Copy Link", key=f"copy_{apt_id}", use_container_width=True):
                                    st.success(f"Link copied: {apt.get('meeting_link')}")
                    except Exception as e:
                        pass
            
            elif notif_type_key == "appointment_reschedule_requested":
                st.warning("⚠️ Reschedule request sent to admin. Waiting for a new appointment time.")
            elif notif_type_key == "appointment_declined":
                st.warning("⚠️ Appointment was declined - reschedule in progress")
            
            st.divider()