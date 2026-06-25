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

        testbench_list = [copy.deepcopy(self.testbench) for _ in range(number_of_corners)]
        control_list = [copy.deepcopy(self.control) for _ in range(number_of_corners)]

        testbench_list = self.__adjust_corner_spice_definitions__(testbench_list)
        control_list = self.__adjust_corner_write_directive__(control_list)
        result_spice_files = self.__create_final_spice_files__(testbench_list, control_list)

        self.__write_spice_files__(sim_dir, result_spice_files)
        self.__write_corner_list__(sim_dir, corner_list)
        pass

    def __adjust_corner_spice_definitions__(self, testbench_list: list[SebaTestbench]) -> list[SebaTestbench]:

        corner_spice_definition_list = self.corners.generate_spice_definition_corners()

        for it_sdl, sdl in enumerate(corner_spice_definition_list):
            for it_sd, sd in enumerate(sdl):
                if type(sd) == LibraryDefinition:
                    lib_idx = testbench_list[it_sdl].lib_index_dict[sd.name]
                    testbench_list[it_sdl].se[lib_idx] = sd
                if type(sd) == ParameterDefinition:
                    param_idx = testbench_list[it_sdl].param_index_dict[sd.name]
                    testbench_list[it_sdl].se[param_idx] = sd

        return testbench_list

    def __adjust_corner_write_directive__(self, control_list: list[SebaControl]) -> list[SebaControl]:

        for it_c, c in enumerate(control_list):
            for it_se, se in enumerate(c.se):
                if type(se) == ControlWriteDefinition:
                    control_list[it_c].se[it_se].name = control_list[it_c].se[it_se].name + f"_{it_c}"

        return control_list
    
    def __create_final_spice_files__(self, testbench_list: list[SebaTestbench], control_list: list[SebaControl]) -> list[list[str]]:
        
        result_spice_files = []

        for it in range(len(testbench_list)):
            spice_file = []

            tb = testbench_list[it].get_spice_lines()
            cntr = control_list[it].get_spice_lines()

            spice_file = tb
            end_of_file = [spice_file.pop()]
            spice_file = spice_file + cntr + end_of_file
            result_spice_files.append(spice_file)

        return result_spice_files
    
    def __write_spice_files__(self, sim_dir: str, spice_files: list[list[str]]):
        
        spice_file_name = self.config.testbench

        for it_sf, sf in enumerate(spice_files):
            sfn = f"{spice_file_name}_{it_sf}"

            with open(f"{sim_dir}/{sfn}", 'w') as f:
                f.write(f"* Title: {self.config.name}")
                for fc in sf:
                    f.write(fc)
                    f.write("\n")
        
    def __write_corner_list__(self, sim_dir: str, corners: list[str]):
        corners_list_file_name = "corners.list"

        clfn = f"{sim_dir}/{corners_list_file_name}"

        with open(clfn, 'w') as f:
            for fc in corners:
                f.write(fc)
                f.write("\n")


