import subprocess
import time
import threading
import queue
import glob
import re

from seba.constants import DEBUG
from seba.logger import AsyncLogger
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

        AsyncLogger.info(f"Starting simulations")
        AsyncLogger.info(f"Found {self.__total_sims__} spice files to simulate.")
        time.sleep(1)

        self.__sim_threads__ = []
        for _ in range(self.max_parraler_sims):
            t = threading.Thread(target=self.worker)
            t.start()
            self.__sim_threads__.append(t)

        self.__progress_thread__ = threading.Thread(target=self.progress)
        self.__progress_thread__.start()

        for it_sf, sf in enumerate(sim_files):
            self.task_queue.put([it_sf, self.simulator, sf]+self.simulator_arguments)

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
                subprocess.run(item[1:], stdout=f"{item[2]}.log_{item[0]}")
            
            with self.__lock__:
                self.__done__ += 1

            self.task_queue.task_done()

    def progress(self):
        total = self.__total_sims__

        thread_sleep_time = 0.2
        last_total = 0
        last_print = 0
        force_print_interval = 2
        calculated_force_print_interval = force_print_interval / thread_sleep_time

        while True:
            with self.__lock__:
                done = self.__done__

            percent = (done / total) * 100 if total else 100

            bar_len = 30
            filled = int(bar_len * percent / 100)
            bar = "#" * filled + "-" * (bar_len - filled)

            if (last_total != total) or calculated_force_print_interval <= last_print:
                last_total = total
                last_print = 0
                AsyncLogger.raw(f"\r[{bar}] {percent:6.2f}% ({done}/{total})")

            if done >= total:
                break
            
            last_print += 1
            time.sleep(thread_sleep_time)
        AsyncLogger.raw("\n")
        AsyncLogger.info("Simulations ended.")

