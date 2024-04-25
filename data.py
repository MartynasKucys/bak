#%%
from netCDF4 import Dataset

from pathlib import Path
import os 
import numpy as np 
import pickle
from tqdm import tqdm 


def read_data(data_dir=Path("..", "data", "raw_data"),  ):
    files = os.listdir(data_dir)
    files.sort()
    all_data = None
    for file in (os.listdir(data_dir)):
        data = Dataset(data_dir.joinpath(file))
        if all_data is None:
            all_data = np.array(data.variables["tas"])
        else:
            all_data = np.concatenate([all_data,  np.array(data.variables["tas"])], axis=0)

    return all_data


def read_data_with_anomaly(data_dir=Path("...","data","raw_data"),grid_size=1, number_of_anom=1000, sensor_anomaly_prob=0.1):
    files = os.listdir(data_dir)
    files.sort()
    all_data = None
    for file in (os.listdir(data_dir)):
        data = Dataset(data_dir.joinpath(file))
        if all_data is None:
            all_data = np.array(data.variables["tas"])
        else:
            all_data = np.concatenate([all_data,  np.array(data.variables["tas"])], axis=0)
    if all_data is None:
        raise Exception("No data found")

    while number_of_anom > 0:
        x = np.random.randint(1, all_data.shape[1]-1)
        y = np.random.randint(1, all_data.shape[2]-1)
        if all_data[0, x,y] <= -50:
            continue
        if sensor_anomaly_prob < np.random.rand():
            add_sensor_anomaly(grid_size, all_data[:, x, y])
        else:
            add_weather_anomaly(grid_size, all_data[:,x-1:x+1, y-1:y+1])
        number_of_anom -= 1


    return all_data


def add_sensor_anomaly(grid_size, data): # data(12, 1, 1)
    data = np.reshape(data, (data.shape[0], grid_size, grid_size))
    sensor_anomaly = 1 
    y=0
    x=0
    match sensor_anomaly:
        case 0:
            # sensor drift
            data[:,x,y] += np.arange(data.shape[0])
        case 1:
            # spike
            data[np.random.randint(data.shape[0]), x, y] = 100 
        case _:
            raise Exception("Invalid sensor anomaly provided")

    pass 

def add_weather_anomaly(grid_size, data): # data(12, 3, 3)
    add_max = 100
    to_add = np.linspace(0,100, data.shape[0])
    for x in range(grid_size):
        for y in range(grid_size):
            data[:,x,y] = to_add





def split_data(data, seq_len:int=12, grid_size:int=1):
    x = list()
    y = list()
    for from_ in tqdm(np.arange(0,data.shape[0],seq_len)):
        for lat in tqdm(np.arange( data.shape[1]), leave=False):
            for lon in tqdm(np.arange( data.shape[2]), leave=False):
                try:
                    xx = data[from_:from_+seq_len, lat:lat+grid_size, lon:lon+grid_size]
                    yy = data[from_+1, lat:lat+grid_size, lon:lon+grid_size]
                    if np.all(xx < 1000) and xx.shape == (seq_len, grid_size, grid_size):
                        x.append(xx)
                        y.append(yy)
                except IndexError:
                    print(f"crashed on {from_}, {lat}, {lon}")
                    pass 
    return np.array(x),np.array(y)

def split_data_with_anomaly(data, seq_len:int=12, grid_size:int=1, anomaly_chance:float=0.5, sensor_percent:float=0.5):

    x = list()
    y = list()

    for from_ in tqdm(np.arange(0,data.shape[0],seq_len)):
        for lat in (np.arange( data.shape[1])):
            for lon in (np.arange( data.shape[2])):    
                try:
                        if np.random.random() < anomaly_chance:
                            if np.random.random() < sensor_percent:
                                # sensor anomaly 
                                xx = data[from_:from_+seq_len, lat:lat+grid_size, lon:lon+grid_size]

                                if xx.any() < -100:
                                    continue

                                random_sensor = np.random.randint(0, grid_size*grid_size)
                                xxx = random_sensor % grid_size
                                xxy = random_sensor - (xxx * grid_size)

                                num_of_sensor_anomalies = 2
                                sensor_anomaly = np.random.randint(0, num_of_sensor_anomalies)
                                sensor_anomaly = 1
                                match sensor_anomaly:
                                    case 0:
                                        # sensor drift
                                        xx[:, xxx, xxy] += np.arange(xx.shape[0])
                                    case 1:
                                        # spike
                                        xx[np.random.randint(xx.shape[0]), xxx, xxy] = 100 
                                    case _:
                                        raise Exception("Invalid sensor anomaly provided")

                                yy = [1,0, 0]
                            else:
                                # weather anomaly 
                                xx = data[from_:from_+seq_len, lat:lat+grid_size, lon:lon+grid_size]
                                # max_at = np.random.randint(0, xx.shape[0]-1)
                                max_at = np.random.randint(50, 100)
                                peak = 2
                                to_add = [abs(abs(i - max_at)/xx.shape[0] - peak) for i, x in enumerate(range(xx.shape[0]))]
                                for i in range(grid_size):
                                    for j in range(grid_size):
                                        xx[:, i, j] += to_add
                                yy = [0, 1, 0]
                        else:
                            # no anomaly 
                            xx = data[from_:from_+seq_len, lat:lat+grid_size, lon:lon+grid_size]
                            yy = [0,0, 1]

                except IndexError:
                    pass

                if np.all(xx < 1000) and xx.shape == (seq_len, grid_size, grid_size):
                    x.append(xx)
                    y.append(yy)
    return np.array(x), np.array(y)


if __name__ == "__main__":
    seq_len = 24
    grid_size = 3
    x, y = split_data_with_anomaly(read_data(), seq_len=seq_len, grid_size=grid_size) 
    print(x.shape)
    import matplotlib.pyplot as plt 
    for i in range(x.shape[0]):
        print(y[i])
        if y[i,0] == 0 and y[i,1] == 1:

            print(">>>>", y[i])
            data_list = x[i,:,:,:].reshape(seq_len, grid_size*grid_size)
            data_list = data_list.transpose()
            print(data_list.shape)
            for d  in data_list:
                plt.plot(range(len(d)), d)
            plt.show()
            break
    
