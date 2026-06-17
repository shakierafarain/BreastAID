"""Consultation notes page - accessible to doctors, admins, and patients."""
import streamlit as st
from datetime import datetime
from utils.firebase_helper import (
    get_consultation_notes_by_appointment,
    get_consultation_notes_for_doctor,
    get_consultation_notes_for_patient,
    get_all_consultation_notes,
    get_user_appointments,
    update_consultation_notes,
)
from utils.navigation import show_sidebar


def show_consultation_notes_page():
    """Display consultation notes page with role-specific access."""
    show_sidebar()
    
    st.title("📋 Consultation Notes")
    
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
    # ADMIN VIEW - See all consultation notes
    # ═══════════════════════════════════════════════════════════════
    if user_role == "Admin":
        st.markdown("### 👥 All Consultation Notes")
        
        all_notes = get_all_consultation_notes()
        
        if all_notes:
            # Create tabs or filters
            col1, col2 = st.columns(2)
            
            with col1:
                search_patient = st.text_input("🔍 Search by patient name or email:", "")
            
            with col2:
                search_doctor = st.text_input("🔍 Search by doctor name or email:", "")
            
            st.divider()
            
            # Filter notes
            filtered_notes = all_notes
            if search_patient:
                filtered_notes = [n for n in filtered_notes if search_patient.lower() in (
                    n.get("patient_name", "").lower() + " " + 
                    n.get("patient_email", "").lower()
                )]
            
            if search_doctor:
                filtered_notes = [n for n in filtered_notes if search_doctor.lower() in (
                    n.get("doctor_name", "").lower() + " " + 
                    n.get("doctor_email", "").lower()
                )]
            
            if filtered_notes:
                for notes in filtered_notes:
                    with st.container():
                        # Header with patient and doctor info
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            st.markdown(f"""
                            <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px;">
                                <strong>👤 Patient</strong><br>
                                {notes.get('patient_name', 'Unknown')}<br>
                                <small>{notes.get('patient_email')}</small>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px;">
                                <strong>👨‍⚕️ Doctor</strong><br>
                                Dr. {notes.get('doctor_name', 'Unknown')}<br>
                                <small>{notes.get('doctor_email')}</small>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown(f"""
                            <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px;">
                                <strong>📅 Date</strong><br>
                                {notes.get('created_at').strftime('%b %d, %Y') if hasattr(notes.get('created_at'), 'strftime') else 'Recently'}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.divider()
                        
                        # Notes content
                        st.markdown(f"""
                        <div style="background: #fff3cd; padding: 1rem; border-left: 4px solid #ffc107; border-radius: 4px; margin: 1rem 0;">
                            <strong>📝 Notes:</strong><br><br>
                            {notes.get('notes', 'No notes provided').replace(chr(10), '<br>')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.divider()
            else:
                st.info("No consultation notes found matching your search.")
        else:
            st.info("📭 No consultation notes have been created yet.")
    
    # ═══════════════════════════════════════════════════════════════
    # DOCTOR VIEW - See and edit own notes
    # ═══════════════════════════════════════════════════════════════
    elif user_role == "Doctor":
        tab1, tab2 = st.tabs(["📋 My Notes", "👥 Patient Notes"])
        
        with tab1:
            st.markdown("### 📝 Consultation Notes I've Written")
            
            my_notes = get_consultation_notes_for_doctor(user_email)
            
            if my_notes:
                for notes in my_notes:
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"""
                            <div style="background: #e7f3ff; padding: 1rem; border-radius: 8px;">
                                <strong>👤 Patient:</strong> {notes.get('patient_name', 'Unknown')}<br>
                                <small>{notes.get('patient_email')}</small><br><br>
                                <strong>📅 Date:</strong> {notes.get('created_at').strftime('%b %d, %Y at %I:%M %p') if hasattr(notes.get('created_at'), 'strftime') else 'Recently'}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            if st.button("✏️ Edit", key=f"edit_{notes['id']}"):
                                st.session_state.editing_notes_id = notes['id']
                                st.rerun()
                        
                        st.divider()
                        
                        # Notes content
                        if st.session_state.get("editing_notes_id") == notes['id']:
                            st.markdown("**✏️ Edit Notes:**")
                            updated_content = st.text_area(
                                "Update consultation notes:",
                                value=notes.get('notes', ''),
                                height=200,
                                key=f"textarea_{notes['id']}"
                            )
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                if st.button("💾 Save", key=f"save_{notes['id']}", use_container_width=True):
                                    if update_consultation_notes(notes['id'], updated_content):
                                        st.success("✅ Notes updated successfully!")
                                        del st.session_state.editing_notes_id
                                        st.rerun()
                            
                            with col2:
                                if st.button("❌ Cancel", key=f"cancel_{notes['id']}", use_container_width=True):
                                    del st.session_state.editing_notes_id
                                    st.rerun()
                        else:
                            st.markdown(f"""
                            <div style="background: #fff3cd; padding: 1rem; border-left: 4px solid #ffc107; border-radius: 4px; margin: 1rem 0;">
                                <strong>📝 Notes:</strong><br><br>
                                {notes.get('notes', 'No notes provided').replace(chr(10), '<br>')}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.divider()
            else:
                st.info("📭 You haven't written any consultation notes yet.")
        
        with tab2:
            st.markdown("### 👥 All Patient Consultation Notes")
            st.info("View all consultation notes for patients you've consulted with.")
            
            # Get all appointments for this doctor
            from utils.firebase_helper import get_doctor_approved_appointments
            appointments = get_doctor_approved_appointments(user_email)
            
            if appointments:
                patient_notes_combined = []
                for apt in appointments:
                    patient_email = apt.get("public_email")
                    notes_list = get_consultation_notes_for_patient(patient_email)
                    
                    # Only show notes from this doctor
                    notes_list = [n for n in notes_list if n.get("doctor_email") == user_email]
                    patient_notes_combined.extend(notes_list)
                
                if patient_notes_combined:
                    for notes in patient_notes_combined:
                        with st.container():
                            st.markdown(f"""
                            <div style="background: #d4edda; padding: 1rem; border-radius: 8px;">
                                <strong>👤 Patient:</strong> {notes.get('patient_name', 'Unknown')}<br>
                                <strong>📅 Consultation Date:</strong> {notes.get('created_at').strftime('%b %d, %Y') if hasattr(notes.get('created_at'), 'strftime') else 'Recently'}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown(f"""
                            <div style="background: #fff3cd; padding: 1rem; border-left: 4px solid #ffc107; border-radius: 4px; margin: 1rem 0;">
                                {notes.get('notes', 'No notes provided').replace(chr(10), '<br>')}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.divider()
                else:
                    st.info("No consultation notes for your patients yet.")
            else:
                st.info("You don't have any confirmed appointments yet.")
    
    # ═══════════════════════════════════════════════════════════════
    # PATIENT/PUBLIC VIEW - See notes from their doctors
    # ═══════════════════════════════════════════════════════════════
    else:  # Public/Patient
        st.markdown("### 📋 Your Consultation Notes")
        
        patient_notes = get_consultation_notes_for_patient(user_email)
        
        if patient_notes:
            for notes in patient_notes:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div style="background: #d4edda; padding: 1rem; border-radius: 8px;">
                            <strong>👨‍⚕️ Doctor:</strong> Dr. {notes.get('doctor_name', 'Unknown')}<br>
                            <strong>📅 Consultation Date:</strong> {notes.get('created_at').strftime('%b %d, %Y at %I:%M %p') if hasattr(notes.get('created_at'), 'strftime') else 'Recently'}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div style="background: #d4edda; padding: 1rem; border-radius: 8px; text-align: center;">
                            <strong>✅ Completed</strong>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.divider()
                    
                    # Notes content
                    st.markdown(f"""
                    <div style="background: #fff3cd; padding: 1rem; border-left: 4px solid #ffc107; border-radius: 4px; margin: 1rem 0;">
                        <strong>📝 Doctor's Notes:</strong><br><br>
                        {notes.get('notes', 'No notes provided').replace(chr(10), '<br>')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.divider()
        else:
            st.info("👋 You don't have any consultation notes yet. They will appear here after your consultations are completed.")
