import os
import shutil
import subprocess

from seba.config import *

class SebaResult:
    def __init__(self, config: SebaConfig):
        self.config = config

        self.__result_dir__ = config.repo_dir + "/tmp/results/" + config.name

    ### TODO: Add proper logger messages

    def generate_results(self):
        dir_exist = self.__check_result_directory_exist__()

        if (dir_exist):
            self.__remove_result_directory__()

        self.__create_result_directory__()
        self.__run_script_wrapper__()
        self.__copy_result__()

    def __check_result_directory_exist__(self):
        return os.path.exists(self.__result_dir__)
    
    def __remove_result_directory__(self):
        shutil.rmtree(self.__result_dir__, ignore_errors=True)

    def __create_result_directory__(self):
        subprocess.run(["mkdir", "-p", self.__result_dir__])

    def __run_script_wrapper__(self):
        script_name = self.config.sim_dir + "/script_wrapper.sh"
        subprocess.run([script_name])

    def __copy_result__(self):
        measure_json = self.config.sim_dir + "\measure.json"
        measure_csv = self.config.sim_dir + "\measure.csv"
        corner_list = self.config.sim_dir + "\corners.list"
        subprocess.run(["cp", measure_json, self.__result_dir__])
        subprocess.run(["cp", measure_csv, self.__result_dir__])
        subprocess.run(["cp", corner_list, self.__result_dir__])