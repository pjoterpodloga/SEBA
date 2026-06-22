from seba.logger import *

class SebaConfig:

    def __init__(self, name=None, control=None, tb=None, corners=None, 
                 script=None, plot=None, meas=None, extraction=None):
        self.name = name
        self.control = control
        self.tb = tb
        self.corners = corners
        self.script = script
        self.plot = plot
        self.meas = meas
        self.extraction = extraction

    def print_config(self):
        AsyncLogger.debug(f"Parsed seba configuration:")
        AsyncLogger.debug(f"NAME = {self.name}")
        AsyncLogger.debug(f"CONTROL = {self.control}")
        AsyncLogger.debug(f"CORNERS = {self.corners}")
        AsyncLogger.debug(f"SCRIPT = {self.script}")
        AsyncLogger.debug(f"MEAS = {self.meas}")
        AsyncLogger.debug(f"PLOT = {self.plot}")
        AsyncLogger.debug(f"EXTRACTION = {", ".join(self.extraction)}")