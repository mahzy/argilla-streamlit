import os

import argilla as rg
import streamlit as st
from huggingface_hub import HfApi


def argilla_login_flow(title: str) -> str:
    """
    It tries to log in to Argilla
    using the environment variables `ARGILLA_API_URL` and `ARGILLA_API_KEY`. If they
    are not set, it shows a sidebar with two text inputs to manually enter the API URL
    and API Key

    Args:
      title: The title of the app.

    Returns:
      The api_url is being returned.
    """
    st.image("https://docs.argilla.io/en/latest/_static/images/logo-light-mode.svg")

    api_url = None
    if os.environ.get("ARGILLA_API_URL") and os.environ.get("ARGILLA_API_KEY"):
        api_url = os.environ.get("ARGILLA_API_URL")
        api_key = os.environ.get("ARGILLA_API_KEY")
        rg.init(
            api_url=api_url,
            api_key=api_key,
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
                "Invalid API URL or API Key. Use a correct manual input or, even"
                " better, set `ARGILLA_API_URL` and `ARGILLA_API_KEY` as environment"
                " variables to avoid this step."
            )
    st.title(title)
    return api_url


def hf_login_flow():
    """
    It checks if the user has provided a Hugging Face API token in the environment variable
    `HF_AUTH_TOKEN` or in the sidebar. If not, it displays an error message and stops the app

    Returns:
      A tuple of the token and the api
    """
    hf_auth_token = os.environ.get("HF_AUTH_TOKEN", "")
    if not hf_auth_token:
        hf_auth_token = st.sidebar.text_input(
            "HuggingFace [User Access Tokens](https://huggingface.co/settings/tokens)",
            os.environ.get("HF_AUTH_TOKEN", ""),
        )
    if not hf_auth_token:
        st.error(
            "Please provide a HuggingFace [User Access"
            " Tokens](https://huggingface.co/settings/tokens) in the sidebar or set"
            " `HF_AUTH_TOKEN` as environment variable"
        )
        st.stop()
    api = HfApi(token=hf_auth_token)
    return hf_auth_token, api


# def record_info():
#     with st.expander("Dataset Type Info"):
#         if dataset_type == "Text Classification":
#             st.write(rg.TextClassificationRecord.__doc__)
#         elif dataset_type == "Token Classification":
#             st.write(rg.TokenClassificationRecord.__doc__)
#         else:
#             st.write(rg.Text2TextRecord.__doc__)
