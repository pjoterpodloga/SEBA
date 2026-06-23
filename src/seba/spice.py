class SpiceEntity:
    def __init__(self):
        pass

    def spice_line(self) -> str:
        return f"* Default spice entity"

class Library(SpiceEntity):
    def __init__(self, name: str, value: str):
        super().__init__()
        self.name = name
        self.value = value
    
    def spice_line(self) -> str:
        return f".lib {self.name} {self.value}"

class Parameter(SpiceEntity):
    def __init__(self, name: str, value: str):
        super().__init__()
        self.name = name
        self.value = value
    
    def spice_line(self) -> str:
        return f".param {self.name}={self.value}"

class Temperatur(SpiceEntity):
    def __init__(self, value: str):
        super().__init__()
        self.value = value
    
    def spice_line(self) -> str:
        return f".temp {self.value}"

class Device(SpiceEntity):
    def __init__(self, name: str, nets: list[str], value: str):
        super().__init__()
        self.name = name
        self.nets = nets
        self.value = value

    def spice_line(self) -> str:
        line = f"{self.name}"

        for n in self.nets:
            line = f"{line} {n}"

        line = f"{line} {self.value}"

        return line

class DcAnalysis(SpiceEntity):
    def __init__(self, sweep: str, start: str, stop: str, step: str):
        super().__init__()
        self.sweep = sweep
        self.start = start
        self.stop = stop
        self.step = step
    
    def spice_line(self) -> str:
        return f".dc {self.sweep} {self.start} {self.stop} {self.step}"

class Probe(SpiceEntity):
    def __init__(self, probe):
        super().__init__()
        self.probe = probe

    def spice_line(self) -> str:
        return f".probe {self.probe}"

class Save(SpiceEntity):
    def __init__(self, save):
        super().__init__()
        self.save = save

    def spice_line(self) -> str:
        return f".save {self.save}"

class SubcircuitDefinition(SpiceEntity):
    def __init__(self, name, pins):
        super().__init__()
        self.name = name
        self.pins = pins

    def spice_line(self) -> str:
        line = f".subckt {self.name}"

        for p in self.pins:
            line = f"{line} {p}"
        
        return line

class SubcircuitInstance(SpiceEntity):
    def __init__(self, name, pins):
        super().__init__()
        self.name = name
        self.pins = pins

    def spice_line(self) -> str:
        line = f"{self.name}"

        for p in self.pins:
            line = f"{line} {p}"

        return line

class Subcircuit(SpiceEntity):
    def __init__(self,  name: str, pins: list[str], parameters: list[str]):
        super().__init__()
        self.name = name
        self.pins = pins
        self.parameters = parameters

class GlobalNet(SpiceEntity):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def spice_line(self) -> str:
        return f".global {self.name}"

class EndSubcircuit(SpiceEntity):
    def __init__(self):
        super().__init__()
    
    def spice_line(self) -> str:
        return f".endc"

class Endfile(SpiceEntity):
    def __init__(self):
        super().__init__()

    def spice_line(self) -> str:
        return f".end"

class SebaSpice:
    def __init__(self, se: list[SpiceEntity]):
        self.se = se