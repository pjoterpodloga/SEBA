class SpiceDefinition:
    def __init__(self):
        pass

    def spice_line(self) -> str:
        return f"* Default spice entity"

class LibraryDefinition(SpiceDefinition):
    def __init__(self, name: str, value: str):
        super().__init__()
        self.name = name
        self.value = value
    
    def spice_line(self) -> str:
        return f".LIB {self.name} {self.value}"

class ParameterDefinition(SpiceDefinition):
    def __init__(self, name: str, value: str):
        super().__init__()
        self.name = name
        self.value = value
    
    def spice_line(self) -> str:
        return f".PARAM {self.name}={self.value}"

class TemperatureDefinition(SpiceDefinition):
    def __init__(self, value: str):
        super().__init__()
        self.value = value
    
    def spice_line(self) -> str:
        return f".TEMP {self.value}"

class DeviceDefinition(SpiceDefinition):
    def __init__(self, name: str, nets: list[str], parameters: list[str]):
        super().__init__()
        self.name = name
        self.nets = nets
        self.parameters = parameters

    def spice_line(self) -> str:
        line = f"{self.name}"

        for n in self.nets:
            line = f"{line} {n}"

        for v in self.parameters:
            line = f"{line} {v[0]}={v[1]}"

        return line

class DcAnalysisDefinition(SpiceDefinition):
    def __init__(self, sweep: str, start: str, stop: str, step: str):
        super().__init__()
        self.sweep = sweep
        self.start = start
        self.stop = stop
        self.step = step
    
    def spice_line(self) -> str:
        return f".DC {self.sweep} {self.start} {self.stop} {self.step}"

class ProbeDefinition(SpiceDefinition):
    def __init__(self, probe):
        super().__init__()
        self.probe = probe

    def spice_line(self) -> str:
        return f".PROBE {self.probe}"

class SaveDefinition(SpiceDefinition):
    def __init__(self, save):
        super().__init__()
        self.save = save

    def spice_line(self) -> str:
        return f".SAVE {self.save}"

class SubcircuitDefinition(SpiceDefinition):
    def __init__(self, name: str, pins):
        super().__init__()
        self.name = name
        self.pins = pins

    def spice_line(self) -> str:
        line = f".SUBCKT {self.name}"

        for p in self.pins:
            line = f"{line} {p}"
        
        return line

class GlobalNetDefinition(SpiceDefinition):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def spice_line(self) -> str:
        return f".GLOBAL {self.name}"

class EndSubcircuitDefinition(SpiceDefinition):
    def __init__(self):
        super().__init__()
    
    def spice_line(self) -> str:
        return f".ENDC"

class EndDefinition(SpiceDefinition):
    def __init__(self):
        super().__init__()

    def spice_line(self) -> str:
        return f".END"

class SebaSpice:
    def __init__(self, se: list[SpiceDefinition]):
        self.se = se

    def get_spice_lines(self):
        lines = []

        for se in self.se:
            lines.append(se.spice_line())

        return lines