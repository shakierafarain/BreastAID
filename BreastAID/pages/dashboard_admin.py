"""Admin dashboard page."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from utils.firebase_helper import (
    get_db, 
    load_all_assessments_aggregated,
    get_all_appointments,
    schedule_appointment,
)
from utils.navigation import show_sidebar


@st.cache_data(ttl=300)
def get_admin_stats():
    """Get admin statistics from Firebase. Cached for 5 minutes."""
    try:
        db = get_db()
        
        # Get total users
        all_users = list(db.collection("users").stream())
        total_users = len(all_users)
        
        # Get total doctors
        doctors_query = db.collection("users").where("role", "==", "Doctor").stream()
        total_doctors = len(list(doctors_query))
        
        # Get all assessments for statistics
        all_assessments = load_all_assessments_aggregated()
        completed_surveys = len(all_assessments)
        
        # Calculate average risk level (as percentage)
        high_risk_count = sum(1 for a in all_assessments if a.get("risk_level") == "High Risk")
        avg_risk_percentage = (high_risk_count / completed_surveys * 100) if completed_surveys > 0 else 0
        
        return {
            "total_users": total_users,
            "total_doctors": total_doctors,
            "completed_surveys": completed_surveys,
            "avg_risk_percentage": avg_risk_percentage,
            "high_risk_count": high_risk_count,
        }
    except Exception as e:
        st.error(f"Error fetching admin stats: {e}")
        return {
            "total_users": 0,
            "total_doctors": 0,
            "completed_surveys": 0,
            "avg_risk_percentage": 0,
            "high_risk_count": 0,
        }


def create_risk_gauge_chart(percentage):
    """Create a gauge chart for average risk level."""
    fig = go.Figure(data=[go.Indicator(
        mode="gauge+number+delta",
        value=percentage,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Average Risk Level (%)"},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#ff1493"},
            'steps': [
                {'range': [0, 33], 'color': "#e8f5e9"},
                {'range': [33, 66], 'color': "#fff9c4"},
                {'range': [66, 100], 'color': "#ffebee"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        },
        number={'suffix': "%"}
    )])
    
    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=80, b=20),
        font=dict(family="Segoe UI", size=12, color="black"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig


def get_appointment_overview():
    """Get appointment overview statistics."""
    try:
        all_appointments = get_all_appointments()
        
        upcoming = sum(1 for a in all_appointments if a.get("status") in ["scheduled", "confirmed"])
        completed = sum(1 for a in all_appointments if a.get("status") == "completed")
        cancelled = sum(1 for a in all_appointments if a.get("status") in ["cancelled", "needs_reschedule"])
        pending = sum(1 for a in all_appointments if a.get("status") == "pending")
        
        return {
            "pending": pending,
            "upcoming": upcoming,
            "completed": completed,
            "cancelled": cancelled,
        }
    except Exception:
        return {
            "pending": 0,
            "upcoming": 0,
            "completed": 0,
            "cancelled": 0,
        }


def get_all_doctors() -> list:
    """Get all doctors from Firebase."""
    try:
        db = get_db()
        doctors_query = db.collection("users").where("role", "==", "Doctor").stream()
        doctors = []
        for doc in doctors_query:
            doctor_data = doc.to_dict()
            doctor_data["email"] = doc.id
            doctors.append(doctor_data)
        return doctors
    except Exception:
        return []


def show_dashboard_admin_page():
    """Display admin dashboard page."""
    show_sidebar()
    # Custom CSS for admin dashboard
    st.markdown(
        """
        <style>
            .admin-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 2rem;
            }
            
            .admin-title {
                font-size: 1.8rem;
                font-weight: 800;
                color: #333;
            }
            
            .admin-user-info {
                display: flex;
                align-items: center;
                gap: 1rem;
            }
            
            .user-badge {
                background: #ff1493;
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-weight: 600;
                font-size: 0.9rem;
            }
            
            .stat-card {
                background: linear-gradient(135deg, #ffd4e5 0%, #fff0b8 100%);
                padding: 1.5rem;
                border-radius: 15px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            
            .stat-label {
                font-size: 0.9rem;
                color: #555;
                font-weight: 600;
                margin-bottom: 0.5rem;
            }
            
            .stat-value {
                font-size: 2rem;
                font-weight: 800;
                color: #ff1493;
            }
            
            .section-title {
                font-size: 1.2rem;
                font-weight: 700;
                color: #333;
                margin-top: 2rem;
                margin-bottom: 1rem;
            }
            
            .action-button {
                background: linear-gradient(135deg, #ff1493 0%, #ff69b4 100%);
                color: white;
                padding: 0.75rem 1.5rem;
                border-radius: 20px;
                border: none;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .action-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(255, 20, 147, 0.3);
            }
            
            .appointment-card {
                background: white;
                border-left: 4px solid #ff1493;
                padding: 1.5rem;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                margin-bottom: 1rem;
            }
            
            .appointment-label {
                font-size: 0.85rem;
                color: #888;
                font-weight: 600;
                text-transform: uppercase;
                margin-bottom: 0.25rem;
            }
            
            .appointment-value {
                font-size: 1.8rem;
                font-weight: 800;
                color: #ff1493;
            }
            
            .sidebar-link {
                display: block;
                padding: 0.75rem 1rem;
                margin-bottom: 0.5rem;
                border-radius: 8px;
                color: #666;
                text-decoration: none;
                font-weight: 500;
                transition: all 0.3s ease;
                background: #f5f5f5;
                border-left: 3px solid transparent;
            }
            
            .sidebar-link:hover {
                background: #f0e6f0;
                color: #ff1493;
                border-left-color: #ff1493;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Header with user info
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="admin-title">Welcome Back, Admin</div>', unsafe_allow_html=True)
    
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_email = None
            st.session_state.user_name = None
            st.session_state.user_role = None
            st.session_state.page = "landing"
            st.rerun()

    st.divider()

    # Get stats
    stats = get_admin_stats()
    
    # Display stat cards
    st.markdown('<div class="section-title">Overview</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Total Users</div>
                <div class="stat-value">{stats['total_users']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Total Doctors</div>
                <div class="stat-value">{stats['total_doctors']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Completed Surveys</div>
                <div class="stat-value">{stats['completed_surveys']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # Survey Statistics and Risk Chart
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="section-title">Survey Statistics</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="stat-card" style="margin-bottom: 1rem;">
                <div class="stat-label">Average Risk Level</div>
                <div style="display: flex; align-items: baseline; gap: 0.5rem;">
                    <div class="stat-value">{stats['avg_risk_percentage']:.1f}%</div>
                    <div style="font-size: 0.9rem; color: #666;">({stats['high_risk_count']} high risk)</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Show gauge chart
        fig = create_risk_gauge_chart(stats['avg_risk_percentage'])
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    
    with col2:
        st.markdown('<div class="section-title">Appointment Overview</div>', unsafe_allow_html=True)
        
        appointments = get_appointment_overview()
        
        st.markdown(
            f"""
            <div class="appointment-card">
                <div class="appointment-label">Upcoming</div>
                <div class="appointment-value">{appointments['upcoming']}</div>
            </div>
            <div class="appointment-card">
                <div class="appointment-label">Completed</div>
                <div class="appointment-value">{appointments['completed']}</div>
            </div>
            <div class="appointment-card">
                <div class="appointment-label">Cancelled</div>
                <div class="appointment-value">{appointments['cancelled']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.divider()

    # Management Sections
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="section-title">📅 Manage Appointments</div>', unsafe_allow_html=True)
        
        all_appointments = get_all_appointments()
        pending_count = sum(1 for a in all_appointments if a.get("status") == "pending")
        
        if st.button(f"View Appointments ({pending_count} Pending)", use_container_width=True):
            st.session_state.admin_action = "manage_appointments"
    
    with col2:
        st.markdown('<div class="section-title">Manage Users</div>', unsafe_allow_html=True)
        
        col_view, col_add, col_edit = st.columns(3)
        
        with col_view:
            if st.button("📋 View", use_container_width=True):
                st.session_state.admin_action = "view_users"
        
        with col_add:
            if st.button("➕ Add", use_container_width=True):
                st.session_state.admin_action = "add_user"
        
        with col_edit:
            if st.button("✏️ Edit", use_container_width=True):
                st.session_state.admin_action = "edit_user"
    
    st.divider()

    # Management Section
    if hasattr(st.session_state, 'admin_action'):
        action = st.session_state.admin_action
        
        if action == "manage_appointments":
            st.markdown('<div class="section-title">Appointment Management</div>', unsafe_allow_html=True)
            
            all_appointments = get_all_appointments()
            
            # Filter by status
            status_filter = st.selectbox("Filter by Status", 
                                        ["Pending", "Scheduled", "Confirmed", "All"],
                                        key="apt_filter")
            
            if status_filter == "Pending":
                filtered_apts = [a for a in all_appointments if a.get("status") == "pending"]
            elif status_filter == "Scheduled":
                filtered_apts = [a for a in all_appointments if a.get("status") == "scheduled"]
            elif status_filter == "Confirmed":
                filtered_apts = [a for a in all_appointments if a.get("status") == "confirmed"]
            else:
                filtered_apts = all_appointments
            
            if filtered_apts:
                for apt in filtered_apts:
                    with st.container():
                        apt_type = apt.get('appointment_type', 'ftf')
                        apt_type_display = "🎥 Online" if apt_type == "online" else "🏥 Face-to-Face"
                        
                        st.markdown(f"""
                        **Patient:** {apt.get('public_name', 'N/A')}  
                        **Email:** {apt.get('public_email', 'N/A')}  
                        **Type:** {apt_type_display}  
                        **Status:** {apt.get('status', 'unknown').upper()}  
                        **Requested:** {apt.get('requested_at').strftime('%b %d, %Y') if apt.get('requested_at') else 'N/A'}
                        """)
                        
                        if apt.get("status") == "pending":
                            st.markdown("**Action: Assign Doctor & Schedule**")
                            
                            doctors = get_all_doctors()
                            if doctors:
                                doctor_options = {f"{d.get('name', 'Unknown')} ({d['email']})": d for d in doctors}
                                selected_doctor = st.selectbox(
                                    "Select Doctor",
                                    options=list(doctor_options.keys()),
                                    key=f"doctor_{apt['id']}"
                                )
                                
                                col_date, col_time = st.columns(2)
                                with col_date:
                                    apt_date = st.date_input("Appointment Date", key=f"date_{apt['id']}")
                                with col_time:
                                    apt_time = st.time_input("Appointment Time", key=f"time_{apt['id']}")
                                
                                if st.button("✅ Schedule Appointment", key=f"schedule_{apt['id']}", use_container_width=True, type="primary"):
                                    doctor = doctor_options[selected_doctor]
                                    if schedule_appointment(
                                        apt['id'],
                                        doctor['email'],
                                        doctor.get('name', 'Doctor'),
                                        str(apt_date),
                                        str(apt_time)
                                    ):
                                        st.success("Appointment scheduled! Notifications sent to doctor and patient.")
                                        st.rerun()
                            else:
                                st.warning("No doctors available. Please add doctors first.")
                        
                        elif apt.get("status") == "scheduled":
                            meeting_link = apt.get('meeting_link')
                            meeting_info = f"\n🔗 [Join Meeting]({meeting_link})" if meeting_link else ""
                            st.info(f"Scheduled with Dr. {apt.get('doctor_name')} on {apt.get('appointment_date')} at {apt.get('appointment_time')}{meeting_info}")
                        
                        elif apt.get("status") == "confirmed":
                            meeting_link = apt.get('meeting_link')
                            meeting_info = f"\n🔗 [Join Meeting]({meeting_link})" if meeting_link else ""
                            st.success(f"Confirmed with Dr. {apt.get('doctor_name')} on {apt.get('appointment_date')} at {apt.get('appointment_time')}{meeting_info}")
                        
                        st.divider()
            else:
                st.info(f"No {status_filter.lower()} appointments")
        
        elif action == "view_users":
            st.markdown('<div class="section-title">View Users</div>', unsafe_allow_html=True)
            try:
                db = get_db()
                users = list(db.collection("users").stream())
                
                if users:
                    user_data = []
                    for user_doc in users:
                        user_info = user_doc.to_dict()
                        user_info["Email"] = user_doc.id
                        user_info["Role"] = user_info.get("role", "Public")
                        user_info["Name"] = user_info.get("name", "N/A")
                        user_data.append(user_info)
                    
                    st.dataframe(
                        [{
                            "Email": u["Email"],
                            "Name": u["Name"],
                            "Role": u["Role"]
                        } for u in user_data],
                        use_container_width=True
                    )
                else:
                    st.info("No users found")
            except Exception as e:
                st.error(f"Error loading users: {e}")
        
        elif action == "add_user":
            st.markdown('<div class="section-title">Add New User</div>', unsafe_allow_html=True)
            
            with st.form("add_user_form"):
                new_email = st.text_input("Email")
                new_name = st.text_input("Name")
                new_role = st.selectbox("Role", ["Public", "Doctor", "Admin"])
                new_password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Add User"):
                    if new_email and new_name and new_password:
                        try:
                            from utils.firebase_helper import save_user_info
                            save_user_info(new_email, new_name, new_role, new_password)
                            st.success(f"User {new_email} added successfully!")
                            st.session_state.admin_action = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error adding user: {e}")
                    else:
                        st.warning("Please fill in all fields")
        
        elif action == "edit_user":
            st.markdown('<div class="section-title">Edit User Role</div>', unsafe_allow_html=True)
            
            try:
                db = get_db()
                users = list(db.collection("users").stream())
                
                if users:
                    user_emails = [user.id for user in users]
                    selected_email = st.selectbox("Select User", user_emails)
                    
                    selected_user = db.collection("users").document(selected_email).get()
                    if selected_user.exists:
                        current_role = selected_user.to_dict().get("role", "Public")
                        new_role = st.selectbox("New Role", ["Public", "Doctor", "Admin"], 
                                               index=["Public", "Doctor", "Admin"].index(current_role))
                        
                        if st.button("Update Role"):
                            try:
                                from utils.firebase_helper import update_user_role
                                update_user_role(selected_email, new_role)
                                st.success(f"Role updated for {selected_email}")
                                st.session_state.admin_action = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error updating role: {e}")
            except Exception as e:
                st.error(f"Error loading users: {e}")
