"""Chat system for notifications, approvals, and communication."""
import streamlit as st
from datetime import datetime
from utils.firebase_helper import (
    send_chat_message,
    get_chat_messages,
    get_chat_participants,
    approve_appointment_chat,
    decline_appointment_chat,
    get_pending_appointments,
)
from utils.navigation import show_sidebar


def show_chat_page():
    """Display chat page with role-specific conversations."""
    show_sidebar()
    
    st.title("💬 Messages & Notifications")
    
    user_email = st.session_state.get("user_email")
    user_role = st.session_state.get("user_role", "Public")
    user_name = st.session_state.get("user_name", "User")
    
    if not user_email:
        st.error("❌ Please log in first")
        return
    
    # Back button
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("← Back"):
            st.session_state.page = "dashboard"
            st.rerun()
    
    st.divider()
    
    # ═══════════════════════════════════════════════════════════════
    # ADMIN VIEW
    # ═══════════════════════════════════════════════════════════════
    if user_role == "Admin":
        st.subheader("👨‍💼 Doctor Conversations")
        
        # Get pending appointments for doctor assignment
        pending_apts = get_pending_appointments()
        
        if pending_apts:
            st.markdown("### 📋 Pending Appointment Requests")
            for apt in pending_apts:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"""
                        **Patient:** {apt.get('public_name', 'Unknown')}  
                        **Email:** {apt.get('public_email')}  
                        **Type:** {'Online' if apt.get('appointment_type') == 'online' else 'Face-to-Face'}  
                        **Status:** {apt.get('status').upper()}
                        """)
                    with col2:
                        if st.button("💬 Assign & Chat", key=f"assign_{apt['id']}"):
                            st.session_state.selected_conversation = {
                                "type": "appointment_request",
                                "appointment_id": apt["id"],
                                "public_email": apt["public_email"],
                                "public_name": apt["public_name"],
                                # participant_email/name required by the chat window & send_chat_message
                                "participant_email": apt["public_email"],
                                "participant_name": apt["public_name"],
                            }
                            st.rerun()
                    st.divider()
        
        # Doctor list for general chat
        st.markdown("### 👨‍⚕️ Doctors")
        
        # Get all doctors
        from utils.firebase_helper import load_all_doctors
        doctors = load_all_doctors()
        
        if doctors:
            for idx, doctor in enumerate(doctors):
                doctor_email = doctor.get("email")
                doctor_name = doctor.get("name", "Unknown")
                
                if st.button(f"💬 {doctor_name}", key=f"admin_doctor_{idx}_{doctor_email}"):
                    st.session_state.selected_conversation = {
                        "type": "admin_doctor",
                        "participant_email": doctor_email,
                        "participant_name": doctor_name,
                    }
                    st.rerun()
        else:
            st.info("No doctors available")
    
    # ═══════════════════════════════════════════════════════════════
    # DOCTOR VIEW
    # ═══════════════════════════════════════════════════════════════
    elif user_role == "Doctor":
        st.subheader("👨‍⚕️ Doctor Communications")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📬 Admin Messages")
            if st.button("💬 Chat with Admin", key="chat_admin"):
                st.session_state.selected_conversation = {
                    "type": "doctor_admin",
                    "participant_email": "admin@gmail.com",
                    "participant_name": "Admin",
                }
                st.rerun()
        
        with col2:
            st.markdown("### 👥 Patient Conversations")
            # Get approved appointments with patients
            from utils.firebase_helper import get_doctor_approved_appointments
            approved_apts = get_doctor_approved_appointments(user_email)
            
            if approved_apts:
                for apt in approved_apts:
                    patient_email = apt.get("public_email")
                    patient_name = apt.get("public_name", "Unknown")
                    
                    if st.button(f"💬 {patient_name}", key=f"patient_{apt['id']}"):
                        st.session_state.selected_conversation = {
                            "type": "doctor_patient",
                            "participant_email": patient_email,
                            "participant_name": patient_name,
                            "appointment_id": apt["id"],
                        }
                        st.rerun()
            else:
                st.info("No approved appointments yet")
    
    # ═══════════════════════════════════════════════════════════════
    # PUBLIC/PATIENT VIEW
    # ═══════════════════════════════════════════════════════════════
    else:  # Public/Patient
        st.subheader("👤 Your Conversations")
        
        # Get approved appointments with doctors
        from utils.firebase_helper import get_patient_approved_appointments
        approved_apts = get_patient_approved_appointments(user_email)
        
        if approved_apts:
            st.markdown("### 👨‍⚕️ Your Doctors")
            for apt in approved_apts:
                doctor_email = apt.get("doctor_email")
                doctor_name = apt.get("doctor_name", "Unknown")
                
                if doctor_email:  # Only show if doctor assigned
                    if st.button(f"💬 {doctor_name}", key=f"doctor_{apt['id']}"):
                        st.session_state.selected_conversation = {
                            "type": "patient_doctor",
                            "participant_email": doctor_email,
                            "participant_name": doctor_name,
                            "appointment_id": apt["id"],
                        }
                        st.rerun()
        else:
            st.info("👋 No approved appointments yet. Once a doctor approves your appointment, you can chat with them here!")
    
    st.divider()
    
    # ═══════════════════════════════════════════════════════════════
    # CHAT WINDOW
    # ═══════════════════════════════════════════════════════════════
    if "selected_conversation" in st.session_state:
        conv = st.session_state.selected_conversation
        participant_name = conv.get("participant_name", "User")
        participant_email = conv.get("participant_email", "")
        
        st.markdown(f"### 💬 Chat with {participant_name}")
        
        # Create unique conversation ID
        conv_type = conv.get("type")
        if conv_type == "appointment_request":
            conv_id = f"admin_apt_{conv['appointment_id']}"
        else:
            # Sort emails to create consistent conversation ID
            emails = sorted([user_email, participant_email])
            conv_id = f"{emails[0]}_{emails[1]}"
        
        # Display messages
        messages = get_chat_messages(conv_id)
        
        if messages:
            for msg in messages:
                sender_name = msg.get("sender_name", "Unknown")
                sender_role = msg.get("sender_role", "")
                content = msg.get("content", "")
                timestamp = msg.get("timestamp")
                msg_type = msg.get("message_type", "text")
                
                if isinstance(timestamp, datetime):
                    time_str = timestamp.strftime("%I:%M %p")
                else:
                    time_str = "Recently"
                
                # Determine if message is from current user
                is_own_message = msg.get("sender_email") == user_email
                
                # Style message based on sender
                if is_own_message:
                    st.markdown(f"""
                    <div style="text-align: right; margin: 0.5rem 0;">
                        <div style="display: inline-block; background: #ff1493; color: white; padding: 0.8rem; border-radius: 10px; max-width: 70%; text-align: left;">
                            <strong>{sender_name}</strong> ({sender_role})<br>
                            {content}
                            <br><small style="opacity: 0.8;">{time_str}</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="text-align: left; margin: 0.5rem 0;">
                        <div style="display: inline-block; background: #f0f0f0; color: #333; padding: 0.8rem; border-radius: 10px; max-width: 70%;">
                            <strong>{sender_name}</strong> ({sender_role})<br>
                            {content}
                            <br><small style="opacity: 0.8;">{time_str}</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Show action buttons for appointment requests (Admin/Doctor)
                if msg_type == "appointment_request" and user_role in ["Admin", "Doctor"]:
                    apt_id = conv.get("appointment_id")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✅ Approve", key=f"approve_{apt_id}", use_container_width=True):
                            approve_appointment_chat(
                                apt_id,
                                user_email,
                                user_name,
                                user_role,
                                conv_id
                            )
                            st.success("✅ Appointment approved!")
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Decline", key=f"decline_{apt_id}", use_container_width=True):
                            decline_appointment_chat(
                                apt_id,
                                user_email,
                                user_name,
                                user_role,
                                conv_id
                            )
                            st.info("❌ Appointment declined")
                            st.rerun()
        
        # Message input
        st.divider()
        
        # Counter-based key forces a brand-new widget after each send,
        # which is the only safe way to clear a text_input in Streamlit.
        if "msg_send_count" not in st.session_state:
            st.session_state.msg_send_count = 0

        col1, col2 = st.columns([4, 1])

        with col1:
            message_input = st.text_input(
                "Type your message...",
                placeholder="Write your message here...",
                key=f"msg_input_{conv_id}_{st.session_state.msg_send_count}"
            )
        
        with col2:
            if st.button("📤 Send", use_container_width=True, key=f"send_btn_{conv_id}"):
                if message_input and message_input.strip():
                    success = send_chat_message(
                        conversation_id=conv_id,
                        sender_email=user_email,
                        sender_name=user_name,
                        sender_role=user_role,
                        content=message_input.strip(),
                        recipient_email=participant_email,
                        message_type="text"
                    )
                    if success:
                        # Increment counter → new widget key on next render → input is blank
                        st.session_state.msg_send_count += 1
                        st.rerun()
                    else:
                        st.error("❌ Failed to send message")
                else:
                    st.warning("⚠️ Please type a message")
        
        st.divider()
        
        # ═══════════════════════════════════════════════════════════════
        # END CONSULTATION & NOTES (Only for Doctor-Patient conversations)
        # ═══════════════════════════════════════════════════════════════
        if user_role == "Doctor" and conv.get("type") == "doctor_patient":
            st.markdown("### 📋 Consultation Complete?")
            
            if st.button("✅ End Consultation & Write Notes", use_container_width=True, key="end_consultation"):
                st.session_state.show_notes_modal = True
            
            # Modal for writing consultation notes
            if st.session_state.get("show_notes_modal"):
                st.markdown("---")
                st.markdown("### 📝 Write Consultation Notes")
                
                consultation_notes = st.text_area(
                    "Write your consultation notes here (observations, recommendations, diagnosis, follow-up required, etc.):",
                    height=300,
                    placeholder="Enter your detailed consultation notes...",
                    key="consultation_notes_input"
                )
                
                st.markdown("**Tips for good notes:**")
                st.markdown("""
                - Document patient's symptoms and complaints
                - Note your observations and findings
                - Include any test results or recommendations
                - Specify follow-up actions or referrals
                - Add any important medical history
                """)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("💾 Save & End Consultation", use_container_width=True, key="save_notes_btn"):
                        if consultation_notes.strip():
                            from utils.firebase_helper import save_consultation_notes
                            
                            appointment_id = conv.get("appointment_id", "unknown")
                            patient_email = participant_email
                            patient_name = participant_name
                            
                            if save_consultation_notes(
                                appointment_id=appointment_id,
                                doctor_email=user_email,
                                doctor_name=user_name,
                                patient_email=patient_email,
                                patient_name=patient_name,
                                notes_content=consultation_notes.strip()
                            ):
                                st.success("✅ Consultation completed! Notes saved successfully.")
                                st.session_state.show_notes_modal = False
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ Error saving consultation notes. Please try again.")
                        else:
                            st.warning("⚠️ Please enter consultation notes before saving.")
                
                with col2:
                    if st.button("❌ Cancel", use_container_width=True, key="cancel_notes_btn"):
                        st.session_state.show_notes_modal = False
                        st.rerun()
        
        st.divider()
        
        if st.button("← Back to Conversations"):
            del st.session_state.selected_conversation
            st.rerun()