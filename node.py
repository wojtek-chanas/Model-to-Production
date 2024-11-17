from data_generator import generate_data
import time
from fastapi import FastAPI
from random import randint
import threading

app = FastAPI()


df = generate_data(num_records=1, random_seed=randint(1,100))

@app.get('/node/data')
async def send_to_main():
    data = {"humidity" : df['humidity'][0], 
            "temperature" : df['temperature'][0],
            "sound_volume" : df['sound_volume'][0]}
    return data

def update_sensor_data():
    global df
    while True:
        df = generate_data(num_records=1, random_seed=randint(1,100))
        time.sleep(1) # wait 1 second

sensor_update_thread = threading.Thread(target=update_sensor_data)
sensor_update_thread.daemon = True
sensor_update_thread.start()