import pickle
from fastapi import FastAPI
import pandas as pd
from pydantic import BaseModel
import sqlite3


app = FastAPI()

# Load the model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# Define the input schema using Pydantic BaseModel
class Query(BaseModel):
    sound_volume: float
    humidity: float
    temperature: float


    
# Create a table if it doesn't exist
def create_table():
    conn = sqlite3.connect('data_log.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Data (
            temperature INT NOT NULL,
            humidity INT NOT NULL,
            sound_volume INT NOT NULL,
            datestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL PRIMARY KEY,
            is_anomaly BOOLEAN DEFAULT 0
        )
    ''')  # SQLite CURRENT_TIMESTAMP uses GMT timezone, not the local timezone of the machine
    conn.commit()
    conn.close()


def add_data(data):
    create_table()
    # Connect to the database
    conn = sqlite3.connect('data_log.db')
    cursor = conn.cursor()
    humidity = int(data["humidity"].iloc[0])
    temperature = int(data["temperature"].iloc[0])
    sound_volume = int(data["sound_volume"].iloc[0])
    is_anomaly = int(data["is_anomaly"].iloc[0])

    # Insert the new record into the Data table
    cursor.execute('''
                    INSERT INTO Data (humidity, temperature, sound_volume, is_anomaly)
                    VALUES (?, ?, ?, ?)
                ''', 
    (humidity, temperature, sound_volume, is_anomaly))
    print("Successfully inserted the record to database.")
    # Commit and close the connection
    conn.commit()
    conn.close()

@app.post("/predict")
async def predict(query: Query):
    """ 
    Takes arguments from the Query model 
    Returns prediction for anomalies as a boolean (is_anomaly = True or False)
    Saves the data with its label in a database
    """
    # Convert the incoming request into a DataFrame
    data = dict(query)  # Convert Pydantic model to dictionary
    df = pd.DataFrame([data])  # Create a DataFrame

    # Make the prediction
    prediction = model.predict(df)

    # The model outputs 1 for anomaly and 0 for normal
    is_anomaly = bool(prediction)  # Convert int to a boolean
    df["is_anomaly"] = is_anomaly
    add_data(df)

    return {"is_anomaly": is_anomaly}  # Return result as a JSON response

@app.get("/latest_readings")
def post_db():
    create_table()
    conn = sqlite3.connect('data_log.db')
    df = pd.read_sql_query("SELECT * FROM Data ORDER BY datestamp DESC LIMIT 10", conn)
    conn.close()
    result = {
        'data': df.values.tolist(),
        'columns': df.columns.tolist()
    }
    return result

@app.get("/latest_anomalies")
def post_db():
    create_table()
    conn = sqlite3.connect('data_log.db')
    df = pd.read_sql_query("SELECT * FROM Data WHERE is_anomaly = 1 ORDER BY datestamp DESC LIMIT 10", conn)
    conn.close()
    result = {
        'data': df.values.tolist(),
        'columns': df.columns.tolist()
    }
    return result
