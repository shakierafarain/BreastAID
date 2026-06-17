"""Survey page with multi-step form."""
from pathlib import Path

import streamlit as st
from utils.validators import get_missing_questions, get_section_header_text, get_section_strip
from utils.navigation import show_sidebar
from utils.firebase_helper import has_user_completed_assessment


def show_section_header(step: int):
    """Display section header with progress indicator."""
    part_text, section_label = get_section_header_text(step)
    
    logo_path = Path("assets/logoBArbg.png")
    if logo_path.exists():
        st.image(str(logo_path), width=210)
    else:
        st.markdown('<div class="main-title">BreastAID</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-title">{part_text}: {section_label}</div>', 
                unsafe_allow_html=True)
    
    strip = get_section_strip(step)
    st.markdown(f'<div class="step-strip">{strip}</div>', unsafe_allow_html=True)


def show_survey_page():
    """Display survey page with questions based on current step."""
    show_sidebar()
    
    # Check if public user has already completed survey
    if st.session_state.user_role == "Public" and has_user_completed_assessment(st.session_state.user_email):
        logo_path = Path("assets/logoBArbg.png")
        if logo_path.exists():
            st.image(str(logo_path), width=210)
        else:
            st.markdown('<div class="main-title">BreastAID</div>', unsafe_allow_html=True)
        st.warning("⚠️ Survey Already Completed")
        st.info("Public users can only complete the survey once. Your assessment results are available on your dashboard.")
        if st.button("Back to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        return
    
    step = st.session_state.survey_step
    show_section_header(step)

    # Section A: Demographics & Personal History
    if step == 0:
        st.write("1. What is your current age?")
        st.session_state.answers["age"] = st.radio(
            "", ["Under 30", "30 to 39", "40 to 49", "50 to 59", "60 or older"],
            horizontal=True, index=None, key="q_age"
        )

        st.write("2. How would you describe your weight relative to your height? (BMI)")
        st.session_state.answers["bmi"] = st.radio(
            " ", ["Normal (18.5 - 24.9)", "Underweight or Overweight", "Obese (over 29.9)"],
            horizontal=True, index=None, key="q_bmi"
        )

        st.write("3. At what age did you start your first menstrual period?")
        st.session_state.answers["first_period"] = st.radio(
            "  ", ["After age 16", "Age 15 to 16", "Age 12 to 14", "Before age 12"],
            horizontal=True, index=None, key="q_period"
        )

        st.write("4. Have you ever been pregnant and given birth?")
        st.session_state.answers["gave_birth"] = st.radio(
            "   ", ["Yes", "No"], horizontal=True, index=None, key="q_birth"
        )

        # Follow-up question if answered "Yes"
        if st.session_state.answers["gave_birth"] == "Yes":
            st.write("5. How old were you when you gave birth for the first time?")
            st.session_state.answers["first_birth_age"] = st.radio(
                "    ", ["Before age 31", "Age 31 or older"],
                horizontal=True, index=None, key="q_first_birth"
            )
        else:
            st.session_state.answers["first_birth_age"] = "Not applicable"

        st.write("6. Have you gone through menopause (end of menstrual periods)?")
        st.session_state.answers["menopause"] = st.radio(
            "     ", ["No", "Yes, before age 45", "Yes, between ages 45-55", "Yes, after age 55"],
            horizontal=True, index=None, key="q_menopause"
        )

    # Section B: Family & Medical History
    elif step == 1:
        st.write("1. Has your mother, sister, or daughter ever been diagnosed with breast cancer?")
        st.session_state.answers["family_cancer"] = st.radio(
            "", ["Yes", "No or Not sure"],
            horizontal=True, index=None, key="q_family"
        )

        st.write("2. Have you ever been told by a doctor that you had a benign (non-cancerous) breast condition, such as fibrocystic changes or a cyst?")
        st.session_state.answers["benign_condition"] = st.radio(
            " ", ["Yes", "No"], horizontal=True, index=None, key="q_benign"
        )

        st.write("3. Have you ever taken hormone replacement therapy (HRT) for menopause symptoms?")
        st.session_state.answers["hrt"] = st.radio(
            "  ", ["Yes", "No"], horizontal=True, index=None, key="q_hrt"
        )

        st.write("4. Have you ever been diagnosed with diabetes?")
        st.session_state.answers["diabetes"] = st.radio(
            "   ", ["Yes", "No"], horizontal=True, index=None, key="q_diabetes"
        )

    # Section C: Lifestyle & Habits
    elif step == 2:
        st.write("1. How often do you engage in physical exercise or physical activity?")
        st.session_state.answers["activity"] = st.radio(
            "", ["Daily", "3 to 5 days per week", "1 to 2 days per week", "Rarely or Never"],
            horizontal=True, index=None, key="q_activity"
        )

        st.write("2. How often do you drink alcoholic beverages?")
        st.session_state.answers["alcohol"] = st.radio(
            " ", ["No", "Occasionally", "Frequently"],
            horizontal=True, index=None, key="q_alcohol"
        )

        st.write("3. Do you smoke tobacco or use other nicotine products?")
        st.session_state.answers["smoking"] = st.radio(
            "  ", ["No", "Occasionally", "Frequently"],
            horizontal=True, index=None, key="q_smoking"
        )

    # Section D: Screening & Imaging History
    elif step == 3:
        st.write("1. Have you had a mammogram (breast X-ray) in the last 2 years?")
        st.session_state.answers["mammogram_recent"] = st.radio(
            "", ["Yes", "No"],
            horizontal=True, index=None, key="q_mammogram"
        )

        st.write("2. What was your most recent BI-RADS score from your mammogram report? (BI-RADS is a standardized reporting system for mammography)")
        st.session_state.answers["birads"] = st.radio(
            " ", [
                "1 - Negative",
                "2 - Benign",
                "3 - Probably Benign",
                "4 - Suspicious",
                "5 - Highly Suspicious",
                "Don't know",
            ],
            horizontal=True, index=None, key="q_birads"
        )

        st.write("3. Were you ever called back for additional tests or images after a mammogram?")
        st.session_state.answers["callback"] = st.radio(
            "  ", ["Yes", "No"], horizontal=True, index=None, key="q_callback"
        )

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("Back"):
            if step == 0:
                st.session_state.page = "dashboard"
            else:
                st.session_state.survey_step -= 1
            st.rerun()

    with col3:
        if step < 3:
            if st.button("Next"):
                missing = get_missing_questions(step, st.session_state.answers)
                if missing:
                    st.warning("Please answer all questions: " + ", ".join(missing))
                else:
                    st.session_state.survey_step += 1
                    st.rerun()
        else:
            if st.button("Submit Survey"):
                missing = get_missing_questions(step, st.session_state.answers)
                if missing:
                    st.warning("Please answer all questions: " + ", ".join(missing))
                else:
                    st.session_state.page = "result"
                    st.rerun()
