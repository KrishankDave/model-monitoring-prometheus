import os
import json
import requests
import streamlit as st


# API URLs
MODEL_API_URL = os.getenv(
    "MODEL_API_URL",
    "http://localhost:8000/predict"
)

MONITORING_API_URL = os.getenv(
    "MONITORING_API_URL",
    "http://localhost:5000/metrics"
)


# Decode the model API response.
# Your existing API returns JSON inside a JSON string,
# so we handle both formats.
def decode_response(response):
    data = response.json()

    if isinstance(data, str):
        data = json.loads(data)

    if isinstance(data, str):
        data = json.loads(data)

    return data


# Streamlit page settings
st.set_page_config(
    page_title="Model Monitoring Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("Model Monitoring Dashboard")
st.caption(
    "Machine Learning Prediction and Monitoring System"
)

st.markdown("---")


# Input section
st.subheader("Make a Prediction")

with st.form("prediction_form"):

    model_id = st.number_input(
        "Model ID",
        min_value=1,
        value=1,
        step=1
    )

    article_text = st.text_area(
        "Enter article text",
        placeholder="Enter the text you want the model to classify...",
        height=150
    )

    target = st.selectbox(
        "Ground-truth label",
        options=[0, 1],
        help="This label is submitted to the monitoring API for comparison."
    )

    submitted = st.form_submit_button(
        "Predict and Monitor",
        type="primary"
    )


if submitted:

    if not article_text.strip():
        st.warning("Please enter some article text.")

    else:

        with st.spinner("Getting prediction from the model..."):

            try:
                # Step 1: Send input to the model API
                input_data = {
                    "model_id": int(model_id),
                    "body": article_text,
                    "target": int(target)
                }

                model_response = requests.post(
                    MODEL_API_URL,
                    json=input_data,
                    timeout=60
                )

                model_response.raise_for_status()

                prediction_data = decode_response(model_response)

                # Step 2: Display prediction
                st.success("Prediction generated successfully!")

                predictions = prediction_data.get("predictions", [])

                if predictions:

                    first_prediction = predictions[0]

                    prediction = first_prediction.get("prediction")
                    confidence = first_prediction.get(
                        "prediction_probability"
                    )

                    # Handle prediction values returned as lists
                    if isinstance(prediction, list):
                        prediction = prediction[0]

                    if isinstance(confidence, list):
                        confidence = confidence[0]

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(
                            "Predicted Class",
                            str(prediction)
                        )

                    with col2:
                        if confidence is not None:
                            st.metric(
                                "Prediction Confidence",
                                f"{float(confidence) * 100:.2f}%"
                            )
                        else:
                            st.metric(
                                "Prediction Confidence",
                                "Not available"
                            )

                else:
                    st.warning("The API returned no prediction records.")

                with st.expander("View complete model response"):
                    st.json(prediction_data)

                # Step 3: Send prediction data to monitoring API
                st.markdown("---")
                st.subheader("Monitoring Results")

                with st.spinner("Sending prediction to monitoring service..."):

                    monitoring_response = requests.post(
                        MONITORING_API_URL,
                        json=prediction_data,
                        timeout=60
                    )

                    monitoring_response.raise_for_status()

                    try:
                        monitoring_data = monitoring_response.json()
                    except ValueError:
                        monitoring_data = monitoring_response.text

                    st.success(
                        "Prediction successfully sent to the monitoring service!"
                    )

                    st.write("Monitoring API response:")

                    if isinstance(monitoring_data, dict):
                        st.json(monitoring_data)
                    else:
                        st.code(str(monitoring_data))

            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to an API. "
                    "Make sure your Docker services are running."
                )

            except requests.exceptions.HTTPError as error:
                st.error(f"API returned an HTTP error: {error}")

                if error.response is not None:
                    st.code(error.response.text)

            except Exception as error:
                st.error(f"Something went wrong: {error}")


st.markdown("---")

st.subheader("Monitoring Tools")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Prometheus**")
    st.markdown("[Open Prometheus](http://localhost:9090)")

with col2:
    st.markdown("**Grafana**")
    st.markdown("[Open Grafana](http://localhost:3001)")