"""Doctor Dashboard page with patient analytics and visualizations."""
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from utils.firebase_helper import (
    load_all_assessments_aggregated,
    get_user_appointments,
    accept_appointment,
    decline_appointment,
    get_unread_notification_count,
)
from utils.navigation import show_sidebar


def get_patient_key(assessment):
    """Return a stable patient identifier, or None if unavailable."""
    def _normalize(value):
        if not value:
            return ""
        # Normalize casing and spacing so one patient is not split into duplicates.
        return " ".join(str(value).strip().lower().split())

    email = _normalize(assessment.get("user_email") or assessment.get("email"))
    if email and email not in {"unknown", "none", "null", "n/a"}:
        return f"email:{email}"

    name = _normalize(assessment.get("user_name") or assessment.get("name"))
    if name and name not in {"unknown", "none", "null", "n/a"}:
        return f"name:{name}"

    return None


def create_patient_risk_distribution_chart(patients_risk_data):
    """Create pie chart showing high vs low risk patients distribution."""
    risk_counts = {"High Risk Patients": 0, "Low Risk Patients": 0}
    
    for risk_level in patients_risk_data:
        if risk_level == "High Risk":
            risk_counts["High Risk Patients"] += 1
        else:
            risk_counts["Low Risk Patients"] += 1
    
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
        title=dict(text="Patient Risk Distribution", font=dict(size=16, color="black", family="Segoe UI")),
        showlegend=True,
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
        font=dict(family="Segoe UI", size=13, color="black"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    fig.update_traces(textfont=dict(size=13, color="black"))
    
    return fig


def create_patient_frequency_chart(assessments_data):
    """Create bar chart showing unique patient frequency over time."""
    from collections import defaultdict

    # Count unique patients seen per date.
    date_patients = defaultdict(set)

    for assessment in assessments_data:
        completed_at = assessment["completed_at"]
        if hasattr(completed_at, "strftime"):
            date_str = completed_at.strftime("%b %d")
        else:
            date_str = str(completed_at)[:10]

        patient_key = get_patient_key(assessment)
        if patient_key:
            date_patients[date_str].add(patient_key)

    dates = sorted(date_patients.keys())
    counts = [len(date_patients[d]) for d in dates]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=dates,
        y=counts,
        name="Patients",
        marker=dict(color="#ff1493"),
        textposition="auto",
        text=counts,
        textfont=dict(color="black", size=11),
        hovertemplate="<b>%{x}</b><br>Patients: %{y}<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(text="Patient Frequency", font=dict(size=16, color="black", family="Segoe UI")),
        xaxis_title=dict(text="Date", font=dict(size=14, color="black")),
        yaxis_title=dict(text="Number of Patients", font=dict(size=14, color="black")),
        xaxis=dict(tickfont=dict(size=12, color="black")),
        yaxis=dict(tickfont=dict(size=12, color="black")),
        height=400,
        margin=dict(l=60, r=20, t=60, b=60),
        font=dict(family="Segoe UI", size=12, color="black"),
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    fig.update_xaxes(showgrid=False, tickfont=dict(color="black", size=12))
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(0,0,0,0.15)", tickfont=dict(color="black", size=12))
    
    return fig


def create_score_distribution_chart(scores):
    """Create discrete bar chart showing score frequency across assessments."""
    fig = go.Figure()

    # Use exact score values to avoid merged histogram bins.
    score_counts = {}
    for score in scores:
        score_counts[score] = score_counts.get(score, 0) + 1

    sorted_scores = sorted(score_counts.keys())
    frequencies = [score_counts[s] for s in sorted_scores]

    fig.add_trace(go.Bar(
        x=sorted_scores,
        y=frequencies,
        name="Score Distribution",
        marker=dict(color="#ff1493"),
        width=0.8,
        text=frequencies,
        textposition="outside",
        textfont=dict(color="black", size=11),
        hovertemplate="<b>Score: %{x}</b><br>Count: %{y}<extra></extra>"
    ))
    
    fig.add_vline(
        x=21,
        line_dash="dash",
        line_color="rgba(255, 20, 147, 0.8)",
        line_width=2,
        annotation_text="High Risk Threshold (21)",
        annotation_position="top right"
    )
    
    fig.update_layout(
        title=dict(text="Score Distribution Across Assessments", font=dict(size=16, color="black", family="Segoe UI")),
        xaxis_title=dict(text="Risk Score", font=dict(size=14, color="black")),
        yaxis_title=dict(text="Frequency", font=dict(size=14, color="black")),
        xaxis=dict(tickfont=dict(size=12, color="black")),
        yaxis=dict(tickfont=dict(size=12, color="black")),
        height=400,
        margin=dict(l=60, r=20, t=60, b=60),
        font=dict(family="Segoe UI", size=12, color="black"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    fig.update_xaxes(
        showgrid=False,
        tickfont=dict(color="black", size=12),
        type="linear",
        range=[0, 40],
        dtick=5
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(0,0,0,0.15)",
        tickfont=dict(color="black", size=12),
        rangemode="tozero",
        dtick=1
    )
    
    return fig


def create_doctor_stats_cards(all_assessments):
    """Create statistics summary cards for doctor view."""
    total_assessments = len(all_assessments)
    high_risk_count = sum(1 for a in all_assessments if a["risk_level"] == "High Risk")
    low_risk_count = total_assessments - high_risk_count
    unique_patients = {
        get_patient_key(a)
        for a in all_assessments
        if get_patient_key(a)
    }
    total_patients = len(unique_patients) if unique_patients else total_assessments
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">""" + str(total_assessments) + """</div>
                <div class="stat-label">Total Assessments</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">""" + str(high_risk_count) + """</div>
                <div class="stat-label">High Risk Cases</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">""" + str(low_risk_count) + """</div>
                <div class="stat-label">Low Risk Cases</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">""" + str(total_patients) + """</div>
                <div class="stat-label">Total Patients</div>
            </div>
        """, unsafe_allow_html=True)


def show_dashboard_doctor_page():
    """Display doctor dashboard page with patient analytics."""
    show_sidebar()
    st.markdown(
        """
        <style>
            [data-testid="stSelectbox"] > div > div,
            [data-baseweb="select"] > div {
                background: #ffffff !important;
                color: #111111 !important;
                border: 1px solid #d9c2d7 !important;
                border-radius: 10px !important;
            }

            [data-testid="stSelectbox"] svg,
            [data-baseweb="select"] svg {
                fill: #111111 !important;
                color: #111111 !important;
            }

            div[role="listbox"] {
                background: #ffffff !important;
                border: 1px solid #d9c2d7 !important;
            }

            div[role="option"] {
                background: #ffffff !important;
                color: #111111 !important;
            }

            div[role="option"]:hover {
                background: #ffeaf4 !important;
            }

            /* BaseWeb popover menu used by Streamlit selectbox */
            [data-baseweb="popover"],
            [data-baseweb="popover"] * {
                color: #111111 !important;
            }

            [data-baseweb="menu"],
            [data-baseweb="menu"] ul,
            [data-baseweb="menu"] li,
            [data-baseweb="menu"] div {
                background: #ffffff !important;
                color: #111111 !important;
            }

            [data-baseweb="menu"] li[aria-selected="true"],
            [data-baseweb="menu"] li:hover,
            [data-baseweb="menu"] div[aria-selected="true"],
            [data-baseweb="menu"] div:hover {
                background: #ffeaf4 !important;
                color: #111111 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    logo_path = Path("assets/logoBArbg.png")
    if logo_path.exists():
        st.image(str(logo_path), width=210)
    else:
        st.markdown('<div class="main-title">BreastAID</div>', unsafe_allow_html=True)
    st.subheader(f"Doctor Dashboard - Welcome, Dr. {st.session_state.user_name or 'Doctor'}!")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.write("Overview of patient assessments and risk analytics.")
    
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
    st.subheader("📊 Patient Assessment Analytics")
    
    # Load all public users' assessments
    assessments = load_all_assessments_aggregated()
    
    if assessments:
        # Display statistics cards
        st.markdown("<h4 style='color:#2a2a2a;'>📈 Overview</h4>", unsafe_allow_html=True)
        create_doctor_stats_cards(assessments)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Display charts in two columns
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            risk_levels = [a["risk_level"] for a in assessments]
            st.plotly_chart(
                create_patient_risk_distribution_chart(risk_levels),
                use_container_width=True,
                config={"displayModeBar": False}
            )
        
        with chart_col2:
            if len(assessments) > 1:
                st.plotly_chart(
                    create_patient_frequency_chart(assessments),
                    use_container_width=True,
                    config={"displayModeBar": False}
                )
            else:
                st.info("Need at least 2 assessments to show frequency chart")
        
        # Score distribution chart
        st.markdown("<br>", unsafe_allow_html=True)
        scores = [a["score"] for a in assessments]
        st.plotly_chart(
            create_score_distribution_chart(scores),
            use_container_width=True,
            config={"displayModeBar": False}
        )
        
        # Detailed assessment table
        st.markdown("<br><h4 style='color:#2a2a2a;'>📋 Assessment Details</h4>", unsafe_allow_html=True)

        patients_map = {}
        for assessment in assessments:
            patient_key = get_patient_key(assessment) or "Unknown Patient"
            if patient_key not in patients_map:
                patients_map[patient_key] = {
                    "name": assessment.get("user_name") or patient_key,
                    "email": assessment.get("user_email") or "Unknown",
                    "items": [],
                }
            patients_map[patient_key]["items"].append(assessment)

        for patient_key, patient_data in patients_map.items():
            patient_name = patient_data["name"]
            patient_email = patient_data["email"]
            patient_assessments = patient_data["items"]
            latest_assessment = patient_assessments[0]
            latest_risk_color = "🔴" if latest_assessment["risk_level"] == "High Risk" else "🟢"

            expander_title = (
                f"{latest_risk_color} **{patient_name}** - "
                f"{len(patient_assessments)} assessment(s)"
            )

            with st.expander(expander_title):
                option_labels = []
                for idx, item in enumerate(patient_assessments, 1):
                    date_label = item["completed_at"].strftime("%Y-%m-%d") \
                        if hasattr(item["completed_at"], "strftime") \
                        else str(item["completed_at"])[:10]
                    option_labels.append(
                        f"Assessment {idx} - {date_label} - {item['score']}/40 ({item['risk_level']})"
                    )

                selected_label = st.selectbox(
                    "Select assessment",
                    option_labels,
                    key=f"doctor_patient_assessment_{patient_key}",
                )
                selected_index = option_labels.index(selected_label)
                selected_assessment = patient_assessments[selected_index]

                completed_date = selected_assessment["completed_at"].strftime("%B %d, %Y at %I:%M %p") \
                    if hasattr(selected_assessment["completed_at"], "strftime") \
                    else str(selected_assessment["completed_at"])

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Risk Score", f"{selected_assessment['score']}/40")
                with col2:
                    st.metric("Risk Level", selected_assessment["risk_level"])
                with col3:
                    st.metric("Date", completed_date.split(" at ")[0])

                st.markdown("---")
                st.write(f"**Patient Email:** {patient_email}")
                st.write(f"**Completed At:** {completed_date}")
    else:
        st.info("No assessments available yet.")

    st.markdown("---")
    st.subheader("📅 Your Appointments")
    
    doctor_appointments = get_user_appointments(st.session_state.user_email)
    pending_apts = [a for a in doctor_appointments if a.get("status") == "scheduled" and a.get("doctor_accepted") is None]
    confirmed_apts = [a for a in doctor_appointments if a.get("status") == "confirmed"]
    
    if pending_apts:
        st.markdown("**⏳ Pending Confirmation**")
        for apt in pending_apts:
            with st.container():
                apt_type = apt.get('appointment_type', 'ftf')
                apt_type_display = "🎥 Online" if apt_type == "online" else "🏥 Face-to-Face"
                meeting_link = apt.get('meeting_link')
                meeting_info = f"\n🔗 [Join Meeting]({meeting_link})" if meeting_link else ""
                
                st.markdown(f"""
                **Patient:** {apt.get('public_name', 'N/A')}  
                **Type:** {apt_type_display}  
                **Date:** {apt.get('appointment_date', 'N/A')} at {apt.get('appointment_time', 'N/A')}  
                **Status:** Waiting for confirmation{meeting_info}
                """)
                st.caption("Check your notifications to accept or request reschedule")
            st.divider()
    
    if confirmed_apts:
        st.markdown("**✅ Confirmed Appointments**")
        for apt in confirmed_apts:
            apt_type = apt.get('appointment_type', 'ftf')
            apt_type_display = "🎥 Online" if apt_type == "online" else "🏥 Face-to-Face"
            meeting_link = apt.get('meeting_link')
            meeting_info = f" | 🔗 [Join Meeting]({meeting_link})" if meeting_link else ""
            st.success(f"**{apt.get('public_name', 'N/A')}** ({apt_type_display}) - {apt.get('appointment_date')} at {apt.get('appointment_time')}{meeting_info}")
    
    if not pending_apts and not confirmed_apts:
        st.info("No appointments at this time")