import copy

from seba.config import SebaConfig
from seba.corners import SebaCorner
from seba.spice import *

class SebaAssembler:
    def __init__(self, config: SebaConfig,\
                    corners: SebaCorner, testbench: SebaTestbench,\
                    control: SebaControl):
        self.config = config
        self.corners = corners
        self.testbench = testbench
        self.control = control

        sim_dir = "../tmp/simulations/" + config.name

        number_of_corners = self.corners.tnoc
        corner_list = self.corners.generate_corner_list()
        corner_spice_list = self.corners.generate_spice_corners()
        corner_spice_definition_list = self.corners.generate_spice_definition_corners()

        testbench_list = [copy.deepcopy(self.testbench) for _ in range(number_of_corners)]
        control_list = [copy.deepcopy(self.control) for _ in range(number_of_corners)]

        result_spice_files = []

        for it_sdl, sdl in enumerate(corner_spice_definition_list):
            for it_sd, sd in enumerate(sdl):
                if type(sd) == LibraryDefinition:
                    lib_idx = testbench_list[it_sdl].lib_index_dict[sd.name]
                    testbench_list[it_sdl].se[lib_idx] = sd
                if type(sd) == ParameterDefinition:
                    param_idx = testbench_list[it_sdl].param_index_dict[sd.name]
                    testbench_list[it_sdl].se[param_idx] = sd

        for it_c, c in enumerate(control_list):
            for it_se, se in enumerate(c.se):
                if type(se) == ControlWriteDefinition:
                    control_list[it_c].se[it_se].name = control_list[it_c].se[it_se].name + f"_{it_c}"
        
        for it in range(number_of_corners):
            spice_file = []

            tb = testbench_list[it].get_spice_lines()
            cntr = control_list[it].get_spice_lines()

            spice_file = tb
            end_of_file = [spice_file.pop()]
            spice_file = spice_file + cntr + end_of_file
            result_spice_files.append(spice_file)

        pass



