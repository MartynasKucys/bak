import tkinter as tk 
from tkinter import ttk
import time
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 

class GUI_graph:
    def __init__(self,weather_data, anomaly_data, at, *events):
        self.root = tk.Tk()

        print("weather data")
        print(weather_data)
        print("anomoly_datt")
        print()

        self.__setup_graph()

        for wd in weather_data:
            self.__plot(wd)
        self.__plot_anomaly(at)

        self.__setup_ax()
        self.__setup_gui()

        self.weather_data = weather_data
        self.anomaly_data = anomaly_data

        self.events = events
        self.command_to_close = False

    def __setup_gui(self,):
        self.console_cavas = tk.Canvas(self.root)
        self.button = tk.Button(self.console_cavas, text="test")
        self.button.grid(row=0, column=0)
        self.console_cavas.grid(row=1, column=0)
        pass

    def __setup_graph(self,):
        self.fig = Figure(figsize=(8,4))
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0)

    def __setup_ax(self,):
        self.ax.set_xlabel("time")
        self.ax.set_ylabel("temperature")


    def __clear_graph(self,):
        self.canvas.get_tk_widget().pack_forget()
        del self.canvas
        del self.fig
        self.__setup_graph

    def __plot(self,data, color="red",):
        self.ax.plot(range(len(data)), data)

    def __plot_anomaly(self,data):
        self.ax.plot([data,data], [-50,50])

    def close(self,):
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def run(self,):
        while not self.events[0].is_set():
            self.root.update_idletasks()
            self.root.update()
            time.sleep(0.01)
        self.root.destroy()
