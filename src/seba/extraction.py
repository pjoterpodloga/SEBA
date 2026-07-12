from seba.spice import *
from seba.parser import *

class SebaExtraction:
    def __init__(self, file_content: list[str]):
        parser = SebaParser(None, file_content, None)
        self.subckt = parser.parse_extraction()

class SebaExtractionMap:
    def __init__(self, extraction_files: list[list[str]]):
        self.__extractions__: list[SebaExtraction] = []
        
        for ef in extraction_files:
            self.__extractions__.append(SebaExtraction(ef))

        self.subckt_index_map = dict()
        
        for it_ext, ext in enumerate(self.__extractions__):
            subckt = ext.subckt.se[0]
            self.subckt_index_map[subckt.name] = it_ext

    def get_by_index(self, index: int) -> SebaExtraction:
        return self.__extractions__[index]

    def get_by_name(self, name: str) -> SebaExtraction:
        return self.__extractions__[self.subckt_index_map[name]]