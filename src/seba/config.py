from seba.logger import *

class SebaConfig:

    def __init__(self, name=None, control=None, tb=None, netlist=None,
                 corners=None, variants=None, script=None, plot=None, meas=None, 
                 extraction=None, sim_dir=None, config_dir=None, repo_dir=None):
        self.name: str = name
        self.control: str = control
        self.testbench: str = tb
        self.netlist: str = netlist
        self.corners: str = corners
        self.varinats: str = variants
        self.script: str = script
        self.plot: str = plot
        self.measure: str = meas
        self.extraction: list[str] = extraction
        self.sim_dir: str = sim_dir
        self.config_dir: str = config_dir
        self.repo_dir: str= repo_dir
        self.proc_quant: str = "1"

    def print_config(self):
        AsyncLogger.debug(f"Parsed seba configuration:")
        AsyncLogger.debug(f"NAME = {self.name}")
        AsyncLogger.debug(f"TESTBENCH = {self.testbench}")
        AsyncLogger.debug(f"NETLIST = {self.netlist}")
        AsyncLogger.debug(f"CONTROL = {self.control}")
        AsyncLogger.debug(f"CORNERS = {self.corners}")
        AsyncLogger.debug(f"VARIANTS = {self.varinats}")
        AsyncLogger.debug(f"SCRIPT = {self.script}")
        AsyncLogger.debug(f"MEAS = {self.measure}")
        AsyncLogger.debug(f"PLOT = {self.plot}")
        if self.extraction != None:
            AsyncLogger.debug(f"EXTRACTION = {", ".join(self.extraction)}")
        else:
            AsyncLogger.debug(f"EXTRACTION = {self.extraction}")
        AsyncLogger.debug(f"SIM_DIR = {self.sim_dir}")
        AsyncLogger.debug(f"CONFIG_DIR = {self.config_dir}")
        AsyncLogger.debug(f"REPO_DIR = {self.repo_dir}")