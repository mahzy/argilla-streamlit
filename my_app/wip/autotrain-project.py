import argilla as rg
import streamlit as st
import streamlit_analytics
from huggingface_hub import DatasetFilter, HfApi, ModelFilter
from streamlit_datalist import stDatalist
from utils.autotrain import get_projects, schedule_retrain, task_id_mapping
from utils.commons import argilla_login_flow, hf_login_flow

st.set_page_config(
    page_title="Argilla - Autotrain Project",
    page_icon=":writing_hand::skin-tone-4:",
    layout="wide",
)

streamlit_analytics.start_tracking(load_from_json=f"{__file__}.json")

# login workflow
api_url = argilla_login_flow("Autotrain Project")
hf_auth_token, api = hf_login_flow()

user_info = api.whoami()
namespaces = [user_info["name"]] + [org["name"] for org in user_info["orgs"]]

projects = get_projects(hf_auth_token)
project_ids = [proj["proj_name"] for proj in projects]

autotrain_project_name = stDatalist(
    "Select an existing AutoTrain project (press arrow down) or create a new one",
    project_ids,
)
project_id = None
for proj in projects:
    if proj["proj_name"] == autotrain_project_name:
        project_id = proj["id"]
        break

target_namespace = st.selectbox(
    "Target namespace for saving trained model",
    options=namespaces,
    help="the namespace where the trained model should end up",
)

input_dataset = st.text_input(
    "Input Dataset from the hub [from the hub](https://huggingface.co/models) or"
    f" [Argilla]({api_url})",
    "davidberenstein1957/ray-summit-classy",
    help="the dataset on which the model will be trained",
)
try:
    ds = rg.load("input_dataset")
    ds_ds = ds.prepare_for_training(framework="transformers", train_size=0.8)
    ds_ds.push_to_hub(input_dataset, token=hf_auth_token)
except:
    potential_datasets = api.list_datasets(
        filter=DatasetFilter(dataset_name=input_dataset)
    )
    if not len(potential_datasets) == 1:
        st.warning("Please select a dataset from the list below:")
        st.write(potential_datasets)
        st.stop()
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
