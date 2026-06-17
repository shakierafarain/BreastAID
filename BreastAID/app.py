"""
BreastAID - Breast Cancer Risk Assessment Application
Main entry point for the Streamlit app
"""
import streamlit as st
from config.firebase_config import init_firebase
from styles.theme import apply_theme
from pages.landing import show_landing_page
from pages.login import show_login_page
from pages.register import show_register_page
from pages.dashboard import show_dashboard_page
from pages.dashboard_doctor import show_dashboard_doctor_page
from pages.dashboard_admin import show_dashboard_admin_page
from pages.notifications import show_notifications_page
from pages.chat import show_chat_page
from pages.profile import show_profile_page
from pages.survey import show_survey_page
from pages.result import show_result_page
from pages.consultation_notes import show_consultation_notes_page

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════
st.set_page_config(page_title="BreastAID", layout="wide")

# ═══════════════════════════════════════════════════════════════
# INITIALIZATION
# ═══════════════════════════════════════════════════════════════
init_firebase()
apply_theme()


# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "page": "landing",
        "user_email": None,
        "user_name": None,
        "user_role": None,
        "risk": None,
        "risk_score": 0,
        "survey_step": 0,
        "answers": {},
        "assessment_saved": False,
        "show_settings": False,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


VALID_PAGES = {"landing", "login", "register", "dashboard", "survey", "result", "notifications", "chat", "profile", "consultation_notes"}


def sync_page_with_url():
    """Keep session page and URL query param in sync for browser back/forward support."""
    current_page = st.session_state.page
    url_page = st.query_params.get("page")
    url_page = str(url_page) if url_page is not None else None
    last_url_page = st.session_state.get("_last_url_page")

    # If URL is missing/invalid, set it to the current in-app page.
    if url_page not in VALID_PAGES:
        st.query_params["page"] = current_page
        st.session_state["_last_url_page"] = current_page
        return

    # Browser back/forward changes URL externally; apply only in that case.
    if last_url_page is not None and url_page != last_url_page and url_page != current_page:
        st.session_state.page = url_page
        current_page = url_page

    # In-app button navigation should update URL.
    elif url_page != current_page:
        st.query_params["page"] = current_page

    st.session_state["_last_url_page"] = current_page


# ═══════════════════════════════════════════════════════════════
# MAIN APP ROUTER
# ═══════════════════════════════════════════════════════════════
def main():
    """Main app router - directs to correct page based on session state."""
    sync_page_with_url()
    page = st.session_state.page
    
    if page == "landing":
        show_landing_page()
    elif page == "login":
        show_login_page()
    elif page == "register":
        show_register_page()
    elif page == "dashboard":
        # Route to appropriate dashboard based on user role
        if st.session_state.user_role == "Admin":
            show_dashboard_admin_page()
        elif st.session_state.user_role == "Doctor":
            show_dashboard_doctor_page()
        else:
            show_dashboard_page()
    elif page == "survey":
        show_survey_page()
    elif page == "result":
        show_result_page()
    elif page == "notifications":
        show_notifications_page()
    elif page == "chat":
        show_chat_page()
    elif page == "profile":
        show_profile_page()
    elif page == "consultation_notes":
        show_consultation_notes_page()


if __name__ == "__main__":
    main()
