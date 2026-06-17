"""Application theme and styling."""
import streamlit as st

def apply_theme():
    """Apply light pink-and-white theme using the user's pink accent."""
    st.markdown(
        """
        <style>
            :root {
                --primary-pink: #ff1493; /* vivid pink */
                --soft-pink: #ffe6f0;   /* very light pink */
                --white-bg: #ffffff;
                --muted-text: #111111; /* darker/near-black for legibility on white bg */
                --soft-gray: #9b9b9b;
                --border-light: #f0d9e6;
            }

            * { font-family: 'Segoe UI', Trebuchet MS, sans-serif; }

            /* App background: clean white with a subtle pink gradient at top-left */
            .stApp {
                background: linear-gradient(135deg, var(--soft-pink) 0%, var(--white-bg) 35%);
            }

            /* Ensure default text (labels, placeholders, form labels) is readable on white */
            .stApp, .stApp * {
                color: var(--muted-text) !important;
            }

            /* Main Title */
            .main-title {
                font-size: 2.5rem;
                font-weight: 700;
                color: var(--primary-pink);
                margin-bottom: 0.5rem;
            }

            /* Subtitle */
            .sub-title {
                color: var(--muted-text);
                font-size: 1.1rem;
                margin-bottom: 1rem;
                font-weight: 600;
            }

            /* Card Container */
            .card {
                border: 1px solid var(--border-light);
                border-radius: 12px;
                padding: 1.2rem;
                background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(255,255,255,0.95));
                margin-top: 1rem;
                box-shadow: 0 6px 18px rgba(255, 20, 147, 0.08);
            }

            /* Progress Strip */
            .step-strip {
                background: linear-gradient(90deg, rgba(255, 20, 147, 0.06) 0%, rgba(255, 255, 255, 0) 100%);
                border: 1px solid var(--border-light);
                border-radius: 10px;
                padding: 0.9rem 1.2rem;
                margin-bottom: 1rem;
                color: var(--muted-text);
                font-weight: 600;
            }

            /* Risk Box */
            .risk-box {
                border-radius: 10px;
                padding: 1rem;
                background: linear-gradient(135deg, rgba(255, 20, 147, 0.06) 0%, rgba(255, 20, 147, 0.03) 100%);
                border: 1px solid var(--border-light);
                margin: 0.6rem 0 1rem 0;
                font-size: 1rem;
                color: var(--muted-text);
            }

            /* Input Fields */
            .stTextInput > div > div > input {
                border: 1px solid var(--border-light) !important;
                border-radius: 8px !important;
                padding: 0.7rem !important;
                font-size: 1rem !important;
                background: var(--white-bg) !important;
                color: var(--muted-text) !important;
            }

            .stTextInput > div > div > input:focus {
                border: 1.5px solid var(--primary-pink) !important;
                box-shadow: 0 0 0 4px rgba(255, 20, 147, 0.06) !important;
            }

            .stTextInput > div > div > input::placeholder { color: var(--soft-gray) !important; }

            /* Password input eye icon - keep black */
            .stTextInput button svg { fill: #000 !important; color: #000 !important; stroke: #000 !important; }
            input[type="password"]::after { color: #000 !important; }

            /* Buttons */
            .stButton > button {
                background: linear-gradient(135deg, var(--primary-pink) 0%, #ff6ea1 100%);
                color: white !important;
                border: none !important;
                border-radius: 8px !important;
                padding: 0.6rem 1.4rem !important;
                font-weight: 700 !important;
                letter-spacing: 0.3px !important;
                box-shadow: 0 6px 18px rgba(255, 20, 147, 0.18) !important;
            }

            .stButton > button:hover { transform: translateY(-2px); }

            /* Radio Buttons */
            .stRadio > div { gap: 1.2rem !important; }
            .stRadio > div > label { font-weight: 600 !important; color: var(--muted-text) !important; }

            /* Alerts */
            .stWarning { background-color: rgba(255, 200, 220, 0.8) !important; color: var(--muted-text) !important; border-left: 4px solid var(--primary-pink) !important; }
            .stSuccess { background-color: rgba(220, 255, 235, 0.9) !important; color: var(--muted-text) !important; border-left: 4px solid #6fbf8f !important; }
            .stError { background-color: rgba(255, 230, 240, 0.9) !important; color: var(--muted-text) !important; border-left: 4px solid #ff6b9d !important; }
            .stInfo { background-color: rgba(240, 245, 255, 0.9) !important; color: var(--muted-text) !important; border-left: 4px solid #7a9bd6 !important; }

            /* Text Styling */
            .stMarkdown h1 { color: var(--muted-text) !important; }
            .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 { color: var(--muted-text) !important; font-weight: 700 !important; }
            .stMarkdown p { color: var(--muted-text) !important; line-height: 1.6 !important; }
            .stMarkdown a { color: var(--primary-pink) !important; }

            /* Separator */
            hr { border: none !important; height: 1px !important; background: linear-gradient(90deg, transparent, var(--border-light), transparent) !important; margin: 1.6rem 0 !important; }

            /* Statistics Cards */
            .stat-card { background: linear-gradient(180deg, #fff 0%, var(--soft-pink) 100%); border: 1px solid var(--border-light); border-radius: 10px; padding: 1rem; text-align: center; }
            .stat-card:hover { transform: translateY(-4px); box-shadow: 0 10px 30px rgba(255, 20, 147, 0.08); }
            .stat-number { font-size: 1.8rem; font-weight: 800; color: var(--primary-pink); margin-bottom: 0.3rem; }
            .stat-label { font-size: 0.95rem; color: var(--soft-gray); font-weight: 600; }

            /* Expander */
            .streamlit-expanderHeader { color: var(--muted-text) !important; }

            /* Metric */
            [data-testid="metric-container"] { background-color: rgba(255,255,255,0.95) !important; border: 1px solid var(--border-light) !important; border-radius: 10px !important; padding: 0.9rem !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

