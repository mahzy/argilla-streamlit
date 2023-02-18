import os
from ast import literal_eval

import argilla as rg
import spacy
import streamlit as st
import streamlit_analytics
from _utils import login_workflow
from text_highlighter import text_highlighter

st.set_page_config(
    page_title="Argilla - UI record creator",
    page_icon=":writing_hand::skin-tone-4:",
    layout="wide",
)

streamlit_analytics.start_tracking(load_from_json=f"{__file__}.json")
st.image("https://docs.argilla.io/en/latest/_static/images/logo-light-mode.svg")
st.title("UI record creator")

# loging workflow
login_workflow()

nlp = spacy.blank("en")
dataset = st.text_input("Dataset Name")

if dataset:
    dataset_type = st.selectbox(
        "Dataset Type", ["Text Classification", "Token Classification", "Text2Text"]
    )
    if dataset_type in ["Text Classification", "Token Classification"]:
        labels = st.text_input("Labels")
        split_labels = labels.split(",")
        split_labels = [label.strip() for label in split_labels]

        if not any(split_labels):
            st.warning("No labels provided")
            st.stop()
        if dataset_type == "Text Classification":
            multi_label = st.radio("multi label", [False, True], horizontal=True)
        else:
            multi_label = False
    text = st.text_area("Text")

    if text:
        if dataset_type == "Text Classification":
            if multi_label:
                annotation = st.multiselect(
                    "annotation", split_labels, default=split_labels
                )
            else:
                annotation = st.radio("annotation", split_labels, horizontal=True)

            record = rg.TextClassificationRecord(
                text=text, annotation=annotation, multi_label=multi_label
            )
        elif dataset_type == "Token Classification":
            annotation = text_highlighter(
                text=text,
                labels=split_labels,
            )
            if annotation:
                annotation = [(an["tag"], an["start"], an["end"]) for an in annotation]

            tokens = [token.text for token in nlp(text)]
            record = rg.TokenClassificationRecord(
                text=text, tokens=tokens, annotation=annotation
            )

        elif dataset_type == "Text2Text":
            annotation = st.text_area("Annotation")
            record = rg.Text2TextRecord(text=text, annotation=annotation)
        metadata = st.text_area("Metadata", value="{}")
        metadata = literal_eval(metadata)
        record.metadata = metadata
        st.write(record)
    else:
        st.warning("Please enter text")

    save = st.button("Save")
    if save:
        rg.log(record, dataset)
        st.success("Saved")
else:
    st.warning("Please enter dataset name")

streamlit_analytics.stop_tracking(save_to_json=f"{__file__}.json")
