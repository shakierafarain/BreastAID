"""Public landing page shown before login."""
from pathlib import Path

import streamlit as st


def show_landing_page():
    """Display public landing page with breast cancer information and news highlights."""
    st.markdown(
        """
        <style>
            .landing-shell {
                max-width: 1160px;
                margin: 0 auto;
                padding: 0.3rem 0 1.8rem 0;
            }

            .landing-nav {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0.2rem 0 0.8rem 0;
            }

            .landing-brand {
                font-size: 1.5rem;
                font-weight: 900;
                letter-spacing: 0.6px;
                color: #d4147d;
                margin: 0;
            }

            .landing-links {
                display: flex;
                gap: 1.4rem;
                color: #2c2130;
                font-weight: 600;
                opacity: 0.9;
                font-size: 0.95rem;
            }

            .landing-hero {
                margin-top: 0.35rem;
                border: 1px solid #f4d9e9;
                border-radius: 22px;
                background:
                    radial-gradient(circle at 18% 22%, rgba(255, 20, 147, 0.13), transparent 55%),
                    radial-gradient(circle at 82% 24%, rgba(255, 182, 204, 0.2), transparent 52%),
                    #ffffff;
                padding: 2.1rem;
                box-shadow: 0 18px 45px rgba(255, 20, 147, 0.08);
            }

            .hero-title {
                margin: 0;
                font-size: clamp(2rem, 4vw, 3.1rem);
                line-height: 1.08;
                color: #241f27;
                font-weight: 800;
            }

            .hero-sub {
                margin: 1rem 0 1.2rem 0;
                max-width: 540px;
                color: #3d3242;
                font-size: 1.06rem;
                line-height: 1.55;
            }

            .hero-chip-wrap {
                display: flex;
                flex-wrap: wrap;
                gap: 0.55rem;
                margin-bottom: 0.30rem;
            }

            .hero-chip {
                border: 1px solid #efbfd8;
                background: #fff7fc;
                color: #7a2f5d;
                border-radius: 999px;
                font-size: 0.88rem;
                padding: 0.32rem 0.76rem;
                font-weight: 600;
            }

            .hero-visual {
                border-radius: 24px;
                height: 100%;
                min-height: 280px;
                background:
                    radial-gradient(circle at 32% 24%, rgba(255,255,255,0.92), rgba(255,255,255,0) 35%),
                    radial-gradient(circle at 78% 76%, rgba(255, 20, 147, 0.28), rgba(255, 20, 147, 0.07) 45%, rgba(255,255,255,0) 72%),
                    linear-gradient(145deg, #ffecf6, #ffd9ec 45%, #f9e8ff);
                border: 1px solid #efbfd8;
                position: relative;
                overflow: hidden;
            }

            .hero-visual::before {
                content: "";
                position: absolute;
                width: 270px;
                height: 270px;
                border-radius: 999px;
                border: 2px solid rgba(212, 20, 125, 0.2);
                top: -95px;
                right: -60px;
            }

            .hero-visual::after {
                content: "";
                position: absolute;
                width: 210px;
                height: 210px;
                border-radius: 999px;
                border: 2px dashed rgba(212, 20, 125, 0.24);
                bottom: -85px;
                left: -45px;
            }

            .section-title {
                font-size: 1.5rem;
                color: #271f2b;
                margin: 2rem 0 0.55rem 0;
            }

            .section-text {
                color: #3d3242;
                line-height: 1.62;
                margin-bottom: 0.95rem;
            }

            .news-card {
                border: 1px solid #f0d2e4;
                border-radius: 16px;
                background: #fff;
                padding: 1rem;
                min-height: 172px;
                box-shadow: 0 10px 20px rgba(178, 63, 133, 0.07);
            }

            .news-tag {
                display: inline-block;
                border-radius: 999px;
                font-size: 0.75rem;
                padding: 0.2rem 0.58rem;
                background: #fff0f8;
                color: #94275f;
                border: 1px solid #efbfd8;
                margin-bottom: 0.5rem;
                font-weight: 700;
            }

            .news-title {
                margin: 0 0 0.45rem 0;
                color: #251f2a;
                font-size: 1rem;
            }

            .news-text {
                margin: 0;
                color: #44364a;
                font-size: 0.93rem;
                line-height: 1.5;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="landing-shell">', unsafe_allow_html=True)

    nav_col_1, nav_col_2, nav_col_3 = st.columns([5.2, 2.6, 1.2])
    with nav_col_1:
        logo_path = Path("assets/logoBArbg.png")
        if logo_path.exists():
            st.image(str(logo_path), width=190)
        else:
            st.markdown('<div class="landing-brand">BreastAID</div>', unsafe_allow_html=True)
    with nav_col_2:
        st.markdown(
            '<div class="landing-links"><span>Learn</span><span>Trends</span><span>Support</span></div>',
            unsafe_allow_html=True,
        )
    with nav_col_3:
        if st.button("Log in", key="landing_login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

    hero_left, hero_right = st.columns([1.35, 1])

    with hero_left:
        st.markdown(
            """
            <h1 class="hero-title">Trusted guidance for breast health awareness</h1>
            <p class="hero-sub">
                Learn the basics of breast cancer, understand risk factors, and stay updated with
                prevention trends. Early awareness and screening can make a real difference.
            </p>
            <div class="hero-chip-wrap">
                <span class="hero-chip">Early Detection</span>
                <span class="hero-chip">Risk Assessment</span>
                <span class="hero-chip">Reliable Guidance</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        cta_1 = st.columns([1])[0]
        with cta_1:
            if st.button("Start Risk Assessment", key="landing_start", use_container_width=False):
                st.session_state.page = "login"
                st.rerun()

    with hero_right:
        ribbon_path = Path("assets/ribbonpic.png")

        if ribbon_path.exists():
            st.image(str(ribbon_path), use_container_width=True)
        else:
            st.markdown('<div class="hero-visual"></div>', unsafe_allow_html=True)

    st.markdown('<h2 class="section-title">What is breast cancer?</h2>', unsafe_allow_html=True)
    st.markdown(
        """
        <p class="section-text">
            Breast cancer is a disease where cells in the breast grow abnormally and form a tumor.
            It can affect both women and men, though it is far more common in women. Regular screening,
            healthy lifestyle habits, and early consultation with healthcare professionals can help improve outcomes.
        </p>
        """,
        unsafe_allow_html=True,
    )

    info_a, info_b = st.columns(2)
    with info_a:
        st.info("Common signs include a new lump, change in breast shape, skin dimpling, or unusual nipple discharge.")
    with info_b:
        st.info("Many breast changes are not cancer, but any persistent change should be checked by a clinician.")

    st.markdown('<h2 class="section-title">Trends and news</h2>', unsafe_allow_html=True)

    news_1, news_2, news_3 = st.columns(3)

    with news_1:
        st.markdown(
            """
            <div class="news-card">
                <span class="news-tag">Screening</span>
                <h3 class="news-title">More programs are adopting digital breast tomosynthesis</h3>
                <p class="news-text">3D mammography is expanding in many clinics to improve imaging clarity, especially for dense breast tissue.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with news_2:
        st.markdown(
            """
            <div class="news-card">
                <span class="news-tag">Technology</span>
                <h3 class="news-title">AI-assisted image reading continues to grow</h3>
                <p class="news-text">Health systems are exploring AI tools to support radiologists, helping prioritize suspicious findings faster.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with news_3:
        st.markdown(
            """
            <div class="news-card">
                <span class="news-tag">Awareness</span>
                <h3 class="news-title">Community education improves early consultation rates</h3>
                <p class="news-text">Local awareness campaigns are encouraging people to seek checkups sooner after noticing breast changes.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)
