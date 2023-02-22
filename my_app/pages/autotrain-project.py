import os

import argilla as rg
import streamlit as st
import streamlit_analytics
from huggingface_hub import DatasetFilter, HfApi, ModelFilter
from streamlit_datalist import stDatalist
from utils.autotrain import get_projects, schedule_retrain, task_id_mapping
from utils.commons import argilla_login_flow, get_dataset_list, hf_login_flow

st.set_page_config(
    page_title="Argilla - Autotrain Project",
    page_icon=":writing_hand::skin-tone-4:",
    layout="wide",
)

streamlit_analytics.start_tracking(load_from_json=f"{__file__}.json")

api_url, api_key = argilla_login_flow("Autotrain Project")

st.write(
    """
    This page allows you to share your dataset from Argilla to HuggingFace Hub without requiring any code!
    In the background it uses `argilla.load().prepare_for_training()` and `datasets.push_to_hub()`.
    """
)

hf_auth_token, api = hf_login_flow()

api = HfApi(token=hf_auth_token)
user_info = api.whoami()
namespaces = [user_info["name"]] + [org["name"] for org in user_info["orgs"]]

projects = get_projects(hf_auth_token)
project_ids = [proj["proj_name"] for proj in projects]

autotrain_project_name = st.selectbox(
    "Autotrain project name", options=project_ids + ["other"]
)
if autotrain_project_name == "other":
    autotrain_project_name = st.text_input("Autotrain project name")

project_id = None
for proj in projects:
    if proj["proj_name"] == autotrain_project_name:
        project_id = proj["id"]
        break

target_namespace = st.selectbox(
    "Target HuggingFace namespace for saving trained model",
    options=namespaces,
    help="the namespace where the trained model should end up",
)

datasets_list = [
    f"{ds['owner']}/{ds['name']}" for ds in get_dataset_list(api_url, api_key)
]
dataset_argilla = st.selectbox(
    "Argilla or Hub Dataset Name", options=datasets_list + ["Custom HuggingFace Hub"]
)
dataset_argilla_name = dataset_argilla.split("/")[-1]
dataset_argilla_workspace = dataset_argilla.split("/")[0]


input_model = st.text_input(
    "Input Model [from the hub](https://huggingface.co/models)",
    value="bert-base-uncased",
    help="the base model to re-train",
)
potential_models = api.list_models(filter=ModelFilter(model_name=input_model))
if not len(potential_models) == 1:
    if not any([(input_model == model.modelId) for model in list(potential_models)]):
        st.warning("Please select a model from the list below:")
        st.write(potential_models)
        st.stop()

task = st.selectbox("Task", task_id_mapping)
task_id = task_id_mapping[task]
start = st.button("Schedule Autotrain")
if start:
    if dataset_argilla != "Custom HuggingFace Hub":
        rg.set_workspace(dataset_argilla_workspace)
        ds = rg.load(dataset_argilla_name)
        ds_ds = ds.prepare_for_training(framework="transformers", train_size=0.8)
        ds_ds.push_to_hub(
            f"{target_namespace}/{dataset_argilla_name}",
            token=hf_auth_token,
            private=True,
        )
    else:
        input_dataset = st.text_input(
            "Input Dataset from the hub [from the hub](https://huggingface.co/datasets)"
        )
        potential_datasets = api.list_datasets(
            filter=DatasetFilter(dataset_name=input_dataset)
        )
        if not len(potential_datasets) == 1:
            st.warning("Please select a correct dataset from the list below:")
            st.write(potential_datasets)
            st.stop()
    schedule_retrain(
        hf_auth_token=hf_auth_token,
        target_namespace=target_namespace,
        input_dataset=input_dataset,
        input_model=input_model,
        autotrain_project_prefix=autotrain_project_name,
        project_id=project_id,
        task_id=task_id,
    )


streamlit_analytics.stop_tracking(save_to_json=f"{__file__}.json")
