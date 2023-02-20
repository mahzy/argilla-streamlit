import os

import argilla as rg
import datasets
import streamlit as st
import streamlit_analytics
from utils.commons import argilla_login_flow, hf_login_flow

st.set_page_config(
    page_title="Argilla - Hub Exporter",
    page_icon=":writing_hand::skin-tone-4:",
    layout="wide",
)

streamlit_analytics.start_tracking(load_from_json=f"{__file__}.json")

argilla_login_flow("Hub Exporter")
hf_auth_token, api = hf_login_flow()

st.write(
    """
    This page allows you to share your dataset from Argilla to HuggingFace Hub without requiring any code!
    In the background it uses `argilla.load().prepare_for_training()` and `datasets.push_to_hub()`.
    """
)

user_info = api.whoami()
namespaces = [user_info["name"]] + [org["name"] for org in user_info["orgs"]]

dataset_argilla = st.text_input("Dataset Argilla Name")
target_namespace = st.selectbox(
    "Target HF organization for saving trained model",
    options=namespaces,
    help="the namespace where the trained model should end up",
)
dataset_huggingface = st.text_input(
    "Dataset HuggingFace Name", f"{target_namespace}/{dataset_argilla}"
)

if dataset_argilla:
    dataset_huggingface = st.text_input(
        "Dataset HuggingFace Name", f"{target_namespace}/{dataset_argilla}"
    )
    try:
        query = st.text_input("Query", value="status: Validated")
        with st.spinner(text="Loading dataset..."):
            ds = rg.load(dataset_argilla, query=query)
        st.write("Below is a subset of the dataframe", ds.to_pandas().head(5))
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
else:
    st.warning("Please enter a dataset name")

streamlit_analytics.stop_tracking(save_to_json=f"{__file__}.json")
