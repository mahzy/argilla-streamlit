import os

import argilla as rg
import datasets
import streamlit as st
import streamlit_analytics
from _utils import login_workflow

st.set_page_config(
    page_title="Argilla - Hub Exporter",
    page_icon=":writing_hand::skin-tone-4:",
    layout="wide",
)

streamlit_analytics.start_tracking(load_from_json=f"{__file__}.json")
st.image("https://docs.argilla.io/en/latest/_static/images/logo-light-mode.svg")
st.title("Hub Exporter")

# login workflow
login_workflow()

hf_auth_token = os.environ.get("HF_AUTH_TOKEN", "")
if not hf_auth_token:
    hf_auth_token = st.sidebar.text_input(
        "HuggingFace [User Access Tokens](https://huggingface.co/settings/tokens)",
        os.environ.get("HF_AUTH_TOKEN", ""),
    )
if not hf_auth_token:
    st.error(
        "Please provide a HuggingFace [User Access"
        " Tokens](https://huggingface.co/settings/tokens) or set `HF_AUTH_TOKEN` as"
        " environment variable"
    )
    st.stop()

dataset_argilla = st.text_input("Dataset Argilla Name")
dataset_huggingface = st.text_input("Dataset HuggingFace Name", dataset_argilla)

if dataset_argilla:
    try:
        query = st.text_input("Query", value="status: Validated")
        with st.spinner(text="Loading dataset..."):
            ds = rg.load(dataset_argilla, query=query)
        st.write("Below is a dataframe", ds.to_pandas().head(5))
        train_size = st.number_input(
            "Train size", value=0.8, min_value=0.0, max_value=1.0
        )
        private = st.checkbox("Use Private Repo", value=False)
        button = st.button("Export to HuggingFace")

        if button:
            with st.spinner(text="Export in progress..."):
                ds_ds = ds.prepare_for_training(
                    framework="transformers", train_size=train_size
                )
                ds_ds.push_to_hub(dataset_huggingface, token=hf_auth_token)
            st.success(
                "Dataset pushed to HuggingFace and available"
                f" [here](https://huggingface.co/datasets?sort=downloads&search={dataset_huggingface}"
            )
    except Exception as e:
        st.error("Invalid dataset name or query")
        st.write(e)

streamlit_analytics.stop_tracking(save_to_json=f"{__file__}.json")
