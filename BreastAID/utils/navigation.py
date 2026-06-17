"""
BreastAID - Role-Based Sidebar Navigation
Place this file in: utils/navigation.py
"""
import streamlit as st


# ═══════════════════════════════════════════════════════════════
# ROLE → PAGES MAPPING
# ═══════════════════════════════════════════════════════════════
ROLE_NAV = {
    "Public": [
        {"icon": "🏠", "label": "Dashboard",         "page": "dashboard"},
        #{"icon": "📋", "label": "Take Survey",       "page": "survey"},
        #{"icon": "📊", "label": "My Results",        "page": "result"},
        {"icon": "💬", "label": "Chat",              "page": "chat"},
        {"icon": "📝", "label": "Consultation Notes", "page": "consultation_notes"},
        {"icon": "👤", "label": "Profile",           "page": "profile"},
        {"icon": "🔔", "label": "Notifications",     "page": "notifications"},
    ],
    "Doctor": [
        {"icon": "🏠", "label": "Dashboard",         "page": "dashboard"},
        {"icon": "💬", "label": "Chat",              "page": "chat"},
        {"icon": "📝", "label": "Consultation Notes", "page": "consultation_notes"},
        {"icon": "👤", "label": "Profile",           "page": "profile"},
        {"icon": "🔔", "label": "Notifications",     "page": "notifications"},
    ],
    "Admin": [
        {"icon": "🏠", "label": "Dashboard",         "page": "dashboard"},
        {"icon": "💬", "label": "Chat",              "page": "chat"},
        {"icon": "📝", "label": "Consultation Notes", "page": "consultation_notes"},
        {"icon": "👤", "label": "Profile",           "page": "profile"},
        {"icon": "🔔", "label": "Notifications",     "page": "notifications"},
    ],
}

ROLE_COLORS = {
    "Public": "#EC4899",   # pink (breast cancer awareness)
    "Doctor": "#DB2777",   # darker pink
    "Admin":  "#BE185D",   # deep pink
}

ROLE_ICONS = {
    "Public": "👤",
    "Doctor": "👨‍⚕️",
    "Admin":  "🛡️",
}


