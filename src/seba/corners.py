import copy

from seba.utils import CornerGenerator, Corner
from seba.spice import SpiceDefinition

class SebaCorner:

    def __init__(self, corner_generators: list[CornerGenerator], monte_carlo_seeds: int = None):
        self.__corner_generators__ = corner_generators
        self.tnoc = 0
        self.corners = corner_generators[0].corners
        self.monte_carlo_seeds = monte_carlo_seeds

        if self.monte_carlo_seeds == None:
            self.monte_carlo_seeds = 1

        for cg in self.__corner_generators__:
            self.tnoc = self.tnoc + cg.tnoc * self.monte_carlo_seeds

        self.__generate_corner_mapping__()

    def __get_corners_generators__(self) -> list[CornerGenerator]:
        if self.__corner_generators__ == None:
            raise Exception("Corner generator is \"None\"")
        return self.__corner_generators__
    
    def __generate_corner_mapping__(self):
        corner_name_value_map = dict()

        corners_list = self.generate_corners()

        for it_cl, cl in enumerate(corners_list):
            for it_c, c in enumerate(cl):
                corner_name_value_map_keys = list(corner_name_value_map.keys())
                if c.name not in corner_name_value_map_keys:
                    corner_name_value_map[c.name] = dict()
                corner_name_value_map_keys = list(corner_name_value_map[c.name].keys())
                if c.value not in corner_name_value_map_keys:
                    corner_name_value_map[c.name][c.value] = []
                corner_name_value_map[c.name][c.value].append(it_cl)    
        
        self.__corner_reverse_mapping__ = corner_name_value_map

        corner_index_value_map = dict()

        for it_cl, cl in enumerate(corners_list):
            corner_index_value_map[it_cl] = dict()
            for it_c, c in enumerate(cl):
                corner_index_value_map[it_cl][c.name] = c.value

        self.__corner_mapping__ = corner_index_value_map
    
    def get_corner_map_from_index(self, index: int):
        return self.__corner_mapping__[index]

    def get_corner_index_from_map(self, corner: dict) -> list[list[list[int]] | list[list[str]]]:
        
        input_corner_keys = list(corner.keys())
        existing_corner_keys = list(self.__corner_reverse_mapping__.keys())

        exisitng_index_list: list[list[int]] = []
        missing_variants_list: list[list[str]] = []

        abort_search = False

        for it_ick, ick in enumerate(input_corner_keys):
            if ick not in existing_corner_keys:
                continue

            search_value = corner[ick]

            existing_corner_values = list(self.__corner_reverse_mapping__[ick].keys())

            if (search_value in existing_corner_values) and not abort_search:
                exisitng_index_list.append(self.__corner_reverse_mapping__[ick][search_value])
            elif (search_value in existing_corner_values) and abort_search:
                pass
            else:
                missing_variants_list.append([ick, search_value])
                abort_search = True
                exisitng_index_list = []

        if len(exisitng_index_list) == 1:
            return [exisitng_index_list[0], missing_variants_list]

        if len(exisitng_index_list) == 0:
            return [[], missing_variants_list]

        tmp_index_list = exisitng_index_list[0]

        for il in exisitng_index_list[1:]:
            til = copy.deepcopy(tmp_index_list)
            tmp_index_list = []
            for i in il:
                if i in til:
                    tmp_index_list.append(i)
                    
        result_index_list = sorted(tmp_index_list)

        return [result_index_list, missing_variants_list]

    ### TODO: Write proper exception
    def add_variants_corners(self, variant_corners: list[list[Corner]]):
        if len(variant_corners) != self.tnoc:
            raise Exception("Wrong number of variant corners.")
        
        self.__variants_corners__ = variant_corners

        split_intervals = [0]
        integrated_interval = 0

        for cg in self.__corner_generators__:
            integrated_interval = integrated_interval + cg.tnoc
            split_intervals.append(integrated_interval)

        for it_si in range(len(split_intervals) - 1):
            interval_start = split_intervals[it_si]
            interval_end = split_intervals[it_si + 1]
            vc = self.__variants_corners__[interval_start : interval_end]
            self.__corner_generators__[it_si].add_variants_corners(vc)


    def generate_corners(self) -> list[list[Corner]]:
        result = []

        corners_generators = self.__get_corners_generators__()
        
        for it_cg, cg in enumerate(corners_generators):
            resolved_corners = cg.resolve()

            if self.monte_carlo_seeds == 1:
                result.extend(resolved_corners)
            else:
                for it_rc, rc in enumerate(resolved_corners):
                    mc_corners = []
                    for it_mc in range(self.monte_carlo_seeds):
                        mc_corners.append(rc)
                    result.extend(mc_corners)

        return result

    def generate_spice_corners(self) -> list[list[str]]:
        result = []

        corners_generators = self.__get_corners_generators__()

        for it_cg, cg in enumerate(corners_generators):
            resolved_corners = cg.spice_list()

            if self.monte_carlo_seeds == 1:
                result = result + resolved_corners
            else:
                for it_rc, rc in enumerate(resolved_corners):
                    mc_corners = []
                    for it_mc in range(self.monte_carlo_seeds):
                        mc_corners.append(rc)
                    result = result + mc_corners
        
        return result

    def generate_corner_list(self) -> list[str]:
        result = []

        corners_generators = self.__get_corners_generators__()

        for it_cg, cg in enumerate(corners_generators):
            resolved_corners = cg.corner_list()

            if self.monte_carlo_seeds == 1:
                result = result + resolved_corners
            else:
                for it_rc, rc in enumerate(resolved_corners):
                    mc_corners = []
                    for it_mc in range(self.monte_carlo_seeds):
                        mc_corners.append(rc)
                    result = result + mc_corners

        for it_r in range(len(result)):
            result[it_r] = f"{it_r}: {result[it_r]}"

        result = corners_generators[0].corner_list_header() + result
        
        return result
    
    def generate_spice_definition_corners(self) -> list[list[SpiceDefinition]]:
        result = []

        corners_generators = self.__get_corners_generators__()

        for it_cg, cg in enumerate(corners_generators):
            resolved_corners = cg.spice_definition_list()

            if self.monte_carlo_seeds == 1:
                result = result + resolved_corners
            else:
                for it_rc, rc in enumerate(resolved_corners):
                    mc_corners = []
                    for it_mc in range(self.monte_carlo_seeds):
                        mc_corners.append(rc)
                    result = result + mc_corners

        return result