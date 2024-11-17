import requests
import time
import streamlit as st
import pandas as pd 

#st.cache_data.clear()

# Function to fetch data from the sensor node
def fetch_data():
    try:
        response = requests.get("http://127.0.0.1:8001/node/data", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Failed to fetch data from the node.")
            return None
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Function to get a prediction for the data package
def get_prediction(data):
    try:
        response = requests.post("http://127.0.0.1:8000/predict", json=data, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Failed to get prediction from the model.")
            return None
    except Exception as e:
        st.error(f"Error getting prediction: {e}")
        return None

# Function to get data from the database
def get_data():
    response = requests.get('http://127.0.0.1:8000/latest_readings', timeout=5)
    data = response.json()
    # Create DataFrame with explicit columns
    df = pd.DataFrame(data['data'], columns=data['columns'])
    df.set_index("datestamp", inplace=True)
    return df

def get_anomalies():
    response = requests.get('http://127.0.0.1:8000/latest_anomalies', timeout=5)
    data = response.json()
    # Create DataFrame with explicit columns
    df = pd.DataFrame(data['data'], columns=data['columns'])
    df.set_index("datestamp", inplace=True)
    return df

st.set_page_config(page_icon='logo.png', page_title="Live Dashboard")
st.logo("logo.png")

# Instantiate selectbox outside the loop
options = ["Sound Volume", "Humidity", "Temperature"]
selection = st.selectbox("Select the data to plot", options, key='data_selector')
values = {
    "Humidity": 'humidity',
    "Sound Volume": 'sound_volume',
    "Temperature": 'temperature'
}

# Placeholders for live updates
status_placeholder = st.empty()
st.write(f"### {selection} Time Series")
plot_placeholder = st.empty()
st.write("### Latest Anomalies")
num_records = st.number_input(label="Number of records to display", min_value=0, value=5)
data_placeholder = st.empty()



# Main loop for real-time updates
while True:
    # Fetch new data and make predictions
    data = fetch_data()
    if data:
        prediction = get_prediction(data)
        if prediction:
            if prediction.get("is_anomaly"):
                status_placeholder.markdown("### :red[Anomaly detected!]")
            else:
                status_placeholder.markdown("### :green[Current parameters seem to be normal.]")

    # Fetch data from the database and update plots
    
    df = get_data()
    with plot_placeholder.container():
        st.line_chart(df[[values[selection]]].tail(20))

    df = get_anomalies()
    with data_placeholder.container():
        st.dataframe(df.tail(num_records), width=800)

    # Pause for a second before the next update
    time.sleep(1)