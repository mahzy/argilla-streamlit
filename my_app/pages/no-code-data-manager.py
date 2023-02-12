import argilla as rg
import pandas as pd
import spacy
import streamlit as st
import streamlit_analytics

st.set_page_config(
    page_title="Argilla NoCode Data Manager", page_icon="💾", layout="wide"
)

streamlit_analytics.start_tracking(load_from_json=f"{__file__}.json")

st.image("https://docs.argilla.io/en/latest/_static/images/logo-light-mode.svg")
st.title("No-code data manager")
api_url = st.sidebar.text_input(
    "API URL", value="https://dvilasuero-argilla-template-space.hf.space"
)
api_key = st.sidebar.text_input("API Key", value="team.apikey")
action = st.sidebar.selectbox("Action", ["✍️ Upload Dataset", "💾 Download dataset"])

if action == "✍️ Upload Dataset":
    st.subheader(action)
    dataset_type = st.selectbox(
        "Dataset Type", ["Text Classification", "Token Classification"]
    )
    dataset_name = st.text_input("Dataset Name", value="", key="dataset_name")

    records = []
    uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Dataset preview:", df.head())
        string_columns = [col for col in df.columns if df[col].dtype == "object"]
        if len(string_columns) > 0:
            if dataset_type == "Text Classification":
                column_select = st.multiselect("Select columns", string_columns)
                if column_select:
                    records = []
                    for i, row in df[column_select].iterrows():
                        record = rg.TextClassificationRecord(
                            inputs={col: row[col] for col in column_select}
                        )
                        records.append(record)
            elif dataset_type == "Token Classification":
                column_select = st.selectbox("Select a Column", string_columns)
                if column_select:
                    # Load the spaCy en_core_web_sm model
                    nlp = spacy.blank("en")
                    # Create a new column in the DataFrame with the tokenized text
                    df["tokenized_text"] = df[column_select].apply(
                        lambda x: [token.text for token in nlp(x)]
                    )
                    st.write("Tokenized Text:", df["tokenized_text"].head(3))
                    for i, row in df.iterrows():
                        record = rg.TokenClassificationRecord(
                            text=row[column_select],
                            tokens=row["tokenized_text"],
                        )
                        records.append(record)
            if len(records) > 0:
                if st.button("Log data into Argilla"):
                    rg.init(api_url=api_url, api_key=api_key)
                    output = rg.log(records=records, name=dataset_name)
                    st.write(output)
                    st.write(f"{output.processed} records added to {api_url}")

elif action == "💾 Download dataset":
    st.title(action)
    dataset_name_down = st.text_input("Dataset Name", value="", key="dataset_name")
    api_url = st.text_input(
        "API URL", value="https://dvilasuero-argilla-template-space.hf.space"
    )
    api_key = st.text_input("API Key", value="team.apikey")
    if dataset_name_down:
        rg.init(api_url=api_url, api_key=api_key)
        dataset = rg.load(dataset_name_down).to_pandas()
        st.write("Dataset preview:", dataset.head())
        st.download_button(
            label="Download as CSV",
            data=dataset.to_csv(index=False).encode("utf-8"),
            file_name=f"{dataset_name_down}.csv",
            mime="text/csv",
        )
        st.download_button(
            label="Download as JSON!",
            data=dataset.to_json(orient="records", lines=True).encode("utf-8"),
            file_name=f"{dataset_name_down}.json",
            mime="application/json",
        )

streamlit_analytics.stop_tracking(save_to_json=f"{__file__}.json")
