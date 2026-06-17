"""Dashboard page with visualizations."""
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from utils.firebase_helper import (
    load_user_assessments,
    get_user_notifications,
    get_user_appointments,
    get_unread_notification_count,
    get_user_latest_assessment,
    has_user_completed_assessment,
)
from utils.navigation import show_sidebar


def create_risk_distribution_chart(assessments):
    """Create pie chart showing high vs low risk distribution."""
    risk_counts = {"High Risk": 0, "Low Risk": 0}
    
    for assessment in assessments:
        risk_level = assessment["risk_level"]
        risk_counts[risk_level] += 1
    
    fig = go.Figure(data=[go.Pie(
        labels=list(risk_counts.keys()),
        values=list(risk_counts.values()),
        hole=0.3,
        marker=dict(colors=["#ff1493", "#649678"]),
        textposition="inside",
        textinfo="label+percent",
        textfont=dict(size=13, color="black"),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>"
    )])
    
    fig.update_layout(
        title=dict(text="Risk Distribution", font=dict(size=16, color="black", family="Segoe UI")),
        showlegend=True,
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
        font=dict(family="Segoe UI", size=12, color="black"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    fig.update_traces(textfont=dict(size=13, color="black"))
    
    return fig


def create_score_trend_chart(assessments):
    """Create line chart showing score trends over time."""
    # Keep newest first so Assessment 1 is the most recent record.
    # load_user_assessments already returns data sorted by completed_at DESC.
    assessments_sorted = list(assessments)
    
    scores = [a["score"] for a in assessments_sorted]
    dates = []
    
    for a in assessments_sorted:
        completed_at = a["completed_at"]
        if hasattr(completed_at, "strftime"):
            dates.append(completed_at.strftime("%b %d"))
        else:
            dates.append(str(completed_at)[:10])
    
    # Create assessment numbers for x-axis
    assessment_nums = [f"Assessment {i}" for i in range(1, len(scores) + 1)]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=assessment_nums,
        y=scores,
        mode="lines+markers",
        name="Risk Score",
        line=dict(color="#ff1493", width=3),
        marker=dict(size=10, color="#ff1493", symbol="circle"),
        fill="tozeroy",
        fillcolor="rgba(255, 20, 147, 0.2)",
        hovertemplate="<b>%{x}</b><br>Score: %{y}/40<br>",
    ))
    
    # Add reference line for high risk threshold (21)
    fig.add_hline(y=21, line_dash="dash", line_color="rgba(255, 20, 147, 0.6)",
                  annotation_text="High Risk Threshold", annotation_position="right")
    fig.add_hline(y=20, line_dash="dash", line_color="rgba(100, 150, 120, 0.6)",
                  annotation_text="Low Risk Threshold", annotation_position="right")
    
    fig.update_layout(
        title=dict(text="Risk Score Trend Over Time", font=dict(size=16, color="black", family="Segoe UI")),
        xaxis_title=dict(text="Assessments", font=dict(size=14, color="black")),
        yaxis_title=dict(text="Score (0-40)", font=dict(size=14, color="black")),
        xaxis=dict(tickfont=dict(size=12, color="black")),
        yaxis=dict(tickfont=dict(size=12, color="black")),
        height=400,
        margin=dict(l=60, r=20, t=60, b=60),
        font=dict(family="Segoe UI", size=12, color="black"),
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis_range=[0, 40]
    )
    
    fig.update_xaxes(showgrid=False, tickfont=dict(color="black", size=12))
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(0,0,0,0.15)", tickfont=dict(color="black", size=12))
    
    return fig


def create_stats_cards(assessments):
    """Create statistics summary cards."""
    total = len(assessments)
    high_risk = sum(1 for a in assessments if a["risk_level"] == "High Risk")
    low_risk = total - high_risk
    avg_score = sum(a["score"] for a in assessments) / total if total > 0 else 0
    latest_score = assessments[0]["score"] if assessments else 0
    latest_risk = assessments[0]["risk_level"] if assessments else "N/A"
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">""" + str(total) + """</div>
                <div class="stat-label">Total Assessments</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">""" + str(high_risk) + """</div>
                <div class="stat-label">High Risk</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">""" + str(low_risk) + """</div>
                <div class="stat-label">Low Risk</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">""" + f"{avg_score:.1f}" + """</div>
                <div class="stat-label">Average Score</div>
            </div>
        """, unsafe_allow_html=True)


