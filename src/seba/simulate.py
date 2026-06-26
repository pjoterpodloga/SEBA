import subprocess
import time
import threading
import queue
import glob
import re

from seba.constants import DEBUG
from seba.config import SebaConfig

class SebaSimulate:

    def __init__(self, config: SebaConfig):
        self.config = config

        self.max_parraler_sims = 4
        self.simulator = "ngspice"
        self.simulator_arguments = ["--batch"]

        self.task_queue = queue.Queue()
        self.__lock__ = threading.Lock()
        self.__done__ = 0
        self.__finished__ = 0

        sim_files = glob.glob(f"{self.config.sim_dir}/{self.config.testbench}_*")
        sim_files = [f for f in sim_files if re.search(fr"{self.config.sim_dir}/{self.config.testbench}_\d+", f)]

        sim_files = sorted(sim_files, key=lambda x: int(x.split("_")[-1]))

        self.__total_sims__ = len(sim_files)

        self.__sim_threads__ = []
        for _ in range(self.max_parraler_sims):
            t = threading.Thread(target=self.worker)
            t.start()
            self.__sim_threads__.append(t)

        self.__progress_thread__ = threading.Thread(target=self.progress)
        self.__progress_thread__.start()

        for sf in sim_files:
            self.task_queue.put([self.simulator, sf]+self.simulator_arguments)

        self.task_queue.join()

        for _ in range(self.max_parraler_sims):
            self.task_queue.put(None)

        for t in self.__sim_threads__:
            t.join()
        self.__progress_thread__.join()

        self.__finished__ = 1

    def worker(self):
        while True:
            item = self.task_queue.get()

            if item == None:
                break
            
            if DEBUG:
                time.sleep(1)
            else:
                subprocess.run(item)
            
            with self.__lock__:
                self.__done__ += 1

            self.task_queue.task_done()

    def progress(self):
        total = self.__total_sims__

        while True:
            with self.__lock__:
                done = self.__done__

            percent = (done / total) * 100 if total else 100

            bar_len = 30
            filled = int(bar_len * percent / 100)
            bar = "#" * filled + "-" * (bar_len - filled)

            print(f"\r[{bar}] {percent:6.2f}% ({done}/{total})", end="", flush=True)

            if done >= total:
                break

            time.sleep(0.2)

        print()

