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

    def format_date(value, with_time: bool = False):
        if hasattr(value, "strftime"):
            return value.strftime("%b %d, %Y at %I:%M %p") if with_time else value.strftime("%b %d, %Y")
        return "Recently"

    def preview_notes(notes: str, length: int = 80) -> str:
        text = (notes or "No notes provided").replace("\n", " ").strip()
        return text[:length] + "..." if len(text) > length else text
    
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
                table_rows = []
                for notes in filtered_notes:
                    table_rows.append({
                        "Patient": f"{notes.get('patient_name', 'Unknown')} ({notes.get('patient_email', '')})",
                        "Doctor": f"Dr. {notes.get('doctor_name', 'Unknown')} ({notes.get('doctor_email', '')})",
                        "Date": format_date(notes.get('created_at')),
                        "Notes Preview": preview_notes(notes.get('notes', 'No notes provided')),
                    })

                st.dataframe(table_rows, use_container_width=True, hide_index=True)

                st.markdown("#### Full Notes")
                for notes in filtered_notes:
                    with st.expander(f"{notes.get('patient_name', 'Unknown')} - {format_date(notes.get('created_at'))}"):
                        st.write(f"Patient: {notes.get('patient_name', 'Unknown')} ({notes.get('patient_email', 'N/A')})")
                        st.write(f"Doctor: Dr. {notes.get('doctor_name', 'Unknown')} ({notes.get('doctor_email', 'N/A')})")
                        st.write(f"Date: {format_date(notes.get('created_at'), with_time=True)}")
                        st.markdown(notes.get('notes', 'No notes provided').replace(chr(10), "\n\n"))
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
                table_rows = []
                for notes in my_notes:
                    table_rows.append({
                        "Patient": f"{notes.get('patient_name', 'Unknown')} ({notes.get('patient_email', '')})",
                        "Date": format_date(notes.get('created_at'), with_time=True),
                        "Notes Preview": preview_notes(notes.get('notes', 'No notes provided')),
                        "Edit Status": "Open to edit below",
                    })

                st.dataframe(table_rows, use_container_width=True, hide_index=True)

                st.markdown("#### Edit Notes")
                for notes in my_notes:
                    with st.expander(f"{notes.get('patient_name', 'Unknown')} - {format_date(notes.get('created_at'), with_time=True)}"):
                        st.write(f"Patient: {notes.get('patient_name', 'Unknown')} ({notes.get('patient_email', 'N/A')})")
                        st.write(f"Date: {format_date(notes.get('created_at'), with_time=True)}")

                        if st.session_state.get("editing_notes_id") == notes['id']:
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
                            st.markdown(notes.get('notes', 'No notes provided').replace(chr(10), "\n\n"))
                            if st.button("✏️ Edit This Note", key=f"edit_{notes['id']}"):
                                st.session_state.editing_notes_id = notes['id']
                                st.rerun()
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
                    table_rows = []
                    for notes in patient_notes_combined:
                        table_rows.append({
                            "Patient": notes.get('patient_name', 'Unknown'),
                            "Consultation Date": format_date(notes.get('created_at')),
                            "Notes Preview": preview_notes(notes.get('notes', 'No notes provided')),
                        })

                    st.dataframe(table_rows, use_container_width=True, hide_index=True)

                    st.markdown("#### Full Notes")
                    for notes in patient_notes_combined:
                        with st.expander(f"{notes.get('patient_name', 'Unknown')} - {format_date(notes.get('created_at'))}"):
                            st.write(f"Patient: {notes.get('patient_name', 'Unknown')}")
                            st.write(f"Consultation Date: {format_date(notes.get('created_at'), with_time=True)}")
                            st.markdown(notes.get('notes', 'No notes provided').replace(chr(10), "\n\n"))
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
            table_rows = []
            for notes in patient_notes:
                table_rows.append({
                    "Doctor": f"Dr. {notes.get('doctor_name', 'Unknown')}",
                    "Consultation Date": format_date(notes.get('created_at'), with_time=True),
                    "Status": "Completed",
                    "Notes Preview": preview_notes(notes.get('notes', 'No notes provided')),
                })

            st.dataframe(table_rows, use_container_width=True, hide_index=True)

            st.markdown("#### Full Notes")
            for notes in patient_notes:
                with st.expander(f"Dr. {notes.get('doctor_name', 'Unknown')} - {format_date(notes.get('created_at'))}"):
                    st.write(f"Doctor: Dr. {notes.get('doctor_name', 'Unknown')}")
                    st.write(f"Consultation Date: {format_date(notes.get('created_at'), with_time=True)}")
                    st.markdown(notes.get('notes', 'No notes provided').replace(chr(10), "\n\n"))
        else:
            st.info("👋 You don't have any consultation notes yet. They will appear here after your consultations are completed.")
