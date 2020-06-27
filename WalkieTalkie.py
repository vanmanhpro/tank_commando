import tkinter as tk
from tkinter import W, S, N, E, CENTER
from tkinter.filedialog import askopenfilename
import pyaudio
import wave
import os
import pickle
from models.asg2 import get_mfcc

COMMAND_PATH = '/home/vanmanh/XuLyTiengNoi/TankCommando/commands'

MAP_COMMAND = {
    'Hoc': 'shoot',
    'YTe': 'up',
    'ThanhPho': 'down',
    'Me': 'left',
    'Nha': 'right'
}

def find_result(lsres):
    dc = {}
    cmax = 0
    res = "Unknown"
    for e in lsres:
        if (e in dc): dc[e] += 1
        else: dc[e] = 1
        if (dc[e]>cmax):
            cmax = dc[e]
            res = e
    return MAP_COMMAND[res]

class App:
    def __init__(self, chunk=1024, sample_format=pyaudio.paInt16, channels=2, rate=44100, p=pyaudio.PyAudio()):
        # For recording
        self.CHUNK = chunk
        self.FORMAT = sample_format
        self.CHANNELS = channels
        self.RATE = rate
        self.p = p
        self.frames = []
        self.st = 1
        self.stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        self.recording = False

        # For model
        self.models_v = []
        for i in range(1, 12):
            file = open(f"models/models_v{i}.pkl", "rb")
            self.models_v.append(pickle.load(file))
            file.close()
        # self.models_v = [pickle.load(open(f"models_v{i}.pkl", "rb")) for i in range(1,12)]
        self.file_path = ""
        # self.predict = ""

        # For App
        self.main = tk.Tk()
        self.main.geometry('400x200')
        self.main.title('Speech Recognition')

        self.record_state = tk.Label(text="")
        self.result_text = tk.Label(text="Command: ")

        self.btn_record = tk.Button(self.main, text = "Start Record", width = 12, command=self.record)

        self.btn_record.grid(row=0, column=0)
        self.btn_record.place(relx=0.5, rely=0.2, anchor=CENTER)
        self.record_state.grid(row=0, column=1, sticky=W, padx = 20)
        self.result_text.grid(row=2, column=1, sticky=W, padx = 20, pady=50)
        self.main.mainloop()

    def start_record(self):
        self.result_text.config(text="Command: ")
        self.st = 1
        self.frames = []
        stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        print("start recording")
        while self.st == 1:
            data = stream.read(self.CHUNK)
            self.frames.append(data)
            self.main.update()
        stream.close()
        wf = wave.open('record.wav', 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def stop_record(self):
        self.st = 0
        print("recording completed")
        self.predict()

    def record(self):
        if self.recording == True:
            self.btn_record.config(text="Start Record")
            self.record_state.config(text="")
            self.recording = False
            self.file_path = "record.wav"
            self.stop_record()
        elif self.recording == False:
            self.btn_record.config(text="Stop Record")
            self.record_state.config(text="Recording ...")
            self.recording = True
            self.start_record()

    def predict(self):
        print("predicting")
        if not self.file_path:
            print("NO file")
            return
        O = get_mfcc(self.file_path)
        result_predict = "Unknown"
        lsres = []
        for models in self.models_v:
            score = {cname : model.score(O, [len(O)]) for cname, model in models.items()}
            print(score)
            predict = max(score, key=score.get)
            lsres.append(predict)
        result_predict = find_result(lsres)
        print(lsres)
        print("predicted")
        self.result_text.config(text="Command: "+result_predict)

        with open(COMMAND_PATH, "rb") as file:
            commands = pickle.load(file)


        commands.append(result_predict)

        with open(COMMAND_PATH, "wb") as file:
            pickle.dump(commands, file)

app = App()