from seba.config import SebaConfig
from seba.corners import SebaCorner
from seba.utils import *

class SebaVariant:
    def __init__(self, config: SebaConfig, variant_json):
        self.config = config
        self.__json_file__ = variant_json

        self.__variants__: list[Variant] = []

        self.__match_by__: list[str] = []

        for it_jf, jf in enumerate(self.__json_file__):
            variant = self.__parse_variant__(jf)
            self.__variants__.append(variant)
            self.__match_by__.extend(variant.match)
            self.__parsed_corners__ = self.__parse_testbench_corner_list__(variant)
            self.__parsed_result_csv__ = self.__parse_testbench_measure_csv__(variant)

        self.parsed_corners = SebaCorner(self.__parsed_corners__)

    def get_insert_values_from_map(self, corner: dict) -> list[Corner]:
        meas_idx = self.parsed_corners.get_corner_index_from_map(corner)[0]

        insert_corner_values = []

        for it_v, v in enumerate(self.__variants__):
            vi = v.insert
            for i in vi:
                name = i
                value = self.__parsed_result_csv__.get_value_by_name(name, meas_idx)
                insert_corner_values.append(Corner("param", name, value))

        return insert_corner_values

    def __parse_testbench_measure_csv__(self, variant: Variant):
        tb_name = variant.tb_name
        
        measure_filename = self.config.repo_dir + "/results/" + tb_name + "/measure.csv"

        file_content = None
        with open(measure_filename, "r") as f:
            file_content = f.readlines()

        measure_names: list[str] = []

        header = file_content[0].replace(" ", "").replace("\n", "")
        header = header.split(",")[1:]

        for hs in header:
            measure_names.append(hs)

        values: list[list[str]] = []

        for it_fc, fc in enumerate(file_content[1:]):
            vector = fc.replace(" ", "").replace("\n", "").split(",")[1:]
            v_list = []
            for v in vector:
                v_list.append(v)
            values.append(v_list)
        
        result = Result(header, values)

        return result
            

    def __parse_testbench_corner_list__(self, variant: Variant):
        tb_name = variant.tb_name
        
        measure_filename = self.config.repo_dir + "/results/" + tb_name + "/corners.list"

        file_content = None
        with open(measure_filename, "r") as f:
            file_content = f.readlines()

        corner_list_start = -1
        corner_list_end = -1

        for it_fc, fc in enumerate(file_content):
            str_split = fc.split(" ")

            if str_split[0][-1] == ":" and corner_list_start == -1:
                corner_list_start = it_fc
            
            if str_split[0][-1] != ":" and corner_list_start != -1:
                corner_list_end = it_fc

        if corner_list_start == -1:
            raise Exception("Corners not found in results corner list file.")
        
        if corner_list_end == -1:
            corner_list_end = len(file_content)

        num_of_corners = corner_list_end - corner_list_start

        variant_corners = []
        skip_column_index = []

        for it_vc in range(0, corner_list_start):
            fc = file_content[it_vc].replace("\n", "")
            str_split = fc.split(" ")
            corner_type = "param"
            corner_name = str_split[1]

            if corner_name not in self.__match_by__:
                skip_column_index.append(it_vc)
                continue

            variant_corners.append(Corner(corner_type, corner_name))

        generated_corners: list[CornerGenerator] = []

        for it_gc in range(corner_list_start, corner_list_end):
            fc = file_content[it_gc].replace("\n", "")
            str_split = fc.split(" ")[1:]
            str_filtered = []
            for it_ss, ss in enumerate(str_split):
                if it_ss in skip_column_index:
                    continue
                str_filtered.append(ss)
            values = []
            for it_v, v in enumerate(str_filtered):
                values.append([v])
            mock_grouping = [x for x in range(len(values))]
            generated_corners.append(CornerGenerator(variant_corners, values, mock_grouping))

        return generated_corners

    ### TODO: Write proper exceptions
    def __parse_variant__(self, variant: dict):

        tb_name = None
        match = None
        replace = None
        insert = None

        variant_keys = list(variant.keys())

        if "testbench" not in variant_keys:
            raise Exception("Missing testbench definition in variants file.")
        else:
            tb_name = variant["testbench"]
            self.__check_testbench__(tb_name)

        if "match" not in variant_keys:
            raise Exception("Missing match definition in variants file.")
        else:
            match = variant["match"]
            self.__check_match__(match)

        if "replace" in variant_keys:
            replace = variant["replace"]
            self.__check_replace__(replace)

        if "insert" not in variant_keys:
            raise Exception("Missing insert definition in variants file.")
        else:
            insert = variant["insert"]
            self.__check_insert__(insert)

        return Variant(tb_name=tb_name, match=match,
                       replace=replace, insert=insert)

    ### TODO: write proper checks
    def __check_match__(self, match):
        pass

    def __check_testbench__(self, tb_name):
        pass

    def __check_replace__(self, replace):
        pass

    def __check_insert__(self, insert):
        pass

class Variant:
    def __init__(self, tb_name: str, match: list[str],
                 replace: list[list[str]], insert: list[str]):
        self.tb_name = tb_name
        self.match = match
        self.replace = replace
        self.insert = insert

class Result:
    def __init__(self, header: list[str], measures: list[list[str]]):
        self.header = header
        self.measures = measures

        self.__name_index_map__ = dict()

        for it_h, h in enumerate(header):
            self.__name_index_map__[h] = it_h

    def get_value_by_name(self, name, row):
        return self.measures[row][self.__name_index_map__[name]]