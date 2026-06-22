from seba.config import *

class SebaReader:
    def __init__(self, config: SebaConfig):
        self.config = config
        self.control_file = None
        self.testbench_file = None
        self.corners_file = None
        self.script_file = None
        self.measure_file = None
        self.plot_file = None
        self.extraction_files = None

        self.__read_files__()

    def __read_files__(self):
        self.__read_control_file__()
        self.__read_testbench_file__()
        self.__read_corners_file__()
        self.__read_script_file__()
        self.__read_measure_file__()
        self.__read_plot_file__()
        self.__read_extraction_files__()

        pass

    ### TODO: Handle not existing files
    ### TODO: Resolve searching directories from default dir

    def __read_control_file__(self):
        with open("../control/"+self.config.control, "r") as f:
            self.control_file = f.readlines()
    
    def __read_testbench_file__(self):
        with open("../testbench/"+self.config.testbench, "r") as f:
            self.testbench_file = f.readlines()
    
    def __read_corners_file__(self):
        with open("../corners/"+self.config.corners, "r") as f:
            self.corners_file = f.readlines()

    def __read_script_file__(self):
        with open("../scripts/"+self.config.script, "r") as f:
            self.script_file = f.readlines()
    
    def __read_measure_file__(self):
        with open("../result_gen/"+self.config.meas, "r") as f:
            self.measure_file = f.readlines()

    def __read_plot_file__(self):
        with open("../result_gen/"+self.config.plot, "r") as f:
            self.plot_file = f.readlines()

    def __read_extraction_files__(self):
        if self.config.extraction != None:
            self.extraction_files = []
            for ef in self.config.extraction:
                with open("../pex/"+ef, "r") as f:
                    self.extraction_files.append(f.readlines())