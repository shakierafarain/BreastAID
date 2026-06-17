"""Login page."""
from pathlib import Path

import streamlit as st
from utils.firebase_helper import verify_user


def show_login_page():
    """Display login page."""
    st.markdown(
        """
        <style>
            .block-container {
                max-width: 430px !important;
                margin: 0 auto !important;
                padding-top: 0.8rem !important;
                padding-bottom: 1.2rem !important;
            }

            .login-brand {
                text-align: center;
                font-size: 2.2rem;
                font-weight: 800;
                color: #ff1493;
                margin: 0 0 0.6rem 0;
                letter-spacing: 0.4px;
            }

            .login-avatar {
                width: 88px;
                height: 88px;
                border-radius: 999px;
                margin: 0 auto 0.6rem auto;
                background: #ff1493;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .login-avatar svg {
                width: 44px;
                height: 44px;
                stroke: #ffffff;
                fill: none;
                stroke-width: 2.2;
                stroke-linecap: round;
                stroke-linejoin: round;
            }

            .login-caption {
                text-align: center;
                color: #4a4a4a;
                margin-bottom: 0.3rem;
                font-weight: 600;
            }

            .login-wrap [data-testid="stTextInput"] {
                margin-bottom: 0.2rem;
            }

            .login-wrap [data-testid="stTextInput"] input {
                border: 1px solid #d9c2d7 !important;
                border-radius: 999px !important;
                background: #ffffff !important;
                color: #111111 !important;
                padding: 0.38rem 0.75rem !important;
            }

            .login-wrap [data-testid="stTextInput"] button {
                background: #ffffff !important;
                border-left: 1px solid #e7d1e3 !important;
                border-top: 1px solid #d9c2d7 !important;
                border-right: 1px solid #d9c2d7 !important;
                border-bottom: 1px solid #d9c2d7 !important;
                border-radius: 0 12px 12px 0 !important;
            }

            .login-wrap [data-testid="stTextInput"] button svg {
                fill: #000000 !important;
                color: #000000 !important;
                stroke: #000000 !important;
            }

            .login-wrap [data-testid="stButton"] button[kind="primary"] {
                border-radius: 999px !important;
                font-weight: 700 !important;
                letter-spacing: 1px !important;
                padding: 0.38rem 0.9rem !important;
                min-height: 2.15rem !important;
            }

            .login-wrap [data-testid="stButton"] button[kind="secondary"] {
                border-radius: 999px !important;
                font-size: 0.84rem !important;
                padding: 0.28rem 0.55rem !important;
                border: 1px solid #d4a8cb !important;
                color: #7a4e73 !important;
                background: #fff !important;
                min-height: 1.95rem !important;
                white-space: nowrap !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    logo_path = Path("assets/logoBArbg.png")
    if logo_path.exists():
        _, center_col, _ = st.columns([1, 2, 1])
        with center_col:
            st.image(str(logo_path), width=220)
    else:
        st.markdown('<div class="login-brand">BreastAID</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="login-avatar"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="4"></circle><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"></path></svg></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="login-caption">Welcome back!</div>', unsafe_allow_html=True)

    email = st.text_input("Email", placeholder="Email", key="login_email")
    password = st.text_input("Password", type="password", placeholder="Password", key="login_password")

    if st.button("Login", use_container_width=True, type="primary", key="login_submit"):
        if email and password:
            # Check for admin credentials first
            if email.lower() == "admin@gmail.com" and password == "123456":
                st.session_state.user_email = email
                st.session_state.user_name = "Admin"
                st.session_state.user_role = "Admin"
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                # Check Firebase for regular user
                user = verify_user(email, password)
                if user:
                    st.session_state.user_email = email
                    st.session_state.user_name = user.get("name")
                    raw_role = user.get("role", "Public") or "Public"
                    st.session_state.user_role = str(raw_role).strip().title()
                    st.session_state.page = "dashboard"
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
        else:
            st.warning("Please enter email and password")

    if st.button("Create Account", use_container_width=True, type="primary", key="create_account"):
        st.session_state.page = "register"

    st.markdown('</div>', unsafe_allow_html=True)
