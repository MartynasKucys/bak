from contextlib import asynccontextmanager
from model import anomoly_model
from fastapi import FastAPI
from fastapi import Request
from tkinter import Tk
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import seaborn as sns 
import time 
import numpy as np 
import pickle as pkl
from threading import Thread, Event
from gui import GUI
from queue import Queue





@asynccontextmanager
async def lifespan(app:FastAPI):
    print("started lifespan")
    close_window_event = Event()

    global sent_data_event 
    sent_data_event = Event()

    global gui_data_queue
    gui_data_queue = Queue()

    def run_gui(*events):
        gui = GUI(*events, data_queue=gui_data_queue)
        gui.run()
    gui_thread = Thread(target=run_gui, args=[close_window_event, sent_data_event])
    gui_thread.start()

    yield
    ################
    #   Clean up   #  
    ################
    close_window_event.set()


app = FastAPI(lifespan=lifespan)
# app = FastAPI()
all_data = []
model = anomoly_model()



@app.post("/")
async def recieve(request:Request):
    data = await request.body()
    weather_data = pkl.loads(data)

    all_data.append(weather_data)
    points = model(np.array(all_data))

    data_to_send = {
        "weather": weather_data,
        "anomaly":  points,
    } 

    #
    # data_to_send = {
    #     "weather": weather_data,
    #     "anomaly":  [
    #        {
    #             "points":[[np.random.randint(0,360),
    #                         np.random.randint(0,180)] for i in range(3)], 
    #             "type": np.random.choice(["sensor", "weather"])
    #        }
    #     for _ in range(np.random.randint(5)) ],
    # } 

    send_data_to_gui(data_to_send, gui_data_queue)
    sent_data_event.set()
    time.sleep(0.1)

    return "ok", 200






def send_data_to_gui(data, queue):
    print("[main] putting data")
    queue.put(data)

