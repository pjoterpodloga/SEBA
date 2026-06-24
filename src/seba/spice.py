class SpiceDefinition:
    def __init__(self):
        self.name = None
        self.value = None

    def spice_line(self) -> str:
        return f"* Default spice entity"
    
class GenericDefinition(SpiceDefinition):
    def __init__(self, content: list[str]):
        super().__init__()
        self.content = content

    def spice_line(self):
        line = ""

        for c in self.content:
            line = line + c + " "

        return line

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

class ControlDefinition(SpiceDefinition):
    def __init__(self):
        super().__init__()

    def spice_line(self):
        return ".CONTROL"

class EndSubcircuitDefinition(SpiceDefinition):
    def __init__(self):
        super().__init__()
    
    def spice_line(self) -> str:
        return f".ENDS"

class EndControlDefinition(SpiceDefinition):
    def __init__(self):
        super().__init__()

    def spice_line(self):
        return ".ENDC"
    
class EndDefinition(SpiceDefinition):
    def __init__(self):
        super().__init__()

    def spice_line(self) -> str:
        return f".END"

class GenericSpice:
    def __init__(self, se: list[SpiceDefinition]):
        self.se = se

    def get_spice_lines(self):
        return ["* Generic spice block"]

class SebaTestbench(GenericSpice):
    def __init__(self, se: list[SpiceDefinition]):
        super().__init__(se)

        self.param_index_dict = {}
        self.lib_index_dict = {}
        self.subckt_index_dict = {}
        self.ends_index_dict = {}

        subckt_name = None

        for it_se, _se in enumerate(self.se):
            if type(_se) == ParameterDefinition:
                self.param_index_dict[_se.name] = it_se
            if type(_se) == LibraryDefinition:
                self.lib_index_dict[_se.name] = it_se
            if type(_se) == SubcircuitDefinition:
                if subckt_name != None:
                    raise Exception("Found next subckt definition before .endc directive")
                self.subckt_index_dict[_se.name] = it_se
                subckt_name = _se.name
            if type(_se) == EndSubcircuitDefinition:
                if subckt_name == None:
                    raise Exception("Found .endc directive without prio .subckt directive")
                self.ends_index_dict[subckt_name] = it_se
                subckt_name = None


    def get_spice_lines(self):
        lines = []

        for se in self.se:
            lines.append(se.spice_line())

        return lines

class ControlWriteDefinition(SpiceDefinition):
    def __init__(self, name: str, probes: list[str]):
        super().__init__()
        self.name = name
        self.probes = probes
    
    def spice_line(self):
        line = f"WRITE {self.name}"

        for p in self.probes:
            line = f"{line} {p}"

        return line
    
class ControlSetDefinition(SpiceDefinition):
    def __init__(self, name: str, value: str):
        super().__init__()
        self.name = name
        self.value = value

    def spice_line(self):
        return f"SET {self.name}={self.value}"

class SebaControl(GenericSpice):
    def __init__(self, se: list[SpiceDefinition]):
        super().__init__(se)

        self.write_index_dict = {}

        for it_se, _se in enumerate(self.se):

            if type(_se) == ControlWriteDefinition:
                self.write_index_dict[_se.name] = it_se
    
    def get_spice_lines(self):        
        lines = []

        for se in self.se:
            lines.append(se.spice_line())

        return lines
    