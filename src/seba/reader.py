from seba.config import *

class SebaReader:
    def __init__(self, config: SebaConfig):
        self.config = config
        self.control_file = None
        self.testbench_file = None
        self.netlist_file = None
        self.corners_file = None
        self.script_file = None
        self.measure_file = None
        self.plot_file = None
        self.extraction_files = None

        self.__read_files__()

    def __read_files__(self):
        self.__read_control_file__()
        self.__generate_netlist_file__()
        self.__read_netlist_file__()
        self.__read_corners_file__()
        self.__read_script_file__()
        self.__read_measure_file__()
        self.__read_plot_file__()
        self.__read_extraction_files__()

        pass

    ### TODO: Handle not existing files
    ### TODO: Resolve searching directories from default dir

    def __read_control_file__(self):
        if self.config.control != None:
            with open("../control/"+self.config.control, "r") as f:
                self.control_file = f.readlines()
    
    def __read_netlist_file__(self):
        if self.config.netlist != None:
            with open("../netlist/"+self.config.netlist, "r") as f:
                self.netlist_file = f.readlines()

        if self.config.testbench != None:
            netlist_filename = self.config.testbench.split(".")
            netlist_filename = "".join(netlist_filename[0:-2])
            netlist_filename = f"{netlist_filename}.spice"
            with open("../netlist/"+netlist_filename, "r") as f:
                self.netlist_file = f.readlines()
    
    def __generate_netlist_file__(self):
        if self.config.testbench != None:
            try:
                subprocess.run(["xschem", "-x", "-q", 
                            "-o", "../netlist/.",
                            "-n", f"../testbench/{self.config.testbench}"])
            except Exception as ex:
                AsyncLogger.error(ex)

    def __read_corners_file__(self):
        if self.config.corners != None:
            with open("../corners/"+self.config.corners, "r") as f:
                self.corners_file = f.readlines()

    def __read_script_file__(self):
        if self.config.script != None:
            with open("../scripts/"+self.config.script, "r") as f:
                self.script_file = f.readlines()
    
    def __read_measure_file__(self):
        if self.config.measure != None:
            with open("../result_gen/"+self.config.measure, "r") as f:
                self.measure_file = f.readlines()

    def __read_plot_file__(self):
        if self.config.plot != None:
            with open("../result_gen/"+self.config.plot, "r") as f:
                self.plot_file = f.readlines()

    def __read_extraction_files__(self):
        if self.config.extraction != None:
            self.extraction_files = []
            for ef in self.config.extraction:
                with open("../pex/"+ef, "r") as f:
                    self.extraction_files.append(f.readlines())