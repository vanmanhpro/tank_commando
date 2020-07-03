import tkinter as tk
from tkinter import W, S, N, E, CENTER
from tkinter.filedialog import askopenfilename
import pyaudio
import wave
import os
import pickle
import time
from models.asg2 import get_mfcc

from threading import Thread


COMMAND_PATH = '/home/vanmanh/XuLyTiengNoi/TankCommando/commands'

MAP_COMMAND = {
    'ban': 'shoot',
    'len': 'up',
    'xuong': 'down',
    'trai': 'left',
    'phai': 'right'
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
    RECORD_CHUNK = 1024
    RECORD_FORMAT = pyaudio.paInt16
    RECORD_CHANNELS = 2
    RECORD_RATE = 44100
    AUDIO = pyaudio.PyAudio()

    def __init__(self):

        # For model
        self.models_v = []
        for i in range(2, 3):
            with open(f"models/model_v{i}.pkl", "rb") as file:
                self.models_v.append(pickle.load(file))
            file.close()

        self.recording = False
        self.recording_lock = 0

        self.current_recording = None
        self.exported_commands = []
    
    def start_recording(self):

        self.recording_lock += 1
        current_recording = self.recording_lock
        file_path = f"record_{current_recording}.wav"

        self.recording = True

        record_frames = []
        record_stream = self.AUDIO.open(format=self.RECORD_FORMAT, channels=self.RECORD_CHANNELS, rate=self.RECORD_RATE, input=True, frames_per_buffer=self.RECORD_CHUNK)
        record_stream.start_stream()

        while True:
            if current_recording != self.recording_lock:
                record_stream.stop_stream()
                record_stream.close()
                return
            if not self.recording:
                break

            data = record_stream.read(self.RECORD_CHUNK)
            record_frames.append(data)

        record_stream.stop_stream()
        record_stream.close()

        if current_recording != self.recording_lock:
            return 
        
        wf = wave.open(file_path, 'wb')
        wf.setnchannels(self.RECORD_CHANNELS)
        wf.setsampwidth(self.AUDIO.get_sample_size(self.RECORD_FORMAT))
        wf.setframerate(self.RECORD_RATE)
        wf.writeframes(b''.join(record_frames))
        wf.close()

        if current_recording != self.recording_lock:
            return 

        self.predict(file_path)

    def stop_recording(self):
        self.recording = False

    def predict(self, file_path):
        O = get_mfcc(file_path)
        result_predict = "Unknown"
        lsres = []
        for models in self.models_v:
            score = {cname : model.score(O, [len(O)]) for cname, model in models.items()}
            print(score)
            predict = max(score, key=score.get)
            lsres.append(predict)
        result_predict = find_result(lsres)
        print(lsres)
        print("predicted: " + result_predict)

        self.exported_commands.append(result_predict)

        os.remove(file_path)

    def export_commands(self):
        commands = self.exported_commands
        self.exported_commands = []
        return commands

# app = App()

# record_thread = Thread(target=app.record)
# stop_record_thread = Thread(target=app.stop_recording)

# record_thread.start()
# time.sleep(2.4)
# stop_record_thread.start()

# record_thread.join()
# stop_record_thread.join()

# record_process = Process(target=app.record)
# stop_record_process = Process(target=app.stop_recording)

# record_process.start()
# time.sleep(2.4)
# stop_record_process.start()

# record_process.join()
# stop_record_process.join()
