class Token:
    DEFAULT_ID = 1

    SEARCH_VALUES = [" ", "\t", "\\", "#", "=", "[", "]", ",", "\n"]

    TOKEN_DICT = {x: i + 2 for i, x in enumerate(SEARCH_VALUES)}

    def __init__(self, type=None, value=None, line=None, column=None):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

class TokenCorner(Token):
    def __init__(self, type=None, value=None, line=None, column=None):
        super().__init__(type, value, line, column)
        self.group = -1

    @classmethod
    def from_token(cls, token: Token):
        return cls(type=token.type, value=token.value, line=token.line, column=token.column)
    
class Corner:
    def __init__(self, corner_type, corner_name, corner_value=None):
        self.type = corner_type
        self.name = corner_name
        self.value= corner_value

class CornerGenerator:
    def __init__(self, corners, values, grouping):
        self.corners = corners
        self.values = values
        self.grouping = grouping
            
        total_number_of_corners = 1
        current_group = -1

        for it, v in enumerate(self.values):
            if current_group == self.grouping[it]:
                continue
            total_number_of_corners = total_number_of_corners * len(v)
            current_group = self.grouping[it]

        self.tnoc = total_number_of_corners

        self.__resolved_corners__ = self.resolve()

    def resolve(self) -> list[Corner]:
        index_list = [-1]*len(self.corners)

        it_gen = 0
        current_group = -1

        resolved_corners = []

        while it_gen < self.tnoc:
            it_mod = 0
            it_grp = 0
            current_group = -1
            for it_c in range(len(self.corners)-1, -1, -1):
                grp = self.grouping[it_c]
                if current_group != grp:
                    current_group = grp
                    it_mod = (it_gen >> it_grp) % len(self.values[it_c])
                    if len(self.values[it_c]) != 1:
                        it_grp = it_grp + 1

                index_list[it_c] = it_mod

            corner = []
            for it_il, il in enumerate(index_list):
                t = self.corners[it_il].type
                n = self.corners[it_il].name
                v = self.values[it_il][il]
                corner.append(Corner(t, n, v))

            resolved_corners.append(corner)

            it_gen = it_gen + 1

        return resolved_corners
        
    def corner_list_header(self) -> list[str]:
        result = []

        for it_c, c in enumerate(self.corners):
            t = c.type
            n = c.name
            result.append(f"{t} {n}")
            
        return result

    def corner_line(self, n_corner: int) -> str:
        result = []

        for it_c, c in enumerate(self.__resolved_corners__[n_corner]):
            v = c.value

            if it_c == 0:
                result = f"{v}"
            else:
                result = f"{result} {v}"

        return result

    def spice_block(self, n_corner: int) -> list[str]:
        result = []

        for it_c, c in enumerate(self.__resolved_corners__[n_corner]):
            t = c.type
            n = c.name
            v = c.value

            if t == "lib":
                result.append(f".{t} {n} {v}")
            elif t == "param":
                result.append(f".{t} {n}={v}")

        return result
        
    def spice_list(self) -> list[str]:
        result = []

        for it_tnoc in range(self.tnoc):
            result.append(self.spice_block(it_tnoc))

        return result
        
    def corner_list(self) -> list[str]:
        result = []

        for it_tnoc in range(self.tnoc):
            result.append(self.corner_line(it_tnoc))

        return result