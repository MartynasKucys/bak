import tkinter as tk 
import numpy as np 
from gui_graph import GUI_graph
from tkinter import ttk
from datetime import datetime
import pickle as pkl
import matplotlib.pyplot as plt
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 
import seaborn as sns 
from threading import Event
from queue import Queue, Empty
import time 


class GUI:
    def __init__(self, *events, data_queue=Queue()):
        self.events = events
        self.accept_live_data = True 

        self.root = tk.Tk()
        self.children_windows =None  
        self.__setup_map()
        self.__setup_gui()

        with open("mock_data.pkl", "rb") as f:
            mock_data = pkl.load(f)
        self.__plot_map(mock_data)


        self.data_queue = data_queue

        self.data_list = list()

    #######
    # gui #
    #######
    
    def __setup_gui(self,):
        self.console_canvas = tk.Canvas(self.root)

        self.button_live = tk.Button(
            self.console_canvas,
            text="live",
            bg="green",
            command=self.__toggle_live,
        )
        self.button_live.grid(row=0,column=0)

        self.button_historic = tk.Button(
            self.console_canvas,
            text="load historic data",
            command=self.__load_historic_data,
            )
        self.button_historic.grid(row=0, column=1)

        self.dropdown = ttk.Combobox(self.console_canvas)
        self.dropdown.set("None selected")
        self.dropdown.grid(row=0, column=2)

        self.anomaly_list_box = tk.Listbox(self.console_canvas, width=50)
        self.anomaly_list_box.configure(height=6, state="normal")
        self.anomaly_list_box.grid(row=1, column=0, columnspan=10, sticky="nswe")

        self.button_open_anomaly = tk.Button(
            self.console_canvas,
            text="Open anomaly",
            command=self.__open_anomaly
        )
        self.button_open_anomaly.grid(row=0, column=5, sticky="nswe")



        self.button_save = tk.Button(
            self.console_canvas,
            text="Save data",
            command=self.save_data, 
        )
        self.button_save.grid(row=0, column=3, sticky="wn")

        self.button_load = tk.Button(
            self.console_canvas,
            text="Load data",
            command=self.load_data,
        )
        self.button_load.grid(row=0, column=4)



        self.console_canvas.grid(row=1, column=0, sticky="wns", padx=0)


    def __clear_console(self):
        self.anomaly_list_box.delete("0", "end")



    def __set_console(self,text):
        self.anomaly_list_box.delete("0", "end")
        self.anomaly_list_box.insert("end", text)

    def __append_to_console(self, text):
        self.anomaly_list_box.insert("end", text)
            
    ####################
    # button functions #
    ####################
    
    def __load_historic_data(self,):
        self.__toggle_live(set_to=False)
        try:
            selected_value = int(self.dropdown.get()) - 1
            self.__plot_map(self.data_list[selected_value]["weather"])
            self.__plot_anomaly_at(self.data_list[selected_value]["anomaly"])
        except ValueError as e:

            raise(e)
            print("Invalid data selected")

    def __toggle_live(self,set_to=None):
        if set_to == None:
            set_to = self.accept_live_data
        else:
            set_to = not set_to

        if set_to:
            # if false 
            self.button_live.configure(bg="red")

            self.accept_live_data = False
        else:
            # if True 
            self.button_live.configure(bg="green")

            self.__plot_map(self.data_list[-1]["weather"])
            self.__plot_anomaly_at(self.data_list[-1]["anomaly"])
            self.dropdown.set(len(self.data_list))


            self.accept_live_data = True

    def save_data(self, file_name:str="saved_data.pkl"):
        with open (file_name, "wb") as f:
            pkl.dump((self.data_list), f)
            self.__set_console(f"data writen to {file_name}")

    def load_data(self,file_name:str="saved_data.pkl"):
        try:
            with open (file_name, "rb") as f:
                data  = pkl.load(f)
                self.data_list = data
                self.__set_console(f"data read form {file_name}")
                self.dropdown["values"]=list(range(1, len(self.data_list)+1))
        except FileNotFoundError:
            self.__set_console(f"File '{file_name}' not found ")

    def __open_anomaly(self,):

        selected_index = int(self.dropdown.get())-1
        selected_anomaly =self.anomaly_list_box.curselection()[0]
    
        anomaly = self.data_list[selected_index]["anomaly"][selected_anomaly]
        print(len(self.data_list))
        collected_data = [x["weather"] for x in self.data_list] 
        collected_data = np.array(collected_data)

        weather_data = np.ndarray((len(anomaly["points"]), collected_data.shape[0])) 
        for i,a in enumerate(anomaly["points"]):
            weather_data[i] = collected_data[:, a[1], a[0]]


        if self.children_windows != None:
            self.children_windows.close()
            self.children_windows = None

        self.children_windows = GUI_graph(
            weather_data,
            anomaly,
            selected_index,
            *self.events,
        )
        self.children_windows.run()


        
    #######
    # map #
    #######

    def __setup_map(self,):
        self.map_fig = Figure(figsize=(12,8))
        self.map_ax = self.map_fig.add_subplot(111)

        self.map_canvas = FigureCanvasTkAgg(self.map_fig, master=self.root)
        self.map_canvas.draw()
        self.map_canvas.get_tk_widget().grid(row=0,column=0, columnspan=2)
   
    def __setup_ax(self,):
        self.map_ax.set_ylabel("Latitude")
        self.map_ax.set_xlabel("Longitude")

    def __clear_map(self,):
        self.map_canvas.get_tk_widget().pack_forget()
        del self.map_canvas 
        del self.map_fig
        self.__setup_map()


    def __plot_map(self, weather_data):
        self.__clear_map()
        sns.heatmap(weather_data, ax=self.map_ax, vmin=-50, vmax=50)
        self.__setup_ax()

    def __plot_anomaly_at(self,anomaly_data):
        dpi = 10
        self.__clear_console()
        if len(anomaly_data) == 0:
            self.__set_console("No anomalies found")


        # print(anomaly_data)
        weather_anomalies = [] 
        sensor_anomalies = []
        print(anomaly_data[0])
        for i in range(len(anomaly_data)):
            if anomaly_data[i]["type"] == "weather":
                weather_anomalies += anomaly_data[i]["points"]
            else:
                sensor_anomalies += anomaly_data[i]["points"]
        weather_anomalies = np.array(weather_anomalies)
        sensor_anomalies = np.array(sensor_anomalies)
        if weather_anomalies.shape != (0,):
            self.map_ax.scatter(weather_anomalies[:, 0], weather_anomalies[:, 1], color="blue", linewidths=dpi)
        if sensor_anomalies.shape != (0,):
            self.map_ax.scatter(sensor_anomalies[:, 0], sensor_anomalies[:, 1], color="red", linewidths=dpi)

        #
        #
        #     
        # temp = np.array(anomaly_data)
        # temp = np.array([ [([xx for xx in x ], y) for x, y  in zip(pset["points"], (pset["type"],))] for pset in temp ])
        # 
        # print(temp[0])
        # print(temp[1])
        # print(temp[2])
        # print(temp[3])
        # # temp = temp.reshape(temp.shape[0], 2)
        # # x = temp[:,0]
        # # y = temp[:,1]
        # self.map_ax.scatter(x,y, color="blue" if anomaly_type == "weather" else "green", linewidths=dpi) 
        for i,anomaly in enumerate(anomaly_data):
            #i is index for anomaly set 

            self.__append_to_console( f"{i}|{anomaly['type']} anomaly at {str([f'|lat={p[1]}, lon={p[0]}|' for p in anomaly['points']])}")

                # a is anomaly points 

            anomaly_type = anomaly["type"]
            # temp = np.array(anomaly["points"])
            # x = temp[:,0]
            # y = temp[:,1]
            # self.map_ax.scatter(x,y, color="blue" if anomaly_type == "weather" else "green", linewidths=dpi) 
            for x,y in anomaly["points"]:

                    # self.__append_to_console( f"weather anomaly at lat={y}, lon={x}\n")
                    # self.map_ax.scatter([x],[y], color="blue" if anomaly_type == "weather" else "green", linewidths=dpi) 
                    # print(x,y)
                    self.map_ax.annotate(str(i), (x-0.75,y+0.75, ), color="white")
#######

    def __check_queues(self):
        if self.events[1].is_set():
            print("cheking queues")
            found_data = True
            while found_data:
                try:
                    data = self.data_queue.get(timeout=0.1)

                    # self.data_list["weather"].append(data["weather"])
                    # self.data_list["anomaly"].append(data["anomaly"])

                    self.data_list.append({"weather":data["weather"], "anomaly":data["anomaly"]})

                    self.dropdown["values"]=list(range(1, len(self.data_list)+1))

                    self.__plot_map(data["weather"])
                    self.__plot_anomaly_at(data["anomaly"])
                    print("data found")
                    self.dropdown.set(len(self.data_list))
                    found_data = True
                except Empty:
                    found_data = False

        self.events[1].clear()

    def run(self,):
        while not self.events[0].is_set():
            if self.accept_live_data:
                self.__check_queues()

            self.root.update_idletasks()
            self.root.update()
            time.sleep(0.01)

        self.root.destroy()

if __name__ == "__main__":
    e1 = Event()
    e2 = Event()
    gui = GUI(e1, e2)
    gui.run()
