class Measure:
    def __init__(self, name, max, min, unit, prefix, desc):
        self.name = name
        self.max = max
        self.min = min
        self.unit = unit
        self.prefix = prefix
        self.desc = desc

class SebaMeasure:
    def __init__(self):
        self.__measure_list__ = []
        self.__measure_name_map__ = {}

    def add(self, measure: Measure):
        self.__measure_list__.append(measure)
        self.__measure_name_map__[measure.name] = len(self.__measure_list__)

    def get_by_name(self, name) -> Measure:
        index = self.__measure_name_map__[name]
        return self.__measure_list__[index]
    
    def get_measure_list(self) -> list[Measure]:
        return self.__measure_list__
