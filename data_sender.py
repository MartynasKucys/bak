import requests 
from data import  * 
from pathlib import Path 
import numpy as np 
import pickle as pkl 
import time



def send_data(send_to:str, data):
    response = requests.post(

        url=send_to,
        headers={"Content-Type":"application/octet-stream"},
        data=pkl.dumps(data)

    )
    return response

def load_data(anomaly:True):
    # data = read_data(data_dir=Path("data"))
    if anomaly: 
        data = read_data_with_anomaly(data_dir=Path("data"))
    else:
        data= read_data(data_dir=Path("data"))
    a = data>1000
    # b = data<1000
    data[a] = -50
    # data[b] = 50
    # with open("mock_data.pkl", "wb") as f:
    #     pkl.dump(np.flip(data[0], axis=0),f
    return np.flip(data, axis=1) 



if __name__ == "__main__":
    data = load_data(False)
    for month in range(data.shape[0]):
        send_data("http://127.0.1:8080", data[month])
        time.sleep(0.3)
    data = load_data(True)
    for month in range(data.shape[0]):
        send_data("http://127.0.1:8080", data[month])
        time.sleep(0.3)