def show_dashboard_page():
    """Display dashboard page with visualizations."""
    show_sidebar()
    logo_path = Path("assets/logoBArbg.png")
    if logo_path.exists():
        st.image(str(logo_path), width=210)
    else:
        st.markdown('<div class="main-title">BreastAID</div>', unsafe_allow_html=True)
    st.subheader(f"Dashboard - Welcome, {st.session_state.user_name or 'User'}!")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.write("Welcome! Start your breast cancer risk assessment.")
    
    with col2:
        # Notification badge
        unread_count = get_unread_notification_count(st.session_state.user_email)
        if unread_count > 0:
            if st.button(f"📬 Notifications ({unread_count})", use_container_width=True):
                st.session_state.page = "notifications"
                st.rerun()
        else:
            if st.button("📬 Notifications", use_container_width=True):
                st.session_state.page = "notifications"
                st.rerun()

    # Logout button
    if st.button("🚪 Logout"):
        st.session_state.user_email = None
        st.session_state.user_name = None
        st.session_state.page = "login"
        st.rerun()

    st.markdown("---")

    # Appointment section
    st.subheader("📅 Your Appointments")
    
    user_appointments = get_user_appointments(st.session_state.user_email)
    pending_apts = [a for a in user_appointments if a.get("status") == "pending"]
    scheduled_apts = [a for a in user_appointments if a.get("status") == "scheduled"]
    confirmed_apts = [a for a in user_appointments if a.get("status") == "confirmed"]
    
    apt_col1, apt_col2, apt_col3 = st.columns(3)
    with apt_col1:
        st.metric("Pending", len(pending_apts))
    with apt_col2:
        st.metric("Scheduled", len(scheduled_apts))
    with apt_col3:
        st.metric("Confirmed", len(confirmed_apts))
    
    if pending_apts:
        st.markdown("**⏳ Pending Appointments** (Awaiting Admin Assignment)")
        for apt in pending_apts:
            apt_type = apt.get('appointment_type', 'ftf')
            apt_type_display = "🎥 Online" if apt_type == "online" else "🏥 Face-to-Face"
            st.info(f"{apt_type_display} - Appointment request sent on {apt.get('requested_at').strftime('%b %d, %Y') if apt.get('requested_at') else 'N/A'}")
    
    if scheduled_apts:
        st.markdown("**⏳ Scheduled Appointments** (Awaiting Your Confirmation)")
        for apt in scheduled_apts:
            apt_type = apt.get('appointment_type', 'ftf')
            apt_type_display = "🎥 Online" if apt_type == "online" else "🏥 Face-to-Face"
            meeting_link = apt.get('meeting_link')
            meeting_info = f"\n🔗 [Join Meeting]({meeting_link})" if meeting_link else ""
            
            st.warning(f"**Dr. {apt.get('doctor_name', 'N/A')}** ({apt_type_display}) - {apt.get('appointment_date', 'N/A')} at {apt.get('appointment_time', 'N/A')}{meeting_info}")
            st.caption("Check your notifications to accept or request reschedule")
    
    if confirmed_apts:
        st.markdown("**✅ Confirmed Appointments** (Ready for Consultation)")
        for apt in confirmed_apts:
            apt_type = apt.get('appointment_type', 'ftf')
            apt_type_display = "🎥 Online" if apt_type == "online" else "🏥 Face-to-Face"
            meeting_link = apt.get('meeting_link')
            meeting_info = f"\n🔗 [Join Meeting]({meeting_link})" if meeting_link else ""
            
            st.success(f"**Dr. {apt.get('doctor_name', 'N/A')}** ({apt_type_display}) - {apt.get('appointment_date', 'N/A')} at {apt.get('appointment_time', 'N/A')}{meeting_info}")
    
    if not pending_apts and not scheduled_apts and not confirmed_apts:
        st.info("No appointments at this time")

    st.markdown("---")

    # Check if user has already completed assessment
    has_assessment = has_user_completed_assessment(st.session_state.user_email)
    
    if st.session_state.user_role == "Public" and has_assessment:
        latest_assessment = get_user_latest_assessment(st.session_state.user_email)
        st.info("✅ **Survey Completed** - You have already completed your assessment. Public users can only complete the survey once.")
        if latest_assessment:
            st.subheader("📋 Your Assessment Results")
            risk_level = latest_assessment.get("risk_level", "N/A")
            score = latest_assessment.get("score", 0)
            completed_at = latest_assessment.get("completed_at", "N/A")
            
            # Display results
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Risk Level", risk_level)
            with col2:
                st.metric("Score", f"{score}/40")
            with col3:
                if hasattr(completed_at, "strftime"):
                    date_str = completed_at.strftime("%b %d, %Y")
                else:
                    date_str = str(completed_at)[:10]
                st.metric("Completed", date_str)
            
            # Show risk-specific next steps
            if risk_level == "High Risk":
                st.markdown("---")
                st.error("⚠️ **High Risk - Consultation Recommended**")
                st.write("Your assessment indicates a higher risk for breast cancer. We recommend scheduling a consultation with a healthcare provider.")
                if st.button("View Appointments", use_container_width=True):
                    st.session_state.page = "notifications"
                    st.rerun()
            else:
                st.markdown("---")
                st.success("✓ **Low Risk - Prevention Focus**")
                st.write("Your assessment indicates a lower risk for breast cancer. Continue with preventive measures:")
                st.write("• Maintain regular exercise and healthy diet")
                st.write("• Limit alcohol consumption and avoid smoking")
                st.write("• Get regular mammography screening as recommended for your age")
                st.write("• Perform regular breast self-exams")
    else:
        if st.button("➕ Start New Assessment", use_container_width=True, type="primary"):
            st.session_state.survey_step = 0
            st.session_state.answers = {}
            st.session_state.page = "survey"
            st.rerun()

