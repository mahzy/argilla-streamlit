from ast import literal_eval

import argilla as rg
import spacy
import streamlit as st
import streamlit_analytics
from streamlit_tags import st_tags
from text_highlighter import text_highlighter
from utils.commons import argilla_login_flow

st.set_page_config(
    page_title="Argilla - UI record creator",
    page_icon=":writing_hand::skin-tone-4:",
    layout="wide",
)

streamlit_analytics.start_tracking(load_from_json=f"{__file__}.json")


argilla_login_flow("UI record creator")

nlp = spacy.blank("en")
dataset = st.text_input("Dataset Name")

if dataset:
    dataset_type = st.selectbox(
        "Dataset Type", ["Text Classification", "Token Classification", "Text2Text"]
    )
    if dataset_type in ["Text Classification", "Token Classification"]:
        labels = st_tags(label="Labels", text="Press enter to add more")

        if not any(labels):
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
                annotation = st.multiselect("annotation", labels, default=labels)
            else:
                annotation = st.radio("annotation", labels, horizontal=True)

            record = rg.TextClassificationRecord(
                text=text, annotation=annotation, multi_label=multi_label
            )
        elif dataset_type == "Token Classification":
            annotation = text_highlighter(
                text=text,
                labels=labels,
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
