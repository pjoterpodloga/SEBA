from seba.utils import CornerGenerator, Corner
from seba.spice import SpiceDefinition

class SebaCorner:

    def __init__(self, corner_generators: list[CornerGenerator]):
        self.__corner_generators__ = corner_generators
        self.tnoc = 0
        self.corners = corner_generators[0].corners

        for cg in self.__corner_generators__:
            self.tnoc = self.tnoc + cg.tnoc

    def __get_corners_generators__(self) -> list[CornerGenerator]:
        if self.__corner_generators__ == None:
            raise Exception("Corner generator is \"None\"")
        return self.__corner_generators__
    
    def generate_spice_corners(self) -> list[str]:
        result = []

        corners_generators = self.__get_corners_generators__()

        for it_cg, cg in enumerate(corners_generators):
            result = result + cg.spice_list()
        
        return result

    def generate_corner_list(self) -> list[str]:
        result = []

        corners_generators = self.__get_corners_generators__()

        for it_cg, cg in enumerate(corners_generators):
            result = result + cg.corner_list()

        for it_r in range(len(result)):
            result[it_r] = f"{it_r}: {result[it_r]}"

        result = corners_generators[0].corner_list_header() + result
        
        return result
    
    def generate_spice_definition_corners(self) -> list[SpiceDefinition]:
        result = []

        corners_generators = self.__get_corners_generators__()

        for it_cg, cg in enumerate(corners_generators):
            result = result + cg.spice_definition_list() 

        return result