"""
    st.subheader("📊 Your Assessment Analytics")
    
    if st.session_state.user_email:
        assessments = load_user_assessments(st.session_state.user_email)
        
        if assessments:
            # Display statistics cards
            st.markdown("<h4 style='color:#2a2a2a;'>📈 Overview</h4>", unsafe_allow_html=True)
            create_stats_cards(assessments)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Display charts in two columns
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.plotly_chart(
                    create_risk_distribution_chart(assessments),
                    use_container_width=True,
                    config={"displayModeBar": False}
                )
            
            with chart_col2:
                if len(assessments) > 1:
                    st.plotly_chart(
                        create_score_trend_chart(assessments),
                        use_container_width=True,
                        config={"displayModeBar": False}
                    )
                else:
                    st.info("Need at least 2 assessments to show trend chart")
            
            # Detailed history table
            st.markdown("<h4 style='color:#2a2a2a;'>📋 Detailed History</h4>", unsafe_allow_html=True)
            
            for idx, assessment in enumerate(assessments, 1):
                completed_date = assessment["completed_at"].strftime("%B %d, %Y at %I:%M %p") \
                    if hasattr(assessment["completed_at"], "strftime") \
                    else str(assessment["completed_at"])
                risk_color = "🔴" if assessment["risk_level"] == "High Risk" else "🟢"
                
                with st.expander(f"{risk_color} **Assessment #{idx}** - Score: {assessment['score']}/40 ({assessment['risk_level']})"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Risk Score", f"{assessment['score']}/40")
                    with col2:
                        st.metric("Risk Level", assessment['risk_level'])
                    with col3:
                        st.metric("Date", completed_date.split(" at ")[0])
        else:
            st.info("No assessments yet. Click 'Start New Assessment' to begin!")

"""
