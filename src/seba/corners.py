from seba.utils import CornerGenerator, Corner

class SebaCorner:

    def __init__(self, corner_generators: list[CornerGenerator]):
        self.__corner_generators__ = corner_generators

    def __get_corners_generators__(self) -> list[CornerGenerator]:
        if self.__corner_generators__ == None:
            raise Exception("Error occured while creating generators or corner generator file was not provided.")
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

        result = result + corners_generators[0].corner_list_header()

        for it_cg, cg in enumerate(corners_generators):
            result = result + cg.corner_list()
        
        return result