# ═══════════════════════════════════════════════════════════════
# NAVIGATION CSS
# ═══════════════════════════════════════════════════════════════
def _inject_nav_css(accent: str):
    st.markdown(f"""
    <style>
        /* ── hide default Streamlit sidebar nav ── */
        [data-testid="stSidebarNav"] {{display: none !important;}}

        /* ── sidebar background ── */
        [data-testid="stSidebar"] {{
            background: #f8fafc;
            border-right: 1px solid #e2e8f0;
            overflow: hidden !important;
        }}

        /* ── reduce streamlit padding ── */
        [data-testid="stSidebar"] > div {{
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            overflow: hidden !important;
            height: 100vh;
        }}

        /* ── app logo/title area ── */
        .nav-brand {{
            padding: 0.8rem 0.8rem 0.6rem;
            border-bottom: 1px solid #e2e8f0;
            margin-bottom: 0.3rem;
            text-align: center;
        }}
        .nav-brand h1 {{
            font-size: 1.1rem;
            font-weight: 700;
            color: #1e293b;
            margin: 0;
            letter-spacing: -0.5px;
            font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
        }}
        .nav-brand h1 span {{color: {accent}; font-weight: 800;}}

        /* ── role badge ── */
        .role-badge {{
            display: inline-block;
            background: {accent}10;
            color: {accent};
            border: 1px solid {accent}30;
            border-radius: 16px;
            padding: 2px 8px;
            font-size: 0.6rem;
            font-weight: 600;
            margin-top: 4px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}

        /* ── user info ── */
        .nav-user {{
            padding: 0.6rem 0.8rem;
            margin-bottom: 0.3rem;
            text-align: center;
            border-bottom: 1px solid #e2e8f0;
        }}
        .nav-user-avatar {{
            width: 45px;
            height: 45px;
            border-radius: 50%;
            background: linear-gradient(135deg, {accent}, {accent}cc);
            margin: 0 auto 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            color: white;
            font-weight: 600;
        }}
        .nav-user-name {{
            font-size: 0.8rem;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 1px;
            font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
        }}
        .nav-user-email {{
            font-size: 0.65rem;
            color: #64748b;
            font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
        }}

        /* ── section label ── */
        .nav-section {{
            padding: 0.3rem 0.8rem;
            font-size: 0.55rem;
            font-weight: 700;
            color: #64748b;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-top: 0.3rem;
            margin-bottom: 0.2rem;
            font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
        }}

        /* ── nav buttons ── */
        div[data-testid="stSidebar"] .stButton > button {{
            width: 100%;
            text-align: left;
            background: transparent;
            border: none;
            color: #475569;
            padding: 0.5rem 0.8rem;
            font-size: 0.8rem;
            font-weight: 500;
            border-radius: 6px;
            border-left: 3px solid transparent;
            transition: all 0.2s ease;
            cursor: pointer;
            margin-bottom: 0.15rem;
            font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
        }}
        div[data-testid="stSidebar"] .stButton > button:hover {{
            background: {accent}08;
            color: {accent};
            border-left-color: {accent}40;
        }}

        /* ── active nav button ── */
        div[data-testid="stSidebar"] .stButton.active-nav > button {{
            background: {accent}12;
            color: {accent};
            border-left-color: {accent};
            font-weight: 600;
        }}

        /* ── divider ── */
        .nav-divider {{
            border: none;
            border-top: 1px solid #e2e8f0;
            margin: 0.2rem 0.8rem 0.15rem;
        }}

        /* ── logout button ── */
        .logout-area {{
            padding: 0;
            margin: 0;
        }}
        div[data-testid="stSidebar"] .logout-area .stButton > button {{
            color: #ef4444;
            font-size: 0.8rem;
            border-left-color: transparent !important;
            padding: 0.5rem 0.8rem !important;
            margin-bottom: 0 !important;
        }}
        div[data-testid="stSidebar"] .logout-area .stButton > button:hover {{
            color: #dc2626;
            background: #fecaca20;
        }}
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# MAIN NAVIGATION FUNCTION
# ═══════════════════════════════════════════════════════════════
def show_sidebar():
    """
    Renders the role-based sidebar navigation.
    Call this at the top of every authenticated page.

    Usage in each dashboard page:
        from utils.navigation import show_sidebar
        show_sidebar()
    """
    role  = st.session_state.get("user_role", "Patient")
    name  = st.session_state.get("user_name", "User")
    email = st.session_state.get("user_email", "")
    page  = st.session_state.get("page", "dashboard")

    accent = ROLE_COLORS.get(role, "#E91E8C")
    icon   = ROLE_ICONS.get(role, "👤")
    pages  = ROLE_NAV.get(role, ROLE_NAV["Public"])

    _inject_nav_css(accent)

    with st.sidebar:
        # ── Brand ──────────────────────────────────────────────
        st.markdown(f"""
        <div class="nav-brand">
            <h1>Breast<span>AID</span></h1>
        </div>
        """, unsafe_allow_html=True)

        # ── User Info ──────────────────────────────────────────
        first_letter = name[0].upper() if name else "U"
        st.markdown(f"""
        <div class="nav-user">
            <div class="nav-user-avatar">{first_letter}</div>
            <div class="nav-user-name">{name}</div>
            <div class="nav-user-email">{email}</div>
            <div class="role-badge" style="margin: 8px auto 0;">👤 {role}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Menu Label ─────────────────────────────────────────
        st.markdown('<div class="nav-section">Navigation</div>', unsafe_allow_html=True)

        # ── Nav Items ──────────────────────────────────────────
        for item in pages:
            is_active = (page == item["page"])

            # Wrap in active class using a container trick
            container = st.container()
            if is_active:
                container.markdown('<div class="active-nav">', unsafe_allow_html=True)

            if container.button(
                f"{item['icon']}  {item['label']}",
                key=f"nav_{item['page']}",
                use_container_width=True,
            ):
                st.session_state.page = item["page"]
                st.rerun()

            if is_active:
                container.markdown('</div>', unsafe_allow_html=True)

        # ── Logout ─────────────────────────────────────────────
        st.markdown('<hr class="nav-divider">', unsafe_allow_html=True)
        st.markdown('<div class="nav-section">Settings</div>', unsafe_allow_html=True)

        with st.container():
            st.markdown('<div class="logout-area">', unsafe_allow_html=True)
            if st.button("🚪 Logout", key="nav_logout", use_container_width=True):
                st.session_state.clear()
                st.session_state.page = "landing"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)