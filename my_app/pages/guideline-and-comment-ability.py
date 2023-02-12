import argilla as rg
import streamlit as st
import streamlit_analytics
from text_highlighter import text_highlighter

st.set_page_config(
    page_title="Annotation Guideline and Comment Ability", page_icon=":", layout="wide"
)

streamlit_analytics.start_tracking(load_from_json=f"{__file__}.json")
st.image("https://docs.argilla.io/en/latest/_static/images/logo-light-mode.svg")
st.title("Annotation Comment and Note support")

api_url = st.sidebar.text_input(
    "API URL", value="https://dvilasuero-argilla-template-space.hf.space"
)
api_key = st.sidebar.text_input("API Key", value="team.apikey")
# rg.init(
#     api_url=api_url,
#     api_key=api_key,
# )
labels = st.text_input("Comma separated labels")
split_labels = labels.split(",")
dataset = st.text_input("Dataset Name")

if dataset and labels:
    st.write(
        "This is an annotation guideline. Label A is for cats, label B is for dogs."
    )
    query = st.text_input("Query", value="status: Default", key="query")
    if not query:
        query = None

    try:
        records = rg.load(name=dataset, limit=1, query=query)
    except Exception as e:
        st.write(e)

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
                colors=["red"],
                annotations=old_annotation,
            )
            annotation = [(an["tag"], an["start"], an["end"]) for an in annotation]

        elif isinstance(records, rg.TextClassificationRecord):
            st.write(records.inputs)

            if records.multi_label:
                annotation = st.multiselect(
                    "annotation", split_labels, records.annotation
                )
            else:
                annotation = st.selectbox(
                    "annotation",
                    split_labels,
                    split_labels.index(records.annotation),
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
    else:
        st.warning("No records found")
else:
    st.warning("Please enter dataset name and labels")
streamlit_analytics.stop_tracking(save_to_json=f"{__file__}.json")
