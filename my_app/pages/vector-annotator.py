import argilla as rg
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit_analytics
from streamlit_plotly_events import plotly_events
from streamlit_tags import st_tags
from umap import UMAP
from utils.commons import argilla_login_flow

st.set_page_config(
    page_title="Argilla - Vector Annotator",
    page_icon=":writing_hand::skin-tone-4:",
    layout="wide",
)

streamlit_analytics.start_tracking(load_from_json=f"{__file__}.json")

# login workflow
api_url = argilla_login_flow("Vector Annotator")

dataset_argilla = st.text_input("Dataset Argilla Name", "ray-summit")
labels = st_tags(label="Labels", text="Press enter to add more")
query = st.text_input("Query", value="status: Validated")
if dataset_argilla and labels:
    ds = rg.load(dataset_argilla, query=f"({query}) AND vectors: *", limit=1000)
    df = ds.to_pandas()
    if df.empty:
        st.warning("No dataset found")
        st.stop()
    vectors = df.vectors.values
    if len(list(vectors[0].keys())) > 1:
        vector_name = st.selectbox("Select vector", list(vectors[0].keys()))
    else:
        vector_name = list(vectors[0].keys())[0]
    vectors = np.array([v[vector_name] for v in vectors])

    # Reduce the dimensions with UMAP
    umap = UMAP()
    X_tfm = umap.fit_transform(vectors)

    # # Apply coordinates
    df["x"] = X_tfm[:, 0]
    df["y"] = X_tfm[:, 1]

    fig = px.scatter(
        data_frame=df,
        x="x",
        y="y",
        hover_data={
            "text": True,
            "prediction": True,
            "annotation": True,
            "x": False,
            "y": False,
        },
        color="annotation",
        title="Vectors",
    )

    selected_points = plotly_events(fig, select_event=True, click_event=False)
    df_new = st.write(pd.DataFrame(selected_points))
    st.write(df_new)
    if ds[0].multi_label:
        annotation = st.multiselect("annotation", labels, default=labels)
    else:
        annotation = st.radio("annotation", labels, horizontal=True)
    if st.button("Annotate"):
        df_new["annotation"] = annotation

else:
    st.warning("No dataset found")
