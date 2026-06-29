import copy
import json
import subprocess

from seba.config import SebaConfig
from seba.corners import SebaCorner
from seba.measure import SebaMeasure, Measure
from seba.spice import *

class SebaAssembler:
    def __init__(self, config: SebaConfig,\
                    corners: SebaCorner, testbench: SebaTestbench,\
                    control: SebaControl, measure: SebaMeasure,
                    script: list[str]):
        self.config = config
        self.corners = corners
        self.testbench = testbench
        self.control = control
        self.measure = measure

        self.number_of_corners = self.corners.tnoc
        self.corner_list = self.corners.generate_corner_list()

        self.testbench_list = [copy.deepcopy(self.testbench) for _ in range(self.number_of_corners)]
        self.control_list = [copy.deepcopy(self.control) for _ in range(self.number_of_corners)]

        self.__adjust_corner_spice_definitions__()
        self.__adjust_corner_write_directive__()
        self.spice_files = self.__create_spice_files__()
        
        self.measure_json_file = self.__create_measure_json_file__()

        self.script_file = script

    def __adjust_corner_spice_definitions__(self):

        corner_spice_definition_list = self.corners.generate_spice_definition_corners()

        for it_sdl, sdl in enumerate(corner_spice_definition_list):
            for it_sd, sd in enumerate(sdl):
                if type(sd) == LibraryDefinition:
                    lib_idx = self.testbench_list[it_sdl].lib_index_dict[sd.name]
                    self.testbench_list[it_sdl].se[lib_idx] = sd
                if type(sd) == ParameterDefinition:
                    param_idx = self.testbench_list[it_sdl].param_index_dict[sd.name]
                    self.testbench_list[it_sdl].se[param_idx] = sd

    def __adjust_corner_write_directive__(self):

        for it_c, c in enumerate(self.control_list):
            for it_se, se in enumerate(c.se):
                if type(se) == ControlWriteDefinition:
                    self.control_list[it_c].se[it_se].name = self.control_list[it_c].se[it_se].name + f"_{it_c}"

    
    def __create_spice_files__(self) -> list[list[str]]:
        
        result_spice_files = []

        for it in range(len(self.testbench_list)):
            spice_file = []

            tb = self.testbench_list[it].get_spice_lines()
            cntr = self.control_list[it].get_spice_lines()

            spice_file = tb
            end_of_file = [spice_file.pop()]
            spice_file = spice_file + cntr + end_of_file
            result_spice_files.append(spice_file)

        return result_spice_files
    
    def __create_measure_json_file__(self) -> str:
        data = []

        for m in self.measure.get_measure_list():
            data.append({
                "name": m.name,
                "max" : m.max,
                "min" : m.min,
                "unit" : m.unit,
                "prefix" : m.prefix,
                "description" : m.desc
            })

        result = json.dumps(data, ensure_ascii=False, indent=2)
        
        return result
    
    def __create_res_directory__(self):
        subprocess.run(["mkdir", f"{self.config.sim_dir}/res"])

    def __write_spice_files__(self):
        
        spice_file_name = self.config.testbench

        for it_sf, sf in enumerate(self.spice_files):
            sfn = f"{spice_file_name}_{it_sf}"

            with open(f"{self.config.sim_dir}/{sfn}", 'w') as f:
                f.write(f"* Title: {self.config.name}")
                f.write("\n")
                for fc in sf:
                    f.write(fc)
                    f.write("\n")
        
    def __write_corner_list__(self):
        corners_list_file_name = "corners.list"

        clfn = f"{self.config.sim_dir}/{corners_list_file_name}"

        with open(clfn, 'w') as f:
            for fc in self.corner_list:
                f.write(fc)
                f.write("\n")

    def __write_measure_json__(self):
        measure_json_file_name = "measure.json"

        mjfn = f"{self.config.sim_dir}/{measure_json_file_name}"

        with open(mjfn, "w") as f:
            f.write(self.measure_json_file)

    def __write_script_file__(self):
        script_file_name = "script.py"

        sfn = f"{self.config.sim_dir}/{script_file_name}"

        with open(sfn, "w") as f:
            f.writelines(self.script_file)

    def __copy_ngspice_utils__(self):
        subprocess.run(["cp", "../result_gen/ngspice_utils.py", f"{self.config.sim_dir}/res"])

    def write_all(self):
        self.__write_spice_files__()
        self.__write_corner_list__()
        self.__write_measure_json__()
        self.__write_script_file__()
        self.__create_res_directory__()
        self.__copy_ngspice_utils__()
