"""Registration page."""
from pathlib import Path

import streamlit as st
from utils.firebase_helper import save_user_info


def show_register_page():
    """Display registration page."""
    st.markdown(
        """
        <style>
            .block-container {
                max-width: 430px !important;
                margin: 0 auto !important;
                padding-top: 0.8rem !important;
                padding-bottom: 1.2rem !important;
            }

            .register-brand {
                text-align: center;
                font-size: 2.2rem;
                font-weight: 800;
                color: #ff1493;
                margin: 0 0 0.6rem 0;
                letter-spacing: 0.4px;
            }

            .register-avatar {
                width: 88px;
                height: 88px;
                border-radius: 999px;
                margin: 0 auto 0.6rem auto;
                background: #ff1493;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .register-avatar svg {
                width: 44px;
                height: 44px;
                stroke: #ffffff;
                fill: none;
                stroke-width: 2.2;
                stroke-linecap: round;
                stroke-linejoin: round;
            }

            .register-caption {
                text-align: center;
                color: #4a4a4a;
                margin-bottom: 0.3rem;
                font-weight: 600;
            }

            .register-wrap [data-testid="stTextInput"] {
                margin-bottom: 0.2rem;
            }

            .register-wrap [data-testid="stTextInput"] input {
                border: 1px solid #d9c2d7 !important;
                border-radius: 999px !important;
                background: #ffffff !important;
                color: #111111 !important;
                padding: 0.38rem 0.75rem !important;
            }

            .register-wrap [data-testid="stTextInput"] button {
                background: #ffffff !important;
                border-left: 1px solid #e7d1e3 !important;
                border-top: 1px solid #d9c2d7 !important;
                border-right: 1px solid #d9c2d7 !important;
                border-bottom: 1px solid #d9c2d7 !important;
                border-radius: 0 12px 12px 0 !important;
            }

            .register-wrap [data-testid="stTextInput"] button svg {
                fill: #000000 !important;
                color: #000000 !important;
                stroke: #000000 !important;
            }

            .register-wrap [data-testid="stSelectbox"] > div > div {
                border: 1px solid #d9c2d7 !important;
                border-radius: 999px !important;
                background: #ffffff !important;
                min-height: 2.15rem !important;
            }

            .register-wrap [data-testid="stButton"] button[kind="primary"] {
                border-radius: 999px !important;
                font-weight: 700 !important;
                letter-spacing: 1px !important;
                padding: 0.38rem 0.9rem !important;
                min-height: 2.15rem !important;
            }

            .register-wrap [data-testid="stButton"] button[kind="secondary"] {
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

    st.markdown('<div class="register-wrap">', unsafe_allow_html=True)
    logo_path = Path("assets/logoBArbg.png")
    if logo_path.exists():
        _, center_col, _ = st.columns([1, 2, 1])
        with center_col:
            st.image(str(logo_path), width=220)
    else:
        st.markdown('<div class="register-brand">BreastAID</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="register-avatar"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="4"></circle><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"></path></svg></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="register-caption">Create your account</div>', unsafe_allow_html=True)

    name = st.text_input("Full Name", placeholder="Full Name", key="register_name")
    email = st.text_input("Email", placeholder="Email", key="register_email")
    password = st.text_input("Password", type="password", placeholder="Password", key="register_password")

    role = st.selectbox(
        "Select Role",
        options=[None, "Public", "Doctor"],
        format_func=lambda x: "Choose a role..." if x is None else x,
        index=0,
        key="register_role",
    )

    if st.button("Sign Up", use_container_width=True, type="primary", key="register_submit"):
        if name and email and password and role:
            try:
                save_user_info(email, name, role, password)
                st.success("Account created! Redirecting to login...")
                st.session_state.page = "login"
                st.rerun()
            except Exception as e:
                st.error(f"Registration error: {e}")
        else:
            st.warning("Please fill in all fields")

    if st.button("Back to Login", key="back_to_login", use_container_width=True):
        st.session_state.page = "login"

    st.markdown('</div>', unsafe_allow_html=True)
