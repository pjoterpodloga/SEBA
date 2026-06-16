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
    
class Parser:

    @classmethod
    def prepare_file(cls, file_content: list[str]) -> str:
        file_content_copy = file_content.copy()
        file_content_copy.append("\n")

        file_content_copy_merged = "".join(file_content_copy)

        return file_content_copy_merged

    @classmethod
    def define_tokens(cls, file_content: str) -> list[Token]:
        token_dict = Token.TOKEN_DICT

        token = [Token(0)]*len(file_content)
        token_keys = token_dict.keys()

        row = 1
        col = 1

        for it_fc, fc in enumerate(file_content):
            if fc in token_keys:
                token[it_fc] = Token(token_dict[fc], fc, row, col)
            else:
                token[it_fc] = Token(Token.DEFAULT_ID, fc, row, col)

            col = col + 1

            if fc == "\n":
                row = row + 1
                col = 1

        return token

    @classmethod
    def change_tokens(cls, tokens: list[Token], target: list[int], until: list[int]) -> list[Token]:

        if (target == None):
            raise Exception("\"Target\" token is \"None\"")
        if (type(target) != list):
            raise Exception("\"Tagert\" token is not \"list()\"")
        
        if (until == None):
            raise Exception("\"Until\" token is \"None\"")
        if (type(until) != list):
            raise Exception("\"Until\" token is not \"list()\"")

        current_target = 0
        t_found = False

        for it_t, t in enumerate(tokens):
            
            tt = t.type

            if tt in target:
                current_target = tt
                t_found = True
                continue
            
            if tt in until:
                current_target = 0
                t_found = False
                continue
            
            if t_found:
                tokens[it_t].type = current_target

        return tokens

    @classmethod
    def delete_tokens(cls, tokens: list[Token], target: list[int]) -> list[Token]:

        for it_t in range(len(tokens)-1, -1, -1):
            tt = tokens[it_t].type

            if tt in target:
                tokens.pop(it_t)

        return tokens
    
    @classmethod
    def group_tokens(cls, tokens: list[Token], target: list[int]) -> list[Token]:
        
        found_target = False
        current_target = -1

        grouped_value = ""

        grouped_token = Token()

        popped_token = Token()

        for it_t in range(len(tokens)-1, -1, -1):
            
            tt = tokens[it_t].type
            tv = tokens[it_t].value

            if tt != current_target and found_target:
                grouped_token = popped_token
                grouped_token.value = grouped_value
                tokens.insert(it_t+1, grouped_token)
                found_target = False

            if tt in target and not found_target:
                grouped_value = ""
                current_target = tt
                found_target = True

            if found_target:
                grouped_value = tv + grouped_value
                popped_token = tokens.pop(it_t)
        
        return tokens
  
    @classmethod  
    def split_tokens(cls, tokens: list[Token], target: int) -> list[list[Token]]:
        
        result = []
        tmp_group = []
        
        for t in tokens:
            tt = t.type

            if tt in target and len(tmp_group) == 0:
                continue

            if tt in target:
                result.append(tmp_group)
                tmp_group = []
                continue

            tmp_group.append(t)

        if len(tmp_group) != 0:
            result.append(tmp_group)

        return result

    @classmethod
    def delete_after_tokens(cls, tokens: list[Token], target: list[int], until: list[int]) -> list[Token]:

        target_found = False
        last_target_it = -1

        for it_t in range(len(tokens)-1, -1, -1):
            tt = tokens[it_t].type

            if tt in until and target_found:

                for it_d in range(last_target_it, it_t-1, -1):
                    tokens.pop(it_d)

                target_found = False
                
            if tt in target:
                target_found = True
                last_target_it = it_t

        return tokens
    
    @classmethod
    def bound_by_token(cls, tokens: list[Token], target: list[int], until: list[int]) -> list[Token]:

        until_found = False

        pm_second_character_found = lambda t1, t2, fc:  f"Found second \"{t2.value}\" token; row: {t2.line}, col: {t2.column}\n"\
                                                        f"{fc[t2.line-1]}"\
                                                        f"{"~"*(t2.column-1)}^{"~"*((t1.column)-(t2.column)-1)}^"
        
        last_ut_token = None

        grouped_tokens = []
        popped_token = None
        for it_t in range(len(tokens)-1, -1, -1):

            tt = tokens[it_t].type

            if tt in target and until_found:
                last_ut_token = tokens[it_t]
                until_found = False
                tokens.insert(it_t, Token(popped_token.type, grouped_tokens, popped_token.line, popped_token.column))
                grouped_tokens = []
                continue

            if tt in target and not until_found:
                raise Exception(pm_second_character_found(last_ut_token, tokens[it_t], self.file_content))
                

            if tt in until and not until_found:
                until_found = True
                last_ut_token = tokens[it_t]
                continue

            if tt in until and until_found:
                raise Exception(pm_second_character_found(last_ut_token, tokens[it_t], self.file_content))

            if until_found:
                popped_token = tokens.pop(it_t)
                grouped_tokens.append(popped_token.value)

        return tokens
    
    @classmethod
    def check_surrounding_token(cls, tokens: list[Token], target: list[int], legal_surrounding: list[int]):
        pass

        return tokens