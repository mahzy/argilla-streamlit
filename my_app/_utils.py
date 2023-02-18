import os

import argilla as rg
import streamlit as st


def login_workflow():
    if os.environ.get("ARGILLA_API_URL") and os.environ.get("ARGILLA_API_KEY"):
        rg.init(
            api_url=os.environ.get("ARGILLA_API_URL"),
            api_key=os.environ.get("ARGILLA_API_KEY"),
        )
        st.success(
            f"Logged in at {os.environ.get('ARGILLA_API_URL')}, and workspace is"
            f" {rg.get_workspace()}"
        )
    else:
        try:
            api_url = st.sidebar.text_input(
                "API URL", "https://dvilasuero-argilla-template-space.hf.space"
            )
            api_key = st.sidebar.text_input("API Key", value="team.apikey")
            rg.init(
                api_url=api_url,
                api_key=api_key,
            )
            st.success(
                f"Logged in at {api_url}, and workspace is {rg.get_workspace()}. Set"
                " `ARGILLA_API_URL` and `ARGILLA_API_KEY` as environment variables to"
                " avoid this step."
            )
        except Exception:
            st.error(
                "Invalid API URL or API Key. Use a correct manual input or even better,"
                " set `ARGILLA_API_URL` and `ARGILLA_API_KEY` as environment variables"
                " to avoid this step."
            )
