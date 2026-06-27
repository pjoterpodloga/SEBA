from seba.logger import *

class SebaConfig:

    def __init__(self, name=None, control=None, tb=None, corners=None, 
                 script=None, plot=None, meas=None, extraction=None, 
                 sim_dir=None, config_dir=None):
        self.name = name
        self.control = control
        self.testbench = tb
        self.corners = corners
        self.script = script
        self.plot = plot
        self.meas = meas
        self.extraction = extraction
        self.sim_dir = sim_dir
        self.config_dir = config_dir

    def print_config(self):
        AsyncLogger.debug(f"Parsed seba configuration:")
        AsyncLogger.debug(f"NAME = {self.name}")
        AsyncLogger.debug(f"CONTROL = {self.control}")
        AsyncLogger.debug(f"CORNERS = {self.corners}")
        AsyncLogger.debug(f"SCRIPT = {self.script}")
        AsyncLogger.debug(f"MEAS = {self.meas}")
        AsyncLogger.debug(f"PLOT = {self.plot}")
        if self.extraction != None:
            AsyncLogger.debug(f"EXTRACTION = {", ".join(self.extraction)}")
        else:
            AsyncLogger.debug(f"EXTRACTION = {self.extraction}")
        AsyncLogger.debug(f"SIM_DIR = {self.sim_dir}")
        AsyncLogger.debug(f"CONFIG_DIR = {self.config_dir}")