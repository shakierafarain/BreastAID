"""Firebase configuration and initialization."""
import os
import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore


@st.cache_resource
def get_db():
    """Get Firestore database instance — initialized and cached once.

    - When deployed on Streamlit Cloud: reads credentials from st.secrets
    - When running locally: reads from firebase_key.json file
    """
    if not firebase_admin._apps:
        try:
            # ── Streamlit Cloud (secrets) ──────────────────────
            if "firebase" in st.secrets:
                cred_dict = dict(st.secrets["firebase"])
                # private_key newlines are escaped in TOML — restore them
                cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
                cred = credentials.Certificate(cred_dict)

            # ── Local development (key file) ───────────────────
            else:
                base_dir = os.path.dirname(__file__)
                key_path = os.path.join(base_dir, "firebase_key.json")
                cred = credentials.Certificate(key_path)

            firebase_admin.initialize_app(cred)

        except Exception as e:
            st.error(f"Firebase initialization failed: {e}")
            raise e

    return firestore.client()


def init_firebase():
    """Kept for backward compatibility — actual init happens inside get_db()."""
    get_db()