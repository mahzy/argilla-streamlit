import os

import argilla as rg
import streamlit as st
import streamlit_analytics
from text_highlighter import text_highlighter

st.set_page_config(
    page_title="Argilla Annotation Guideline and Comment Ability",
    page_icon=":memo:",
    layout="wide",
)

streamlit_analytics.start_tracking(load_from_json=f"{__file__}.json")
st.image("https://docs.argilla.io/en/latest/_static/images/logo-light-mode.svg")
st.title("Annotation Comment and Note support")

# login workflow
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


dataset = st.text_input("Dataset Name")

if dataset:
    records = rg.load(name=dataset, limit=1)

    if records:
        record = records[0]
        if isinstance(record, rg.TokenClassificationRecord) or isinstance(
            record, rg.TokenClassificationRecord
        ):
            labels = st.text_input("Labels")
            split_labels = labels.split(",")
            split_labels = [label.strip() for label in split_labels]

            if not any(split_labels):
                st.warning("No labels provided")
                st.stop()
            if isinstance(record, rg.TokenClassificationRecord):
                multi_label = st.radio("multi label", [False, True], horizontal=True)
            else:
                multi_label = False
else:
    st.warning("No dataset provided")
    st.stop()

st.write("This is an annotation guideline. Label A is for cats, label B is for dogs.")
query = st.text_input("Query", value="status: Default", key="query")
if not query:
    query = None

records = rg.load(name=dataset, limit=1, query=query)

if records:
    records = records[0]

    if isinstance(records, rg.TokenClassificationRecord):
        if records.annotation:
            old_annotation = [
                {
                    "start": an[1],
                    "end": an[2],
                    "tag": an[0],
                    "text": records.text[an[1] : an[2]],
                }
                for an in records.annotation
            ]
        else:
            old_annotation = None
        annotation = text_highlighter(
            text=records.text,
            labels=split_labels,
            annotations=old_annotation,
        )
        annotation = [(an["tag"], an["start"], an["end"]) for an in annotation]

    elif isinstance(records, rg.TextClassificationRecord):
        if records.inputs is not None:
            st.write(records.inputs)
        else:
            st.write(records.text)

        if records.multi_label:
            annotation = st.multiselect("annotation", split_labels, records.annotation)
        else:
            annotation = st.radio(
                "annotation",
                split_labels,
                split_labels.index(records.annotation),
                horizontal=True,
            )

    elif isinstance(records, rg.Text2TextRecord):
        st.write(records.text)
        st.text_area(records.annotation)

    try:
        records.__class__(records.text, annotation)
        records.annotation = annotation
    except Exception as e:
        st.write(e)

    if records.metadata:
        if "comment" in records.metadata:
            input_comment = records.metadata["comment"]
        else:
            input_comment = ""
    else:
        input_comment = ""

    comment = st.text_input("comment", value=input_comment)
    if records.metadata:
        records.metadata["comment/note"] = comment
    else:
        records.metadata = {"comment": comment}

    save = st.button("Save")
    if save:
        rg.log(records, dataset)
        records = rg.load(dataset=dataset, limit=1, query=query)
        st.success("Saved")
else:
    st.warning("No records found")

streamlit_analytics.stop_tracking(save_to_json=f"{__file__}.json")
