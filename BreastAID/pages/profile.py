"""Profile management page for all users."""
import streamlit as st
from utils.firebase_helper import (
    get_user_profile,
    update_user_profile,
    change_user_password,
    update_user_email,
)
from utils.navigation import show_sidebar


def show_profile_page():
    """Display profile management page with view and edit functionality."""
    show_sidebar()
    
    st.title("👤 My Profile")
    
    user_email = st.session_state.get("user_email")
    user_role = st.session_state.get("user_role", "Public")
    
    if not user_email:
        st.error("❌ Please log in first")
        if st.button("← Back to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        return
    
    # Back button
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("← Back to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
    
    st.divider()
    
    # Create tabs for different operations
    tab1, tab2, tab3, tab4 = st.tabs(["📖 View Profile", "✏️ Edit Profile", "🔐 Change Password", "📧 Change Email"])
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 1: VIEW PROFILE (READ)
    # ═══════════════════════════════════════════════════════════════
    with tab1:
        st.subheader("Your Profile Information")
        
        profile_data = get_user_profile(user_email)
        
        if profile_data:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Basic Information")
                st.markdown(f"""
                **📧 Email:** {profile_data.get('email', 'N/A')}
                
                **👤 Name:** {profile_data.get('name', 'N/A')}
                
                **🔷 Role:** {user_role}
                
                **📅 Member Since:** {profile_data.get('registered_at', 'N/A')}
                """)
            
            with col2:
                st.markdown("### Additional Information")
                if user_role == "Doctor":
                    st.markdown(f"""
                    **🏥 Specialization:** {profile_data.get('specialization', 'Not specified')}
                    
                    **📜 License Number:** {profile_data.get('license_number', 'Not specified')}
                    
                    **🏢 Hospital/Clinic:** {profile_data.get('hospital', 'Not specified')}
                    
                    **📱 Phone:** {profile_data.get('phone', 'Not specified')}
                    """)
                
                elif user_role == "Admin":
                    st.markdown(f"""
                    **🏛️ Department:** {profile_data.get('department', 'Not specified')}
                    
                    **👔 Employee ID:** {profile_data.get('employee_id', 'Not specified')}
                    
                    **📱 Phone:** {profile_data.get('phone', 'Not specified')}
                    """)
                
                else:  # Public/Patient
                    st.markdown(f"""
                    **🎂 Date of Birth:** {profile_data.get('dob', 'Not specified')}
                    
                    **📱 Phone:** {profile_data.get('phone', 'Not specified')}
                    
                    **💊 Medical History:** {profile_data.get('medical_history', 'Not specified')}
                    """)
            
            st.success("✅ Profile loaded successfully")
        else:
            st.error("❌ Could not load profile information")
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 2: EDIT PROFILE (UPDATE)
    # ═══════════════════════════════════════════════════════════════
    with tab2:
        st.subheader("Edit Your Profile")
        
        profile_data = get_user_profile(user_email)
        
        # Common fields
        new_name = st.text_input(
            "Full Name",
            value=profile_data.get('name', '') if profile_data else '',
            placeholder="Enter your full name"
        )
        
        new_phone = st.text_input(
            "Phone Number",
            value=profile_data.get('phone', '') if profile_data else '',
            placeholder="Enter your phone number"
        )
        
        # Role-specific fields
        if user_role == "Doctor":
            new_specialization = st.text_input(
                "Specialization",
                value=profile_data.get('specialization', '') if profile_data else '',
                placeholder="e.g., Oncology, Radiology"
            )
            
            new_license = st.text_input(
                "License Number",
                value=profile_data.get('license_number', '') if profile_data else '',
                placeholder="Enter your medical license number"
            )
            
            new_hospital = st.text_input(
                "Hospital/Clinic Name",
                value=profile_data.get('hospital', '') if profile_data else '',
                placeholder="Enter hospital or clinic name"
            )
            
            new_bio = st.text_area(
                "Professional Bio",
                value=profile_data.get('bio', '') if profile_data else '',
                placeholder="Tell us about your experience and expertise",
                height=100
            )
        
        elif user_role == "Admin":
            new_department = st.text_input(
                "Department",
                value=profile_data.get('department', '') if profile_data else '',
                placeholder="e.g., Operations, IT, Support"
            )
            
            new_employee_id = st.text_input(
                "Employee ID",
                value=profile_data.get('employee_id', '') if profile_data else '',
                placeholder="Enter employee ID"
            )
        
        else:  # Public/Patient
            new_dob = st.text_input(
                "Date of Birth (YYYY-MM-DD)",
                value=profile_data.get('dob', '') if profile_data else '',
                placeholder="e.g., 1990-05-15"
            )
            
            new_medical_history = st.text_area(
                "Medical History",
                value=profile_data.get('medical_history', '') if profile_data else '',
                placeholder="Enter any relevant medical history",
                height=100
            )
        
        # Save changes button
        if st.button("💾 Save Changes", use_container_width=True, type="primary"):
            update_data = {
                "name": new_name,
                "phone": new_phone,
            }
            
            # Add role-specific fields
            if user_role == "Doctor":
                update_data.update({
                    "specialization": new_specialization,
                    "license_number": new_license,
                    "hospital": new_hospital,
                    "bio": new_bio,
                })
            elif user_role == "Admin":
                update_data.update({
                    "department": new_department,
                    "employee_id": new_employee_id,
                })
            else:  # Public
                update_data.update({
                    "dob": new_dob,
                    "medical_history": new_medical_history,
                })
            
            if update_user_profile(user_email, update_data):
                st.session_state.user_name = new_name
                st.success("✅ Profile updated successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to update profile")
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 3: CHANGE PASSWORD
    # ═══════════════════════════════════════════════════════════════
    with tab3:
        st.subheader("Change Your Password")
        
        st.info("ℹ️ Password must be at least 6 characters long")
        
        current_password = st.text_input(
            "Current Password",
            type="password",
            placeholder="Enter your current password"
        )
        
        new_password = st.text_input(
            "New Password",
            type="password",
            placeholder="Enter new password (min 6 characters)"
        )
        
        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            placeholder="Confirm new password"
        )
        
        if st.button("🔑 Update Password", use_container_width=True, type="primary"):
            if not current_password:
                st.error("❌ Please enter your current password")
            elif len(new_password) < 6:
                st.error("❌ New password must be at least 6 characters long")
            elif new_password != confirm_password:
                st.error("❌ New passwords do not match")
            else:
                if change_user_password(user_email, current_password, new_password):
                    st.success("✅ Password changed successfully!")
                else:
                    st.error("❌ Failed to change password")
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 4: CHANGE EMAIL
    # ═══════════════════════════════════════════════════════════════
    with tab4:
        st.subheader("Change Your Email Address")
        
        st.warning("⚠️ Changing your email will log you out. You'll need to log in again with your new email.")
        
        current_email = st.text_input(
            "Current Email",
            value=user_email,
            disabled=True,
            placeholder="Your current email"
        )
        
        new_email = st.text_input(
            "New Email Address",
            placeholder="Enter your new email address",
            help="Make sure this is a valid email you have access to"
        )
        
        password_confirm = st.text_input(
            "Enter Your Password to Confirm",
            type="password",
            placeholder="Enter your password to authorize this change"
        )
        
        if st.button("📧 Change Email Address", use_container_width=True, type="primary"):
            if not new_email:
                st.error("❌ Please enter a new email address")
            elif "@" not in new_email or "." not in new_email:
                st.error("❌ Please enter a valid email address")
            elif new_email == user_email:
                st.error("❌ New email must be different from current email")
            elif not password_confirm:
                st.error("❌ Please enter your password to confirm")
            else:
                if update_user_email(user_email, new_email, password_confirm):
                    st.success("✅ Email changed successfully! You will be logged out now.")
                    st.info("🔐 Please log in again with your new email address.")
                    import time
                    time.sleep(2)
                    st.session_state.clear()
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error("❌ Failed to change email")
