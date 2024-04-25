# %%

import numpy as np
import keras 
from datetime import datetime
from threading import Thread
from queue import Queue
class anomoly_model():

    def __init__(self, model_file_name="model.keras", grid_size=1, seq_len=12):
        self.model_file_name = model_file_name
        self.grid_size = grid_size
        self.seq_len = seq_len
        self.model = keras.saving.load_model(self.model_file_name)

    def __call__(self, data):
        if data.shape[0] < self.seq_len:
            return []
        anomalies = Queue()
        thread_grid = 5 # nxn 
        lat_step = data.shape[1]//thread_grid
        lon_step = data.shape[2]//thread_grid
        threads = list()
        for lat_start in range(0, data.shape[1], lat_step):
            for lon_start in range(0, data.shape[2], lon_step):
                threads.append(Thread(target=self.__predict, args=
                           (
                            f"<{lat_start}|{lon_start}>",
                            data[:, lat_start:lat_start+lat_step, lon_start:lon_start+lon_step],
                            anomalies,
                            keras.saving.load_model(self.model_file_name),
                            self.seq_len, 
                            self.grid_size,
                            lat_start,
                            lon_start,
                            )
                           ))
                # print(lat_start, lon_start, end="\t")
                print(data[:, lat_start:lat_start+lat_step, lon_start:lon_start+lon_step].shape, end="\t")

            print()
        start = datetime.now()
        print(start)
        for thread in threads:
            print("thread started")
            thread.start()
        for thread in threads:
            thread.join()
            print("thread stoped")
        end = datetime.now()
        print(end)
        print(f"took: {end-start}")

        ano = list()
        for _ in range(anomalies.qsize()) :
            ano.append(anomalies.get())


        return ano

    @staticmethod
    def __predict(name, data, anomalies, model, seq_len, grid_size, lat_offset, lon_offset):

        print(name,  "shape:", data.shape)
        # anomalies.append({"points":[[lat_offset, lon_offset]],
        #                   "type": "weather"})
        # anomalies.append({"points":[[lat_offset+data.shape[1], lon_offset+data.shape[2]]],
        #                   "type": "sensor"})        
        # return  
        found_count = 0
        found_weather = 0 
        found_sensor = 0
        for lat in range(data.shape[1]):
            for lon in range(data.shape[2]):
                if data[0, lat, lon] == -50:
                    continue


                prediction = model(data[-seq_len:, lat, lon].reshape(1,seq_len, grid_size,grid_size))
                argmax = np.argmax(prediction)
                prediction = [0,0,0]
                prediction[argmax] = 1
                match prediction:
                    case [0,0,1]: # no anomaly 
                        continue
                    case [0,1,0]: # weather anomaly 
                        # print(f"found weather anomoly at {lat}, {lon}")
                        found_count += 1 
                        found_weather += 1
                        anomalies.put({"points":[[lon_offset+lon,lat_offset+lat, ]],
                                          "type": "weather"})
                    case [1,0,0]: # sensor anomaly 
                        # print(f"found sensor anomoly at {lat}, {lon}")
                        found_count += 1 
                        found_sensor += 1 
                        anomalies.put({"points":[[lon_offset+lon,lat_offset+lat, ]],
                                          "type": "sensor"})
        print(name, f"found {found_count}, {found_weather}, {found_sensor}")


    # def __call__(self, data):
    #     anomoly_list = list()
    #     for y in range(0, data.shape[2], 3):
    #         for x in range(0, data.shape[1], 3):
    #             if x >= 358 or y>= 178:
    #                 continue
    #             if data[0, y,x] ==-50 or data[0, y+self.grid_size, x+self.grid_size]==-50:
    #                 continue
    #             # print(data[:, x:x+self.grid_size, y:y+self.grid_size].shape)
    #             temp = np.random.random()
    #             if temp < 0.005:
    #                 # weather anomoly 
    #                 anomoly_list.append(
    #                     {"type":"weather",
    #                      "points":np.array([
    #                      [[x+i, y+j] for i in range(0, self.grid_size)] 
    #                      for j in range(0, self.grid_size)
    #                      ]).reshape(self.grid_size**2, 2)
    #                               }
    #
    #                 )
    #                 pass 
    #             elif temp < 0.01:
    #                 # sensor anomoly 
    #                 anomoly_list.append(
    #                     {"type":"sensor",
    #                      "points":[
    #                      [np.random.randint(x,x+self.grid_size),
    #                       np.random.randint(y,y+self.grid_size)]
    #                      ]
    #                      }
    #                 )
    #                 pass 
    #             else:
    #                 pass
    #             
    #     return anomoly_list


if __name__ == "__main__":
    model = anomoly_model()
    model(np.ndarray((12,180,360)))

