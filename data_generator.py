import numpy as np
import pandas as pd
import numpy as np


def generate_data(num_records = 1000,
                  random_seed = 42 , 
                  mean_temperature = 15, # Celsius degrees
                  std_temperature = 7, 
                  mean_humidity = 70, # in %
                  std_humidity = 12,
                  mean_sound_volume = 65, # dB
                  std_sound_volume = 10):
    
    """ Returns a dataframe with generated random values of temperature, humidity, and sound_volume along with their expected labels
     assigned by the criterion of falling into the range of three standard deviations from the mean.
      The parameters of each variable, as well as random seed and number of records can be specified as the function arguments,
       or left blank to use default values. """
    
    # Set seed for reproducibility
    np.random.seed(random_seed)

    # Generate the data
    temperature = np.random.normal(mean_temperature, std_temperature, num_records).round(2)
    humidity = np.random.normal(mean_humidity, std_humidity, num_records).round(2)
    sound_volume = np.random.normal(mean_sound_volume, std_sound_volume, num_records).round(2)

    # Generate anomaly labels (1 = anomaly, 0 = normal)
    # Mark anomalies where conditions are farther than 3 standard deviations away from the mean
    anomalies = (humidity <= mean_humidity-3*std_humidity) | (humidity > mean_humidity+3*std_humidity) | \
                (temperature <= mean_temperature-3*std_temperature) | (temperature > mean_temperature+3*std_temperature) | \
                (sound_volume <= mean_sound_volume-3*std_sound_volume) | (sound_volume > mean_sound_volume+3*std_sound_volume)

    # Create the dataframe
    data = {
        'sound_volume': sound_volume,
        'humidity': humidity,
        'temperature': temperature,
        'is_anomaly': anomalies.astype(int)
    }

    df = pd.DataFrame(data)

    return df


### Optionally, to create a training dataset in CSV file

#df = generate_data()
#df.to_csv('turbine_data.csv', index=False)