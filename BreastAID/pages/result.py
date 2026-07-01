"""Result page showing assessment outcome."""
from pathlib import Path

import streamlit as st
from utils.firebase_helper import save_assessment, request_appointment, has_user_completed_assessment
from utils.scoring import calculate_risk_score
from utils.navigation import show_sidebar


def show_result_page():
    """Display assessment result page."""
    show_sidebar()
    logo_path = Path("assets/logoBArbg.png")
    if logo_path.exists():
        st.image(str(logo_path), width=210)
    else:
        st.markdown('<div class="main-title">BreastAID</div>', unsafe_allow_html=True)
    st.subheader("Assessment Result")

    # Save assessment to Firebase on first load
    if st.session_state.user_email and not st.session_state.get("assessment_saved", False):
        # Block Public users who already have a completed assessment
        if st.session_state.get("user_role") == "Public" and has_user_completed_assessment(st.session_state.user_email):
            st.warning("You have already completed your assessment. Public users can only submit once.")
            if st.button("Back to Dashboard"):
                st.session_state.page = "dashboard"
                st.rerun()
            return
        score, risk_level = calculate_risk_score(st.session_state.answers)
        st.session_state.risk_score = score
        st.session_state.risk = risk_level
        save_assessment(
            st.session_state.user_email,
            st.session_state.answers,
            score,
            risk_level
        )
        st.session_state.assessment_saved = True

    # Display score box
    st.markdown(
        f'<div class="risk-box"><b>Your Risk Score:</b> {st.session_state.risk_score} out of 40</div>',
        unsafe_allow_html=True,
    )

    # Display recommendations based on risk level
    if st.session_state.risk == "High Risk":
        st.error("⚠️ High Risk (Score 21 or higher)")
        st.write("Based on your assessment, you have a higher risk for breast cancer. We recommend:")
        st.write("• Schedule an appointment with a doctor or healthcare provider as soon as possible")
        st.write("• Discuss preventive screening options and personalized prevention strategies")
        st.write("• Ask your doctor about regular mammograms or other imaging tests")
        
        # Appointment request button
        st.divider()
        st.subheader("📅 Schedule Consultation")
        st.write("Request a consultation with a healthcare provider to discuss your results.")
        st.write("Choose your preferred appointment type:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎥 Online Consultation", use_container_width=True, type="primary"):
                if request_appointment(st.session_state.user_email, st.session_state.user_name, "online"):
                    st.success("✅ Online consultation request submitted.")
                    st.info("Admin will review it and notify you after a doctor is assigned.")
                else:
                    st.error("Failed to send appointment request. Please try again.")
        
        with col2:
            if st.button("🏥 Face-to-Face Visit", use_container_width=True):
                if request_appointment(st.session_state.user_email, st.session_state.user_name, "ftf"):
                    st.success("✅ Face-to-face appointment request submitted.")
                    st.info("Admin will review it and notify you after a doctor is assigned.")
                else:
                    st.error("Failed to send appointment request. Please try again.")
    else:
        st.success("✓ Low Risk (Score 0-20)")
        st.write("Based on your assessment, you are in the lower risk category. We recommend focusing on prevention:")
        
        # Prevention recommendations
        st.divider()
        st.subheader("🛡️ Prevention Recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Lifestyle Factors**")
            st.write("✓ Maintain regular physical activity (30+ minutes daily)")
            st.write("✓ Keep a healthy weight and balanced diet")
            st.write("✓ Limit alcohol consumption (≤1 drink/day)")
            st.write("✓ Avoid smoking and secondhand smoke")
        
        with col2:
            st.markdown("**Screening & Monitoring**")
            st.write("✓ Perform regular breast self-exams (monthly)")
            st.write("✓ Get mammography screening per age guidelines")
            st.write("✓ Report any new changes to your doctor promptly")
            st.write("✓ Maintain regular check-ups with healthcare provider")
        
        st.divider()
        st.info("💡 Continue monitoring your health. Regular preventive care is key to early detection. Schedule routine check-ups and mammograms as recommended for your age group.")

    # Navigation button
    if st.button("Back to Dashboard"):
        st.session_state.assessment_saved = False
        st.session_state.page = "dashboard"
        st.rerun()