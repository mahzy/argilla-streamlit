import os

import argilla as rg
import streamlit as st


def login():
    if os.environ.get("ARGILLA_API_URL") and os.environ.get("ARGILLA_API_KEY"):
        rg.init(
            api_url=os.environ.get("ARGILLA_API_URL"),
            api_key=os.environ.get("ARGILLA_API_KEY"),
        )
        st.success(f"Logged in at {os.environ.get('ARGILLA_API_URL')}")
    else:
        try:
            api_url = st.sidebar.text_input(
                "API URL", value="https://dvilasuero-argilla-template-space.hf.space"
            )
            api_key = st.sidebar.text_input("API Key", value="team.apikey")
            rg.init(
                api_url=api_url,
                api_key=api_key,
            )
            st.success(f"Logged in at {api_url}")

        except Exception:
            st.error("Invalid API URL or API Key")
