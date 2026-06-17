import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# connect to firebase
cred = credentials.Certificate("firebase_key.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

import streamlit as st

# -----------------------------
# BREASTAID (MULTI-PART SURVEY)
# -----------------------------

st.set_page_config(page_title="BreastAID", layout="wide")


def apply_theme() -> None:
    st.markdown(
        """
        <style>
            :root {
                --pink: #f45bb8;
                --coral: #f39a9f;
                --yellow: #f4d85b;
                --ink: #222222;
                --card-border: #c37aa1;
            }

            .stApp {
                background: linear-gradient(100deg, var(--pink) 0%, var(--coral) 50%, var(--yellow) 100%);
            }

            .main-title {
                font-size: 2.1rem;
                font-weight: 700;
                color: var(--ink);
                margin-bottom: 0.2rem;
            }

            .sub-title {
                color: #2d2d2d;
                font-size: 1rem;
                margin-bottom: 1rem;
            }

            .card {
                border: 3px solid var(--card-border);
                border-radius: 12px;
                padding: 1.2rem;
                background: rgba(255, 255, 255, 0.15);
                margin-top: 0.8rem;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            }

            .step-strip {
                background: rgba(255, 255, 255, 0.22);
                border: 1px solid rgba(0, 0, 0, 0.08);
                border-radius: 12px;
                padding: 0.7rem 0.9rem;
                margin-bottom: 0.7rem;
                font-weight: 600;
                color: var(--ink);
            }

            .risk-box {
                border-radius: 10px;
                padding: 0.9rem;
                background: rgba(255, 255, 255, 0.4);
                border: 1px solid rgba(0, 0, 0, 0.12);
                margin: 0.5rem 0 1rem 0;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def calculate_risk_score(answers: dict) -> tuple[int, str]:
    """
    Calculate breast cancer risk score based on the assessment answers.
    Scoring values match the official assessment tables.
    Max possible score: 40
    Low Risk: 0-20, High Risk: 21+
    """
    score = 0

    # Section A: Demographics & Personal History
    age = answers.get("age")
    if age == "Under 30":
        score += 0
    elif age == "30 to 39":
        score += 1
    elif age == "40 to 49":
        score += 2
    elif age == "50 to 59":
        score += 3
    elif age == "60 or older":
        score += 4

    bmi = answers.get("bmi")
    if bmi == "Normal (18.5 - 24.9)":
        score += 0
    elif bmi == "Underweight or Overweight":
        score += 1
    elif bmi == "Obese (over 29.9)":
        score += 2

    first_period = answers.get("first_period")
    if first_period == "After age 16":
        score += 0
    elif first_period == "Age 15 to 16":
        score += 1
    elif first_period == "Age 12 to 14":
        score += 2
    elif first_period == "Before age 12":
        score += 3

    gave_birth = answers.get("gave_birth")
    if gave_birth == "Yes":
        score += 0
    elif gave_birth == "No":
        score += 2

    if gave_birth == "Yes":
        first_birth_age = answers.get("first_birth_age")
        if first_birth_age == "Before age 31":
            score += 0
        elif first_birth_age == "Age 31 or older":
            score += 1
    else:
        # If no birth, "Not applicable" choice adds 0
        pass

    menopause = answers.get("menopause")
    if menopause == "No":
        score += 0
    elif menopause == "Yes, before age 45":
        score += 2
    elif menopause == "Yes, between ages 45-55":
        score += 1
    elif menopause == "Yes, after age 55":
        score += 0

    # Section B: Family & Medical History
    family_cancer = answers.get("family_cancer")
    if family_cancer == "Yes":
        score += 3
    elif family_cancer == "No or Not sure":
        score += 0

    benign_condition = answers.get("benign_condition")
    if benign_condition == "Yes":
        score += 2
    elif benign_condition == "No":
        score += 0

    hrt = answers.get("hrt")
    if hrt == "Yes":
        score += 1
    elif hrt == "No":
        score += 0

    diabetes = answers.get("diabetes")
    if diabetes == "Yes":
        score += 1
    elif diabetes == "No":
        score += 0

    # Section C: Lifestyle & Habits
    activity = answers.get("activity")
    if activity == "Daily":
        score += 0
    elif activity == "3 to 5 days per week":
        score += 1
    elif activity == "1 to 2 days per week":
        score += 2
    elif activity == "Rarely or Never":
        score += 3

    alcohol = answers.get("alcohol")
    if alcohol == "No":
        score += 0
    elif alcohol == "Occasionally":
        score += 1
    elif alcohol == "Frequently":
        score += 2

    smoking = answers.get("smoking")
    if smoking == "No":
        score += 0
    elif smoking == "Occasionally":
        score += 1
    elif smoking == "Frequently":
        score += 2

    # Section D: Screening & Imaging History
    mammogram_recent = answers.get("mammogram_recent")
    if mammogram_recent == "Yes":
        score += 0
    elif mammogram_recent == "No":
        score += 1

    birads = answers.get("birads")
    if birads == "1 - Negative":
        score += 0
    elif birads == "2 - Benign":
        score += 1
    elif birads == "3 - Probably Benign":
        score += 2
    elif birads == "4 - Suspicious":
        score += 3
    elif birads == "5 - Highly Suspicious":
        score += 4
    elif birads == "Don't know":
        score += 2

    callback = answers.get("callback")
    if callback == "No":
        score += 0
    elif callback == "Yes":
        score += 2

    # Risk classification: Low Risk 0-20, High Risk 21+
    if score >= 21:
        return score, "High Risk"
    return score, "Low Risk"


def get_missing_questions(step: int, answers: dict) -> list[str]:
    """Check for unanswered required questions in the current step."""
    required_by_step = {
        0: [
            ("age", "Age"),
            ("bmi", "Weight category (BMI)"),
            ("first_period", "Age at first menstrual period"),
            ("gave_birth", "Whether you have ever given birth"),
            ("first_birth_age", "Age at first birth"),
            ("menopause", "Menopause status"),
        ],
        1: [
            ("family_cancer", "Family history of breast cancer"),
            ("benign_condition", "History of benign breast condition"),
            ("hrt", "Hormone replacement therapy use"),
            ("diabetes", "Diabetes diagnosis"),
        ],
        2: [
            ("activity", "Physical activity level"),
            ("alcohol", "Alcohol consumption"),
            ("smoking", "Smoking status"),
        ],
        3: [
            ("mammogram_recent", "Mammogram in the last 2 years"),
            ("birads", "Most recent BI-RADS score"),
            ("callback", "Whether you were called back after mammogram"),
        ],
    }

    missing = []
    for field, label in required_by_step.get(step, []):
        if answers.get(field) is None:
            missing.append(label)
    return missing


def section_header(step: int) -> None:
    labels = [
        "Demographics & Personal History",
        "Family & Medical History",
        "Lifestyle & Habit",
        "Screening & Imaging History",
    ]

    st.markdown('<div class="main-title">BreastAID</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="sub-title">Part {step + 1} of 4: {labels[step]}</div>',
        unsafe_allow_html=True,
    )

    strip = " | ".join(
        [
            f"{'●' if idx == step else '○'} {label}"
            for idx, label in enumerate(labels)
        ]
    )
    st.markdown(f'<div class="step-strip">{strip}</div>', unsafe_allow_html=True)


def save_user_info(email: str, name: str) -> None:
    """Save user registration info to Firestore."""
    try:
        db.collection("users").document(email).set({
            "name": name,
            "email": email,
            "registered_at": datetime.now(),
        }, merge=True)
    except Exception as e:
        st.error(f"Error saving user info: {e}")


def save_assessment(email: str, answers: dict, score: int, risk_level: str) -> None:
    """Save completed assessment to Firestore."""
    try:
        assessment_data = {
            "email": email,
            "answers": answers,
            "score": score,
            "risk_level": risk_level,
            "completed_at": datetime.now(),
        }
        db.collection("users").document(email).collection("assessments").add(assessment_data)
        st.success("Assessment saved!")
    except Exception as e:
        st.error(f"Error saving assessment: {e}")


def load_user_assessments(email: str) -> list:
    """Load all assessments for a user from Firestore."""
    try:
        assessments_query = db.collection("users").document(email).collection("assessments")
        docs = assessments_query.stream()
        assessments = [{"id": doc.id, **doc.to_dict()} for doc in docs]
        # Sort by completed_at in descending order
        assessments.sort(key=lambda x: x.get("completed_at", datetime.now()), reverse=True)
        return assessments
    except Exception as e:
        return []


apply_theme()

# Session state
if "page" not in st.session_state:
    st.session_state.page = "login"

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "risk" not in st.session_state:
    st.session_state.risk = None

if "risk_score" not in st.session_state:
    st.session_state.risk_score = 0

if "survey_step" not in st.session_state:
    st.session_state.survey_step = 0

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "assessment_saved" not in st.session_state:
    st.session_state.assessment_saved = False

# -----------------------------
# LOGIN PAGE
# -----------------------------
if st.session_state.page == "login":
    st.markdown('<div class="main-title">BreastAID</div>', unsafe_allow_html=True)
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email and password:
            try:
                user_doc = db.collection("users").document(email).get()
                if user_doc.exists:
                    st.session_state.user_email = email
                    st.session_state.user_name = user_doc.get("name")
                    st.session_state.page = "dashboard"
                    st.rerun()
                else:
                    st.error("User not found. Please register first.")
            except Exception as e:
                st.error(f"Login error: {e}")
        else:
            st.warning("Please enter email and password")

    if st.button("Create Account"):
        st.session_state.page = "register"

# -----------------------------
# REGISTER PAGE
# -----------------------------
elif st.session_state.page == "register":
    st.markdown('<div class="main-title">BreastAID</div>', unsafe_allow_html=True)
    st.subheader("Register")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        if name and email and password:
            try:
                save_user_info(email, name)
                st.session_state.user_email = email
                st.session_state.user_name = name
                st.success("Account created! Redirecting to login...")
                st.session_state.page = "login"
                st.rerun()
            except Exception as e:
                st.error(f"Registration error: {e}")
        else:
            st.warning("Please fill in all fields")

# -----------------------------
# DASHBOARD
# -----------------------------
elif st.session_state.page == "dashboard":
    st.markdown('<div class="main-title">BreastAID</div>', unsafe_allow_html=True)
    st.subheader(f"Dashboard - Welcome, {st.session_state.user_name or 'User'}!")
    
    if st.button("Logout"):
        st.session_state.user_email = None
        st.session_state.user_name = None
        st.session_state.page = "login"
        st.rerun()
    
    st.write("Welcome! Start your breast cancer risk assessment.")

    if st.button("Start New Assessment"):
        st.session_state.survey_step = 0
        st.session_state.answers = {}
        st.session_state.page = "survey"

    st.markdown("---")
    st.subheader("📋 Your Assessment History")
    
    if st.session_state.user_email:
        assessments = load_user_assessments(st.session_state.user_email)
        if assessments:
            for idx, assessment in enumerate(assessments, 1):
                completed_date = assessment["completed_at"].strftime("%B %d, %Y at %I:%M %p") if hasattr(assessment["completed_at"], "strftime") else str(assessment["completed_at"])
                risk_color = "🔴" if assessment["risk_level"] == "High Risk" else "🟢"
                st.write(f"{risk_color} **Assessment #{idx}** - {assessment['score']}/40 ({assessment['risk_level']}) - {completed_date}")
        else:
            st.info("No assessments yet. Start a new one!")

# -----------------------------
# SURVEY PAGE (PART BY PART)
# -----------------------------
elif st.session_state.page == "survey":
    step = st.session_state.survey_step
    section_header(step)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    if step == 0:
        st.write("1. What is your current age?")
        st.session_state.answers["age"] = st.radio(
            "",
            ["Under 30", "30 to 39", "40 to 49", "50 to 59", "60 or older"],
            horizontal=True,
            index=None,
            key="q_age",
        )

        st.write("2. How would you describe your weight relative to your height? (BMI)")
        st.session_state.answers["bmi"] = st.radio(
            " ",
            ["Normal (18.5 - 24.9)", "Underweight or Overweight", "Obese (over 29.9)"],
            horizontal=True,
            index=None,
            key="q_bmi",
        )

        st.write("3. At what age did you start your first menstrual period?")
        st.session_state.answers["first_period"] = st.radio(
            "  ", 
            ["After age 16", "Age 15 to 16", "Age 12 to 14", "Before age 12"], 
            horizontal=True, 
            index=None, 
            key="q_period"
        )

        st.write("4. Have you ever been pregnant and given birth?")
        st.session_state.answers["gave_birth"] = st.radio(
            "   ", ["Yes", "No"], horizontal=True, index=None, key="q_birth"
        )

        # Show follow-up question only if answered "Yes"
        if st.session_state.answers["gave_birth"] == "Yes":
            st.write("5. How old were you when you gave birth for the first time?")
            st.session_state.answers["first_birth_age"] = st.radio(
                "    ", 
                ["Before age 31", "Age 31 or older"], 
                horizontal=True, 
                index=None, 
                key="q_first_birth"
            )
        else:
            st.session_state.answers["first_birth_age"] = "Not applicable"

        st.write("6. Have you gone through menopause (end of menstrual periods)?")
        st.session_state.answers["menopause"] = st.radio(
            "     ",
            ["No", "Yes, before age 45", "Yes, between ages 45-55", "Yes, after age 55"],
            horizontal=True,
            index=None,
            key="q_menopause",
        )

    elif step == 1:
        st.write("1. Has your mother, sister, or daughter ever been diagnosed with breast cancer?")
        st.session_state.answers["family_cancer"] = st.radio(
            "",
            ["Yes", "No or Not sure"],
            horizontal=True,
            index=None,
            key="q_family",
        )

        st.write(
            "2. Have you ever been told by a doctor that you had a benign (non-cancerous) breast condition, such as fibrocystic changes or a cyst?"
        )
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

    elif step == 2:
        st.write("1. How often do you engage in physical exercise or physical activity?")
        st.session_state.answers["activity"] = st.radio(
            "",
            ["Daily", "3 to 5 days per week", "1 to 2 days per week", "Rarely or Never"],
            horizontal=True,
            index=None,
            key="q_activity",
        )

        st.write("2. How often do you drink alcoholic beverages?")
        st.session_state.answers["alcohol"] = st.radio(
            " ", ["No", "Occasionally", "Frequently"], horizontal=True, index=None, key="q_alcohol"
        )

        st.write("3. Do you smoke tobacco or use other nicotine products?")
        st.session_state.answers["smoking"] = st.radio(
            "  ", ["No", "Occasionally", "Frequently"], horizontal=True, index=None, key="q_smoking"
        )

    elif step == 3:
        st.write("1. Have you had a mammogram (breast X-ray) in the last 2 years?")
        st.session_state.answers["mammogram_recent"] = st.radio(
            "",
            ["Yes", "No"],
            horizontal=True,
            index=None,
            key="q_mammogram",
        )

        st.write("2. What was your most recent BI-RADS score from your mammogram report? (BI-RADS is a standardized reporting system for mammography)")
        st.session_state.answers["birads"] = st.radio(
            " ",
            [
                "1 - Negative",
                "2 - Benign",
                "3 - Probably Benign",
                "4 - Suspicious",
                "5 - Highly Suspicious",
                "Don't know",
            ],
            horizontal=True,
            index=None,
            key="q_birads",
        )

        st.write("3. Were you ever called back for additional tests or images after a mammogram?")
        st.session_state.answers["callback"] = st.radio(
            "  ", ["Yes", "No"], horizontal=True, index=None, key="q_callback"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])

    with c1:
        if st.button("Back"):
            if step == 0:
                st.session_state.page = "dashboard"
            else:
                st.session_state.survey_step -= 1

    with c3:
        if step < 3:
            if st.button("Next"):
                missing_questions = get_missing_questions(step, st.session_state.answers)
                if missing_questions:
                    st.warning(
                        "Please answer all questions in this part before continuing: "
                        + ", ".join(missing_questions)
                    )
                else:
                    st.session_state.survey_step += 1
        else:
            if st.button("Submit Survey"):
                missing_questions = get_missing_questions(step, st.session_state.answers)
                if missing_questions:
                    st.warning(
                        "Please answer all questions in this part before submitting: "
                        + ", ".join(missing_questions)
                    )
                else:
                    score, label = calculate_risk_score(st.session_state.answers)
                    st.session_state.risk_score = score
                    st.session_state.risk = label
                    st.session_state.page = "result"

# -----------------------------
# RESULT PAGE
# -----------------------------
elif st.session_state.page == "result":
    st.markdown('<div class="main-title">BreastAID</div>', unsafe_allow_html=True)
    st.subheader("Assessment Result")

    # Save assessment to Firestore
    if st.session_state.user_email and "assessment_saved" not in st.session_state:
        save_assessment(
            st.session_state.user_email,
            st.session_state.answers,
            st.session_state.risk_score,
            st.session_state.risk
        )
        st.session_state.assessment_saved = True

    st.markdown(
        f'<div class="risk-box"><b>Your Risk Score:</b> {st.session_state.risk_score} out of 40</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.risk == "High Risk":
        st.error("⚠️ High Risk (Score 21 or higher)")
        st.write("Based on your assessment, you have a higher risk for breast cancer. We recommend:")
        st.write("• Schedule an appointment with a doctor or healthcare provider as soon as possible")
        st.write("• Discuss preventive screening options and personalized prevention strategies")
        st.write("• Ask your doctor about regular mammograms or other imaging tests")
    else:
        st.success("✓ Low Risk (Score 0-20)")
        st.write("Based on your assessment, you are in the lower risk category. We recommend:")
        st.write("• Maintain a healthy lifestyle with regular exercise, balanced diet, and healthy weight")
        st.write("• Limit alcohol consumption and avoid smoking")
        st.write("• Continue regular mammography screening as recommended for your age group")
        st.write("• Check your breasts regularly for any changes and report them to your doctor")

    if st.button("Back to Dashboard"):
        st.session_state.assessment_saved = False
        st.session_state.page = "dashboard"
        st.rerun()
