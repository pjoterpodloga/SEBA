import copy
import json
import subprocess

from seba.logger import AsyncLogger
from seba.config import SebaConfig
from seba.corners import SebaCorner
from seba.variants import SebaVariant
from seba.measure import SebaMeasure, Measure
from seba.spice import *
from seba.extraction import SebaExtractionMap, SebaExtraction

class SebaAssembler:
    def __init__(self, config: SebaConfig,\
                    corners: SebaCorner, variants: SebaVariant,
                    testbench: SebaNetlist, control: SebaControl, 
                    measure: SebaMeasure, script: list[str], 
                    extraction: SebaExtractionMap):
        self.config = config
        self.corners = corners
        self.variants = variants
        self.testbench = testbench
        self.control = control
        self.measure = measure
        self.script_file = script
        self.extraction = extraction

        self.number_of_corners = self.corners.tnoc

        self.__corners__ = self.corners.generate_corners()

        self.__adjust_corners_for_variants__()

        self.corner_list = self.corners.generate_corner_list()

        self.__adjust_extraction_subckt_definitions__()

        self.testbench_list = [copy.deepcopy(self.testbench) for _ in range(self.number_of_corners)]
        self.control_list = [copy.deepcopy(self.control) for _ in range(self.number_of_corners)]

        self.__adjust_corner_spice_definitions__()
        self.__adjust_corner_write_directive__()
        self.spice_files = self.__create_spice_files__()
        
        self.measure_json_file = self.__create_measure_json_file__()


    def __adjust_corners_for_variants__(self):

        variant_corners = []

        for it_c in range(self.number_of_corners):
            corner_base_map = self.corners.get_corner_map_from_index(it_c)
            corner_variant_insert = self.variants.get_insert_values_from_map(corner_base_map)
            variant_corners.append(corner_variant_insert)
        self.corners.add_variants_corners(variant_corners)
            

    def __adjust_extraction_subckt_definitions__(self):
        if not self.extraction.extraction_found:
            return

        subckt_keys = list(self.testbench.subckt_index_dict.keys())
        ext_subckt_keys = list(self.extraction.subckt_index_map.keys())

        for it_esk, esk in enumerate(ext_subckt_keys):
            if esk in subckt_keys:
                ext = self.extraction.get_by_index(it_esk).subckt.se[0]
                self.testbench.swap_subckt(esk, ext)
            else:
                AsyncLogger.warning(f"Subckt not found in testbench netlist, extraction \"{esk}\" skipped.")

    def __adjust_corner_spice_definitions__(self):

        corner_spice_definition_list = self.corners.generate_spice_definition_corners()

        lib_keys = list(self.testbench.lib_index_dict.keys())
        param_keys = list(self.testbench.param_index_dict.keys())

        for it_sdl, sdl in enumerate(corner_spice_definition_list):
            for it_sd, sd in enumerate(sdl):
                if type(sd) == LibraryDefinition:
                    if sd.name in lib_keys:
                        lib_idx = self.testbench_list[it_sdl].lib_index_dict[sd.name]
                        self.testbench_list[it_sdl].se[lib_idx] = sd
                    else:
                        self.testbench_list[it_sdl].add_lib(sd)
                if type(sd) == ParameterDefinition:
                    if sd.name in param_keys:
                        param_idx = self.testbench_list[it_sdl].param_index_dict[sd.name]
                        self.testbench_list[it_sdl].se[param_idx] = sd
                    else:
                        self.testbench_list[it_sdl].add_param(sd)

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
        
        if self.config.netlist == None:
            spice_file_name = self.config.testbench.split(".")
            spice_file_name = "".join(spice_file_name[0:-1])+".spice"
        else:
            spice_file_name = self.config.netlist

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
        script_file_name = self.config.script

        sfn = f"{self.config.sim_dir}/{script_file_name}"

        with open(sfn, "w") as f:
            f.writelines(self.script_file)

    def __copy_ngspice_utils__(self):
        subprocess.run(["cp", "../tmp/simulations/res/ngspice_utils.py", f"{self.config.sim_dir}"])

    def __create_script_wrapper__(self):
        wrapper_script_file_name = "script_wrapper.sh"

        wsfn = f"{self.config.sim_dir}/{wrapper_script_file_name}"

        with open(wsfn, "w") as f:
            f.write(f"#!/bin/bash\n")
            f.write( "SCRIPT_DIR=\"$(cd \"$(dirname \"${BASH_SOURCE[0]}\")\" && pwd)\"\n")
            f.write(f"cd \"$SCRIPT_DIR\"\n")
            f.write(f"\"$SCRIPT_DIR/../venv/bin/python\" {self.config.script}\n")

        subprocess.run(["chmod", "+x", wsfn])

    def __copy_result_html__(self):
        result_html_file_name = "index.html"
    
        subprocess.run(["cp", f"../result_gen/{result_html_file_name}", f"{self.config.sim_dir}"])

    def write_all(self):
        self.__write_spice_files__()
        self.__write_corner_list__()
        self.__write_measure_json__()
        self.__write_script_file__()
        self.__create_res_directory__()
        self.__copy_ngspice_utils__()
        self.__create_script_wrapper__()
        self.__copy_result_html__()
